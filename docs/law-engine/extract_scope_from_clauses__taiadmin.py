#!/usr/bin/env python3
"""
extract_scope_from_clauses.py — semantic_clause → master_rule_scope + master_rule_scope_threshold

핵심 원칙 (위반 시 작업 폐기):
1) 키워드 사전에 명시된 매핑만 사용 (사전 외 단어 매핑 금지)
2) 정규식 명시 패턴만 사용 (변형/추정 금지)
3) 매핑 안 되면 NULL + needs_review=true (default 0/1/-1 채움 금지)
4) AI/LLM 호출 0%

Spec source:
- docs/extraction/CURSOR_TASK_2026-05-08_extract_scope.md
- docs/extraction/LEGAL_RULE_PIPELINE.md
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
from collections import Counter, defaultdict
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
                delay = initial_delay * (2**attempt)
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


# =============================================================================
# Step 2. layer 분류 (ONLY 명시 패턴)
# =============================================================================


def determine_layer(law_name: str) -> str:
    """ONLY 명시된 패턴만. 이외는 '본법령'."""
    if not law_name:
        return "본법령"
    if "시행령" in law_name:
        return "시행령"
    if "시행규칙" in law_name:
        return "시행규칙"
    if "고시" in law_name:
        return "고시"
    if "기준" in law_name or "규정" in law_name:
        return "기준규정"
    return "본법령"


# =============================================================================
# Step 0. normalization (의미해석 0%: 문자 치환만)
# =============================================================================


def normalize_text(text: Optional[str]) -> str:
    """
    문자 정규화 (의미해석 아님).
    - 가운뎃점: 'ㆍ' → '·'
    """
    if not text:
        return ""
    return str(text).replace("ㆍ", "·")


# =============================================================================
# Step 3. 분류형 차원 추출 — 키워드 사전만
# =============================================================================


BUILDING_USE_DICT: Dict[str, str] = {
    "단독주택": "01_단독주택",
    "공동주택": "02_공동주택",
    "아파트": "02_공동주택",
    "연립주택": "02_공동주택",
    "다세대주택": "02_공동주택",
    "기숙사": "02_공동주택",
    "제1종근린생활시설": "03_제1종근린생활시설",
    "근린생활시설": "03_제1종근린생활시설",
    "제2종근린생활시설": "04_제2종근린생활시설",
    "문화및집회시설": "05_문화및집회시설",
    "문화시설": "05_문화및집회시설",
    "집회시설": "05_문화및집회시설",
    "공연장": "05_문화및집회시설",
    "관람장": "05_문화및집회시설",
    "전시장": "05_문화및집회시설",
    "종교시설": "06_종교시설",
    "판매시설": "07_판매시설",
    "대형마트": "07_판매시설",
    "백화점": "07_판매시설",
    "쇼핑센터": "07_판매시설",
    "운수시설": "08_운수시설",
    "의료시설": "09_의료시설",
    "병원": "09_의료시설",
    "종합병원": "09_의료시설",
    "의원": "09_의료시설",
    "요양병원": "09_의료시설",
    "교육연구시설": "10_교육연구시설",
    "학교": "10_교육연구시설",
    "대학교": "10_교육연구시설",
    "연구소": "10_교육연구시설",
    "노유자시설": "11_노유자시설",
    "아동관련시설": "11_노유자시설",
    "노인복지시설": "11_노유자시설",
    "수련시설": "12_수련시설",
    "운동시설": "13_운동시설",
    "체육관": "13_운동시설",
    "경기장": "13_운동시설",
    "업무시설": "14_업무시설",
    "오피스텔": "14_업무시설",
    "숙박시설": "15_숙박시설",
    "호텔": "15_숙박시설",
    "여관": "15_숙박시설",
    "위락시설": "16_위락시설",
    "공장": "17_공장",
    "창고시설": "18_창고시설",
    "창고": "18_창고시설",
    "위험물저장및처리시설": "19_위험물저장및처리시설",
    "위험물시설": "19_위험물저장및처리시설",
    "주유소": "19_위험물저장및처리시설",
    "가스충전소": "19_위험물저장및처리시설",
    "자동차관련시설": "20_자동차관련시설",
    "주차장": "20_자동차관련시설",
    "세차장": "20_자동차관련시설",
    "동물및식물관련시설": "21_동물및식물관련시설",
    "축사": "21_동물및식물관련시설",
    "자원순환관련시설": "22_자원순환관련시설",
    "폐기물처리시설": "22_자원순환관련시설",
    "교정및군사시설": "23_교정및군사시설",
    "교정시설": "23_교정및군사시설",
    "군사시설": "23_교정및군사시설",
    "방송통신시설": "24_방송통신시설",
    "방송국": "24_방송통신시설",
    "전신전화국": "24_방송통신시설",
    "발전시설": "25_발전시설",
    "발전소": "25_발전시설",
    "묘지관련시설": "26_묘지관련시설",
    "봉안당": "26_묘지관련시설",
    "관광휴게시설": "27_관광휴게시설",
    "장례시설": "28_장례시설",
    "야영장시설": "29_야영장시설",
    "야영장": "29_야영장시설",
}


def extract_building_use(text: str) -> List[str]:
    """사전에 명시된 키워드만 매핑. 사전 외 단어는 매핑 안 함."""
    text = normalize_text(text)
    if not text:
        return []
    found = set()
    for kw, code in BUILDING_USE_DICT.items():
        if kw in text:
            found.add(code)
    return sorted(list(found))


INDUSTRY_DICT: Dict[str, str] = {
    "제조업": "C",
    "건설업": "F",
    "농업": "A",
    "임업": "A",
    "어업": "A",
    "광업": "B",
    "도매업": "G",
    "소매업": "G",
    "판매업": "G",
    "운수업": "H",
    "운수창고업": "H",
    "숙박업": "I",
    "음식점업": "I",
    "정보통신업": "J",
    "금융업": "K",
    "보험업": "K",
    "부동산업": "L",
    "교육서비스업": "P",
    "보건업": "Q",
    "사회복지서비스업": "Q",
    "예술스포츠업": "R",
}


def extract_industry(text: str) -> List[str]:
    text = normalize_text(text)
    if not text:
        return []
    found = set()
    for kw, code in INDUSTRY_DICT.items():
        if kw in text:
            found.add(code)
    return sorted(list(found))


CONSTRUCTION_TYPE_DICT: Dict[str, str] = {
    "토목공사": "civil",
    "건축공사": "building",
    "전기공사": "electrical",
    "통신공사": "communication",
    "소방공사": "firefighting",
    "소방시설공사": "firefighting",
    "정보통신공사": "information",
    "문화재수리공사": "cultural_heritage",
    "조경공사": "landscaping",
}


def extract_construction_type(text: str) -> List[str]:
    text = normalize_text(text)
    if not text:
        return []
    found = set()
    for kw, code in CONSTRUCTION_TYPE_DICT.items():
        if kw in text:
            found.add(code)
    return sorted(list(found))


FACILITY_KEYWORDS: List[str] = [
    "공장",
    "창고",
    "사업장",
    "작업장",
    "공사장",
    "발전시설",
    "변전소",
    "송전탑",
    "저장시설",
    "저장탱크",
    "가스시설",
    "폐수처리시설",
    "대기오염방지시설",
    "소각시설",
    "매립시설",
    "가축사육시설",
    "도축시설",
    "항만시설",
    "공항시설",
    "철도시설",
]


def extract_facility(text: str) -> List[str]:
    text = normalize_text(text)
    if not text:
        return []
    found = set()
    for kw in FACILITY_KEYWORDS:
        if kw in text:
            found.add(kw)
    return sorted(list(found))


EQUIPMENT_KEYWORDS: List[str] = [
    "압력용기",
    "보일러",
    "냉동기",
    "크레인",
    "리프트",
    "곤돌라",
    "승강기",
    "에스컬레이터",
    "지게차",
    "굴착기",
    "포크레인",
    "고압가스용기",
    "고압가스저장탱크",
    "전기설비",
    "전기시설",
    "용접기",
    "연마기",
    "프레스",
    "컨베이어",
    "호이스트",
]


def extract_equipment(text: str) -> List[str]:
    text = normalize_text(text)
    if not text:
        return []
    found = set()
    for kw in EQUIPMENT_KEYWORDS:
        if kw in text:
            found.add(kw)
    return sorted(list(found))


PROCESS_KEYWORDS: List[str] = [
    "용접",
    "용단",
    "도장",
    "열처리",
    "주조",
    "단조",
    "연마",
    "절단",
    "도금",
    "표면처리",
    "화학반응",
    "증류",
    "발효",
    "건조",
]


def extract_process(text: str) -> List[str]:
    text = normalize_text(text)
    if not text:
        return []
    found = set()
    for kw in PROCESS_KEYWORDS:
        if kw in text:
            found.add(kw)
    return sorted(list(found))


def get_sectors(clause: Dict[str, Any]) -> List[str]:
    s = clause.get("sectors")
    return s if isinstance(s, list) else []


# =============================================================================
# Step 4. 임계값 추출 (4값) — 정규식 패턴만
# =============================================================================


THRESHOLD_PATTERNS: List[Dict[str, str]] = [
    {
        "name": "employee",
        "pattern": r"(?P<criterion>상시근로자|근로자)(?:\s*수)?(?:\s*(?:가|이|은|는|의))?\s*(?P<value>\d+(?:,\d{3})*)\s*(?P<unit>명|인)\s*(?P<op>이상|이하|초과|미만)",
        "criterion_code": "employee",
    },
    {
        "name": "area",
        "pattern": r"(?P<criterion>연면적|대지면적|건축면적|면적)(?:\s*수)?(?:\s*(?:가|이|은|는|의))?\s*(?P<value>\d+(?:,\d{3})*(?:\.\d+)?)\s*(?P<unit>㎡|제곱미터|평방미터|m²|m2|평)\s*(?P<op>이상|이하|초과|미만)",
        "criterion_code": "area_floor",
    },
    {
        "name": "construction_amount",
        "pattern": r"(?P<criterion>공사금액|총공사금액|도급금액|계약금액)(?:\s*수)?(?:\s*(?:가|이|은|는|의))?\s*(?P<value>\d+(?:,\d{3})*(?:\.\d+)?)\s*(?P<unit>억\s*원|만\s*원|억원|억|만원|천만원|백만원|원)\s*(?P<op>이상|이하|초과|미만)",
        "criterion_code": "construction_amount",
    },
    {
        "name": "capacity_power",
        "pattern": r"(?P<criterion>용량|정격용량|발전용량|수전용량|설비용량|처리용량|처리량)(?:\s*수)?(?:\s*(?:가|이|은|는|의))?\s*(?P<value>\d+(?:,\d{3})*(?:\.\d+)?)\s*(?P<unit>kW|MW|kVA)\s*(?P<op>이상|이하|초과|미만)",
        "criterion_code": "capacity_power",
    },
    {
        "name": "height",
        "pattern": r"(?P<criterion>높이|건축물높이)(?:\s*수)?(?:\s*(?:가|이|은|는|의))?\s*(?P<value>\d+(?:\.\d+)?)\s*(?P<unit>m|미터|층)\s*(?P<op>이상|이하|초과|미만)",
        "criterion_code": "height",
    },
    {
        "name": "capacity_weight",
        "pattern": r"(?P<criterion>저장량|처리량|보관량|반입량)(?:\s*수)?(?:\s*(?:가|이|은|는|의))?\s*(?P<value>\d+(?:,\d{3})*(?:\.\d+)?)\s*(?P<unit>톤|t|kg|㎏)\s*(?P<op>이상|이하|초과|미만)",
        "criterion_code": "capacity_weight",
    },
    {
        "name": "pressure",
        "pattern": r"(?P<criterion>압력|작업압력|설계압력)(?:\s*수)?(?:\s*(?:가|이|은|는|의))?\s*(?P<value>\d+(?:\.\d+)?)\s*(?P<unit>MPa|kPa|bar|kgf/cm²)\s*(?P<op>이상|이하|초과|미만)",
        "criterion_code": "capacity_pressure",
    },
    {
        "name": "count_unit",
        "pattern": r"(?P<criterion>세대수|호수|동수)(?:\s*수)?(?:\s*(?:가|이|은|는|의))?\s*(?P<value>\d+(?:,\d{3})*)\s*(?P<unit>세대|호|동|실)\s*(?P<op>이상|이하|초과|미만)",
        "criterion_code": "count_unit",
    },
]

OPERATOR_MAP: Dict[str, str] = {
    "이상": "GTE",
    "이하": "LTE",
    "초과": "GT",
    "미만": "LT",
}


def extract_thresholds(text: str) -> List[Dict[str, Any]]:
    """4값 분해. 매핑 안 되면 [] 반환 (추정 금지)."""
    text = normalize_text(text)
    if not text:
        return []

    thresholds: List[Dict[str, Any]] = []
    for pattern_def in THRESHOLD_PATTERNS:
        for m in re.finditer(pattern_def["pattern"], text):
            value_str = (m.group("value") or "").replace(",", "")
            unit = m.group("unit")
            op_kr = m.group("op")

            try:
                numeric_value = float(value_str)
            except ValueError:
                continue

            operator = OPERATOR_MAP.get(op_kr)
            if not operator:
                continue

            thresholds.append(
                {
                    "criterion": m.group("criterion"),
                    "criterion_code": pattern_def["criterion_code"],
                    "numeric_value": numeric_value,
                    "unit": unit,
                    "operator": operator,
                    "normalized_value": None,
                    "normalized_unit": None,
                    "source_text": m.group(0),
                }
            )

    return thresholds


# =============================================================================
# Step 1. semantic_clause SELECT (pagination)
# =============================================================================


def fetch_clauses(
    start_from: int = 0,
    sample_size: int = 100000,
    with_threshold_only: bool = False,
) -> List[Dict[str, Any]]:
    """
    with_threshold_only=True 시 임계값 키워드 보유 의미절만 SELECT
    (4값 추출 알고리즘 검증용)
    """
    all_clauses: List[Dict[str, Any]] = []
    offset = max(0, int(start_from))
    sample_size = int(sample_size)

    sel = (
        "id, source_part_id, source_article_id, "
        "source_text, content_type, action_text, executor_text, "
        "sectors, condition_text, exception_text"
    )

    while len(all_clauses) < sample_size:
        chunk_size = min(1000, sample_size - len(all_clauses))

        def _do():
            q = supabase.from_("semantic_clause").select(sel)
            if with_threshold_only:
                q = q.or_(
                    "source_text.ilike.%근로자%이상%,"
                    "source_text.ilike.%근로자%이하%,"
                    "source_text.ilike.%근로자%초과%,"
                    "source_text.ilike.%근로자%미만%,"
                    "source_text.ilike.%면적%이상%,"
                    "source_text.ilike.%면적%이하%,"
                    "source_text.ilike.%면적%초과%,"
                    "source_text.ilike.%면적%미만%,"
                    "source_text.ilike.%공사금액%이상%,"
                    "source_text.ilike.%공사금액%이하%,"
                    "source_text.ilike.%공사금액%초과%,"
                    "source_text.ilike.%공사금액%미만%,"
                    "source_text.ilike.%용량%이상%,"
                    "source_text.ilike.%용량%이하%,"
                    "source_text.ilike.%용량%초과%,"
                    "source_text.ilike.%용량%미만%,"
                    "source_text.ilike.%높이%이상%,"
                    "source_text.ilike.%높이%이하%,"
                    "source_text.ilike.%높이%초과%,"
                    "source_text.ilike.%높이%미만%,"
                    "source_text.ilike.%저장량%이상%,"
                    "source_text.ilike.%저장량%이하%,"
                    "source_text.ilike.%저장량%초과%,"
                    "source_text.ilike.%저장량%미만%,"
                    "source_text.ilike.%압력%이상%,"
                    "source_text.ilike.%압력%이하%,"
                    "source_text.ilike.%압력%초과%,"
                    "source_text.ilike.%압력%미만%,"
                    "source_text.ilike.%세대수%이상%"
                    ",source_text.ilike.%세대수%이하%"
                    ",source_text.ilike.%세대수%초과%"
                    ",source_text.ilike.%세대수%미만%"
                )
            return q.order("id").range(offset, offset + chunk_size - 1).execute()

        res = with_retry(_do)
        batch = res.data or []
        if not batch:
            break
        all_clauses.extend(batch)
        if len(batch) < chunk_size:
            break
        offset += chunk_size

    # 중복 제거 (with_retry partial success 시 같은 batch 재수집 방지)
    seen_ids = set()
    deduped: List[Dict[str, Any]] = []
    for c in all_clauses:
        cid = c.get("id")
        if cid and cid not in seen_ids:
            seen_ids.add(cid)
            deduped.append(c)
    if len(deduped) < len(all_clauses):
        print(
            f"[DEDUPE] fetch_clauses: {len(all_clauses)} → {len(deduped)} "
            f"({len(all_clauses) - len(deduped)}건 중복 제거)",
            file=sys.stderr,
        )
    return deduped[:sample_size]


def fetch_article_meta(article_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    article_id → (source_law_id, law_name) 매핑.
    - law_article.law_id 사용
    - law_master JOIN으로 law_name 조회
    """
    ids = [x for x in (article_ids or []) if x]
    if not ids:
        return {}

    article_meta_map: Dict[str, Dict[str, Any]] = {}
    for i in range(0, len(ids), 200):
        chunk = ids[i : i + 200]

        def _do_articles():
            return (
                supabase.from_("law_article")
                .select("id, law_id")
                .in_("id", chunk)
                .execute()
            )

        res = with_retry(_do_articles)
        for a in (res.data or []):
            article_meta_map[a["id"]] = {
                "source_law_id": a.get("law_id"),
                "law_name": "",
            }

    law_ids = list(
        {
            m["source_law_id"]
            for m in article_meta_map.values()
            if m.get("source_law_id")
        }
    )
    if law_ids:
        law_name_map: Dict[str, str] = {}
        for i in range(0, len(law_ids), 200):
            chunk = law_ids[i : i + 200]

            def _do_laws():
                return (
                    supabase.from_("law_master")
                    .select("id, law_name")
                    .in_("id", chunk)
                    .execute()
                )

            res = with_retry(_do_laws)
            law_name_map.update(
                {
                    l["id"]: (l.get("law_name") or "")
                    for l in (res.data or [])
                    if l.get("id")
                }
            )

        for meta in article_meta_map.values():
            lid = meta.get("source_law_id")
            if lid in law_name_map:
                meta["law_name"] = law_name_map[lid]

    return article_meta_map


# =============================================================================
# Step 5. process clause → scope + thresholds
# =============================================================================


def calculate_confidence(has_classification: bool, has_threshold: bool, has_sectors: bool) -> float:
    """신뢰도. AI 유추 없음. 추출된 차원 수만 카운트."""
    score = 0.0
    if has_sectors:
        score += 0.3
    if has_classification:
        score += 0.4
    if has_threshold:
        score += 0.3
    return float(score)


def process_clause(
    clause: Dict[str, Any],
    article_meta: Dict[str, Any],
) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    의미절 1개 → master_rule_scope 0~1개 + threshold 0~N개

    master_rule_scope INSERT 조건:
    - 분류형 결과 1개 이상, OR
    - 임계값 1개 이상, OR
    - sectors 1개 이상
    """
    source_text = (clause.get("source_text") or "").strip()
    sectors = get_sectors(clause)

    industry = extract_industry(source_text)
    building = extract_building_use(source_text)
    facility = extract_facility(source_text)
    construction = extract_construction_type(source_text)
    equipment = extract_equipment(source_text)
    proc = extract_process(source_text)
    thresholds = extract_thresholds(source_text)

    has_classification = any([industry, building, facility, construction, equipment, proc])
    has_threshold = len(thresholds) > 0
    has_sectors = len(sectors) > 0

    if not (has_classification or has_threshold or has_sectors):
        return None, []

    layer = determine_layer(article_meta.get("law_name") or "")
    scope_code = f"SCOPE_{str(clause.get('id'))[:8]}"

    scope = {
        "scope_code": scope_code,
        "source_clause_id": clause.get("id"),
        "source_part_id": clause.get("source_part_id"),
        "source_article_id": clause.get("source_article_id"),
        "source_law_id": article_meta.get("source_law_id"),
        "layer": layer,
        "sectors": sectors,
        "industry_codes": industry,
        "building_use_codes": building,
        "facility_types": facility,
        "construction_types": construction,
        "equipment_types": equipment,
        "process_codes": proc,
        "scope_text": source_text[:1000],
        "generation_method": "AUTO_REGEX",
        "generation_confidence": calculate_confidence(has_classification, has_threshold, has_sectors),
        "needs_review": not (has_classification and has_threshold),
        "review_reason": (
            "분류형/임계값 둘 다 추출됨"
            if (has_classification and has_threshold)
            else "분류형만 추출"
            if has_classification
            else "임계값만 추출"
            if has_threshold
            else "sectors만 보유"
        ),
    }

    return scope, thresholds


# =============================================================================
# apply helpers
# =============================================================================


def truncate_tables_best_effort():
    rpc_candidates = [
        "truncate_master_rule_scope_all",
        "truncate_master_rule_scope",
        "truncate_scope_tables_v1",
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


def insert_scope_and_thresholds(scope: Dict[str, Any], thresholds: List[Dict[str, Any]]) -> str:
    # upsert(on_conflict=scope_code): retry로 인한 중복 INSERT 시 update로 멱등성 보장
    res = with_retry(
        lambda: supabase.table("master_rule_scope")
        .upsert(scope, on_conflict="scope_code")
        .execute()
    )
    scope_id = (res.data or [{}])[0].get("id")
    if not scope_id:
        # upsert가 결과를 반환하지 않으면 scope_code로 조회
        sel = with_retry(
            lambda: supabase.table("master_rule_scope")
            .select("id")
            .eq("scope_code", scope.get("scope_code"))
            .single()
            .execute()
        )
        scope_id = (sel.data or {}).get("id")
    if not scope_id:
        raise RuntimeError("master_rule_scope upsert 결과에서 id를 받지 못했습니다.")

    if thresholds:
        payload = []
        for t in thresholds:
            payload.append({**t, "scope_id": scope_id})
        with_retry(lambda: supabase.table("master_rule_scope_threshold").insert(payload).execute())

    return str(scope_id)


# =============================================================================
# reports
# =============================================================================


def print_sample(scopes: List[Dict[str, Any]], thresholds_by_code: Dict[str, int], k: int = 5):
    print("\n[SAMPLE 출력 5건]")
    for i, s in enumerate(scopes[:k]):
        code = s.get("scope_code")
        print("  ─────────────────────────────────────────────")
        print(f"  [{i+1}] scope_code={code} layer={s.get('layer')}")
        print(f"      sectors={s.get('sectors')}")
        print(f"      industry={s.get('industry_codes')} building={s.get('building_use_codes')}")
        print(f"      facility={s.get('facility_types')} equipment={s.get('equipment_types')} process={s.get('process_codes')}")
        print(f"      thresholds={thresholds_by_code.get(code, 0)} needs_review={s.get('needs_review')} reason={s.get('review_reason')}")
        print(f"      scope_text(head)={repr((s.get('scope_text') or '')[:120])}")


def _print_threshold_details(thresholds: List[Dict[str, Any]], limit: int = 4):
    picked = thresholds[:limit]
    if not picked:
        print("\n[THRESHOLD 상세] 매칭 0건")
        return

    print(f"\n[THRESHOLD 상세] 매칭 {len(picked)}건 (상위 {limit}건)")
    for i, t in enumerate(picked):
        print("  ─────────────────────────────────────────────")
        print(f"  [{i+1}] match_source_text={repr(t.get('source_text') or '')}")
        print(
            "      4값:"
            f" criterion={repr(t.get('criterion'))}"
            f" numeric_value={t.get('numeric_value')}"
            f" unit={repr(t.get('unit'))}"
            f" operator={repr(t.get('operator'))}"
        )
        cid = (t.get("clause_id") or "")[:8]
        print(f"      clause_id={cid}")
        print(f"      clause_source_text(head200)={repr(t.get('clause_source_text_head') or '')}")


def _print_threshold_miss_samples(miss: List[Dict[str, Any]], limit: int = 10):
    if not miss:
        print("\n[THRESHOLD 미매칭 sample] 0건")
        return
    print(f"\n[THRESHOLD 미매칭 sample] {min(limit, len(miss))}건 (키워드 보유 but 정규식 미매칭)")
    for i, c in enumerate(miss[:limit]):
        cid = (c.get("id") or "")[:8]
        print("  ─────────────────────────────────────────────")
        print(f"  [{i+1}] clause_id={cid}")
        print(f"      source_text(head300)={repr((c.get('source_text') or '')[:300])}")


def dry_run_report(
    scopes: List[Dict[str, Any]],
    thresholds: List[Dict[str, Any]],
    threshold_miss_samples: Optional[List[Dict[str, Any]]] = None,
):
    layer_counts = Counter(s.get("layer") for s in scopes)
    needs_review_cnt = sum(1 for s in scopes if s.get("needs_review"))
    th_by_scope = defaultdict(int)
    for t in thresholds:
        sc = t.get("scope_code")
        if sc:
            th_by_scope[sc] += 1

    print("======================================================================")
    print("[extract_scope_from_clauses — dry-run]")
    print("======================================================================")
    print(f"\n[CONVERT] scopes: {len(scopes)} (INSERT 대상), thresholds: {len(thresholds)}")
    print(f"[STATS] needs_review: {needs_review_cnt}/{len(scopes)} ({(100.0*needs_review_cnt/len(scopes) if scopes else 0.0):.1f}%)")
    print("\n[STATS] layer:")
    for k, v in layer_counts.most_common():
        print(f"  {k:<8}: {v}")

    print_sample(scopes, th_by_scope, k=5)
    _print_threshold_details(thresholds, limit=4)
    if threshold_miss_samples is not None:
        _print_threshold_miss_samples(threshold_miss_samples, limit=10)
    print("\n[DRY-RUN 종료] 실제 DB INSERT 없음. 적용은 --apply 사용.\n")


# =============================================================================
# main
# =============================================================================


def main():
    parser = argparse.ArgumentParser(description="semantic_clause → master_rule_scope 추출 (의미해석 0%)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--truncate-first", action="store_true", help="적용 전 master_rule_scope* 비움 (RPC 필요)")
    parser.add_argument(
        "--sample-with-threshold",
        action="store_true",
        help="임계값 보유 의미절만 샘플 (4값 알고리즘 검증용)",
    )
    parser.add_argument("--sample-size", type=int, default=100000, help="처리할 의미절 수. 전체 처리는 100000+ 명시.")
    parser.add_argument("--start-from", type=int, default=0, help="몇 번째 의미절부터 시작 (재개용, id 정렬 기준 range offset)")
    args = parser.parse_args()

    if args.apply and args.dry_run:
        print("[ERROR] --dry-run 과 --apply 는 동시에 사용할 수 없습니다.", file=sys.stderr)
        sys.exit(2)
    if not args.apply and not args.dry_run:
        print("[ERROR] --dry-run 또는 --apply 중 하나를 지정하세요.", file=sys.stderr)
        sys.exit(2)
    if args.apply and "--sample-size" not in sys.argv:
        print(
            f"[WARN] --apply 실행 시 --sample-size 명시를 강력 권장합니다. (현재 default={args.sample_size})",
            file=sys.stderr,
        )

    clauses = fetch_clauses(
        start_from=args.start_from,
        sample_size=args.sample_size,
        with_threshold_only=bool(args.sample_with_threshold),
    )
    print(f"[INFO] fetched semantic_clause: {len(clauses)} rows (sample_size={args.sample_size}, start_from={args.start_from})")

    article_meta_map = fetch_article_meta([c.get("source_article_id") for c in clauses])

    scopes: List[Dict[str, Any]] = []
    thresholds_out: List[Dict[str, Any]] = []
    threshold_miss_samples: List[Dict[str, Any]] = []

    for c in clauses:
        am = article_meta_map.get(c.get("source_article_id") or "", {})
        scope, thresholds = process_clause(c, am)
        # --sample-with-threshold 모드: 키워드 필터는 통과했지만 정규식 미매칭인 케이스 샘플링
        if args.sample_with_threshold and not thresholds:
            threshold_miss_samples.append(c)

        if scope:
            scopes.append(scope)
            for t in thresholds:
                thresholds_out.append(
                    {
                        **t,
                        "scope_code": scope["scope_code"],
                        # dry-run 출력용 메타 (INSERT 시 제거)
                        "clause_id": c.get("id"),
                        "clause_source_text_head": (c.get("source_text") or "")[:200],
                    }
                )

    if args.dry_run:
        dry_run_report(
            scopes,
            thresholds_out,
            threshold_miss_samples=threshold_miss_samples if args.sample_with_threshold else None,
        )
        return

    if args.truncate_first:
        print("[TRUNCATE] truncate-first requested.")
        truncate_tables_best_effort()

    inserted_scopes = 0
    inserted_thresholds = 0
    for scope in scopes:
        scope_code = scope["scope_code"]
        ths = [t for t in thresholds_out if t.get("scope_code") == scope_code]
        _ = insert_scope_and_thresholds(
            scope,
            [
                {
                    k: v
                    for k, v in t.items()
                    if k
                    in {
                        "criterion",
                        "criterion_code",
                        "numeric_value",
                        "unit",
                        "operator",
                        "normalized_value",
                        "normalized_unit",
                        "source_text",
                    }
                }
                for t in ths
            ],
        )
        inserted_scopes += 1
        inserted_thresholds += len(ths)

    print(f"[DONE] inserted scopes={inserted_scopes} thresholds={inserted_thresholds}")


if __name__ == "__main__":
    main()

