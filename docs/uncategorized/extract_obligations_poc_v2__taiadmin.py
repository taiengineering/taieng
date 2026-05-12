#!/usr/bin/env python3
"""
extract_obligations_poc.py — KEC 의무 추출 PoC v2.6 (S11)

v2.5 → v2.6: SDK string-wrapping 수정 (정밀 진단 기반).

진단 결과 (v2.5 575건 추출 결과 분석):
  - 14/38 batch 실패 (페이지/입력 크기 무관)
  - 모든 실패 동일 에러: "obligations is not list: type=str, len=6358~7272"
  - 검증: batch 1 (15 obligations) JSON 직렬화 = 6324 chars → 실패 string 범위와 일치
  - 결론: SDK가 valid JSON 배열을 string으로 wrapping (Anthropic Python SDK 동작)

수정:
  - block.input.get("obligations")가 str이면 json.loads()로 unwrap
  - 6줄 추가 (isinstance 체크 + 변환 + 로깅)
  - source_api = "gemini_pro_poc_v2_6"
  - 나머지 코드 v2.5와 동일

캐시: 25개 verify_batch 살아있음 → 14 batch만 재호출 (~$1.5)
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import sys
import time
from pathlib import Path

import anthropic
import google.generativeai as genai
import pdfplumber
from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_ROLE_KEY = (
    os.environ.get("SUPABASE_SERVICE_KEY")
    or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    or os.environ["SUPABASE_KEY"]
)
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

KEC_MASTER_ID_DEFAULT = "64209405-1a40-4f0a-aa8a-6f3e55917001"
STORAGE_BUCKET = "law-attachments"
GEMINI_MODEL = "gemini-2.5-pro"
CLAUDE_MODEL = "claude-sonnet-4-6"

SOURCE_API_VERSION = "gemini_pro_poc_v2_6"
CLAUDE_MAX_TOKENS = 16384
SONNET_BATCH_SIZE = 15

GEMINI_CHUNK_MAX_CHARS = 350_000

LOCAL_TMP = Path("./tmp_extracts")
LOCAL_TMP.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("poc")


def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def fetch_kec_meta(sb: Client, master_id: str) -> dict:
    r = (
        sb.from_("law_master")
        .select("id, law_name, current_version_id")
        .eq("id", master_id).single().execute()
    )
    master = r.data
    r2 = (
        sb.from_("law_attachment")
        .select("id, attachment_title, storage_path, file_size_bytes")
        .eq("law_version_id", master["current_version_id"])
        .eq("attachment_type_code", "ATTACHMENT_BODY")
        .order("file_size_bytes", desc=True).limit(1).execute()
    )
    if not r2.data:
        raise RuntimeError(f"No ATTACHMENT_BODY for master_id={master_id}")
    return {
        "master_id": master["id"],
        "law_name": master["law_name"],
        "version_id": master["current_version_id"],
        "attachment_id": r2.data[0]["id"],
        "attachment_title": r2.data[0]["attachment_title"],
        "storage_path": r2.data[0]["storage_path"],
        "file_size": r2.data[0]["file_size_bytes"],
    }


def download_attachment(sb: Client, storage_path: str, dest: Path) -> Path:
    if dest.exists() and dest.stat().st_size > 1024 * 100:
        log.info(f"Cached: {dest} ({dest.stat().st_size:,} bytes) — skip")
        return dest
    log.info(f"Downloading {storage_path} ...")
    blob = sb.storage.from_(STORAGE_BUCKET).download(storage_path)
    dest.write_bytes(blob)
    log.info(f"Downloaded → {dest} ({len(blob):,} bytes)")
    return dest


def extract_text(pdf_path: Path) -> tuple[str, list[dict]]:
    log.info(f"Extracting text from {pdf_path} ...")
    full_pages: list[str] = []
    page_meta: list[dict] = []
    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        log.info(f"Total pages: {total}")
        for i, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""
            tables = page.extract_tables() or []
            tables_md = ""
            for tb in tables:
                rows = ["| " + " | ".join((c or "") for c in row) + " |" for row in tb if row]
                if rows:
                    tables_md += "\n" + "\n".join(rows) + "\n"
            page_text = f"\n[PAGE {i}]\n{text}{tables_md}"
            full_pages.append(page_text)
            page_meta.append({
                "page_no": i, "char_count": len(text), "has_table": bool(tables),
            })
            if i % 100 == 0:
                log.info(f"  ... {i}/{total} pages")
    full_text = "".join(full_pages)
    failed = sum(1 for p in page_meta if p["char_count"] < 50)
    log.info(f"Extracted {len(full_text):,} chars; failed pages (<50 chars): {failed}/{total}")
    return full_text, page_meta


def split_text_for_gemini(full_text: str, max_chars: int = GEMINI_CHUNK_MAX_CHARS) -> list[str]:
    if len(full_text) <= max_chars:
        return [full_text]
    chunks: list[str] = []
    pos = 0
    while pos < len(full_text):
        end = pos + max_chars
        if end >= len(full_text):
            chunks.append(full_text[pos:])
            break
        marker_pos = full_text.rfind("\n[PAGE ", pos, end)
        if marker_pos > pos + max_chars // 2:
            chunks.append(full_text[pos:marker_pos])
            pos = marker_pos
        else:
            chunks.append(full_text[pos:end])
            pos = end
    return chunks


GEMINI_SYSTEM = """당신은 한국 산업안전 법령에서 사업장 의무를 추출하는 전문가다.
법령 본문을 받으면, 사업장(소유자/관리자/안전관리자)에게 부과되는 의무를 추출하라.
"의무"는 다음 패턴을 포함한다:
- "~을 갖추어야 한다"
- "~하여야 한다"
- "~을 해서는 아니 된다"
- "~이상 / ~이하 / ~ 미만의 기준에 적합해야 한다"
- "점검 / 검사 / 확인 / 보고 / 신고"
의무 1건 = 단일 조치 (법령 1조항 또는 점번호 1개에 해당).
정의 조항("본 규정에서 ...라 함은 ...")은 의무 아님.
응답은 반드시 유효한 JSON. 다른 설명 텍스트 없음.
응답 구조는 반드시 {"obligations": [...]} 형태로 반환하라.
의무 목록만 단독 배열로 반환하지 말고 반드시 obligations 키로 감싸라."""


def parse_gemini_obligations(raw_text: str) -> list[dict]:
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as e:
        log.error(f"  JSON parse failed: {e}")
        log.error(f"  raw response (first 500 chars): {raw_text[:500]}")
        return []
    if isinstance(data, dict) and "obligations" in data:
        return data["obligations"] if isinstance(data["obligations"], list) else []
    if isinstance(data, list):
        log.info("  Note: Gemini returned bare list (no 'obligations' wrapper)")
        return data
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                log.info(f"  Note: Gemini used '{key}' as wrapper key")
                return value
    log.error(f"  Unexpected response type: {type(data).__name__}")
    return []


def call_gemini_chunk(law_name, chunk_text, chunk_idx, total_chunks, max_obligations):
    genai.configure(api_key=GEMINI_API_KEY)
    instruction_max = (
        f"\n\n중요: 의무는 최대 {max_obligations}건만 추출하라."
        if max_obligations else ""
    )
    user_prompt = f"""법령명: {law_name}
공고: 기후에너지환경부 공고 제2025-227호 (2026-01-05 시행)
청크: {chunk_idx}/{total_chunks}

다음 본문에서 사업장 의무를 추출하여 JSON으로 반환하라.

본문:
---
{chunk_text}
---

응답 형식 (반드시 obligations 키로 감쌀 것, JSON만):
{{
  "obligations": [
    {{
      "obligation_summary": "...",
      "obligation_detail": "...",
      "law_article": "131.1",
      "applicable_to": "...",
      "frequency": "상시",
      "penalty_summary": "...",
      "page_no": 245
    }}
  ]
}}{instruction_max}"""
    model = genai.GenerativeModel(
        GEMINI_MODEL,
        system_instruction=GEMINI_SYSTEM,
        generation_config={"response_mime_type": "application/json", "temperature": 0.2},
    )
    log.info(f"  Gemini chunk {chunk_idx}/{total_chunks} — input ~{len(user_prompt):,} chars ...")
    t0 = time.time()
    resp = model.generate_content(user_prompt)
    elapsed = time.time() - t0
    usage = resp.usage_metadata
    log.info(f"  done in {elapsed:.1f}s — input={usage.prompt_token_count:,} output={usage.candidates_token_count:,}")
    obligations = parse_gemini_obligations(resp.text)
    log.info(f"  → {len(obligations)} obligations")
    return obligations, {
        "input_tokens": usage.prompt_token_count,
        "output_tokens": usage.candidates_token_count,
        "elapsed_sec": elapsed,
    }


def call_gemini(law_name, full_text, max_obligations):
    chunks = split_text_for_gemini(full_text)
    log.info(f"Split into {len(chunks)} chunks (max_chars={GEMINI_CHUNK_MAX_CHARS:,})")
    all_obligations: list[dict] = []
    total_in = total_out = 0
    total_elapsed = 0.0
    cached_count = 0
    for i, chunk in enumerate(chunks, 1):
        remaining = (max_obligations - len(all_obligations) if max_obligations else None)
        if remaining is not None and remaining <= 0:
            log.info(f"Reached max_obligations={max_obligations}, stop")
            break
        chunk_cache = LOCAL_TMP / f"chunk_{i}_obligations.json"
        if chunk_cache.exists() and not max_obligations:
            try:
                obs = json.loads(chunk_cache.read_text(encoding="utf-8"))
                if isinstance(obs, list):
                    log.info(f"  Cached chunk {i}: {len(obs)} obligations — skip API")
                    all_obligations.extend(obs)
                    cached_count += 1
                    continue
            except Exception as e:
                log.warning(f"  Cache load failed for chunk {i}: {e}; will refetch")
        obs, usage = call_gemini_chunk(law_name, chunk, i, len(chunks), remaining)
        try:
            chunk_cache.write_text(json.dumps(obs, ensure_ascii=False, indent=2), encoding="utf-8")
            log.info(f"  Saved: {chunk_cache.name}")
        except Exception as e:
            log.warning(f"  Cache save failed: {e}")
        all_obligations.extend(obs)
        total_in += usage["input_tokens"]
        total_out += usage["output_tokens"]
        total_elapsed += usage["elapsed_sec"]
        if i < len(chunks):
            time.sleep(2)
    if cached_count:
        log.info(f"Used {cached_count} cached chunks")
    if max_obligations:
        all_obligations = all_obligations[:max_obligations]
    seen: set[tuple[str, str]] = set()
    deduped: list[dict] = []
    for ob in all_obligations:
        if not isinstance(ob, dict):
            continue
        key = (ob.get("law_article", ""), (ob.get("obligation_summary") or "")[:50])
        if key not in seen:
            seen.add(key)
            deduped.append(ob)
    log.info(f"Total {len(all_obligations)} obligations (after dedup: {len(deduped)})")
    return deduped, {
        "input_tokens": total_in, "output_tokens": total_out, "elapsed_sec": total_elapsed,
    }


CLAUDE_SYSTEM = """당신은 한국 산업안전 법령 의무 추출 결과를 검증하는 감사관이다.
원본 법령 본문 일부와 추출된 의무 후보를 받아 검증한다.

# 핵심 원칙
verified=False는 다음 3가지 경우에만 부여한다:
1. 정의 조항을 의무로 잘못 분류 — "~라 함은 ...을 말한다" 같은 정의문을 의무로 본 경우
2. 너무 일반적 — 구체적 행위·기준·대상이 없어 누가 무엇을 해야 하는지 판단 불가
3. 본문에 근거 없음 — 제공된 컨텍스트에 해당 의무가 존재하지 않음 (환각)

위 3가지 외의 경우는 verified=True로 두고, 의문점은 verification_note에만 기록한다.

# law_article 형식에 대한 주의
KEC 점번호 체계는 다음과 같다:
- "132.2" = 132조의 제2항 (정상)
- "142.2.6" = 142.2 절의 6항 (정상)
- "153.1.4.1" = 153.1.4 항의 1번 (정상)
- 여러 단계의 점번호 모두 유효한 KEC 표기다

페이지 분할로 인해 컨텍스트에 조번호 헤더가 잘려있을 수 있다.
이 경우 "조번호 확인 불가"는 verification_note에만 기록하고
verified=True를 유지하라. 의무 자체가 본문에 있고 정의 조항이 아니면 verified=True다.

# applicable_to / frequency
"사업장", "상시", "해당 시" 등 일반적 표현도 산업안전 의무에서는 허용된다.
이로 인해 verified=False 부여하지 마라.

# 응답 방식
submit_verified_obligations 도구를 호출하여 결과를 제출하라.
verification_note는 1~2문장으로 간결히. 본문 직접 인용은 피하고 요약하여 기록하라."""


VERIFY_TOOL = {
    "name": "submit_verified_obligations",
    "description": "검증된 의무 목록을 제출한다. 입력받은 의무 후보 각각에 verified와 verification_note를 추가하여 동일한 순서로 반환하라.",
    "input_schema": {
        "type": "object",
        "properties": {
            "obligations": {
                "type": "array",
                "description": "검증된 의무 배열 (입력 batch와 동일한 길이, 동일 순서)",
                "items": {
                    "type": "object",
                    "properties": {
                        "obligation_summary": {"type": "string"},
                        "obligation_detail": {"type": "string"},
                        "law_article": {"type": "string"},
                        "applicable_to": {"type": "string"},
                        "frequency": {"type": "string"},
                        "penalty_summary": {"type": "string"},
                        "page_no": {"type": "integer"},
                        "verified": {"type": "boolean", "description": "True=의무로 정당, False=3가지 거부 사유 중 하나"},
                        "verification_note": {"type": "string", "description": "검증 사유 또는 의문점 (1~2문장)"}
                    },
                    "required": ["obligation_summary", "law_article", "page_no", "verified", "verification_note"]
                }
            }
        },
        "required": ["obligations"]
    }
}


def call_claude_verify(obligations, full_text, batch_size=SONNET_BATCH_SIZE):
    """v2.6: SDK string-wrapping 처리 (json.loads unwrap)."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    verified_all: list[dict] = []
    total_in = total_out = 0
    total_batches = (len(obligations) + batch_size - 1) // batch_size
    cached_batches = 0
    for i in range(0, len(obligations), batch_size):
        batch = obligations[i : i + batch_size]
        batch_num = i // batch_size + 1
        batch_cache = LOCAL_TMP / f"verify_batch_{batch_num}.json"
        if batch_cache.exists():
            try:
                cached = json.loads(batch_cache.read_text(encoding="utf-8"))
                if (isinstance(cached, list) and len(cached) == len(batch)
                        and all(isinstance(x, dict) for x in cached)):
                    log.info(f"Cached batch {batch_num}/{total_batches}: {len(cached)} obligations — skip Sonnet")
                    verified_all.extend(cached)
                    cached_batches += 1
                    continue
            except Exception as e:
                log.warning(f"  Verify cache load failed for batch {batch_num}: {e}; refetch")
        ctx_pages = sorted({ob.get("page_no", 0) for ob in batch if ob.get("page_no")})
        ctx_chunks = []
        for p in ctx_pages:
            marker = f"\n[PAGE {p}]\n"
            idx = full_text.find(marker)
            if idx >= 0:
                ctx_chunks.append(full_text[idx : idx + 3000])
        ctx = "\n---\n".join(ctx_chunks) if ctx_chunks else "(컨텍스트 없음)"
        user_msg = (
            f"원본 본문 일부 (pages={ctx_pages}):\n---\n{ctx}\n---\n\n"
            f"검증할 의무 후보 ({len(batch)}건):\n"
            f"{json.dumps(batch, ensure_ascii=False, indent=2)}\n\n"
            f"submit_verified_obligations 도구를 호출하여 "
            f"각 의무에 verified와 verification_note를 추가한 결과를 제출하라. "
            f"입력 순서를 유지하고 모든 {len(batch)}건을 반환하라."
        )
        log.info(f"Verifying batch {batch_num}/{total_batches} ({len(batch)} obligations) ...")
        try:
            resp = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=CLAUDE_MAX_TOKENS,
                tools=[VERIFY_TOOL],
                tool_choice={"type": "tool", "name": "submit_verified_obligations"},
                system=CLAUDE_SYSTEM,
                messages=[{"role": "user", "content": user_msg}],
            )
            verified_batch = None
            for block in resp.content:
                if block.type == "tool_use" and block.name == "submit_verified_obligations":
                    raw = block.input.get("obligations", [])

                    # ============================================================
                    # v2.6 핵심 수정: SDK가 valid JSON 배열을 string으로 wrapping하는 경우 unwrap
                    # 진단 근거:
                    #   v2.5 14/38 batch 실패 모두 "type=str, len=6358~7272"
                    #   batch 1 (15 obligations) JSON 직렬화 = 6324 chars로 일치
                    #   → string은 valid JSON, json.loads로 복원 가능
                    # ============================================================
                    if isinstance(raw, str):
                        log.warning(
                            f"  SDK wrapped obligations as string (len={len(raw)}); "
                            f"unwrapping with json.loads"
                        )
                        try:
                            raw = json.loads(raw)
                        except json.JSONDecodeError as je:
                            raise ValueError(
                                f"obligations is string but not valid JSON: {je}"
                            ) from je

                    if not isinstance(raw, list):
                        raise ValueError(
                            f"obligations is not list: type={type(raw).__name__}, "
                            f"len={len(raw) if hasattr(raw, '__len__') else 'N/A'}"
                        )
                    if raw and not all(isinstance(x, dict) for x in raw):
                        bad_idx = next(i for i, x in enumerate(raw) if not isinstance(x, dict))
                        raise ValueError(
                            f"obligations[{bad_idx}] is not dict: type={type(raw[bad_idx]).__name__}"
                        )
                    verified_batch = raw
                    break
            if verified_batch is None:
                raise ValueError("No tool_use block found in response")
            if len(verified_batch) != len(batch):
                log.warning(f"  Length mismatch: batch={len(batch)}, verified={len(verified_batch)}")
            verified_all.extend(verified_batch)
            try:
                batch_cache.write_text(
                    json.dumps(verified_batch, ensure_ascii=False, indent=2), encoding="utf-8"
                )
            except Exception as e:
                log.warning(f"  Verify cache save failed: {e}")
        except Exception as e:
            log.error(f"  Batch {batch_num} failed: {e}")
            for ob in batch:
                ob["verified"] = False
                ob["verification_note"] = f"검증 실패: {str(e)[:200]}"
            verified_all.extend(batch)
        try:
            total_in += resp.usage.input_tokens
            total_out += resp.usage.output_tokens
        except Exception:
            pass
    if cached_batches:
        log.info(f"Used {cached_batches} cached verify batches")
    log.info(f"Verification done — input={total_in:,} output={total_out:,}")
    return verified_all, {"input_tokens": total_in, "output_tokens": total_out}


def insert_drafts(sb, verified, meta):
    rows = []
    for ob in verified:
        if not isinstance(ob, dict):
            continue
        rows.append({
            "obligation_summary": (ob.get("obligation_summary") or "")[:200],
            "obligation_detail": (ob.get("obligation_detail") or "")[:1000],
            "law_article": ob.get("law_article", ""),
            "applicable_to": ob.get("applicable_to", ""),
            "frequency": ob.get("frequency", ""),
            "penalty_summary": ob.get("penalty_summary", ""),
            "law_id": meta["master_id"],
            "law_version_id": meta["version_id"],
            "source_doc_id": meta["attachment_id"],
            "source_api": SOURCE_API_VERSION,
            "status": "PENDING_REVIEW",
            "is_active": False,
            "verified": ob.get("verified", False),
            "verification_note": ob.get("verification_note", ""),
        })
    log.info(f"Inserting {len(rows)} rows into law_rule_drafts ...")
    BATCH = 50
    inserted = 0
    for i in range(0, len(rows), BATCH):
        chunk = rows[i : i + BATCH]
        sb.from_("law_rule_drafts").insert(chunk).execute()
        inserted += len(chunk)
    log.info(f"Inserted {inserted} rows")
    return inserted


def write_csv(verified, path):
    cols = [
        "page_no", "law_article", "obligation_summary", "obligation_detail",
        "applicable_to", "frequency", "penalty_summary",
        "verified", "verification_note",
    ]
    skipped = 0
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for ob in verified:
            if not isinstance(ob, dict):
                skipped += 1
                continue
            w.writerow(ob)
    if skipped:
        log.warning(f"  Skipped {skipped} non-dict items in CSV")
    log.info(f"CSV written → {path}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--master-id", default=KEC_MASTER_ID_DEFAULT)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--max-obligations", type=int, default=None)
    p.add_argument("--reset-cache", action="store_true",
        help="Gemini chunk_*_obligations.json 캐시 삭제 후 재실행")
    p.add_argument("--reset-verify-cache", action="store_true",
        help="Sonnet verify_batch_*.json 캐시만 삭제")
    args = p.parse_args()
    if args.reset_cache:
        for f in LOCAL_TMP.glob("chunk_*_obligations.json"):
            f.unlink()
            log.info(f"Removed Gemini cache: {f.name}")
        for f in LOCAL_TMP.glob("verify_batch_*.json"):
            f.unlink()
            log.info(f"Removed Sonnet cache: {f.name}")
    if args.reset_verify_cache:
        for f in LOCAL_TMP.glob("verify_batch_*.json"):
            f.unlink()
            log.info(f"Removed Sonnet cache: {f.name}")
    sb = get_supabase()
    log.info("=" * 60)
    log.info(f"PoC version: {SOURCE_API_VERSION} (tool_use, batch={SONNET_BATCH_SIZE}, max_tokens={CLAUDE_MAX_TOKENS})")
    log.info("Step 1: fetch master + attachment meta")
    meta = fetch_kec_meta(sb, args.master_id)
    log.info(f"  law_name = {meta['law_name']}")
    log.info(f"  attachment = {meta['attachment_title']}")
    log.info(f"  size = {meta['file_size']:,} bytes")
    log.info("=" * 60)
    log.info("Step 2: download PDF")
    pdf_path = LOCAL_TMP / f"{meta['master_id']}.pdf"
    download_attachment(sb, meta["storage_path"], pdf_path)
    log.info("=" * 60)
    log.info("Step 3: extract text")
    full_text, _ = extract_text(pdf_path)
    log.info("=" * 60)
    log.info("Step 4: Gemini extract obligations (chunked, cached)")
    obligations, gemini_usage = call_gemini(meta["law_name"], full_text, args.max_obligations)
    if not obligations:
        log.error("No obligations extracted, abort")
        return 1
    log.info("=" * 60)
    log.info(f"Step 5: Sonnet verify (tool_use + str unwrap, batch_size={SONNET_BATCH_SIZE})")
    verified, claude_usage = call_claude_verify(obligations, full_text)
    log.info("=" * 60)
    log.info("Step 6: write CSV report")
    csv_path = LOCAL_TMP / f"{meta['master_id']}_obligations.csv"
    write_csv(verified, csv_path)
    if args.dry_run:
        log.info("=" * 60)
        log.info("DRY RUN — DB INSERT skipped")
    else:
        log.info("=" * 60)
        log.info("Step 7: INSERT to law_rule_drafts")
        insert_drafts(sb, verified, meta)
    log.info("=" * 60)
    log.info("SUMMARY")
    log.info(f"  Total obligations: {len(verified)}")
    pass_n = sum(1 for ob in verified if isinstance(ob, dict) and ob.get("verified"))
    valid_n = sum(1 for ob in verified if isinstance(ob, dict))
    log.info(f"  Verified: {pass_n}/{valid_n} (valid dicts)")
    log.info(f"  Gemini tokens: in={gemini_usage['input_tokens']:,} out={gemini_usage['output_tokens']:,}")
    log.info(f"  Claude tokens: in={claude_usage['input_tokens']:,} out={claude_usage['output_tokens']:,}")
    g_cost = gemini_usage["input_tokens"] / 1e6 * 1.25 + gemini_usage["output_tokens"] / 1e6 * 5
    c_cost = claude_usage["input_tokens"] / 1e6 * 3 + claude_usage["output_tokens"] / 1e6 * 15
    log.info(f"  Estimated cost: Gemini=${g_cost:.2f} + Claude=${c_cost:.2f} = ${g_cost + c_cost:.2f}")
    log.info(f"  CSV: {csv_path.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
