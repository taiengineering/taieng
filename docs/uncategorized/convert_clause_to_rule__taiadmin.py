#!/usr/bin/env python3
"""
convert_clause_to_rule.py — semantic_clause(v1.9.1) → master_rule_v2 + 3 sub tables

원칙:
- AI/LLM 호출 0%
- 모든 의미절 1:1 변환 (제외 없음)
- rule_kind 보존 (content_type → rule_kind, None → UNCLASSIFIED)
- dry-run → 검증 → apply

Spec source:
- docs/extraction/CURSOR_TASK_2026-05-08_convert_clause_to_rule.md
- docs/extraction/LEGAL_RULE_PIPELINE.md §5
"""

from __future__ import annotations

import argparse
import os
import random
import re
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

try:
    import httpx
    from supabase import Client, create_client
except ImportError:
    print("[ERROR] pip install supabase httpx", file=sys.stderr)
    sys.exit(1)


SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = (
    os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    or os.environ.get("SUPABASE_SERVICE_KEY")
    or os.environ.get("SUPABASE_KEY")
)
if not SUPABASE_URL or not SUPABASE_KEY:
    print("[ERROR] SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY 없음.", file=sys.stderr)
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

RETRY_EXCEPTIONS = (
    httpx.RemoteProtocolError,
    httpx.ConnectError,
    httpx.ReadTimeout,
    httpx.WriteTimeout,
    httpx.PoolTimeout,
    httpx.ConnectTimeout,
    httpx.NetworkError,
    ConnectionError,
)


def reset_supabase():
    global supabase
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def with_retry(func, max_retries: int = 5, initial_delay: float = 1.0):
    for attempt in range(max_retries):
        try:
            return func()
        except RETRY_EXCEPTIONS as e:
            if attempt < max_retries - 1:
                delay = initial_delay * (2 ** attempt)
                print(
                    f"  [RETRY {attempt+1}/{max_retries}] {type(e).__name__}: 대기 {delay:.1f}s + 재연결",
                    file=sys.stderr,
                )
                time.sleep(delay)
                reset_supabase()
            else:
                raise


def chunks(seq: Sequence[Any], n: int) -> Iterable[Sequence[Any]]:
    for i in range(0, len(seq), n):
        yield seq[i : i + n]


def _now_ms() -> int:
    return int(time.time() * 1000)


# =============================================================================
# Step 3 helpers
# =============================================================================

_RX_OBL_ENDING = re.compile(r"하여야\s*한다|해야\s*한다")
_RX_AUTH_ENDING = re.compile(r"할\s*수\s*있다")
_RX_PROH_ENDING = re.compile(r"아니\s*된다|금지한다")


def infer_rule_kind(content_type: Optional[str], source_text: str) -> str:
    """
    LEGAL_RULE_PIPELINE.md §5.2 정책 반영:
    - 기본은 content_type 보존
    - None/DEFINITION 이면서 의무 어말 보유 시 rule_kind 역추론
    """
    rule_kind = content_type or "UNCLASSIFIED"
    if content_type in (None, "DEFINITION"):
        s = source_text or ""
        if re.search(r"하여야\s*한다|해야\s*한다|할\s*수\s*있다|아니\s*된다|금지한다", s):
            if _RX_PROH_ENDING.search(s):
                rule_kind = "PROHIBITION"
            elif _RX_AUTH_ENDING.search(s):
                rule_kind = "AUTHORITY"
            else:
                rule_kind = "OBLIGATION"
    return rule_kind


def parse_when(cycle_text: Optional[str], action_text: Optional[str]) -> Dict[str, Any]:
    """
    CURSOR_TASK Step 3-2 / Step 6 spec.
    출력: when_cycle_type/value/unit/due_days/base_event/text_raw
    """
    when: Dict[str, Any] = {
        "when_cycle_type": None,
        "when_cycle_value": None,
        "when_cycle_unit": None,
        "when_due_days": None,
        "when_base_event": None,
        "when_text_raw": cycle_text,
    }

    if not cycle_text:
        # action_text에서 base_event 추출
        s = action_text or ""
        m = re.search(
            r"(작업\s*전|착공\s*전|운전\s*전|발생\s*시|발생\s*후|완료\s*후|즉시|지체\s*없이)",
            s,
        )
        if m:
            when["when_base_event"] = m.group(1)
            when["when_cycle_type"] = "ON_EVENT"  # DDL 값에 맞춤
        return when

    s = cycle_text

    # 매년/매월/매주/매일
    m = re.search(r"매(년|월|주|일)", s)
    if m:
        unit_map = {"년": "YEAR", "월": "MONTH", "주": "WEEK", "일": "DAY"}
        type_map = {"년": "YEARLY", "월": "MONTHLY", "주": "WEEKLY", "일": "DAILY"}
        when["when_cycle_type"] = type_map[m.group(1)]
        when["when_cycle_unit"] = unit_map[m.group(1)]
        when["when_cycle_value"] = 1
        return when

    # N년/N개월 마다 → YEARLY/MONTHLY/WEEKLY/DAILY로 매핑
    m = re.search(r"(\d+)\s*(년|개월|월|주|일)\s*마다", s)
    if m:
        unit_map = {"년": "YEAR", "개월": "MONTH", "월": "MONTH", "주": "WEEK", "일": "DAY"}
        type_map = {"년": "YEARLY", "개월": "MONTHLY", "월": "MONTHLY", "주": "WEEKLY", "일": "DAILY"}
        when["when_cycle_value"] = int(m.group(1))
        when["when_cycle_unit"] = unit_map[m.group(2)]
        when["when_cycle_type"] = type_map[m.group(2)]
        return when

    # 3) DUE
    m = re.search(r"(\d+)\s*일\s*이내", s)
    if m:
        when["when_cycle_type"] = "DUE"
        when["when_due_days"] = int(m.group(1))
        return when

    m = re.search(r"(\d+)\s*개월\s*이내", s)
    if m:
        when["when_cycle_type"] = "DUE"
        when["when_due_days"] = int(m.group(1)) * 30
        return when

    # cycle_text에 base_event 키워드
    m = re.search(r"(작업\s*전|착공\s*전|발생\s*후|완료\s*후|즉시|지체\s*없이)", s)
    if m:
        when["when_base_event"] = m.group(1)
        when["when_cycle_type"] = "ON_EVENT"
    return when


def classify_action_category(action_text: Optional[str]) -> str:
    # action_category_code — 소문자 매핑
    if not action_text:
        return "other"
    rules: List[Tuple[str, str]] = [
        (r"점검|진단|검사|확인", "inspection"),
        (r"위험성\s*평가|위해\s*평가", "risk_assessment"),
        (r"교육|훈련", "education"),
        (r"측정|계측", "measurement"),
        (r"보고|신고|통보|통지|제출", "report"),
        (r"설치|비치|구비", "installation"),
        (r"기록|보존|작성|보관", "recordkeeping"),
        (r"알림|고지|공지|공표", "notification"),
        (r"조치|시정|개선|보호", "action"),
        (r"작업\s*방법|작업\s*절차", "work_method"),
        (r"승인|허가|인가|면허", "approval"),
        (r"보호구|보호\s*장비|안전\s*장비", "protection"),
        (r"체계|시스템|구축", "system_management"),
    ]
    for pattern, code in rules:
        if re.search(pattern, action_text):
            return code
    return "other"


def classify_what_action(action_text: Optional[str]) -> str:
    """
    master_rule_v2.what_action: 동사 표제어(간단 정규식).
    NOT NULL 보장: 미분류는 '기타'.
    """
    s = action_text or ""
    if re.search(r"점검|진단|검사|확인", s):
        return "점검"
    if re.search(r"교육|훈련", s):
        return "교육"
    if re.search(r"보고|신고|통보|통지|제출", s):
        return "보고"
    if re.search(r"작성|보관|보존|기록", s):
        return "작성"
    if re.search(r"설치|비치|구비", s):
        return "설치"
    if re.search(r"측정|계측", s):
        return "측정"
    if re.search(r"승인|허가|인가|면허", s):
        return "승인"
    if re.search(r"조치|시정|개선", s):
        return "조치"
    if re.search(r"선임|지정", s):
        return "선임"
    return "기타"


def extract_scope(source_text: Optional[str]) -> Dict[str, Any]:
    """
    best-effort 키워드 기반 scope_* 추출 (보유 10.2%).
    없는 경우는 모두 NULL.
    """
    s = source_text or ""
    scope: Dict[str, Any] = {
        "scope_min_area_sqm": None,
        "scope_min_employees": None,
        "scope_min_construction_amount": None,
        # 확장 필드들은 우선 NULL (스키마가 있을 때만 insert 성공; insert 단계에서 필터링)
        "scope_industry_codes": None,
        "scope_facility_types": None,
        "scope_construction_types": None,
        "scope_process_codes": None,
        "scope_equipment_types": None,
        "scope_building_use_codes": None,
        "scope_extra": None,
    }

    # 면적: "5000제곱미터" / "5,000 m2" / "5000㎡" 정도만.
    m = re.search(r"(\d{1,3}(?:,\d{3})+|\d+)\s*(?:㎡|m2|제곱미터)", s)
    if m:
        scope["scope_min_area_sqm"] = float(m.group(1).replace(",", ""))

    # 인원: "50명 이상" 류
    m = re.search(r"(\d{1,3}(?:,\d{3})+|\d+)\s*명\s*(?:이상|초과)", s)
    if m:
        scope["scope_min_employees"] = int(m.group(1).replace(",", ""))

    # 공사금액: "5억원 이상" 류 (억/만원 단위 단순)
    m = re.search(r"(\d+(?:\.\d+)?)\s*억\s*원\s*(?:이상|초과)", s)
    if m:
        scope["scope_min_construction_amount"] = float(m.group(1)) * 100_000_000
    else:
        m = re.search(r"(\d{1,3}(?:,\d{3})+|\d+)\s*만\s*원\s*(?:이상|초과)", s)
        if m:
            scope["scope_min_construction_amount"] = float(m.group(1).replace(",", "")) * 10_000

    return scope


def calc_confidence_v19(clause: Dict[str, Any]) -> float:
    """
    CURSOR_TASK Step 3-8 / §7 옵션 B.
    """
    content_type = clause.get("content_type")
    if content_type in ("STATEMENT", "DELEGATION", "DEFINITION"):
        return 0.5

    has_who = bool((clause.get("executor_text") or "").strip())
    has_what = bool((clause.get("action_text") or "").strip())
    has_where = bool(clause.get("sectors"))
    has_why = bool((clause.get("source_text") or "").strip())

    if not (has_who and has_what and has_where and has_why):
        miss = 4 - sum([has_who, has_what, has_where, has_why])
        return max(0.0, 0.5 - miss * 0.1)

    confidence = 0.7

    action_text = clause.get("action_text") or ""
    if clause.get("cycle_text") or re.search(
        r"작업\s*전|착공\s*전|발생\s*후|완료\s*후|즉시|지체\s*없이|\d+일\s*이내",
        action_text,
    ):
        confidence += 0.075
    if clause.get("form_token"):
        confidence += 0.075
    if clause.get("recipient_text"):
        confidence += 0.075
    if clause.get("condition_text"):
        confidence += 0.075

    return float(min(confidence, 1.0))


def generate_rule_code(article_meta: Dict[str, Any], clause: Dict[str, Any]) -> str:
    """
    rule_code UNIQUE 보장:
    - law_id 앞 4자
    - article_no
    - source_part_id 앞 4자  (paragraph 식별)
    - clause_seq

    예: LAW_0782_ART_19_P0a54_C1

    같은 paragraph 내에서 (source_part_id, clause_seq) 조합은 unique
    → 자연키 매칭에서 100% 매칭으로 검증됨
    """
    law_short = str(article_meta.get("source_law_id") or "00000000")[:8]
    article_no = article_meta.get("article_no") or "0"
    part_short = str(clause.get("source_part_id") or "00000000")[:8]
    clause_seq = clause.get("clause_seq", 0)
    return f"LAW_{law_short}_ART_{article_no}_P{part_short}_C{clause_seq}"


def _format_why_citation(article_meta: Dict[str, Any]) -> str:
    law_name = (article_meta.get("law_name") or "").strip()
    article_no = article_meta.get("article_no")
    if article_no is None:
        article_ref = "제?조"
    else:
        s = str(article_no).strip()
        article_ref = s if (s.startswith("제") and "조" in s) else f"제{s}조"
    return f"{law_name} {article_ref}".strip()


def split_conditions(condition_text: str) -> List[str]:
    if not condition_text:
        return []
    parts = re.split(r"[,;]\s*|또는|또한", condition_text)
    out = []
    for p in parts:
        s = (p or "").strip()
        if s:
            out.append(s)
    return out[:20]


# =============================================================================
# Step 1~2: fetch
# =============================================================================


def fetch_clauses(sample_size: int, start_from: int = 0) -> List[Dict[str, Any]]:
    """페이지네이션. Supabase default 1000 limit 우회."""
    all_clauses: List[Dict[str, Any]] = []
    offset = max(0, int(start_from))
    sample_size = int(sample_size)

    sel = (
        "id, source_part_id, source_article_id, clause_seq, "
        "source_text, source_part_text, "
        "executor_text, recipient_text, alternative_kept_text, "
        "action_text, cycle_text, condition_text, exception_text, form_token, "
        "content_type, applied_rules, decomposition_version, "
        "needs_review, review_reason, sectors"
    )

    while len(all_clauses) < sample_size:
        remaining = sample_size - len(all_clauses)
        chunk_size = min(1000, remaining)

        def _do():
            return (
                supabase.from_("semantic_clause")
                .select(sel)
                .order("id")
                .range(offset, offset + chunk_size - 1)
                .execute()
            )

        res = with_retry(_do)
        batch = res.data or []
        if not batch:
            break
        all_clauses.extend(batch)
        if len(batch) < chunk_size:
            break  # 더 이상 없음
        offset += chunk_size

    print(
        f"[INFO] fetched semantic_clause: {len(all_clauses)} rows (sample_size={sample_size}, start_from={start_from})"
    )
    return all_clauses[:sample_size]


def get_sectors_for_rule(clause: Dict[str, Any]) -> List[str]:
    sectors = clause.get("sectors")
    if sectors and isinstance(sectors, list) and len(sectors) > 0:
        return sectors
    # INACTIVE는 모두 sector 미상 → 빈 배열 (DDL 정정 후 허용)
    return []


def fetch_article_meta(article_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    article_id → (law_id, law_name, article_no, article_internal_key) 매핑.

    law_article에는 law_name이 없으므로 law_master에서 추가 JOIN.
    master_rule_v2.source_law_id는 law_article.law_id 값을 그대로 사용.
    """
    ids = [x for x in (article_ids or []) if x]
    if not ids:
        return {}

    # 1. law_article 가져오기 (law_id + 메타)
    article_meta_map: Dict[str, Dict[str, Any]] = {}
    for i in range(0, len(ids), 200):
        chunk = ids[i : i + 200]

        def _do_articles():
            return (
                supabase.from_("law_article")
                .select("id, law_id, article_no, article_internal_key")
                .in_("id", chunk)
                .execute()
            )

        res = with_retry(_do_articles)
        for a in (res.data or []):
            article_meta_map[a["id"]] = {
                "source_law_id": a.get("law_id"),  # master_rule_v2.source_law_id로 사용
                "article_no": a.get("article_no"),
                "article_internal_key": a.get("article_internal_key"),
                "law_name": "",  # 아래에서 JOIN
            }

    # 2. law_master에서 law_name JOIN
    law_ids = list(
        {
            m["source_law_id"]
            for m in article_meta_map.values()
            if m.get("source_law_id")
        }
    )
    if law_ids:
        for i in range(0, len(law_ids), 200):
            chunk = law_ids[i : i + 200]

            def _do_laws():
                return (
                    supabase.from_("law_master")
                    .select("id, law_name, law_name_short")
                    .in_("id", chunk)
                    .execute()
                )

            res = with_retry(_do_laws)
            law_name_map = {
                l["id"]: (l.get("law_name") or l.get("law_name_short") or "")
                for l in (res.data or [])
            }
            for meta in article_meta_map.values():
                law_id = meta.get("source_law_id")
                if law_id in law_name_map:
                    meta["law_name"] = law_name_map[law_id]

    return article_meta_map


# =============================================================================
# Step 3: convert
# =============================================================================


def convert_clause_to_rule_row(clause: Dict[str, Any], article_meta: Dict[str, Any]) -> Dict[str, Any]:
    rule_kind = infer_rule_kind(clause.get("content_type"), clause.get("source_text") or "")
    when = parse_when(clause.get("cycle_text"), clause.get("action_text"))
    what_action = classify_what_action(clause.get("action_text"))
    action_cat = classify_action_category(clause.get("action_text"))
    confidence = calc_confidence_v19(clause)
    scope = extract_scope(clause.get("source_text"))

    sectors = get_sectors_for_rule(clause)

    why_summary = (clause.get("source_text") or "")[:500]
    why_citation = _format_why_citation(article_meta)

    return {
        "rule_code": generate_rule_code(article_meta, clause),
        "source_clause_id": clause["id"],
        "source_article_id": clause["source_article_id"],
        "source_law_id": article_meta.get("source_law_id"),
        "rule_kind": rule_kind,
        **when,
        "what_action": what_action,
        "what_target": None,
        "what_action_text_raw": clause.get("action_text"),
        "how_method": None,
        "how_form": clause.get("form_token"),
        "sectors": sectors,
        **scope,
        "why_obligation_summary": why_summary,
        "why_law_citation": why_citation,
        "action_category_code": action_cat,
        "generation_method": "AUTO_REGEX",
        "generation_confidence": confidence,
        "status": "DRAFT",
        "needs_review": bool(clause.get("needs_review")),
        "review_reason": clause.get("review_reason"),
    }


def build_sub_rows(
    clause: Dict[str, Any],
    rule_id: str,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Step 5~6: master_rule_executor / condition / exception rows
    """
    executors: List[Dict[str, Any]] = []
    conds: List[Dict[str, Any]] = []
    excs: List[Dict[str, Any]] = []

    ex = (clause.get("executor_text") or "").strip()
    if ex:
        executors.append(
            {
                "rule_id": rule_id,
                "role": "EXECUTOR",
                "role_label": ex,
                "text_raw": ex,
                "sort_order": 1,
            }
        )

    rec = (clause.get("recipient_text") or "").strip()
    if rec:
        executors.append(
            {
                "rule_id": rule_id,
                "role": "RECIPIENT",
                "role_label": rec,
                "text_raw": rec,
                "sort_order": 2,
            }
        )

    alt = (clause.get("alternative_kept_text") or "").strip()
    if alt:
        executors.append(
            {
                "rule_id": rule_id,
                "role": "ALTERNATIVE",
                "role_label": alt,
                "text_raw": alt,
                "sort_order": 3,
            }
        )

    cond_text = (clause.get("condition_text") or "").strip()
    if cond_text:
        parts = split_conditions(cond_text)
        if not parts:
            parts = [cond_text]
        for i, p in enumerate(parts):
            conds.append(
                {
                    "rule_id": rule_id,
                    "condition_text": p,
                    "sort_order": i + 1,
                }
            )

    exc_text = (clause.get("exception_text") or "").strip()
    if exc_text:
        excs.append(
            {
                "rule_id": rule_id,
                "exception_text": exc_text,
                "sort_order": 1,
            }
        )

    return executors, conds, excs


# =============================================================================
# Step 4~6: insert (apply)
# =============================================================================


TABLES_TO_TRUNCATE = [
    "master_rule_executor",
    "master_rule_condition",
    "master_rule_exception",
    "master_rule_v2",
]


def truncate_tables_best_effort():
    """
    --truncate-first 옵션.
    주의: Supabase REST로 TRUNCATE는 직접 불가하므로, 서버에 정의된 RPC가 있는 경우 우선 사용.
    RPC가 없으면 안전을 위해 실패 처리.
    """
    # 가능한 RPC 시도 (프로젝트마다 이름 다를 수 있음)
    rpc_candidates = [
        "truncate_master_rule_v2_all",
        "truncate_master_rule_v2",
        "truncate_rule_tables_v2",
    ]
    last_err: Optional[Exception] = None
    for fn in rpc_candidates:
        try:
            with_retry(lambda: supabase.rpc(fn, {}).execute())
            print(f"[TRUNCATE] RPC {fn} 성공")
            return
        except Exception as e:
            last_err = e
            continue
    raise RuntimeError(
        "truncate-first 실패: TRUNCATE용 RPC를 찾지 못했습니다. "
        "DB에 안전한 RPC를 추가하거나 수동 TRUNCATE 후 재실행하세요."
    ) from last_err


def insert_rules_apply(
    clauses: List[Dict[str, Any]],
    article_meta_map: Dict[str, Dict[str, Any]],
    batch_size: int = 100,
) -> Dict[str, str]:
    """
    Step 4~6 apply:
    - master_rule_v2 insert (batch)
    - sub tables insert (batch)
    반환: clause_id → rule_id mapping
    """
    # 1) build rule rows
    rule_rows: List[Dict[str, Any]] = []
    for c in clauses:
        am = article_meta_map.get(c["source_article_id"])
        if not am:
            raise RuntimeError(f"article_meta 누락: source_article_id={c['source_article_id']}")
        rule_rows.append(convert_clause_to_rule_row(c, am))

    clause_to_rule_id: Dict[str, str] = {}

    # 2) insert master_rule_v2
    for chunk in chunks(rule_rows, batch_size):
        def _do():
            # returning=representation: insert 결과에 id가 포함되도록 기대
            return supabase.table("master_rule_v2").insert(list(chunk)).execute()

        res = with_retry(_do)
        inserted = res.data or []
        # 안전: source_clause_id로 다시 매핑
        for row in inserted:
            scid = row.get("source_clause_id")
            rid = row.get("id")
            if scid and rid:
                clause_to_rule_id[str(scid)] = str(rid)

    # 3) build + insert sub rows
    ex_rows: List[Dict[str, Any]] = []
    cond_rows: List[Dict[str, Any]] = []
    exc_rows: List[Dict[str, Any]] = []

    for c in clauses:
        rid = clause_to_rule_id.get(str(c["id"]))
        if not rid:
            raise RuntimeError(f"insert 결과 누락: clause_id={c['id']}")
        ex, cond, exc = build_sub_rows(c, rid)
        ex_rows.extend(ex)
        cond_rows.extend(cond)
        exc_rows.extend(exc)

    for tbl, rows in [
        ("master_rule_executor", ex_rows),
        ("master_rule_condition", cond_rows),
        ("master_rule_exception", exc_rows),
    ]:
        if not rows:
            continue
        for chunk in chunks(rows, batch_size):
            with_retry(lambda: supabase.table(tbl).insert(list(chunk)).execute())

    return clause_to_rule_id


# =============================================================================
# Step 7: stats / display
# =============================================================================


def print_sample(rules: List[Dict[str, Any]], k: int = 5):
    print("\n[SAMPLE 출력 5건]")
    for i, r in enumerate(rules[:k]):
        print("  ─────────────────────────────────────────────")
        print(f"  [{i+1}] rule_code={r.get('rule_code')}")
        print(f"      rule_kind={r.get('rule_kind')}")
        print(f"      what_action={r.get('what_action')} action_category_code={r.get('action_category_code')}")
        print(f"      when={r.get('when_cycle_type')} {r.get('when_cycle_value')} {r.get('when_cycle_unit')} due={r.get('when_due_days')} base={r.get('when_base_event')}")
        print(f"      sectors={r.get('sectors')}")
        print(f"      why_law_citation={r.get('why_law_citation')}")


def dry_run_report(
    clauses: List[Dict[str, Any]],
    article_meta_map: Dict[str, Dict[str, Any]],
):
    rules = []
    rule_kind_counts = Counter()
    conf_sum = 0.0
    needs_review = 0
    ex_cnt = 0
    rec_cnt = 0
    alt_cnt = 0
    cond_rows = 0
    exc_rows = 0

    for c in clauses:
        am = article_meta_map.get(c["source_article_id"]) or {}
        r = convert_clause_to_rule_row(c, am)
        rules.append(r)
        rule_kind_counts[r["rule_kind"]] += 1
        conf_sum += float(r.get("generation_confidence") or 0.0)
        if r.get("needs_review"):
            needs_review += 1

        ex, cond, exc = build_sub_rows(c, rule_id="(dry-run)")
        for x in ex:
            if x["role"] == "EXECUTOR":
                ex_cnt += 1
            elif x["role"] == "RECIPIENT":
                rec_cnt += 1
            elif x["role"] == "ALTERNATIVE":
                alt_cnt += 1
        cond_rows += len(cond)
        exc_rows += len(exc)

    n = len(clauses)
    avg_conf = conf_sum / n if n else 0.0

    print("======================================================================")
    print("[semantic_clause → master_rule_v2 — dry-run]")
    print("======================================================================")
    print(f"\n[CONVERT] {n} clauses → {n} rules (1:1)")
    print(f"[INSERT 예정] master_rule_v2: {n} rows")
    print(f"[INSERT 예정] master_rule_executor: {ex_cnt + rec_cnt + alt_cnt} rows (executor {ex_cnt} + recipient {rec_cnt} + alt {alt_cnt})")
    print(f"[INSERT 예정] master_rule_condition: {cond_rows} rows")
    print(f"[INSERT 예정] master_rule_exception: {exc_rows} rows")

    print("\n[STATS] rule_kind:")
    for k, v in rule_kind_counts.most_common():
        print(f"  {k:<12}: {v}")

    print(f"\n[STATS] confidence avg: {avg_conf:.2f}")
    print(f"[STATS] needs_review: {needs_review} / {n} ({(100.0*needs_review/n if n else 0.0):.1f}%)")
    print_sample(rules, k=5)
    print("\n[DRY-RUN 종료] 실제 DB 쓰기 없음. 적용은 --apply 사용.\n")


# =============================================================================
# main
# =============================================================================


def main():
    parser = argparse.ArgumentParser(description="semantic_clause → master_rule_v2 변환 (v1.9.1)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument(
        "--truncate-first",
        action="store_true",
        help="적용 전 master_rule_v2 + 3 부속 테이블 비움 (RPC 필요)",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=100,
        help="처리할 의미절 수. 전체 처리는 100000+ 명시 권장.",
    )
    parser.add_argument(
        "--start-from",
        type=int,
        default=0,
        help="몇 번째 의미절부터 시작 (재개용, id 정렬 기준 range offset)",
    )
    args = parser.parse_args()

    if args.apply and args.dry_run:
        print("[ERROR] --dry-run 과 --apply 는 동시에 사용할 수 없습니다.", file=sys.stderr)
        sys.exit(2)
    if not args.apply and not args.dry_run:
        print("[ERROR] --dry-run 또는 --apply 중 하나를 지정하세요.", file=sys.stderr)
        sys.exit(2)

    if args.apply and "--sample-size" not in sys.argv:
        print(
            "[WARN] --apply 실행 시 --sample-size 명시를 강력 권장합니다. "
            f"(현재 default={args.sample_size})",
            file=sys.stderr,
        )

    sample_size = int(args.sample_size)
    if sample_size <= 0:
        print("[ERROR] --sample-size 는 1 이상이어야 합니다.", file=sys.stderr)
        sys.exit(2)

    clauses = fetch_clauses(sample_size=sample_size, start_from=args.start_from)
    print(f"[INFO] fetched semantic_clause: {len(clauses)} rows (sample_size={sample_size}, start_from={args.start_from})")

    article_meta_map = fetch_article_meta([c.get("source_article_id") for c in clauses])
    missing_meta = sum(1 for c in clauses if c.get("source_article_id") not in article_meta_map)
    if missing_meta:
        print(f"[WARN] article_meta 누락: {missing_meta} clauses (INSERT 시 실패 가능)", file=sys.stderr)

    if args.dry_run:
        dry_run_report(clauses, article_meta_map)
        return

    # apply
    if args.truncate_first:
        print("[TRUNCATE] truncate-first requested.")
        truncate_tables_best_effort()

    start_ms = _now_ms()
    mapping = insert_rules_apply(clauses, article_meta_map, batch_size=100)
    elapsed = (_now_ms() - start_ms) / 1000.0
    print(f"[DONE] inserted {len(mapping)} rules in {elapsed:.1f}s")


if __name__ == "__main__":
    main()

