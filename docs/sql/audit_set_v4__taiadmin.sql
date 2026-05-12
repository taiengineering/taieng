-- SET-XXX cycle Y 검증 v4 (의미 검증 룰 추가)
-- 변경: v3 → v4
--   - 23번 신설: E-1 — skipped_paragraphs SKIP_XXX 코드 미부여 detect
--   - 24번 신설: L-1 — reasoning이 article에 없는 항(⑤+) 참조하는 환각 detect
--   - 25번 신설: L-2 — article에 SKIP 키워드(위임/준용) 있으나 reasoning 미언급
--   - 26번 신설: B-1 엄격 — obligation_summary 전체 substring 부재 (분류 지표용, PASS/FAIL 아님)
--
-- v3 baseline (SET-001 cycle 1, 39 drafts):
--   01~14, 18, 20: 모두 0 (PASS처럼 보임)
--   19: 1
-- v4 신규 결과 (사람 검증과 비교):
--   23: 8 (skip 보유 article 전체 = 100% E-1 위반) — 사람 검증 일치 ✓
--   24: 1 (분양 시령 7조의2) — 사람 검증 일치 ✓
--   25: 1 (건축사법 38조의8 준용) — 사람 검증 일치 ✓
--   26: 34 (87%, 분류 지표용 — B-1~B-4 통합 카운트)

WITH set_drafts AS (
  SELECT * FROM law_rule_drafts
  WHERE ai_flags->>'extraction_set' = 'SET-001'
    AND (ai_flags->>'extraction_cycle')::int = 1
)
SELECT '01_drafts 추출 수' AS check_id, COUNT(*)::text AS value FROM set_drafts

UNION ALL SELECT '02_appointment_target NULL', COUNT(*)::text
FROM set_drafts WHERE appointment_target IS NULL OR TRIM(appointment_target)=''

UNION ALL SELECT '03_obligation_type 누락 또는 8종 외', COUNT(*)::text
FROM set_drafts WHERE obligation_type IS NULL OR obligation_type NOT IN
  ('ACTION','INSTALL','REPORT','INSPECT','EDUCATION','RECORD','APPOINT','POSSESS')

UNION ALL SELECT '04_obligation_summary 30자 미만', COUNT(*)::text
FROM set_drafts WHERE LENGTH(obligation_summary) < 30

UNION ALL SELECT '05_obligation_summary 150자 초과', COUNT(*)::text
FROM set_drafts WHERE LENGTH(obligation_summary) > 150

UNION ALL SELECT '06_조건키워드 있는데 condition_code NULL', COUNT(*)::text
FROM set_drafts
WHERE ai_reasoning ~ '(이상|이하|초과|미만|이내|별표)' AND condition_code IS NULL

UNION ALL SELECT '07_ai_confidence 70 미만', COUNT(*)::text
FROM set_drafts WHERE ai_confidence < 70

UNION ALL SELECT '08_sector NULL or 8종 외', COUNT(*)::text
FROM set_drafts
WHERE sector IS NULL OR sector NOT IN
  ('BUILDING','INDUSTRIAL','CONSTRUCTION','CHEMICAL','GAS','ELECTRIC','FIRE','ENV')

UNION ALL SELECT '09_article_id NULL', COUNT(*)::text
FROM set_drafts WHERE article_id IS NULL

UNION ALL SELECT '10_article_id orphan', COUNT(*)::text
FROM set_drafts d
WHERE d.article_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM law_article a WHERE a.id = d.article_id)

UNION ALL SELECT '11_law_name 불일치', COUNT(*)::text
FROM set_drafts d
JOIN law_article a ON a.id = d.article_id
JOIN law_master m ON m.id = a.law_id
WHERE d.law_name <> m.law_name

UNION ALL SELECT '12_obligation_summary 첫명사구 article_text 없음(환각, normalize)', COUNT(*)::text
FROM (
  SELECT
    d.id,
    REPLACE(REPLACE(d.obligation_summary, 'ㆍ', '·'), '・', '·') AS norm_summary,
    REPLACE(REPLACE(a.article_text, 'ㆍ', '·'), '・', '·') AS norm_text
  FROM set_drafts d
  JOIN law_article a ON a.id = d.article_id
) t
WHERE LENGTH(norm_summary) >= 5
  AND norm_text NOT LIKE '%' || REGEXP_REPLACE(SPLIT_PART(norm_summary, ' ', 1), '[^가-힣·]', '', 'g') || '%'
  AND norm_text NOT LIKE '%' || REGEXP_REPLACE(SPLIT_PART(norm_summary, ' ', 2), '[^가-힣·]', '', 'g') || '%'
  AND norm_text NOT LIKE '%' || REGEXP_REPLACE(SPLIT_PART(norm_summary, ' ', 3), '[^가-힣·]', '', 'g') || '%'

UNION ALL SELECT '13_condition_value 숫자 article_text 없음(환각)', COUNT(*)::text
FROM set_drafts d
JOIN law_article a ON a.id = d.article_id
WHERE d.condition_value IS NOT NULL
  AND REGEXP_REPLACE(d.condition_value, '[^0-9]', '', 'g') <> ''
  AND a.article_text NOT LIKE '%' || REGEXP_REPLACE(d.condition_value, '[^0-9]', '', 'g') || '%'

UNION ALL SELECT '14_같은article 안 obligation_summary 중복', COUNT(*)::text
FROM (
  SELECT article_id, obligation_summary, COUNT(*) c
  FROM set_drafts WHERE article_id IS NOT NULL
  GROUP BY article_id, obligation_summary HAVING COUNT(*)>1
) t

UNION ALL SELECT '18_self_check 누락', COUNT(DISTINCT article_id)::text
FROM set_drafts WHERE ai_flags->'self_check' IS NULL

UNION ALL SELECT '19_보정ratio < 0.5 (skipped 차감)', COUNT(DISTINCT article_id)::text
FROM set_drafts
WHERE (
  (ai_flags->'self_check'->>'extracted_count')::float /
  GREATEST(
    (ai_flags->'self_check'->>'verb_count')::float -
      jsonb_array_length(ai_flags->'self_check'->'skipped_paragraphs')::float,
    1
  )
) < 0.5

UNION ALL SELECT '20_LLM 자가보고 confidence_in_completeness=low', COUNT(DISTINCT article_id)::text
FROM set_drafts WHERE ai_flags->'self_check'->>'confidence_in_completeness' = 'low'

-- ==========================================
-- v4 신규: 의미 검증 룰
-- ==========================================

UNION ALL SELECT '23_E1_skipped_paragraphs SKIP_XXX 코드 미부여', COUNT(DISTINCT article_id)::text
FROM set_drafts
WHERE jsonb_typeof(ai_flags->'self_check'->'skipped_paragraphs') = 'array'
  AND jsonb_array_length(ai_flags->'self_check'->'skipped_paragraphs') > 0
  AND NOT EXISTS (
    SELECT 1 FROM jsonb_array_elements_text(ai_flags->'self_check'->'skipped_paragraphs') AS s(skip_text)
    WHERE s.skip_text LIKE 'SKIP_%'
  )

UNION ALL SELECT '24_L1_reasoning에 article에 없는 항 참조(환각)', COUNT(DISTINCT d.article_id)::text
FROM set_drafts d
JOIN law_article a ON a.id = d.article_id
WHERE d.ai_flags->'self_check'->>'reasoning' IS NOT NULL
  AND (
    (d.ai_flags->'self_check'->>'reasoning' LIKE '%⑤%' AND a.article_text NOT LIKE '%⑤%')
    OR (d.ai_flags->'self_check'->>'reasoning' LIKE '%⑥%' AND a.article_text NOT LIKE '%⑥%')
    OR (d.ai_flags->'self_check'->>'reasoning' LIKE '%⑦%' AND a.article_text NOT LIKE '%⑦%')
    OR (d.ai_flags->'self_check'->>'reasoning' LIKE '%⑧%' AND a.article_text NOT LIKE '%⑧%')
    OR (d.ai_flags->'self_check'->>'reasoning' LIKE '%⑨%' AND a.article_text NOT LIKE '%⑨%')
  )

UNION ALL SELECT '25_L2_article SKIP 키워드 있으나 reasoning 미언급', COUNT(DISTINCT d.article_id)::text
FROM set_drafts d
JOIN law_article a ON a.id = d.article_id
WHERE d.ai_flags->'self_check'->>'reasoning' IS NOT NULL
  AND (
    (a.article_text LIKE '%위임%' AND d.ai_flags->'self_check'->>'reasoning' NOT LIKE '%위임%')
    OR (a.article_text LIKE '%준용%' AND d.ai_flags->'self_check'->>'reasoning' NOT LIKE '%준용%')
  )

-- 26번: 분류 지표용 (PASS/FAIL 아님). B-1~B-4 통합 카운트.
-- 이 값이 0에 수렴하려면 추출 룰이 article_text를 더 그대로 보존해야 함.
-- 현재 SET-001 cycle 1: 34/39 (87%) — 추출 결과 대부분이 article_text 변형
UNION ALL SELECT '26_B1엄격_obligation_summary 전체 substring 부재(분류지표)', COUNT(*)::text
FROM (
  SELECT
    REPLACE(REPLACE(d.obligation_summary, 'ㆍ', '·'), '・', '·') AS norm_summary,
    REPLACE(REPLACE(a.article_text, 'ㆍ', '·'), '・', '·') AS norm_text
  FROM set_drafts d
  JOIN law_article a ON a.id = d.article_id
) t
WHERE norm_text NOT LIKE '%' || norm_summary || '%'

ORDER BY check_id;
