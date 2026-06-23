# WO-PATTERN-SCOPE-001
# 3섹션 입력패턴·법령패턴·매핑구조 확정

**작성일:** 2026-06-23 | **상태:** 확정
**엔진 설계 금지 / 개별 조문 검증 금지 / 정제레이어 논의 금지**

---

## TASK-001: 섹션 정의

### 3섹션 확정

```
INDUSTRIAL    산업 (공장·제조·화학·물류)
CONSTRUCTION  건설 (건축·토목·플랜트 공사)
BUILDING      건물 (완공 후 유지관리·운영)
```

**COMMON 없음.** 공용 법령은 applicable_sectors = ['INDUSTRIAL','CONSTRUCTION','BUILDING'] 다중 배열로 표현.

---

### 섹션별 입력 원천 확정

#### INDUSTRIAL 입력 원천

| 원천 | 실제 데이터 | 규모 |
|---|---|---|
| KSIC 업종코드 | C10~C30(제조), D35(에너지), H49~H52(운수) | 38개 코드 (현재 DB) |
| 공정(process_lv1) | 반응·증류·원료처리·혼합·도금·용접·밀폐공간작업·도장·건조·위험물보관 등 | 15개 공정명 |
| 설비(equipment_type_code) | PRESSURE_VESSEL·CRANE·CONVEYOR·PRESS 등 | 정수코드 36종 + 의미코드 4종 |
| 화학물질 보유(has_*) | has_chemical_substance·has_high_pressure_gas | boolean |
| 유해인자(has_*) | has_confined_space·has_boiler | boolean |
| 수치조건 | employee_count·building_area·electrical_capacity_kw | numeric |

#### CONSTRUCTION 입력 원천

| 원천 | 실제 데이터 | 규모 |
|---|---|---|
| KSIC 업종코드 | F41(건축), F42(토목) | 5,063개 사업장 (88%) |
| 공사종류(process_lv1) | 토공사·철근콘크리트·철골공사·타워크레인양중·발파굴착·방수공사·전기공사 등 | 8개 공정명 |
| 장비(has_*/equipment) | has_tower_crane·has_blasting | boolean |
| 위험작업(has_*) | has_diving·has_asbestos_demo·has_confined_space | boolean |
| 공사금액 | construction_amount (numeric, 5,114개) | 만원 단위 |
| 현장조건 | contractor_count (협력업체 수) | integer |

#### BUILDING 입력 원천

| 원천 | 실제 데이터 | 규모 |
|---|---|---|
| KSIC 업종코드 | Q86(보건·의료), G4719(유통), N7400(사무서비스) | 41개 사업장 |
| 시설(process_lv1) | 보일러운영·전기설비운영·승강기운영·소방설비점검·청소위생·경비보안·주차관제 등 | 8개 공정명 |
| 설비 보유(has_*/elevator) | has_boiler·has_asbestos_demo·elevator_count | boolean/integer |
| 면적 | building_area (numeric, 623개) | ㎡ 단위 |
| 인원 | employee_count·occupant_capacity | integer |
| 관리대상 | has_confined_space·has_chemical_substance | boolean |

---

## TASK-002: 입력패턴 테이블 설계

### 테이블: `input_pattern_catalog`

**목적:** 입력값 4,000여 개를 섹션별 패턴으로 분류하는 카탈로그.
"4,000여 개"의 의미 = KSIC 전체(1,200+ 세분류) + 공정명 + 설비코드 + has_* + 수치조건 전체.

```sql
CREATE TABLE input_pattern_catalog (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- 섹션 분류
  section           TEXT NOT NULL,               -- INDUSTRIAL / CONSTRUCTION / BUILDING
                                                 -- 복수 적용 시 별도 레코드로 각각 등록

  -- 원천 정보
  input_source      TEXT NOT NULL,               -- KSIC / PROCESS / EQUIPMENT / FACILITY /
                                                 --   MATERIAL / HAZARD / NUMERIC / BOOLEAN / SPECIAL_CASE
  input_code        TEXT,                        -- 원천 코드 (KSIC: C20, 설비: PRESSURE_VESSEL 등)
  input_name        TEXT NOT NULL,               -- 한국어 명칭 (화학물질 제조업, 압력용기 등)
  input_name_en     TEXT,                        -- 영문 명칭 (선택)

  -- 패턴 정보
  input_type        TEXT NOT NULL,               -- 아래 참조
  normalized_pattern TEXT,                       -- 정규화된 표현 (has_chemical_substance=true 등)
  pattern_group     TEXT,                        -- 상위 그룹 (HAZARDOUS_MATERIAL, HEAVY_EQUIPMENT 등)

  -- 매핑 가능성
  law_linkable      BOOLEAN DEFAULT false,       -- 법령 직결 가능 여부
  law_linkable_note TEXT,                        -- 직결 불가 사유 (COMPOUND 경유 등)

  -- 상태 관리
  confidence        NUMERIC(3,2),                -- 0.00~1.00
  status            TEXT NOT NULL DEFAULT 'CANDIDATE',  -- CANDIDATE / CONFIRMED / REJECTED
  reject_reason     TEXT,

  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),

  CONSTRAINT ipc_section_check CHECK (
    section IN ('INDUSTRIAL','CONSTRUCTION','BUILDING')
  ),
  CONSTRAINT ipc_input_type_check CHECK (
    input_type IN (
      'KSIC_CODE',       -- 업종 분류코드
      'PROCESS',         -- 공정명
      'EQUIPMENT',       -- 설비 코드/종류
      'FACILITY',        -- 시설 종류
      'MATERIAL',        -- 물질 종류 (화학물질, 위험물 등)
      'HAZARD',          -- 유해인자 (has_* boolean)
      'NUMERIC',         -- 수치 조건 (인원수, 면적, 금액 등)
      'BOOLEAN',         -- 보유 여부 (has_* true/false)
      'SPECIAL_CASE'     -- 특수 케이스
    )
  ),
  CONSTRAINT ipc_status_check CHECK (
    status IN ('CANDIDATE','CONFIRMED','REJECTED')
  )
);

CREATE INDEX idx_ipc_section ON input_pattern_catalog (section);
CREATE INDEX idx_ipc_input_type ON input_pattern_catalog (input_type, status);
CREATE INDEX idx_ipc_input_code ON input_pattern_catalog (input_code);
CREATE INDEX idx_ipc_pattern_group ON input_pattern_catalog (pattern_group);
CREATE INDEX idx_ipc_law_linkable ON input_pattern_catalog (law_linkable, status);
```

### input_type 값 정의

| input_type | 설명 | 예시 |
|---|---|---|
| KSIC_CODE | 한국표준산업분류 코드 | C20(화학물질 제조), F41(건축공사) |
| PROCESS | 공정/작업 명칭 | 반응, 발파굴착, 승강기운영 |
| EQUIPMENT | 설비 종류 코드 | PRESSURE_VESSEL, CRANE, 040(정수코드) |
| FACILITY | 시설 종류 | 밀폐공간, 보일러실, 기압조절실 |
| MATERIAL | 물질 종류 | 관리대상 유해물질, 화약류, 석면 |
| HAZARD | 유해인자 boolean | has_confined_space, has_blasting |
| NUMERIC | 수치 임계값 | employee_count, building_area, construction_amount |
| BOOLEAN | 보유 여부 boolean | has_tower_crane, has_boiler |
| SPECIAL_CASE | 특수 처리 케이스 | 계절작업, 임시시설 등 |

---

## TASK-003: 법령 의미절 패턴 테이블 설계

### 테이블: `law_pattern_catalog`

**목적:** semantic_clause 58,495건을 법령 로직 패턴으로 분류.
모든 조문을 전수 분류하는 것이 아니라, 매핑 후보군에 포함되는 조문을 패턴화.

```sql
CREATE TABLE law_pattern_catalog (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- 원천 연결
  semantic_clause_id    UUID REFERENCES semantic_clause(id) ON DELETE SET NULL,
  law_id                UUID,                    -- law_master 참조
  article_id            UUID REFERENCES law_article(id) ON DELETE SET NULL,
  appendix_id           UUID REFERENCES appendix_condition(id) ON DELETE SET NULL,

  -- 섹션 후보
  section_candidates    TEXT[],                  -- ['INDUSTRIAL','CONSTRUCTION'] 등
                                                 -- COMMON 금지 — 다중 배열로 표현

  -- 조문 역할
  clause_role           TEXT NOT NULL,           -- 아래 참조

  -- 패턴 분류
  condition_pattern     TEXT,                    -- 조건 패턴 유형 (HAS_WORK / NUMERIC_GTE / EQUIPMENT_OWNED 등)
  obligation_pattern    TEXT,                    -- 의무 패턴 유형 (INSTALL / APPOINT / SUBMIT / RESTRICT 등)
  reference_pattern     TEXT,                    -- 다른 조문 참조 패턴 (DELEGATION / CROSS_REF 등)
  penalty_pattern       TEXT,                    -- 벌칙 연계 패턴

  -- 입력값 연결 가능성
  input_linkable        BOOLEAN DEFAULT false,   -- 입력값과 직결 가능 여부
  input_linkable_type   TEXT,                    -- DIRECT / THRESHOLD / COMPOUND / PROCESS / EQUIPMENT
  national_code_ref     TEXT,                    -- KSIC 코드 참조 여부 (별표 업종 포함 시)

  -- 상태 관리
  confidence            NUMERIC(3,2),
  status                TEXT NOT NULL DEFAULT 'CANDIDATE',
  reject_reason         TEXT,

  created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at            TIMESTAMPTZ NOT NULL DEFAULT now(),

  CONSTRAINT lpc_clause_role_check CHECK (
    clause_role IN (
      'IF',              -- 조건절 (발동 조건)
      'DEFINITION',      -- 정의
      'OBLIGATION',      -- 의무 (하여야 한다)
      'PROHIBITION',     -- 금지 (하여서는 아니 된다)
      'EXCEPTION',       -- 예외
      'PENALTY',         -- 벌칙
      'DELEGATION',      -- 위임 (대통령령으로 정한다)
      'REFERENCE',       -- 다른 조문 참조
      'APPENDIX_CONDITION' -- 별표/부록 조건
    )
  ),
  CONSTRAINT lpc_status_check CHECK (
    status IN ('CANDIDATE','CONFIRMED','REJECTED')
  )
);

CREATE INDEX idx_lpc_semantic_clause ON law_pattern_catalog (semantic_clause_id);
CREATE INDEX idx_lpc_section_candidates ON law_pattern_catalog USING GIN (section_candidates);
CREATE INDEX idx_lpc_clause_role ON law_pattern_catalog (clause_role, status);
CREATE INDEX idx_lpc_input_linkable ON law_pattern_catalog (input_linkable, input_linkable_type);
CREATE INDEX idx_lpc_condition_pattern ON law_pattern_catalog (condition_pattern);
```

### condition_pattern 값 정의

| condition_pattern | 설명 | 예시 조문 |
|---|---|---|
| HAS_WORK | 특정 작업 수행 시 | 밀폐공간에서 작업하는 경우 |
| HAS_EQUIPMENT | 특정 설비 보유·사용 시 | 타워크레인을 사용하는 경우 |
| HAS_MATERIAL | 특정 물질 취급 시 | 관리대상 유해물질을 취급하는 경우 |
| NUMERIC_GTE | 수치 이상 조건 | 50명 이상, 400㎡ 이상 |
| NUMERIC_RANGE | 수치 범위 조건 | 20명 이상 50명 미만 |
| EVENT_TRIGGER | 사건 발생 시 | 사고가 발생한 경우, 누출이 발생한 경우 |
| SECTOR_SPECIFIC | 업종/공사 특정 | 건설업에서, 제조업에서 |
| ALWAYS | 조건 없이 항상 | 사업주는 ... 하여야 한다 (무조건) |
| COMPOUND | 복합 조건 | A이거나 B인 경우 |

### obligation_pattern 값 정의

| obligation_pattern | 설명 |
|---|---|
| INSTALL | 설치·구비 의무 |
| APPOINT | 선임·배치 의무 |
| SUBMIT | 제출·신고 의무 |
| PREPARE | 수립·작성 의무 |
| INSPECT | 점검·검사 의무 |
| RESTRICT | 금지·제한 의무 |
| EDUCATE | 교육 의무 |
| PROVIDE | 지급·제공 의무 |
| MEASURE | 측정·평가 의무 |
| NOTIFY | 고지·공지 의무 |

---

## TASK-004: 매핑 테이블 설계

### 테이블: `input_law_pattern_mapping`

**목적:** input_pattern_catalog ↔ law_pattern_catalog 직결 연결.
이 테이블이 "입력값 → 의무" 직결 매핑의 핵심 저장소.

```sql
CREATE TABLE input_law_pattern_mapping (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- 섹션
  section               TEXT NOT NULL,           -- INDUSTRIAL / CONSTRUCTION / BUILDING

  -- 연결 대상
  input_pattern_id      UUID REFERENCES input_pattern_catalog(id) ON DELETE CASCADE,
  law_pattern_id        UUID REFERENCES law_pattern_catalog(id) ON DELETE CASCADE,
  semantic_clause_id    UUID REFERENCES semantic_clause(id) ON DELETE SET NULL,  -- 직접 참조 가능

  -- 매핑 특성
  mapping_type          TEXT NOT NULL,           -- 아래 참조
  mapping_basis         TEXT,                    -- 매핑 근거 설명 한 문장
  match_strength        NUMERIC(3,2),            -- 0.00~1.00 (매핑 강도)

  -- 상태 관리
  status                TEXT NOT NULL DEFAULT 'CANDIDATE',
  review_result         TEXT,                    -- 검증 결과 메모
  reviewed_by           TEXT,                    -- 검토자 (human / llm / auto)
  reviewed_at           TIMESTAMPTZ,

  created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at            TIMESTAMPTZ NOT NULL DEFAULT now(),

  CONSTRAINT ilpm_section_check CHECK (
    section IN ('INDUSTRIAL','CONSTRUCTION','BUILDING')
  ),
  CONSTRAINT ilpm_mapping_type_check CHECK (
    mapping_type IN (
      'EXACT',              -- 입력값이 조문 조건과 정확히 일치
      'PARTIAL',            -- 부분 일치 (조건 중 일부)
      'POSSIBLE',           -- 가능성 있음 (추가 검토 필요)
      'CODE_MATCH',         -- KSIC 코드 일치
      'TEXT_PATTERN_MATCH', -- 조문 텍스트 패턴 일치
      'NUMERIC_MATCH',      -- 수치 조건 일치
      'APPENDIX_MATCH'      -- 별표 조건 일치
    )
  ),
  CONSTRAINT ilpm_status_check CHECK (
    status IN ('CANDIDATE','CONFIRMED','REJECTED')
  )
);

CREATE INDEX idx_ilpm_section ON input_law_pattern_mapping (section, status);
CREATE INDEX idx_ilpm_input_pattern ON input_law_pattern_mapping (input_pattern_id);
CREATE INDEX idx_ilpm_law_pattern ON input_law_pattern_mapping (law_pattern_id);
CREATE INDEX idx_ilpm_semantic_clause ON input_law_pattern_mapping (semantic_clause_id);
CREATE INDEX idx_ilpm_mapping_type ON input_law_pattern_mapping (mapping_type, status);
CREATE INDEX idx_ilpm_confirmed ON input_law_pattern_mapping (status, match_strength)
  WHERE status = 'CONFIRMED';
```

---

## TASK-005: 후보군 운영 원칙

### 상태 전이 흐름

```
CANDIDATE (기본값)
    │
    ├── 검증 통과 → CONFIRMED
    └── 검증 탈락 → REJECTED

CONFIRMED 조건:
  - 입력값과 법령 의미절이 한 문장으로 설명 가능
  - 섹션이 명확히 일치
  - 다른 입력값과 충돌 없음

CANDIDATE 유지 조건:
  - 맞을 가능성 있으나 조건 세부 미검증
  - 법령 스코프 애매
  - 섹션은 맞으나 COMPOUND 가능성 존재

REJECTED 조건:
  - 섹션 불일치
  - 입력값과 법령 무관
  - TAI Safe 1차 서비스 범위 외
```

### 단계별 투입 전략

```
1단계: 현재 condition_mapping_candidate 77건
       → input_law_pattern_mapping에 CONFIRMED으로 이전
       → mapping_type = 'EXACT' / 'NUMERIC_MATCH' / 'APPENDIX_MATCH'

2단계: HARVEST-001 발굴 15건 (CONFIRMED 4건 + PENDING 11건)
       → input_law_pattern_mapping에 CANDIDATE로 등록
       → REVIEW 통과 후 CONFIRMED 승격

3단계: KSIC × 법령 교차 매핑 (대규모 배치)
       → input_pattern_catalog × law_pattern_catalog 교차
       → CODE_MATCH / TEXT_PATTERN_MATCH 타입으로 CANDIDATE 등록
       → 검토 후 CONFIRMED

4단계: 공정명·설비코드 × 법령 교차
       → PROCESS / EQUIPMENT 타입
```

---

## TASK-006: condition_mapping_candidate 위치 재정의

### 변경 전 (현재)

```
입력값 → condition_mapping_candidate → 의무 출력
          (직접 매핑 저장소)
```

### 변경 후 (신규 구조)

```
input_pattern_catalog
        ↓
law_pattern_catalog
        ↓
input_law_pattern_mapping   ← 후보·검증 단계 저장소
        ↓
    [검증 완료]
        ↓
condition_mapping_candidate ← 최종 운영 매핑 저장소
        ↓
    의무후보 출력 (체크엔진)
```

**condition_mapping_candidate는 폐기하지 않는다.**
역할을 "최종 운영 매핑 저장소"로 격상.
현재 77건은 이미 검증 완료된 CONFIRMED이므로 그대로 유지.

신규 매핑은:
1. input_law_pattern_mapping에 CANDIDATE로 등록
2. REVIEW 통과 후 CONFIRMED 승격
3. APPLY 시 condition_mapping_candidate에 INSERT

---

## 현재 데이터 기반 입력값 규모 추정

| 입력 원천 | 현재 DB 규모 | 전체 규모 추정 |
|---|---|---|
| KSIC 코드 (현재 DB) | 38개 코드 | 1,228개 (KSIC 세분류 전체) |
| 공정명 (factory_process) | 32개 | 100~200개 (확장 시) |
| 설비코드 (equipment_assets) | 40종 (정수 36 + 의미 4) | 100~150개 (확장 시) |
| has_* boolean | 9개 | 9개 (현재 완성) |
| 수치 필드 (numeric) | 8개 | 8개 (현재) |
| **소계** | **약 137개** | **약 1,600개** |

> 지시서의 "4,000여 개"는 KSIC 세분류 전체(약 1,228개) + 공정 × 설비 조합 확장 시 도달 가능한 규모.
> 현재 DB 기준으로는 약 137개의 고유 입력값이 식별된다.

---

## 다음 단계

```
WO-PATTERN-SCOPE-001 (현재) — 완료
      ↓
WO-PATTERN-INVENTORY-001
  섹션별 입력값 전수 인벤토리
  input_pattern_catalog 초기 적재
  KSIC 전체 × 섹션 분류
  공정명 × 섹션 분류
  설비코드 × 섹션 분류
      ↓
WO-PATTERN-LAW-001
  law_pattern_catalog 초기 적재
  semantic_clause 5만건 → clause_role 분류
  condition_pattern / obligation_pattern 부여
      ↓
WO-PATTERN-MAPPING-001
  input_law_pattern_mapping 교차 매핑
  KSIC × 법령 / 공정 × 법령 / 설비 × 법령
```

---

*WO-PATTERN-SCOPE-001 완료.*
*3섹션 확정 / 테이블 3종 설계 완료 / condition_mapping_candidate 위치 재정의.*
*COMMON 없음. 공용 법령은 다중 섹션 배열로 표현.*
