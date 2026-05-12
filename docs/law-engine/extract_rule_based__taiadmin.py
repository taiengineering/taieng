#!/usr/bin/env python3
"""
TAI 법령엔진 룰 기반 추출기 v3.7 (LENGTH 필터 제거, 모든 article 처리)

대표 명령: "(C) 모든 32,808 article 처리"

v3.6 → v3.7 변경:
- SQL `LENGTH(article_text) > 100` 필터 제거 → `IS NOT NULL`만 유지
- 짧은 article 8,754건 추가 처리 가능 (정의·삭제·간단 조항 위주, 대부분 placeholder 예상)
- 누락 0 원칙 강화

NOTE: v3.8은 잘못된 변경(drafts 0개 article의 placeholder를 paragraph 단위 여러 건으로)
이었음. 이전 v3.3/v3.4 동작 = drafts 0개 article은 placeholder 1건만. v3.7이 정확함.

작성: 2026-05-05 (S14, v3.7 — 재push)
"""

import argparse
import os
import re
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

try:
    from supabase import Client, create_client
except ImportError:
    print("[ERROR] pip install supabase", file=sys.stderr)
    sys.exit(1)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = (
    os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    or os.environ.get("SUPABASE_SERVICE_KEY")
    or os.environ.get("SUPABASE_KEY")
)
if not SUPABASE_URL or not SUPABASE_KEY:
    print("[ERROR] SUPABASE 환경변수 없음.", file=sys.stderr)
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


SKIP_TITLE_PATTERNS = [
    ("SKIP_001", r"^정의|^용어"),
    ("SKIP_002", r"벌칙|과태료|양벌|행정처분|과징금"),
    ("SKIP_003", r"^부칙|시행일|경과조치|특례"),
    ("SKIP_004", r"재검토|타당성"),
    ("SKIP_006", r"^목적$"),
    ("SKIP_007", r"적용 ?(범위|대상)"),
    ("SKIP_009", r"^수수료|수수료 등|교육비|등록비"),
    ("SKIP_010", r"(벌칙|과태료).*징수"),
]

SKIP_TEXT_PATTERNS = [("SKIP_011", r"관하여는 제\d+조.*준용한다")]

AUTHORITY_PATTERNS = [r"할 수 있다\.?", r"필요하다고 인정"]

OBLIGATION_PATTERNS = [
    r"하여야 한다\.?", r"해야 한다\.?", r"되어야 한다\.?",
    r"하여서는 아니 된다\.?", r"해서는 아니 된다\.?",
    r"하여야 하며", r"해야 하며", r"하여야 함", r"해야 함",
]

SUBJECT_PATTERNS = [
    (r"사업주는", "사업주"), (r"안전관리자는", "안전관리자"),
    (r"보건관리자는", "보건관리자"), (r"건설업자는", "건설업자"),
    (r"발주자는", "발주자"), (r"발주청은", "발주청"),
    (r"도급인은", "도급인"), (r"수급인은", "수급인"),
    (r"근로자는", "근로자"), (r"분양사업자는", "분양사업자"),
    (r"전기사업자는", "전기사업자"), (r"전기통신사업자는", "전기통신사업자"),
    (r"자동차제작자는", "자동차제작자"), (r"관계인은", "관계인"),
    (r"관리주체는", "관리주체"), (r"공공기관은", "공공기관"),
    (r"관리자는", "관리자"), (r"총량관리사업자는", "총량관리사업자"),
    (r"피출연자는", "피출연자"), (r"건설공사도급인은", "건설공사도급인"),
    (r"고용노동부장관은", "고용노동부장관"),
    (r"기후에너지환경부장관은", "기후에너지환경부장관"),
    (r"국토교통부장관은", "국토교통부장관"),
    (r"식품의약품안전처장은", "식품의약품안전처장"),
    (r"환경부장관은", "환경부장관"),
    (r"중앙행정기관의 장은", "중앙행정기관의 장"),
    (r"지방자치단체의 장은", "지방자치단체의 장"),
    (r"위원회는", "위원회"),
    (r"소방서장은", "소방서장"), (r"소방청장은", "소방청장"),
    (r"보건복지부장관은", "보건복지부장관"),
    (r"공단은", "공단"),
    (r"안전인증기관은", "안전인증기관"),
    (r"안전관리전문기관[은가]", "안전관리전문기관"),
    (r"보건관리전문기관[은가]", "보건관리전문기관"),
    (r"석면해체.제거업자[는가]", "석면해체·제거업자"),
    (r"지도사[는가]", "지도사"), (r"건축사[는가]", "건축사"),
    (r"건축사보[는가]", "건축사보"),
    (r"안전보건진단기관[은가]", "안전보건진단기관"),
    (r"건설재해예방전문지도기관[은가]", "건설재해예방전문지도기관"),
    (r"제조업자[는가]", "제조업자"),
    (r"수입업자[는가]", "수입업자"),
    (r"운영자[는가]", "운영자"),
    (r"건설·운영자[는가]", "건설·운영자"),
    (r"설치기관[은가]", "설치기관"),
    (r"검진기관[은가]", "검진기관"),
    (r"의료기관의 장[은가]", "의료기관의 장"),
    (r"건설사업관리용역사업자[는가]", "건설사업관리용역사업자"),
    (r"시[ㆍ·\W]*도지사는", "시·도지사"),
    (r"시장[ㆍ·\W]*군수[ㆍ·\W]*구청장은", "시장·군수·구청장"),
]

TYPE_PATTERNS = [
    ("REPORT", r"(보고|통지|통보|제출|공개|게시|신고|발급)(?:하|해|함)"),
    ("INSPECT", r"(확인|검사|평가|점검|조사|진단|심사|측정)(?:하|해|함)"),
    ("RECORD", r"(기록|보존|작성|기명날인|보관|기재)(?:하|해|함)"),
    ("INSTALL", r"(설치|시공|구축|장착|부착)(?:하|해|함)"),
    ("POSSESS", r"(?:비치|소지|구비)(?:하|해)|갖추어 (?:두는|두어)"),
    ("EDUCATION", r"(교육|훈련)(?:하|해|시)"),
    ("APPOINT", r"(선임|임명|지정|위촉)(?:하|해|함)"),
]

SECTOR_BY_LAW = [
    ("FIRE", r"화재|소방|위험물"),
    ("ENV", r"환경|대기|물환경|수질|폐기물|소음|탄소"),
    ("CHEMICAL", r"화학|화학물질"),
    ("GAS", r"가스"),
    ("ELECTRIC", r"전기|전력"),
    ("CONSTRUCTION", r"건설|건설기계"),
    ("BUILDING", r"건축|건축물|시설물|주택|기계설비|건축사"),
    ("INDUSTRIAL", r"산업안전|산업재해|중대재해"),
]

NFTC_TRIGGER_PATTERNS = [
    r"다음의?\s*(?:기준|각 호|어느 하나|규정|사항|방식)",
    r"다음과 같(?:다|이)",
    r"다음에 따라",
    r"아래 (?:기준|규정)",
]

COND_AREA = re.compile(r"(\d+(?:,\d{3})*)\s*(㎡|m²|평방미터)\s*(이상|초과|이하|미만)")
COND_WORKER = re.compile(r"(\d+)\s*명\s*(이상|초과|이하|미만)")
COND_AMOUNT = re.compile(r"(\d+)\s*(억|만)\s*원\s*(이상|초과|이하|미만)")
COND_DURATION = re.compile(r"(\d+)\s*(일|개월|년)\s*(이내|이전)")
OPERATOR_MAP = {"이상": "gte", "초과": "gt", "이하": "lte", "미만": "lt", "이내": "lte", "이전": "lt"}


def pre_check_skip(article_title, article_text):
    for code, pattern in SKIP_TITLE_PATTERNS:
        if re.search(pattern, article_title or ""):
            return code
    if article_text and len(article_text) < 200:
        for code, pattern in SKIP_TEXT_PATTERNS:
            if re.search(pattern, article_text):
                return code
    return None


def split_paragraphs(article_text):
    bracket_markers = list(re.finditer(r'\[([①②③④⑤⑥⑦⑧⑨⑩])\]', article_text))
    if len(bracket_markers) >= 2:
        result = []
        for i, m in enumerate(bracket_markers):
            start = m.end()
            end = bracket_markers[i + 1].start() if i + 1 < len(bracket_markers) else len(article_text)
            text = article_text[start:end].strip()
            if text and text[0] in '①②③④⑤⑥⑦⑧⑨⑩':
                text = text[1:].strip()
            result.append((m.group(1), text))
        return result

    direct_markers = []
    seen = set()
    for m in re.finditer(r'([①②③④⑤⑥⑦⑧⑨⑩])', article_text):
        marker = m.group(1)
        if m.start() > 0 and article_text[m.start() - 1] == '[':
            continue
        if marker in seen:
            continue
        seen.add(marker)
        direct_markers.append((m.start(), marker))

    if len(direct_markers) >= 2:
        direct_markers.sort()
        result = []
        for i, (pos, marker) in enumerate(direct_markers):
            end = direct_markers[i + 1][0] if i + 1 < len(direct_markers) else len(article_text)
            text = article_text[pos + 1:end].strip()
            result.append((marker, text))
        return result

    return [("①", article_text.strip())]


def split_clauses(para_text):
    pattern = re.compile(r'\[(\d+)\.\]\s*\d+\.\s*(.+?)(?=\[\d+\.\]|\Z)', re.DOTALL)
    matches = pattern.findall(para_text)
    if len(matches) >= 2:
        return [(no, text.strip()) for no, text in matches]
    return None


def split_clauses_nftc(para_text):
    has_trigger = any(re.search(p, para_text) for p in NFTC_TRIGGER_PATTERNS)
    if not has_trigger:
        return None

    direct_markers = []
    seen = set()
    for m in re.finditer(r'(?:^|[\s.])(\d+)\.\s+(?=[가-힣A-Za-z])', para_text):
        marker = m.group(1)
        try:
            n = int(marker)
        except ValueError:
            continue
        if n < 1 or n > 30:
            continue
        if marker in seen:
            continue
        marker_pos = m.start(1)
        if marker_pos > 0 and para_text[marker_pos - 1] == '[':
            continue
        seen.add(marker)
        direct_markers.append((marker_pos, marker, n))

    if len(direct_markers) < 2:
        return None

    nums = sorted([m[2] for m in direct_markers])
    if nums[0] != 1:
        return None
    for i in range(len(nums) - 1):
        if nums[i + 1] - nums[i] != 1:
            return None

    direct_markers.sort()
    result = []
    for i, (pos, marker, n) in enumerate(direct_markers):
        end = direct_markers[i + 1][0] if i + 1 < len(direct_markers) else len(para_text)
        text_start = pos + len(marker) + 1
        while text_start < end and para_text[text_start].isspace():
            text_start += 1
        text = para_text[text_start:end].strip()
        if len(text) >= 15:
            result.append((marker, text))
    if len(result) >= 2:
        return result
    return None


def split_subitems(clause_text):
    pattern1 = re.compile(
        r'\[([가나다라마바사아자차카타파하])\.\]\s*[가나다라마바사아자차카타파하]\.\s*(.+?)(?=\[[가-하]\.\]|\Z)',
        re.DOTALL
    )
    matches = pattern1.findall(clause_text)
    if len(matches) >= 2:
        return [(no, text.strip()) for no, text in matches]

    direct_markers = []
    seen = set()
    for m in re.finditer(r'([가나다라마바사아자차카타파하])\.', clause_text):
        marker = m.group(1)
        if m.start() > 0 and clause_text[m.start() - 1] == '[':
            continue
        if m.start() > 0 and clause_text[m.start() - 1].isalnum():
            continue
        if marker in seen:
            continue
        seen.add(marker)
        direct_markers.append((m.start(), marker))

    if len(direct_markers) >= 2:
        direct_markers.sort()
        result = []
        for i, (pos, marker) in enumerate(direct_markers):
            end = direct_markers[i + 1][0] if i + 1 < len(direct_markers) else len(clause_text)
            text = clause_text[pos + 2:end].strip()
            if len(text) >= 10:
                result.append((marker, text))
        if len(result) >= 2:
            return result

    return None


def split_by_obligation_endings(para_text):
    pattern = re.compile(
        r'(.{30,400}?(?:하여야 한다|해야 한다|되어야 한다|아니 된다|하여야 하며|해야 하며|하여야 함|해야 함)\.?,?)',
        re.DOTALL
    )
    matches = pattern.findall(para_text)
    if len(matches) >= 2:
        return [m.strip().rstrip(',') for m in matches if len(m.strip()) >= 20]
    return None


def split_by_proviso(para_text):
    parts = re.split(r'\.\s*다만,?\s*', para_text, maxsplit=1)
    if len(parts) == 2 and len(parts[1]) > 20:
        return (parts[0].strip() + ".", "다만, " + parts[1].strip())
    return None


def is_authority_only(text):
    has_authority = any(re.search(p, text) for p in AUTHORITY_PATTERNS)
    has_obligation = any(re.search(p, text) for p in OBLIGATION_PATTERNS)
    return has_authority and not has_obligation


def has_obligation_verb(text):
    return any(re.search(p, text) for p in OBLIGATION_PATTERNS)


def match_subject(text):
    head = text[:300]
    for pattern, target in SUBJECT_PATTERNS:
        if re.search(pattern, head):
            return target
    return None


def classify_type(text):
    for type_name, pattern in TYPE_PATTERNS:
        if re.search(pattern, text):
            return type_name
    return "ACTION"


def classify_sector(law_name):
    for sector, pattern in SECTOR_BY_LAW:
        if re.search(pattern, law_name):
            return sector
    return "INDUSTRIAL"


def extract_condition(text):
    m = COND_AREA.search(text)
    if m:
        return "area", OPERATOR_MAP.get(m.group(3), "gte"), m.group(1).replace(",", "")
    m = COND_WORKER.search(text)
    if m:
        return "worker_count", OPERATOR_MAP.get(m.group(2), "gte"), m.group(1)
    m = COND_AMOUNT.search(text)
    if m:
        unit = 100_000_000 if m.group(2) == "억" else 10_000
        return "contract_amount", OPERATOR_MAP.get(m.group(3), "gte"), str(int(m.group(1)) * unit)
    m = COND_DURATION.search(text)
    if m:
        return "duration", OPERATOR_MAP.get(m.group(2), "lte"), m.group(1)
    return None, None, None


def normalize_summary(text):
    s = re.sub(r"[ㆍ・]", "·", text)
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) > 500:
        s = s[:500] + "..."
    return s


def build_draft(text, target, target_conf, para_label, rule_id, fallback_target=None):
    if not target and fallback_target:
        target = fallback_target
        target_conf = "medium"
    if not target:
        target = "(target 추론 실패)"
        target_conf = "low"
    obligation_type = classify_type(text)
    summary = normalize_summary(text)
    cond_code, cond_op, cond_val = extract_condition(text)
    confidence_pct = 85 if target_conf == "high" else 70 if target_conf == "medium" else 60
    return {
        "summary": summary, "target": target, "type": obligation_type,
        "confidence_pct": confidence_pct,
        "condition_code": cond_code, "condition_op": cond_op, "condition_val": cond_val,
        "para_no": para_label,
        "reasoning": f"룰 기반 v3.7 — {para_label} ({rule_id}). 본문 그대로 적재.",
        "is_placeholder": False, "skip_reason": None,
    }


def build_placeholder(text, para_label, skip_reason):
    summary = normalize_summary(text)
    return {
        "summary": summary,
        "target": "(미정 — placeholder)", "type": "ACTION", "confidence_pct": 50,
        "condition_code": None, "condition_op": None, "condition_val": None,
        "para_no": para_label,
        "reasoning": f"룰 기반 v3.7 — {para_label} ({skip_reason}). paragraph 단위 placeholder.",
        "is_placeholder": True, "skip_reason": skip_reason,
    }


def deduplicate_drafts(drafts):
    seen = set()
    result = []
    for d in drafts:
        key = (d["summary"], d.get("is_placeholder", False))
        if key in seen:
            continue
        seen.add(key)
        result.append(d)
    return result


def extract_rule_based(article_id, law_name, article_no, article_title, article_text):
    sector = classify_sector(law_name)
    skip_code = pre_check_skip(article_title, article_text)
    if skip_code:
        return {
            "drafts": [], "status": "placeholder_article",
            "skip_code": skip_code, "sector": sector,
            "self_check": {
                "reasoning": f"{skip_code} 사전 매칭 (article 전체)",
                "extracted_count": 1, "skipped_paragraphs": [skip_code],
                "confidence_in_completeness": "medium",
            },
        }

    paragraphs = split_paragraphs(article_text)
    drafts = []

    for para_no, para_text in paragraphs:
        if not has_obligation_verb(para_text):
            if is_authority_only(para_text):
                drafts.append(build_placeholder(para_text, f"{para_no}항", "SKIP_005_authority"))
            else:
                drafts.append(build_placeholder(para_text, f"{para_no}항", "no_obligation_verb"))
            continue

        para_target = match_subject(para_text)
        para_target_conf = "high" if para_target else "medium"

        clauses = split_clauses(para_text)
        clause_rule = "EXTRACT_004"
        if not clauses:
            clauses = split_clauses_nftc(para_text)
            clause_rule = "EXTRACT_004_NFTC"

        if clauses:
            if clause_rule == "EXTRACT_004":
                first_clause_pos = para_text.find("[1.]")
            else:
                first_clause_match = re.search(r'(?:^|[\s.])1\.\s+', para_text)
                first_clause_pos = first_clause_match.start() if first_clause_match else -1

            if first_clause_pos > 0:
                header = para_text[:first_clause_pos].strip()
                if len(header) >= 20:
                    drafts.append(build_draft(
                        header, para_target, para_target_conf,
                        f"{para_no}항 (헤더)", f"{clause_rule}_header",
                        fallback_target=para_target,
                    ))
            for clause_no, clause_text in clauses:
                subitems = split_subitems(clause_text)
                if subitems:
                    first_sub_pos = -1
                    for sub_marker in '가나다라마바사아자차':
                        p = clause_text.find(f"{sub_marker}.")
                        if p > 0 and (p == 0 or not clause_text[p-1].isalnum()):
                            first_sub_pos = p
                            break
                    if first_sub_pos > 20:
                        sub_header = clause_text[:first_sub_pos].strip()
                        sub_target = match_subject(sub_header) or para_target
                        drafts.append(build_draft(
                            sub_header, sub_target, "high" if match_subject(sub_header) else para_target_conf,
                            f"{para_no}항 {clause_no}호 (헤더)", "EXTRACT_007_header",
                            fallback_target=para_target,
                        ))
                    for sub_no, sub_text in subitems:
                        sub_target = match_subject(sub_text) or para_target
                        sub_target_conf = "high" if match_subject(sub_text) else para_target_conf
                        drafts.append(build_draft(
                            sub_text, sub_target, sub_target_conf,
                            f"{para_no}항 {clause_no}호 {sub_no}목", "EXTRACT_007",
                            fallback_target=para_target,
                        ))
                else:
                    sub_target = match_subject(clause_text) or para_target
                    sub_target_conf = "high" if match_subject(clause_text) else para_target_conf
                    drafts.append(build_draft(
                        clause_text, sub_target, sub_target_conf,
                        f"{para_no}항 {clause_no}호", clause_rule,
                        fallback_target=para_target,
                    ))
            continue

        sub_obs = split_by_obligation_endings(para_text)
        if sub_obs:
            for i, sub_text in enumerate(sub_obs, 1):
                sub_target = match_subject(sub_text) or para_target
                sub_target_conf = "high" if match_subject(sub_text) else para_target_conf
                drafts.append(build_draft(
                    sub_text, sub_target, sub_target_conf,
                    f"{para_no}항 #{i}", "EXTRACT_005",
                    fallback_target=para_target,
                ))
            continue

        proviso = split_by_proviso(para_text)
        if proviso:
            main_text, proviso_text = proviso
            for sub_text, sub_label in [(main_text, "메인"), (proviso_text, "단서")]:
                sub_target = match_subject(sub_text) or para_target
                sub_target_conf = "high" if match_subject(sub_text) else para_target_conf
                if has_obligation_verb(sub_text):
                    drafts.append(build_draft(
                        sub_text, sub_target, sub_target_conf,
                        f"{para_no}항 ({sub_label})", "EXTRACT_006",
                        fallback_target=para_target,
                    ))
                else:
                    drafts.append(build_placeholder(
                        sub_text, f"{para_no}항 ({sub_label})", "no_obligation_verb"
                    ))
            continue

        drafts.append(build_draft(
            para_text, para_target, para_target_conf,
            f"{para_no}항", "EXTRACT_001",
        ))

    drafts = deduplicate_drafts(drafts)

    real_drafts = [d for d in drafts if not d.get("is_placeholder")]
    placeholders_in_paragraphs = [d for d in drafts if d.get("is_placeholder")]

    return {
        "drafts": drafts,
        "status": "draft" if real_drafts else "placeholder_article",
        "skip_code": None, "sector": sector,
        "self_check": {
            "reasoning": f"룰 기반 v3.7 — {len(real_drafts)} drafts + {len(placeholders_in_paragraphs)} paragraph placeholders",
            "extracted_count": len(drafts), "skipped_paragraphs": [],
            "confidence_in_completeness": "medium",
        },
        "stats": {"real_drafts": len(real_drafts), "para_placeholders": len(placeholders_in_paragraphs)},
    }


def load_articles_from_sql(sql_where, limit=20):
    """v3.7: LENGTH 필터 제거. IS NOT NULL만 유지."""
    query = f"""
    SELECT a.id, m.law_name, a.article_no, a.article_title, a.article_text
    FROM law_article a
    JOIN law_master m ON m.id = a.law_id
    WHERE m.is_active = true
      AND a.article_text IS NOT NULL
      AND a.id NOT IN (SELECT DISTINCT article_id FROM law_rule_drafts WHERE article_id IS NOT NULL)
      AND a.is_deleted_in_version = false
      AND ({sql_where})
    ORDER BY RANDOM()
    LIMIT {int(limit)}
    """
    res = supabase.rpc("execute_sql", {"query": query}).execute()
    return res.data or []


def delete_existing(set_id, cycle):
    res = (
        supabase.table("law_rule_drafts").delete()
        .eq("ai_flags->>extraction_set", set_id)
        .eq("ai_flags->>extraction_cycle", str(cycle))
        .execute()
    )
    return len(res.data) if res.data else 0


def build_flags(set_id, cycle, self_check, skip_reason=None, is_placeholder=False):
    flags = {
        "extraction_set": set_id, "extraction_cycle": cycle,
        "from_pipeline": "rule_based_v3_7",
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "broken": False, "self_check": self_check,
        "needs_review": True,
        "review_reason": "rule_based_extraction" if not is_placeholder else "paragraph_placeholder",
    }
    if skip_reason:
        flags["skip_reason"] = skip_reason
        flags["placeholder_type"] = "paragraph_placeholder" if is_placeholder else "article_full"
    return flags


def insert_drafts(article_id, law_name, article_no, article_text, result, set_id, cycle):
    if result["status"] == "placeholder_article":
        flags = build_flags(set_id, cycle, result["self_check"],
                          skip_reason=result.get("skip_code"), is_placeholder=True)
        skip_code = result.get("skip_code", "RULE_NOT_MATCHED")
        row = {
            "law_name": law_name, "law_article": f"제{article_no}조",
            "article_id": article_id, "article_text": article_text,
            "obligation_summary": f"article 전체 SKIP ({skip_code}). 정정 회부.",
            "appointment_target": f"({skip_code})", "obligation_type": "ACTION",
            "sector": result["sector"],
            "ai_reasoning": result["self_check"]["reasoning"],
            "ai_confidence": 50, "ai_flags": flags, "status": "placeholder",
            "diagnosis_stage": 1,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        supabase.table("law_rule_drafts").insert([row]).execute()
        return 0, 1

    rows = []
    for d in result["drafts"]:
        is_ph = d.get("is_placeholder", False)
        flags = build_flags(set_id, cycle, result["self_check"],
                          skip_reason=d.get("skip_reason"), is_placeholder=is_ph)
        rows.append({
            "law_name": law_name, "law_article": f"제{article_no}조",
            "article_id": article_id, "article_text": article_text,
            "obligation_summary": d["summary"], "appointment_target": d["target"],
            "obligation_type": d["type"], "sector": result["sector"],
            "condition_code": d["condition_code"], "condition_operator": d["condition_op"],
            "condition_value": d["condition_val"],
            "ai_reasoning": d["reasoning"], "ai_confidence": d["confidence_pct"],
            "ai_flags": flags, "status": "placeholder" if is_ph else "draft",
            "diagnosis_stage": 1,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })
    if rows:
        supabase.table("law_rule_drafts").insert(rows).execute()
    drafts_n = sum(1 for d in result["drafts"] if not d.get("is_placeholder"))
    ph_n = sum(1 for d in result["drafts"] if d.get("is_placeholder"))
    return drafts_n, ph_n


def main():
    parser = argparse.ArgumentParser(description="TAI 룰 기반 추출 v3.7")
    parser.add_argument("--set", dest="set_id", required=True)
    parser.add_argument("--cycle", type=int, default=1)
    parser.add_argument("--sql-where", required=True)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--no-delete", action="store_true")
    args = parser.parse_args()

    print(f"=== {args.set_id} cycle={args.cycle} 룰 기반 v3.7 추출 ===")
    print("[INFO] LLM 호출 없음. LENGTH 필터 제거. 모든 article 처리.")

    articles = load_articles_from_sql(args.sql_where, args.limit)
    print(f"[INFO] 대상 article {len(articles)}건")

    if not args.no_delete:
        deleted = delete_existing(args.set_id, args.cycle)
        print(f"[INFO] 기존 {deleted}건 삭제")

    drafts_total = 0
    placeholders_total = 0

    for i, art in enumerate(articles, 1):
        try:
            result = extract_rule_based(
                art["id"], art.get("law_name", ""), art["article_no"],
                art.get("article_title") or "", art.get("article_text") or ""
            )
            n_drafts, n_ph = insert_drafts(
                art["id"], art.get("law_name", ""), art["article_no"],
                art.get("article_text") or "", result, args.set_id, args.cycle
            )
            drafts_total += n_drafts
            placeholders_total += n_ph
            marker = f"{n_drafts} drafts + {n_ph} ph"
            print(f"[{i}/{len(articles)}] {art.get('law_name', '')} 제{art['article_no']}조 — {marker}")
        except Exception as e:
            print(f"[{i}/{len(articles)}] ERROR {e}", file=sys.stderr)

    print(f"\n=== 완료 ===")
    print(f"[RESULT] drafts:       {drafts_total}")
    print(f"[RESULT] placeholders: {placeholders_total}")
    print(f"[RESULT] 비용:         $0.00 (LLM 호출 없음)")
    print(f"\n다음: validate_drafts.py --set {args.set_id} --cycle {args.cycle}")


if __name__ == "__main__":
    main()
