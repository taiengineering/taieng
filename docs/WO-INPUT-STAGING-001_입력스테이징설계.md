# WO-INPUT-STAGING-001
# 입력 데이터 전수 스테이징 설계

**작성일:** 2026-06-24 | **상태:** 설계 완료 / 테이블 생성·적재 미실행
**선행:** WO-INPUT-CODE-ARCHITECTURE-001 / WO-INPUT-CODE-AUDIT-001
**STAGE-OBJECTIVE 검증:** Q1(입력 원본 수집) ✅ / Q2(패턴 발견 전 단계) ✅ / Q3(매핑 아님) ✅ / Q4(원칙 준수) ✅
**금지:** SECTION 확정 / 패턴 정의 / 법령 매핑 / UNUSED 판정 / ORPHAN 판정 / 엔진 수정

> 핵심 원칙: 지금은 판단하지 않는다. 지금은 모은다. 판단은 스테이징 완료 후 한다.

---

## 산출물 A: INPUT_SOURCE_TABLE_MAP

| source_table | 입력원천 여부 | 코드 컬럼 | 명칭 컬럼 | 계층 컬럼 | 섹션힌트 컬럼 | row 수 | 적재 대상 |
|---|---|---|---|---|---|---|---|
| **ksic_process_map** | ✅ | lv1~lv4_code, process_id | lv1~lv4_name, process_lv1~4 | KSIC 4단계 + 공정 4단계 | industry_code_full | 6,957 | ✅ |
| **process_equipment_map** | ✅ | process_id, lv1~lv4_code | facility_name_std, process_lv1~4 | 공정 4단계 + 설비 | source_facility_category | 187,319 | ✅ |
| **equipment_assets** | ✅ | equipment_type_code, asset_code | asset_name | equipment_category | ksic_code | 3,284 | ✅ |
| **factory_process** | ✅ | process_id | process_lv1~4, process_name_manual | 공정 4단계 | (없음) | 476 | ✅ |
| **factories** | ✅ | ksic_code | name | (없음) | sector | 5,812 | ✅ (has_*/numeric만) |
| **equipment_model_master** | ✅ (원천) | equipment_std, model_name | product_name, manufacturer | equipment_lv2 | (없음) | **0** | ❌ (데이터 없음) |

### 적재 대상 확정: 5개 테이블

```
ksic_process_map        6,957건   ← KSIC + 공정 원천
process_equipment_map   187,319건 ← 공정 + 설비 원천
equipment_assets        3,284건   ← 설비 인스턴스
factory_process         476건     ← 사업장 공정
factories               5,812건   ← has_* + numeric 필드 추출
```

**equipment_model_master는 원천이나 0건 — 적재 제외 (향후 데이터 입력 시 재포함).**

---

## 산출물 B: input_staging_catalog DDL

```sql
CREATE TABLE input_staging_catalog (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- 원천 추적
  source_table        TEXT NOT NULL,           -- ksic_process_map / process_equipment_map 등
  source_pk           TEXT,                    -- 원본 레코드 PK (uuid 또는 코드)
  source_column_group TEXT,                    -- KSIC / PROCESS / EQUIPMENT / FACILITY / NUMERIC / BOOLEAN

  -- 원형 보존 (raw — 가공 없음)
  raw_code            TEXT,                    -- 원본 코드
  raw_name            TEXT,                    -- 원본 명칭
  raw_description     TEXT,                    -- 원본 설명
  raw_category        TEXT,                    -- 원본 분류

  -- 계층 원형 보존
  raw_level_1         TEXT,
  raw_level_2         TEXT,
  raw_level_3         TEXT,
  raw_level_4         TEXT,
  raw_parent_code     TEXT,

  -- 메타데이터 (원본 전체 보존)
  raw_metadata        JSONB,                   -- 원본 행의 추가 정보 전체

  -- 수집 추적
  collection_batch    TEXT NOT NULL,           -- 적재 배치 식별자 (예: STAGING-2026-06-24)
  collected_at        TIMESTAMPTZ NOT NULL DEFAULT now()

  -- 주의: section, pattern, status 컬럼 없음. 아직 판단 단계 아님.
);

-- 원천 추적 인덱스
CREATE INDEX idx_isc_source_table ON input_staging_catalog (source_table);
CREATE INDEX idx_isc_column_group ON input_staging_catalog (source_column_group);
CREATE INDEX idx_isc_raw_code ON input_staging_catalog (raw_code);
CREATE INDEX idx_isc_raw_name ON input_staging_catalog (raw_name);
CREATE INDEX idx_isc_batch ON input_staging_catalog (collection_batch);
CREATE INDEX idx_isc_metadata ON input_staging_catalog USING GIN (raw_metadata);
```

**설계 의도:**
- `section` / `pattern` / `status` 컬럼 **없음** — 판단 단계 아님
- `raw_*` 접두어로 "가공 안 된 원형"임을 명시
- `raw_metadata` JSONB로 원본 행 전체 보존 (정보 손실 0)
- 중복 제거 안 함 — UNIQUE 제약 없음

---

## 산출물 C: 원천별 적재 SQL 초안

### C-1. ksic_process_map → KSIC 코드 (lv1~lv4)

```sql
-- KSIC 계층 코드 적재 (공정과 분리하여 KSIC 자체만)
INSERT INTO input_staging_catalog (
  source_table, source_pk, source_column_group,
  raw_code, raw_name, raw_level_1, raw_level_2, raw_level_3, raw_level_4,
  raw_metadata, collection_batch
)
SELECT DISTINCT
  'ksic_process_map', industry_code_full, 'KSIC',
  industry_code_full, industry_name_full,
  lv1_code || ':' || COALESCE(lv1_name,''),
  lv2_code || ':' || COALESCE(lv2_name,''),
  lv3_code || ':' || COALESCE(lv3_name,''),
  lv4_code || ':' || COALESCE(lv4_name,''),
  jsonb_build_object(
    'lv1_code', lv1_code, 'lv1_name', lv1_name,
    'lv2_code', lv2_code, 'lv2_name', lv2_name,
    'lv3_code', lv3_code, 'lv3_name', lv3_name,
    'lv4_code', lv4_code, 'lv4_name', lv4_name,
    'ksic_revision', ksic_revision,
    'industry_path_ko', industry_path_ko
  ),
  'STAGING-2026-06-24'
FROM ksic_process_map
WHERE industry_code_full IS NOT NULL;
-- 예상: 501 distinct KSIC 코드
```

### C-2. ksic_process_map → 공정 코드 (process)

```sql
INSERT INTO input_staging_catalog (
  source_table, source_pk, source_column_group,
  raw_code, raw_name, raw_level_1, raw_level_2, raw_level_3, raw_level_4,
  raw_metadata, collection_batch
)
SELECT DISTINCT
  'ksic_process_map', process_id, 'PROCESS',
  process_id, process_lv1,
  process_lv1, process_lv2, process_lv3, process_lv4,
  jsonb_build_object(
    'process_path', process_path,
    'process_source', process_source,
    'mapping_basis', mapping_basis,
    'linked_ksic', industry_code_full
  ),
  'STAGING-2026-06-24'
FROM ksic_process_map
WHERE process_id IS NOT NULL;
-- 예상: 3,378 distinct process_id
```

### C-3. process_equipment_map → 설비 (facility_name_std)

```sql
INSERT INTO input_staging_catalog (
  source_table, source_pk, source_column_group,
  raw_code, raw_name, raw_category, raw_parent_code,
  raw_metadata, collection_batch
)
SELECT DISTINCT
  'process_equipment_map',
  facility_name_std, 'EQUIPMENT',
  facility_name_std, facility_name_std,
  source_facility_category, process_id,
  jsonb_build_object(
    'source_facility_category', source_facility_category,
    'equipment_role', equipment_role,
    'linked_process', process_id,
    'industry_focus', industry_focus
  ),
  'STAGING-2026-06-24'
FROM process_equipment_map
WHERE facility_name_std IS NOT NULL;
-- 예상: 446 distinct facility_name_std (단, 공정 연결 보존 시 더 많음)
-- 주의: DISTINCT facility_name_std만 하면 446, 공정-설비 조합 보존 시 136,127
-- 적재 전략 결정 필요 (아래 D 참조)
```

### C-4. equipment_assets → 설비 인스턴스 + 유형코드

```sql
INSERT INTO input_staging_catalog (
  source_table, source_pk, source_column_group,
  raw_code, raw_name, raw_category,
  raw_metadata, collection_batch
)
SELECT
  'equipment_assets', id::text, 'EQUIPMENT',
  equipment_type_code, asset_name, equipment_category,
  jsonb_build_object(
    'asset_code', asset_code,
    'equipment_type_code', equipment_type_code,
    'capacity_value', capacity_value,
    'capacity_unit', capacity_unit,
    'ksic_code', ksic_code
  ),
  'STAGING-2026-06-24'
FROM equipment_assets;
-- 예상: 3,284 (전 row — 인스턴스라 중복 제거 안 함)
```

### C-5. factory_process → 사업장 공정

```sql
INSERT INTO input_staging_catalog (
  source_table, source_pk, source_column_group,
  raw_code, raw_name, raw_level_1, raw_level_2, raw_level_3, raw_level_4,
  raw_metadata, collection_batch
)
SELECT
  'factory_process', id::text, 'PROCESS',
  process_id, COALESCE(process_name_manual, process_lv1),
  process_lv1, process_lv2, process_lv3, process_lv4,
  jsonb_build_object(
    'process_path', process_path,
    'source', source,
    'is_primary', is_primary,
    'factory_id', factory_id
  ),
  'STAGING-2026-06-24'
FROM factory_process;
-- 예상: 476
```

### C-6. factories → has_* boolean + numeric 필드

```sql
-- has_* 필드를 행으로 펼쳐서 적재 (입력값 카탈로그이므로 필드 자체를 수집)
INSERT INTO input_staging_catalog (
  source_table, source_column_group, raw_code, raw_name,
  raw_metadata, collection_batch
)
SELECT 'factories', 'BOOLEAN', col, col, '{}'::jsonb, 'STAGING-2026-06-24'
FROM (VALUES
  ('has_confined_space'),('has_blasting'),('has_chemical_substance'),
  ('has_high_pressure_gas'),('has_tower_crane'),('has_boiler'),
  ('has_asbestos_demo'),('has_diving'),('has_safety_manager')
) AS t(col)
UNION ALL
SELECT 'factories', 'NUMERIC', col, col, '{}'::jsonb, 'STAGING-2026-06-24'
FROM (VALUES
  ('employee_count'),('building_area'),('electrical_capacity_kw'),
  ('transformer_capacity_kva'),('gas_capacity_m3'),('boiler_capacity_kw'),
  ('construction_amount'),('elevator_count'),('occupant_capacity'),
  ('contractor_count')
) AS t(col);
-- 예상: 9 boolean + 10 numeric = 19 (필드 정의 단위)
```

---

## 산출물 D: 적재 후 row count 검증표

### 적재 전략 결정 필요 사항

설비(C-3)는 두 가지 적재 방식이 가능:

| 방식 | 적재 건수 | 장점 | 단점 |
|---|---|---|---|
| A: DISTINCT facility_name_std | 446 | 설비 카탈로그 단위 | 공정-설비 관계 손실 |
| B: 공정-설비 조합 보존 | 136,127 | 관계 보존 | 대용량 |

**권고: A 방식 (446)으로 설비 카탈로그 적재 + 공정-설비 관계는 process_equipment_map 원본 유지로 추적.**
이번 WO는 "입력값 수집"이므로 설비 종류 446개가 입력 카탈로그 단위로 적합.

### 예상 적재 검증표 (A 방식 기준)

| source_table | column_group | 예상 건수 | 검증 기준 |
|---|---|---|---|
| ksic_process_map | KSIC | 501 | DISTINCT industry_code_full |
| ksic_process_map | PROCESS | 3,378 | DISTINCT process_id |
| process_equipment_map | EQUIPMENT | 446 | DISTINCT facility_name_std |
| equipment_assets | EQUIPMENT | 3,284 | 전 row (인스턴스) |
| factory_process | PROCESS | 476 | 전 row |
| factories | BOOLEAN | 9 | 필드 정의 |
| factories | NUMERIC | 10 | 필드 정의 |
| **합계** | | **약 8,104** | |

### 적재 후 검증 쿼리 (APPLY 시 실행)

```sql
-- 1. source_table별 row 보존 확인
SELECT source_table, source_column_group, COUNT(*) AS cnt
FROM input_staging_catalog
GROUP BY source_table, source_column_group
ORDER BY source_table, source_column_group;

-- 2. 코드 컬럼 보존 확인 (raw_code NULL 비율)
SELECT source_column_group,
  COUNT(*) AS total,
  COUNT(raw_code) AS has_code,
  COUNT(raw_name) AS has_name
FROM input_staging_catalog
GROUP BY source_column_group;

-- 3. 계층 구조 보존 확인 (KSIC/PROCESS)
SELECT source_column_group,
  COUNT(raw_level_1) AS lv1, COUNT(raw_level_2) AS lv2,
  COUNT(raw_level_3) AS lv3, COUNT(raw_level_4) AS lv4
FROM input_staging_catalog
WHERE source_column_group IN ('KSIC','PROCESS')
GROUP BY source_column_group;

-- 4. raw_metadata 보존 확인
SELECT source_table, COUNT(*) FILTER (WHERE raw_metadata != '{}'::jsonb) AS with_meta
FROM input_staging_catalog
GROUP BY source_table;
```

---

## TASK-004 준수: 중복 제거 금지

```
이번 단계에서 중복 제거하지 않는다.

- equipment_assets의 asset_name이 process_equipment_map의 facility_name_std와
  겹쳐도 둘 다 보존
- factory_process의 process_id가 ksic_process_map의 process_id와
  겹쳐도 둘 다 보존
- 동의어·상하위 관계 판단은 패턴 발견 단계(이후 WO)에서 수행

중복은 source_table로 구분되므로 추적 가능.
```

---

## 성공 기준 답변

> 현재 입력될 수 있는 모든 입력 데이터가
> 판단 없이, 원형 그대로, 하나의 스테이징 구조에 모이는가?

```
✅ 입력 원천 5개 테이블 확정 (+equipment_model_master는 0건 제외)
✅ input_staging_catalog DDL 설계 (section/pattern/status 없음)
✅ 원천별 적재 SQL 초안 6종 작성
✅ raw_metadata JSONB로 원본 정보 100% 보존
✅ 중복 제거 안 함 — source_table로 구분
✅ 예상 적재 약 8,104건
```

---

## 다음 단계

```
WO-INPUT-STAGING-001 (현재 — 설계) — 완료
      ↓
WO-INPUT-STAGING-001-APPLY
  input_staging_catalog 테이블 생성 (apply_migration)
  6종 적재 SQL 실행
  검증 쿼리 4종 실행
      ↓
WO-LAW-STAGING-001
  법령 원본 전수 스테이징 (semantic_clause 5만건)
      ↓
WO-PATTERN-DISCOVERY-001
  입력 스테이징 + 법령 스테이징 → 패턴 발견 시작
```

---

*WO-INPUT-STAGING-001 완료 (설계). 테이블 생성·적재 미실행.*
*입력 원천 5개 / 예상 적재 8,104건 / 판단 컬럼 없음 / 중복 제거 없음.*
