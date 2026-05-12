-- =============================================================================
-- Track C — Frequency Analysis SQL (DRAFT v0.1, 2026-05-09)
-- =============================================================================
-- 실행 시점: Track A Phase 1 (Kiwi 설치) 완료 후
-- 목적: semantic_clause.source_text → 명사 후보 빈도 추출 → top 1000 후보
-- 원칙:
--   1. LLM X
--   2. 직접 인용만 (substring of source_text, 변경 X)
--   3. 단순 토큰화 (1차 baseline) + Kiwi 형태소 분석 (2차) 교차 검증
--   4. 모든 후보는 verified=false 초기 → 사용자 검증 통과만 verified=true
-- =============================================================================

-- 사전 점검 (2026-05-09 확인):
--   total_rows           = 160,372
--   distinct_articles    = 26,801
--   avg_source_len       = 62 chars
--   min / max            = 1 / 3,752 chars


-- -----------------------------------------------------------------------------
-- A. Pre-Kiwi surface tokenization (TF baseline)
-- -----------------------------------------------------------------------------
-- 한계: 조사 미분리 (사업주는 / 사업주가 / 사업주에게 = 별도 token)
-- 용도: Kiwi 결과 cross-check (Kiwi 인식 누락 토큰 발견용)

WITH tokens AS (
  SELECT
    regexp_split_to_table(
      regexp_replace(source_text, '[^\uAC00-\uD7A3a-zA-Z0-9]+', ' ', 'g'),
      '\s+'
    ) AS token
  FROM semantic_clause
  WHERE source_text IS NOT NULL
    AND LENGTH(source_text) >= 2
),
filtered AS (
  SELECT token
  FROM tokens
  WHERE LENGTH(token) >= 2
    AND token ~ '[\uAC00-\uD7A3]'   -- 한글 포함만
    AND token !~ '^[0-9]+$'          -- 순수 숫자 제외
)
SELECT
  token AS surface_form,
  COUNT(*) AS term_freq,
  ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS rank
FROM filtered
GROUP BY token
HAVING COUNT(*) >= 5
ORDER BY term_freq DESC
LIMIT 2000;


-- -----------------------------------------------------------------------------
-- B. Document Frequency (DF) — token이 등장한 의미절 수
-- -----------------------------------------------------------------------------
-- 용도: 일반어 vs 도메인어 1차 분류
--   df_pct > 30.0  → 일반어 의심 (검증 제외 후보, 단 DEFINITION 어휘 注)
--   df_pct 0.1~30 → 법령 도메인 후보 (검증 필요)
--   df_pct < 0.1  → 희귀 (수동 검토 — 신조어/전문용어 가능성)

WITH clause_tokens AS (
  SELECT
    id AS clause_id,
    regexp_split_to_table(
      regexp_replace(source_text, '[^\uAC00-\uD7A3a-zA-Z0-9]+', ' ', 'g'),
      '\s+'
    ) AS token
  FROM semantic_clause
  WHERE source_text IS NOT NULL
),
distinct_pairs AS (
  SELECT DISTINCT clause_id, token
  FROM clause_tokens
  WHERE LENGTH(token) >= 2
    AND token ~ '[\uAC00-\uD7A3]'
)
SELECT
  token AS surface_form,
  COUNT(*) AS doc_freq,
  ROUND(100.0 * COUNT(*) / 160372, 4) AS df_pct
FROM distinct_pairs
GROUP BY token
HAVING COUNT(*) >= 50
ORDER BY doc_freq DESC
LIMIT 2000;


-- -----------------------------------------------------------------------------
-- C. Combined view (TF + DF + sample sentences)
-- -----------------------------------------------------------------------------
-- 검증 시 token이 등장하는 sample 의미절 3건 함께 제공.
-- 임시 테이블 `ext_track_c_freq_v01`에 저장 (Track A migration 후 결정).
-- (구현 보류 — A/B 결과 확인 후 임계값 조정)


-- =============================================================================
-- D. Post-Kiwi 명사 추출 (Python 파이프라인) — 의사코드
-- =============================================================================
-- 본 SQL의 surface tokens는 baseline. 실제 명사 후보 추출은 Kiwi.
-- 코드 위치: tai-api/engine/track_c/extractor.py (Track A 인프라 확정 후)
--
-- 추출 품사:
--   NNG (일반명사)
--   NNP (고유명사)
--   NF  (미등록어 — Kiwi가 분석 실패한 후보, 사전 등록 가장 중요)
--
-- 산출 컬럼:
--   surface_form / pos / term_freq / doc_freq / df_pct
--   sample_clause_ids[3] / candidate_class (general/domain/compound/unknown)
--   verified (false 초기) / verification_note (NULL 초기)
--
-- 산출 위치:
--   1차: ext_track_c_candidates (임시 테이블)
--   2차 (검증 후): dict_legal_terms (verified=true만 INSERT)
