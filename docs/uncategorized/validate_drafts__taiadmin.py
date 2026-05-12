#!/usr/bin/env python3
"""
TAI 법령엔진 검증 스크립트 (검증 단계)

3 정적 검증기 실행 + 이상치 ai_flags['needs_review']=true 설정.
LLM 호출 없음 (자기 충족 회피).

검증기 (rule_patterns.yaml v1.2):
1. audit_set_v5 의미 검증 (E-1, L-1, L-2, B-1, F-1, G-1, B-2, B-4, E-2)
2. baseline_metrics 분포 (M01~M22, 추출기 metric만 SET 간 비교 의미)
3. ACTION 편향 진단 (obligation_type_dictionary v0.1 사전 매칭)

review vs 분류 지표 구분:
- review (needs_review=true 설정): E-1, L-1, L-2, F-1, G-1, medium
- 분류 지표 (보고만): B-1, B-2, B-4, 다중 target, ACTION 편향

실행:
  $ railway run python validate_drafts.py --set SET-003 --cycle 1
  $ railway run python validate_drafts.py --set SET-003 --cycle 1 --report-only

작성: 2026-05-05 (S14 세션)
"""

import argparse
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

try:
    from supabase import Client, create_client
except ImportError:
    print("[ERROR] pip install supabase", file=sys.stderr)
    sys.exit(1)


# ============================================================
# 환경변수
# ============================================================
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


# ============================================================
# Helper: SQL 실행 (rpc execute_sql 또는 직접)
# ============================================================
def run_sql(sql: str) -> List[Dict[str, Any]]:
    """raw SQL 실행. supabase-py에서는 rpc 또는 PostgREST를 통해야 함.
    이 스크립트는 별도 rpc 함수 'execute_sql' 가정. 미존재 시 SET 인자 직접 binding으로 우회."""
    res = supabase.rpc("execute_sql", {"query": sql}).execute()
    return res.data or []


# ============================================================
# 검증 룰 SQL (set/cycle 변수 binding)
# ============================================================
def audit_v5_sql(set_id: str, cycle: int) -> str:
    return f"""
    WITH set_drafts AS (
      SELECT * FROM law_rule_drafts
      WHERE ai_flags->>'extraction_set' = '{set_id}'
        AND (ai_flags->>'extraction_cycle')::int = {cycle}
        AND status != 'placeholder'
    )
    SELECT 'A_01_drafts' AS check_id, COUNT(*)::text AS value FROM set_drafts
    UNION ALL SELECT 'A_02_articles', COUNT(DISTINCT article_id)::text FROM set_drafts
    UNION ALL SELECT 'A_07_confidence_70_under', COUNT(*)::text FROM set_drafts WHERE ai_confidence < 70
    UNION ALL SELECT 'A_14_dup_in_article', COUNT(*)::text
    FROM (SELECT article_id, obligation_summary, COUNT(*) c FROM set_drafts
      WHERE article_id IS NOT NULL GROUP BY article_id, obligation_summary HAVING COUNT(*)>1) t
    UNION ALL SELECT 'A_20b_completeness_medium', COUNT(DISTINCT article_id)::text
    FROM set_drafts WHERE ai_flags->'self_check'->>'confidence_in_completeness' = 'medium'
    UNION ALL SELECT 'A_23_E1_skipped_no_code', COUNT(DISTINCT article_id)::text
    FROM set_drafts
    WHERE jsonb_typeof(ai_flags->'self_check'->'skipped_paragraphs') = 'array'
      AND jsonb_array_length(ai_flags->'self_check'->'skipped_paragraphs') > 0
      AND NOT EXISTS (
        SELECT 1 FROM jsonb_array_elements_text(ai_flags->'self_check'->'skipped_paragraphs') AS s(skip_text)
        WHERE s.skip_text LIKE 'SKIP_%'
      )
    UNION ALL SELECT 'A_24_L1_reasoning_hallucination', COUNT(DISTINCT d.article_id)::text
    FROM set_drafts d JOIN law_article a ON a.id = d.article_id
    WHERE d.ai_flags->'self_check'->>'reasoning' IS NOT NULL
      AND ((d.ai_flags->'self_check'->>'reasoning' LIKE '%⑤%' AND a.article_text NOT LIKE '%⑤%')
        OR (d.ai_flags->'self_check'->>'reasoning' LIKE '%⑥%' AND a.article_text NOT LIKE '%⑥%')
        OR (d.ai_flags->'self_check'->>'reasoning' LIKE '%⑦%' AND a.article_text NOT LIKE '%⑦%'))
    UNION ALL SELECT 'A_25_L2_skip_keyword_unmentioned', COUNT(DISTINCT d.article_id)::text
    FROM set_drafts d JOIN law_article a ON a.id = d.article_id
    WHERE d.ai_flags->'self_check'->>'reasoning' IS NOT NULL
      AND ((a.article_text LIKE '%위임%' AND d.ai_flags->'self_check'->>'reasoning' NOT LIKE '%위임%')
        OR (a.article_text LIKE '%준용%' AND d.ai_flags->'self_check'->>'reasoning' NOT LIKE '%준용%'))
    UNION ALL SELECT 'A_26_B1_substring_absent_pct', COUNT(*)::text
    FROM (SELECT REPLACE(REPLACE(d.obligation_summary, 'ㆍ', '·'), '・', '·') AS norm_summary,
      REPLACE(REPLACE(a.article_text, 'ㆍ', '·'), '・', '·') AS norm_text
      FROM set_drafts d JOIN law_article a ON a.id = d.article_id) t
    WHERE norm_text NOT LIKE '%' || norm_summary || '%'
    UNION ALL SELECT 'A_30_F1_exact_duplicate', COALESCE(SUM(c - 1)::text, '0')
    FROM (SELECT obligation_summary, COUNT(*) c FROM set_drafts
      GROUP BY obligation_summary HAVING COUNT(*) > 1) t
    UNION ALL SELECT 'A_32_G1_verb_count_higher_than_drafts', COUNT(*)::text
    FROM (
      SELECT a.id,
        (LENGTH(a.article_text) - LENGTH(REPLACE(a.article_text, '하여야 한다', '')))
          / NULLIF(LENGTH('하여야 한다'), 0)
        + (LENGTH(a.article_text) - LENGTH(REPLACE(a.article_text, '해야 한다', '')))
          / NULLIF(LENGTH('해야 한다'), 0)
        + (LENGTH(a.article_text) - LENGTH(REPLACE(a.article_text, '아니 된다', '')))
          / NULLIF(LENGTH('아니 된다'), 0) AS verb_count,
        (SELECT COUNT(*) FROM set_drafts d WHERE d.article_id = a.id) AS draft_count,
        (SELECT MAX(jsonb_array_length(ai_flags->'self_check'->'skipped_paragraphs'))
         FROM set_drafts d WHERE d.article_id = a.id) AS skip_count
      FROM law_article a WHERE a.id IN (SELECT DISTINCT article_id FROM set_drafts)
    ) t WHERE verb_count - COALESCE(skip_count, 0) > draft_count * 1.0
    UNION ALL SELECT 'A_33_B2_classifier_each_clause', COUNT(DISTINCT a.id)::text
    FROM law_article a JOIN set_drafts d ON d.article_id = a.id
    WHERE a.article_text LIKE '%다음 각 호의 어느 하나%'
    UNION ALL SELECT 'A_34_B4_classifier_ending_variation', COUNT(*)::text
    FROM set_drafts d JOIN law_article a ON a.id = d.article_id
    WHERE ((a.article_text LIKE '%해야 한다%' AND a.article_text NOT LIKE '%하여야 한다%' AND d.obligation_summary LIKE '%하여야 한다%')
      OR (a.article_text LIKE '%하여야 한다%' AND a.article_text NOT LIKE '%해야 한다%' AND d.obligation_summary LIKE '%해야 한다%'))
    UNION ALL SELECT 'A_36_classifier_multi_target', COUNT(*)::text
    FROM set_drafts WHERE appointment_target ~ '(또는|및)'
    ORDER BY check_id;
    """


def baseline_metrics_sql(set_id: str, cycle: int) -> str:
    return f"""
    WITH set_drafts AS (
      SELECT * FROM law_rule_drafts
      WHERE ai_flags->>'extraction_set' = '{set_id}'
        AND (ai_flags->>'extraction_cycle')::int = {cycle}
        AND status != 'placeholder'
    )
    SELECT * FROM (VALUES
      ('B_target_distinct', (SELECT COUNT(DISTINCT appointment_target)::text FROM set_drafts)),
      ('B_type_distinct', (SELECT COUNT(DISTINCT obligation_type)::text FROM set_drafts)),
      ('B_type_top', (SELECT obligation_type || ' ' || ROUND((cnt::float / total * 100)::numeric, 1) || '%'
         FROM (SELECT obligation_type, COUNT(*) cnt, SUM(COUNT(*)) OVER () total FROM set_drafts GROUP BY obligation_type) t
         ORDER BY cnt DESC LIMIT 1)),
      ('B_summary_len_avg_stddev',
        (SELECT ROUND(AVG(LENGTH(obligation_summary))::numeric, 1)::text || ' / ' ||
                ROUND(STDDEV(LENGTH(obligation_summary))::numeric, 1)::text FROM set_drafts)),
      ('B_confidence_avg_stddev',
        (SELECT ROUND(AVG(ai_confidence)::numeric, 1)::text || ' / ' ||
                ROUND(STDDEV(ai_confidence)::numeric, 1)::text FROM set_drafts)),
      ('B_skip_pct_articles',
        (SELECT ROUND((COUNT(*) FILTER (WHERE jsonb_array_length(ai_flags->'self_check'->'skipped_paragraphs') > 0)::float / GREATEST(COUNT(*), 1) * 100)::numeric, 1)::text
         FROM (SELECT DISTINCT article_id, ai_flags FROM set_drafts) sub))
    ) AS metrics(metric, value);
    """


def action_diagnosis_sql(set_id: str, cycle: int) -> str:
    """ACTION drafts 대상 사전 매칭 (obligation_type_dictionary v0.1)."""
    return f"""
    WITH set_drafts AS (
      SELECT * FROM law_rule_drafts
      WHERE ai_flags->>'extraction_set' = '{set_id}'
        AND (ai_flags->>'extraction_cycle')::int = {cycle}
        AND obligation_type = 'ACTION'
        AND status != 'placeholder'
    )
    SELECT
      CASE
        WHEN obligation_summary ~ '(보고|통지|통보|제출|공개|게시)(하|해|함)' THEN 'REPORT_missing'
        WHEN obligation_summary ~ '(확인|검사|평가|점검|조사|진단|심사)(하|해|함)' THEN 'INSPECT_missing'
        WHEN obligation_summary ~ '(기록|보존|작성|기명날인|보관)(하|해|함)' THEN 'RECORD_missing'
        WHEN obligation_summary ~ '(설치|시공|구축)(하|해|함)' THEN 'INSTALL_missing'
        WHEN (obligation_summary ~ '(비치|소지)(하|해)' OR obligation_summary ~ '갖추어 (두는|두어)') THEN 'POSSESS_missing'
        WHEN obligation_summary ~ '(교육|훈련)(하|해|시)' THEN 'EDUCATION_missing'
        WHEN obligation_summary ~ '(선임|임명|지정)(하|해|함)' THEN 'APPOINT_missing'
        WHEN obligation_summary ~ '(고시|공시|발표|공포)(하|해|함)' THEN 'PUBLISH_candidate (8종 한계)'
        WHEN obligation_summary ~ '(통제|제한|규제)(하|해|함)' THEN 'REGULATE_candidate (8종 한계)'
        WHEN obligation_summary ~ '(위탁|위임|이관|대행)(하|해|함|하도록)' THEN 'DELEGATE_candidate (8종 한계)'
        ELSE 'ACTION_legitimate'
      END AS judgment,
      COUNT(*) AS cnt,
      ROUND((COUNT(*)::float / SUM(COUNT(*)) OVER () * 100)::numeric, 1) AS pct
    FROM set_drafts
    GROUP BY judgment ORDER BY cnt DESC;
    """


# ============================================================
# 이상치 → needs_review flag UPDATE
# ============================================================
def flag_needs_review_sql(set_id: str, cycle: int) -> str:
    """review 대상 룰: E-1, L-1, L-2, F-1, G-1.
    분류 지표 (B-1, B-2, B-4, 다중 target, ACTION 편향)는 review 안 함.

    medium은 추출 단계에서 이미 flag됨 (extract_iterative_v3.py).
    여기서는 검증기가 새로 발견한 이상치만 추가로 flag.
    """
    return f"""
    WITH set_drafts AS (
      SELECT id, article_id, obligation_summary, ai_flags
      FROM law_rule_drafts
      WHERE ai_flags->>'extraction_set' = '{set_id}'
        AND (ai_flags->>'extraction_cycle')::int = {cycle}
        AND status != 'placeholder'
    ),
    -- E-1 위반 article의 모든 drafts
    e1_articles AS (
      SELECT DISTINCT article_id FROM set_drafts
      WHERE jsonb_typeof(ai_flags->'self_check'->'skipped_paragraphs') = 'array'
        AND jsonb_array_length(ai_flags->'self_check'->'skipped_paragraphs') > 0
        AND NOT EXISTS (
          SELECT 1 FROM jsonb_array_elements_text(ai_flags->'self_check'->'skipped_paragraphs') AS s(skip_text)
          WHERE s.skip_text LIKE 'SKIP_%'
        )
    ),
    -- L-1 위반 article
    l1_articles AS (
      SELECT DISTINCT d.article_id FROM set_drafts d
      JOIN law_article a ON a.id = d.article_id
      WHERE d.ai_flags->'self_check'->>'reasoning' IS NOT NULL
        AND ((d.ai_flags->'self_check'->>'reasoning' LIKE '%⑤%' AND a.article_text NOT LIKE '%⑤%')
          OR (d.ai_flags->'self_check'->>'reasoning' LIKE '%⑥%' AND a.article_text NOT LIKE '%⑥%')
          OR (d.ai_flags->'self_check'->>'reasoning' LIKE '%⑦%' AND a.article_text NOT LIKE '%⑦%'))
    ),
    -- L-2 위반 article
    l2_articles AS (
      SELECT DISTINCT d.article_id FROM set_drafts d
      JOIN law_article a ON a.id = d.article_id
      WHERE d.ai_flags->'self_check'->>'reasoning' IS NOT NULL
        AND ((a.article_text LIKE '%위임%' AND d.ai_flags->'self_check'->>'reasoning' NOT LIKE '%위임%')
          OR (a.article_text LIKE '%준용%' AND d.ai_flags->'self_check'->>'reasoning' NOT LIKE '%준용%'))
    ),
    -- F-1 본문 동일 중복 drafts
    f1_drafts AS (
      SELECT id FROM set_drafts
      WHERE obligation_summary IN (
        SELECT obligation_summary FROM set_drafts
        GROUP BY obligation_summary HAVING COUNT(*) > 1
      )
    ),
    -- G-1 누락 의심 article
    g1_articles AS (
      SELECT a.id FROM law_article a
      WHERE a.id IN (SELECT DISTINCT article_id FROM set_drafts)
        AND (
          (LENGTH(a.article_text) - LENGTH(REPLACE(a.article_text, '하여야 한다', '')))
            / NULLIF(LENGTH('하여야 한다'), 0)
          + (LENGTH(a.article_text) - LENGTH(REPLACE(a.article_text, '해야 한다', '')))
            / NULLIF(LENGTH('해야 한다'), 0)
          + (LENGTH(a.article_text) - LENGTH(REPLACE(a.article_text, '아니 된다', '')))
            / NULLIF(LENGTH('아니 된다'), 0)
          - COALESCE((SELECT MAX(jsonb_array_length(ai_flags->'self_check'->'skipped_paragraphs'))
                      FROM set_drafts d WHERE d.article_id = a.id), 0)
          > (SELECT COUNT(*) FROM set_drafts d WHERE d.article_id = a.id) * 1.0
        )
    ),
    review_target AS (
      SELECT id, 'E1_skip_no_code' AS reason FROM set_drafts WHERE article_id IN (SELECT article_id FROM e1_articles)
      UNION ALL
      SELECT id, 'L1_reasoning_hallucination' FROM set_drafts WHERE article_id IN (SELECT article_id FROM l1_articles)
      UNION ALL
      SELECT id, 'L2_skip_keyword_unmentioned' FROM set_drafts WHERE article_id IN (SELECT article_id FROM l2_articles)
      UNION ALL
      SELECT id, 'F1_exact_duplicate' FROM f1_drafts
      UNION ALL
      SELECT id, 'G1_recall_gap' FROM set_drafts WHERE article_id IN (SELECT id FROM g1_articles)
    ),
    aggregated AS (
      SELECT id, jsonb_agg(reason ORDER BY reason) AS reasons FROM review_target GROUP BY id
    )
    UPDATE law_rule_drafts d
    SET ai_flags = jsonb_set(
          jsonb_set(d.ai_flags, '{{needs_review}}', 'true'::jsonb),
          '{{review_reasons}}',
          a.reasons
        ),
        updated_at = NOW()
    FROM aggregated a
    WHERE d.id = a.id
    RETURNING d.id;
    """


# ============================================================
# 메인
# ============================================================
def print_section(title: str):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def main():
    parser = argparse.ArgumentParser(description="TAI 법령엔진 검증 (정적, LLM 호출 없음)")
    parser.add_argument("--set", dest="set_id", required=True)
    parser.add_argument("--cycle", type=int, default=1)
    parser.add_argument("--report-only", action="store_true",
                        help="needs_review flag UPDATE 없이 리포트만 출력")
    args = parser.parse_args()

    print(f"=== {args.set_id} cycle={args.cycle} 검증 시작 ===")
    print(f"[INFO] mode: {'report-only' if args.report_only else 'full (UPDATE flag)'}")

    # 1. audit_set_v5
    print_section("1. audit_set_v5 (의미 검증)")
    rows = run_sql(audit_v5_sql(args.set_id, args.cycle))
    review_signals = []
    classifier_signals = []
    for r in rows:
        check = r["check_id"]
        val = r["value"]
        is_review = check.startswith(("A_23", "A_24", "A_25", "A_30", "A_32", "A_20b"))
        is_classifier = "classifier" in check or check.startswith(("A_26", "A_36"))
        marker = "⭐" if is_review and val not in ("0", None) else "  "
        print(f"  {marker} {check}: {val}")
        if is_review and val not in ("0", None):
            review_signals.append(f"{check}={val}")
        if is_classifier:
            classifier_signals.append(f"{check}={val}")

    # 2. baseline_metrics
    print_section("2. baseline_metrics (분포 — SET 비교용)")
    for r in run_sql(baseline_metrics_sql(args.set_id, args.cycle)):
        print(f"     {r['metric']}: {r['value']}")

    # 3. ACTION 진단
    print_section("3. ACTION 편향 진단 (사전 v0.1 매칭)")
    for r in run_sql(action_diagnosis_sql(args.set_id, args.cycle)):
        marker = "⭐" if "_missing" in r["judgment"] else "  "
        print(f"  {marker} {r['judgment']}: {r['cnt']} ({r['pct']}%)")

    # 4. needs_review flag UPDATE
    if not args.report_only:
        print_section("4. needs_review flag UPDATE")
        updated = run_sql(flag_needs_review_sql(args.set_id, args.cycle))
        print(f"     UPDATE: {len(updated)} drafts -> needs_review=true")

    # 요약
    print_section("요약")
    print(f"  Review 신호 (정정 필요): {len(review_signals)}개 룰")
    for sig in review_signals:
        print(f"     - {sig}")
    print(f"  분류 지표 (보고만): {len(classifier_signals)}개")
    print(f"\n다음 단계: python correct_drafts.py --set {args.set_id} --cycle {args.cycle}")


if __name__ == "__main__":
    main()
