-- SET-XXX cycle Y 정순+역순 검증
-- 사용법: ai_flags->>'extraction_set' = 'SET-001' 부분만 변경

-- ===========================================
-- 정순 검증 (article → drafts)
-- ===========================================
WITH set_drafts AS (
  SELECT * FROM law_rule_drafts
  WHERE ai_flags->>'extraction_set' = 'SET-001'
    AND (ai_flags->>'extraction_cycle')::int = 1
)
SELECT '01_drafts 추출 수' AS check_id, COUNT(*)::text AS value
FROM set_drafts

UNION ALL SELECT '02_appointment_target NULL', COUNT(*)::text
FROM set_drafts WHERE appointment_target IS NULL OR TRIM(appointment_target)=''

UNION ALL SELECT '03_obligation_type NULL or 8종_외', COUNT(*)::text
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

UNION ALL SELECT '08_sector NULL', COUNT(*)::text
FROM set_drafts WHERE sector IS NULL OR sector NOT IN ('BUILDING','INDUSTRIAL','CONSTRUCTION','CHEMICAL','GAS','ELECTRIC','FIRE','ENV')

-- ===========================================
-- 역순 검증 (drafts → article)
-- ===========================================
UNION ALL SELECT '09_article_id NULL', COUNT(*)::text
FROM set_drafts WHERE article_id IS NULL

UNION ALL SELECT '10_article_id orphan (article 없음)', COUNT(*)::text
FROM set_drafts d
WHERE d.article_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM law_article a WHERE a.id = d.article_id)

UNION ALL SELECT '11_law_name 불일치 (drafts vs article의 master)', COUNT(*)::text
FROM set_drafts d
JOIN law_article a ON a.id = d.article_id
JOIN law_master m ON m.id = a.law_id
WHERE d.law_name <> m.law_name

UNION ALL SELECT '12_obligation_summary 첫명사구가 article_text에 없음(환각)', COUNT(*)::text
FROM set_drafts d
JOIN law_article a ON a.id = d.article_id
WHERE LENGTH(d.obligation_summary) >= 5
  AND a.article_text NOT LIKE '%' || REGEXP_REPLACE(SPLIT_PART(d.obligation_summary, ' ', 1), '[^가-힣]', '', 'g') || '%'
  AND a.article_text NOT LIKE '%' || REGEXP_REPLACE(SPLIT_PART(d.obligation_summary, ' ', 2), '[^가-힣]', '', 'g') || '%'

UNION ALL SELECT '13_condition_value 숫자가 article_text에 없음(환각)', COUNT(*)::text
FROM set_drafts d
JOIN law_article a ON a.id = d.article_id
WHERE d.condition_value IS NOT NULL
  AND REGEXP_REPLACE(d.condition_value, '[^0-9]', '', 'g') <> ''
  AND a.article_text NOT LIKE '%' || REGEXP_REPLACE(d.condition_value, '[^0-9]', '', 'g') || '%'

UNION ALL SELECT '14_같은article 안에서 obligation_summary 중복', COUNT(*)::text
FROM (
  SELECT article_id, obligation_summary, COUNT(*) c
  FROM set_drafts WHERE article_id IS NOT NULL
  GROUP BY article_id, obligation_summary HAVING COUNT(*)>1
) t

ORDER BY check_id;

-- ===========================================
-- PASS 조건
-- ===========================================
-- 02~14 모두 0건이면 SET PASS
-- 1건이라도 있으면 ERROR_PATTERNS.md에 추가 + PROMPT 강화 + cycle 재실행
