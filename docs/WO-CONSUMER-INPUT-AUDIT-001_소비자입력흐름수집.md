# WO-CONSUMER-INPUT-AUDIT-001
# 소비자 입력 흐름 전수 수집

**작성일:** 2026-06-24 | **상태:** 완료 (수집·관찰 전용)
**선행:** WO-INPUT-STAGING-002
**목적:** 실제 사용자가 진단 페이지에서 입력하는 질문 전체 수집
**금지:** 패턴 정의 / 매핑 / SECTION 재분류 / 엔진 수정

> 지금까지 모은 것은 선택지 풀(Layer A)과 입력 필드 마스터(Layer B).
> 이번에 맨 위 레이어 — "소비자가 실제로 무엇을 입력하는가"를 수집한다.

---

## 핵심 발견

```
diagnosis_input_fields가 곧 소비자 입력 흐름이었다.

이 테이블은 단순 필드 정의가 아니라
실제 진단 페이지의 화면 질문 + 입력 순서 + 무료/유료 단계까지
모두 담은 "소비자 입력 양식"이다.

3단 구조가 처음으로 완성됨:
  소비자 입력 (화면 질문)  ← diagnosis_input_fields
        ↓
  입력 필드 (저장 필드)    ← field_code
        ↓
  선택지 풀 (참조 데이터)  ← KSIC/위험물/설비 등 8,754건
```

---

## 산출물 A: consumer_input_catalog (소비자 입력 전수)

### BUILDING (건물) — FREE 5 + PAID 29 = 34개 질문

**무료 진단 (FREE) — 5개:**

| 화면 질문 | 저장 필드 | 타입 | 필수 | 단위 |
|---|---|---|---|---|
| 건물 주소 | address | text | ✅ | — |
| 연면적 | total_floor_area | number | ✅ | ㎡ |
| 지상 층수 | floor_count | number | ✅ | 층 |
| 건물 용도 | building_use_type | select | ✅ | — |
| 상시 근로자 수 | worker_count | number | ✅ | 명 |

**유료 진단 (PAID) 주요 — 29개 중 발췌:**

| 화면 질문 | 저장 필드 | 타입 | help_text |
|---|---|---|---|
| 수전용량 | electric_capacity | number | 75kW 이상 시 전기안전관리자 선임 의무 |
| 비상발전기 유무 | has_emergency_gen | boolean | — |
| 승강기 대수 | elevator_count | number | — |
| 스프링클러 유무 | has_sprinkler | boolean | — |
| 소화전 유무 | has_fire_hydrant | boolean | — |
| 제연설비 유무 | has_smoke_control | boolean | — |
| 비상방송 유무 | has_emergency_broadcast | boolean | — |
| 가스시설 유무 | has_gas | boolean | — |
| 화학물질 유무 | has_chemical | boolean | — |
| 위험물저장소 유무 | has_hazmat_storage | boolean | — |
| 저수조 유무 / 용량 | has_water_tank / water_tank_ton | boolean/number | 톤 |
| 다중이용업소 여부 / 업종 | is_multi_use / multi_use_type | boolean/multi_select | 노래방·PC방·학원·음식점 |
| 에너지다소비 여부 | is_energy_intensive | boolean | 연간 2,000TOE 이상 |
| 가스 저장용량 | gas_capacity_kg / gas_capacity_m3 | number | kg / m³ |
| 보일러 유무 / 용량 | has_boiler / boiler_capacity_kw | boolean/number | kW |
| 변압기 용량 | transformer_capacity_kva | number | kVA |

### CONSTRUCTION (건설) — FREE 3 + PAID 12 = 15개 질문

**무료 진단 (FREE) — 3개:**

| 화면 질문 | 저장 필드 | 타입 | help_text |
|---|---|---|---|
| 현장 주소 | project_address | text | — |
| 총 공사금액 | project_amount | number | 억 단위는 만원으로 환산 (1억=10000만원) |
| 동시 투입 인원 | worker_count | number | 최대 동시 작업 인원 |

**유료 진단 (PAID) — 12개:**

| 화면 질문 | 저장 필드 | 타입 |
|---|---|---|
| 공사 유형 | construction_type | select |
| 하도급 업체 수 | subcontractor_count | number |
| 주요 공정 | process_list | table (위험요인 입력) |
| 타워크레인 유무 | has_tower_crane | boolean |
| 밀폐공간 유무 | has_confined_space | boolean |
| 석면해체 유무 | has_asbestos_demo | boolean |
| 발파작업 유무 | has_blasting | boolean |
| 잠수작업 유무 | has_diving | boolean |
| 협력업체 현황 | subcontractor | table |

### INDUSTRIAL (산업) — FREE 4 + PAID1 12 + PAID2 1 + PAID3 1 = 18개 질문

**무료 진단 (FREE) — 4개:**

| 화면 질문 | 저장 필드 | 타입 | help_text |
|---|---|---|---|
| 사업장 주소 | address | text | — |
| 업종 대분류 | ksic_major | select | 한국표준산업분류(KSIC) 대분류 |
| 상시 근로자 수 | worker_count | number | — |
| 연면적 | total_floor_area | number | — |

**유료 진단 (PAID1) — 12개 + 단계별 PAID2/PAID3:**

| 화면 질문 | 저장 필드 | 타입 | 단계 |
|---|---|---|---|
| 안전관리자 선임 | has_safety_manager | boolean | PAID1 |
| 수전용량 | electric_capacity | number | PAID1 |
| 보일러 유무 | has_boiler | boolean | PAID1 |
| 화학물질 취급 | has_chemical_substance | boolean | PAID1 |
| 고압가스 유무 | has_high_pressure_gas | boolean | PAID1 |
| 가스 저장용량 | gas_capacity_kg | number | PAID1 |
| 승강기 대수 | elevator_count | number | PAID1 |
| 연간 에너지 사용량 | annual_energy_toe | number | PAID1 |
| **공정 목록** | process_list | table | **PAID2** |
| **설비 목록** | equipment_list | table | **PAID3** |

---

## 산출물 B: 입력 흐름 구조 (tier 단계)

```
무료/유료 단계 구조 (tier):

BUILDING:      FREE(5) → PAID(29)
CONSTRUCTION:  FREE(3) → PAID(12)
INDUSTRIAL:    FREE(4) → PAID1(12) → PAID2(1:공정) → PAID3(1:설비)
```

**관찰:**
- INDUSTRIAL만 PAID를 3단계(PAID1/2/3)로 분리 — 기본정보→공정→설비 순차 입력
- 공정(process_list)과 설비(equipment_list)는 table 타입 — 여기서 Layer A 선택지 풀 참조
- 무료 진단은 전부 필수 필드만 (간단 입력 → 빠른 결과)

---

## 산출물 C: 입력 타입 분포

| sector | tier | 필드 | 필수 | boolean | number | select | table |
|---|---|---|---|---|---|---|---|
| BUILDING | FREE | 5 | 5 | 0 | 3 | 1 | 0 |
| BUILDING | PAID | 29 | 6 | 13 | 12 | 2 | 0 |
| CONSTRUCTION | FREE | 3 | 3 | 0 | 2 | 0 | 0 |
| CONSTRUCTION | PAID | 12 | 5 | 5 | 3 | 1 | 2 |
| INDUSTRIAL | FREE | 4 | 3 | 0 | 2 | 1 | 0 |
| INDUSTRIAL | PAID1 | 12 | 4 | 4 | 6 | 1 | 0 |
| INDUSTRIAL | PAID2 | 1 | 1 | 0 | 0 | 0 | 1 |
| INDUSTRIAL | PAID3 | 1 | 1 | 0 | 0 | 0 | 1 |

**관찰:**
- boolean이 가장 많은 입력 방식 (22개) — "~유무" 형태 질문
- number 28개 — 수치 입력 (면적·용량·인원·금액)
- table 4개 — 공정/설비/협력업체 (선택지 풀 참조 지점)
- select 6개 — 업종·용도·공사유형 (선택지 풀 참조 지점)

---

## 산출물 D: 소비자입력 ↔ 선택지풀 연결 지점 (table/select 필드)

이 필드들이 Layer A(선택지 풀)를 참조하는 실제 연결 지점:

| 화면 질문 | 저장 필드 | 참조하는 선택지 풀 (Layer A) |
|---|---|---|
| 업종 대분류 | ksic_major | KSIC 501 |
| 건물 용도 | building_use_type | (건물용도 코드 — 별도) |
| 공사 유형 | construction_type | CONSTRUCTION_PROCESS 161 |
| 주요 공정 (건설) | process_list | CONSTRUCTION_WORK 243 + PROCESS 161 |
| 공정 목록 (산업) | process_list | KSIC 공정 3,378 |
| 설비 목록 (산업) | equipment_list | 설비 446 + equipment_assets |
| 다중이용 업종 | multi_use_type | (다중이용 코드 — 별도) |
| 협력업체 현황 | subcontractor | (자유 입력 table) |

**관찰:** select/table 8개 필드만 선택지 풀을 참조. 나머지 boolean/number 필드는 직접 입력.

---

## 산출물 E: 죽은 필드 / 활성 필드 분석

### 실제 소비자 입력에 노출되는 field_code (활성)

```
약 49개 distinct field_code가 실제 화면에 노출됨
(sector × tier 중복 제외 시 고유 필드)
```

### staging의 has_*/numeric과 대조

| factories 컬럼 | 소비자 입력 노출? | 비고 |
|---|---|---|
| has_confined_space | ✅ CONSTRUCTION | — |
| has_chemical_substance | ✅ INDUSTRIAL | — |
| has_high_pressure_gas | ✅ INDUSTRIAL | — |
| has_tower_crane | ✅ CONSTRUCTION | — |
| has_boiler | ✅ BUILDING/INDUSTRIAL | — |
| has_asbestos_demo | ✅ CONSTRUCTION | — |
| has_blasting | ✅ CONSTRUCTION | — |
| has_diving | ✅ CONSTRUCTION | — |
| has_safety_manager | ✅ BUILDING/INDUSTRIAL | — |
| employee_count | ✅ (worker_count로 노출) | **필드명 불일치** |
| building_area | ✅ (total_floor_area로 노출) | **필드명 불일치** |
| construction_amount | ✅ (project_amount로 노출) | **필드명 불일치** |
| elevator_count | ✅ | — |

### 중요 발견: DB 필드명 ≠ 소비자 입력 필드명

```
employee_count (factories) ≠ worker_count (입력화면)
building_area (factories)  ≠ total_floor_area (입력화면)
construction_amount        ≠ project_amount
electrical_capacity_kw     ≠ electric_capacity

→ 사용자가 말한 "DB 필드 ≠ 사용자 입력" 가설이 사실로 확인됨.
→ 매핑 시 필드명 정규화 레이어 필요.
```

### 신규 발견 입력 필드 (factories에 없으나 소비자가 입력)

```
BUILDING 전용:
  floor_count, building_use_type, main_structure, has_emergency_gen,
  has_sprinkler, has_fire_hydrant, has_smoke_control, has_emergency_broadcast,
  has_gas, has_chemical, has_hazmat_storage, has_water_tank, water_tank_ton,
  is_multi_use, multi_use_type, is_energy_intensive, building_grade

CONSTRUCTION 전용:
  construction_type, subcontractor_count, process_list, subcontractor

→ 이전에 "factories 9개 has_*"로만 봤던 입력 세계가
  실제로는 49개 소비자 입력 필드로 훨씬 넓었다.
```

---

## 산출물 F: 발견사항 종합

### 발견 1: 3단 구조 완성

```
소비자 입력 (49 화면 질문)
      ↓ field_code
입력 필드 (128 정의, tier/sector 포함)
      ↓ select/table 8개 지점
선택지 풀 (8,754 참조 데이터)
```

### 발견 2: DB 필드명 ≠ 소비자 입력 필드명

```
worker_count / total_floor_area / project_amount 등
소비자 입력 필드명과 factories DB 컬럼명이 다름.
→ 법령 매핑은 소비자 입력 필드명 기준으로 시작해야 함.
```

### 발견 3: 무료→유료 단계 설계

```
무료: 필수 핵심 필드만 (3~5개) → 빠른 진단
유료: 상세 필드 (12~29개) → 정밀 진단
INDUSTRIAL은 유료를 3단계(기본→공정→설비)로 분리
```

### 발견 4: help_text에 법령 기준 내장

```
"75kW 이상 시 전기안전관리자 선임 의무"
"50인 이상 안전관리자 선임 기준"
"연간 2,000TOE 이상"
"5,000㎡ 기준 자동 판단"

→ 진단 페이지가 이미 법령→질문 압축 결과물.
→ 이 help_text가 THRESHOLD 매핑의 힌트.
```

### 발견 5: BUILDING이 가장 입력 필드가 많다 (34개)

```
BUILDING 34 > INDUSTRIAL 18 > CONSTRUCTION 15

이전 KSIC 정책에서 "BUILDING 확정 0개"였는데,
실제 소비자 입력은 BUILDING이 가장 풍부.
→ BUILDING 입력 세계가 가장 발달되어 있음.
```

---

## 다음 단계

```
WO-CONSUMER-INPUT-AUDIT-001 (현재) — 완료
      ↓
WO-INPUT-FIELD-NORMALIZE-001
  소비자 입력 필드명 ↔ DB 필드명 ↔ 선택지 풀 매핑 테이블
  (worker_count = employee_count 등 정규화)
      ↓
WO-INPUT-PATTERN-DISCOVERY-001
  49개 소비자 입력 필드 기준 패턴 발견
  (이제 진짜 입력 세계 맨 위에서 시작 가능)
```

---

## 완료 기준 답변

```
진단 페이지 모든 질문 수집?       ✅ 49개 화면 질문 (sector×tier 128 정의)
필수/선택 여부?                   ✅ tier별 required 집계
입력 타입?                        ✅ boolean 22/number 28/select 6/table 4
선택지 존재 여부?                 ✅ has_options + select/table 8개
선택지 원천?                      ✅ KSIC/CONSTRUCTION_PROCESS/설비 등
DB 저장 필드?                     ✅ field_code (단 DB컬럼명과 불일치 발견)
연결되는 diagnosis_input_fields?  ✅ 전수 확인
```

---

*WO-CONSUMER-INPUT-AUDIT-001 완료.*
*소비자 입력 49 화면질문 수집. 3단 구조(소비자입력→필드→선택지풀) 완성.*
*핵심: DB 필드명 ≠ 소비자 입력 필드명 확인. BUILDING이 입력 가장 풍부(34개).*
