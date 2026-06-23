# WO-MAPPING-ARCHITECTURE-001
# Condition Mapping 아키텍처 확정

**작성일:** 2026-06-23 | **상태:** 확정
**근거:** DDL-004 / SEED-001 / AUDIT-001 / INPUT-MODEL-AUDIT-001 완료 결과

---

## 산출물 A: Mapping Architecture Diagram

```
사용자 입력
    │
    ▼
┌─────────────────────────────────────┐
│  Level 1: SECTOR                    │
│  INDUSTRIAL / CONSTRUCTION /        │
│            BUILDING                 │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│  Level 2: CONDITION PATH                                │
│                                                         │
│  ┌──────────┐  ┌───────────┐  ┌───────────┐            │
│  │ HAS_*    │  │ THRESHOLD │  │ COMPOUND  │            │
│  │ (구현완료)│  │ (미구현)  │  │ (미구현)  │            │
│  └──────────┘  └───────────┘  └───────────┘            │
│                                                         │
│  ┌──────────┐  ┌───────────┐  ┌───────────┐            │
│  │EQUIPMENT │  │ PROCESS   │  │ UNIVERSAL │            │
│  │ (미구현) │  │ (미구현)  │  │ (미구현)  │            │
│  └──────────┘  └───────────┘  └───────────┘            │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │  Level 3: LAW MATCH          │
        │  semantic_clause             │
        │  appendix_condition          │
        └──────────────────────────────┘
                       │
                       ▼
               의무후보 출력
```

**3단계 불변 원칙:**
```
Sector → Condition Path → Law
```
이 순서를 건너뛰는 경로(입력값 → 법령 직결)는 허용하지 않는다.

---

## 산출물 B: Condition Path 정의서

### B-1. HAS_* Path (구현 완료)

**정의:** 사업장 내 특정 위험 작업·설비·물질의 보유 여부(boolean)가 의무 발생 조건인 경로.

**입력 형식:**
```
input_field  = 'has_XXX'
input_operator = '='
input_value  = 'true'
```

**발동 조건:** 해당 has_* 필드가 `true`인 모든 사업장에서 해당 sector의 매핑 전부 발동.

**현재 적재 건수:** 77건

**대표 예시:**
```
has_confined_space = true
  + SECTOR = CONSTRUCTION
  → 619조~641조 밀폐공간 의무 16건 발동
```

**한계 (확인됨):**
- has_* 필드 하나가 여러 실물 개념을 대표하는 경우 과매핑 발생 (has_high_pressure_gas)
- 수량/규모 조건은 별도 Path 필요

---

### B-2. THRESHOLD Path (미구현)

**정의:** 숫자 임계값(employee_count, 면적, 금액 등)이 의무 발생 조건인 경로.

**입력 형식:**
```
input_field  = 'employee_count'
input_operator = '>='
input_value  = '50'
```

**발동 조건:** 사업장의 해당 수치 필드가 임계값을 초과하면 의무 발동.

**데이터 현황:**
```
appendix_condition 테이블: 7건 (전부 employee_count 기반)
  - employee_count >= 50  : 4건 (안전관리자 선임 기준)
  - employee_count >= 500 : 2건
  - employee_count >= 1000: 1건

factories 테이블 분포:
  employee_count >= 50  : 3,434개 사업장 (59%)
  employee_count >= 100 : 2,266개 사업장 (39%)
  employee_count >= 300 : 1,049개 사업장 (18%)
```

**구현 필요 필드:**
```
factories.employee_count    (존재 확인)
factories.building_area     (존재 확인)
factories.contract_amount   (미존재 — CONSTRUCTION 전용, 추가 필요)
chemical_daily_volume_liter (미존재 — has_chemical 수량 조건, 추가 필요)
```

**구현 우선순위:** **1순위** — appendix_condition 데이터 이미 존재, 핵심 의무 직결.

---

### B-3. COMPOUND Path (미구현)

**정의:** 2개 이상의 입력 조건이 AND/OR 결합되어야 의무가 발생하는 경로.

**입력 형식:**
```
input_field     = 'has_confined_space'   input_value     = 'true'
input_field_2   = 'employee_count'       input_value_2   = '100'
compound_operator = 'AND'
```

**발동 조건:** 복합 조건 전부 충족 시 의무 발동.

**현재 확인된 COMPOUND 후보 5건:**

| semantic_clause_id | 조번호 | 조건 구조 |
|---|---|---|
| 80135fef | 532 | has_diving = true OR has_high_pressure_work = true |
| 3cba36fb | 535 | has_diving = true OR has_high_pressure_work = true |
| 6edd3dd8 | 535 | 동일 |
| ALARM:dd47 | 434 | has_chemical = true AND chemical_volume >= 100L |
| SPILL_KIT:a88d | 434 | 동일 |

**구현 우선순위:** **2순위** — 현재 ALARM:dd47, SPILL_KIT:a88d 2건이 HAS_* Path에 잘못 적재된 상태 (과매핑).

---

### B-4. EQUIPMENT Path (미구현)

**정의:** 사업장에 등록된 특정 설비 코드(equipment_type_code)가 의무 발생 조건인 경로.

**입력 형식:**
```
input_field  = 'equipment_type_code'
input_operator = '='
input_value  = 'PRESSURE_VESSEL'
```

**발동 조건:** equipment_assets 테이블에서 해당 type_code를 보유한 사업장.

**현재 데이터 현황:**
```
equipment_assets: 3,284건
unique equipment_type_code: 36종
  주요 카테고리: MACHINE / ELECTRICAL / TRANSPORT / FIRE
  명확한 코드: PRESSURE_VESSEL / CRANE / CONVEYOR / PRESS
  불명확한 코드: 040 / 036 / 021 / 011 ... (정수 코드 — 분류 기준 미확정)
```

**선행 조건:**
- equipment_type_code 표준화 필요 (정수코드 → 의미 코드 매핑)
- condition_mapping_candidate의 `required_equipment_type` 필드 활용

**구현 우선순위:** **4순위** — 데이터 정규화 선행 필요.

---

### B-5. PROCESS Path (미구현)

**정의:** 사업장에 등록된 공정(process_id, process_lv1~4)이 의무 발생 조건인 경로.

**입력 형식:**
```
input_field  = 'process_id'
input_operator = '='
input_value  = 'P-WELDING'
```

**발동 조건:** factory_process 테이블에서 해당 공정을 보유한 사업장.

**현재 데이터 현황:**
```
factory_process: 476건
unique process_id: 10종
process_lv1~4: 계층 구조 존재 (내용 미확인)
```

**선행 조건:**
- process_id 10종과 법령 의무의 연결 관계 설계 필요
- VCF-02 샘플 결과 "공정만으로는 의무 미발생" 확인됨 (WO-SAMPLE-LOAD-001)
- 공정 → has_* 신호 변환 레이어 설계 필요

**구현 우선순위:** **5순위** — HAS_* Path 안정화 후 진행.

---

### B-6. UNIVERSAL Path (미구현)

**정의:** 특정 입력 조건 없이 sector 소속만으로 발동되는 전 사업장 의무.

**발동 조건:** 해당 sector에 속하면 무조건 발동.

**예상 대상:**
```
안전보건관리체계 구축 의무 (employee_count와 무관한 기본 의무)
안전보건교육 의무 (전 근로자)
중대재해 발생 시 보고 의무
```

**현재 상태:** condition_mapping_candidate에 아직 없음. SEED-002 이후 별도 설계.

**구현 우선순위:** **3순위** — THRESHOLD 다음. 교육·보고 의무가 여기 해당.

---

## 산출물 C: Path별 매핑 건수

### 현재 상태

| Condition Path | 적재 건수 | 상태 | 비고 |
|---|---|---|---|
| HAS_* | 77 | **구현 완료** | CONFIRMED 전원 |
| THRESHOLD | 0 | 미구현 | appendix_condition 7건 연결 대기 |
| COMPOUND | 0 | 미구현 | 후보 5건 설계 필요 |
| EQUIPMENT | 0 | 미구현 | 코드 정규화 선행 |
| PROCESS | 0 | 미구현 | 설계 선행 |
| UNIVERSAL | 0 | 미구현 | THRESHOLD 이후 |
| **전체** | **77** | | |

### 목표 상태 (SEED-002 + THRESHOLD + COMPOUND 완료 후)

| Condition Path | 예상 건수 | 근거 |
|---|---|---|
| HAS_* | 77 (현행) + PENDING 38 | PENDING 적재 시 115건 |
| THRESHOLD | 7~20 | appendix_condition 7건 + 추가 설계 |
| COMPOUND | 5 | 현재 후보 5건 |
| EQUIPMENT | 미정 | 코드 정규화 후 |
| PROCESS | 미정 | 설계 후 |
| UNIVERSAL | 미정 | 설계 후 |

---

## 산출물 D: 미구현 경로 목록

### D-1. 즉시 구현 가능 (데이터 존재)

| 경로 | 필요 조건 | 차단 요소 없음 |
|---|---|---|
| THRESHOLD(employee_count) | factories.employee_count 존재, appendix_condition 7건 존재 | 없음 |
| COMPOUND(HAS_* + HAS_*) | condition_mapping_candidate DDL에 compound 필드 존재 | 없음 |

### D-2. 데이터 추가 필요

| 경로 | 필요한 추가 데이터 |
|---|---|
| THRESHOLD(면적) | factories.building_area 존재 — 면적 기준 appendix_condition 미존재 |
| THRESHOLD(공사금액) | factories.contract_amount 미존재 |
| THRESHOLD(화학물질 수량) | chemical_daily_volume_liter 미존재 |
| COMPOUND(HAS_* AND THRESHOLD) | 위 데이터 추가 후 |

### D-3. 설계 선행 필요

| 경로 | 선행 작업 |
|---|---|
| EQUIPMENT | equipment_type_code 정수코드 → 의미코드 매핑 |
| PROCESS | process_id 10종 → 법령 의무 연결 관계 설계 |
| UNIVERSAL | 전 사업장 의무 목록 도출 |

---

## 산출물 E: 구현 우선순위

```
1순위: THRESHOLD (employee_count)
  근거:
    - appendix_condition 데이터 이미 존재 (7건)
    - factories.employee_count 존재
    - 안전관리자 선임 의무 — 가장 핵심 법정 의무
    - WO-CONDITION-THRESHOLD-001로 진행

2순위: COMPOUND (현재 과매핑 2건 수정 포함)
  근거:
    - dd47, a88d 2건 HAS_* 과매핑 → COMPOUND로 이동 필요
    - 기압조절실 3건 (532·535조) 설계 필요
    - WO-CONDITION-COMPOUND-001로 진행

3순위: UNIVERSAL
  근거:
    - 교육·보고 의무는 sector 소속만으로 발동
    - 현재 가장 많은 사업장에 영향
    - WO-CONDITION-UNIVERSAL-001로 진행

4순위: EQUIPMENT
  근거:
    - equipment_type_code 정규화 선행 필요
    - 정규화 완료 후 PRESSURE_VESSEL / CRANE 등 연결

5순위: PROCESS
  근거:
    - "공정만으로는 의무 미발생" 확인됨 (VCF-02 결과)
    - 설계 복잡도 높음
    - HAS_*, THRESHOLD, COMPOUND 안정화 이후

VCF-02 원인 검증:
    - THRESHOLD 구현 완료 후 실행
    - 현재 HAS_* 77건만으로는 THRESHOLD 의무 미발생 → 불완전한 검증
```

---

## 확정된 3대 원칙

**원칙 1: Sector 우선**
```
모든 의무 후보 조회는 applicable_sectors @> ARRAY[sector]이 1순위.
sector 없이 조건 검색하지 않는다.
```

**원칙 2: COMMON 금지**
```
applicable_sectors에 'COMMON' 불가.
전 sector 공통 의무는 ['INDUSTRIAL','CONSTRUCTION','BUILDING']로 표현.
```

**원칙 3: 3단계 구조 유지**
```
입력값이 법령에 직접 연결되지 않는다.
반드시: Sector → Condition Path → Law
```

**원칙 4: 입력값 정규화는 아키텍처 확정 후**
```
has_high_pressure_gas 분리,
chemical_daily_volume_liter 추가 등
개별 입력필드 논의는 아키텍처 확정 이후 진행.
```

---

## 현재 상태 요약

```
Level 1 (Sector)      : 확정 완료 — INDUSTRIAL / CONSTRUCTION / BUILDING
Level 2 (Path)        : HAS_* 완료 / 나머지 5개 Path 설계 확정
Level 3 (Law Match)   : semantic_clause 77건 연결 완료

다음 구현 순서:
  WO-CONDITION-THRESHOLD-001   ← 1순위
  WO-CONDITION-COMPOUND-001    ← 2순위 (과매핑 2건 수정 포함)
  WO-CONDITION-UNIVERSAL-001   ← 3순위
  WO-CONDITION-EQUIPMENT-001   ← 4순위
  WO-CONDITION-PROCESS-001     ← 5순위
  VCF-02 원인 검증              ← THRESHOLD 완료 후
```

---

*WO-MAPPING-ARCHITECTURE-001 완료. 3단계 아키텍처 확정. Path 6종 정의. 구현 순서 확정.*
