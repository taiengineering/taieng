# WO-INPUT-BOUNDARY-001
# 입력세계 경계 확정서

**작성일:** 2026-06-24 | **상태:** 확정 (입력원천 분류 전용)
**선행:** WO-CONSUMER-INPUT-AUDIT-001
**금지:** 패턴 발견 / 매핑 / 정규화 / 법령 연결
**목적:** "법령엔진이 실제 사용하는 입력값은 무엇인가?"를 확정한다.

---

## 핵심 발견: 입력 필드가 98개로 확장 + 건축물대장 API 발견

```
이전 WO에서 본 "활성 49개"는 일부였다.
diagnosis_input_fields 전체 distinct field_code = 98개

그리고 결정적 발견:
  auto_source = 'building_register' (건축물대장 API) 6개 필드
  → 소비자가 입력하지 않고 주소 입력 시 자동 생성되는 입력원천

→ Boundary가 아직 안 닫혀 있었다. API 입력원천이 새로 발견됨.
```

---

## 산출물 A: 입력원천 3분류

### DIRECT_INPUT (소비자 직접 입력) — 92개

소비자가 화면에서 직접 입력하는 필드.

```
boolean (~52개): has_* 시리즈
  has_confined_space, has_chemical_substance, has_tower_crane,
  has_blasting, has_diving, has_asbestos_demo, has_boiler,
  has_press, has_crane, has_forklift, has_welding, has_painting,
  has_plating, has_casting, has_heat_treatment, has_high_place_work,
  has_excavation, has_scaffold, has_steel_frame, has_pile_work,
  has_demolition, has_concrete_work, has_temp_electric,
  has_sprinkler, has_fire_hydrant, has_smoke_control,
  has_emergency_broadcast, has_emergency_gen, has_gas,
  has_chemical, has_hazmat_storage, has_water_tank,
  has_pressure_vessel, has_gondola, has_grinding, has_injection,
  has_conveyor, has_rolling, has_cooling_tower, has_septic_tank,
  has_mech_parking, has_oil_storage, has_radiation, has_dust_work,
  has_noise_work, has_elevator, has_subcontractor, has_central_hvac,
  is_complex_building, is_energy_intensive, is_multi_use, has_safety_manager

number (~33개):
  worker_count, total_floor_area, project_amount, electric_capacity,
  gas_capacity_kg, gas_capacity_m3, elevator_count, annual_energy_toe,
  boiler_capacity_kw, transformer_capacity_kva, building_grade,
  crane_count, emergency_gen_kw, escalator_count, excavation_depth,
  forklift_count, max_work_height, mech_parking_count, process_count,
  project_duration, septic_tank_ton, subcontractor_count,
  tower_crane_count, underground_area, water_tank_ton,
  mech_parking_count, ...

select (~6개):
  ksic_major, ksic_sub, construction_type, operation_shift,
  equipment_inspection_status

multi_select (1개): multi_use_type

table (4개): process_list, equipment_list, process_worker_data, subcontractor

text (2개): address, project_address
```

### DERIVED_INPUT / EXTERNAL_SOURCE (건축물대장 API 자동 생성) — 6개

`auto_source = 'building_register'` — 주소 입력 시 건축물대장 API에서 자동 생성.

| field_code | field_name | 타입 | API 생성 |
|---|---|---|---|
| total_floor_area | 연면적 | number | 건축물대장 |
| floor_count | 지상 층수 | number | 건축물대장 |
| basement_count | 지하 층수 | number | 건축물대장 |
| building_use_type | 건물 용도 | select | 건축물대장 |
| built_year | 건축연도 | number | 건축물대장 |
| main_structure | 주구조 | select | 건축물대장 |

**파생 입력 (API 결과로 자동 판정):**
```
has_asbestos (석면 사용 여부)
  → built_year 2009년 이전이면 자동 경고
  → DERIVED_INPUT (API 직접 아님, API 결과 가공)
```

### EXTERNAL_SOURCE (외부 코드 표준)

```
KSIC 표준코드        (industry_master / ksic_process_map)
KCSC 건설표준코드     (kcsc_work_master / kcsc_process_master)
건축물대장 API        (building_register — 6개 필드 생성)
위험물 지정수량 기준   (master_dangerous_goods)
고압가스 기준         (master_highpressure_gas)
안전인증 기준         (master_safety_certification)
전기설비 KC인증       (master_products_elec)
```

---

## 산출물 B: SaaS 입력화면 역추적 (입력방식별)

| 입력방식 | distinct 필드 수 | 대표 예시 |
|---|---|---|
| BOOLEAN | ~52 | has_* 유무 질문 |
| NUMBER | ~33 | 면적·용량·인원·금액·대수·깊이·높이 |
| SELECT | ~6 | 업종·용도·공사유형·교대제 |
| MULTI_SELECT | 1 | 다중이용 업종 |
| TABLE | 4 | 공정·설비·협력업체·공정별작업자 |
| TEXT | 2 | 주소 |
| API_AUTO | 6 | 건축물대장 자동생성 |

---

## 산출물 C: 건축물대장 API 영향도

```
주소 입력 (address / project_address)
      ↓
건축물대장 API (building_register)
      ↓
자동 생성 6개 필드:
  연면적 (total_floor_area)
  지상 층수 (floor_count)
  지하 층수 (basement_count)
  건물 용도 (building_use_type)
  건축연도 (built_year)
  주구조 (main_structure)
      ↓
파생 판정:
  석면 사용 여부 (has_asbestos) ← built_year 2009 이전
```

**중요:** 연면적(total_floor_area)은 소비자 직접 입력이 아니라 **API 자동 생성**.
이전 WO에서 "소비자 직접 입력"으로 분류했던 것이 사실은 API 입력원천.

---

## 산출물 D: 입력변수 총량 산정 (중복 없는 목록)

| 분류 | distinct 수 |
|---|---|
| A. 소비자 직접 입력 (DIRECT) | 92 |
| B. 건축물대장 API 자동 생성 | 6 |
| C. 코드 선택지 풀 (OPTION_POOL) | 8,754 |
| **입력 필드 총량 (A+B)** | **98** |
| **선택지 포함 총량 (A+B+C)** | **8,852** |

**핵심:** 입력 필드는 98개 (활성 49 + 비활성 49).
이전에 "49개"로 본 것은 is_active=true 필터 결과.
**실제 정의된 입력 세계는 98개 필드.**

---

## 산출물 E: 입력세계 Boundary 선언

| 입력원천 | 분류 | 판정 | 비고 |
|---|---|---|---|
| **DIRECT_INPUT** | 소비자 직접 입력 92개 | **포함** | 법령엔진 핵심 입력 |
| **EXTERNAL_SOURCE (건축물대장 API)** | API 자동 6개 | **포함** | 주소→자동생성 |
| **DERIVED_INPUT** | has_asbestos 등 파생 | **포함** | API 결과 가공 |
| **OPTION_POOL** | 선택지 풀 8,754 | **포함** | select/table 참조용 |
| **CODE_MASTER** | KSIC/KCSC 표준 | **포함** | 선택지 원천 |
| **RELATION** | 공정-설비 관계 198,278 | **포함** | 입력 조합 추적 |
| **INSTANCE** | equipment_assets 등 사업장 실제 | **보류** | 진단 시점엔 미입력 |
| master_safety_manager_criteria | 안전관리자 기준 19 | **제외** | 법령측 (입력 아님) |
| master_legal_inspection_target | 법정점검 13 | **제외** | 법령측 |
| industry_master | KSIC 중복 501 | **보류** | ksic_process_map과 중복 확인 필요 |
| master_fields | 필드 정의 118 | **보류** | diagnosis_input_fields와 중복 확인 필요 |

---

## 성공 기준 답변

> "새로운 입력원천이 또 나올 수 있는가?"

```
이번 WO에서 새 입력원천 1개 발견됨:
  건축물대장 API (building_register) — 6개 필드 자동생성

이것을 포함하면:
  소비자 직접 입력 (92)
  + API 자동 생성 (6)
  + 선택지 풀 (8,754)
  = 입력세계 닫힘

남은 불확실성:
  - industry_master / master_fields 중복 여부 (보류 2건)
  - 추가 외부 API 존재 여부 (주소 외 다른 API?)

→ 건축물대장 API 외 다른 외부 API가 없다면 Boundary 닫힘.
→ 보류 2건은 중복 확인이므로 신규 원천 아님.
```

### Boundary 닫힘 조건

```
✅ 소비자 입력 98개 필드 전수 확보
✅ 건축물대장 API 6개 식별
✅ 선택지 풀 8,754 확보
✅ 관계망 198,278 확보
⚠️ industry_master / master_fields 중복 확인 필요 (보류, 신규 아님)

→ 외부 API가 건축물대장 1개뿐이라면 Boundary 닫힘 선언 가능.
```

---

## 발견사항 종합

### 발견 1: 입력 필드 49 → 98개 (2배)

```
is_active=true: 49개 (현재 노출)
전체 정의:      98개 (비활성 49 포함)

비활성 필드 예시:
  has_press, has_crane, has_forklift, has_welding, has_plating,
  has_casting, has_grinding, has_injection, has_rolling,
  crane_count, forklift_count, max_work_height, excavation_depth ...

→ 입력 세계는 설계상 98개. 현재 절반만 활성화.
→ 비활성 49개는 향후 확장 대상 (또는 폐기 대상).
```

### 발견 2: 건축물대장 API = 숨은 입력원천

```
total_floor_area(연면적)을 "소비자 직접 입력"으로 봤던 것이 오류.
실제로는 주소 입력 → 건축물대장 API 자동 생성.

→ 법령 매핑 시 "이 입력값의 출처가 소비자인가 API인가"가 중요.
→ API 값은 신뢰도 높음 (공공데이터), 소비자 입력은 검증 필요.
```

### 발견 3: 입력 필드명이 has_* 중심으로 대폭 확장

```
factories 테이블: has_* 9개
diagnosis_input_fields: has_* 52개

신규 has_*:
  has_press, has_crane, has_forklift, has_welding, has_plating,
  has_grinding, has_conveyor, has_gondola, has_pressure_vessel,
  has_scaffold, has_pile_work, has_excavation, has_demolition ...

→ 이전 INPUT-MODEL-AUDIT에서 논의한 has_pressure_vessel,
  has_pile_driver가 이미 입력 필드에 존재했음(has_pressure_vessel, has_pile_work).
→ has_high_pressure_gas 분리 논의가 이미 필드 레벨에서 해결되어 있었음.
```

---

## 다음 단계

```
WO-INPUT-BOUNDARY-001 (현재) — 완료
      ↓
WO-INPUT-SOURCE-VERIFY-001 (권고)
  industry_master / master_fields 중복 확인
  추가 외부 API 존재 여부 최종 확인
  → Boundary 완전 닫힘 선언
      ↓
WO-INPUT-PATTERN-DISCOVERY-001
  98개 입력 필드 기준 패턴 발견
  (Boundary 닫힌 후 시작)
```

---

*WO-INPUT-BOUNDARY-001 완료.*
*입력원천: 소비자 직접 92 + 건축물대장 API 6 + 선택지풀 8,754.*
*핵심 발견: 건축물대장 API 입력원천 / 입력필드 실제 98개 / has_* 52개로 확장.*
*Boundary 거의 닫힘 — industry_master/master_fields 중복 확인만 남음.*
