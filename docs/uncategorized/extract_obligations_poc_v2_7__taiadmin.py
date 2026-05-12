#!/usr/bin/env python3
"""
extract_obligations_poc_v2_7.py — KEC 의무 추출 PoC v2.7 (S12)

v2.6 → v2.7: § 3.1 5가지 해결책 중 4가지 적용 (broken JSON 33% → 0% 목표).

S11 진단 (2026-05-04):
  - 575건 의무 추출 완료 (chunk 5/5)
  - 26 batch verify 캐시 / 13 batch broken JSON으로 미캐시
  - 누락 batch: [7, 8, 10, 11, 12, 13, 14, 18, 20, 23, 29, 34, 35]
  - 누락 의무: ~195건

v2.7 보강:
  1) Sonnet 입력에서 obligation_detail/applicable_to/frequency/penalty_summary 제거
     검증에는 summary + law_article + page_no만 필요. 입력 ~60% 축소.
  2) verification_note 100자 제한 + 따옴표/줄바꿈/백슬래시 금지
     (system prompt + tool schema maxLength 둘 다 강제)
  3) json_repair.loads fallback (string-wrap broken 시 자동 복구)
  4) batch 전체 실패 시 batch=1로 단건 재시도 (실패 의무만 fail 처리)
  5) verify cache 저장 시 입력에서 뺀 필드 보강 (다음 단계용)

캐시 동작:
  - 26개 verify_batch cache 자동 활용 (skip)
  - 13개 누락 batch만 v2.7 보강된 로직으로 재시도
  - 비용 ~$1~2, 시간 ~10~30분

실행:
  cd ~/dev/tai-poc-kec
  source venv/bin/activate
  python3 extract_obligations_poc_v2_7.py

  기본값 --dry-run (DB INSERT skip — schema 미스매치 회피)
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

# v2.7: json_repair fallback (선택)
try:
    from json_repair import repair_json
    HAS_JSON_REPAIR = True
except ImportError:
    HAS_JSON_REPAIR = False

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

SOURCE_API_VERSION = "gemini_pro_poc_v2_7"
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
log = logging.getLogger("poc_v2_7")


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


# ======================================================================
# v2.7 강화된 검증 (broken JSON 0% 목표)
# ======================================================================

CLAUDE_SYSTEM = """당신은 한국 산업안전 법령 의무 추출 결과를 검증하는 감사관이다.
원본 법령 본문 일부와 추출된 의무 후보를 받아 검증한다.

# 핵심 원칙
verified=False는 다음 3가지 경우에만 부여한다:
1. 정의 조항을 의무로 잘못 분류 — "~라 함은 ...을 말한다" 같은 정의문을 의무로 본 경우
2. 너무 일반적 — 구체적 행위·기준·대상이 없어 누가 무엇을 해야 하는지 판단 불가
3. 본문에 근거 없음 — 제공된 컨텍스트에 해당 의무가 존재하지 않음 (환각)

위 3가지 외의 경우는 verified=True로 두고, 의문점은 verification_note에만 기록한다.

# law_article 형식 주의
KEC 점번호 체계는 "132.2", "142.2.6", "153.1.4.1" 등 모두 유효.
페이지 분할로 컨텍스트에 조번호 헤더가 잘려있을 수 있다.
이 경우 "조번호 확인 불가"는 verification_note에만 기록하고 verified=True 유지.

# applicable_to / frequency
"사업장", "상시", "해당 시" 등 일반 표현 허용. 이로 인해 verified=False 부여하지 마라.

# verification_note 작성 규칙 (★ 매우 중요 — JSON 안전)
- 반드시 100자 이내 (한글 기준)
- 본문 직접 인용 금지: 큰따옴표 사용 절대 금지
- 줄바꿈 사용 금지: 한 줄로 작성
- 백슬래시 사용 금지
- 너의 판단 사유만 간결히 기록 (예: 정의 조항이 아닌 의무 명시 / 구체 기준 모호 / 조번호 확인 불가)

# 응답 방식
submit_verified_obligations 도구를 호출하여 결과를 제출하라.
입력 batch와 동일한 길이, 동일 순서를 유지하라."""


VERIFY_TOOL = {
    "name": "submit_verified_obligations",
    "description": "검증된 의무 목록을 제출한다. 입력 batch와 동일 길이/순서를 유지하라.",
    "input_schema": {
        "type": "object",
        "properties": {
            "obligations": {
                "type": "array",
                "description": "검증된 의무 배열 (입력과 동일 길이/순서)",
                "items": {
                    "type": "object",
                    "properties": {
                        "obligation_summary": {"type": "string"},
                        "law_article": {"type": "string"},
                        "page_no": {"type": "integer"},
                        "verified": {
                            "type": "boolean",
                            "description": "True=의무로 정당, False=3가지 거부 사유 중 하나"
                        },
                        "verification_note": {
                            "type": "string",
                            "maxLength": 100,
                            "description": "검증 사유 100자 이내. 따옴표·줄바꿈·백슬래시 금지."
                        }
                    },
                    "required": ["obligation_summary", "law_article", "page_no", "verified", "verification_note"]
                }
            }
        },
        "required": ["obligations"]
    }
}


def _strip_detail_for_verify(batch: list[dict]) -> list[dict]:
    """v2.7: Sonnet 입력에서 검증 불필요한 필드 제거.

    검증에는 summary + law_article + page_no 만 필요.
    obligation_detail/applicable_to/frequency/penalty_summary 제거 → 입력 ~60% 축소.
    """
    keep_keys = {"obligation_summary", "law_article", "page_no"}
    return [
        {k: v for k, v in ob.items() if k in keep_keys}
        for ob in batch if isinstance(ob, dict)
    ]


def _restore_dropped_fields(verified_batch: list[dict], original_batch: list[dict]) -> list[dict]:
    """v2.7: verify cache 저장 전에 입력에서 뺀 필드 보강 (다음 단계용)."""
    fields_to_restore = ("obligation_detail", "applicable_to", "frequency", "penalty_summary")
    for i, vb in enumerate(verified_batch):
        if not (i < len(original_batch) and isinstance(vb, dict) and isinstance(original_batch[i], dict)):
            continue
        for k in fields_to_restore:
            if not vb.get(k):
                vb[k] = original_batch[i].get(k, "")
    return verified_batch


def _parse_obligations_from_response(raw) -> list[dict]:
    """v2.7: SDK string-wrap 처리 + json_repair fallback."""
    if isinstance(raw, str):
        log.warning(f"    SDK가 obligations를 string으로 wrap (len={len(raw)})")
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError as je1:
            if not HAS_JSON_REPAIR:
                raise ValueError(
                    f"obligations is broken JSON & json_repair not installed: {je1}"
                ) from je1
            try:
                repaired = repair_json(raw)
                raw = json.loads(repaired)
                log.warning(f"    ✅ json_repair로 복구 성공")
            except Exception as je2:
                raise ValueError(
                    f"obligations json parse 실패 (json_repair도 실패): "
                    f"json_decode={je1}, json_repair={je2}"
                ) from je2

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
    return raw


def _call_sonnet_once(client, batch: list[dict], full_text: str, label: str):
    """Sonnet 1회 호출. broken JSON 발생 시 ValueError.

    v2.7: input 축소 + json_repair fallback 적용.
    """
    batch_for_input = _strip_detail_for_verify(batch)

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
        f"검증할 의무 후보 ({len(batch_for_input)}건):\n"
        f"{json.dumps(batch_for_input, ensure_ascii=False, indent=2)}\n\n"
        f"submit_verified_obligations 도구를 호출하여 "
        f"각 의무에 verified와 verification_note(100자 이내, 따옴표·줄바꿈 금지)를 추가한 결과를 제출하라. "
        f"입력 순서를 유지하고 모든 {len(batch_for_input)}건을 반환하라."
    )

    log.info(f"  Sonnet {label} (n={len(batch)}) 호출 중...")
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
            verified_batch = _parse_obligations_from_response(raw)
            break

    if verified_batch is None:
        raise ValueError("No tool_use block found in response")
    if len(verified_batch) != len(batch):
        log.warning(f"    ⚠️ Length mismatch: input={len(batch)}, output={len(verified_batch)}")

    verified_batch = _restore_dropped_fields(verified_batch, batch)
    return verified_batch, resp.usage


def _verify_batch_with_fallback(client, batch, full_text, batch_num, total_batches):
    """v2.7: batch 전체 호출 실패 시 batch=1로 단건 재시도."""
    try:
        result, usage = _call_sonnet_once(
            client, batch, full_text, f"batch {batch_num}/{total_batches}"
        )
        return result, {
            "input_tokens": getattr(usage, "input_tokens", 0),
            "output_tokens": getattr(usage, "output_tokens", 0),
            "used_fallback": False,
        }
    except Exception as e:
        log.warning(
            f"  ⚠️ batch {batch_num} 전체 실패 ({type(e).__name__}: {str(e)[:100]}); "
            f"batch=1 fallback 시작"
        )

    results = []
    total_in = total_out = 0
    for i, ob in enumerate(batch):
        try:
            r, usage = _call_sonnet_once(
                client, [ob], full_text,
                f"batch {batch_num}.{i+1}/{total_batches} (single)"
            )
            results.extend(r)
            total_in += getattr(usage, "input_tokens", 0)
            total_out += getattr(usage, "output_tokens", 0)
        except Exception as e2:
            log.error(
                f"    ❌ obligation {batch_num}.{i+1} 단건도 실패: {str(e2)[:100]}"
            )
            ob_failed = dict(ob)
            ob_failed["verified"] = False
            ob_failed["verification_note"] = (
                f"검증 실패 (batch=1 fallback): {str(e2)[:60]}"
            )[:100]
            results.append(ob_failed)
        time.sleep(0.5)

    return results, {
        "input_tokens": total_in,
        "output_tokens": total_out,
        "used_fallback": True,
    }


def call_claude_verify(obligations, full_text, batch_size=SONNET_BATCH_SIZE):
    """v2.7: 26 cache 활용 + 13 누락 batch만 보강된 로직으로 재시도."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    verified_all: list[dict] = []
    total_in = total_out = 0
    total_batches = (len(obligations) + batch_size - 1) // batch_size
    cached_batches = 0
    refetched_batches = 0
    fallback_batches = 0

    for i in range(0, len(obligations), batch_size):
        batch = obligations[i : i + batch_size]
        batch_num = i // batch_size + 1
        batch_cache = LOCAL_TMP / f"verify_batch_{batch_num}.json"

        if batch_cache.exists():
            try:
                cached = json.loads(batch_cache.read_text(encoding="utf-8"))
                if (isinstance(cached, list) and len(cached) == len(batch)
                        and all(isinstance(x, dict) for x in cached)):
                    log.info(
                        f"Cached batch {batch_num}/{total_batches}: "
                        f"{len(cached)} obligations — skip Sonnet"
                    )
                    verified_all.extend(cached)
                    cached_batches += 1
                    continue
            except Exception as e:
                log.warning(f"  Verify cache load 실패 batch {batch_num}: {e}; refetch")

        log.info(f"Verifying batch {batch_num}/{total_batches} (n={len(batch)}) ...")
        try:
            verified_batch, usage = _verify_batch_with_fallback(
                client, batch, full_text, batch_num, total_batches
            )
            verified_all.extend(verified_batch)
            refetched_batches += 1
            if usage["used_fallback"]:
                fallback_batches += 1

            try:
                batch_cache.write_text(
                    json.dumps(verified_batch, ensure_ascii=False, indent=2),
                    encoding="utf-8"
                )
                log.info(f"  ✅ Saved: {batch_cache.name}")
            except Exception as e:
                log.warning(f"  Cache save 실패: {e}")

            total_in += usage["input_tokens"]
            total_out += usage["output_tokens"]
        except Exception as e:
            log.error(f"  ❌ Batch {batch_num} 완전 실패: {e}")
            for ob in batch:
                ob_failed = dict(ob)
                ob_failed["verified"] = False
                ob_failed["verification_note"] = f"검증 완전 실패: {str(e)[:60]}"[:100]
                verified_all.append(ob_failed)

    log.info("=" * 60)
    log.info(
        f"Verify summary — cached={cached_batches}, refetched={refetched_batches}, "
        f"fallback used={fallback_batches}"
    )
    log.info(f"  Tokens (refetched only): input={total_in:,}, output={total_out:,}")
    return verified_all, {"input_tokens": total_in, "output_tokens": total_out}


# ======================================================================
# INSERT / CSV / Main
# ======================================================================

def insert_drafts(sb, verified, meta):
    """⚠️ 현재 schema 미스매치로 실패 예정 (--dry-run 사용 권장).

    drafts 테이블에 law_id, law_version_id, source_doc_id, source_api,
    is_active, verified, verification_note 컬럼이 없음.
    """
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
    p = argparse.ArgumentParser(description="KEC 의무 추출 PoC v2.7 (S12)")
    p.add_argument("--master-id", default=KEC_MASTER_ID_DEFAULT)
    p.add_argument("--dry-run", action="store_true", default=True,
                   help="DB INSERT skip (v2.7 기본값 — schema 미스매치 회피)")
    p.add_argument("--insert", dest="dry_run", action="store_false",
                   help="실제 INSERT 시도 (현재 schema 미스매치로 실패할 것)")
    p.add_argument("--max-obligations", type=int, default=None)
    p.add_argument("--reset-cache", action="store_true",
                   help="모든 cache 삭제 후 재실행 (chunk + verify)")
    p.add_argument("--reset-verify-cache", action="store_true",
                   help="verify_batch cache만 삭제")
    args = p.parse_args()

    if args.reset_cache:
        for f in LOCAL_TMP.glob("chunk_*_obligations.json"):
            f.unlink(); log.info(f"Removed Gemini cache: {f.name}")
        for f in LOCAL_TMP.glob("verify_batch_*.json"):
            f.unlink(); log.info(f"Removed Sonnet cache: {f.name}")
    if args.reset_verify_cache:
        for f in LOCAL_TMP.glob("verify_batch_*.json"):
            f.unlink(); log.info(f"Removed Sonnet cache: {f.name}")

    sb = get_supabase()
    log.info("=" * 60)
    log.info(f"PoC version: {SOURCE_API_VERSION}")
    log.info(f"  ✅ obligation_detail 입력 제거 (broken JSON 방지)")
    log.info(f"  ✅ verification_note 100자 + 따옴표/줄바꿈 금지")
    log.info(f"  {'✅' if HAS_JSON_REPAIR else '❌ (not installed)'} json_repair fallback")
    log.info(f"  ✅ batch=1 자동 retry on failure")
    log.info(f"  Sonnet batch_size = {SONNET_BATCH_SIZE}, max_tokens = {CLAUDE_MAX_TOKENS}")
    log.info(f"  Mode: {'DRY-RUN (INSERT skip)' if args.dry_run else 'INSERT 실행'}")
    log.info("=" * 60)

    log.info("Step 1: fetch master + attachment meta")
    meta = fetch_kec_meta(sb, args.master_id)
    log.info(f"  law_name = {meta['law_name']}")
    log.info(f"  attachment = {meta['attachment_title']}")
    log.info(f"  size = {meta['file_size']:,} bytes")

    log.info("=" * 60)
    log.info("Step 2: download PDF (cached)")
    pdf_path = LOCAL_TMP / f"{meta['master_id']}.pdf"
    download_attachment(sb, meta["storage_path"], pdf_path)

    log.info("=" * 60)
    log.info("Step 3: extract text from PDF")
    full_text, _ = extract_text(pdf_path)

    log.info("=" * 60)
    log.info("Step 4: Gemini extract (chunked + cached)")
    obligations, gemini_usage = call_gemini(meta["law_name"], full_text, args.max_obligations)
    if not obligations:
        log.error("No obligations extracted, abort")
        return 1

    log.info("=" * 60)
    log.info("Step 5: Sonnet verify (v2.7 강화 + cache)")
    verified, claude_usage = call_claude_verify(obligations, full_text)

    log.info("=" * 60)
    log.info("Step 6: write CSV report")
    csv_path = LOCAL_TMP / f"{meta['master_id']}_obligations_v2_7.csv"
    write_csv(verified, csv_path)

    if args.dry_run:
        log.info("=" * 60)
        log.info("Step 7: DRY-RUN — DB INSERT skipped (v2.7 기본 모드)")
    else:
        log.info("=" * 60)
        log.info("Step 7: INSERT to law_rule_drafts (schema 미스매치 가능성 ★)")
        try:
            insert_drafts(sb, verified, meta)
        except Exception as e:
            log.error(f"INSERT 실패: {e}")
            log.error("→ 정상. drafts schema에 9개 컬럼 없음. 별도 INSERT 경로 결정 필요.")

    log.info("=" * 60)
    log.info("SUMMARY")
    log.info(f"  Total obligations: {len(verified)}")
    pass_n = sum(1 for ob in verified if isinstance(ob, dict) and ob.get("verified"))
    fail_n = sum(1 for ob in verified if isinstance(ob, dict) and ob.get("verified") is False)
    log.info(f"  Verified pass: {pass_n}, fail: {fail_n}")
    log.info(f"  Gemini tokens: in={gemini_usage['input_tokens']:,} out={gemini_usage['output_tokens']:,}")
    log.info(f"  Sonnet tokens (refetched only): in={claude_usage['input_tokens']:,} out={claude_usage['output_tokens']:,}")
    g_cost = gemini_usage["input_tokens"] / 1e6 * 1.25 + gemini_usage["output_tokens"] / 1e6 * 5
    c_cost = claude_usage["input_tokens"] / 1e6 * 3 + claude_usage["output_tokens"] / 1e6 * 15
    log.info(f"  Estimated cost: Gemini=${g_cost:.2f} + Claude=${c_cost:.2f} = ${g_cost + c_cost:.2f}")
    log.info(f"  CSV: {csv_path.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
