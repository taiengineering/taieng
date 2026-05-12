-- SET-001 선정 (재현 가능, random seed 고정)
-- 비즈니스 핵심 5 명시 + 다양성 무작위 15

-- ===========================================
-- Step 1: 비즈니스 핵심 5 (각 법령에서 article 1개)
-- ===========================================
WITH core_5 AS (
  SELECT m.id AS law_id, m.law_name, m.law_type_code,
         a.id AS article_id, a.article_no, a.article_title,
         ROW_NUMBER() OVER (PARTITION BY m.id ORDER BY md5(a.id::text || '001')) AS rn
  FROM law_master m
  JOIN law_article a ON a.law_id = m.id
  WHERE m.is_active = true
    AND a.article_type IN ('조문', '본칙', '조')
    AND a.article_text ~ '(해야 한다|하여야 한다|선임|신고|보고|교육|점검|기록|비치|설치하여야|갖추어야|준수하여야|지정하여야)'
    AND m.law_name IN (
      '산업안전보건법',
      '산업안전보건법 시행규칙',
      '산업안전보건기준에 관한 규칙',
      '위험물안전관리법',
      '건설기술 진흥법'
    )
),
-- ===========================================
-- Step 2: 다양성 무작위 15 (각 type별 분배)
-- ===========================================
diversity_pool AS (
  SELECT m.id AS law_id, m.law_name, m.law_type_code,
         a.id AS article_id, a.article_no, a.article_title,
         ROW_NUMBER() OVER (
           PARTITION BY m.law_type_code, m.id 
           ORDER BY md5(a.id::text || '001')
         ) AS art_rn,
         ROW_NUMBER() OVER (
           PARTITION BY m.law_type_code
           ORDER BY md5(m.id::text || '001')
         ) AS law_rn
  FROM law_master m
  JOIN law_article a ON a.law_id = m.id
  WHERE m.is_active = true
    AND a.article_type IN ('조문', '본칙', '조')
    AND a.article_text ~ '(해야 한다|하여야 한다|선임|신고|보고|교육|점검|기록|비치|설치하여야|갖추어야|준수하여야|지정하여야)'
    AND m.law_name NOT IN (
      '산업안전보건법', '산업안전보건법 시행규칙', '산업안전보건기준에 관한 규칙',
      '위험물안전관리법', '건설기술 진흥법'
    )
),
-- type별 분배: LAW 3 / DECREE 4 / RULE 4 / NOTICE 4 / STANDARD 3 / OTHER 1 = 19? 15로 조정
-- 비즈니스 핵심 5 + 다양성 15 = 20
-- 다양성: LAW 3 / DECREE 4 / RULE 3 / NOTICE 4 / STANDARD 1 = 15
type_quotas AS (
  SELECT * FROM (VALUES
    ('LAW', 3),
    ('ENFORCEMENT_DECREE', 4),
    ('ENFORCEMENT_RULE', 3),
    ('NOTICE', 4),
    ('STANDARD', 1)
  ) AS t(law_type_code, quota)
),
selected_diversity AS (
  SELECT d.law_id, d.law_name, d.law_type_code,
         d.article_id, d.article_no, d.article_title
  FROM diversity_pool d
  JOIN type_quotas q ON q.law_type_code = d.law_type_code
  WHERE d.law_rn <= q.quota   -- 각 type별 quota 만큼 법령 선정
    AND d.art_rn = 1          -- 각 법령에서 article 1개
)
-- ===========================================
-- 최종: 5 + 15 = 20
-- ===========================================
SELECT 'CORE' AS source, law_id, law_name, law_type_code, article_id, article_no, article_title
FROM core_5 WHERE rn = 1
UNION ALL
SELECT 'DIVERSITY', law_id, law_name, law_type_code, article_id, article_no, article_title
FROM selected_diversity
ORDER BY source, law_type_code, law_name;
