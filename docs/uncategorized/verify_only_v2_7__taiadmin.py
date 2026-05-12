#!/usr/bin/env python3
"""verify_only_v2_7.py — KEC 의무 검증 v2.7 (verify만, chunk cache 재사용).

S12: 13 batch 누락 [7,8,10,11,12,13,14,18,20,23,29,34,35] 재시도용.

v2.7 보강 (§ 3.1):
  1) Sonnet 입력에서 obligation_detail 등 4개 필드 제거
  2) verification_note 100자 + 따옴표/줄바꿈/백슬래시 금지
  3) json_repair fallback
  4) batch 실패 시 batch=1 자동 retry

캐시: 26 verify_batch 자동 활용. 13 누락만 호출.
INSERT 없음 (drafts schema 미스매치 회피).

실행:
  cd ~/dev/tai-poc-kec
  source venv/bin/activate
  python3 verify_only_v2_7.py
"""

from __future__ import annotations
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
from supabase import create_client

try:
    from json_repair import repair_json
    HAS_JSON_REPAIR = True
except ImportError:
    HAS_JSON_REPAIR = False

load_dotenv()

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = (
    os.environ.get("SUPABASE_SERVICE_KEY")
    or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    or os.environ["SUPABASE_KEY"]
)

KEC_MASTER_ID = "64209405-1a40-4f0a-aa8a-6f3e55917001"
STORAGE_BUCKET = "law-attachments"
CLAUDE_MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 16384
BATCH_SIZE = 15
LOCAL_TMP = Path("./tmp_extracts")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("v2_7")


SYSTEM_PROMPT = """당신은 한국 산업안전 법령 의무 추출 결과를 검증하는 감사관이다.

# 핵심 원칙
verified=False는 다음 3가지 경우에만:
1. 정의 조항 잘못 분류
2. 너무 일반적 (구체 행위·기준·대상 없음)
3. 본문 근거 없음 (환각)

위 외엔 verified=True. 의문은 verification_note에만 적기.

# law_article: KEC 점번호 (132.2, 142.2.6, 153.1.4.1) 모두 유효.
# 페이지 분할로 조번호 잘려있어도 verified=True 유지.
# applicable_to/frequency: "사업장", "상시", "해당 시" 일반 표현 허용.

# verification_note 작성 규칙 (★ JSON 안전 핵심)
- 100자 이내 (한글)
- 큰따옴표 사용 절대 금지
- 줄바꿈 금지 (한 줄)
- 백슬래시 금지
- 판단 사유만 간결히 (예: 정의 조항 / 구체 기준 모호 / 조번호 확인 불가)

submit_verified_obligations 도구 호출. 입력과 동일 길이/순서 반환."""


VERIFY_TOOL = {
    "name": "submit_verified_obligations",
    "description": "검증된 의무 목록 제출. 입력과 동일 길이/순서.",
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
                            "maxLength": 100,
                            "description": "100자 이내, 따옴표·줄바꿈·백슬래시 금지"
                        }
                    },
                    "required": ["obligation_summary", "law_article", "page_no", "verified", "verification_note"]
                }
            }
        },
        "required": ["obligations"]
    }
}


def strip_for_input(batch):
    keep = {"obligation_summary", "law_article", "page_no"}
    return [{k: v for k, v in ob.items() if k in keep}
            for ob in batch if isinstance(ob, dict)]


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
                raise ValueError(f"broken JSON & no json_repair: {e1}") from e1
            try:
                raw = json.loads(repair_json(raw))
                log.warning("  ✅ json_repair 복구 성공")
            except Exception as e2:
                raise ValueError(f"json_repair 실패: decode={e1} repair={e2}") from e2
    if not isinstance(raw, list):
        raise ValueError(f"not list: {type(raw).__name__}")
    return raw


def call_sonnet(client, batch, full_text, label):
    bi = strip_for_input(batch)
    pages = sorted({ob.get("page_no", 0) for ob in batch if ob.get("page_no")})
    ctxs = []
    for p in pages:
        idx = full_text.find(f"\n[PAGE {p}]\n")
        if idx >= 0:
            ctxs.append(full_text[idx:idx + 3000])
    ctx = "\n---\n".join(ctxs) if ctxs else "(컨텍스트 없음)"

    msg = (f"원본 본문 (pages={pages}):\n---\n{ctx}\n---\n\n"
           f"검증할 의무 ({len(bi)}건):\n"
           f"{json.dumps(bi, ensure_ascii=False, indent=2)}\n\n"
           f"submit_verified_obligations 호출하여 verified, verification_note(100자, 따옴표·줄바꿈 금지) 추가하라. "
           f"입력 순서와 길이({len(bi)}) 유지.")

    log.info(f"  Sonnet {label} (n={len(batch)}) 호출 중...")
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
        raise ValueError("no tool_use block")
    if len(verified) != len(batch):
        log.warning(f"    ⚠️ length mismatch: in={len(batch)} out={len(verified)}")
    return restore_fields(verified, batch), resp.usage


def verify_with_fallback(client, batch, full_text, num, total):
    try:
        r, u = call_sonnet(client, batch, full_text, f"batch {num}/{total}")
        return r, getattr(u, "input_tokens", 0), getattr(u, "output_tokens", 0), False
    except Exception as e:
        log.warning(f"  ⚠️ batch {num} 실패 ({type(e).__name__}: {str(e)[:80]}); batch=1 fallback")

    results = []
    ti = to = 0
    for i, ob in enumerate(batch):
        try:
            r, u = call_sonnet(client, [ob], full_text, f"batch {num}.{i+1}/{total}")
            results.extend(r)
            ti += getattr(u, "input_tokens", 0)
            to += getattr(u, "output_tokens", 0)
        except Exception as e2:
            log.error(f"    ❌ {num}.{i+1} 단건 실패: {str(e2)[:80]}")
            of = dict(ob)
            of["verified"] = False
            of["verification_note"] = f"실패(batch=1): {str(e2)[:60]}"[:100]
            results.append(of)
        time.sleep(0.5)
    return results, ti, to, True


def get_pdf_path():
    p = LOCAL_TMP / f"{KEC_MASTER_ID}.pdf"
    if p.exists() and p.stat().st_size > 1024 * 100:
        log.info(f"PDF cache: {p} ({p.stat().st_size:,} bytes)")
        return p
    log.info("PDF cache 없음. Supabase 다운로드...")
    sb = create_client(SUPABASE_URL, SUPABASE_KEY)
    master = sb.from_("law_master").select("current_version_id").eq(
        "id", KEC_MASTER_ID).single().execute().data
    att = sb.from_("law_attachment").select("storage_path").eq(
        "law_version_id", master["current_version_id"]
    ).eq("attachment_type_code", "ATTACHMENT_BODY").order(
        "file_size_bytes", desc=True).limit(1).execute()
    blob = sb.storage.from_(STORAGE_BUCKET).download(att.data[0]["storage_path"])
    p.write_bytes(blob)
    log.info(f"Downloaded: {p} ({len(blob):,} bytes)")
    return p


def extract_full_text(pdf_path):
    log.info("PDF 텍스트 추출 (1234p, ~1분 소요)...")
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        for i, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""
            tables = page.extract_tables() or []
            tm = ""
            for tb in tables:
                rows = ["| " + " | ".join((c or "") for c in row) + " |" for row in tb if row]
                if rows:
                    tm += "\n" + "\n".join(rows) + "\n"
            pages.append(f"\n[PAGE {i}]\n{text}{tm}")
            if i % 200 == 0:
                log.info(f"  ... {i}/{total}")
    full_text = "".join(pages)
    log.info(f"  추출 완료: {len(full_text):,} chars")
    return full_text


def load_chunks():
    obs = []
    for i in range(1, 6):
        cf = LOCAL_TMP / f"chunk_{i}_obligations.json"
        if not cf.exists():
            log.error(f"❌ {cf.name} 없음")
            return None
        d = json.loads(cf.read_text(encoding="utf-8"))
        obs.extend(d)
        log.info(f"  chunk_{i}: {len(d)}건")
    return obs


def main():
    log.info("=" * 60)
    log.info("KEC 의무 검증 v2.7 (verify-only)")
    log.info(f"  obligation_detail 입력 제거: ✅")
    log.info(f"  verification_note 100자 + 따옴표/줄바꿈 금지: ✅")
    log.info(f"  json_repair fallback: {'✅' if HAS_JSON_REPAIR else '❌ 미설치'}")
    log.info(f"  batch=1 자동 retry: ✅")
    log.info("=" * 60)

    if not HAS_JSON_REPAIR:
        log.warning("⚠️ pip install json-repair 권장 (없어도 batch=1 fallback 작동)")

    pdf_path = get_pdf_path()
    full_text = extract_full_text(pdf_path)
    log.info("=" * 60)
    log.info("Chunk cache 로드...")
    obligations = load_chunks()
    if obligations is None:
        return 1
    log.info(f"의무 총합: {len(obligations)}건")

    log.info("=" * 60)
    log.info("Sonnet 검증 (cache 활용 + 누락만 v2.7로)...")
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    out = []
    cached = refetched = fallback = 0
    total_in = total_out = 0
    total_b = (len(obligations) + BATCH_SIZE - 1) // BATCH_SIZE

    for i in range(0, len(obligations), BATCH_SIZE):
        batch = obligations[i:i + BATCH_SIZE]
        num = i // BATCH_SIZE + 1
        cf = LOCAL_TMP / f"verify_batch_{num}.json"

        if cf.exists():
            try:
                d = json.loads(cf.read_text(encoding="utf-8"))
                if isinstance(d, list) and len(d) == len(batch) and all(isinstance(x, dict) for x in d):
                    log.info(f"Cached batch {num}/{total_b}: skip")
                    out.extend(d)
                    cached += 1
                    continue
            except Exception as e:
                log.warning(f"  cache load 실패 batch {num}: {e}")

        log.info(f"Batch {num}/{total_b} (n={len(batch)})...")
        try:
            r, ti, to, used_fb = verify_with_fallback(client, batch, full_text, num, total_b)
            out.extend(r)
            refetched += 1
            if used_fb:
                fallback += 1
            total_in += ti
            total_out += to
            cf.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
            log.info(f"  ✅ Saved: {cf.name}")
        except Exception as e:
            log.error(f"  ❌ batch {num} 완전 실패: {e}")
            for ob in batch:
                of = dict(ob)
                of["verified"] = False
                of["verification_note"] = f"완전 실패: {str(e)[:60]}"[:100]
                out.append(of)

    pass_n = sum(1 for x in out if isinstance(x, dict) and x.get("verified"))
    fail_n = sum(1 for x in out if isinstance(x, dict) and x.get("verified") is False)
    cost = total_in / 1e6 * 3 + total_out / 1e6 * 15

    log.info("=" * 60)
    log.info("SUMMARY")
    log.info(f"  의무 총: {len(out)}건  pass={pass_n}  fail={fail_n}")
    log.info(f"  Cache: {cached}/{total_b}  Re-verified: {refetched} (fallback used: {fallback})")
    log.info(f"  Tokens (refetched only): in={total_in:,} out={total_out:,}")
    log.info(f"  Sonnet cost: ${cost:.2f}")
    log.info("=" * 60)

    csv_path = LOCAL_TMP / f"{KEC_MASTER_ID}_verified_v2_7.csv"
    cols = ["page_no", "law_article", "obligation_summary", "obligation_detail",
            "applicable_to", "frequency", "penalty_summary", "verified", "verification_note"]
    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for x in out:
            if isinstance(x, dict):
                w.writerow(x)
    log.info(f"CSV: {csv_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
