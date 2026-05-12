-- ============================================================
-- classify_articles_v1.py 검증용 SQL 모음
-- 사람 검증 불가 → 룰 자체 검증 (5층 자동 검증 체계)
--
-- 사용법:
--   psql 또는 Supabase SQL editor에서 각 query 실행
--   대표가 직접 점검할 수 있는 SQL 5단계
-- ============================================================

-- ────────────────────────────────────────────────────────────
-- [Layer 0] 분류 진행 상황 — 100% 커버 확인
-- ────────────────────────────────────────────────────────────
SELECT
  '== Layer 0: 분류 커버리지 ==' AS check_name;

-- A. NFTC/KDS leaf articles (대상 약 3,560)
WITH leaf_articles AS (
  SELECT a.id, a.content_types, a.primary_content_type, a.classification_confidence
  FROM law_article a JOIN law_master m ON m.id = a.law_id
  WHERE (m.law_name LIKE '%NFTC%' OR m.law_name LIKE '%KDS%' OR m.law_name LIKE '%설계기준%')
    AND m.law_name != '건축물의 에너지절약설계기준'
    AND NOT EXISTS (SELECT 1 FROM law_article c WHERE c.parent_article_id = a.id)
)
SELECT
  'NFTC/KDS leaf' AS scope,
  COUNT(*) AS total,
  COUNT(*) FILTER (WHERE primary_content_type IS NOT NULL) AS classified,
  COUNT(*) FILTER (WHERE primary_content_type IS NULL) AS null_pending,
  COUNT(*) FILTER (WHERE classified_by_rules @> ARRAY['_NULL_NEEDS_REVIEW']) AS needs_review,
  ROUND(100.0 * COUNT(*) FILTER (WHERE primary_content_type IS NOT NULL) / NULLIF(COUNT(*), 0), 1) AS pct_classified
FROM leaf_articles;

-- B. law_article_part (전체)
SELECT
  'law_article_part 전체' AS scope,
  COUNT(*) AS total,
  COUNT(*) FILTER (WHERE primary_content_type IS NOT NULL) AS classified,
  COUNT(*) FILTER (WHERE primary_content_type IS NULL) AS null_pending,
  COUNT(*) FILTER (WHERE classified_by_rules @> ARRAY['_NULL_NEEDS_REVIEW']) AS needs_review
FROM law_article_part;


-- ────────────────────────────────────────────────────────────
-- [Layer 1] type 분포 — 비정상 비중 검출
-- ────────────────────────────────────────────────────────────
SELECT
  '== Layer 1: type 분포 ==' AS check_name;

-- NFTC/KDS leaf의 primary_content_type 분포
WITH leaf_articles AS (
  SELECT a.* FROM law_article a JOIN law_master m ON m.id = a.law_id
  WHERE (m.law_name LIKE '%NFTC%' OR m.law_name LIKE '%KDS%' OR m.law_name LIKE '%설계기준%')
    AND m.law_name != '건축물의 에너지절약설계기준'
    AND NOT EXISTS (SELECT 1 FROM law_article c WHERE c.parent_article_id = a.id)
)
SELECT
  primary_content_type,
  classification_confidence,
  COUNT(*) AS cnt,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM leaf_articles
GROUP BY 1, 2
ORDER BY cnt DESC;


-- ────────────────────────────────────────────────────────────
-- [Layer 2] 다중 분류 분포 — 다중 매칭 패턴 확인
-- ────────────────────────────────────────────────────────────
SELECT
  '== Layer 2: 다중 분류 패턴 ==' AS check_name;

WITH leaf_articles AS (
  SELECT a.* FROM law_article a JOIN law_master m ON m.id = a.law_id
  WHERE (m.law_name LIKE '%NFTC%' OR m.law_name LIKE '%KDS%' OR m.law_name LIKE '%설계기준%')
    AND m.law_name != '건축물의 에너지절약설계기준'
    AND NOT EXISTS (SELECT 1 FROM law_article c WHERE c.parent_article_id = a.id)
)
SELECT
  array_length(content_types, 1) AS num_types,
  content_types,
  COUNT(*) AS cnt
FROM leaf_articles
WHERE content_types IS NOT NULL
GROUP BY 1, 2
ORDER BY cnt DESC
LIMIT 20;


-- ────────────────────────────────────────────────────────────
-- [Layer 3] 부모-자식 일관성 — 자식들이 같은 부모면 type 일관해야
-- ────────────────────────────────────────────────────────────
SELECT
  '== Layer 3: 부모-자식 일관성 (NFTC/KDS) ==' AS check_name;

-- 같은 부모 아래 자식들의 type이 다양한 케이스 (의심 — 최대 5개 조사)
WITH parent_child_types AS (
  SELECT
    parent.id AS parent_id,
    parent.article_internal_key AS parent_key,
    parent.primary_content_type AS parent_type,
    array_agg(DISTINCT child.primary_content_type) FILTER (WHERE child.primary_content_type IS NOT NULL) AS children_types,
    COUNT(child.id) AS children_count
  FROM law_article parent
  JOIN law_article child ON child.parent_article_id = parent.id
  WHERE parent.article_internal_key LIKE 'NFTC%' OR parent.article_internal_key LIKE 'KDS%'
  GROUP BY 1, 2, 3
  HAVING array_length(array_agg(DISTINCT child.primary_content_type) FILTER (WHERE child.primary_content_type IS NOT NULL), 1) > 2
)
SELECT parent_key, parent_type, children_types, children_count
FROM parent_child_types
ORDER BY children_count DESC
LIMIT 20;


-- ────────────────────────────────────────────────────────────
-- [Layer 4] 룰별 매칭 통계 — 어떤 룰이 가장 많이 사용됐나
-- ────────────────────────────────────────────────────────────
SELECT
  '== Layer 4: 룰별 매칭 통계 ==' AS check_name;

WITH leaf_articles AS (
  SELECT a.* FROM law_article a JOIN law_master m ON m.id = a.law_id
  WHERE (m.law_name LIKE '%NFTC%' OR m.law_name LIKE '%KDS%' OR m.law_name LIKE '%설계기준%')
    AND m.law_name != '건축물의 에너지절약설계기준'
    AND NOT EXISTS (SELECT 1 FROM law_article c WHERE c.parent_article_id = a.id)
),
unnested AS (
  SELECT unnest(classified_by_rules) AS rule_id
  FROM leaf_articles
  WHERE classified_by_rules IS NOT NULL
)
SELECT rule_id, COUNT(*) AS hits
FROM unnested
GROUP BY rule_id
ORDER BY hits DESC;


-- ────────────────────────────────────────────────────────────
-- [Layer 5] NULL_NEEDS_REVIEW 목록 — 사람 검토 또는 룰 추가 보강 대상
-- ────────────────────────────────────────────────────────────
SELECT
  '== Layer 5: NULL leaf list (검토용) ==' AS check_name;

-- NFTC/KDS NULL leaf
WITH leaf_articles AS (
  SELECT a.* FROM law_article a JOIN law_master m ON m.id = a.law_id
  WHERE (m.law_name LIKE '%NFTC%' OR m.law_name LIKE '%KDS%' OR m.law_name LIKE '%설계기준%')
    AND m.law_name != '건축물의 에너지절약설계기준'
    AND NOT EXISTS (SELECT 1 FROM law_article c WHERE c.parent_article_id = a.id)
)
SELECT
  article_internal_key,
  article_type,
  LEFT(article_text, 200) AS text_preview
FROM leaf_articles
WHERE classified_by_rules @> ARRAY['_NULL_NEEDS_REVIEW']
ORDER BY article_internal_key
LIMIT 50;


-- ────────────────────────────────────────────────────────────
-- [정확성 sanity check] sample 50건 본문 + 분류 결과 (사람 spot-check)
-- ────────────────────────────────────────────────────────────
SELECT
  '== Spot-check sample 50건 ==' AS check_name;

WITH leaf_articles AS (
  SELECT a.* FROM law_article a JOIN law_master m ON m.id = a.law_id
  WHERE (m.law_name LIKE '%NFTC%' OR m.law_name LIKE '%KDS%' OR m.law_name LIKE '%설계기준%')
    AND m.law_name != '건축물의 에너지절약설계기준'
    AND NOT EXISTS (SELECT 1 FROM law_article c WHERE c.parent_article_id = a.id)
)
SELECT
  article_internal_key,
  primary_content_type,
  content_types,
  classification_confidence,
  LEFT(article_text, 150) AS text
FROM leaf_articles
WHERE primary_content_type IS NOT NULL
ORDER BY RANDOM()
LIMIT 50;


-- ────────────────────────────────────────────────────────────
-- [통계 검증] 키워드-type 상관관계
-- 특정 키워드가 매칭됐을 때 어떤 type으로 분류됐는지
-- 95% 이상이면 룰 정확, 그 미만이면 룰 누수
-- ────────────────────────────────────────────────────────────
SELECT
  '== 키워드-type 상관관계 ==' AS check_name;

WITH leaf_articles AS (
  SELECT a.id, a.article_text, a.primary_content_type
  FROM law_article a JOIN law_master m ON m.id = a.law_id
  WHERE (m.law_name LIKE '%NFTC%' OR m.law_name LIKE '%KDS%' OR m.law_name LIKE '%설계기준%')
    AND m.law_name != '건축물의 에너지절약설계기준'
    AND NOT EXISTS (SELECT 1 FROM law_article c WHERE c.parent_article_id = a.id)
)
SELECT
  '하여야 한다' AS keyword,
  primary_content_type,
  COUNT(*) AS cnt
FROM leaf_articles
WHERE article_text ~ '하여야 한다'
GROUP BY 1, 2
ORDER BY cnt DESC

UNION ALL

SELECT
  '다만,',
  primary_content_type,
  COUNT(*)
FROM leaf_articles
WHERE article_text ~ '(?:^|\n)\s*다만,'
GROUP BY 1, 2

UNION ALL

SELECT
  '할 수 있다',
  primary_content_type,
  COUNT(*)
FROM leaf_articles
WHERE article_text ~ '할 수 있다'
GROUP BY 1, 2

ORDER BY 1, cnt DESC;
