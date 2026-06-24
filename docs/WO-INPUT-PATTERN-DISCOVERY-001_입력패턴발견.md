# WO-INPUT-PATTERN-DISCOVERY-001
# 입력 패턴 발견

**작성일:** 2026-06-24 | **상태:** 완료 (패턴 발견 전용)
**선행:** WO-INPUT-BOUNDARY-001
**금지:** 법령 매핑 / 조건 생성 / condition_mapping_candidate 수정
**목적:** 98개 입력필드를 개별이 아니라 패턴으로 압축한다.

> 핵심 가설: 입력값은 수천 개지만 패턴은 훨씬 적다.

---

## 결론 먼저

```
98개 입력필드 → 7개 입력 패턴으로 압축됨.

P1. BOOLEAN_EXISTENCE   55개  (예/아니오 — 보유 여부)
P2. NUMERIC_THRESHOLD   18개  (수치 — 임계값 판정)
P3. NUMERIC_QUANTITY     7개  (수치 — 단순 수량)
P4. CODE_SELECT          7개  (선택지 풀 단일 선택)
P5. TABLE_COLLECTION     4개  (복수 항목 + 선택지 풀 참조)
P6. EXTERNAL_LOOKUP      6개  (건축물대장 API 자동 생성)
P7. TEXT_TRIGGER         2개  (주소 — API 트리거)

7개 패턴으로 입력세계 전체를 설명할 수 있다.
```

---

## TASK-001~002: 행동 기준 귀납 분류

필드명이 아니라 **입력의 행동**을 기준으로 묶었다.

### field_type × origin × options 매트릭스

| field_type | origin | options | 개수 | → 패턴 |
|---|---|---|---|---|
| boolean | USER | no | 55 | P1 BOOLEAN_EXISTENCE |
| number | USER | no | 25 | P2 THRESHOLD + P3 QUANTITY |
| select | USER | no | 4 | P4 CODE_SELECT |
| select | USER | yes | 1 | P4 CODE_SELECT |
| table | USER | yes | 4 | P5 TABLE_COLLECTION |
| number | API_AUTO | no | 4 | P6 EXTERNAL_LOOKUP |
| select | API_AUTO | yes | 2 | P6 EXTERNAL_LOOKUP |
| multi_select | USER | no | 1 | P4 CODE_SELECT |
| text | USER | no | 2 | P7 TEXT_TRIGGER |

---

## TASK-003~005: INPUT_PATTERN_CATALOG

### P1. BOOLEAN_EXISTENCE (55개)

| 속성 | 값 |
|---|---|
| pattern_code | BOOLEAN_EXISTENCE |
| pattern_name | 보유·존재 여부 |
| description | 시설·설비·작업·물질의 존재를 예/아니오로 입력. true일 때 해당 의무 발동 트리거. |
| field_count | 55 |
| example_fields | has_confined_space, has_chemical_substance, has_tower_crane, has_boiler, has_press, has_crane, has_welding, is_multi_use |

**행동:** "X가 있습니까?" → true/false. 입력세계의 절반 이상(56%). 법령엔진의 가장 큰 트리거 군.

**하위 의미 그룹 (참고, 패턴은 동일):**
```
설비 보유:  has_press, has_crane, has_forklift, has_conveyor, has_boiler ...
작업 수행:  has_welding, has_painting, has_plating, has_excavation, has_blasting ...
물질 취급:  has_chemical_substance, has_high_pressure_gas, has_hazmat_storage ...
시설 존재:  has_sprinkler, has_fire_hydrant, has_elevator, has_septic_tank ...
상태 여부:  has_safety_manager, is_complex_building, is_energy_intensive ...
```

---

### P2. NUMERIC_THRESHOLD (18개)

| 속성 | 값 |
|---|---|
| pattern_code | NUMERIC_THRESHOLD |
| pattern_name | 임계값 판정 수치 |
| description | 수치를 입력받아 법정 임계값과 비교. 기준 초과 시 의무 발동. |
| field_count | 18 |
| example_fields | worker_count, electric_capacity, excavation_depth, max_work_height, project_amount, total_floor_area |

**행동:** "수치 N → N >= 임계값이면 의무." help_text에 임계값이 명시됨:
```
worker_count       → 50인 이상 안전관리자 선임
electric_capacity  → 75kW 이상 전기안전관리자 선임
excavation_depth   → 2m 이상 흙막이 의무
max_work_height    → 31m 이상 안전관리계획서 의무
project_amount     → (공사금액 구간별 의무)
total_floor_area   → 5,000㎡ 기준 자동 판단
```

**이 패턴이 THRESHOLD Path의 입력측 원천.** help_text가 곧 법령 임계값 힌트.

---

### P3. NUMERIC_QUANTITY (7개)

| 속성 | 값 |
|---|---|
| pattern_code | NUMERIC_QUANTITY |
| pattern_name | 단순 수량 |
| description | 임계 판정 없이 수량·개수만 기록. 다른 조건과 결합되거나 참고용. |
| field_count | 7 |
| example_fields | crane_count, forklift_count, elevator_count, process_count, subcontractor_count, mech_parking_count |

**행동:** "몇 개입니까?" → 개수. 단독으로 의무 발동 안 함. P1(존재)과 결합되거나 COMPOUND 보조.

**P2 vs P3 구분:**
```
P2 THRESHOLD: 임계값 비교 → 의무 (worker_count >= 50)
P3 QUANTITY:  단순 개수 → 참고 (crane_count = 3)
```

---

### P4. CODE_SELECT (7개)

| 속성 | 값 |
|---|---|
| pattern_code | CODE_SELECT |
| pattern_name | 코드 선택 |
| description | 선택지 풀(Layer A)에서 1개 또는 복수 선택. KSIC·공사유형 등. |
| field_count | 7 |
| example_fields | ksic_major, ksic_sub, construction_type, operation_shift, building_use_type, multi_use_type |

**행동:** "목록에서 고르세요." → 선택지 풀 참조. 단일(select) + 복수(multi_select) 포함.

**참조 선택지 풀:**
```
ksic_major/ksic_sub → KSIC 501
construction_type   → CONSTRUCTION_PROCESS 161
building_use_type   → 건물용도 코드 (API)
multi_use_type      → 다중이용 코드
```

---

### P5. TABLE_COLLECTION (4개)

| 속성 | 값 |
|---|---|
| pattern_code | TABLE_COLLECTION |
| pattern_name | 복수 항목 수집 |
| description | 표 형태로 여러 행 입력. 각 행이 선택지 풀 참조 + 추가 속성. |
| field_count | 4 |
| example_fields | process_list, equipment_list, process_worker_data, subcontractor |

**행동:** "여러 개를 표로 등록." → 선택지 풀에서 반복 선택 + 행별 속성(위험요인·인원).

**가장 복잡한 입력 패턴.** 공정/설비를 다수 등록하고 각각에 속성 부여. 관계망(input_staging_relation)으로 펼쳐짐.

---

### P6. EXTERNAL_LOOKUP (6개)

| 속성 | 값 |
|---|---|
| pattern_code | EXTERNAL_LOOKUP |
| pattern_name | 외부 API 자동 조회 |
| description | 소비자 입력 없이 주소 기반 건축물대장 API에서 자동 생성. |
| field_count | 6 |
| example_fields | total_floor_area, floor_count, basement_count, building_use_type, built_year, main_structure |

**행동:** "주소 입력 → 자동 채움." 소비자 미입력. 공공데이터 신뢰도.

**주의:** total_floor_area는 P2(THRESHOLD)이면서 P6(API)이다. 출처는 API, 용도는 임계 판정. 패턴 중복 케이스.

---

### P7. TEXT_TRIGGER (2개)

| 속성 | 값 |
|---|---|
| pattern_code | TEXT_TRIGGER |
| pattern_name | 텍스트 입력 (API 트리거) |
| description | 자유 텍스트지만 자체로는 의무 미발동. API 조회를 촉발하는 트리거. |
| field_count | 2 |
| example_fields | address, project_address |

**행동:** "주소 입력" → 건축물대장 API 호출 트리거. 입력값 자체는 매핑 대상 아님.

---

## 패턴 규모 요약

| 패턴 | 개수 | 비율 | 의무 발동 방식 |
|---|---|---|---|
| P1 BOOLEAN_EXISTENCE | 55 | 56% | true → 트리거 |
| P2 NUMERIC_THRESHOLD | 18 | 18% | 임계값 초과 → 트리거 |
| P3 NUMERIC_QUANTITY | 7 | 7% | 참고·결합 |
| P4 CODE_SELECT | 7 | 7% | 선택값 → 분류 |
| P6 EXTERNAL_LOOKUP | 6 | 6% | API 자동 |
| P5 TABLE_COLLECTION | 4 | 4% | 행별 트리거 |
| P7 TEXT_TRIGGER | 2 | 2% | API 트리거 |
| **합계** | **99** | | (total_floor_area 중복 1) |

*98개 필드 중 total_floor_area가 P2·P6 양쪽 집계되어 99.*

---

## 핵심 발견

### 발견 1: 입력세계는 사실상 2개 패턴이 지배

```
BOOLEAN_EXISTENCE (55) + NUMERIC_THRESHOLD (18) = 73개 (74%)

입력세계의 4분의 3이:
  "X가 있는가?" (boolean)
  "N이 임계값을 넘는가?" (threshold)

→ 법령 매핑의 핵심은 이 두 패턴.
→ 나머지 5개 패턴은 보조·참조·자동화.
```

### 발견 2: 법령 코드 패턴과 정확히 대응

```
WO-LAW-CODE-ARCHITECTURE-001의 법령 condition_pattern:
  HAS_WORK / HAS_EQUIPMENT / HAS_MATERIAL  ←→  P1 BOOLEAN_EXISTENCE
  NUMERIC_GTE / NUMERIC_RANGE              ←→  P2 NUMERIC_THRESHOLD
  SECTOR_SPECIFIC                          ←→  P4 CODE_SELECT

입력 패턴 7개 ←→ 법령 패턴이 1:1에 가깝게 대응.
→ 다음 단계(패턴 매핑)의 길이 열렸다.
```

### 발견 3: help_text가 THRESHOLD 매핑 사전

```
P2 필드의 help_text에 법정 임계값이 이미 명시:
  worker_count → 50인
  electric_capacity → 75kW
  excavation_depth → 2m
  max_work_height → 31m

→ NUMERIC_THRESHOLD 18개는 help_text만 읽어도
  법령 임계값 매핑 후보가 즉시 도출됨.
```

### 발견 4: total_floor_area = 패턴 중복 (정상)

```
출처(P6 API) ≠ 용도(P2 THRESHOLD)
입력값 하나가 "어떻게 들어오는가"와 "어떻게 쓰이는가"가 다름.
→ 패턴은 다차원. 출처 패턴 + 용도 패턴 분리 가능.
```

---

## 성공 기준 답변

> 98개 입력필드를 7개 패턴으로 설명할 수 있는가?

```
✅ 가능.

P1 BOOLEAN_EXISTENCE   55  존재 여부
P2 NUMERIC_THRESHOLD   18  임계 판정
P3 NUMERIC_QUANTITY     7  단순 수량
P4 CODE_SELECT          7  코드 선택
P5 TABLE_COLLECTION     4  복수 수집
P6 EXTERNAL_LOOKUP      6  API 자동
P7 TEXT_TRIGGER         2  API 트리거

이제 "98개 필드"가 아니라 "7개 패턴"으로 입력세계를 말할 수 있다.
핵심 가설 검증됨: 입력값은 98개지만 패턴은 7개.
```

---

## 다음 단계

```
WO-INPUT-PATTERN-DISCOVERY-001 (현재) — 완료
      ↓
WO-LAW-PATTERN-DISCOVERY-001 (권고)
  법령 의미절도 동일하게 패턴으로 압축
  (이미 LAW-CODE-ARCHITECTURE에서 4개 조문패턴 발견 — 정밀화)
      ↓
WO-PATTERN-MAPPING-001
  입력 패턴 7개 ←→ 법령 패턴 N개 연결
  P1 BOOLEAN ←→ HAS_WORK/EQUIPMENT/MATERIAL
  P2 THRESHOLD ←→ NUMERIC_GTE
  (드디어 패턴 대 패턴 매핑 시작)
```

---

*WO-INPUT-PATTERN-DISCOVERY-001 완료.*
*98개 입력필드 → 7개 패턴. BOOLEAN(55)+THRESHOLD(18)이 74% 지배.*
*핵심: 입력 패턴 7개가 법령 패턴과 1:1 대응. 패턴 매핑의 길 열림.*
