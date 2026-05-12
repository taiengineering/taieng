#!/usr/bin/env python3
"""
TAI 법령엔진 반복 추출 스크립트 v2 (Railway 환경변수 사용)

실행 방법:
  $ railway link  # tai-api 프로젝트 링크 (한 번만)
  $ railway run python extract_iterative_v2.py SET-002 1

필수 환경변수 (Railway에서 자동 주입):
  - ANTHROPIC_API_KEY
  - SUPABASE_URL
  - SUPABASE_SERVICE_ROLE_KEY (또는 SUPABASE_SERVICE_KEY)

v1 관련 조치:
  - .env 파일 읽지 않음 (Railway 채널만 신뢰)
  - SUPABASE_SERVICE_ROLE_KEY 폴백 추가 (해결됨)
  - PROMPT v3.0.1 + 21개 룰 inline (외부 파일 의존 제거)
  - audit_set_v3 자동 실행 (가운뎃점 normalize)

작성: 2026-05-04 (S13 세션)
"""

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
# 1. 환경변수 (Railway에서 주입)
# ============================================================
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = (
    os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    or os.environ.get("SUPABASE_SERVICE_KEY")
    or os.environ.get("SUPABASE_KEY")
)

if not ANTHROPIC_API_KEY:
    print("[ERROR] ANTHROPIC_API_KEY 없음. `railway run python extract_iterative_v2.py`로 실행.", file=sys.stderr)
    sys.exit(1)
if not SUPABASE_URL or not SUPABASE_KEY:
    print("[ERROR] SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY 없음.", file=sys.stderr)
    sys.exit(1)

# ============================================================
# 2. 설정
# ============================================================
SET_ID = sys.argv[1] if len(sys.argv) > 1 else "SET-002"
CYCLE = int(sys.argv[2]) if len(sys.argv) > 2 else 1
MODEL = os.environ.get("EXTRACT_MODEL", "claude-opus-4-5-20251015")
MAX_TOKENS_PER_CALL = 4096
COST_LIMIT_USD = float(os.environ.get("COST_LIMIT_USD", "10.0"))

# Opus 4.5 가격 (입력 $15/MTok, 출력 $75/MTok)
INPUT_PRICE_PER_MTOK = 15.0
OUTPUT_PRICE_PER_MTOK = 75.0

ROOT = Path(__file__).resolve().parent.parent.parent  # tai-admin/
ARTICLES_JSON_PATH = ROOT / "docs" / "extraction" / f"SET_{SET_ID.split('-')[1]}_articles.json"

# ============================================================
# 3. PROMPT v3.0.1 (inline)
# ============================================================
SYSTEM_PROMPT = """\
당신은 TAI 법령엔진 의무 추출기입니다. 대한민국 산업안전 관련 법령 조문에서 **현장 적용 의무**만 정확히 추출합니다.

## 핵심 원칙
1. **환각 금지**: article_text에 명시적으로 있는 내용만 추출. 원문 용어 사용.
2. **다중 의무 분해**: 한 article에 여러 항/동사/주체가 있으면 분해.
   - 주체 다르면 분해 (예: "사업주와 근로자는" → 사업주 1개, 근로자 1개)
   - 동사 다르면 분해 (예: "개최하고 작성·보존" → 개최 1개, 작성·보존 1개)
3. **self_check 필수**: 애 article마다 self_check JSON 출력.

## SKIP 패턴 (추출 안 함)
- SKIP_001 정의 조항 ("...이란 ...을 말한다")
- SKIP_002 벌칙 조항 ("...한 자는 ...에 처한다")
- SKIP_003 부칙 (시행일, 경과조치, 특례)
- SKIP_004 재검토 ("...에 대해 N년마다 ... 타당성을 검토")
- SKIP_005 권한 위임 ("...은 대통령령으로 정한다")
- SKIP_006 목적
- SKIP_007 적용범위
- SKIP_009 수수료/행정비용 (신규, S13)
- SKIP_010 벌칙·과태료 징수절차 (신규, S13)
- SKIP_011 준용 조항 (신규, S13 발견 예정): "...에 관하여는 제XX조를 준용한다"

## 권한·재량 (의무 아님)
- "할 수 있다" → 권한, 추출 안 함
- "필요하다고 인정하면" → 재량, 추출 안 함
- "...하여야 한다" / "...되어야 한다" / "...해서는 아니 된다" → 의무 (추출)

## 출력 스키마 (JSON)
```json
{
  "obligations": [
    {
      "obligation_summary": "...",  // 30~150자
      "appointment_target": "사업주",  // 의무의 주체 (NULL 금지)
      "obligation_type": "ACTION",  // 8종: ACTION/INSTALL/REPORT/INSPECT/EDUCATION/RECORD/APPOINT/POSSESS
      "sector": "INDUSTRIAL",  // 8종: BUILDING/INDUSTRIAL/CONSTRUCTION/CHEMICAL/GAS/ELECTRIC/FIRE/ENV
      "condition_code": "area",  // 조건 코드 (NULL 가능)
      "condition_operator": "gte",  // gt/gte/lt/lte/eq
      "condition_value": "5000",  // 값 (NULL 가능)
      "ai_reasoning": "article_text 인용: '...'",
      "ai_confidence": 90  // 70~100
    }
  ],
  "self_check": {
    "para_count": 7,
    "verb_count": 6,
    "clause_count": 0,
    "extracted_count": 8,
    "coverage_ratio": 1.14,
    "skipped_paragraphs": ["⑧항 (위임)"],
    "confidence_in_completeness": "high",  // high/medium/low
    "reasoning": "..."
  }
}
```

SKIP 패턴에 걸리는 article은 obligations: [] 반환, self_check의 reasoning에 SKIP 원인 명시.
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

JSON만 출력하세요 (코드 펜스 사용 X, 설명 텍스트 없이 순수 JSON).
"""

# ============================================================
# 4. SKIP 패턴 사전 체크 (LLM 안 부르고 넘김)
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
    # SKIP_011 (준용): article_text가 "...에 관하여는 제XX조를 준용한다"로 구성
    # 단 다른 의무 없을 때만 skip (단일 문장)
    ("SKIP_011", r"관하여는 제\d+조.*준용한다"),
]


def pre_check_skip(article_title: str, article_text: str) -> Optional[str]:
    """SKIP 패턴 사전 체크. 매칭되면 SKIP 코드 반환, 아니면 None."""
    for code, pattern in SKIP_TITLE_PATTERNS:
        if re.search(pattern, article_title or ""):
            return code
    # SKIP_011 준용: article_text가 짧고 준용 패턴만 있을 때
    if article_text and len(article_text) < 200:
        for code, pattern in SKIP_TEXT_PATTERNS:
            if re.search(pattern, article_text):
                return code
    return None


# ============================================================
# 5. Supabase 클라이언트
# ============================================================
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def load_articles() -> List[Dict[str, Any]]:
    if not ARTICLES_JSON_PATH.exists():
        raise FileNotFoundError(f"{ARTICLES_JSON_PATH} 없음")
    with open(ARTICLES_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["articles"]


def fetch_article_text(article_id: str) -> Optional[Dict[str, Any]]:
    res = supabase.table("law_article").select("id,article_no,article_title,article_text,article_type,law_id").eq("id", article_id).execute()
    if not res.data:
        return None
    return res.data[0]


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
# 6. LLM 호출
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
    # 코드 펜스 제거
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
# 7. INSERT
# ============================================================
def insert_obligations(
    article_id: str, law_name: str, article_no: int, article_text: str,
    obligations: List[Dict[str, Any]], self_check: Dict[str, Any], skip_code: Optional[str] = None
) -> int:
    if not obligations:
        return 0

    base_flags = {
        "extraction_set": SET_ID,
        "extraction_cycle": CYCLE,
        "prompt_version": "v3.0.1",
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "from_pipeline": "v3_iterative_v2",
        "broken": False,
        "self_check": self_check,
    }
    if skip_code:
        base_flags["skip_code"] = skip_code

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
            "penalty_summary": None,
            "ai_reasoning": ob["ai_reasoning"],
            "ai_confidence": ob["ai_confidence"],
            "ai_flags": base_flags,
            "status": "PENDING",
            "diagnosis_stage": 1,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })
    res = supabase.table("law_rule_drafts").insert(rows).execute()
    return len(res.data) if res.data else 0


# ============================================================
# 8. 메인 흐름
# ============================================================
def main():
    print(f"=== {SET_ID} cycle={CYCLE} 시작 ===")
    print(f"[INFO] model={MODEL} cost_limit=${COST_LIMIT_USD}")

    articles = load_articles()
    print(f"[INFO] 대상 article {len(articles)}건")

    deleted = delete_existing(SET_ID, CYCLE)
    print(f"[INFO] 기존 {deleted}건 삭제 (idempotent)")

    total_inserted = 0
    skipped_count = 0
    for i, art in enumerate(articles, 1):
        article_id = art["id"]
        law_name = art["law_name"]
        article_no = art["article_no"]
        article_title = art.get("article_title") or ""

        # 본문 가져오기
        full = fetch_article_text(article_id)
        if not full:
            print(f"[{i}/{len(articles)}] {law_name} 제{article_no}조 — article 없음, skip")
            continue
        article_text = full["article_text"]

        # 사전 SKIP 체크
        skip_code = pre_check_skip(article_title, article_text)
        if skip_code:
            print(f"[{i}/{len(articles)}] {law_name} 제{article_no}조 — 사전 SKIP ({skip_code})")
            skipped_count += 1
            continue

        # LLM 호출
        try:
            result, cost = call_llm(law_name, article_no, article_title, article_text)
            obligations = result.get("obligations", [])
            self_check = result.get("self_check", {})
            inserted = insert_obligations(article_id, law_name, article_no, article_text, obligations, self_check)
            print(f"[{i}/{len(articles)}] {law_name} 제{article_no}조 — {inserted}건 INSERT (비용 ${cost:.4f})")
            total_inserted += inserted
            if inserted == 0:
                skipped_count += 1
        except Exception as e:
            print(f"[{i}/{len(articles)}] {law_name} 제{article_no}조 — ❌ {e}", file=sys.stderr)

        time.sleep(0.5)  # 소프트 레이트리밋

    print(f"\n=== {SET_ID} cycle={CYCLE} 완료 ===")
    print(f"[RESULT] 총 INSERT: {total_inserted} drafts")
    print(f"[RESULT] skipped article: {skipped_count}")
    print(f"[RESULT] 총 비용: ${total_cost_usd:.2f}")
    print(f"\n다음 단계: docs/extraction/sql/audit_set_v3.sql 실행 후 결과 검토")


if __name__ == "__main__":
    main()
