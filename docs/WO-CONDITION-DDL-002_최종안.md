# WO-CONDITION-DDL-002
# condition_mapping_candidate DDL 최종안

**작성일:** 2026-06-23 | **상태:** 설계 완료 / apply_migration 금지

---

## DDL-001 대비 변경점

| 항목 | DDL-001 | DDL-002 |
|---|---|---|
| applicable_sectors 콴럼 | 없음 | `TEXT[]` 추가 |
| COMMON 금지 제약 | 없음 | `cmc_applicable_sectors_check` 추가 |
| OUT_OF_SCOPE sectors 처리 | 미정 | `NULL` 명시 |
| A_UNIVERSAL sectors 처리 | 미정 | `ARRAY['INDUSTRIAL','CONSTRUCTION','BUILDING']` |
| GIN 인덱스 | 없음 | `idx_cmc_applicable_sectors_gin` 추가 |
| sectors 필수 제약 | 없음 | `cmc_applicable_sectors_required_check` 추가 |

---

## applicable_sectors 컴럼

```
TYPE:    TEXT[]
NULL:    허용 (OUT_OF_SCOPE는 NULL)
허용값: INDUSTRIAL / CONSTRUCTION / BUILDING / SPECIAL
금지값: COMMON (절대 금지)

저장 패턴:
  타워크레인 의무:   ARRAY['CONSTRUCTION']
  화학물질 의무:  ARRAY['INDUSTRIAL']
  보일러 의무:    ARRAY['INDUSTRIAL','BUILDING']
  밀폐공간 의무:  ARRAY['INDUSTRIAL','CONSTRUCTION','BUILDING']
  안전관리자:   ARRAY['INDUSTRIAL','CONSTRUCTION','BUILDING']
  OUT_OF_SCOPE:  NULL
```

---

## 핵심 CHECK 제약 (DDL-002 신규 2개)

```sql
-- COMMON 금지 + 유효값
CONSTRAINT cmc_applicable_sectors_check CHECK (
  applicable_sectors IS NULL OR (
    NOT ('COMMON' = ANY(applicable_sectors))
    AND applicable_sectors <@ ARRAY['INDUSTRIAL','CONSTRUCTION','BUILDING','SPECIAL']
  )
),

-- OUT_OF_SCOPE 제외 시 필수
CONSTRAINT cmc_applicable_sectors_required_check CHECK (
  condition_type = 'OUT_OF_SCOPE'
  OR applicable_sectors IS NOT NULL
)
```

---

## 신규 인덱스 (GIN)

```sql
CREATE INDEX idx_cmc_applicable_sectors_gin
  ON condition_mapping_candidate
  USING GIN (applicable_sectors);
-- 활용: WHERE 'INDUSTRIAL' = ANY(applicable_sectors)
```

---

## 검증 쿼리 4개

```sql
-- 1. COMMON 금지
SELECT COUNT(*) FROM condition_mapping_candidate
WHERE 'COMMON' = ANY(applicable_sectors);
-- 목표: 0

-- 2. 유효하지 않은 섹터 없음
SELECT id, applicable_sectors FROM condition_mapping_candidate
WHERE applicable_sectors IS NOT NULL
  AND NOT (applicable_sectors <@ ARRAY['INDUSTRIAL','CONSTRUCTION','BUILDING','SPECIAL']);
-- 목표: 0건

-- 3. OUT_OF_SCOPE는 sectors = NULL
SELECT COUNT(*) FROM condition_mapping_candidate
WHERE condition_type = 'OUT_OF_SCOPE' AND applicable_sectors IS NOT NULL;
-- 목표: 0

-- 4. 정상 매핑은 sectors 존재
SELECT COUNT(*) FROM condition_mapping_candidate
WHERE condition_type != 'OUT_OF_SCOPE' AND applicable_sectors IS NULL;
-- 목표: 0
```

---

## 최종 DDL (apply_migration 승인 후 실행)

```sql
CREATE TABLE condition_mapping_candidate (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- 법령 참조
  semantic_clause_id    UUID REFERENCES semantic_clause(id) ON DELETE SET NULL,
  source_article_id     UUID REFERENCES law_article(id) ON DELETE SET NULL,
  law_article_part_id   UUID REFERENCES law_article_part(id) ON DELETE SET NULL,
  appendix_condition_id UUID REFERENCES appendix_condition(id) ON DELETE SET NULL,

  -- 적용영역 (COMMON 금지)
  applicable_sectors    TEXT[],

  -- 조건 출처
  condition_source      TEXT NOT NULL,
  condition_text_raw    TEXT,
  action_text_raw       TEXT,

  -- 조건 분류
  condition_type        TEXT NOT NULL,
  condition_code        TEXT,

  -- 단일 조건
  input_field           TEXT,
  input_operator        TEXT,
  input_value           TEXT,

  -- 복합 조건
  input_field_2         TEXT,
  input_operator_2      TEXT,
  input_value_2         TEXT,
  compound_operator     TEXT,

  -- 법령 요구 대상
  required_equipment_type TEXT,
  required_work_type      TEXT,
  required_material_type  TEXT,
  required_facility_type  TEXT,

  -- 검토 상태
  confidence            NUMERIC(3,2),
  review_status         TEXT NOT NULL DEFAULT 'PENDING',
  null_condition_class  TEXT,
  exclude_reason        TEXT,
  reviewer              TEXT,
  reviewed_at           TIMESTAMPTZ,

  created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at            TIMESTAMPTZ NOT NULL DEFAULT now(),

  -- CHECK 제약
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
  CONSTRAINT cmc_condition_source_check CHECK (
    condition_source IN ('CONDITION_TEXT','ACTION_TEXT','APPENDIX','MANUAL')
  ),
  CONSTRAINT cmc_condition_type_check CHECK (
    condition_type IN (
      'WORK_ACT','EQUIPMENT_ACT','FACILITY_ACT','MATERIAL_ACT',
      'THRESHOLD','INDUSTRY','COMPOUND','NONE','OUT_OF_SCOPE'
    )
  ),
  CONSTRAINT cmc_review_status_check CHECK (
    review_status IN ('PENDING','CONFIRMED','REJECTED')
  ),
  CONSTRAINT cmc_null_condition_class_check CHECK (
    null_condition_class IS NULL OR
    null_condition_class IN ('A_UNIVERSAL','B_HIDDEN_COND','C_OUT_OF_SCOPE')
  ),
  CONSTRAINT cmc_input_operator_check CHECK (
    input_operator IS NULL OR
    input_operator IN ('=','!=','>=','<=','>','<','IN','CONTAINS')
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

-- 인덱스
CREATE INDEX idx_cmc_input_field_value ON condition_mapping_candidate (input_field, input_value) WHERE review_status = 'CONFIRMED';
CREATE INDEX idx_cmc_input_field ON condition_mapping_candidate (input_field) WHERE review_status = 'CONFIRMED';
CREATE INDEX idx_cmc_semantic_clause ON condition_mapping_candidate (semantic_clause_id);
CREATE INDEX idx_cmc_source_article ON condition_mapping_candidate (source_article_id);
CREATE INDEX idx_cmc_condition_code ON condition_mapping_candidate (condition_code) WHERE condition_code IS NOT NULL;
CREATE INDEX idx_cmc_review_status ON condition_mapping_candidate (review_status, condition_type);
CREATE INDEX idx_cmc_condition_type ON condition_mapping_candidate (condition_type);
CREATE INDEX idx_cmc_appendix_condition ON condition_mapping_candidate (appendix_condition_id) WHERE appendix_condition_id IS NOT NULL;
CREATE INDEX idx_cmc_applicable_sectors_gin ON condition_mapping_candidate USING GIN (applicable_sectors);

-- 트리거
CREATE OR REPLACE FUNCTION update_cmc_updated_at()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = now(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_cmc_updated_at
  BEFORE UPDATE ON condition_mapping_candidate
  FOR EACH ROW EXECUTE FUNCTION update_cmc_updated_at();
```

---

*WO-CONDITION-DDL-002 완료. 승인 후 apply_migration.*
