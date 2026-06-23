# WO-CONDITION-DDL-004
# condition_mapping_candidate DDL 최종확정안

**작성일:** 2026-06-23 | **상태:** 최종확정 / apply_migration 승인 대기

---

## DDL-003 대비 수정사항 3가지

| 항목 | DDL-003 | DDL-004 |
|---|---|---|
| UNIQUE 제약 | `(semantic_clause_id, input_field, input_value, applicable_sectors)` — NULL 중복 허용 | `condition_code NOT NULL` + `UNIQUE(condition_code)` + 보조 UNIQUE NULLS NOT DISTINCT |
| GIN 검증 기준 | "Bitmap Index Scan 반드시" | 초기 Seq Scan 정상, ANALYZE 후 확인으로 수정 |
| has_diving + SPECIAL | 정책 미확정 | `has_diving → ['CONSTRUCTION']` 확정, SPECIAL 미사용 유지 |

---

## 수정 상세

### 1. UNIQUE 제약: condition_code 기반으로 교체

**문제 (DDL-003):**
```sql
UNIQUE (semantic_clause_id, input_field, input_value, applicable_sectors)
-- NULL이 포함된 컬럼은 PostgreSQL UNIQUE에서 중복 허용됨
-- employee_count >= 50 이 3번 들어갈 수 있음
```

**해결 (DDL-004):**
```sql
-- condition_code NOT NULL로 승격
condition_code TEXT NOT NULL,

-- 단일 UNIQUE
CONSTRAINT cmc_unique_condition_code UNIQUE (condition_code),

-- 보조: sector+조건 조합 중복 방지 (NULLS NOT DISTINCT, PG15+)
CONSTRAINT cmc_unique_sector_mapping UNIQUE NULLS NOT DISTINCT (
  semantic_clause_id,
  input_field,
  input_value,
  applicable_sectors
)
```

**condition_code 설계 원칙:**
```
형식: {SECTOR_PREFIX}-{TYPE_CODE}-{SEQUENCE}
예시:
  IND-WORK-001   = INDUSTRIAL / WORK_ACT 첫번째
  CON-EQUIP-014  = CONSTRUCTION / EQUIPMENT_ACT 14번째
  BLD-THRES-003  = BUILDING / THRESHOLD 3번째
  ALL-NONE-001   = 전 섹터 공통 / NONE (has_* = false 류)

생성 규칙:
  - GPT 배치가 생성
  - 중복 시 INSERT 실패 → 배치 로그에 기록 후 스킵
  - 수동 검토 후 재적재
```

---

### 2. GIN 검증 기준 수정

**DDL-003 문제:** 초기 적재 전 EXPLAIN 실행 시 Seq Scan 나와도 정상인데 "반드시 Bitmap Index Scan"으로 오기재

**DDL-004 확정 검증 순서:**
```sql
-- STEP 1: 테이블 생성 확인
SELECT COUNT(*) FROM information_schema.tables
WHERE table_name = 'condition_mapping_candidate';  -- 1

-- STEP 2: 인덱스 존재 확인
SELECT indexname FROM pg_indexes
WHERE tablename = 'condition_mapping_candidate';  -- 9개 이상

-- STEP 3: CHECK 제약 확인
SELECT COUNT(*) FROM condition_mapping_candidate
WHERE 'COMMON' = ANY(applicable_sectors);  -- 0 (제약 테스트)

-- STEP 4: GIN 활용 확인 (초기 데이터 적재 후 실행)
-- 최소 1,000건 이상 적재 → ANALYZE 실행 → 아래 쿼리
ANALYZE condition_mapping_candidate;
EXPLAIN ANALYZE
  SELECT id FROM condition_mapping_candidate
  WHERE applicable_sectors @> ARRAY['INDUSTRIAL']
  AND review_status = 'CONFIRMED';
-- 기대값: Bitmap Index Scan on idx_cmc_applicable_sectors_gin
-- 초기 데이터 적을 경우 Seq Scan 나와도 정상 (플래너 판단)
```

---

### 3. has_diving ↔ SPECIAL 정책 확정

**문제 (DDL-003):**
- SPECIAL 미사용 원칙인데, has_diving이 WORK-005 (잠수작업) 20건과 연결됨
- SPECIAL로 분류 시 기존 매핑 소실 위험

**확정 (DDL-004):**
```
has_diving → applicable_sectors = ['CONSTRUCTION']
근거:
  - 잠수작업은 현행법상 건설업 특수작업 분류
  - WORK-005 20건 매핑 유지 가능
  - 향후 SPECIAL 활성화 시 ['CONSTRUCTION', 'SPECIAL']로 확장

SPECIAL 정책 (유지):
  DDL CHECK: 허용
  1차 적재: 금지
  서비스 사용: 금지
  활성화 시점: WO-CONDITION-SPECIAL-001 (별도 WO)
```

**적재 시 has_* → sector 매핑 기준:**
| has_* 필드 | applicable_sectors |
|---|---|
| has_chemical_substance, has_high_pressure_vessel, has_special_chemical | ['INDUSTRIAL'] |
| has_tower_crane, has_scaffolding, has_blasting, has_diving | ['CONSTRUCTION'] |
| has_elevator, has_escalator, has_fire_equipment | ['BUILDING'] |
| has_confined_space, has_asbestos_demo | ['INDUSTRIAL', 'CONSTRUCTION'] |
| 범용 안전보건관리체계, 교육 | ['INDUSTRIAL', 'CONSTRUCTION', 'BUILDING'] |

---

## 확정 DDL

```sql
CREATE TABLE condition_mapping_candidate (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  semantic_clause_id    UUID REFERENCES semantic_clause(id) ON DELETE SET NULL,
  source_article_id     UUID REFERENCES law_article(id) ON DELETE SET NULL,
  law_article_part_id   UUID REFERENCES law_article_part(id) ON DELETE SET NULL,
  appendix_condition_id UUID REFERENCES appendix_condition(id) ON DELETE SET NULL,
  applicable_sectors    TEXT[],
  condition_source      TEXT NOT NULL,
  condition_text_raw    TEXT,
  action_text_raw       TEXT,
  condition_type        TEXT NOT NULL,
  condition_code        TEXT NOT NULL,
  input_field           TEXT,
  input_operator        TEXT,
  input_value           TEXT,
  input_field_2         TEXT,
  input_operator_2      TEXT,
  input_value_2         TEXT,
  compound_operator     TEXT,
  required_equipment_type TEXT,
  required_work_type      TEXT,
  required_material_type  TEXT,
  required_facility_type  TEXT,
  confidence            NUMERIC(3,2),
  review_status         TEXT NOT NULL DEFAULT 'PENDING',
  null_condition_class  TEXT,
  exclude_reason        TEXT,
  reviewer              TEXT,
  reviewed_at           TIMESTAMPTZ,
  created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at            TIMESTAMPTZ NOT NULL DEFAULT now(),

  -- 중복 방지: condition_code 단일 식별자
  CONSTRAINT cmc_unique_condition_code UNIQUE (condition_code),

  -- 보조: sector+조건 조합 중복 방지 (PostgreSQL 15+ NULLS NOT DISTINCT)
  CONSTRAINT cmc_unique_sector_mapping UNIQUE NULLS NOT DISTINCT (
    semantic_clause_id,
    input_field,
    input_value,
    applicable_sectors
  ),

  -- COMMON 절대 금지 + 허용값 검증
  CONSTRAINT cmc_applicable_sectors_check CHECK (
    applicable_sectors IS NULL OR (
      NOT ('COMMON' = ANY(applicable_sectors))
      AND applicable_sectors <@ ARRAY['INDUSTRIAL','CONSTRUCTION','BUILDING','SPECIAL']
    )
  ),

  -- OUT_OF_SCOPE 외에는 sectors 필수
  CONSTRAINT cmc_applicable_sectors_required_check CHECK (
    condition_type = 'OUT_OF_SCOPE' OR applicable_sectors IS NOT NULL
  ),

  -- 참조 최소 1개 필수
  CONSTRAINT cmc_reference_required CHECK (
    condition_type = 'OUT_OF_SCOPE'
    OR semantic_clause_id IS NOT NULL
    OR law_article_part_id IS NOT NULL
    OR appendix_condition_id IS NOT NULL
  ),

  CONSTRAINT cmc_condition_source_check CHECK (
    condition_source IN ('CONDITION_TEXT','ACTION_TEXT','APPENDIX','MANUAL')
  ),
  CONSTRAINT cmc_condition_type_check CHECK (
    condition_type IN ('WORK_ACT','EQUIPMENT_ACT','FACILITY_ACT','MATERIAL_ACT',
                       'THRESHOLD','INDUSTRY','COMPOUND','NONE','OUT_OF_SCOPE')
  ),
  CONSTRAINT cmc_review_status_check CHECK (
    review_status IN ('PENDING','CONFIRMED','REJECTED')
  ),
  CONSTRAINT cmc_null_condition_class_check CHECK (
    null_condition_class IS NULL
    OR null_condition_class IN ('A_UNIVERSAL','B_HIDDEN_COND','C_OUT_OF_SCOPE')
  ),
  CONSTRAINT cmc_input_operator_check CHECK (
    input_operator IS NULL
    OR input_operator IN ('=','!=','>=','<=','>','<','IN','CONTAINS')
  ),
  CONSTRAINT cmc_compound_operator_check CHECK (
    compound_operator IS NULL OR compound_operator IN ('AND','OR')
  ),
  CONSTRAINT cmc_confidence_range CHECK (
    confidence IS NULL OR (confidence >= 0.0 AND confidence <= 1.0)
  ),
  CONSTRAINT cmc_compound_consistency CHECK (
    (input_field_2 IS NULL AND compound_operator IS NULL) OR
    (input_field_2 IS NOT NULL AND compound_operator IS NOT NULL)
  )
);

-- GIN 인덱스: @> 연산자 최적화
CREATE INDEX idx_cmc_applicable_sectors_gin
  ON condition_mapping_candidate USING GIN (applicable_sectors);

-- 체크엔진 핵심 조회 인덱스
CREATE INDEX idx_cmc_input_field_value
  ON condition_mapping_candidate (input_field, input_value)
  WHERE review_status = 'CONFIRMED';

CREATE INDEX idx_cmc_input_field
  ON condition_mapping_candidate (input_field)
  WHERE review_status = 'CONFIRMED';

-- 참조 인덱스
CREATE INDEX idx_cmc_semantic_clause
  ON condition_mapping_candidate (semantic_clause_id);

CREATE INDEX idx_cmc_source_article
  ON condition_mapping_candidate (source_article_id);

CREATE INDEX idx_cmc_condition_code
  ON condition_mapping_candidate (condition_code);

CREATE INDEX idx_cmc_review_status
  ON condition_mapping_candidate (review_status, condition_type);

CREATE INDEX idx_cmc_condition_type
  ON condition_mapping_candidate (condition_type);

CREATE INDEX idx_cmc_appendix_condition
  ON condition_mapping_candidate (appendix_condition_id)
  WHERE appendix_condition_id IS NOT NULL;

-- updated_at 자동 갱신
CREATE OR REPLACE FUNCTION update_cmc_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_cmc_updated_at
  BEFORE UPDATE ON condition_mapping_candidate
  FOR EACH ROW EXECUTE FUNCTION update_cmc_updated_at();
```

---

## 검증 쿼리 (apply_migration 후 순서대로 실행)

```sql
-- 1. 테이블 존재 확인
SELECT COUNT(*) FROM information_schema.tables
WHERE table_name = 'condition_mapping_candidate';  -- 기대: 1

-- 2. 인덱스 목록 확인
SELECT indexname FROM pg_indexes
WHERE tablename = 'condition_mapping_candidate'
ORDER BY indexname;  -- 기대: 9개

-- 3. CHECK 제약 동작 확인 (삽입 테스트)
-- 아래 INSERT는 실패해야 정상
INSERT INTO condition_mapping_candidate
  (condition_source, condition_type, condition_code, applicable_sectors)
VALUES ('MANUAL', 'NONE', 'TEST-000', ARRAY['COMMON']);
-- ERROR 나오면 PASS

-- 4. COMMON 완전 차단 확인
SELECT COUNT(*) FROM condition_mapping_candidate
WHERE 'COMMON' = ANY(applicable_sectors);  -- 기대: 0

-- 5. GIN 확인 (데이터 1,000건+ 적재 후)
ANALYZE condition_mapping_candidate;
EXPLAIN ANALYZE
  SELECT id FROM condition_mapping_candidate
  WHERE applicable_sectors @> ARRAY['INDUSTRIAL']
  AND review_status = 'CONFIRMED';
-- 충분한 데이터: Bitmap Index Scan on idx_cmc_applicable_sectors_gin
-- 초기 소량: Seq Scan 나와도 정상 (플래너 판단, 오류 아님)
```

---

## 체크엔진 표준 조회 패턴

```sql
-- sector-first: 모든 조회의 1순위
SELECT cmc.*
FROM condition_mapping_candidate cmc
WHERE cmc.applicable_sectors @> ARRAY[:sector]  -- 1순위: GIN
  AND cmc.input_field = :input_field             -- 2순위
  AND cmc.input_value = :input_value             -- 3순위
  AND cmc.review_status = 'CONFIRMED'            -- 4순위
ORDER BY cmc.condition_code;
```

---

## 다음 단계

1. `apply_migration` 실행 (본 DDL)
2. 검증 쿼리 5개 순서대로 실행
3. WO-CONDITION-002: `has_*` 기반 초기 매핑 적재 시작
   - condition_code 생성 규칙 확정 후 GPT 배치
   - sector 매핑 기준표 (has_* → applicable_sectors) 위 표 적용

---

*WO-CONDITION-DDL-004 최종확정. 승인 후 apply_migration.*
