# WO-DIRECT-MAPPING-HARVEST-001
# 입력값 → 의무 직결 매핑 수확 작업

**작성일:** 2026-06-23 | **상태:** 수확 완료 / INSERT 금지
**원칙:** 수확 전용. 검증·COMPOUND 설계·엔진 수정 금지.
**데이터 기반:** 이전 WO 조회 결과 + 현 세션 DB 탐색 결과 통합

---

## TASK-001: factories 입력필드 전체 목록

*(이전 세션 확인 결과 기준. DB 컬럼 전수 확인 완료.)*

| field_name | data_type | non_null 사업장 수 | 예시값 |
|---|---|---|---|
| id | uuid | 5,812 | uuid |
| sector | varchar | 5,812 | INDUSTRIAL / CONSTRUCTION / BUILDING |
| site_type | text | 5,812 | FACTORY / OFFICE / CONSTRUCTION_SITE |
| name | text | 5,812 | (사업장명) |
| employee_count | integer | 5,811 | 5 ~ 3,000+ |
| building_area | numeric | 623 | 120.0 ~ 50,000.0 (㎡) |
| electrical_capacity_kw | numeric | 387 | 10 ~ 5,000 (kW) |
| transformer_capacity_kva | numeric | 21 | 100 ~ 2,000 (kVA) |
| gas_capacity_m3 | numeric | 15 | 0.5 ~ 500 (㎥) |
| boiler_capacity_kw | numeric | 23 | 50 ~ 2,000 (kW) |
| construction_amount | numeric | 5,114 | 100 ~ 100,000,000 (만원) |
| elevator_count | integer | 25 | 1 ~ 20 |
| occupant_capacity | integer | 22 | 50 ~ 2,000 |
| contractor_count | integer | 23 | 1 ~ 50 |
| annual_energy_toe | numeric | 0 | — |
| has_confined_space | boolean | 5,812 | true / false |
| has_blasting | boolean | 5,812 | true / false |
| has_chemical_substance | boolean | 5,812 | true / false |
| has_high_pressure_gas | boolean | 5,812 | true / false |
| has_tower_crane | boolean | 5,812 | true / false |
| has_boiler | boolean | 5,812 | true / false |
| has_asbestos_demo | boolean | 5,812 | true / false |
| has_diving | boolean | 5,812 | true / false |
| has_safety_manager | boolean | 5,812 | true / false |
| ksic_code | varchar | 5,812 | (KSIC 분류코드) |
| created_at | timestamptz | 5,812 | — |
| updated_at | timestamptz | 5,812 | — |

---

## TASK-002: 입력필드 분류

### A. 이미 매핑됨 (condition_mapping_candidate 연결 완료)

| field_name | 매핑건수 | 비고 |
|---|---|---|
| has_confined_space | 16 | CONFIRMED |
| has_tower_crane | 5 | CONFIRMED |
| has_blasting | 2 | CONFIRMED |
| has_asbestos_demo | 7 | CONFIRMED |
| has_boiler | 4 | CONFIRMED |
| has_diving | 14 | CONFIRMED |
| has_chemical_substance | 24 | CONFIRMED |
| has_high_pressure_gas | 5 | CONFIRMED (과적재 이슈 별도) |
| employee_count | 0 (후보 3건) | THRESHOLD APPLY 대기 |

---

### B. 직결 가능 후보 (이번 HARVEST 핵심 대상)

| field_name | 데이터 있는 사업장 | 직결 법령 존재 여부 | 우선순위 |
|---|---|---|---|
| building_area | 623개 | **확인됨** — 400㎡ 경보설비(19조) | **최우선** |
| elevator_count | 25개 | **확인됨** — 리프트 권과방지 등(151~156조) | 높음 |
| has_safety_manager | 5,812개 | THRESHOLD 연계(employee_count 선행) | 중간 |
| construction_amount | 5,114개 | appendix_condition 미입력 | 중간 |
| occupant_capacity | 22개 | 조문 탐색 필요 | 낮음 |
| contractor_count | 23개 | 도급인 의무 조문 탐색 필요 | 낮음 |
| ksic_code | 5,812개 | 업종별 의무 — COMPOUND 경유 | COMPOUND 이관 |

---

### C. 원천 데이터 부족

| field_name | 사유 |
|---|---|
| electrical_capacity_kw | kW ≠ V 불일치. 의무 조건은 전압(V) 기준. 직결 불가 |
| transformer_capacity_kva | 동일 — 용량(kVA)과 전압(V) 불일치 |
| gas_capacity_m3 | 고압가스안전관리법 영역 — TAI Safe 1차 범위 외 |
| boiler_capacity_kw | has_boiler boolean으로 충분. 용량 기준 별도 의무 미발견 |
| annual_energy_toe | 데이터 없음(0건) |

---

### D. 현재 범위 제외 (운영·시스템 컬럼)

| field_name | 사유 |
|---|---|
| id | 시스템 식별자 |
| name | 사업장 명칭 — 법령 연결 대상 아님 |
| sector | LEVEL-1 분류자 — 입력값 아닌 매핑 필터 |
| site_type | 내부 분류자 |
| ksic_code | COMPOUND 경유 필요 — 단독 직결 불가 |
| created_at / updated_at | 시스템 타임스탬프 |

---

## TASK-003 + TASK-004: B그룹 직결 조문 수확

### 수확 원칙
- 입력값 하나 → 조문 하나 → 의무 하나만 찾는다
- 중간 개념 경유 없음
- 지금은 맞는지 틀린지 판단하지 않는다. 일단 모은다.

---

### B-1. building_area 수확

**수확 기준:** factories.building_area (㎡) 값이 조건을 충족하면 발동

| # | input_field | 조건 | sc_id | 조번호 | 의무 내용 | sectors | 신뢰도 |
|---|---|---|---|---|---|---|---|
| 1 | building_area | >= 400 | 94e85f9b | 19(기준규칙) | 옥내작업장 비상경보용 설비 설치 | IND·CON·BLD | 높음 |

**추가 탐색 필요 조문 (DB 복구 후 확인):**
- 소방법·건축물관리법 기준 면적 조건 의무
- 작업장 바닥면적 기준 통로 확보 조문
- 야적장 면적 기준 낙하물 방지 조문

**현재 확보: 1건**

---

### B-2. elevator_count 수확

**수확 기준:** factories.elevator_count >= 1 (승강기·리프트 보유)

| # | input_field | 조건 | sc_id | 조번호 | 의무 내용 | sectors | 신뢰도 |
|---|---|---|---|---|---|---|---|
| 1 | elevator_count | >= 1 | 59090e50 | 151 | 리프트 권과방지·과부하방지·비상정지장치 설치 | IND·BLD | 높음 |
| 2 | elevator_count | >= 1 | a63a4f4c | 152 | 리프트 운반구 조작반 잠금장치 설치 | IND·BLD | 높음 |
| 3 | elevator_count | >= 1 | 7e8a7b7a | 86 | 소형화물용 엘리베이터 근로자 탑승 금지 | IND·BLD | 높음 |
| 4 | elevator_count | >= 1 | 027d0122 | 153 | 리프트 피트 내 청소·수리 시 운반구 낙하방지 | IND·BLD | 중간 (작업 조건 추가) |
| 5 | elevator_count | >= 1 | 4d03823a | 156 | 리프트 설치·조립·수리·점검·해체 작업 시 추락방지 조치 | IND·BLD | 중간 (설치작업 조건 추가) |
| 6 | elevator_count | >= 1 | 687b21c7 | 162 | 승강기 설치·조립·수리·점검·해체 작업 시 조치 | IND·BLD | 중간 (설치작업 조건 추가) |

**현재 확보: 6건**

---

### B-3. has_safety_manager 수확 (THRESHOLD 연계)

**수확 기준:** has_safety_manager = false AND employee_count >= 50 → 미선임 의무 발생
*(단, 이 필드는 결과 상태 필드 — 의무 발생 원인은 employee_count)*

| # | input_field | 조건 | sc_id | 조번호 | 의무 내용 | sectors | 신뢰도 |
|---|---|---|---|---|---|---|---|
| 1 | has_safety_manager | = false | 66772b0d | 17 | 안전관리자를 두어야 한다 | IND·CON·BLD | 높음 (employee_count 선행 필요) |

**판단:** has_safety_manager 단독 직결은 어렵다. employee_count >= 50 결과로 파생되는 필드.
이번 HARVEST에서는 COMPOUND 후보로 등록. 단독 직결 불가.

**현재 확보: 0건 (COMPOUND 이관)**

---

### B-4. construction_amount 수확

**수확 기준:** CONSTRUCTION sector, factories.construction_amount (만원)

| # | input_field | 조건 | sc_id | 조번호 | 의무 내용 | sectors | 신뢰도 |
|---|---|---|---|---|---|---|---|
| 1 | construction_amount | >= 8억 | (appendix 미입력) | 시행령 별표 3 | 건설업 안전관리자 선임 | CON | 높음 (appendix 입력 선행 필요) |
| 2 | construction_amount | >= 120억 | (appendix 미입력) | 시행령 별표 3 | 건설업 안전관리자 전담 의무 | CON | 높음 (appendix 입력 선행 필요) |
| 3 | construction_amount | >= 150억 | (appendix 미입력) | 법 제73조 | 건설공사 안전관리계획 수립 | CON | 높음 (appendix 입력 선행 필요) |
| 4 | construction_amount | >= 2,000억 | (appendix 미입력) | 법 제68조 | 안전관리전문기관 계약 의무 | CON | 중간 (법 구조 확인 필요) |

**현재 확보: 4건 후보 (appendix_condition 입력 선행 필요)**

---

### B-5. occupant_capacity 수확

**수확 기준:** factories.occupant_capacity (수용인원)

탐색 결과: semantic_clause에서 "수용인원" 직접 조건 조문 미발견.
건물관리 영역은 건축물관리법 / 소방법 → TAI Safe 1차 범위 경계.
**현재 확보: 0건**

---

### B-6. contractor_count 수확

**수확 기준:** factories.contractor_count (협력업체 수)

탐색 결과: semantic_clause에서 "도급인 의무" 연결 조문이 executor_text = '도급인'으로 분류되어 있을 가능성.
*(executor_text LIKE '%도급인%' 추가 탐색 필요 — DB 복구 후)*

**잠정 후보 (DB 복구 후 확인 필요):**

| # | input_field | 조건 | 조번호(추정) | 의무 내용(추정) | sectors | 신뢰도 |
|---|---|---|---|---|---|---|
| 1 | contractor_count | >= 1 | 법 제63조 | 도급인의 안전·보건 조치 의무 | IND·CON | 중간 (탐색 필요) |
| 2 | contractor_count | >= 1 | 법 제64조 | 도급인의 안전보건협의체 구성 | IND·CON | 중간 (탐색 필요) |

**현재 확보: 0건 (탐색 대기)**

---

## TASK-005: DIRECT 후보 인벤토리

### DIRECT-CONFIRMED (즉시 적재 가능 수준)

| condition_code | input_field | 조건 | sc_id | 조번호 | 의무 내용 | sectors |
|---|---|---|---|---|---|---|
| AREA_GTE_400:ALARM_DEVICE | building_area | >= 400 | 94e85f9b | 19(기준규칙) | 옥내작업장 경보용 설비 설치 | IND·CON·BLD |
| EQUIP_GTE_1:LIFT_OVERHOIST | elevator_count | >= 1 | 59090e50 | 151 | 리프트 권과방지·과부하방지·비상정지장치 | IND·BLD |
| EQUIP_GTE_1:LIFT_LOCK | elevator_count | >= 1 | a63a4f4c | 152 | 리프트 운반구 조작반 잠금장치 | IND·BLD |
| EQUIP_GTE_1:ELEVATOR_NO_BOARD | elevator_count | >= 1 | 7e8a7b7a | 86 | 소형화물용 엘리베이터 근로자 탑승 금지 | IND·BLD |

**소계: 4건**

---

### DIRECT-PENDING (조문 확인됐으나 조건 추가 또는 appendix 입력 필요)

| condition_code | input_field | 조건 | sc_id / 근거 | 의무 내용 | 보류 사유 |
|---|---|---|---|---|---|
| EQUIP_GTE_1:LIFT_PIT_CLEAN | elevator_count | >= 1 | 027d0122 / 153조 | 리프트 피트 청소 시 낙하방지 | 작업 시 조건 추가 필요 |
| EQUIP_GTE_1:LIFT_INSTALL | elevator_count | >= 1 | 4d03823a / 156조 | 리프트 설치·해체 시 추락방지 | 설치작업 시 조건 추가 필요 |
| EQUIP_GTE_1:ELEVATOR_INSTALL | elevator_count | >= 1 | 687b21c7 / 162조 | 승강기 설치·해체 시 조치 | 설치작업 시 조건 추가 필요 |
| THRESHOLD:CONSTR_GTE_8억:SAFETY_MANAGER | construction_amount | >= 80000 | 시행령 별표 3 | 건설업 안전관리자 선임 | appendix_condition 미입력 |
| THRESHOLD:CONSTR_GTE_120억:SAFETY_MANAGER_FULL | construction_amount | >= 1200000 | 시행령 별표 3 | 건설업 안전관리자 전담 | appendix_condition 미입력 |
| THRESHOLD:CONSTR_GTE_150억:SAFETY_PLAN | construction_amount | >= 1500000 | 법 제73조 | 건설공사 안전관리계획 수립 | appendix_condition 미입력 |
| THRESHOLD:EMPLOYEE_GTE_50:SAFETY_MANAGER | employee_count | >= 50 | 66772b0d / 법17조 | 안전관리자 선임 | THRESHOLD-001-APPLY 대기 |
| THRESHOLD:EMPLOYEE_GTE_20:SAFETY_HEALTH_OFFICER | employee_count | >= 20 | 879aeeac / 법19조 | 안전보건관리담당자 선임 | THRESHOLD-001-APPLY 대기 |
| THRESHOLD:EMPLOYEE_GTE_100:SAFETY_HEALTH_RULES | employee_count | >= 100 | 67055d7d / 법25조 | 안전보건관리규정 작성 | THRESHOLD-001-APPLY 대기 |
| DIRECT:CONTRACTOR_GTE_1:OBLIGATION | contractor_count | >= 1 | 법63조 (추정) | 도급인 안전·보건 조치 의무 | sc_id 확인 필요 |
| DIRECT:CONTRACTOR_GTE_1:COUNCIL | contractor_count | >= 1 | 법64조 (추정) | 도급인 안전보건협의체 구성 | sc_id 확인 필요 |

**소계: 11건**

---

### DIRECT-REJECTED (단독 직결 불가 — COMPOUND 또는 타 경로)

| 항목 | 사유 | 이관 경로 |
|---|---|---|
| building_area >= 400 OR employee_count >= 50 → 경보설비 | OR 조건 존재 — building_area 단독은 CONFIRMED, 복합은 COMPOUND | COMPOUND-001 |
| has_safety_manager = false | 결과 상태 필드 — 원인은 employee_count | THRESHOLD 연계 |
| electrical_capacity_kw | kW ≠ V — 의무 조건은 전압(V) 기준 | 필드 불일치 |
| gas_capacity_m3 | 고압가스안전관리법 영역 — 1차 범위 외 | DEFERRED |
| ksic_code | 업종만으로 직결 의무 없음 — COMPOUND 경유 필요 | COMPOUND-001 |
| occupant_capacity | 직결 조문 미발견 | DEFERRED |

---

## 핵심 질문에 대한 답변

> **현재 시스템이 가진 입력값 중 법령과 직접 연결 가능한 것은 무엇인가?**

```
즉시 연결 가능 (DIRECT-CONFIRMED 4건):
  building_area >= 400       → 경보용 설비 설치 (기준규칙 19조)
  elevator_count >= 1        → 리프트 권과방지 (151조)
  elevator_count >= 1        → 리프트 잠금장치 (152조)
  elevator_count >= 1        → 엘리베이터 탑승 금지 (86조)

확인 후 연결 가능 (DIRECT-PENDING 11건):
  elevator_count >= 1        → 리프트 피트 청소 조치 (153조)
  elevator_count >= 1        → 리프트 설치 시 추락방지 (156조)
  elevator_count >= 1        → 승강기 설치 시 조치 (162조)
  construction_amount >= N   → 건설업 안전관리자 선임 (시행령 별표 3)
  construction_amount >= N   → 건설공사 안전관리계획 (법 73조)
  employee_count >= 20/50/100 → 관리담당자·관리자·규정 3건 (법 17·19·25조)
  contractor_count >= 1      → 도급인 의무 2건 (법 63·64조, sc_id 확인 필요)

단독 직결 불가 (DIRECT-REJECTED — COMPOUND 이관):
  건물면적 OR 인원수 복합 조건
  업종(ksic_code) + 인원수 복합 조건
  화학물질 + 수량 복합 조건
```

---

## 다음 단계

```
WO-DIRECT-MAPPING-HARVEST-001 (현재) — 완료
      ↓
WO-DIRECT-MAPPING-REVIEW-001
  CONFIRMED 4건: "이게 진짜 DIRECT인가?" 조문 직독 검증
  PENDING 11건: sc_id 미확인 항목 DB 조회 완료
      ↓
WO-DIRECT-MAPPING-APPLY-001
  검증 통과 항목 INSERT
```

**DB 복구 후 추가 조회 필요:**
- contractor_count → 법63조·64조 sc_id 확인
- building_area 추가 면적 기준 조문 탐색 (통로 확보·야적장 등)
- executor_text = '%도급인%' 조문 전수 조회

---

*WO-DIRECT-MAPPING-HARVEST-001 완료.*
*CONFIRMED 4건 / PENDING 11건 / REJECTED 6건.*
*수확 단계 완료. 다음은 REVIEW.*
