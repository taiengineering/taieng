#!/usr/bin/env python3
"""verify_fails_v2_9.py — v2.8 fail 33건 재검증 (멀티 위치 ctx).

v2.8 → v2.9 핵심 변경:
  - ctx 추출: find() 첫 위치만 → 최대 3개 발견 위치 모두
  - 위치별 ±2000 chars (앞 800, 뒤 2200)
  - 목차 + 본문 양쪽 다 ctx에 포함하여 Sonnet이 본문 영역 식별

문제 진단 (v2.8 33 fail):
  - 33건 모두 "본문 컨텍스트에 X 내용 없음"
  - 명시적으로 "목차만 있고 본문 내용 확인 불가" 25건+
  - find()가 처음 발견 위치(목차)만 반환 → ctx에 진짜 본문 안 들어감

해결: 멀티 위치 ctx로 본문/목차 모두 보여주고 Sonnet이 본문 부분 인식.

실행:
  cd ~/dev/tai-poc-kec && source venv/bin/activate
  railway run python3 verify_fails_v2_9.py
"""
import csv
import json
import logging
import os
import sys
import time
from pathlib import Path

import anthropic
import pdfplumber
from dotenv import load_dotenv

try:
    from json_repair import repair_json
    HAS_JSON_REPAIR = True
except ImportError:
    HAS_JSON_REPAIR = False

load_dotenv()
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
CLAUDE_MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 16384
BATCH_SIZE = 15

LOCAL_TMP = Path("./tmp_extracts")
KEC_MASTER_ID = "64209405-1a40-4f0a-aa8a-6f3e55917001"
PDF_PATH = LOCAL_TMP / f"{KEC_MASTER_ID}.pdf"
CSV_V2_8 = LOCAL_TMP / f"{KEC_MASTER_ID}_verified_v2_8.csv"
CSV_OUT = LOCAL_TMP / f"{KEC_MASTER_ID}_verified_v2_9.csv"
CACHE_OUT = LOCAL_TMP / "verify_fails_v2_9.json"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("v2_9")


SYSTEM_PROMPT = """당신은 한국 산업안전 법령 의무 추출 결과를 검증하는 감사관이다.

# 핵심 원칙
verified=False는 다음 3가지 경우에만:
1. 정의 조항 잘못 분류
2. 너무 일반적 (구체 행위·기준·대상 없음)
3. 본문에 진짜 근거 없음 (환각)

# law_article 형식 주의
KEC 본문은 hierarchical 표기. 본문에 "241.17.2 ..." 헤더 + "가. ~~~" 항목 형태.
Gemini는 이를 "241.17.2.가" 합성으로 추출. 본문에 정확한 합성 점번호 없어도 환각 아님.

# ctx 컨텍스트 해석 (★ v2.9 핵심 가이드)
입력 ctx는 "=====" 구분자로 같은 점번호의 여러 발견 위치를 합친 것.
- 한 위치는 PDF 앞쪽 목차 (점번호 + 짧은 제목만)
- 다른 위치는 본문 (점번호 + 의무 내용 상세)

목차 entry만 있고 본문 entry가 없으면 환각 의심 가능.
하지만 본문 entry가 한 곳이라도 있으면 의무 자체는 실재. verified=True.
헤더만 있고 하위 항목(가/나/다)이 ctx 범위 밖이면 "조번호 확인 가능, 하위 항목 미확인"으로 verified=True.

# verification_note 작성 규칙
- 100자 이내, 따옴표/줄바꿈/백슬래시 금지
- 간결한 판단 사유

submit_verified_obligations 도구 호출. 입력과 동일 길이/순서."""


VERIFY_TOOL = {
    "name": "submit_verified_obligations",
    "description": "검증 결과 제출.",
    "input_schema": {
        "type": "object",
        "properties": {
            "obligations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "obligation_summary": {"type": "string"},
                        "law_article": {"type": "string"},
                        "page_no": {"type": "integer"},
                        "verified": {"type": "boolean"},
                        "verification_note": {"type": "string", "maxLength": 100}
                    },
                    "required": ["obligation_summary", "law_article", "page_no", "verified", "verification_note"]
                }
            }
        },
        "required": ["obligations"]
    }
}


def find_ctx_v2_9(ob, full_text):
    """v2.9: find() 최대 3개 발견 위치 모두 ctx로."""
    art = (ob.get('law_article') or '').strip()
    if not art:
        return ""
    parts = art.split('.')
    for d in range(len(parts), 1, -1):
        prefix = '.'.join(parts[:d])
        positions = []
        start_pos = 0
        while len(positions) < 3:
            idx = full_text.find(prefix, start_pos)
            if idx < 0:
                break
            positions.append(idx)
            start_pos = idx + len(prefix)
        if positions:
            chunks = [full_text[max(0, p - 800):p + 2200] for p in positions]
            return "\n=====\n".join(chunks)
    return ""


def strip_for_input(batch):
    keep = {"obligation_summary", "law_article", "page_no"}
    return [{k: v for k, v in ob.items() if k in keep} for ob in batch if isinstance(ob, dict)]


def restore_fields(verified, original):
    fields = ("obligation_detail", "applicable_to", "frequency", "penalty_summary")
    for i, v in enumerate(verified):
        if i < len(original) and isinstance(v, dict) and isinstance(original[i], dict):
            for k in fields:
                if not v.get(k):
                    v[k] = original[i].get(k, "")
    return verified


def parse_response(raw):
    if isinstance(raw, str):
        log.warning(f"  string-wrap (len={len(raw)})")
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError as e1:
            if not HAS_JSON_REPAIR:
                raise ValueError(f"broken JSON: {e1}")
            try:
                raw = json.loads(repair_json(raw))
                log.warning("  json_repair OK")
            except Exception as e2:
                raise ValueError(f"json_repair fail: {e2}")
    if not isinstance(raw, list):
        raise ValueError(f"not list: {type(raw).__name__}")
    return raw


def call_sonnet(client, batch, full_text, label):
    bi = strip_for_input(batch)
    ctx_per_ob = []
    for ob in batch:
        c = find_ctx_v2_9(ob, full_text)
        if c:
            ctx_per_ob.append(f"[for {ob.get('law_article')}]\n{c}")
    ctx = "\n###\n".join(ctx_per_ob) if ctx_per_ob else "(ctx 없음)"
    if len(ctx) > 50000:
        ctx = ctx[:50000] + "\n...(truncated)"
    msg = (f"본문 컨텍스트 (law_article별, ===== 구분자는 같은 점번호의 다른 발견 위치):\n---\n{ctx}\n---\n\n"
           f"검증할 의무 ({len(bi)}건):\n"
           f"{json.dumps(bi, ensure_ascii=False, indent=2)}\n\n"
           f"각 의무에 verified, verification_note(100자, 따옴표/줄바꿈 금지) 추가. 입력 순서/길이 유지.")
    log.info(f"  Sonnet {label} (n={len(batch)}, ctx={len(ctx)}자)...")
    resp = client.messages.create(
        model=CLAUDE_MODEL, max_tokens=MAX_TOKENS,
        tools=[VERIFY_TOOL],
        tool_choice={"type": "tool", "name": "submit_verified_obligations"},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": msg}],
    )
    verified = None
    for b in resp.content:
        if b.type == "tool_use" and b.name == "submit_verified_obligations":
            verified = parse_response(b.input.get("obligations", []))
            break
    if verified is None:
        raise ValueError("no tool_use")
    if len(verified) != len(batch):
        log.warning(f"  length mismatch: in={len(batch)} out={len(verified)}")
    return restore_fields(verified, batch), resp.usage


def verify_with_fallback(client, batch, full_text, num, total):
    try:
        r, u = call_sonnet(client, batch, full_text, f"batch {num}/{total}")
        return r, getattr(u, "input_tokens", 0), getattr(u, "output_tokens", 0), False
    except Exception as e:
        log.warning(f"  batch {num} fail; batch=1 fallback: {str(e)[:80]}")
    results = []
    ti = to = 0
    for i, ob in enumerate(batch):
        try:
            r, u = call_sonnet(client, [ob], full_text, f"{num}.{i+1}/{total}")
            results.extend(r)
            ti += getattr(u, "input_tokens", 0)
            to += getattr(u, "output_tokens", 0)
        except Exception as e2:
            of = dict(ob)
            of["verified"] = False
            of["verification_note"] = f"v2.9 single fail: {str(e2)[:60]}"[:100]
            results.append(of)
        time.sleep(0.5)
    return results, ti, to, True


def extract_full_text():
    log.info(f"PDF 텍스트 추출: {PDF_PATH}")
    if not PDF_PATH.exists():
        log.error(f"PDF 없음: {PDF_PATH}")
        sys.exit(1)
    pages = []
    with pdfplumber.open(PDF_PATH) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""
            tables = page.extract_tables() or []
            tm = ""
            for tb in tables:
                rows = ["| " + " | ".join((c or "") for c in row) + " |" for row in tb if row]
                if rows:
                    tm += "\n" + "\n".join(rows) + "\n"
            pages.append(f"\n[PAGE {i}]\n{text}{tm}")
            if i % 300 == 0:
                log.info(f"  ... {i}")
    return "".join(pages)


def main():
    log.info("=" * 60)
    log.info("v2.9: fail 33건 멀티 위치 ctx 재검증")
    log.info("=" * 60)

    if not CSV_V2_8.exists():
        log.error(f"v2.8 CSV 없음: {CSV_V2_8}")
        return 1

    with open(CSV_V2_8, encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    fails = [r for r in rows if str(r.get('verified', '')).lower() in ('false', '0')]

    fail_obs = []
    for r in fails:
        ob = dict(r)
        try:
            ob['page_no'] = int(r.get('page_no', 0) or 0)
        except (ValueError, TypeError):
            ob['page_no'] = 0
        fail_obs.append(ob)
    log.info(f"v2.8 fail load: {len(fail_obs)}건")

    full_text = extract_full_text()
    log.info(f"  full_text: {len(full_text):,} chars")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    out = []
    total_in = total_out = 0
    fallback = 0
    total_b = (len(fail_obs) + BATCH_SIZE - 1) // BATCH_SIZE

    for i in range(0, len(fail_obs), BATCH_SIZE):
        batch = fail_obs[i:i + BATCH_SIZE]
        num = i // BATCH_SIZE + 1
        log.info(f"Batch {num}/{total_b} (n={len(batch)})...")
        try:
            r, ti, to, fb = verify_with_fallback(client, batch, full_text, num, total_b)
            out.extend(r)
            if fb:
                fallback += 1
            total_in += ti
            total_out += to
        except Exception as e:
            log.error(f"  batch {num} total fail: {e}")
            for ob in batch:
                of = dict(ob)
                of["verified"] = False
                of["verification_note"] = f"v2.9 total fail: {str(e)[:60]}"[:100]
                out.append(of)

    CACHE_OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')

    pass_n = sum(1 for x in out if isinstance(x, dict) and x.get('verified') is True)
    fail_n = sum(1 for x in out if isinstance(x, dict) and x.get('verified') is False)
    cost = total_in / 1e6 * 3 + total_out / 1e6 * 15

    log.info("=" * 60)
    log.info("SUMMARY (v2.9)")
    log.info(f"  v2.8 fail {len(fail_obs)}건 -> v2.9 재검증")
    log.info(f"  pass={pass_n}, fail={fail_n}")
    log.info(f"  회복률: {pass_n/len(fail_obs)*100:.0f}% ({pass_n}/{len(fail_obs)})")
    log.info(f"  fallback used: {fallback}")
    log.info(f"  Tokens: in={total_in:,} out={total_out:,}")
    log.info(f"  Sonnet cost: ${cost:.2f}")
    log.info("=" * 60)

    final = []
    v9_lookup = {}
    for r in out:
        if isinstance(r, dict):
            key = (r.get('law_article', ''), (r.get('obligation_summary', '') or '')[:50])
            v9_lookup[key] = r

    for r in rows:
        key = (r.get('law_article', ''), (r.get('obligation_summary', '') or '')[:50])
        is_fail = str(r.get('verified', '')).lower() in ('false', '0')
        if is_fail and key in v9_lookup:
            v9 = v9_lookup[key]
            r2 = dict(r)
            r2['verified'] = v9.get('verified', False)
            r2['verification_note'] = v9.get('verification_note', '')
            final.append(r2)
        else:
            final.append(r)

    cols = ["page_no", "law_article", "obligation_summary", "obligation_detail",
            "applicable_to", "frequency", "penalty_summary", "verified", "verification_note"]
    with CSV_OUT.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        w.writeheader()
        for x in final:
            w.writerow(x)

    final_pass = sum(1 for x in final if str(x.get('verified', '')).lower() in ('true', '1'))
    final_fail = sum(1 for x in final if str(x.get('verified', '')).lower() in ('false', '0'))

    log.info(f"통합 CSV: {CSV_OUT}")
    log.info(f"  최종: pass={final_pass}, fail={final_fail} (575건 중)")
    log.info("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
