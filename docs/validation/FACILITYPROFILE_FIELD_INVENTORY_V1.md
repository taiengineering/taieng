# FACILITYPROFILE FIELD INVENTORY V1
# WO-FACILITYPROFILE-FIELD-INVENTORY-001

**작성일**: 2026-06-20
**출처**: services/facility_profile_service.py (build_facility_profile, 코드 실측)
**성격**: 인벤토리 표만. 판단/해석/결론 없음.

---

## FacilityProfile Field Inventory (전체)

### 최상위 필드

| field | type | required | default | description |
|---|---|---|---|---|
| factory_id | str | YES | 없음 (row["id"] 필수) | factories.id |
| sector | str | NO | "INDUSTRIAL" (null시) | 섹터 |
| sector_provenance | str | 자동 | "INPUT"/"DEFAULT" | sector 출처 |
| ksic_code | str/None | NO | None | row.ksic_code |
| profile_version | int | 자동 | 1 | 프로파일 버전 |
| provenance | dict | 자동 | {input/inferred/default_fields} | 출처 요약 |

### workforce (TriValue: state/value/provenance)

| field | type | required | default | description |
|---|---|---|---|---|
| workforce.regular_workers | TriValue | NO | UNKNOWN(null시) | row.employee_count |
| workforce.subcontract_workers | TriValue | NO | UNKNOWN(null시) | row.subcontractor_worker_count |
| workforce.total_workers | TriValue | NO | UNKNOWN(null시) | row.total_worker_count_calc |

### building (TriValue)

| field | type | required | default | description |
|---|---|---|---|---|
| building.use_code | TriValue | NO | UNKNOWN(null시) | row.building_use_code |
| building.floor_area | TriValue | NO | UNKNOWN(null시) | row.building_area |
| building.floor_count | TriValue | NO | UNKNOWN(null시) | row.floor_count |

### metrics (TriValue)

| field | type | required | default | description |
|---|---|---|---|---|
| metrics.construction_amount | TriValue | NO | UNKNOWN(null시) | row.construction_amount |
| metrics.electrical_kw | TriValue | NO | UNKNOWN(null시) | row.electrical_capacity_kw |
| metrics.gas_capacity | TriValue | NO | UNKNOWN(null시) | row.gas_capacity_m3 우선, 없으면 gas_capacity_kg |

---

## TriValue 구조 (각 TriValue 필드의 내부)

| sub-field | type | required | default | description |
|---|---|---|---|---|
| state | str | 자동 | "PRESENT"/"UNKNOWN" | null→UNKNOWN, 값→PRESENT |
| value | any/None | 자동 | None(UNKNOWN시) | 원본 값 (UNKNOWN시 None) |
| provenance | str | 자동 | "INPUT" | 출처 (INPUT/INFERRED/DEFAULT) |

---

## profile_to_db_row 출력 컬럼 (facility_profiles 테이블 적재용)

```
참고: build_facility_profile의 필드가 DB 행으로 평탄화될 때 컬럼:
  factory_id, profile_version, sector, ksic_code,
  regular_workers_{state,value,provenance},
  subcontract_workers_{state,value,provenance},
  total_workers_{state,value,provenance},
  use_code_{state,value,provenance},
  floor_area_{state,value,provenance},
  floor_count_{state,value,provenance},
  construction_amount_{state,value,provenance},
  electrical_kw_{state,value,provenance},
  gas_capacity_{state,value,provenance},
  input_fields, inferred_fields, default_fields,
  profile_snapshot (JSON 전체)
```

---

## 수집 메타

```
FacilityProfile이 factories row에서 읽는 원본 컬럼 (전수):
  id, sector, ksic_code,
  employee_count, subcontractor_worker_count, total_worker_count_calc,
  building_use_code, building_area, floor_count,
  construction_amount, electrical_capacity_kw,
  gas_capacity_m3, gas_capacity_kg

판정 차원 그룹: workforce(3) + building(3) + metrics(3) = 9개 TriValue
  + sector + ksic_code = 11개 입력 차원.

코드 명시 원칙(파일 docstring):
  UNKNOWN = state 전용. value에 UNKNOWN/0/false 저장 금지.
  null → UNKNOWN, 값 있음 → PRESENT.
  factories 수정 금지. Check Engine/Track A/B 연결 금지.
```

---

## 성공 기준 점검

```
FacilityProfile 전체 필드 100% 수집 → ✅ (build_facility_profile 전수)
누락 필드 0건 → ✅ (코드의 모든 필드 표에 포함)
추정 필드 0건 → ✅ (코드에 있는 것만, 추정 없음)
```

---

## 원칙 준수

```
엔진 좁다/넓다 판단 안 함 ✅
VR 비교 안 함 ✅
조건(condition) 분석 안 함 ✅
UI 분석 안 함 ✅
Check Engine 분석 안 함 ✅
개선안/결론 작성 안 함 ✅
인벤토리 표만 ✅
```

---

(판단 문장 없음. 인벤토리 표만 제출.)
