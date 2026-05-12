-- SET-XXX cycle Y baseline 분포 metric (추출기 독립 정량 지표)
-- ============================================================
-- 사용법: 아래 set_drafts CTE의 'SET-001'·cycle 값을 측정 대상으로 변경
--
-- 설계 원칙:
--   - 추출기와 독립된 통계·분포 검사
--   - SET·cycle·추출기 변경되어도 동일 SQL로 측정 가능
--   - cross-SET 비교용 baseline으로 활용
--   - audit_set_v4(자기 충족 위험)와 별도 트랙
--
-- SET-001 cycle 1 baseline 결과 (2026-05-05):
--   M01_drafts 총수: 39
--   M02_articles 총수: 14
--   M03_target distinct: 24
--   M04_target entropy (nat, max=ln(24)=3.178): 2.968 (93% 균등)
--   M05_target 최빈 비율%: 17.9
--   M06_type distinct (max=8): 6
--   M07_type entropy (nat, max=ln(6)=1.792): 1.295 (72%)
--   M08_type 최빈: ACTION 51.3%   ← 추출기 약점 신호 (구체 type 미활용)
--   M09~13_summary length: min 31 / max 122 / avg 62.8 / median 61 / stddev 24.0
--   M14~17_ai_confidence: min 85 / max 95 / avg 89.7 / stddev 2.0
--     ← stddev 2.0 너무 좁음 — metric 가치 낮음, 향후 제거 검토
--   M18_skip 보유 article: 8
--   M19_skip 비율%: 57.1
--   M20_article당 의무 분포: 1:2, 2:7, 3:1, 4:3, 8:1   ← 8은 outlier (산안법 24조)
--   M21~22_의무 평균/stddev: 2.79 / 1.81
--
-- 해석 가이드 (SET-002 비교 시):
--   - target entropy 변동 → 주체 다양성 안정성
--   - type 편향(M08) 변동 → ACTION 일반화 약점의 일관성
--   - summary length stddev 변동 → 추출 일관성
--   - skip 비율 — article 카테고리 의존, 카테고리별 baseline 따로 쌓아야

WITH set_drafts AS (
  SELECT * FROM law_rule_drafts
  WHERE ai_flags->>'extraction_set' = 'SET-001'    -- ← 측정 대상 변경
    AND (ai_flags->>'extraction_cycle')::int = 1   -- ← 측정 대상 변경
),
article_stats AS (
  SELECT
    article_id,
    COUNT(*) AS extracted_count,
    BOOL_OR(jsonb_array_length(ai_flags->'self_check'->'skipped_paragraphs') > 0) AS has_skip
  FROM set_drafts
  GROUP BY article_id
),
target_entropy AS (
  SELECT -SUM((cnt::float / total) * LN(cnt::float / total)) AS entropy
  FROM (
    SELECT appointment_target, COUNT(*) AS cnt, SUM(COUNT(*)) OVER () AS total
    FROM set_drafts
    GROUP BY appointment_target
  ) t
),
type_entropy AS (
  SELECT -SUM((cnt::float / total) * LN(cnt::float / total)) AS entropy
  FROM (
    SELECT obligation_type, COUNT(*) AS cnt, SUM(COUNT(*)) OVER () AS total
    FROM set_drafts
    GROUP BY obligation_type
  ) t
),
article_count_dist AS (
  SELECT extracted_count, COUNT(*) AS articles
  FROM article_stats
  GROUP BY extracted_count
)
SELECT * FROM (VALUES
  ('M01_drafts 총수', (SELECT COUNT(*)::text FROM set_drafts)),
  ('M02_articles 총수', (SELECT COUNT(DISTINCT article_id)::text FROM set_drafts)),
  ('M03_target distinct', (SELECT COUNT(DISTINCT appointment_target)::text FROM set_drafts)),
  ('M04_target entropy (nat, max=ln(distinct))', (SELECT ROUND(entropy::numeric, 3)::text FROM target_entropy)),
  ('M05_target 최빈 비율%', (SELECT ROUND((MAX(cnt)::float / SUM(cnt) * 100)::numeric, 1)::text FROM (SELECT appointment_target, COUNT(*) cnt FROM set_drafts GROUP BY appointment_target) t)),
  ('M06_type distinct (max=8)', (SELECT COUNT(DISTINCT obligation_type)::text FROM set_drafts)),
  ('M07_type entropy (nat)', (SELECT ROUND(entropy::numeric, 3)::text FROM type_entropy)),
  ('M08_type 최빈', (SELECT obligation_type || ' ' || ROUND((cnt::float / total * 100)::numeric, 1) || '%'
                    FROM (SELECT obligation_type, COUNT(*) cnt, SUM(COUNT(*)) OVER () total FROM set_drafts GROUP BY obligation_type) t
                    ORDER BY cnt DESC LIMIT 1)),
  ('M09_summary length min', (SELECT MIN(LENGTH(obligation_summary))::text FROM set_drafts)),
  ('M10_summary length max', (SELECT MAX(LENGTH(obligation_summary))::text FROM set_drafts)),
  ('M11_summary length avg', (SELECT ROUND(AVG(LENGTH(obligation_summary))::numeric, 1)::text FROM set_drafts)),
  ('M12_summary length stddev', (SELECT ROUND(STDDEV(LENGTH(obligation_summary))::numeric, 1)::text FROM set_drafts)),
  ('M13_summary length median', (SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY LENGTH(obligation_summary))::text FROM set_drafts)),
  ('M14_ai_confidence min', (SELECT MIN(ai_confidence)::text FROM set_drafts)),
  ('M15_ai_confidence max', (SELECT MAX(ai_confidence)::text FROM set_drafts)),
  ('M16_ai_confidence avg', (SELECT ROUND(AVG(ai_confidence)::numeric, 1)::text FROM set_drafts)),
  ('M17_ai_confidence stddev', (SELECT ROUND(STDDEV(ai_confidence)::numeric, 1)::text FROM set_drafts)),
  ('M18_skip 보유 article 수', (SELECT COUNT(*)::text FROM article_stats WHERE has_skip)),
  ('M19_skip 비율%', (SELECT ROUND((SUM(CASE WHEN has_skip THEN 1.0 ELSE 0.0 END) / COUNT(*) * 100)::numeric, 1)::text FROM article_stats)),
  ('M20_article당 의무 분포 (의무수:article수)', (SELECT STRING_AGG(extracted_count || ':' || articles, ', ' ORDER BY extracted_count) FROM article_count_dist)),
  ('M21_article당 의무 평균', (SELECT ROUND(AVG(extracted_count)::numeric, 2)::text FROM article_stats)),
  ('M22_article당 의무 stddev', (SELECT ROUND(STDDEV(extracted_count)::numeric, 2)::text FROM article_stats))
) AS metrics(metric, value)
ORDER BY metric;
