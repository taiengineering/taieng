# WO-CONDITION-DDL-003
# condition_mapping_candidate DDL 확정안

**작성일:** 2026-06-23 | **상태:** 확정 / apply_migration 승인 대기

---

## DDL-002 대비 수정사항 4가지

| 항목 | DDL-002 | DDL-003 |
|---|---|---|
| 조회 연산자 | ANY() 언급 | `@>` 확정 |
| SPECIAL 정리 | 허용으로 읽힐 | DDL허용/적재금지/서비스미사용 명문화 |
| 중복 방지 | 없음 | UNIQUE 제약 추가 |
| 조회 경로 | 미명시 | sector-first 명시 |

---

## 핵심 확정 사항

### 1. 조회 연산자: `@>` 확정

```sql
-- 확정: GIN 인덱스 공식 지원 연산자
WHERE applicable_sectors @> ARRAY['INDUSTRIAL']

-- 체크엔진 표준 조회
SELECT * FROM condition_mapping_candidate
WHERE applicable_sectors @> ARRAY[factory.sector]   -- 1순위: GIN
  AND input_field = 'has_chemical_substance'          -- 2순위
  AND input_value = 'true'                            -- 3순위
  AND review_status = 'CONFIRMED';                    -- 4순위
```

| | ANY() | @> |
|---|---|---|
| GIN 활용 | 비보장 | **보장** |
| 복수 섹터 필터 | 비효율 | `@> ARRAY['A','B']` |

### 2. TEXT[] 유지 + 오타 방지 운영 원칙

```
GPT 배치 적재 프롬프트에 반드시 포함:
  "적용영역은 다음 중 하나만:
   INDUSTRIAL, CONSTRUCTION, BUILDING, SPECIAL"

적재 전 정규화: UPPER(TRIM(sector_value))
```

### 3. SPECIAL 운영정체

```
DDL 허용 여부:  허용 (CHECK 제약에 'SPECIAL' 포함)
1차 적재:      금지
서비스 사용:  금지
향후 활성화:  WO-CONDITION-SPECIAL-001
```

### 4. 중복 방지 UNIQUE

```sql
CONSTRAINT cmc_unique_mapping UNIQUE (
  semantic_clause_id,
  input_field,
  input_value,
  applicable_sectors
)
-- GPT 배치 적재 시 동일 매핑 누적 방지
```

---

## 조회 경로 순서 (sector-first)

```
매핑 생성 순서:
  1. sector 결정 (INDUSTRIAL / CONSTRUCTION / BUILDING)
  2. 해당 sector 법령만 조회
  3. 조건 코드 생성

체크엔진 조회:
  applicable_sectors @> ARRAY[sector]  ← 1순위 (GIN)
  input_field = ...                    ← 2순위
  input_value = ...                    ← 3순위
  review_status = 'CONFIRMED'          ← 4순위
```

---

## 확정 DDL (apply_migration 승인 후 실행)

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
  condition_code        TEXT,
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

  CONSTRAINT cmc_unique_mapping UNIQUE (semantic_clause_id, input_field, input_value, applicable_sectors),
  CONSTRAINT cmc_applicable_sectors_check CHECK (
    applicable_sectors IS NULL OR (
      NOT ('COMMON' = ANY(applicable_sectors))
      AND applicable_sectors <@ ARRAY['INDUSTRIAL','CONSTRUCTION','BUILDING','SPECIAL']
    )
  ),
  CONSTRAINT cmc_applicable_sectors_required_check CHECK (
    condition_type = 'OUT_OF_SCOPE' OR applicable_sectors IS NOT NULL
  ),
  CONSTRAINT cmc_reference_required CHECK (
    condition_type = 'OUT_OF_SCOPE'
    OR semantic_clause_id IS NOT NULL
    OR law_article_part_id IS NOT NULL
    OR appendix_condition_id IS NOT NULL
  ),
  CONSTRAINT cmc_condition_source_check CHECK (condition_source IN ('CONDITION_TEXT','ACTION_TEXT','APPENDIX','MANUAL')),
  CONSTRAINT cmc_condition_type_check CHECK (condition_type IN ('WORK_ACT','EQUIPMENT_ACT','FACILITY_ACT','MATERIAL_ACT','THRESHOLD','INDUSTRY','COMPOUND','NONE','OUT_OF_SCOPE')),
  CONSTRAINT cmc_review_status_check CHECK (review_status IN ('PENDING','CONFIRMED','REJECTED')),
  CONSTRAINT cmc_null_condition_class_check CHECK (null_condition_class IS NULL OR null_condition_class IN ('A_UNIVERSAL','B_HIDDEN_COND','C_OUT_OF_SCOPE')),
  CONSTRAINT cmc_input_operator_check CHECK (input_operator IS NULL OR input_operator IN ('=','!=','>=','<=','>','<','IN','CONTAINS')),
  CONSTRAINT cmc_compound_operator_check CHECK (compound_operator IS NULL OR compound_operator IN ('AND','OR')),
  CONSTRAINT cmc_confidence_range CHECK (confidence IS NULL OR (confidence >= 0.0 AND confidence <= 1.0)),
  CONSTRAINT cmc_compound_consistency CHECK (
    (input_field_2 IS NULL AND compound_operator IS NULL) OR
    (input_field_2 IS NOT NULL AND compound_operator IS NOT NULL)
  )
);

CREATE INDEX idx_cmc_applicable_sectors_gin ON condition_mapping_candidate USING GIN (applicable_sectors);
CREATE INDEX idx_cmc_input_field_value ON condition_mapping_candidate (input_field, input_value) WHERE review_status = 'CONFIRMED';
CREATE INDEX idx_cmc_input_field ON condition_mapping_candidate (input_field) WHERE review_status = 'CONFIRMED';
CREATE INDEX idx_cmc_semantic_clause ON condition_mapping_candidate (semantic_clause_id);
CREATE INDEX idx_cmc_source_article ON condition_mapping_candidate (source_article_id);
CREATE INDEX idx_cmc_condition_code ON condition_mapping_candidate (condition_code) WHERE condition_code IS NOT NULL;
CREATE INDEX idx_cmc_review_status ON condition_mapping_candidate (review_status, condition_type);
CREATE INDEX idx_cmc_condition_type ON condition_mapping_candidate (condition_type);
CREATE INDEX idx_cmc_appendix_condition ON condition_mapping_candidate (appendix_condition_id) WHERE appendix_condition_id IS NOT NULL;

CREATE OR REPLACE FUNCTION update_cmc_updated_at()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = now(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_cmc_updated_at
  BEFORE UPDATE ON condition_mapping_candidate
  FOR EACH ROW EXECUTE FUNCTION update_cmc_updated_at();
```

---

## 검증 쿼리 (apply_migration 후)

```sql
SELECT COUNT(*) FROM condition_mapping_candidate WHERE 'COMMON' = ANY(applicable_sectors);  -- 0
SELECT COUNT(*) FROM condition_mapping_candidate WHERE condition_type = 'OUT_OF_SCOPE' AND applicable_sectors IS NOT NULL;  -- 0
SELECT COUNT(*) FROM condition_mapping_candidate WHERE condition_type != 'OUT_OF_SCOPE' AND applicable_sectors IS NULL;  -- 0
EXPLAIN SELECT id FROM condition_mapping_candidate WHERE applicable_sectors @> ARRAY['INDUSTRIAL'];  -- GIN 인덱스 확인
```

---

*WO-CONDITION-DDL-003 확정. 승인 후 apply_migration.*
