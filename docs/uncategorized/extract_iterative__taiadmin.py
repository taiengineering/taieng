#!/usr/bin/env python3
"""
SET-001 iterative extraction — 명세: docs/extraction/CURSOR_TASK_SET_001.md

실행 위치:
  - 권장: ~/dev/tai-extraction-v3 (prompts/sql 복사본과 함께)
  - 또는: 본 파일이 있는 docs/extraction/ 기준으로 상위 폴더에서 리소스 로드
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

_script_dir = Path(__file__).resolve().parent
ROOT = _script_dir if (_script_dir / "SET_001_articles.json").exists() else _script_dir.parent

load_dotenv(ROOT / ".env")
_api_env = Path.home() / "Desktop" / "tai-engineering" / "tai-api" / ".env"
if _api_env.is_file():
    load_dotenv(_api_env, override=False)

SET_ID = "SET-001"
CYCLE = 1
PROMPT_VERSION = "v3.0.1"
MAX_ARTICLE_SECONDS = 90
ESTIMATED_COST_CAP_USD = 10.0
DEFAULT_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")


def _prompt_path() -> Path:
    p1 = ROOT / "prompts" / "v3_0_1.md"
    if p1.is_file():
        return p1
    return ROOT / "PROMPT_v3_0_1.md"


def _read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _strip_json_fence(text: str) -> str:
    t = text.strip()
    if "```json" in t:
        return t.split("```json", 1)[1].split("```", 1)[0].strip()
    if "```" in t:
        parts = t.split("```")
        if len(parts) >= 2:
            return parts[1].strip()
    return t


def _estimate_cost_usd(input_chars: int, output_chars: int) -> float:
    in_tok = max(1, input_chars // 4)
    out_tok = max(1, output_chars // 4)
    return in_tok * 3.0e-6 + out_tok * 15.0e-6


def _delete_set_cycle(sb) -> None:
    try:
        sb.table("law_rule_drafts").delete().contains(
            "ai_flags", {"extraction_set": SET_ID, "extraction_cycle": CYCLE}
        ).execute()
        return
    except Exception:
        pass
    set_info = json.loads((ROOT / "SET_001_articles.json").read_text(encoding="utf-8"))
    ids = [a["article_id"] for a in set_info["articles"]]
    res = sb.table("law_rule_drafts").select("id,ai_flags").in_("article_id", ids).execute()
    for row in res.data or []:
        flags = row.get("ai_flags") or {}
        if flags.get("extraction_set") != SET_ID:
            continue
        cyc = flags.get("extraction_cycle")
        if int(cyc) != CYCLE and str(cyc) != str(CYCLE):
            continue
        sb.table("law_rule_drafts").delete().eq("id", row["id"]).execute()


def _run_audit_psycopg2(sql_path: Path) -> list[dict] | None:
    dsn = os.environ.get("POSTGRES_URL") or os.environ.get("DATABASE_URL") or os.environ.get(
        "SUPABASE_DB_DIRECT_URL"
    )
    if not dsn:
        return None
    try:
        import psycopg2  # type: ignore
        import psycopg2.extras  # type: ignore
    except ImportError:
        return None
    sql = sql_path.read_text(encoding="utf-8")
    conn = psycopg2.connect(dsn)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql)
            rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def _run_audit_psql(sql_path: Path) -> list[dict] | None:
    dsn = os.environ.get("POSTGRES_URL") or os.environ.get("DATABASE_URL")
    if not dsn:
        return None
    try:
        proc = subprocess.run(
            ["psql", dsn, "-v", "ON_ERROR_STOP=1", "-A", "-F", "|", "-f", str(sql_path)],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        print(proc.stderr, file=sys.stderr)
        return None
    lines = [ln for ln in proc.stdout.strip().splitlines() if ln.strip()]
    out: list[dict] = []
    for ln in lines:
        parts = ln.split("|")
        if len(parts) >= 2:
            out.append({"check_id": parts[0], "value": parts[1]})
    return out if out else None


def main() -> int:
    prompt_path = _prompt_path()
    set_path = ROOT / "SET_001_articles.json"
    audit_sql_path = ROOT / "sql" / "audit_set_v2.sql"
    out_dir = ROOT / "output"
    if not prompt_path.exists():
        print("missing prompt file:", prompt_path, file=sys.stderr)
        return 2

    PROMPT = _read_text(prompt_path)
    SET_INFO = json.loads(set_path.read_text(encoding="utf-8"))
    article_ids = [a["article_id"] for a in SET_INFO["articles"]]

    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    supabase_url = os.environ.get("SUPABASE_URL")
    # ⭐ Service role key 우선 (RLS 우회 가능). anon key는 fallback (RLS 정책에 막힐 수 있음)
    supabase_key = (
        os.environ.get("SUPABASE_SERVICE_KEY")
        or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_KEY")
    )

    report: dict = {
        "set_id": SET_ID,
        "cycle": CYCLE,
        "prompt_version": PROMPT_VERSION,
        "model": DEFAULT_MODEL,
        "articles_processed": 0,
        "extracted_drafts": 0,
        "broken_articles": 0,
        "audit": [],
        "issues": [],
        "pass": False,
        "next_step": "",
        "errors": [],
        "estimated_cost_usd": 0.0,
        "audit_source": None,
    }

    if not anthropic_key:
        report["errors"].append("ANTHROPIC_API_KEY 없음 — LLM 단계 생략")
    if not (supabase_url and supabase_key):
        report["errors"].append(
            "SUPABASE_URL / SUPABASE_SERVICE_KEY (또는 SUPABASE_SERVICE_ROLE_KEY) 없음 — DB 단계 생략"
        )

    if report["errors"]:
        report["next_step"] = ".env 설정 후 재실행"
        report["pass"] = False
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "set_001_cycle_1.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    from supabase import create_client

    client = Anthropic(api_key=anthropic_key, timeout=max(120, MAX_ARTICLE_SECONDS + 30))
    sb = create_client(supabase_url, supabase_key)

    _delete_set_cycle(sb)

    res_art = (
        sb.table("law_article")
        .select("id,article_text,article_no,article_title,article_type,law_id")
        .in_("id", article_ids)
        .execute()
    )
    articles_data = res_art.data or []
    report["articles_processed"] = len(articles_data)

    law_ids = list({a["law_id"] for a in articles_data if a.get("law_id")})
    masters_data = (
        sb.table("law_master").select("id,law_name,law_type_code").in_("id", law_ids).execute().data
        or []
    )
    master_map = {m["id"]: m for m in masters_data}

    total_drafts = 0
    broken_count = 0
    cumulative_cost = 0.0

    for art in articles_data:
        if cumulative_cost >= ESTIMATED_COST_CAP_USD:
            report["errors"].append(f"예상 비용 한도 ${ESTIMATED_COST_CAP_USD} 초과 — 중단")
            break
        m = master_map.get(art["law_id"])
        if not m:
            report["errors"].append(f"law_master 없음 article_id={art['id']}")
            broken_count += 1
            continue

        user_input = (
            f"law_name: {m['law_name']}\n"
            f"law_type_code: {m['law_type_code']}\n"
            f"article_no: {art['article_no']}\n"
            f"article_type: {art['article_type']}\n"
            f"article_title: {art['article_title']}\n"
            f"article_text: {art['article_text']}"
        )

        try:
            resp = client.messages.create(
                model=DEFAULT_MODEL,
                max_tokens=4000,
                system=PROMPT,
                messages=[{"role": "user", "content": user_input}],
                timeout=MAX_ARTICLE_SECONDS,
            )
        except Exception as e:
            print(f"LLM 실패 article {art['id']}: {e}", file=sys.stderr)
            broken_count += 1
            continue

        result_text = resp.content[0].text
        cumulative_cost += _estimate_cost_usd(
            len(PROMPT) + len(user_input), len(result_text)
        )
        report["estimated_cost_usd"] = round(cumulative_cost, 4)

        try:
            result = json.loads(_strip_json_fence(result_text))
        except Exception as e:
            print(f"파싱 실패 article {art['id']}: {e}", file=sys.stderr)
            broken_count += 1
            continue

        if result.get("broken"):
            broken_count += 1
            continue

        extracted = result.get("extracted") or []
        if not extracted:
            broken_count += 1
            continue

        self_check = result.get("self_check")
        for ob in extracted:
            ai_flags = {
                "extraction_set": SET_ID,
                "extraction_cycle": CYCLE,
                "prompt_version": PROMPT_VERSION,
                "extracted_at": datetime.now(timezone.utc).isoformat(),
                "from_pipeline": "v3_iterative",
                "self_check": self_check,
                "broken": False,
            }
            row = {
                "law_name": m["law_name"],
                "law_article": f"제{art['article_no']}조",
                "article_id": art["id"],
                "article_text": art["article_text"],
                "obligation_summary": ob["obligation_summary"],
                "appointment_target": ob["appointment_target"],
                "obligation_type": ob["obligation_type"],
                "sector": ob.get("sector"),
                "condition_code": ob.get("condition_code"),
                "condition_operator": ob.get("condition_operator"),
                "condition_value": ob.get("condition_value"),
                "penalty_summary": ob.get("penalty_summary"),
                "ai_reasoning": ob["ai_reasoning"],
                "ai_confidence": ob["ai_confidence"],
                "ai_flags": ai_flags,
                "status": "PENDING",
                "diagnosis_stage": ob.get("diagnosis_stage", 1),
            }
            try:
                sb.table("law_rule_drafts").insert(row).execute()
                total_drafts += 1
            except Exception as e:
                print(f"INSERT 실패 article {art['id']}: {e}", file=sys.stderr)
                report["errors"].append(str(e))

    report["extracted_drafts"] = total_drafts
    report["broken_articles"] = broken_count

    audit = None
    if audit_sql_path.is_file():
        audit = _run_audit_psycopg2(audit_sql_path) or _run_audit_psql(audit_sql_path)
    if audit is None:
        report["audit_source"] = "skipped (POSTGRES_URL 없음 — 본 기획창에서 supabase MCP로 audit 직접 실행)"
        report["audit"] = []
        report["pass"] = False
        report["next_step"] = "본 기획창(Claude)에서 sql/audit_set_v2.sql 직접 실행"
    else:
        report["audit_source"] = "postgres"
        report["audit"] = audit
        issues = [
            r
            for r in audit
            if r.get("check_id") != "01_drafts 추출 수" and int(str(r.get("value", "0")).strip() or "0") > 0
        ]
        report["issues"] = issues
        report["pass"] = len(issues) == 0
        report["next_step"] = (
            "SET-001 PASS! rule_miner 실행 → SET-002"
            if report["pass"]
            else "PROMPT v3.0.2 강화 후 cycle 2"
        )

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "set_001_cycle_1.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"SET-001 Cycle {CYCLE} ({PROMPT_VERSION})")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"처리: {report['articles_processed']}/20 article")
    print(f"추출: {total_drafts} drafts")
    print(f"broken: {broken_count}")
    print(f"예상 비용(대략): ${report.get('estimated_cost_usd', 0)}")
    print("")
    print("검증 결과:")
    for r in report.get("audit") or []:
        cid = r.get("check_id", "")
        val = str(r.get("value", "0")).strip()
        if cid == "01_drafts 추출 수":
            print(f"  ℹ️  {cid}: {val}")
        elif int(val or "0") == 0:
            print(f"  ✅ {cid}")
        else:
            print(f"  ❌ {cid}: {val}")
    if not report.get("audit"):
        print("  (audit 미실행 — 본 기획창 supabase MCP로 처리)")
    print("")
    print(f"PASS: {'YES ✅' if report.get('pass') else 'NO ❌'}")
    print(f"다음: {report['next_step']}")
    print(f"\n저장: {out_path}")
    return 0 if report.get("pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
