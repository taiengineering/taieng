# WO-CONDITION-DDL-001
# condition_mapping_candidate 테이블 DDL 설계서

**작성일:** 2026-06-23  
**상태:** 설계 초안 / 승인 대기  
**참조:** WO-CONDITION-001, WO-CONDITION-MAP-001  
**금지:** 테이블 생성 금지 / apply_migration 금지 / INSERT 금지

---

## 1. 테이블 목적

소비자 입력값이 어떤 법령 조건을 충족하는지 추적 가능하게 연결한다.

```
소비자 입력
  has_confined_space = true
  equipment_type_code = 'MOBILE_CRANE'
  employee_count = 75
        ↓
condition_mapping_candidate 조회
        ↓
semantic_clause_id 목록 반환
        ↓
의무 확정
```

이 테이블이 하지 않는 것: 법령 원문 저장, 의무 내용 저장, 제재 정보 저장, 체크 결과 저장

---

## 2. 컬럼 정의

### 2-1. 식별자 및 법령 참조

| 컬럼명 | 타입 | NOT NULL | 설명 |
|---|---|---|---|
| `id` | UUID | ✓ | PK |
| `semantic_clause_id` | UUID | △ | semantic_clause.id FK |
| `source_article_id` | UUID | △ | law_article.id (비정규화) |
| `law_article_part_id` | UUID | △ | law_article_part.id FK |
| `appendix_condition_id` | UUID | △ | appendix_condition.id FK |

**Q1 결정: 둘 다 보존.** semantic_clause_id + law_article_part_id

### 2-2. 조건 출처

| 컬럼명 | 설명 |
|---|---|
| `condition_source` | CONDITION_TEXT / ACTION_TEXT / APPENDIX / MANUAL |
| `condition_text_raw` | condition_text 원문 |
| `action_text_raw` | action_text 원문 (B유형 참조용) |

### 2-3. 조건 분류

| 컬럼명 | 설명 |
|---|---|
| `condition_type` | WORK_ACT / EQUIPMENT_ACT / FACILITY_ACT / MATERIAL_ACT / THRESHOLD / INDUSTRY / COMPOUND / NONE / OUT_OF_SCOPE |
| `condition_code` | 식별자 코드 (예: EQUIPMENT_ACT:TOWER_CRANE_INSTALL) |

**Q4 결정: 식별자 + 그룹화 키 역할. 실제 평가 로직은 input_field+operator+value 담당.**

### 2-4. 입력값 매핑 (단일)

| 컬럼명 | 설명 |
|---|---|
| `input_field` | 소비자 입력 필드명 (has_confined_space, equipment_type_code 등) |
| `input_operator` | =, !=, >=, <=, >, <, IN, CONTAINS |
| `input_value` | 비교값 (TEXT) |

### 2-5. 복합 조건

| 컬럼명 | 설명 |
|---|---|
| `input_field_2` | 두 번째 조건 필드 |
| `input_operator_2` | 두 번째 연산자 |
| `input_value_2` | 두 번째 비교값 |
| `compound_operator` | AND / OR |

**Q2 결정: input_field_2 방식으로 충분. child table 불필요 (복합 조건 약 8건, 전체 0.5%).**

### 2-6. 법령 요구 대상 세분화

| 컬럼명 | 설명 |
|---|---|
| `required_equipment_type` | TOWER_CRANE / MOBILE_CRANE / JIB_CRANE 등 |
| `required_work_type` | CONFINED_SPACE / BLASTING / HIGH_PRESSURE 등 |
| `required_material_type` | HAZMAT / PERMITTED_HAZMAT / PROHIBITED_HAZMAT 등 |
| `required_facility_type` | COLD_STORAGE / HIGH_PRESSURE_CHAMBER 등 |

### 2-7. 검토 상태

| 컬럼명 | 기본값 | 설명 |
|---|---|---|
| `confidence` | NULL | 0.0~1.0 |
| `review_status` | 'PENDING' | PENDING / CONFIRMED / REJECTED |
| `null_condition_class` | NULL | A_UNIVERSAL / B_HIDDEN_COND / C_OUT_OF_SCOPE |
| `exclude_reason` | NULL | C유형 제외 사유 |
| `reviewer` | NULL | 검토자 |
| `reviewed_at` | NULL | 검토 완료 시각 |

### 2-8. appendix_condition 연동

**Q3 결정: FK 참조만. 복제 안 함.** appendix_condition_id FK로 참조, 체크 시 JOIN 평가.

### 2-9. OUT_OF_SCOPE 처리

**Q5 결정: 이 테이블에 포함 (REJECTED 상태).** audit trail 보존, 향후 범위 확장 대응.

---

## 3. 실제 DDL 초안

```sql
-- ============================================================
-- WO-CONDITION-DDL-001  condition_mapping_candidate
-- 생성 금지 (설계서 용도만)
-- ============================================================

CREATE TABLE condition_mapping_candidate (

  -- 식별자
  id                    UUID        PRIMARY KEY DEFAULT gen_random_uuid(),

  -- 법령 참조
  semantic_clause_id    UUID        REFERENCES semantic_clause(id)      ON DELETE SET NULL,
  source_article_id     UUID        REFERENCES law_article(id)          ON DELETE SET NULL,
  law_article_part_id   UUID        REFERENCES law_article_part(id)     ON DELETE SET NULL,
  appendix_condition_id UUID        REFERENCES appendix_condition(id)   ON DELETE SET NULL,

  -- 조건 출처
  condition_source      TEXT        NOT NULL,
  condition_text_raw    TEXT,
  action_text_raw       TEXT,

  -- 조건 분류
  condition_type        TEXT        NOT NULL,
  condition_code        TEXT,

  -- 입력값 매핑 (단일 조건)
  input_field           TEXT,
  input_operator        TEXT,
  input_value           TEXT,

  -- 입력값 매핑 (복합 조건 2번째)
  input_field_2         TEXT,
  input_operator_2      TEXT,
  input_value_2         TEXT,
  compound_operator     TEXT,

  -- 법령 요구 대상 세분화
  required_equipment_type TEXT,
  required_work_type      TEXT,
  required_material_type  TEXT,
  required_facility_type  TEXT,

  -- 검토 상태
  confidence            NUMERIC(3,2),
  review_status         TEXT        NOT NULL DEFAULT 'PENDING',
  null_condition_class  TEXT,
  exclude_reason        TEXT,
  reviewer              TEXT,
  reviewed_at           TIMESTAMPTZ,

  -- 타임스탬프
  created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at            TIMESTAMPTZ NOT NULL DEFAULT now(),

  -- CHECK 제약
  CONSTRAINT cmc_condition_source_check CHECK (
    condition_source IN ('CONDITION_TEXT', 'ACTION_TEXT', 'APPENDIX', 'MANUAL')
  ),
  CONSTRAINT cmc_condition_type_check CHECK (
    condition_type IN (
      'WORK_ACT', 'EQUIPMENT_ACT', 'FACILITY_ACT', 'MATERIAL_ACT',
      'THRESHOLD', 'INDUSTRY', 'COMPOUND', 'NONE', 'OUT_OF_SCOPE'
    )
  ),
  CONSTRAINT cmc_review_status_check CHECK (
    review_status IN ('PENDING', 'CONFIRMED', 'REJECTED')
  ),
  CONSTRAINT cmc_null_condition_class_check CHECK (
    null_condition_class IS NULL OR
    null_condition_class IN ('A_UNIVERSAL', 'B_HIDDEN_COND', 'C_OUT_OF_SCOPE')
  ),
  CONSTRAINT cmc_input_operator_check CHECK (
    input_operator IS NULL OR
    input_operator IN ('=', '!=', '>=', '<=', '>', '<', 'IN', 'CONTAINS')
  ),
  CONSTRAINT cmc_compound_operator_check CHECK (
    compound_operator IS NULL OR compound_operator IN ('AND', 'OR')
  ),
  CONSTRAINT cmc_confidence_range CHECK (
    confidence IS NULL OR (confidence >= 0.0 AND confidence <= 1.0)
  ),
  CONSTRAINT cmc_compound_consistency CHECK (
    (input_field_2 IS NULL AND compound_operator IS NULL) OR
    (input_field_2 IS NOT NULL AND compound_operator IS NOT NULL)
  ),
  CONSTRAINT cmc_reference_required CHECK (
    condition_type = 'OUT_OF_SCOPE' OR
    semantic_clause_id IS NOT NULL OR
    law_article_part_id IS NOT NULL OR
    appendix_condition_id IS NOT NULL
  )
);

-- 인덱스
CREATE INDEX idx_cmc_input_field_value
  ON condition_mapping_candidate (input_field, input_value)
  WHERE review_status = 'CONFIRMED';

CREATE INDEX idx_cmc_input_field
  ON condition_mapping_candidate (input_field)
  WHERE review_status = 'CONFIRMED';

CREATE INDEX idx_cmc_semantic_clause
  ON condition_mapping_candidate (semantic_clause_id);

CREATE INDEX idx_cmc_source_article
  ON condition_mapping_candidate (source_article_id);

CREATE INDEX idx_cmc_condition_code
  ON condition_mapping_candidate (condition_code)
  WHERE condition_code IS NOT NULL;

CREATE INDEX idx_cmc_review_status
  ON condition_mapping_candidate (review_status, condition_type);

CREATE INDEX idx_cmc_condition_type
  ON condition_mapping_candidate (condition_type);

CREATE INDEX idx_cmc_appendix_condition
  ON condition_mapping_candidate (appendix_condition_id)
  WHERE appendix_condition_id IS NOT NULL;

-- updated_at 자동 갱신 트리거
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

## 4. 설계 결정 요약 (Q1~Q5)

| Q | 질문 | 결정 |
|---|---|---|
| Q1 | semantic_clause_id 단독 vs law_article_part_id 병용 | **둘 다 보존** |
| Q2 | input_field_2 방식 vs child table | **input_field_2 방식** (복합 8건) |
| Q3 | appendix_condition 복제 vs 참조 | **FK 참조만** |
| Q4 | condition_code 식별자 vs 로직 키 | **식별자 + 그룹화 키** |
| Q5 | OUT_OF_SCOPE 포함 vs 별도 table | **이 테이블에 REJECTED 포함** |

---

## 5. 생성 전 검토 필요 사항

1. **ON DELETE 방식** — SET NULL vs RESTRICT (법령 개정 시 semantic_clause 삭제 발생하는가?)
2. **condition_code 명명 체계** — GPT 선확정 후 적용인가, 이 설계서 초안으로 진행하는가?
3. **input_field ENUM 제한** — TEXT vs CHECK 제약 (소비자 입력 필드 목록 확정 여부)
4. **WO-APPENDIX-COLLECT-001 순서** — appendix FK NULL 허용 상태로 먼저 생성 가능
5. **Partial Index 초기 비어있음** — CONFIRMED 전환 워크플로우 필요
6. **예상 초기 행 수** — 약 1,400~1,500건

---

*WO-CONDITION-DDL-001 설계서 완료. 승인 후 apply_migration 진행.*
