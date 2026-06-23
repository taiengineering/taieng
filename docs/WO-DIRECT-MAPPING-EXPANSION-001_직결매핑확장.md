# WO-DIRECT-MAPPING-EXPANSION-001
# DIRECT MAPPING 확장 작업

**작성일:** 2026-06-23 | **상태:** 설계 완료 / INSERT 미실행
**원칙:** 입력값 → 법령 직결 경로 발굴만. 모델·규칙 경유 금지.

---

## 산출물 A: DIRECT_MAPPING_GAP_LIST

### A-1. 현재 매핑 완료 필드

| 입력필드 | 타입 | 매핑건수 | Path | 비고 |
|---|---|---|---|---|
| has_asbestos_demo | boolean | 7 | HAS_* | 완료 |
| has_blasting | boolean | 2 | HAS_* | 완료 |
| has_boiler | boolean | 4 | HAS_* | 완료 |
| has_chemical_substance | boolean | 24 | HAS_* | 완료 (100L 조건 2건 COMPOUND 이관 예정) |
| has_confined_space | boolean | 16 | HAS_* | 완료 |
| has_diving | boolean | 14 | HAS_* | 완료 |
| has_high_pressure_gas | boolean | 5 | HAS_* | 완료 (과적재 이슈 있음) |
| has_tower_crane | boolean | 5 | HAS_* | 완료 |
| employee_count | integer | 0 (후보 3건) | THRESHOLD | 설계 완료, APPLY 대기 |

### A-2. 미연결 필드 — factories 테이블 기준

| 입력필드 | DB 컬럼 | 데이터 있는 사업장 | 직결 가능 여부 | 우선순위 |
|---|---|---|---|---|
| **building_area** | building_area (numeric) | 623개 (11%) | **가능** — 400㎡ 이상 경보설비 | **Tier-1** |
| **construction_amount** | construction_amount (numeric) | 5,114개 (88%) | 가능 — 건설업 안전관리자 기준 | **Tier-1** |
| **electrical_capacity_kw** | electrical_capacity_kw (numeric) | 387개 (7%) | 제한적 — 특별고압(7천V) 조문 존재 | Tier-2 |
| **elevator_count** | elevator_count (integer) | 25개 | 제한적 — 리프트·승강기 보유 시 운용 의무 | Tier-2 |
| **boiler_capacity_kw** | boiler_capacity_kw (numeric) | 23개 | 제한적 — has_boiler와 중복 가능 | Tier-3 |
| **gas_capacity_m3** | gas_capacity_m3 (numeric) | 15개 | 가능 — 고압가스 저장량 기준 | Tier-2 |
| **contractor_count** | contractor_count (integer) | 23개 | 제한적 — 도급인 의무, semantic_clause 연결 미확인 | Tier-3 |
| **occupant_capacity** | occupant_capacity (integer) | 22개 | 제한적 | Tier-3 |
| **transformer_capacity_kva** | transformer_capacity_kva (numeric) | 21개 | 전압 기준과 연계 가능 | Tier-3 |

### A-3. factories에 없는 필드 (추가 필요)

| 미존재 필드 | 관련 의무 | 추가 우선순위 |
|---|---|---|
| chemical_daily_volume_liter | 관리대상 유해물질 100L/일 이상 경보설비·약제 | 높음 |
| construction_contract_amount | CONSTRUCTION 안전관리자 기준 | 높음 |
| voltage_level | 특별고압 취급 설비 접지 | 중간 |

---

## 산출물 B: DIRECT_MAPPING_CANDIDATES

### B-1. Tier-1 — 즉시 적재 가능

#### B-1-1. building_area >= 400 → 경보용 설비 (안전보건기준규칙 19조 — 단독 경로)

**직결 구조:**
```
building_area >= 400 (㎡)
  → 옥내작업장 연면적 400㎡ 이상 조건 충족
  → 경보용 설비 또는 기구 설치 의무 발동
```

**조문 텍스트 확인:**
```
sc_id: 94e85f9b-6f2a-4e99-b40f-40aea08a0864
조문: 사업주는 연면적이 400제곱미터 이상이거나 상시 50명 이상의 근로자가
     작업하는 옥내작업장에는 비상시에 근로자에게 신속하게 알리기 위한
     경보용 설비 또는 기구를 설치하여야 한다.
```

**판정:** condition_text에 **400㎡ 이상** 직접 명시. DIRECT 가능.
**주의:** "또는 50명 이상" 조건이 있어 완전한 DIRECT는 building_area 단독 경로. employee_count 쪽은 COMPOUND.

| condition_code | input_field | op | value | sectors | sc_id | condition_type | 판정 |
|---|---|---|---|---|---|---|---|
| AREA_GTE_400:ALARM_DEVICE | building_area | >= | 400 | ['INDUSTRIAL','CONSTRUCTION','BUILDING'] | 94e85f9b | THRESHOLD | **CONFIRMED_CANDIDATE** |

---

#### B-1-2. construction_amount 기준 (건설업 안전관리자 기준)

**조사 결과:** semantic_clause에서 직접적인 "공사금액 N억 이상" 조문 미발견.
공사금액 기준 안전관리자 선임은 시행령 별표 3의 건설업 조항에 있으나 appendix_condition 미입력.
**현재 상태:** construction_amount는 데이터(5,114건)가 있으나 법령 연결 미확인.

**처리:** appendix_condition에 건설업 별표 3 데이터 입력 후 THRESHOLD 처리. 이번 WO에서는 DEFERRED.

---

### B-2. Tier-2 — 추가 검토 필요

#### B-2-1. elevator_count >= 1 → 리프트·승강기 운용 의무

**조문 현황 (확인됨):**

| sc_id | 조번호 | 의무 내용 | 판정 |
|---|---|---|---|
| 59090e50 | 151 | 리프트 권과방지·과부하방지·비상정지장치 설치 | **DIRECT** — 리프트 보유 사업장 |
| a63a4f4c | 152 | 리프트 조작반 잠금장치 설치 | **DIRECT** — 리프트 보유 |
| 027d0122 | 153 | 리프트 피트 청소 시 운반구 낙하 방지 | PENDING (작업 시 조건) |
| 4d03823a | 156 | 리프트 설치·조립·수리·점검·해체 작업 시 조치 | PENDING (설치 작업 시) |
| 7e8a7b7a | 86 | 소형화물용 엘리베이터 근로자 탑승 금지 | **DIRECT** — 엘리베이터 보유 |
| 687b21c7 | 162 | 승강기 설치·조립·수리·점검·해체 작업 시 조치 | PENDING (설치 작업 시) |

**직결 후보:**
```
elevator_count >= 1
  → 리프트·승강기 보유 의무 (151, 152, 86조)
  applicable_sectors: ['INDUSTRIAL','BUILDING']
```

**주의:** `elevator_count` 필드가 실제로 입력된 사업장이 25개뿐. 데이터 희소성 고려 필요. factories 컬럼은 존재.

| condition_code | input_field | op | value | sc_id | sectors | 판정 |
|---|---|---|---|---|---|---|
| EQUIP_GTE_1:LIFT_SAFETY_DEVICE | elevator_count | >= | 1 | 59090e50 | ['INDUSTRIAL','BUILDING'] | PENDING_REVIEW |
| EQUIP_GTE_1:LIFT_LOCK | elevator_count | >= | 1 | a63a4f4c | ['INDUSTRIAL','BUILDING'] | PENDING_REVIEW |
| EQUIP_GTE_1:ELEVATOR_NO_BOARD | elevator_count | >= | 1 | 7e8a7b7a | ['INDUSTRIAL','BUILDING'] | PENDING_REVIEW |

---

#### B-2-2. electrical_capacity_kw / 특별고압 취급 조문

**조문 현황:**

| sc_id | 조번호 | 의무 내용 | 조건 |
|---|---|---|---|
| c59cc7df | 302 | 특별고압(7천V 초과) 취급 변전소 지락사고 시 접지극 전위상승 방지 | 특별고압 취급 전제 |
| 48b5959d | 307 | 고압·특별고압 단로기 개폐 시 주의표지판 설치 | 고압·특별고압 취급 전제 |

**판정:**
- `electrical_capacity_kw`는 설비 용량(kW)인데, 조문 조건은 "특별고압 취급 여부(7,000V 초과)".
- kW ≠ V — 직결이 아닌 COMPOUND 또는 별도 `has_high_voltage` 필드 필요.
- **현재 DEFERRED. factories에 voltage_level 또는 has_special_voltage 컬럼 추가 후 재검토.**

---

#### B-2-3. gas_capacity_m3 → 가스 저장 의무

**조사 결과:** semantic_clause에서 직접적인 "가스 저장 N㎥ 이상" 조문 미발견.
산업안전보건법보다 고압가스안전관리법 영역. 1차 TAI Safe 범위 외.
**처리:** DEFERRED.

---

### B-3. Tier-3 — COMPOUND 이관 또는 후순위

| 필드 | 이유 | 처리 |
|---|---|---|
| building_area >= 400 + employee_count >= 50 | 경보설비 19조 OR 조건 — COMPOUND | WO-CONDITION-COMPOUND-001 |
| employee_count >= 50 + ksic_code | 안전관리자 업종 조건 — COMPOUND | WO-CONDITION-COMPOUND-001 |
| chemical_daily_volume_liter >= 100 + has_chemical_substance | 관리대상 유해물질 경보설비 — COMPOUND | WO-CONDITION-COMPOUND-001 |
| boiler_capacity_kw | has_boiler와 중복, 용량 기준 의무 별도 없음 | DEFERRED |
| contractor_count | 도급인 의무 — semantic_clause 연결 미확인 | DEFERRED |

---

## 산출물 C: DIRECT_MAPPING_COVERAGE

### 현재 → 이번 WO 후 목표

| input_field | 현재 상태 | 이번 WO 후 추가 가능 | 방법 |
|---|---|---|---|
| has_* (8개) | **완료** 77건 | — | — |
| employee_count | THRESHOLD 후보 3건 | **+3건 APPLY** | THRESHOLD-001-APPLY |
| building_area | 미연결 | **+1건** (400㎡ 경보설비) | DIRECT — Tier-1 |
| construction_amount | 미연결 | 0 (appendix 미입력) | DEFERRED |
| elevator_count | 미연결 | **+3건 후보** (PENDING_REVIEW) | Tier-2 |
| electrical_capacity_kw | 미연결 | 0 (kW≠V 불일치) | DEFERRED |
| gas_capacity_m3 | 미연결 | 0 (타법 영역) | DEFERRED |
| contractor_count | 미연결 | 0 (연결 미확인) | DEFERRED |

**추가 가능 건수: 최소 1건(Tier-1) + 최대 4건(Tier-2 포함)**

---

## 핵심 발견

### 발견 1: building_area >= 400 — Tier-1 즉시 적재 가능

**유일한 Tier-1 미연결 필드.**
- 안전보건기준규칙 19조 condition_text에 "400제곱미터 이상" 직접 명시
- factories.building_area 컬럼 존재 (623개 사업장 데이터)
- input_field 하나 → 법령 하나 → 설명 가능
- 단, "OR 50명 이상" 경로는 COMPOUND로 분리 처리

### 발견 2: construction_amount — 데이터는 풍부(88%), 법령 연결 미확인

5,114개 사업장(88%)이 construction_amount 데이터를 보유하지만
시행령 별표 3 건설업 안전관리자 기준이 appendix_condition에 미입력.
**appendix_condition 입력이 선행 과제.**

### 발견 3: 전압(voltage_level) — 필드 불일치

factories에 `electrical_capacity_kw`, `transformer_capacity_kva`는 있으나
의무 발생 조건은 "전압(V)" 기준 — 용량(kW)≠전압(V).
직결 불가. `has_special_voltage` boolean 또는 `max_voltage_kv` numeric 필드 추가 논의 필요.

### 발견 4: COMPOUND가 실제로는 가장 많음

탐색 결과를 보면 수치 조건 대부분이 "A 이상 **OR/AND** B 이상" 복합 구조.
순수한 "수치 하나 → 의무 하나" DIRECT는 building_area 400㎡가 유일한 발견.
나머지는 COMPOUND 또는 THRESHOLD(employee_count) 범주.

---

## 다음 단계

```
이번 WO 결론:
  Tier-1 신규 1건 확보: building_area >= 400 → 경보설비
  Tier-2 후보 3건: elevator_count >= 1 → 리프트 의무 (PENDING_REVIEW)
  
WO-DIRECT-MAPPING-APPLY-001 적재 대상:
  building_area >= 400 → 경보설비 (CONFIRMED_CANDIDATE)
  elevator_count >= 1 → 리프트 의무 3건 (PENDING_REVIEW — 사업 판단 후)

선행 과제:
  appendix_condition에 건설업 별표 3 (construction_amount 기준) 입력
  appendix_condition에 CONSTRUCTION THRESHOLD (employee_count) 기준 입력

이후 순서:
  WO-DIRECT-MAPPING-APPLY-001
    ↓
  WO-CONDITION-COMPOUND-001
    ↓
  WO-CONDITION-THRESHOLD-001-APPLY
    ↓
  VCF-02 원인 검증
```

---

*WO-DIRECT-MAPPING-EXPANSION-001 완료. INSERT 미실행.*
*핵심: 수치 조건 중 순수 DIRECT는 building_area >= 400 단 1건. 나머지는 COMPOUND 또는 appendix_condition 미입력 상태.*
