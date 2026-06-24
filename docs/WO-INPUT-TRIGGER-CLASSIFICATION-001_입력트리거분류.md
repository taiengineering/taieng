# WO-INPUT-TRIGGER-CLASSIFICATION-001
# 입력필드 → Trigger 계열 분류

**작성일:** 2026-06-24 | **상태:** 완료 (분류 전용)
**선행:** WO-PATTERN-VALIDATION-001
**금지:** semantic_clause 검색 / condition_mapping 생성 / 후보군 생성 / 법령 검증 / appendix 검증
**목적:** 98개 입력필드를 입력필드 → Trigger 계열로 배치. 법령 매핑·후보군 생성 없음.

---

## 결론 먼저

```
98개 입력필드 → 8개 Trigger 계열 배치 완료.

WORK_EXISTS       18  (작업 boolean)
EQUIPMENT_EXISTS  20  (설비 boolean + 수량)
MATERIAL_EXISTS    8  (물질 boolean)
FACILITY_EXISTS   15  (시설 boolean)
DIRECT_THRESHOLD  14  (본조 수치)
APPENDIX_THRESHOLD 3  (별표 위임 수치)
TRUE_UNIVERSAL     2  (sector 분류)
UNDECIDED         18  (수량·메타·table 등)

과적재 입력: 0건 (has_high_pressure_gas는 이미 분리되어 있음 — 발견)
Trigger 공백: COMPOUND는 단일 입력 대응 없음 (정상)
```

---

## 산출물 A: 98개 입력필드 분류표

### WORK_EXISTS (작업 존재) — 18개

| field_code | field_name | L2 | sector |
|---|---|---|---|
| has_welding | 용접 공정 | WELDING | INDUSTRIAL |
| has_painting | 도장 공정 | PAINTING | INDUSTRIAL |
| has_plating | 도금 공정 | PLATING | INDUSTRIAL |
| has_casting | 주조/단조 | CASTING | INDUSTRIAL |
| has_heat_treatment | 열처리 | HEAT_TREATMENT | INDUSTRIAL |
| has_dust_work | 분진작업 | DUST | INDUSTRIAL |
| has_noise_work | 소음작업 | NOISE | INDUSTRIAL |
| has_radiation | 방사선작업 | RADIATION | INDUSTRIAL |
| has_high_place_work | 고소작업 | HIGH_PLACE | INDUSTRIAL |
| has_diving | 잠수작업 | DIVING | CONSTRUCTION |
| has_blasting | 발파작업 | BLASTING | CONSTRUCTION |
| has_excavation | 굴착작업 | EXCAVATION | CONSTRUCTION |
| has_demolition | 해체/철거 | DEMOLITION | CONSTRUCTION |
| has_asbestos_demo | 석면해체 | ASBESTOS | CONSTRUCTION |
| has_concrete_work | 콘크리트 공사 | CONCRETE | CONSTRUCTION |
| has_steel_frame | 철골공사 | STEEL_FRAME | CONSTRUCTION |
| has_pile_work | 항타/항발작업 | PILE_WORK | CONSTRUCTION |
| has_scaffold | 비계 사용 | SCAFFOLD | CONSTRUCTION |

### EQUIPMENT_EXISTS (설비 존재) — 20개

| field_code | field_name | L2 | sector |
|---|---|---|---|
| has_boiler | 보일러 | BOILER | BUILDING,INDUSTRIAL |
| has_pressure_vessel | 압력용기 | PRESSURE_VESSEL | INDUSTRIAL |
| has_crane | 크레인/호이스트 | CRANE | INDUSTRIAL |
| has_tower_crane | 타워크레인 | TOWER_CRANE | CONSTRUCTION |
| has_forklift | 지게차 | FORKLIFT | INDUSTRIAL |
| has_conveyor | 컨베이어 | CONVEYOR | INDUSTRIAL |
| has_press | 프레스 | PRESS | INDUSTRIAL |
| has_rolling | 롤러기 | ROLLING | INDUSTRIAL |
| has_grinding | 연삭기 | GRINDING | INDUSTRIAL |
| has_injection | 사출기 | INJECTION | INDUSTRIAL |
| has_elevator | 승강기(화물) | ELEVATOR | INDUSTRIAL |
| has_gondola | 곤돌라 | GONDOLA | CONSTRUCTION |
| has_mech_parking | 기계식주차장 | MECH_PARKING | BUILDING |
| has_emergency_gen | 비상발전기 | EMERGENCY_GEN | BUILDING |
| has_cooling_tower | 냉각탑 | COOLING_TOWER | BUILDING |
| has_central_hvac | 중앙공조 | HVAC | BUILDING |
| crane_count | 크레인 대수 | CRANE | INDUSTRIAL |
| forklift_count | 지게차 대수 | FORKLIFT | INDUSTRIAL |
| tower_crane_count | 타워크레인 대수 | TOWER_CRANE | CONSTRUCTION |
| elevator_count | 승강기 대수 | ELEVATOR | BUILDING,INDUSTRIAL |

### MATERIAL_EXISTS (물질 존재) — 8개

| field_code | field_name | L2 | sector |
|---|---|---|---|
| has_chemical_substance | 화학물질 취급 | CHEMICAL | INDUSTRIAL |
| has_chemical | 화학물질 | CHEMICAL | BUILDING |
| has_hazardous_material | 유해물질 취급 | HAZMAT | INDUSTRIAL |
| has_high_pressure_gas | 고압가스 | HIGH_PRESSURE_GAS | INDUSTRIAL |
| has_gas | 가스시설 | GAS | BUILDING |
| has_hazmat_storage | 위험물저장소 | HAZMAT_STORAGE | BUILDING,INDUSTRIAL |
| has_oil_storage | 유류저장 | OIL_STORAGE | BUILDING |
| has_asbestos | 석면 사용 | ASBESTOS | BUILDING |

### FACILITY_EXISTS (시설 존재) — 15개

| field_code | field_name | L2 | sector |
|---|---|---|---|
| has_confined_space | 밀폐공간 | CONFINED_SPACE | CONSTRUCTION,INDUSTRIAL |
| has_sprinkler | 스프링클러 | SPRINKLER | BUILDING |
| has_fire_hydrant | 소화전 | FIRE_HYDRANT | BUILDING |
| has_smoke_control | 제연설비 | SMOKE_CONTROL | BUILDING |
| has_emergency_broadcast | 비상방송 | BROADCAST | BUILDING |
| has_water_tank | 저수조 | WATER_TANK | BUILDING |
| has_septic_tank | 정화조 | SEPTIC_TANK | BUILDING |
| has_temp_electric | 가설전기 | TEMP_ELECTRIC | CONSTRUCTION |
| is_multi_use | 다중이용업소 | MULTI_USE | BUILDING |
| is_complex_building | 복합건축물 | COMPLEX_BUILDING | BUILDING |
| has_subcontractor | 하도급 | SUBCONTRACT | CONSTRUCTION |
| escalator_count | 에스컬레이터 | ESCALATOR | BUILDING |
| mech_parking_count | 기계식주차장 대수 | MECH_PARKING | BUILDING |
| has_septic_tank | 정화조 | SEPTIC_TANK | BUILDING |
| underground_area | 지하주차장 면적 | UNDERGROUND | BUILDING |

### DIRECT_THRESHOLD (본조 수치) — 14개

| field_code | field_name | help_text 임계값 | sector |
|---|---|---|---|
| total_floor_area | 연면적 | 5,000㎡ | BUILDING,INDUSTRIAL |
| excavation_depth | 굴착 깊이 | 2m 이상 흙막이 | CONSTRUCTION |
| max_work_height | 최대 작업 높이 | 31m 이상 안전관리계획서 | CONSTRUCTION |
| electric_capacity | 수전용량 | 75kW 이상 전기안전관리자 | BUILDING,INDUSTRIAL |
| is_energy_intensive | 에너지다소비 | 연 2,000TOE | BUILDING |
| annual_energy_toe | 연간 에너지 | 2,000TOE | BUILDING,INDUSTRIAL |
| gas_capacity_kg | 가스 저장용량 | (지정수량) | BUILDING,INDUSTRIAL |
| gas_capacity_m3 | 가스 저장용량 | (지정수량) | BUILDING |
| boiler_capacity_kw | 보일러 용량 | (용량 기준) | BUILDING |
| transformer_capacity_kva | 변압기 용량 | (용량 기준) | BUILDING |
| emergency_gen_kw | 비상발전기 용량 | (용량 기준) | BUILDING |
| water_tank_ton | 저수조 용량 | (용량 기준) | BUILDING |
| septic_tank_ton | 정화조 용량 | (용량 기준) | BUILDING |
| floor_count | 지상 층수 | (층수 기준) | BUILDING |

### APPENDIX_THRESHOLD (별표 위임) — 3개

| field_code | field_name | 위임 별표 | sector |
|---|---|---|---|
| worker_count | 상시 근로자 수 | 안전관리자 별표(50/500/1000인) | ALL |
| project_amount | 총 공사금액 | 건설 안전관리자 별표 | CONSTRUCTION |
| building_grade | 건물 등급 | (등급 기준) | BUILDING |

### TRUE_UNIVERSAL (sector 분류) — 2개

| field_code | field_name | 역할 | sector |
|---|---|---|---|
| ksic_major | 업종 대분류 | sector 확정 → UNIVERSAL 일괄 | INDUSTRIAL |
| ksic_sub | 업종 소분류 | sector 세분 | INDUSTRIAL |

---

## 산출물 B: Trigger별 입력필드 수 집계

| Trigger | 입력필드 수 |
|---|---|
| EQUIPMENT_EXISTS | 20 |
| WORK_EXISTS | 18 |
| FACILITY_EXISTS | 15 |
| DIRECT_THRESHOLD | 14 |
| MATERIAL_EXISTS | 8 |
| APPENDIX_THRESHOLD | 3 |
| TRUE_UNIVERSAL | 2 |
| **UNDECIDED** | **18** |
| **합계** | **98** |

---

## 산출물 C: UNDECIDED 목록 (18개)

분류 불가 또는 보류 — Trigger 단일 배치가 부적절한 필드:

| field_code | field_name | UNDECIDED 사유 |
|---|---|---|
| address | 사업장 주소 | TEXT_TRIGGER — API 실행 스위치, Trigger 아님 |
| project_address | 현장 주소 | TEXT_TRIGGER — 동일 |
| process_list | 주요 공정 | TABLE — 행마다 WORK Trigger 반복 (단일 배치 불가) |
| equipment_list | 설비 목록 | TABLE — 행마다 EQUIPMENT Trigger 반복 |
| process_worker_data | 공정별 작업자 수 | TABLE — 공정+인원 복합 |
| subcontractor | 협력업체 현황 | TABLE — 복합 |
| process_count | 공정 수 | QUANTITY — 단순 수량, Trigger 아님 |
| subcontractor_count | 하도급 업체 수 | QUANTITY — 단순 수량 |
| worker_count(중복) | — | APPENDIX 배치됨 |
| construction_type | 공사 유형 | CODE_SELECT — sector 세분, COMPOUND 가능 |
| operation_shift | 작업 교대제 | CODE_SELECT — 야간작업 조건 (COMPOUND) |
| equipment_inspection_status | 설비 검사 현황 | CODE_SELECT — 상태값, Trigger 아님 |
| multi_use_type | 다중이용 업종 | MULTI_SELECT — 복합 |
| building_use_type | 건물 용도 | CODE_SELECT(API) — 분류, COMPOUND 가능 |
| main_structure | 주구조 | CODE_SELECT(API) — 분류 |
| built_year | 건축연도 | DERIVED — has_asbestos 파생 트리거 |
| basement_count | 지하 층수 | QUANTITY — 단순 수량 |
| project_duration | 공사 기간 | QUANTITY — 기간, Trigger 불명 |
| has_safety_manager | 안전관리자 선임 | STATE — 결과상태, 의무원인 아님 |

---

## 산출물 D: 과적재 입력필드 목록

```
과적재 0건.

중요 발견:
  WO-VALIDATION-001에서 has_high_pressure_gas가
  압력용기/잠함/항타기 3개에 과적재됐던 문제가
  입력필드 레벨에서 이미 해소되어 있음:

  has_pressure_vessel  → EQUIPMENT_EXISTS (압력용기 전용 필드 존재)
  has_pile_work        → WORK_EXISTS (항타/항발 전용 필드 존재)
  has_high_pressure_gas → MATERIAL_EXISTS (순수 고압가스만)

→ 기존 77건 매핑이 has_high_pressure_gas로 과적재됐던 것은
  당시 입력필드가 부족해서였고,
  현재 입력필드(98개)에는 분리된 필드가 모두 존재.
→ 재매핑 시 정확한 필드 사용 가능.
```

---

## 산출물 E: Trigger 공백 목록

```
입력은 있는데 Trigger 매칭이 약한 경우:

COMPOUND:
  단일 입력필드로 직접 대응 없음 (정상)
  construction_type, operation_shift 등이 COMPOUND 조건 구성

TRUE_UNIVERSAL:
  입력 2개(ksic_major/sub)뿐.
  → UNIVERSAL 359 법령은 sector 선택만으로 일괄 발동
  → 입력 적음이 정상 (sector가 트리거)

Trigger는 있는데 입력이 부족:
  APPENDIX_THRESHOLD: 입력 3개 vs 법령 102건
    → worker_count 하나가 다수 별표 의무 트리거
  MATERIAL_EXISTS: 입력 8개 vs 법령 45건
    → 물질 종류는 적지만 의무는 많음 (1:N 정상)
```

---

## 성공 기준 답변

```
Q: WORK_TRIGGER는 몇 개?       A: 18개 입력필드
Q: EQUIPMENT_TRIGGER는 몇 개?  A: 20개 입력필드
Q: THRESHOLD는 몇 개?          A: DIRECT 14 + APPENDIX 3 = 17개
Q: 과적재 입력은 무엇인가?      A: 0건 (입력필드 레벨에서 이미 분리됨)
Q: 분류 불가능한 입력은?        A: UNDECIDED 18개 (table/주소/수량/상태값/CODE_SELECT)
```

---

## 핵심 발견

### 발견 1: 입력세계 → Trigger세계 연결 완료

```
80개 필드(98 - UNDECIDED 18)가 8개 Trigger에 배치됨.
EXISTS 4종(WORK/EQUIPMENT/MATERIAL/FACILITY) = 61개 (62%)
THRESHOLD 2종 = 17개
UNIVERSAL = 2개

→ 입력 → Trigger 연결 골격 완성.
```

### 발견 2: 과적재가 입력필드 레벨에서 자연 해소

```
77건 CONFIRMED의 PARTIAL 4건 원인(has_high_pressure_gas 과적재)이
현재 입력필드 98개에는 has_pressure_vessel/has_pile_work로 이미 분리됨.
→ 재매핑만으로 PARTIAL → EXPLAINABLE 전환 가능.
```

### 발견 3: UNDECIDED 18개의 성격

```
TABLE 4개 (Trigger 반복기 — 행 단위로 풀어야 함)
주소 2개 (API 스위치)
단순수량 5개 (Trigger 아님)
CODE_SELECT 5개 (sector/COMPOUND)
상태/파생 2개 (has_safety_manager, built_year)

→ UNDECIDED는 "분류 실패"가 아니라
  "단일 Trigger 배치가 부적절한 특수 유형".
→ TABLE은 다음 단계에서 행 단위로 EXISTS Trigger에 연결.
```

### 발견 4: APPENDIX_THRESHOLD가 1:N 병목

```
입력 worker_count 1개 → 법령 APPENDIX 102건 트리거.
→ worker_count가 안전관리자/관리담당자/관리규정 등
  다수 별표 의무를 동시 발동.
→ appendix_condition 7건 입력이 이 1:N의 병목.
```

---

## 다음 단계

```
WO-INPUT-TRIGGER-CLASSIFICATION-001 (현재) — 완료
      ↓
WO-TRIGGER-LAW-MAPPING-001
  이제 Trigger ↔ 법령 연결:
  WORK_EXISTS(18입력) ↔ 법령 WORK_EXISTS(189조문)
  EQUIPMENT_EXISTS(20입력) ↔ 법령 EQUIPMENT(153조문)
  각 L2(잠수/보일러/석면)별로 입력↔법령 정밀 연결
```

---

*WO-INPUT-TRIGGER-CLASSIFICATION-001 완료. 분류 전용. 법령 검색 없음.*
*98필드 → 8 Trigger 배치. CLASSIFIED 80 / UNDECIDED 18 / 과적재 0.*
*핵심: 입력→Trigger 연결 완료. has_high_pressure_gas 과적재가 입력필드 레벨에서 해소됨.*
