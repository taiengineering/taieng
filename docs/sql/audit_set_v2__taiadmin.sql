-- SET-XXX cycle Y 정순+역순 검증 v2 (self_check 교차 추가)
-- 사용법: 'SET-001' 부분만 변경

WITH set_drafts AS (
  SELECT * FROM law_rule_drafts
  WHERE ai_flags->>'extraction_set' = 'SET-001'
    AND (ai_flags->>'extraction_cycle')::int = 1
),
set_articles AS (
  SELECT DISTINCT a.id AS article_id, a.article_text, a.article_title
  FROM law_article a
  JOIN set_drafts d ON d.article_id = a.id
)
-- ===========================================
-- A. 정순 검증 (article → drafts)
-- ===========================================
SELECT '01_drafts 추출 수' AS check_id, COUNT(*)::text AS value
FROM set_drafts

UNION ALL SELECT '02_appointment_target NULL', COUNT(*)::text
FROM set_drafts WHERE appointment_target IS NULL OR TRIM(appointment_target)=''

UNION ALL SELECT '03_obligation_type 누락 또는 8종 외', COUNT(*)::text
FROM set_drafts 
WHERE obligation_type IS NULL 
   OR obligation_type NOT IN ('ACTION','INSTALL','REPORT','INSPECT','EDUCATION','RECORD','APPOINT','POSSESS')

UNION ALL SELECT '04_obligation_summary 30자 미만', COUNT(*)::text
FROM set_drafts WHERE LENGTH(obligation_summary) < 30

UNION ALL SELECT '05_obligation_summary 150자 초과', COUNT(*)::text
FROM set_drafts WHERE LENGTH(obligation_summary) > 150

UNION ALL SELECT '06_조건키워드 있는데 condition_code NULL', COUNT(*)::text
FROM set_drafts 
WHERE ai_reasoning ~ '(이상|이하|초과|미만|이내|별표)' 
  AND condition_code IS NULL

UNION ALL SELECT '07_ai_confidence 70 미만', COUNT(*)::text
FROM set_drafts WHERE ai_confidence < 70

UNION ALL SELECT '08_sector NULL or 8종 외', COUNT(*)::text
FROM set_drafts 
WHERE sector IS NULL 
   OR sector NOT IN ('BUILDING','INDUSTRIAL','CONSTRUCTION','CHEMICAL','GAS','ELECTRIC','FIRE','ENV')

-- ===========================================
-- B. 역순 검증 (drafts → article)
-- ===========================================
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

UNION ALL SELECT '12_obligation_summary 첫명사구 article_text 없음(환각)', COUNT(*)::text
FROM set_drafts d
JOIN law_article a ON a.id = d.article_id
WHERE LENGTH(d.obligation_summary) >= 5
  AND a.article_text NOT LIKE '%' || REGEXP_REPLACE(SPLIT_PART(d.obligation_summary, ' ', 1), '[^가-힣]', '', 'g') || '%'
  AND a.article_text NOT LIKE '%' || REGEXP_REPLACE(SPLIT_PART(d.obligation_summary, ' ', 2), '[^가-힣]', '', 'g') || '%'

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

-- ===========================================
-- C. self_check 검증 (다중 의무 누락 방지)
-- ===========================================
UNION ALL SELECT '18_self_check 누락', COUNT(DISTINCT article_id)::text
FROM set_drafts WHERE ai_flags->'self_check' IS NULL

UNION ALL SELECT '19_LLM 자가 보고 coverage_ratio < 0.5', COUNT(DISTINCT article_id)::text
FROM set_drafts 
WHERE (ai_flags->'self_check'->>'coverage_ratio')::float < 0.5

UNION ALL SELECT '20_LLM 자가 confidence_in_completeness=low', COUNT(DISTINCT article_id)::text
FROM set_drafts 
WHERE ai_flags->'self_check'->>'confidence_in_completeness' = 'low'

UNION ALL SELECT '21_LLM 자가보고 verb_count vs SQL 실측 차이 > 2', COUNT(*)::text
FROM (
  SELECT 
    sd.article_id,
    MAX((sd.ai_flags->'self_check'->>'verb_count')::int) AS llm_verb,
    MAX((LENGTH(sa.article_text) - LENGTH(REGEXP_REPLACE(sa.article_text, '해야 한다|하여야 한다', '', 'g'))) / 5) AS sql_verb
  FROM set_drafts sd
  JOIN set_articles sa ON sa.article_id = sd.article_id
  GROUP BY sd.article_id
  HAVING ABS(
    MAX((sd.ai_flags->'self_check'->>'verb_count')::int) - 
    MAX((LENGTH(sa.article_text) - LENGTH(REGEXP_REPLACE(sa.article_text, '해야 한다|하여야 한다', '', 'g'))) / 5)
  ) > 2
) t

UNION ALL SELECT '22_항(①②③) 있는데 추출 0건', COUNT(*)::text
FROM (
  SELECT a.id
  FROM law_article a
  WHERE a.id IN (
    SELECT DISTINCT article_id FROM set_drafts WHERE article_id IS NOT NULL
    UNION
    -- SET-001 article 20건 중 추출 0건
    SELECT article_id FROM (VALUES
      ('81d80ab7-8714-4754-9c0f-53787bcf256b'::uuid),
      ('07d46999-f5a3-4716-ba11-113e772980cf'::uuid),
      ('3d71a14d-1b26-4f3e-a9ef-5c38f27441c1'::uuid),
      ('505edbb4-f922-4b22-9949-dbbf51685f6c'::uuid),
      ('39228368-a06a-42ea-9688-ad58a89371c9'::uuid)
    ) AS s(article_id)
  )
  AND a.article_text ~ '[①②③④⑤]'
  AND NOT EXISTS (SELECT 1 FROM set_drafts d WHERE d.article_id = a.id)
) t

ORDER BY check_id;

-- ===========================================
-- PASS 조건
-- ===========================================
-- 02~22 (01 제외) 모두 0건 → SET PASS
-- 1건이라도 있으면 → ERROR_PATTERNS.md에 추가 + PROMPT 강화 + cycle 재실행
