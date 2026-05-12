#!/usr/bin/env python3
"""
decompose_v1.py — 의미절 분해 v1.9.1 (iter1)

원칙:
- AI/LLM 호출 0%
- paragraph part만 대상
- 정규식 룰 기반 분해/추출
"""

import argparse
import os
import random
import re
import sys
import time
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Tuple

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
    httpx.RemoteProtocolError, httpx.ConnectError, httpx.ReadTimeout,
    httpx.WriteTimeout, httpx.PoolTimeout, httpx.ConnectTimeout,
    httpx.NetworkError, ConnectionError,
)


def reset_supabase():
    global supabase
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def with_retry(func, max_retries=5, initial_delay=1.0):
    for attempt in range(max_retries):
        try:
            return func()
        except RETRY_EXCEPTIONS as e:
            if attempt < max_retries - 1:
                delay = initial_delay * (2 ** attempt)
                print(f"  [RETRY {attempt+1}/{max_retries}] {type(e).__name__}: 대기 {delay:.1f}s + 재연결")
                time.sleep(delay)
                reset_supabase()
            else:
                raise


KEC_LAW_ID = "64209405-1a40-4f0a-aa8a-6f3e55917001"

# 폐지 조문 패턴 (조문 번호 + "삭제" + 개정 일자)
DELETED_ARTICLE_PATTERN = re.compile(
    r'^(?:제\s*\d+(?:조|항)?(?:의\s*\d+)?\s*)?삭제\s*<\d{4}'
)


def filter_deleted(parts):
    """삭제된 조문은 의미절 분해 대상에서 제외."""
    filtered = []
    deleted_count = 0
    for p in parts:
        text = (p.get('part_text') or '').strip()
        if DELETED_ARTICLE_PATTERN.match(text):
            deleted_count += 1
            continue
        filtered.append(p)
    if deleted_count > 0:
        print(f"[INFO] 폐지 조문 제외: {deleted_count}건")
    return filtered


RULES = {
    "rule_1_proviso": {
        "pattern": r"다만,?\s*([^.]+(?:한다|된다)[^.]*\.)",
        "role": "exception",
        "desc": "단서절 = 별도 의미절(예외)",
    },
    "rule_2_condition": {
        "patterns": [
            r"([^.,]*?(?:한 경우|할 때|인 때에는|인 경우|에 한정하여)[,\s])",
            r"(이\s*경우(?:에는|에)?[,\s])",
            r"(이때[,\s])",
        ],
        "role": "condition",
        "desc": "조건절 → 다음 행위에 조건 부여 (경우/때/이 경우/이때)",
    },
    "rule_3_parallel": {
        "pattern_strong": r"([^.]+?하여야\s*하며,?\s*)",
        "pattern_weak": r"([^.]+?(?:하고|하며),?\s+)",
        "role": "split_parallel",
        "desc": "병렬 행위 분리 (하여야 하며 = 강제+연결, 하고/하며 = 일반)",
    },
    "rule_4_or_split": {
        "pattern": r"([^.]+?하거나\s+)",
        "role": "split_or",
        "desc": "OR: '하거나'는 분리 (needs_review)",
    },
    "rule_4_or_keep": {
        "pattern": r"([^.]+?\s+또는\s+[^.]+)",
        "role": "keep_or",
        "desc": "OR: '또는'은 분리하지 않고 묶음+review만",
    },
    "rule_5_and": {
        "pattern": r"([가-힣A-Za-z0-9]+)\s*및\s*([가-힣A-Za-z0-9]+)",
        "role": "and_marker",
        "desc": "AND 결합 (행위/대상/조건 병렬, 모호성 → needs_review)",
        "always_review": True,
    },
    "rule_6_obligation_strong": {
        "pattern": r"(?:하여야\s*한다|해야\s*한다|두어야\s*한다)\.?$",
        "role": "content_type",
        "value": "OBLIGATION",
    },
    "rule_6_obligation_verb": {
        "pattern": r"(?:정한다|결정한다|실시한다|작성한다|보고한다|제출한다|관리한다|점검한다|확인한다|둔다)\.?$",
        "role": "content_type",
        "value": "OBLIGATION",
    },
    "rule_6_obligation_fallback": {
        "pattern": r"한다\.?$",
        "role": "content_type",
        "value": "OBLIGATION",
    },
    "rule_7_authority": {
        "pattern": r"할\s*수\s*있다\.?$",
        "role": "content_type",
        "value": "AUTHORITY",
    },
    "rule_8_prohibition": {
        "pattern": r"(?:아니\s*된다|아니하여야\s*한다|금지한다)\.?$",
        "role": "content_type",
        "value": "PROHIBITION",
    },
    "rule_9_cycle": {
        "pattern_explicit": r"(매년|매월|매일|매\s*반기|매\s*분기|\d+\s*(?:년|개월|월|일|시간)\s*(?:마다|이내에?|내에?)|즉시|지체\s*없이)",
        "pattern_fallback": r"(정기적으로)",
        "role": "cycle",
        "desc": "주기 추출 (명시적 우선, 정기적으로는 fallback)",
    },
    "rule_10_form": {
        "pattern": r"(별지\s*제\s*\d+\s*호\s*서식|별표\s*제?\s*\d+\s*호?)",
        "role": "form_token",
        "desc": "form 토큰 추출",
    },
    "rule_11_delegation": {
        "pattern": r"(?:에\s*따른다|에\s*의한다|에\s*의하여\s*한다)\.?$",
        "role": "content_type",
        "value": "DELEGATION",
    },
    "rule_12_definition": {
        "pattern": r"(?:으?로\s*한다|이?라\s*한다|라고\s*한다|말한다|본다|이다)\.?$",
        "role": "content_type",
        "value": "DEFINITION",
    },
    "rule_13_statement": {
        "pattern": r"아니한다\.?$",
        "role": "content_type",
        "value": "STATEMENT",
    },
}

RX_PROVISO = re.compile(RULES["rule_1_proviso"]["pattern"])
RX_CONDITIONS = [re.compile(p) for p in RULES["rule_2_condition"]["patterns"]]
RX_PARALLEL_STRONG = re.compile(RULES["rule_3_parallel"]["pattern_strong"])
RX_PARALLEL_WEAK = re.compile(RULES["rule_3_parallel"]["pattern_weak"])
RX_OR_SPLIT = re.compile(RULES["rule_4_or_split"]["pattern"])
RX_OR_KEEP = re.compile(RULES["rule_4_or_keep"]["pattern"])
RX_AND = re.compile(RULES["rule_5_and"]["pattern"])
RX_CYCLE_EXPL = re.compile(RULES["rule_9_cycle"]["pattern_explicit"])
RX_CYCLE_FALL = re.compile(RULES["rule_9_cycle"]["pattern_fallback"])
RX_FORM = re.compile(RULES["rule_10_form"]["pattern"])

RX_EXECUTOR = re.compile(r"^\s*([가-힣A-Za-z0-9·\(\)]+?)(?:은|는|이|가)\b")

# v1.7 — 5요소 추출 강화 (doc v17 정규식 그대로)
EXECUTOR_LEXICON_PATTERN = re.compile(
    r'^(?:.*?)('
    r'사업주|사용자|소유자|점유자|임차인|관리자|관계인|관할관청|'
    r'이사장|회장|위원장|청장|구청장|시ㆍ도지사|시장|군수|'
    r'중앙행정기관의\s*장|행정기관의\s*장|지방행정기관의\s*장|'
    r'(?:[가-힣ㆍ]+\s*){0,3}장관|'
    r'(?:[가-힣ㆍ]+\s*){0,4}(?:위원회|이사회)|'
    r'다음\s*각\s*호의?\s*어느\s*하나에\s*해당하는\s*자|'
    r'누구든지|신청인|등록자|대리인|대표자|소속\s*공무원'
    r')\s*(?:은|는|이|가)\s'
)

# v1.7.1 NEW: 법 인용 prefix 제거 패턴
LAW_CITATION_PREFIX = re.compile(
    r'^법\s*제\d+조(?:제\d+항)?(?:제\d+호)?(?:의\d+)?[^,.]*?(?:따라|따른|의하여|의한|에서|에는?)\s+'
)

# =============================================================================
# v1.8 PATCH 0 — 위임조항(DELEGATION) 우선 판정 (v2 보강 포함)
# =============================================================================

DELEGATION_PATTERNS = [
    # "~필요한 사항은 ~으로/~장관/~위원회 정한다" (가장 흔함)
    r'필요한\s*사항(?:은|을)\s*.{0,60}정한다(?:\s*$|\s*[.,;])',
    # "~정하여 고시한다"
    r'정하여\s*고시한다(?:\s*$|\s*[.,;])',
    # "~으로/~령으로 정한다"
    r'(?:대통령령|행정안전부령|기획재정부령|[가-힣]+부령|[가-힣]+령)으?로\s*정한다(?:\s*$|\s*[.,;])',
    # "~에 위임한다"
    r'에\s*위임한다(?:\s*$|\s*[.,;])',
    # "~으로 정하여 ~할 수 있다/한다"
    r'으?로\s*정하여\s*[가-힣]+(?:한다|수\s*있다)(?:\s*$|\s*[.,;])',
    # v1.9 PATCH B — 위임·위탁 재량 (보강)
    r'위임(?:할\s*)?수\s*있다(?:\s*$|\s*[.,;])',
    r'위탁(?:할\s*)?수\s*있다(?:\s*$|\s*[.,;])',
    r'권한\s*위임',
]
DELEGATION_RX = [re.compile(p) for p in DELEGATION_PATTERNS]


def is_delegation_clause(text: Optional[str]) -> bool:
    """텍스트가 위임조항이면 True (DELEGATION 우선 판정)."""
    if not text:
        return False
    for rx in DELEGATION_RX:
        if rx.search(text):
            return True
    return False


# =============================================================================
# v1.8 PATCH 1 (v2 보강) — 가짜 executor 필터
# =============================================================================

FAKE_EXECUTOR_PATTERNS = [
    # 부사구 (목적격) — 진짜 주어 아님
    r'^(?:기본|종합|중장기|마스터)?계획(?:은|이|을|에)$',
    r'경우에$',
    r'^이 경우$',
    r'^다만',

    # 종속어 시작 (subject 추출 실패 잔여)
    r'^따라|^대한|^위한|^관한|^의한|^또는|^및',

    # 시점/위치 부사구
    r'시점에$|때에$|기간에$',
    r'중간에서|중에|중간',

    # 간접 주어
    r'관한 사항은$|대한 사항은$',
    r'필요한 사항',

    # 조건절 잔여
    r'(?:하려면|받으려면|하는 경우|되는 경우|있는 경우|하면|할 때|한 경우)$',

    # v1.8 v2 NEW
    r'\s(?:또|또는|및|에)$',
    r'(?:대통령령|행정안전부령|기획재정부령|[가-힣]+부령|[가-힣]+령)으?로\s*정하?$',
    r'으?로\s*정하?$',
    r'^다음\s*각\s*호',
    r'다음\s*각\s*호의?\s*어느\s*하나에\s*해당하는\s*자$',
    r'^필요한\s*사항(?:은|을)\s+',
    r'받은\s*(?:자|사람)$',
    r'^[^\s]+받은\s*(?:자|사람)$',
    r'^위반자$|위반(?:한|된)\s*자$',
]
FAKE_EXECUTOR_RX = [re.compile(p) for p in FAKE_EXECUTOR_PATTERNS]


def is_fake_executor(executor_text: Optional[str]) -> bool:
    """executor_text가 부사구/조건절/종속어/잘림이면 True."""
    if not executor_text:
        return False
    if len(executor_text.strip()) < 2:
        return True
    for rx in FAKE_EXECUTOR_RX:
        if rx.search(executor_text):
            return True
    return False


# =============================================================================
# v1.8 PATCH 3 — inherit 금지 패턴 + can_inherit_executor
# =============================================================================

NO_INHERIT_PATTERNS = [
    # 위임 조항 — 행위자가 위임받는 사람 (장관 등)
    r'대통령령으로\s*정한다$',
    r'(?:[가-힣]+)?부령으로\s*정한다$',
    r'행정안전부령으로\s*정한다$',
    r'기획재정부령으로\s*정한다$',

    # 수범자 (처벌 대상)
    r'다음\s*각\s*호의?\s*어느\s*하나에\s*해당하는\s*자',
    r'위반(?:한|된)\s*자',
    r'위반자',
    r'[^\s,]{1,40}받은\s*(?:자|사람)',

    # 모호한 주어
    r'다음\s*각\s*호의?\s*사항',
    r'필요한\s*사항',
]
NO_INHERIT_RX = [re.compile(p) for p in NO_INHERIT_PATTERNS]


def can_inherit_executor(clause_text: Optional[str], candidate_executor: Optional[str]) -> bool:
    if not candidate_executor or is_fake_executor(candidate_executor):
        return False
    for rx in NO_INHERIT_RX:
        if rx.search(clause_text or ""):
            return False
    return True


# =============================================================================
# v1.8 PATCH 6 (v2 보강) — recipient_text 추출 (~한테 제거)
# =============================================================================

RECIPIENT_PATTERNS = [
    re.compile(
        r'(?:^|\s)([가-힣ㆍ]{2,30}(?:\s+[가-힣ㆍ]{1,15}){0,3})에게\s+'
        r'(?:.{0,30}?\s+)?(?:신고|보고|제출|통보|통지|요청|회신)'
    ),
    re.compile(r'(?:^|\s)([가-힣ㆍ]{2,30}(?:\s+[가-힣ㆍ]{1,15}){0,3})에게\s'),
    re.compile(
        r'(?:^|\s)([가-힣ㆍ]{2,30}(?:\s+[가-힣ㆍ]{1,15}){0,3})'
        r'(?:으?로)\s+(?:신고|보고|제출|통보|통지|요청|회신)'
    ),
]


def extract_recipient_text(text: Optional[str]) -> Optional[str]:
    """수신자(~에게/~로) 추출. 가장 강한 패턴(~에게 + 동사) 우선."""
    if not text:
        return None
    for rx in RECIPIENT_PATTERNS:
        m = rx.search(text)
        if m:
            candidate = m.group(1).strip()
            if not is_fake_executor(candidate):
                return candidate
    return None

CONDITION_PATTERNS = [
    re.compile(r'(다음\s*각\s*호의?\s*어느\s*하나에\s*해당(?:하는|되는)\s*(?:경우|때))(?:에는?)?'),
    re.compile(r'([^,.]{5,80}(?:할\s*때|한\s*경우|는\s*경우|려면|하려면))(?:에는?)?'),
    re.compile(r'(이\s*경우)(?:에는?)?'),
    re.compile(r'([^,.]{5,80})에는\s'),
]

EXCEPTION_PATTERN = re.compile(
    r'(?:^|[\s,.])다만,?\s*(.+?)(?:\.\s*$|\.$|$)',
    re.DOTALL
)

CYCLE_PATTERNS = [
    re.compile(r'매\s*(?:년|월|주|일|반기|분기|반년)\s*\d*회?(?:\s*이상)?'),
    re.compile(r'\d+(?:년|개월|월|일|시간|주)\s*마다'),
    re.compile(r'\d+(?:년|개월|월|일|시간|영업일)\s*이내'),
    re.compile(r'\d+(?:년|개월|월|일|시간)\s*이상'),
    re.compile(r'(?:매년|매월)?\s*\d+월\s*\d+일(?:까지)?'),
    re.compile(r'\d+월\s*\d+일까지'),
    re.compile(r'(?:정기적으로|상시|즉시|지체\s*없이|수시로|연\s*\d+회)'),
]


def sector_from_law_name(law_name: str) -> str:
    name = law_name or ""
    if "산업안전보건" in name:
        return "INDUSTRIAL"
    if "건설" in name:
        return "CONSTRUCTION"
    if "건축" in name:
        return "BUILDING"
    return "COMMON"


def length_bucket(text: str) -> str:
    n = len(text or "")
    if n < 150:
        return "short"
    if n <= 400:
        return "medium"
    return "long"


def split_proviso(part_text: str, rule_counts: Counter) -> Tuple[str, Optional[str]]:
    m = RX_PROVISO.search(part_text or "")
    if not m:
        return part_text, None
    rule_counts["rule_1_proviso"] += 1
    proviso = m.group(0).strip()
    main = (part_text[: m.start()] + part_text[m.end() :]).strip()
    return main, proviso


def split_parallel(text: str, rule_counts: Counter) -> List[str]:
    s = (text or "").strip()
    if not s:
        return []
    matches = list(RX_PARALLEL_STRONG.finditer(s))
    if matches:
        rule_counts["rule_3_parallel_strong"] += len(matches)
        parts, start = [], 0
        for m in matches:
            end = m.end()
            parts.append(s[start:end].strip().rstrip(","))
            start = end
        tail = s[start:].strip()
        if tail:
            parts.append(tail)
        return parts

    matches = list(RX_PARALLEL_WEAK.finditer(s))
    if matches:
        rule_counts["rule_3_parallel_weak"] += len(matches)
        parts, start = [], 0
        for m in matches:
            end = m.end()
            parts.append(s[start:end].strip().rstrip(","))
            start = end
        tail = s[start:].strip()
        if tail:
            parts.append(tail)
        return parts

    return [s]


def split_or(text: str, rule_counts: Counter) -> Tuple[List[str], bool, bool]:
    """
    v1.2:
    - '하거나'는 분리 (needs_review)
    - '또는'은 분리 X, 묶음+review만
    """
    s = (text or "").strip()
    if not s:
        return [], False, False

    # '또는'은 묶고 review만
    if RX_OR_KEEP.search(s):
        rule_counts["rule_4_or_keep"] += 1
        return [s], False, True

    # '하거나'는 분리
    if not RX_OR_SPLIT.search(s):
        return [s], False, False
    matches = list(RX_OR_SPLIT.finditer(s))
    rule_counts["rule_4_or_split"] += len(matches)
    parts, start = [], 0
    for m in matches:
        end = m.end()
        parts.append(s[start:end].strip().rstrip(","))
        start = end
    tail = s[start:].strip()
    if tail:
        parts.append(tail)
    return parts, True, False


def extract_condition(seg: str, rule_counts: Counter, applied: List[str]) -> Optional[str]:
    s = seg or ""
    for rx in RX_CONDITIONS:
        m = rx.search(s)
        if m:
            rule_counts["rule_2_condition"] += 1
            applied.append("rule_2_condition")
            return m.group(1).strip().rstrip(",")
    return None


def extract_executor(seg: str) -> Optional[str]:
    m = RX_EXECUTOR.search(seg or "")
    if not m:
        return None
    return m.group(1).strip()


# =============================================================================
# v1.9 PATCH A — extract_executor_text 역순(re.finditer) 재설계
# =============================================================================

# 모든 위치에서 은/는/이/가 주제표시 후보 수집
# 비탐욕 \S+?: 붙여쓴 주격 조사(행정안전부장관은)와 제5항(무공백 숫자 인접)까지 포함해 최단 NP→조사 매칭
SUBJECT_MARKER_PATTERN = re.compile(
    r'(\S+?)((?:은|(?<![에])는|(?<!에)이|(?<!에)가))(?=\s|$|[,.])'
)

# v1.9.1 — 접두 제거: 명시적 제X조/항/호 + 에 따라/따른 + 관형사(지정된 등)
_SUBJECT_REF_JO_FULL = re.compile(
    r'^제\s*\d+\s*조(?:의\s*\d+)?(?:제\s*\d+\s*항)?(?:제\s*\d+\s*호)?\s*'
)
_SUBJECT_REF_HANG = re.compile(r'^제\s*\d+\s*항(?:제\s*\d+\s*호)?\s*')
_SUBJECT_REF_HO = re.compile(r'^제\s*\d+\s*호\s*')
_SUBJECT_REF_DA_TAIL_VERB = re.compile(
    r'^(?:에\s*따라|에\s*따른)\s*'
    r'(?:지정된|승인된|정하여\s*|결정된|받은\s*|한\s*)?'
)


def cleanup_subject_candidate(raw: str) -> str:
    """조항·법 인용 등 접두 제거 후 후보 정제 (v1.9.1 명시적 조문 매칭)."""
    c = (raw or "").strip()
    changed = True
    while changed:
        changed = False

        # 반복: 제N조… 또는 제N항… 블록 + (에 따라|에 따른) + (지정된|승인된|…)?
        for ref_rx in (_SUBJECT_REF_JO_FULL, _SUBJECT_REF_HANG, _SUBJECT_REF_HO):
            m = ref_rx.match(c)
            if not m:
                continue
            tail = c[m.end() :].lstrip()
            mv = _SUBJECT_REF_DA_TAIL_VERB.match(tail)
            if mv:
                c = tail[mv.end() :].lstrip()
            else:
                c = tail.lstrip()
            changed = True
            break

        if changed:
            continue

        m2 = re.match(
            r'^법\s*제\d+\s*조(?:제\d+\s*항)?(?:제\d+\s*호)?(?:의\s*\d+)?'
            r'[^,.]{0,40}?(?:에\s*따라|에\s*따른|의하여|의한|에서|에는?)\s+',
            c,
        )
        if m2:
            c = c[m2.end() :].lstrip()
            changed = True
    return c.strip()


def find_condition_end(text: str) -> int:
    """
    선행 조건절(경우/때 등)이 끝나는 최대 인덱스(exclusive).
    서술부 근처 주제표시만 고르기 위해 사용.
    """
    if not text:
        return 0
    rx = re.compile(
        r'^[\s\S]{0,520}?'
        r'(?:한\s*경우|되는\s*경우|있는\s*경우|하였을\s*때|할\s*때|한\s*때|'
        r'인\s*때에는|인\s*경우|이\s*경우(?:에는)?|에\s*한정하여)'
        r'(?:에는)?[\s,]'
    )
    m = rx.match(text)
    return m.end() if m else 0


def select_best_subject_match(
    matches: List[Any],
    condition_end: int,
    cleaned: str,
) -> Optional[Any]:
    """
    v1.9.1 — 은/는 우선:
    1) 조건절 밖(condition_end 이후)의 은/는 중 시작 위치가 가장 앞선 것
    2) 그 다음 전체 텍스트에서 은/는 중 시작 가장 앞선 것
    3) 조건절 밖 이/가 중 시작 가장 앞선 것
    4) 전체 이/가 중 시작 가장 앞선 것
    """
    if not matches:
        return None

    def _ok(m: Any) -> bool:
        cand = cleanup_subject_candidate(m.group(1))
        return bool(cand and not is_fake_executor(cand) and len(cand.strip()) >= 2)

    out_eun = [m for m in matches if m.group(2) in ("은", "는")]
    out_iga = [m for m in matches if m.group(2) in ("이", "가")]

    tier1 = [m for m in out_eun if m.start() >= condition_end and _ok(m)]
    if tier1:
        return min(tier1, key=lambda m: m.start())

    tier2 = [m for m in out_eun if _ok(m)]
    if tier2:
        return min(tier2, key=lambda m: m.start())

    tier3 = [m for m in out_iga if m.start() >= condition_end and _ok(m)]
    if tier3:
        return min(tier3, key=lambda m: m.start())

    tier4 = [m for m in out_iga if _ok(m)]
    if tier4:
        return min(tier4, key=lambda m: m.start())

    return None


_OBJECT_SUBJECT_SUFFIX = re.compile(
    r'(계획|설비|기계|장비|건축물|건물|물품|자료|서류|시설|차량|선박|항공기|장치|시스템|'
    r'표준|기준|오차|속도|압력|온도|금액|거리|면적|용량|부지|대지|노면|와이어로프|드럼|속도계|지시오차)$'
)


def is_object_subject(candidate: str) -> bool:
    """사물·대상 명사형 주어 → 검토(needs_review) 대상."""
    c = (candidate or "").strip()
    if len(c) < 2:
        return False
    if _OBJECT_SUBJECT_SUFFIX.search(c):
        return True
    if (
        re.search(r'.{3,}의\s+[가-힣ㆍ]{2,}(?:의)?$', c)
        and not re.search(r'(장관|이사장|위원장|청장|구청장|시장|군수|위원회|이사회)$', c)
    ):
        return True
    return False


def is_suspicious_executor_candidate(candidate: str) -> bool:
    """추출 신뢰 낮음 (과단순·잘림 의심)."""
    c = (candidate or "").strip()
    if len(c) <= 2:
        return True
    if re.fullmatch(r'[가-힣]{1,2}', c):
        return True
    return False


def extract_executor_text(text: Optional[str]) -> Tuple[Optional[str], List[str]]:
    """
    v1.9.1: 주제표시 스캔 + 조건절 경계 + 은/는 우선(select_best_subject_match).
    반환: (executor_text or None, applied_rules 태그 목록)
    """
    tags: List[str] = []
    if not text:
        return None, tags

    cleaned = text
    cleaned = LAW_CITATION_PREFIX.sub("", cleaned, count=1)
    cleaned = re.sub(r"\([^)]*\)", "", cleaned)

    cond_end = find_condition_end(cleaned)
    matches = list(SUBJECT_MARKER_PATTERN.finditer(cleaned))
    best_m = select_best_subject_match(matches, cond_end, cleaned)

    if best_m:
        cand = cleanup_subject_candidate(best_m.group(1))
        if cand and not is_fake_executor(cand):
            tags.append("v19_reverse_executor")
            if is_object_subject(cand):
                tags.append("v19_object_subject")
            if is_suspicious_executor_candidate(cand):
                tags.append("v19_suspicious_executor")
            return cand, tags

    m = EXECUTOR_LEXICON_PATTERN.match(cleaned)
    if m:
        cand = m.group(1).strip()
        if not is_fake_executor(cand):
            tags.append("v19_lexicon_executor")
            if is_object_subject(cand):
                tags.append("v19_object_subject")
            if is_suspicious_executor_candidate(cand):
                tags.append("v19_suspicious_executor")
            return cand, tags

    fb = re.match(
        r'^([가-힣ㆍ]{2,24}(?:\s+[가-힣ㆍ]{1,15}){0,3})\s+(?:은|는|이|가)\s',
        cleaned,
    )
    if fb:
        cand = fb.group(1).strip()
        if not is_fake_executor(cand):
            tags.append("v19_prefix_fallback_executor")
            if is_object_subject(cand):
                tags.append("v19_object_subject")
            if is_suspicious_executor_candidate(cand):
                tags.append("v19_suspicious_executor")
            return cand, tags

    return None, tags


def merge_executor_extraction(
    seg: str,
    source_part_text: str,
    inherited_executor: Optional[str],
) -> Tuple[Optional[str], List[str]]:
    """세그먼트 → 원문 part → 선행 RX_EXECUTOR → 상속 순으로 시도."""
    ex, tags = extract_executor_text(seg)
    if ex:
        return ex, tags
    ex2, tags2 = extract_executor_text(source_part_text)
    if ex2:
        return ex2, tags2
    m = RX_EXECUTOR.search(seg or "")
    if m:
        cand = m.group(1).strip()
        if not is_fake_executor(cand):
            return cand, ["v19_rx_executor_fallback"]
    if inherited_executor:
        return inherited_executor, []
    return None, []


_V19_EXECUTOR_RULE_TAGS = frozenset({
    "v19_reverse_executor",
    "v19_lexicon_executor",
    "v19_prefix_fallback_executor",
    "v19_rx_executor_fallback",
    "v19_object_subject",
    "v19_suspicious_executor",
})


def extract_condition_text(text):
    """
    조건절 텍스트 추출. 우선순위 순으로 첫 매칭.
    """
    if not text:
        return None
    for pattern in CONDITION_PATTERNS:
        m = pattern.search(text)
        if m:
            return m.group(1).strip()
    return None


def extract_exception(text):
    """
    "다만, X" 패턴에서 X 부분 추출.
    """
    if not text or '다만' not in text:
        return None
    m = EXCEPTION_PATTERN.search(text)
    if m:
        return m.group(1).strip()
    return None


def extract_cycle(seg: str, rule_counts: Counter, applied: List[str]) -> Optional[str]:
    m = RX_CYCLE_EXPL.search(seg or "")
    if m:
        rule_counts["rule_9_cycle_explicit"] += 1
        applied.append("rule_9_cycle_explicit")
        return m.group(1).strip()
    m = RX_CYCLE_FALL.search(seg or "")
    if m:
        rule_counts["rule_9_cycle_fallback"] += 1
        applied.append("rule_9_cycle_fallback")
        return m.group(1).strip()
    return None


def extract_cycle_text(text):
    """
    주기 표현 추출. 첫 매칭만.
    """
    if not text:
        return None
    for pattern in CYCLE_PATTERNS:
        m = pattern.search(text)
        if m:
            return m.group(0).strip()
    return None


def extract_form(seg: str, rule_counts: Counter, applied: List[str]) -> Optional[str]:
    m = RX_FORM.search(seg or "")
    if not m:
        return None
    rule_counts["rule_10_form"] += 1
    applied.append("rule_10_form")
    return m.group(1).strip()


def classify_content_type(seg: str, rule_counts: Counter, applied: List[str]) -> Optional[str]:
    ctype, rule_id = classify_content_type_priority((seg or "").strip())
    if not ctype:
        return None
    rule_counts[rule_id] += 1
    applied.append(rule_id)
    return ctype


def classify_content_type_priority(text, debug: bool = False):
    """
    종결 어미 우선순위 매칭. 매칭되는 첫 룰의 결과를 반환.
    text: 의미절 텍스트 (구두점 포함)
    """
    # v1.8 PATCH 0: 위임조항 우선 판정 (OBLIGATION 오분류 방지)
    if is_delegation_clause(text):
        return "DELEGATION", "rule_11_delegation_priority"

    # 1. DEFINITION (정의/간주/명명)
    if re.search(r'(?:으?로\s*한다|이?라\s*한다|라고\s*한다|말한다|본다|이다)\.?$', text):
        return 'DEFINITION', 'rule_12_definition'

    # 2. DELEGATION (위임/준용/적용)
    if re.search(r'(?:준용한다|에\s*따른다|에\s*의한다|을\s*적용한다|에\s*의하여\s*한다|을\s*따른다|(?:과|와)\s*같다|또한\s*같다|위임한다)\.?$', text):
        return 'DELEGATION', 'rule_11_delegation'

    # 3. PROHIBITION (명시적 금지)
    if re.search(r'(?:(?:아니|안)\s*된다|아니하여야\s*한다|금지한다|할\s*수\s*없다)\.?$', text):
        return 'PROHIBITION', 'rule_8_prohibition'

    # 4. STATEMENT (단순 부정 — fallback for `아니한다`)
    if re.search(r'(?:아니한다|하지\s*않는다|되지\s*않는다)\.?$', text):
        return 'STATEMENT', 'rule_13_statement'

    # 5. AUTHORITY (재량/허용)
    if re.search(r'[가-힣]\s*수\s*있다\.?$', text):
        return 'AUTHORITY', 'rule_7_authority'

    # 6. OBLIGATION 강제 패턴
    if re.search(r'[가-힣](?:어야|아야|여야|야)\s*한다\.?$', text):
        return 'OBLIGATION', 'rule_6_obligation_strong'

    # 7. OBLIGATION 일반 패턴 (`정한다`, `결정한다`, 단순 `한다` fallback)
    #    단, 위 1~6에서 다 빠져나온 경우만
    if re.search(r'(?:정한다|결정한다|실시한다|작성한다|보고한다|제출한다|관리한다|점검한다|확인한다|둔다|책무를\s*진다|책임을\s*진다)\.?$', text):
        return 'OBLIGATION', 'rule_6_obligation_verb'
    if re.search(r'한다\.?$', text):
        return 'OBLIGATION', 'rule_6_obligation_fallback'

    # 8. 미분류
    if debug and '있다' in text:
        last_50 = text[-50:] if len(text) > 50 else text
        print(f"[DEBUG-CLASSIFY] 미분류 with 있다: repr={last_50!r}")
    return None, None


def classify_segments_content_types(
    segments: List[str],
    rule_counts: Counter,
    debug: bool = False,
) -> List[Tuple[Optional[str], List[str], bool]]:
    """
    v1.3:
    - 각 segment를 우선 direct 분류
    - 비종결 segment 중 (direct가 None)인 경우, last segment의 content_type을 inherit
      (multi-step inherit 없음: 오직 last segment 기준)

    returns: (content_type, applied_rules, is_inherited)
    """
    if not segments:
        return []

    direct: List[Tuple[Optional[str], List[str]]] = []
    for seg in segments:
        ct, rule_id = classify_content_type_priority((seg or "").strip(), debug=debug)
        if ct and rule_id:
            rule_counts[rule_id] += 1
            direct.append((ct, [rule_id]))
        else:
            direct.append((None, []))

    last_ct = direct[-1][0]

    out: List[Tuple[Optional[str], List[str], bool]] = []
    for i, (ct, rules) in enumerate(direct):
        is_last = i == (len(direct) - 1)
        if ct is None and last_ct is not None and not is_last:
            rule_counts["inherit_from_last_segment"] += 1
            inherited_rules = rules + [f"inherit_from_last_segment(={last_ct})"]
            if last_ct != "OBLIGATION":
                inherited_rules.append("inherit_review_required")
            out.append((last_ct, inherited_rules, True))
        else:
            out.append((ct, rules, False))

    return out


def has_and(seg: str, rule_counts: Counter, applied: List[str]) -> bool:
    if RX_AND.search(seg or ""):
        rule_counts["rule_5_and"] += 1
        applied.append("rule_5_and")
        return True
    return False


def make_clause(
    source_text: str,
    source_part_text: str,
    source_part_id: str,
    source_article_id: str,
    clause_seq: int,
    sector: str,
    inherited_executor: Optional[str],
    rule_counts: Counter,
    content_type: Optional[str],
    applied_rules_seed: Optional[List[str]] = None,
    content_type_inherited: bool = False,
) -> Dict[str, Any]:
    applied: List[str] = list(applied_rules_seed or [])
    seg = (source_text or "").strip().strip('"')

    needs_review = False
    review_reasons: List[str] = []

    cond = extract_condition(seg, rule_counts, applied)
    cycle = extract_cycle(seg, rule_counts, applied)
    form_token = extract_form(seg, rule_counts, applied)
    ctype = content_type

    # v1.8 PATCH 0: segment가 잘려도 part/source에 위임조항이 있으면 DELEGATION 우선
    if not ctype and (is_delegation_clause(seg) or is_delegation_clause(source_part_text)):
        ctype = "DELEGATION"
        applied.append("rule_11_delegation_priority")

    and_hit = has_and(seg, rule_counts, applied)
    if and_hit:
        needs_review = True
        review_reasons.append('"및" 모호성')

    executor, executor_tags = merge_executor_extraction(seg, source_part_text, inherited_executor)
    if executor_tags:
        applied.extend(executor_tags)
    if "v19_object_subject" in executor_tags:
        needs_review = True
        review_reasons.append("사물 주어 의심 (executor 검토)")
    cond_text = extract_condition_text(seg) or extract_condition_text(source_part_text) or cond
    cycle_text = extract_cycle_text(seg) or extract_cycle_text(source_part_text) or cycle
    exception_text = extract_exception(source_part_text)
    recipient = extract_recipient_text(seg) or extract_recipient_text(source_part_text)

    if not ctype:
        needs_review = True
        review_reasons.append("content_type 미분류")
    elif content_type_inherited:
        # inherit 자체는 정상 동작: "content_type 미분류" review 사유를 만들지 않는다
        # (단, 이미 다른 사유가 있으면 needs_review는 유지)
        if "content_type 미분류" in review_reasons:
            review_reasons = [r for r in review_reasons if r != "content_type 미분류"]
        if not review_reasons:
            needs_review = False
        if "inherit_review_required" in applied:
            needs_review = True
            review_reasons.append(
                "비-OBLIGATION inherit 의심 (last segment의 content_type이 의미적으로 일치하지 않을 수 있음)"
            )

    action_text = seg

    # v1.8 PATCH 0-3: DELEGATION은 행위 의무가 아니므로 executor 무의미 → NULL 강제
    if ctype == "DELEGATION":
        executor = None
        inherited_executor = None
        applied[:] = [a for a in applied if a not in _V19_EXECUTOR_RULE_TAGS]

    return {
        "source_part_id": source_part_id,
        "source_article_id": source_article_id,
        "clause_seq": clause_seq,
        "source_text": seg,
        "source_part_text": source_part_text,
        "condition_text": cond_text,
        "executor_text": executor,
        "action_text": action_text,
        "recipient_text": recipient,
        "cycle_text": cycle_text,
        "exception_text": exception_text,
        "form_token": form_token,
        "content_type": ctype,
        "applied_rules": applied,
        "decomposition_version": "v1.9.1",
        "needs_review": needs_review,
        "review_reason": "; ".join(review_reasons) if review_reasons else None,
        "alternative_kept_text": None,
        "sector": sector,
    }


def decompose_part(part: Dict[str, Any], sector: str, rule_counts: Counter) -> List[Dict[str, Any]]:
    part_text = part.get("part_text") or ""
    main_text, proviso = split_proviso(part_text, rule_counts)

    clauses: List[Dict[str, Any]] = []
    seq = 1

    if proviso:
        clauses.append({
            "source_part_id": part["id"],
            "source_article_id": part["article_id"],
            "clause_seq": seq,
            "source_text": proviso.strip(),
            "source_part_text": part_text,
            "condition_text": None,
            "executor_text": None,
            "action_text": proviso.strip(),
            "recipient_text": None,
            "cycle_text": None,
            "exception_text": proviso.strip(),
            "form_token": None,
            "content_type": None,
            "applied_rules": ["rule_1_proviso"],
            "decomposition_version": "v1.9.1",
            "needs_review": True,
            "review_reason": "단서절 분리(예외) — content_type 미분류",
            "alternative_kept_text": None,
            "sector": sector,
        })
        seq += 1

    segments = split_parallel(main_text, rule_counts)
    expanded: List[Tuple[str, bool, bool]] = []
    for seg in segments:
        parts_or, has_or_split, has_or_keep = split_or(seg, rule_counts)
        for x in parts_or:
            expanded.append((x, has_or_split, has_or_keep))

    seg_texts = [seg for seg, _, _ in expanded]
    seg_cts = classify_segments_content_types(seg_texts, rule_counts, debug=bool(part.get("_debug_classify")))

    # 1차 pass: 직접 추출만 수행 (paragraph inherit는 후처리)
    for (seg, has_or_split, has_or_keep), (ct, ct_rules, is_inherited) in zip(expanded, seg_cts):
        clause = make_clause(
            source_text=seg,
            source_part_text=part_text,
            source_part_id=part["id"],
            source_article_id=part["article_id"],
            clause_seq=seq,
            sector=sector,
            inherited_executor=None,
            rule_counts=rule_counts,
            content_type=ct,
            applied_rules_seed=ct_rules,
            content_type_inherited=is_inherited,
        )
        if has_or_keep:
            clause["needs_review"] = True
            base = clause.get("review_reason") or ""
            clause["review_reason"] = (base + ("; " if base else "") + '"또는" 묶음 처리').strip()
        if has_or_split:
            clause["needs_review"] = True
            base = clause.get("review_reason") or ""
            clause["review_reason"] = (base + ("; " if base else "") + '"하거나" 분리 후').strip()

        clauses.append(clause)
        seq += 1

    # 2차 pass: paragraph 내 inherit (NULL → 첫 valid executor)
    paragraph_executor = next(
        (c.get("executor_text") for c in clauses if c.get("executor_text") and not is_fake_executor(c.get("executor_text"))),
        None,
    )
    if paragraph_executor:
        for c in clauses:
            if c.get("executor_text"):
                continue
            if can_inherit_executor(c.get("source_text"), paragraph_executor):
                c["executor_text"] = paragraph_executor
                c["applied_rules"] = (c.get("applied_rules") or []) + ["inherit_paragraph"]

    return clauses


# =============================================================================
# v1.8 PATCH 5 — Article 단위 inherit (post-processing)
# =============================================================================

def post_process_article_inherit(clauses: List[Dict[str, Any]]) -> int:
    """
    같은 article의 다른 paragraph에서 executor inherit.
    paragraph inherit으로 채워지지 않은 NULL executor 처리.
    """
    by_article: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for c in clauses:
        by_article[c.get("source_article_id")].append(c)

    inherit_count = 0
    for _, article_clauses in by_article.items():
        article_executor = next(
            (c.get("executor_text") for c in article_clauses if c.get("executor_text") and not is_fake_executor(c.get("executor_text"))),
            None,
        )
        if not article_executor:
            continue

        for c in article_clauses:
            if c.get("executor_text"):
                continue
            if not can_inherit_executor(c.get("source_text"), article_executor):
                c["needs_review"] = True
                base = c.get("review_reason") or ""
                c["review_reason"] = (base + ("; " if base else "") + "article inherit 거절 (위임/수범)").strip()
                continue

            c["executor_text"] = article_executor
            c["applied_rules"] = (c.get("applied_rules") or []) + ["inherit_article"]
            inherit_count += 1

    return inherit_count


def fetch_paragraph_pool(pool_size: int = 5000) -> List[Dict[str, Any]]:
    all_parts: List[Dict[str, Any]] = []
    offset = 0
    while len(all_parts) < pool_size:
        def _fetch():
            return supabase.from_("law_article_part").select(
                "id,article_id,part_text,part_type,depth"
            ).eq("part_type", "paragraph").order("id").range(offset, offset + 999).execute().data
        batch = with_retry(_fetch)
        if not batch:
            break
        all_parts.extend(batch)
        if len(batch) < 1000:
            break
        offset += 1000
    # dedup (safety)
    seen, deduped = set(), []
    for p in all_parts:
        if p["id"] not in seen:
            seen.add(p["id"])
            deduped.append(p)
    return deduped[:pool_size]


def fetch_articles(article_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for i in range(0, len(article_ids), 200):
        chunk = article_ids[i:i + 200]
        def _fetch():
            return supabase.from_("law_article").select(
                "id,article_type,law_id,article_internal_key"
            ).in_("id", chunk).execute().data
        res = with_retry(_fetch)
        for r in res:
            out[r["id"]] = r
    return out


def fetch_laws(law_ids: List[str]) -> Dict[str, str]:
    # spec: law_name 키워드로 sector 매핑. law_master가 없으면 COMMON 처리.
    out: Dict[str, str] = {}
    if not law_ids:
        return out
    for i in range(0, len(law_ids), 200):
        chunk = law_ids[i:i + 200]
        def _fetch():
            return supabase.from_("law_master").select("id,law_name").in_("id", chunk).execute().data
        try:
            res = with_retry(_fetch)
        except Exception:
            return out
        for r in res:
            out[r["id"]] = r.get("law_name") or ""
    return out


def fetch_population_paragraphs() -> List[Dict[str, Any]]:
    """모집단: paragraph parts 전체 (order('id') 필수)."""
    all_parts: List[Dict[str, Any]] = []
    offset = 0
    while True:
        def _fetch():
            return supabase.from_("law_article_part").select(
                "id,article_id,part_text,part_type,depth"
            ).eq("part_type", "paragraph").order("id").range(offset, offset + 999).execute().data
        batch = with_retry(_fetch)
        if not batch:
            break
        all_parts.extend(batch)
        if len(batch) < 1000:
            break
        offset += 1000

    # dedup safety
    seen, deduped = set(), []
    for p in all_parts:
        if p["id"] not in seen:
            seen.add(p["id"])
            deduped.append(p)
    return deduped


def eligible_population(parts: List[Dict[str, Any]], articles: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """문서 조건: article_type='조문' AND KEC 제외."""
    out = []
    for p in parts:
        a = articles.get(p.get("article_id"))
        if not a:
            continue
        if a.get("article_type") != "조문":
            continue
        if a.get("law_id") == KEC_LAW_ID:
            continue
        out.append(p)
    return out


def population_length_pct(population: List[Dict[str, Any]]) -> Dict[str, float]:
    cnt = Counter(length_bucket(p.get("part_text") or "") for p in population)
    total = max(1, len(population))
    return {
        "short": 100.0 * cnt.get("short", 0) / total,
        "medium": 100.0 * cnt.get("medium", 0) / total,
        "long": 100.0 * cnt.get("long", 0) / total,
    }


def stratified_sample(parts: List[Dict[str, Any]], articles: Dict[str, Dict[str, Any]], laws: Dict[str, str],
                      sample_size: int, seed: int) -> Tuple[List[Dict[str, Any]], Dict[str, int], Dict[str, int]]:
    rng = random.Random(seed)

    groups: Dict[Tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)
    sector_counts = Counter()
    length_counts = Counter()

    for p in parts:
        a = articles.get(p["article_id"])
        if not a:
            continue
        if a.get("article_type") != "조문":
            continue
        if a.get("law_id") == KEC_LAW_ID:
            continue
        law_name = laws.get(a.get("law_id") or "", "")
        sector = sector_from_law_name(law_name)
        lb = length_bucket(p.get("part_text") or "")
        groups[(sector, lb)].append(p)

    per_group = max(1, sample_size // 12)
    remainder = sample_size - per_group * 12

    selected: List[Dict[str, Any]] = []
    for sector in ("BUILDING", "INDUSTRIAL", "CONSTRUCTION", "COMMON"):
        for lb in ("short", "medium", "long"):
            items = groups.get((sector, lb), [])
            if not items:
                continue
            k = min(per_group, len(items))
            selected.extend(rng.sample(items, k))

    # remainder fill (global from remaining)
    if remainder > 0:
        already = {p["id"] for p in selected}
        remaining = [p for p in parts if p.get("id") not in already and p.get("article_id") in articles]
        if remaining:
            selected.extend(rng.sample(remaining, min(remainder, len(remaining))))

    # v1.2 보정: 빈 그룹으로 인해 sample_size 미달 시, 다른 그룹에서 균등 보충
    if len(selected) < sample_size:
        already = {p["id"] for p in selected}
        remaining = [p for p in parts if p.get("id") not in already and p.get("article_id") in articles]
        if remaining:
            need = min(sample_size - len(selected), len(remaining))
            selected.extend(rng.sample(remaining, need))

    # cap (and deterministic shuffle)
    rng.shuffle(selected)
    selected = selected[:sample_size]

    # info counts
    for p in selected:
        a = articles.get(p["article_id"], {})
        law_name = laws.get(a.get("law_id") or "", "")
        s = sector_from_law_name(law_name)
        sector_counts[s] += 1
        length_counts[length_bucket(p.get("part_text") or "")] += 1

    return selected, dict(sector_counts), dict(length_counts)


def print_dry_run(
    sampled_parts: List[Dict[str, Any]],
    articles: Dict[str, Dict[str, Any]],
    laws: Dict[str, str],
    clauses: List[Dict[str, Any]],
    rule_counts: Counter,
    sample_size: int,
    seed: int,
    sampling: str,
    population_n: int,
    population_laws: int,
    population_len_pct: Dict[str, float],
    sector_counts: Dict[str, int],
    length_counts: Dict[str, int],
):
    print("=" * 70)
    print("[의미절 분해 v1.9.1 — dry-run]")
    print("=" * 70)
    print()
    print(f"[INFO] sampling={sampling} sample_size={sample_size} seed={seed}")
    print(f"[INFO] 모집단: {population_n} paragraphs from {population_laws} laws")
    print("[INFO] 계층화: "
          f"BUILDING={sector_counts.get('BUILDING', 0)} "
          f"INDUSTRIAL={sector_counts.get('INDUSTRIAL', 0)} "
          f"CONSTRUCTION={sector_counts.get('CONSTRUCTION', 0)} "
          f"COMMON={sector_counts.get('COMMON', 0)}")
    print("[INFO] 길이 분포 (sample):    "
          f"short={length_counts.get('short', 0)} "
          f"medium={length_counts.get('medium', 0)} "
          f"long={length_counts.get('long', 0)}")
    print("[INFO] 길이 분포 (모집단 비율): "
          f"short={population_len_pct.get('short', 0.0):.1f}% "
          f"medium={population_len_pct.get('medium', 0.0):.1f}% "
          f"long={population_len_pct.get('long', 0.0):.1f}%")
    print()

    n_clauses = len(clauses)
    print(f"[DECOMPOSE] {len(sampled_parts)} parts → {n_clauses} clauses (확장률 {n_clauses}/{len(sampled_parts)})")
    print()

    # pattern matching counts
    print("[PATTERN MATCHING]")
    print(f"  rule_1_proviso (다만)             :  {rule_counts.get('rule_1_proviso', 0)}건")
    print(f"  rule_2_condition (경우/때/이 경우): {rule_counts.get('rule_2_condition', 0)}건")
    print(f"  rule_3_parallel_strong (하여야 하며): {rule_counts.get('rule_3_parallel_strong', 0)}건")
    print(f"  rule_3_parallel_weak (하고/하며)  :  {rule_counts.get('rule_3_parallel_weak', 0)}건")
    print(f"  rule_4_or_split (하거나)          :  {rule_counts.get('rule_4_or_split', 0)}건  → review {rule_counts.get('review_or_split', 0)}건")
    print(f"  rule_4_or_keep (또는)             :  {rule_counts.get('rule_4_or_keep', 0)}건  → review {rule_counts.get('review_or_keep', 0)}건 (전부 묶음+review)")
    print(f"  rule_5_and (및)                   :  {rule_counts.get('rule_5_and', 0)}건  → review {rule_counts.get('review_and', 0)}건 (전부 review)")
    print(f"  rule_6_obligation_strong (하여야 한다): {rule_counts.get('rule_6_obligation_strong', 0)}건")
    print(f"  rule_6_obligation_verb (정한다/실시한다 등): {rule_counts.get('rule_6_obligation_verb', 0)}건")
    print(f"  rule_6_obligation_fallback (단순 한다): {rule_counts.get('rule_6_obligation_fallback', 0)}건")
    print(f"  rule_7_authority (할 수 있다)     :  {rule_counts.get('rule_7_authority', 0)}건")
    print(f"  rule_8_prohibition (아니 된다/금지한다): {rule_counts.get('rule_8_prohibition', 0)}건")
    print(f"  rule_9_cycle_explicit             :  {rule_counts.get('rule_9_cycle_explicit', 0)}건")
    print(f"  rule_9_cycle_fallback (정기적으로) : {rule_counts.get('rule_9_cycle_fallback', 0)}건")
    print(f"  rule_10_form (별지/별표)          :  {rule_counts.get('rule_10_form', 0)}건")
    print(f"  rule_11_delegation (따른다/준용한다): {rule_counts.get('rule_11_delegation', 0)}건")
    print(f"  rule_12_definition (로 한다/말한다/이다): {rule_counts.get('rule_12_definition', 0)}건")
    print(f"  rule_13_statement (아니한다)      :  {rule_counts.get('rule_13_statement', 0)}건")
    print(f"  inherit_from_last_segment        :  {rule_counts.get('inherit_from_last_segment', 0)}건")
    print()

    # content type distribution
    dist = Counter()
    for c in clauses:
        dist[c.get("content_type")] += 1
    print("[CONTENT_TYPE 분포]")
    for k in ("OBLIGATION", "AUTHORITY", "PROHIBITION", "STATEMENT", "DEFINITION", "DELEGATION"):
        print(f"  {k:<11} : {dist.get(k, 0)}건")
    print(f"  None (룰 미매칭): {dist.get(None, 0)}건")
    print()

    # needs review
    needs = [c for c in clauses if c.get("needs_review")]
    review_rate = (100.0 * len(needs) / max(1, len(clauses)))
    print(f"[NEEDS_REVIEW] {len(needs)}건 ({review_rate:.1f}%)")
    print(f"  - \"및\" 모호성    : {rule_counts.get('review_and', 0)}건")
    print(f"  - \"또는\" 묶음 처리: {rule_counts.get('review_or_keep', 0)}건")
    print(f"  - \"하거나\" 분리 후: {rule_counts.get('review_or_split', 0)}건")
    print(f"  - content_type 미분류: {rule_counts.get('review_no_content_type', 0)}건")
    print()

    # sample output 5 parts, sector diverse
    print("[SAMPLE 출력 5건] (sector 골고루)")
    picked = []
    seen_sector = set()
    for p in sampled_parts:
        a = articles.get(p["article_id"], {})
        law_name = laws.get(a.get("law_id") or "", "")
        s = sector_from_law_name(law_name)
        if s not in seen_sector:
            picked.append((p, s))
            seen_sector.add(s)
        if len(picked) >= 5:
            break
    if len(picked) < 5:
        picked = [(p, sector_from_law_name(laws.get(articles.get(p["article_id"], {}).get("law_id") or "", "")))
                  for p in sampled_parts[:5]]

    clauses_by_part = defaultdict(list)
    for c in clauses:
        clauses_by_part[c["source_part_id"]].append(c)

    for p, s in picked:
        a = articles.get(p["article_id"], {})
        title = a.get("article_internal_key") or str(p["article_id"])
        print("  " + "─" * 45)
        print(f"  [{s}] {title}")
        print("  PART 원문 (전체):")
        txt = (p.get("part_text") or "").replace("\n", " ").strip()
        print(f"    \"{txt}\"")
        part_clauses = clauses_by_part.get(p["id"], [])
        print()
        print(f"  분해 결과 ({len(part_clauses)} clauses):")
        inherit_exec = None
        for idx, c in enumerate(part_clauses, start=1):
            ex = c.get("executor_text") or inherit_exec
            if ex and not inherit_exec:
                inherit_exec = ex
            print(f"    [{idx}] executor: {ex or ''}")
            if c.get("condition_text"):
                print(f"        condition: {c['condition_text']}")
            print(f"        action  : {c.get('action_text') or ''}")
            print(f"        content_type: {c.get('content_type')}")
            print(f"        applied_rules: {c.get('applied_rules')}")
            print(f"        needs_review: {'true' if c.get('needs_review') else 'false'}")
            if c.get("needs_review"):
                print(f"        review_reason: {c.get('review_reason')}")

    # ---------------------------------------------------------------------
    # v1.8 검증 통계 (dry-run 종료 직전)
    # ---------------------------------------------------------------------
    print()
    print("[v1.8 검증 통계]")

    # 1) executor 채움률 (DELEGATION 제외: 행위 의무가 아닌 조항)
    targets = ("OBLIGATION", "PROHIBITION", "AUTHORITY")
    target_clauses = [c for c in clauses if c.get("content_type") in targets]
    target_total = len(target_clauses)
    target_has_exec = sum(1 for c in target_clauses if c.get("executor_text"))
    pct_exec = (100.0 * target_has_exec / max(1, target_total))
    print(f"  - executor 채움률 (OBLIGATION/PROHIBITION/AUTHORITY): {target_has_exec}/{target_total} ({pct_exec:.1f}%)")

    # 2) 가짜 executor 잔존 체크 (목표: 모두 0)
    fake_counts = {
        "jal_chodaen(\\s(또|또는|및|에)$)": 0,
        "wiim_jal(령으로\\s*정하?$)": 0,
        "soobum(^다음\\s*각\\s*호)": 0,
        "pilyo(^필요한\\s*사항(은|을))": 0,
        "badeun(받은\\s*(자|사람)$)": 0,
        "too_short(L<2)": 0,
    }
    for c in target_clauses:
        ex = (c.get("executor_text") or "").strip()
        if not ex:
            continue
        if re.search(r"\s(또|또는|및|에)$", ex):
            fake_counts["jal_chodaen(\\s(또|또는|및|에)$)"] += 1
        if re.search(r"령으로\s*정하?$", ex) or re.search(r"으?로\s*정하?$", ex):
            fake_counts["wiim_jal(령으로\\s*정하?$)"] += 1
        if re.search(r"^다음\s*각\s*호", ex):
            fake_counts["soobum(^다음\\s*각\\s*호)"] += 1
        if re.search(r"^필요한\s*사항(?:은|을)", ex):
            fake_counts["pilyo(^필요한\\s*사항(은|을))"] += 1
        if re.search(r"받은\s*(?:자|사람)$", ex):
            fake_counts["badeun(받은\\s*(자|사람)$)"] += 1
        if len(ex) < 2:
            fake_counts["too_short(L<2)"] += 1

    print("  - 가짜 executor 잔존(목표 0):")
    for k, v in fake_counts.items():
        print(f"      {k}: {v}")

    # 3) recipient 채움률 (보고/신고/제출/통보/통지 동사 포함)
    report_clauses = [
        c for c in target_clauses
        if re.search(r"신고|보고|제출|통보|통지", c.get("action_text") or "")
    ]
    report_total = len(report_clauses)
    report_has_recipient = sum(1 for c in report_clauses if c.get("recipient_text"))
    pct_rec = (100.0 * report_has_recipient / max(1, report_total))
    print(f"  - recipient 채움률 (report actions): {report_has_recipient}/{report_total} ({pct_rec:.1f}%)")

    # 4) inherit 적용 분포 (paragraph/article/direct/still_null)
    src = Counter()
    for c in target_clauses:
        rules = c.get("applied_rules") or []
        if "inherit_paragraph" in rules:
            src["paragraph_inherit"] += 1
        elif "inherit_article" in rules:
            src["article_inherit"] += 1
        elif not c.get("executor_text"):
            src["still_null"] += 1
        else:
            src["direct"] += 1
    print("  - inherit 분포 (OBL/PROH/AUTH):")
    for k in ("direct", "paragraph_inherit", "article_inherit", "still_null"):
        print(f"      {k}: {src.get(k, 0)}")

    # 4-1) still_null 분해 통계 (executor NULL 원인 분해)
    still_nulls = [
        c for c in target_clauses
        if not c.get("executor_text")
        and "inherit_paragraph" not in (c.get("applied_rules") or [])
        and "inherit_article" not in (c.get("applied_rules") or [])
    ]
    print("  - still_null 분해 통계:")
    print(f"      total_still_null: {len(still_nulls)}")

    # (A) 문장 시작 패턴 (주어 미인식/괄호/인용 등)
    start_bucket = Counter()
    for c in still_nulls:
        t = (c.get("action_text") or c.get("source_text") or "").strip()
        if not t:
            start_bucket["(empty)"] += 1
            continue
        if t.startswith("(") or t.startswith("（"):
            start_bucket["starts_with_paren"] += 1
        elif t.startswith("제") and re.match(r"^제\s*\d+", t):
            start_bucket["starts_with_article_ref"] += 1
        elif t.startswith("이 ") or t.startswith("이때") or t.startswith("이 경우"):
            start_bucket["starts_with_pronoun_clause"] += 1
        elif t.startswith("다만"):
            start_bucket["starts_with_proviso"] += 1
        elif re.match(r"^[0-9①②③④⑤⑥⑦⑧⑨⑩]", t):
            start_bucket["starts_with_enumeration"] += 1
        else:
            start_bucket["other"] += 1
    for k, v in start_bucket.most_common(8):
        print(f"      start:{k}: {v}")

    # (B) 조건/주기/서식 유무 (정보가 앞에 치우친 경우 executor 미검출 가능)
    has_cond = sum(1 for c in still_nulls if c.get("condition_text"))
    has_cycle = sum(1 for c in still_nulls if c.get("cycle_text"))
    has_form = sum(1 for c in still_nulls if c.get("form_token"))
    print(f"      has_condition_text: {has_cond}")
    print(f"      has_cycle_text: {has_cycle}")
    print(f"      has_form_token: {has_form}")

    # (C) 샘플 5건 (원인 파악용, 앞 120자)
    print("      samples (first 5, head 120 chars):")
    for c in still_nulls[:5]:
        t = (c.get("action_text") or c.get("source_text") or "").replace("\n", " ").strip()
        head = (t[:120] + ("…" if len(t) > 120 else ""))
        print(f"        - {head}")

    # 4-2) v1.9 추가 지표 (역순 주제표시 / 사물 주어 / 의심)
    print()
    print("[v1.9 추가 지표]")
    rev_n = sum(
        1 for c in target_clauses if "v19_reverse_executor" in (c.get("applied_rules") or [])
    )
    lex_n = sum(
        1 for c in target_clauses if "v19_lexicon_executor" in (c.get("applied_rules") or [])
    )
    pfx_n = sum(
        1
        for c in target_clauses
        if "v19_prefix_fallback_executor" in (c.get("applied_rules") or [])
    )
    rxfb_n = sum(
        1 for c in target_clauses if "v19_rx_executor_fallback" in (c.get("applied_rules") or [])
    )
    direct_extract_ok = sum(
        1
        for c in target_clauses
        if any(
            t in (c.get("applied_rules") or [])
            for t in (
                "v19_reverse_executor",
                "v19_lexicon_executor",
                "v19_prefix_fallback_executor",
            )
        )
    )
    obj_subj_tag = sum(
        1 for c in target_clauses if "v19_object_subject" in (c.get("applied_rules") or [])
    )
    sus_tag = sum(
        1 for c in target_clauses if "v19_suspicious_executor" in (c.get("applied_rules") or [])
    )
    obj_subj_nr = sum(
        1
        for c in target_clauses
        if c.get("needs_review")
        and "사물 주어 의심" in (c.get("review_reason") or "")
    )
    print(f"  - 직접 추출 성공 (reverse): {rev_n}")
    print(f"  - 직접 추출 성공 (lexicon): {lex_n}")
    print(f"  - 직접 추출 성공 (prefix fallback): {pfx_n}")
    print(f"  - 직접 추출 (RX fallback): {rxfb_n}")
    print(f"  - 직접 추출 성공 합계 (reverse+lexicon+prefix): {direct_extract_ok}")
    print(f"  - 사물 주어 태그(v19_object_subject): {obj_subj_tag}")
    print(f"  - 사물 주어 needs_review(문구 포함): {obj_subj_nr}")
    print(f"  - 의심 케이스 태그(v19_suspicious_executor): {sus_tag}")
    print(f"  - inherit_article 적용 건수(rule_counts): {rule_counts.get('inherit_article', 0)}")

    # 5) needs_review 상위 사유
    print()
    print("[needs_review 상위 10]")
    rr = Counter()
    for c in clauses:
        if not c.get("needs_review"):
            continue
        reason = c.get("review_reason") or "(no_reason)"
        rr[reason] += 1
    for reason, cnt in rr.most_common(10):
        print(f"      {cnt:>5}  {reason}")

    print("  " + "─" * 45)
    print()
    print("[DRY-RUN 종료] 실제 DB 쓰기 없음. 적용은 --apply 사용.")


def main():
    parser = argparse.ArgumentParser(description="의미절 분해 v1.9.1 (iter1)")
    parser.add_argument("--sample-size", type=int, default=50,
                        help="첫 iter sample 크기. 기본 50.")
    parser.add_argument('--sampling', choices=['random', 'stratified'], default='random',
        help="random=모집단 비율 그대로 무작위(default), stratified=sector/길이 계층화")
    parser.add_argument("--dry-run", action="store_true",
                        help="DB 쓰기 없이 stdout 출력만.")
    parser.add_argument("--apply", action="store_true",
                        help="실제 DB 적용. dry-run과 상호 배타.")
    parser.add_argument("--truncate-first", action="store_true",
                        help="적용 전 semantic_clause_iter1 truncate. 재실행 시.")
    parser.add_argument("--seed", type=int, default=42,
                        help="sampling seed. 같은 결과 재현용.")
    parser.add_argument('--debug-classify', action='store_true',
        help='classify_content_type 매칭 실패 케이스의 text repr 출력')
    parser.add_argument(
        '--debug-inherit',
        action='store_true',
        help='article inherit 적용 후 NULL executor 분포 디버그 출력',
    )
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        print("[WARN] --dry-run/--apply 미지정 → dry-run으로 진행", file=sys.stderr)
        args.dry_run = True
    if args.dry_run and args.apply:
        print("[ERROR] --dry-run과 --apply는 상호 배타", file=sys.stderr)
        sys.exit(1)

    # 모집단 fetch (order('id') 필수)
    all_paragraphs = fetch_population_paragraphs()
    article_ids = list({p["article_id"] for p in all_paragraphs if p.get("article_id")})
    articles = fetch_articles(article_ids)
    population = filter_deleted(eligible_population(all_paragraphs, articles))

    law_ids = list({articles[p["article_id"]].get("law_id") for p in population if articles.get(p["article_id"])})
    laws = fetch_laws([lid for lid in law_ids if lid])

    pop_len_pct = population_length_pct(population)
    pop_laws = len({articles[p["article_id"]].get("law_id") for p in population if articles.get(p["article_id"])})

    rng = random.Random(args.seed)
    if args.sampling == "random":
        sampled_parts = rng.sample(population, min(args.sample_size, len(population)))
        # sample counts
        sector_counts = Counter()
        length_counts = Counter()
        for p in sampled_parts:
            a = articles.get(p["article_id"], {})
            law_name = laws.get(a.get("law_id") or "", "")
            sector_counts[sector_from_law_name(law_name)] += 1
            length_counts[length_bucket(p.get("part_text") or "")] += 1
        sector_counts = dict(sector_counts)
        length_counts = dict(length_counts)
    else:
        sampled_parts, sector_counts, length_counts = stratified_sample(
            population, articles, laws, sample_size=args.sample_size, seed=args.seed
        )

    rule_counts: Counter = Counter()
    clauses: List[Dict[str, Any]] = []
    for p in sampled_parts:
        if args.debug_classify:
            p["_debug_classify"] = True
        a = articles.get(p["article_id"], {})
        law_name = laws.get(a.get("law_id") or "", "")
        sector = sector_from_law_name(law_name)
        clauses.extend(decompose_part(p, sector=sector, rule_counts=rule_counts))

    # v1.8 PATCH 5: article 단위 inherit (paragraph inherit 이후, dry-run/insert 공통)
    inherit_n = post_process_article_inherit(clauses)
    rule_counts["inherit_article"] = inherit_n
    if args.debug_inherit:
        tgt_ct = ("OBLIGATION", "PROHIBITION", "AUTHORITY")
        post_null = sum(
            1 for c in clauses
            if c.get("content_type") in tgt_ct and not c.get("executor_text")
        )
        art_n = len({c.get("source_article_id") for c in clauses if c.get("source_article_id")})
        print(
            f"[DEBUG-INHERIT] articles={art_n} inherit_article_applied={inherit_n} "
            f"null_executor_OBL_PROH_AUTH={post_null}",
            file=sys.stderr,
        )

    # review breakdown counters (dry-run 포맷용)
    rule_counts["review_and"] = sum(1 for c in clauses if c.get("needs_review") and '"및"' in (c.get("review_reason") or ""))
    rule_counts["review_or_keep"] = sum(1 for c in clauses if c.get("needs_review") and '"또는" 묶음 처리' in (c.get("review_reason") or ""))
    rule_counts["review_or_split"] = sum(1 for c in clauses if c.get("needs_review") and '"하거나" 분리 후' in (c.get("review_reason") or ""))
    rule_counts["review_no_content_type"] = sum(1 for c in clauses if c.get("needs_review") and "content_type 미분류" in (c.get("review_reason") or ""))

    if args.dry_run:
        print_dry_run(
            sampled_parts=sampled_parts,
            articles=articles,
            laws=laws,
            clauses=clauses,
            rule_counts=rule_counts,
            sample_size=args.sample_size,
            seed=args.seed,
            sampling=args.sampling,
            population_n=len(population),
            population_laws=pop_laws,
            population_len_pct=pop_len_pct,
            sector_counts=sector_counts,
            length_counts=length_counts,
        )
        return

    if args.truncate_first:
        ZERO_UUID = "00000000-0000-0000-0000-000000000000"
        with_retry(lambda: supabase.from_("semantic_clause_iter1").delete().neq("id", ZERO_UUID).execute())
        print("[TRUNCATE] semantic_clause_iter1 비움 완료")

    total_inserted = 0
    reset_every = 1000
    since_reset = 0
    for i in range(0, len(clauses), 100):
        batch = clauses[i:i + 100]
        def _ins():
            return supabase.from_("semantic_clause_iter1").insert(batch).execute()
        with_retry(_ins)
        total_inserted += len(batch)
        since_reset += len(batch)
        if since_reset >= reset_every:
            reset_supabase()
            time.sleep(1)
            since_reset = 0

    if total_inserted != len(clauses):
        print(f"[CRITICAL] insert mismatch: inserted={total_inserted}, expected={len(clauses)}", file=sys.stderr)
        sys.exit(1)

    print(f"[DONE] inserted {total_inserted} clauses into semantic_clause_iter1")


if __name__ == "__main__":
    main()

