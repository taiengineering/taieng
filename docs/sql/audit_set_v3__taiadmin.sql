-- SET-XXX cycle Y 검증 v3 (가운뎃점 normalize + coverage 보정)
-- 변경: v2 → v3
--   - 12번: obligation_summary와 article_text 둘 다 가운뎃점 normalize (ㆍ → ·)
--   - 19번: coverage_ratio 분모에서 skipped_paragraphs 수를 차감한 보정 ratio 사용

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

-- 12번 v3: 가운뎃점 normalize 후 환각 검증
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

-- 19번 v3: skipped_paragraphs 수 차감한 보정 ratio < 0.5
UNION ALL SELECT '19_보정ratio < 0.5 (skipped 차감)', COUNT(DISTINCT article_id)::text
FROM set_drafts 
WHERE (
  -- 보정 ratio = extracted_count / GREATEST(verb_count - skipped_paragraphs_count, 1)
  (ai_flags->'self_check'->>'extracted_count')::float / 
  GREATEST(
    (ai_flags->'self_check'->>'verb_count')::float - 
      jsonb_array_length(ai_flags->'self_check'->'skipped_paragraphs')::float,
    1
  )
) < 0.5

UNION ALL SELECT '20_LLM 자가보고 confidence_in_completeness=low', COUNT(DISTINCT article_id)::text
FROM set_drafts WHERE ai_flags->'self_check'->>'confidence_in_completeness' = 'low'

UNION ALL SELECT '22_항(①②③) 있는데 추출 0건', COUNT(*)::text
FROM (
  SELECT a.id
  FROM law_article a
  JOIN (SELECT DISTINCT article_id FROM (
    SELECT (article_id::text)::uuid AS article_id FROM jsonb_array_elements(
      (SELECT (info->'articles')::jsonb FROM (SELECT '{"articles":[]}'::jsonb AS info) x
      UNION ALL SELECT '[]'::jsonb)
    )
  ) z) sa ON true
  WHERE a.article_text ~ '[①②③④⑤]'
    AND NOT EXISTS (
      SELECT 1 FROM set_drafts d 
      WHERE d.article_id = a.id
    )
    AND a.id IN (
      '81d80ab7-8714-4754-9c0f-53787bcf256b'::uuid,'07d46999-f5a3-4716-ba11-113e772980cf'::uuid,
      '3d71a14d-1b26-4f3e-a9ef-5c38f27441c1'::uuid,'505edbb4-f922-4b22-9949-dbbf51685f6c'::uuid,
      '39228368-a06a-42ea-9688-ad58a89371c9'::uuid,'2f415d7c-250a-4aff-9b92-7b36dee58b29'::uuid,
      'c9ddbad7-84fb-4e8b-b1bd-aa7d73dfec3b'::uuid,'07ca4b7f-91ea-42b3-97b9-a5a37c329af7'::uuid,
      '09a87e33-cc26-4d98-9d60-f3e88a0f2409'::uuid,'f2e1b712-b886-4ef7-926e-c987b1a1c3ee'::uuid,
      'fa76cc25-0ff7-4dbb-a835-1b61e26e7a05'::uuid,'b8cb10c9-400b-45b4-ad01-fd0c10ef29a8'::uuid,
      '12b19b7c-7303-40d9-8219-592c1c2af11f'::uuid,'719f4968-404b-43b4-ac3a-1990fdb8dbd5'::uuid,
      '71ca1d8b-5d7d-4a29-8b36-63ba6b83950f'::uuid,'3993e053-5c0a-419b-9ecd-6ddb1f4f4d88'::uuid,
      '0265514c-7181-4167-bc74-01e3664e284e'::uuid,'25aea07e-6628-4826-a377-c8fa55f1f922'::uuid,
      'c27c8673-85d9-4da2-9f5b-23498375973e'::uuid,'8141041d-d6f5-4b67-8f1c-d5ac16d73a3b'::uuid
    )
) t

ORDER BY check_id;
