#!/usr/bin/env python3
"""
TAI 법령엔진 추출 스크립트 v3 (수집 단계)

v2 → v3 변경 (rule_patterns.yaml v1.2 원칙 반영):
1. status 통일: 'PENDING' → 'draft' (소문자) / 'placeholder' / 'needs_review'
2. PLACEHOLDER_001 정책: SKIP article도 1건 적재 (drafts 0건 사각지대 회피)
3. 입력 모드 확장: --input json|ids|sql
4. medium 자동 needs_review flag (검증 단계 회부)
5. 자기 충족 회피: PROMPT v3.0.1 그대로 (검증 룰 미적용)

실행:
  $ railway run python extract_iterative_v3.py --set SET-003 --cycle 1 --input json
  $ railway run python extract_iterative_v3.py --set SET-003 --cycle 1 --input ids --article-ids id1,id2,id3
  $ railway run python extract_iterative_v3.py --set SET-003 --cycle 1 --input sql \\
        --sql-where "law_id IN (SELECT id FROM law_master WHERE domain_code='BUILDING')" --limit 50

필수 환경변수 (Railway 자동 주입):
  - ANTHROPIC_API_KEY
  - SUPABASE_URL
  - SUPABASE_SERVICE_ROLE_KEY

작성: 2026-05-05 (S14 세션)
"""

import argparse
import json
import os
import re
import sys
import time
import uuid as uuid_lib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import anthropic
except ImportError:
    print("[ERROR] pip install anthropic", file=sys.stderr)
    sys.exit(1)

try:
    from supabase import Client, create_client
except ImportError:
    print("[ERROR] pip install supabase", file=sys.stderr)
    sys.exit(1)


# ============================================================
# 환경변수
# ============================================================
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = (
    os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    or os.environ.get("SUPABASE_SERVICE_KEY")
    or os.environ.get("SUPABASE_KEY")
)

if not ANTHROPIC_API_KEY:
    print("[ERROR] ANTHROPIC_API_KEY 없음. railway run 사용.", file=sys.stderr)
    sys.exit(1)
if not SUPABASE_URL or not SUPABASE_KEY:
    print("[ERROR] SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY 없음.", file=sys.stderr)
    sys.exit(1)


# ============================================================
# 모델·비용 설정
# ============================================================
MODEL = os.environ.get("EXTRACT_MODEL", "claude-opus-4-7")
MAX_TOKENS_PER_CALL = 4096
COST_LIMIT_USD = float(os.environ.get("COST_LIMIT_USD", "10.0"))
INPUT_PRICE_PER_MTOK = 15.0
OUTPUT_PRICE_PER_MTOK = 75.0
ROOT = Path(__file__).resolve().parent.parent.parent


# ============================================================
# PROMPT v3.0.1 (자기 충족 회피 위해 검증 룰 미적용)
# ============================================================
SYSTEM_PROMPT = """\
당신은 TAI 법령엔진 의무 추출기입니다. 대한민국 법령 조문에서 **현장 적용 의무**만 정확히 추출합니다.

## 핵심 원칙
1. 환각 금지: article_text에 명시적으로 있는 내용만 추출. 원문 용어 사용.
2. 다중 의무 분해: 주체 다르면 분해, 동사 다르면 분해. 의심스러우면 분해 (통합은 후처리).
3. self_check 필수: 매 article마다 self_check JSON 출력.
4. 모호하면 추출하고 confidence_in_completeness=medium 표시 (누락 회피).

## SKIP 패턴 (추출 안 함)
- SKIP_001 정의 / SKIP_002 벌칙 / SKIP_003 부칙 / SKIP_004 재검토
- SKIP_005 권한 위임 / SKIP_006 목적 / SKIP_007 적용범위
- SKIP_009 수수료/행정비용 / SKIP_010 벌칙·과태료 징수절차
- SKIP_011 준용 ("관하여는 제XX조를 준용한다")

## 권한·재량 (의무 아님)
- "할 수 있다" → 권한 / "필요하다고 인정하면" → 재량
- "하여야 한다" / "되어야 한다" / "해서는 아니 된다" → 의무

## 출력 스키마 (JSON)
```json
{
  "obligations": [
    {
      "obligation_summary": "...",
      "appointment_target": "사업주",
      "obligation_type": "ACTION",
      "sector": "INDUSTRIAL",
      "condition_code": "area",
      "condition_operator": "gte",
      "condition_value": "5000",
      "ai_reasoning": "article_text 인용",
      "ai_confidence": 90
    }
  ],
  "self_check": {
    "para_count": 7, "verb_count": 6, "clause_count": 0,
    "extracted_count": 8, "coverage_ratio": 1.14,
    "skipped_paragraphs": ["SKIP_005 ⑧항 (위임)"],
    "confidence_in_completeness": "high",
    "reasoning": "..."
  }
}
```

8종 type: ACTION/INSTALL/REPORT/INSPECT/EDUCATION/RECORD/APPOINT/POSSESS
8종 sector: BUILDING/INDUSTRIAL/CONSTRUCTION/CHEMICAL/GAS/ELECTRIC/FIRE/ENV
"""

USER_PROMPT_TEMPLATE = """\
다음 법령 조문에서 의무를 추출하세요.

law_name: {law_name}
article_no: {article_no}
article_title: {article_title}

article_text:
```
{article_text}
```

JSON만 출력하세요 (코드 펜스·설명 없이 순수 JSON).
"""


# ============================================================
# SKIP 사전 체크
# ============================================================
SKIP_TITLE_PATTERNS: List[Tuple[str, str]] = [
    ("SKIP_001", r"^정의|^용어"),
    ("SKIP_002", r"벌칙|과태료|양벌|행정처분|과징금"),
    ("SKIP_003", r"^부칙|시행일|경과조치|특례"),
    ("SKIP_004", r"재검토|타당성"),
    ("SKIP_006", r"^목적$"),
    ("SKIP_007", r"적용 ?(범위|대상)"),
    ("SKIP_009", r"^수수료|수수료 등|교육비|등록비"),
    ("SKIP_010", r"(벌칙|과태료).*징수"),
]

SKIP_TEXT_PATTERNS: List[Tuple[str, str]] = [
    ("SKIP_011", r"관하여는 제\d+조.*준용한다"),
]


def pre_check_skip(article_title: str, article_text: str) -> Optional[str]:
    """SKIP 패턴 매칭 시 코드 반환."""
    for code, pattern in SKIP_TITLE_PATTERNS:
        if re.search(pattern, article_title or ""):
            return code
    if article_text and len(article_text) < 200:
        for code, pattern in SKIP_TEXT_PATTERNS:
            if re.search(pattern, article_text):
                return code
    return None


# ============================================================
# Supabase 클라이언트
# ============================================================
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


# ============================================================
# 입력 모드별 article 로드
# ============================================================
def load_articles_from_json(set_id: str) -> List[Dict[str, Any]]:
    path = ROOT / "docs" / "extraction" / f"SET_{set_id.split('-')[1]}_articles.json"
    if not path.exists():
        raise FileNotFoundError(f"{path} 없음")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)["articles"]


def load_articles_from_ids(article_ids: List[str]) -> List[Dict[str, Any]]:
    """article_id 리스트로 직접 로드. law_master 조인."""
    if not article_ids:
        return []
    res = (
        supabase.table("law_article")
        .select("id, article_no, article_title, law_id, law_master(law_name)")
        .in_("id", article_ids)
        .execute()
    )
    return [
        {
            "id": r["id"],
            "law_name": r["law_master"]["law_name"] if r.get("law_master") else "",
            "article_no": r["article_no"],
            "article_title": r.get("article_title") or "",
        }
        for r in res.data
    ]


def load_articles_from_sql(sql_where: str, limit: int = 50) -> List[Dict[str, Any]]:
    """사각지대 채우기용. 의무 동사 보유 + drafts 0건 + WHERE 조건."""
    query = f"""
    SELECT a.id, m.law_name, a.article_no, a.article_title
    FROM law_article a
    JOIN law_master m ON m.id = a.law_id
    WHERE m.is_active = true
      AND a.article_text IS NOT NULL
      AND LENGTH(a.article_text) > 100
      AND (a.article_text LIKE '%하여야 한다%' OR a.article_text LIKE '%해야 한다%')
      AND a.id NOT IN (SELECT DISTINCT article_id FROM law_rule_drafts WHERE article_id IS NOT NULL)
      AND a.is_deleted_in_version = false
      AND ({sql_where})
    ORDER BY RANDOM()
    LIMIT {int(limit)};
    """
    res = supabase.rpc("execute_sql", {"query": query}).execute()
    return res.data or []


def fetch_article_text(article_id: str) -> Optional[Dict[str, Any]]:
    res = (
        supabase.table("law_article")
        .select("id,article_no,article_title,article_text,law_id")
        .eq("id", article_id)
        .execute()
    )
    return res.data[0] if res.data else None


# ============================================================
# 기존 데이터 idempotent 삭제
# ============================================================
def delete_existing(set_id: str, cycle: int) -> int:
    res = (
        supabase.table("law_rule_drafts")
        .delete()
        .eq("ai_flags->>extraction_set", set_id)
        .eq("ai_flags->>extraction_cycle", str(cycle))
        .execute()
    )
    return len(res.data) if res.data else 0


# ============================================================
# LLM 호출
# ============================================================
total_cost_usd = 0.0


def call_llm(law_name: str, article_no: int, article_title: str, article_text: str) -> Tuple[Dict[str, Any], float]:
    global total_cost_usd
    if total_cost_usd >= COST_LIMIT_USD:
        raise RuntimeError(f"비용 한도 초과: ${total_cost_usd:.2f} >= ${COST_LIMIT_USD}")

    user_msg = USER_PROMPT_TEMPLATE.format(
        law_name=law_name, article_no=article_no, article_title=article_title or "", article_text=article_text
    )
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS_PER_CALL,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )
    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\n", "", text)
        text = re.sub(r"\n```$", "", text)

    cost = (
        response.usage.input_tokens / 1_000_000 * INPUT_PRICE_PER_MTOK
        + response.usage.output_tokens / 1_000_000 * OUTPUT_PRICE_PER_MTOK
    )
    total_cost_usd += cost
    return json.loads(text), cost


# ============================================================
# INSERT (draft / placeholder)
# ============================================================
def build_flags(set_id: str, cycle: int, self_check: Dict[str, Any], skip_code: Optional[str] = None,
                placeholder_type: Optional[str] = None) -> Dict[str, Any]:
    flags = {
        "extraction_set": set_id,
        "extraction_cycle": cycle,
        "prompt_version": "v3.0.1",
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "from_pipeline": "v3_iterative_v3",
        "broken": False,
        "self_check": self_check,
    }
    # medium 자동 needs_review (검증 단계로 회부)
    if self_check.get("confidence_in_completeness") == "medium":
        flags["needs_review"] = True
        flags["review_reason"] = "self_check_medium"
    if skip_code:
        flags["skip_code"] = skip_code
    if placeholder_type:
        flags["placeholder_type"] = placeholder_type
    return flags


def insert_drafts(article_id: str, law_name: str, article_no: int, article_text: str,
                  obligations: List[Dict[str, Any]], self_check: Dict[str, Any],
                  set_id: str, cycle: int) -> int:
    if not obligations:
        return 0
    flags = build_flags(set_id, cycle, self_check)
    rows = []
    for ob in obligations:
        rows.append({
            "law_name": law_name,
            "law_article": f"제{article_no}조",
            "article_id": article_id,
            "article_text": article_text,
            "obligation_summary": ob["obligation_summary"],
            "appointment_target": ob["appointment_target"],
            "obligation_type": ob["obligation_type"],
            "sector": ob["sector"],
            "condition_code": ob.get("condition_code"),
            "condition_operator": ob.get("condition_operator"),
            "condition_value": ob.get("condition_value"),
            "ai_reasoning": ob["ai_reasoning"],
            "ai_confidence": ob["ai_confidence"],
            "ai_flags": flags,
            "status": "draft",
            "diagnosis_stage": 1,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })
    res = supabase.table("law_rule_drafts").insert(rows).execute()
    return len(res.data) if res.data else 0


def insert_placeholder(article_id: str, law_name: str, article_no: int, article_text: str,
                       skip_code: str, set_id: str, cycle: int) -> int:
    """PLACEHOLDER_001: SKIP article도 1건 적재 (drafts 0건 사각지대 회피)."""
    skip_reasons = {
        "SKIP_001": "정의 조항", "SKIP_002": "벌칙 조항", "SKIP_003": "부칙",
        "SKIP_004": "재검토", "SKIP_005": "권한 위임", "SKIP_006": "목적",
        "SKIP_007": "적용범위", "SKIP_009": "수수료/행정비용",
        "SKIP_010": "벌칙·과태료 징수절차", "SKIP_011": "조문 전체 준용",
    }
    reason = skip_reasons.get(skip_code, skip_code)
    self_check = {
        "reasoning": f"{skip_code} {reason} - placeholder 1건 적재 (drafts 0건 회피)",
        "para_count": 0, "verb_count": 0, "clause_count": 0,
        "coverage_ratio": 0, "extracted_count": 1,
        "skipped_paragraphs": [f"{skip_code} ({reason})"],
        "confidence_in_completeness": "medium",
    }
    flags = build_flags(set_id, cycle, self_check, skip_code=skip_code,
                       placeholder_type="article_full_skip")
    row = {
        "law_name": law_name,
        "law_article": f"제{article_no}조",
        "article_id": article_id,
        "article_text": article_text,
        "obligation_summary": f"본 article은 {reason}이므로 의무 추출 없음. 검토·재검증용 placeholder.",
        "appointment_target": f"({reason} - target 미정)",
        "obligation_type": "ACTION",
        "sector": "INDUSTRIAL",
        "ai_reasoning": f"{skip_code} 사전 매칭. PLACEHOLDER_001 정책에 따라 1건 적재.",
        "ai_confidence": 60,
        "ai_flags": flags,
        "status": "placeholder",
        "diagnosis_stage": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    res = supabase.table("law_rule_drafts").insert([row]).execute()
    return len(res.data) if res.data else 0


# ============================================================
# 메인
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="TAI 법령엔진 추출 v3 (수집)")
    parser.add_argument("--set", dest="set_id", required=True, help="extraction_set (예: SET-003)")
    parser.add_argument("--cycle", type=int, default=1, help="extraction_cycle")
    parser.add_argument("--input", choices=["json", "ids", "sql"], required=True)
    parser.add_argument("--article-ids", help="--input ids 시 콤마 구분 article_id 리스트")
    parser.add_argument("--sql-where", help="--input sql 시 추가 WHERE 조건 (이미 의무 동사·중복 필터 적용)")
    parser.add_argument("--limit", type=int, default=50, help="--input sql 시 LIMIT")
    parser.add_argument("--no-delete", action="store_true", help="기존 데이터 삭제 건너뜀 (append 모드)")
    args = parser.parse_args()

    print(f"=== {args.set_id} cycle={args.cycle} 추출 시작 ===")
    print(f"[INFO] model={MODEL} cost_limit=${COST_LIMIT_USD}")

    # 입력 모드
    if args.input == "json":
        articles = load_articles_from_json(args.set_id)
    elif args.input == "ids":
        if not args.article_ids:
            print("[ERROR] --article-ids 필요", file=sys.stderr)
            sys.exit(1)
        articles = load_articles_from_ids([s.strip() for s in args.article_ids.split(",")])
    else:  # sql
        if not args.sql_where:
            print("[ERROR] --sql-where 필요", file=sys.stderr)
            sys.exit(1)
        articles = load_articles_from_sql(args.sql_where, args.limit)

    print(f"[INFO] 대상 article {len(articles)}건")

    if not args.no_delete:
        deleted = delete_existing(args.set_id, args.cycle)
        print(f"[INFO] 기존 {deleted}건 삭제 (idempotent)")

    inserted_drafts = 0
    inserted_placeholders = 0
    failed = 0

    for i, art in enumerate(articles, 1):
        article_id = art["id"]
        law_name = art.get("law_name", "")
        article_no = art["article_no"]
        article_title = art.get("article_title") or ""

        full = fetch_article_text(article_id)
        if not full:
            print(f"[{i}/{len(articles)}] {law_name} 제{article_no}조 - article 없음, skip")
            failed += 1
            continue
        article_text = full["article_text"]

        # 사전 SKIP -> placeholder
        skip_code = pre_check_skip(article_title, article_text)
        if skip_code:
            n = insert_placeholder(article_id, law_name, article_no, article_text,
                                   skip_code, args.set_id, args.cycle)
            inserted_placeholders += n
            print(f"[{i}/{len(articles)}] {law_name} 제{article_no}조 - placeholder ({skip_code})")
            continue

        # LLM 호출
        try:
            result, cost = call_llm(law_name, article_no, article_title, article_text)
            obligations = result.get("obligations", [])
            self_check = result.get("self_check", {})

            if not obligations:
                # LLM이 0개 반환 시에도 placeholder (사각지대 회피)
                placeholder_self = {
                    **self_check,
                    "reasoning": (self_check.get("reasoning", "") +
                                  " | LLM 0건 반환 -> PLACEHOLDER_001 적재"),
                    "extracted_count": 1,
                    "confidence_in_completeness": "medium",
                }
                row = {
                    "law_name": law_name,
                    "law_article": f"제{article_no}조",
                    "article_id": article_id,
                    "article_text": article_text,
                    "obligation_summary": "LLM이 0건 반환. 검토 필요 - placeholder 적재.",
                    "appointment_target": "(미정 - LLM 0건)",
                    "obligation_type": "ACTION",
                    "sector": "INDUSTRIAL",
                    "ai_reasoning": "LLM 0건 반환. PLACEHOLDER_001 정책으로 1건 적재 (drafts 0건 회피).",
                    "ai_confidence": 50,
                    "ai_flags": build_flags(args.set_id, args.cycle, placeholder_self,
                                           placeholder_type="llm_zero_output"),
                    "status": "placeholder",
                    "diagnosis_stage": 1,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
                supabase.table("law_rule_drafts").insert([row]).execute()
                inserted_placeholders += 1
                print(f"[{i}/{len(articles)}] {law_name} 제{article_no}조 - LLM 0건 -> placeholder (${cost:.4f})")
            else:
                n = insert_drafts(article_id, law_name, article_no, article_text,
                                  obligations, self_check, args.set_id, args.cycle)
                inserted_drafts += n
                review = " [needs_review]" if self_check.get("confidence_in_completeness") == "medium" else ""
                print(f"[{i}/{len(articles)}] {law_name} 제{article_no}조 - {n}건 INSERT (${cost:.4f}){review}")
        except Exception as e:
            print(f"[{i}/{len(articles)}] {law_name} 제{article_no}조 - ERROR {e}", file=sys.stderr)
            failed += 1

        time.sleep(0.5)

    print(f"\n=== {args.set_id} cycle={args.cycle} 추출 완료 ===")
    print(f"[RESULT] drafts INSERT:       {inserted_drafts}")
    print(f"[RESULT] placeholders INSERT: {inserted_placeholders}")
    print(f"[RESULT] failed:              {failed}")
    print(f"[RESULT] 총 비용:             ${total_cost_usd:.2f}")
    print(f"\n다음 단계: python validate_drafts.py --set {args.set_id} --cycle {args.cycle}")


if __name__ == "__main__":
    main()
