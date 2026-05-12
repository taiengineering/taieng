-- SET-XXX cycle Y 검증 v5 (검증기 보강 — 룰 자체 약점 정정 반영)
-- 변경: v4 → v5
--   - 30번 신설: F-1 — set 전체 의무 본문 완전 동일 중복 (PASS/FAIL)
--   - 31번 폐기: F-2 — article+target+type GROUP BY는 분해 정당 케이스 false positive 100%
--                     (SET-001 9/9 모두 분해 정당이라 검증 가치 없음. 본문 유사도 측정은 SQL 영역 외)
--   - 32번 신설: G-1 — article 의무 동사 빈도 vs draft 수 비교 (임계 2.0)
--   - 33번 신설: B-2 분류지표 — "다음 각 호의 어느 하나" 패턴 article 수
--   - 34번 신설: B-4 분류지표 — 의무 어미 변형 (해야↔하여야) drafts 수
--   - 35번 신설: E-2 — para_count vs skipped 모순 케이스 (self_check 의존)
--
-- 분류지표 vs PASS/FAIL 구분:
--   PASS/FAIL: 30(F-1), 32(G-1), 35(E-2). 0이어야 정상.
--   분류지표: 26(B-1), 33(B-2), 34(B-4). 값 자체보다 SET 간 변동이 신호.
--
-- SET-001 cycle 1 결과 (2026-05-05):
--   30: 0 (본문 완전 동일 중복 없음)
--   32: 0 (의무 동사 누락 의심 없음, 임계 2.0 기준)
--   33: 4 articles (각 호 패턴 보유)
--   34: 3 drafts (어미 변형)
--   35: 0 (self_check 모순 없음)

WITH set_drafts AS (
  SELECT * FROM law_rule_drafts
  WHERE ai_flags->>'extraction_set' = 'SET-001'
    AND (ai_flags->>'extraction_cycle')::int = 1
)
-- v3 형식 검증 (그대로 보존)
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
-- v4 의미 검증 (그대로 보존)
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

UNION ALL SELECT '26_B1엄격_obligation_summary 전체 substring 부재(분류지표)', COUNT(*)::text
FROM (
  SELECT
    REPLACE(REPLACE(d.obligation_summary, 'ㆍ', '·'), '・', '·') AS norm_summary,
    REPLACE(REPLACE(a.article_text, 'ㆍ', '·'), '・', '·') AS norm_text
  FROM set_drafts d
  JOIN law_article a ON a.id = d.article_id
) t
WHERE norm_text NOT LIKE '%' || norm_summary || '%'

-- ==========================================
-- v5 신규: 검증기 보강 (룰 자체 정정 반영)
-- ==========================================

-- 30: F-1 본문 완전 동일 중복 (PASS/FAIL)
UNION ALL SELECT '30_F1_drafts 본문 완전 중복 (set 내)', COALESCE(SUM(c - 1)::text, '0')
FROM (
  SELECT obligation_summary, COUNT(*) c
  FROM set_drafts
  GROUP BY obligation_summary
  HAVING COUNT(*) > 1
) t

-- 31: F-2 폐기 — article+target+type GROUP BY는 분해 정당 케이스 false positive 100%
-- 본문 유사도 측정 필요 (trigram·embedding) — SQL 영역 외, 별도 verify_drafts.py로 이관

-- 32: G-1 의무 동사 누락 의심 (임계 2.0)
UNION ALL SELECT '32_G1_의무 동사 빈도 > drafts*2.0 (누락 의심)', COUNT(*)::text
FROM (
  SELECT
    a.id,
    (LENGTH(a.article_text) - LENGTH(REPLACE(a.article_text, '하여야 한다', '')))
      / NULLIF(LENGTH('하여야 한다'), 0)
    + (LENGTH(a.article_text) - LENGTH(REPLACE(a.article_text, '해야 한다', '')))
      / NULLIF(LENGTH('해야 한다'), 0) AS verb_count,
    (SELECT COUNT(*) FROM set_drafts d WHERE d.article_id = a.id) AS draft_count
  FROM law_article a
  WHERE a.id IN (SELECT DISTINCT article_id FROM set_drafts)
) t
WHERE verb_count > draft_count * 2.0

-- 33: B-2 분류지표 (PASS/FAIL 아님)
UNION ALL SELECT '33_B2_각 호 압축 통합 article 수 (분류지표)', COUNT(DISTINCT a.id)::text
FROM law_article a
JOIN set_drafts d ON d.article_id = a.id
WHERE a.article_text LIKE '%다음 각 호의 어느 하나%'

-- 34: B-4 분류지표 (PASS/FAIL 아님)
UNION ALL SELECT '34_B4_의무 어미 변형 drafts 수 (분류지표)', COUNT(*)::text
FROM set_drafts d
JOIN law_article a ON a.id = d.article_id
WHERE (
  (a.article_text LIKE '%해야 한다%' AND a.article_text NOT LIKE '%하여야 한다%'
   AND d.obligation_summary LIKE '%하여야 한다%')
  OR
  (a.article_text LIKE '%하여야 한다%' AND a.article_text NOT LIKE '%해야 한다%'
   AND d.obligation_summary LIKE '%해야 한다%')
)

-- 35: E-2 paragraph 처리 모순 (self_check 의존)
UNION ALL SELECT '35_E2_para_count < skipped_paragraphs (모순)', COUNT(DISTINCT article_id)::text
FROM set_drafts
WHERE (ai_flags->'self_check'->>'para_count') IS NOT NULL
  AND (ai_flags->'self_check'->>'para_count')::int > 0
  AND (
    (ai_flags->'self_check'->>'para_count')::int
    < jsonb_array_length(ai_flags->'self_check'->'skipped_paragraphs')
  )

ORDER BY check_id;
