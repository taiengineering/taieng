#!/usr/bin/env python3
"""verify_fails_v2_8.py — v2.7 fail 78건 재검증 (ctx law_article prefix 기반).

v2.7 → v2.8:
  - ctx 추출: page_no 기반 (부정확) → law_article prefix 기반 (정확)
  - prefix 단계별 fallback (4단계 → 3단계 → 2단계)
  - 발견 위치 ±5000 chars
  - 의무별 ctx 분리 후 합쳐서 Sonnet 입력

fail 78건이 false negative인지 회복률로 검증.

실행:
  cd ~/dev/tai-poc-kec && source venv/bin/activate
  python3 verify_fails_v2_8.py
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
CSV_V2_7 = LOCAL_TMP / f"{KEC_MASTER_ID}_verified_v2_7.csv"
CSV_OUT = LOCAL_TMP / f"{KEC_MASTER_ID}_verified_v2_8.csv"
CACHE_OUT = LOCAL_TMP / "verify_fails_v2_8.json"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("v2_8")


SYSTEM_PROMPT = """당신은 한국 산업안전 법령 의무 추출 결과를 검증하는 감사관이다.

# 핵심 원칙
verified=False는 다음 3가지 경우에만:
1. 정의 조항 잘못 분류
2. 너무 일반적 (구체 행위·기준·대상 없음)
3. 본문 근거 없음 (환각)

# law_article 형식 주의 (★ v2.8 핵심 가이드)
KEC 본문은 hierarchical 표기를 쓴다. 예를 들어:
  본문에는 241.17.2 헤더 후 가. ~~~ / 나. ~~~ 형태로 표기.
  Gemini는 이를 241.17.2.가 합성 점번호로 추출함.
  본문에 정확히 241.17.2.가 문자열이 없어도 환각 아님.
  241.17.2 헤더 + 가. 항목이 ctx에 있으면 verified=True.

# verification_note 작성 규칙 (★ JSON 안전)
- 100자 이내, 따옴표/줄바꿈/백슬래시 금지
- 간결한 판단 사유만 (예: 정의 조항 / 구체 기준 모호 / 합성 점번호)

submit_verified_obligations 도구 호출. 입력과 동일 길이/순서."""


VERIFY_TOOL = {
    "name": "submit_verified_obligations",
    "description": "검증 결과 제출. 입력과 동일 길이/순서.",
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
                        "verification_note": {
                            "type": "string",
                            "maxLength": 100
                        }
                    },
                    "required": ["obligation_summary", "law_article", "page_no", "verified", "verification_note"]
                }
            }
        },
        "required": ["obligations"]
    }
}


def find_ctx_v2_8(ob, full_text):
    """v2.8: law_article prefix 기반 ctx. page_no 무시."""
    art = (ob.get('law_article') or '').strip()
    if not art:
        return ""
    parts = art.split('.')
    for d in range(len(parts), 1, -1):
        prefix = '.'.join(parts[:d])
        idx = full_text.find(prefix)
        if idx > 0:
            start = max(0, idx - 1500)
            end = idx + 5000
            return full_text[start:end]
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
        c = find_ctx_v2_8(ob, full_text)
        if c:
            ctx_per_ob.append(f"[for {ob.get('law_article')}]\n{c}")
    ctx = "\n---\n".join(ctx_per_ob) if ctx_per_ob else "(ctx 못 찾음)"
    if len(ctx) > 30000:
        ctx = ctx[:30000] + "\n...(truncated)"

    msg = (f"본문 컨텍스트 (law_article별):\n---\n{ctx}\n---\n\n"
           f"검증할 의무 ({len(bi)}건):\n"
           f"{json.dumps(bi, ensure_ascii=False, indent=2)}\n\n"
           f"각 의무에 verified, verification_note(100자, 따옴표/줄바꿈 금지) 추가. 입력 순서/길이 유지.")

    log.info(f"  Sonnet {label} (n={len(batch)}, ctx={len(ctx)}자) 호출...")
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
        log.warning(f"  batch {num} fail ({type(e).__name__}: {str(e)[:80]}); batch=1 fallback")
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
            of["verification_note"] = f"v2.8 single fail: {str(e2)[:60]}"[:100]
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
    log.info("v2.8: fail 78건 ctx-prefix 기반 재검증")
    log.info("=" * 60)

    if not CSV_V2_7.exists():
        log.error(f"v2.7 CSV 없음: {CSV_V2_7}")
        return 1

    with open(CSV_V2_7, encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    fails = [r for r in rows if r.get('verified', '').lower() == 'false']

    fail_obs = []
    for r in fails:
        ob = dict(r)
        try:
            ob['page_no'] = int(r.get('page_no', 0) or 0)
        except (ValueError, TypeError):
            ob['page_no'] = 0
        fail_obs.append(ob)
    log.info(f"v2.7 fail load: {len(fail_obs)}건")

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
                of["verification_note"] = f"v2.8 total fail: {str(e)[:60]}"[:100]
                out.append(of)

    CACHE_OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')

    pass_n = sum(1 for x in out if isinstance(x, dict) and x.get('verified') is True)
    fail_n = sum(1 for x in out if isinstance(x, dict) and x.get('verified') is False)
    cost = total_in / 1e6 * 3 + total_out / 1e6 * 15

    log.info("=" * 60)
    log.info("SUMMARY (v2.8)")
    log.info(f"  v2.7 fail {len(fail_obs)}건 -> v2.8 재검증")
    log.info(f"  pass={pass_n}, fail={fail_n}")
    log.info(f"  회복률: {pass_n/len(fail_obs)*100:.0f}% ({pass_n}/{len(fail_obs)})")
    log.info(f"  fallback used: {fallback}")
    log.info(f"  Tokens: in={total_in:,} out={total_out:,}")
    log.info(f"  Sonnet cost: ${cost:.2f}")
    log.info("=" * 60)

    # 통합 CSV: v2.7 pass + v2.8 결과
    final = []
    v8_lookup = {}
    for r in out:
        if isinstance(r, dict):
            key = (r.get('law_article', ''), (r.get('obligation_summary', '') or '')[:50])
            v8_lookup[key] = r

    for r in rows:
        key = (r.get('law_article', ''), (r.get('obligation_summary', '') or '')[:50])
        if r.get('verified', '').lower() == 'false' and key in v8_lookup:
            v8 = v8_lookup[key]
            r2 = dict(r)
            r2['verified'] = v8.get('verified', False)
            r2['verification_note'] = v8.get('verification_note', '')
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
    log.info(f"  최종: pass={final_pass}, fail={final_fail}")
    log.info("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
