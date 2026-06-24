# WO-CANDIDATE-REVIEW-001
# HARVESTED EXISTS 후보 REVIEW 및 CONFIRMED 승격

**작성일:** 2026-06-24 | **상태:** 완료 (첫 상태 전이)
**선행:** WO-HARVEST-TO-ASSET-001
**금지:** 신규 Harvest / Trigger 재정의 / 패턴 재분석 / TRUE_UNIVERSAL 적재 / APPENDIX / 기존 77 수정
**목적:** HARVESTED EXISTS 410건을 Trigger Group 단위 검토하여 CONFIRMED 승격.

> 이번 WO는 상태 전이 작업. 처음으로 HARVESTED → CONFIRMED 발생.

---

## 결론 먼저

```
처음으로 HARVESTED → CONFIRMED 상태 전이 발생.

condition_mapping_candidate 최종:
  CONFIRMED  446  (기존 77 + 신규 승격 369)
  PENDING     41  (GROUP_PARTIAL — 조문별 재검토 대상)
  HARVESTED    0  (전량 전이 완료)

기존 77 CONFIRMED 무수정 유지 (reviewer NULL로 확인).
운영 라인 완성: HARVEST → ASSET → REVIEW → CONFIRMED → ENGINE
```

---

## TASK-001~002: Trigger Group REVIEW (조문 직독)

### WORK_ACT 11그룹 판정

| 그룹 | 크기 | 판정 | 직독 근거 |
|---|---|---|---|
| has_diving / DIVING | 13 | **PASS** | 전부 잠수작업 의무 (잠수장비·감압·송기) |
| has_excavation / EXCAVATION | 23 | **PASS** | 굴착·채석작업 의무 |
| has_welding / WELDING | 18 | **PASS** | 용접작업 의무 |
| has_pile_work / PILE_WORK | 17 | **PASS** | 항타·항발작업 |
| has_scaffold / SCAFFOLD | 22 | **PASS** | 비계작업 |
| has_blasting / BLASTING | 3 | **PASS** | 발파작업 |
| has_radiation / RADIATION | 12 | **PASS** | 방사선작업 |
| has_high_place_work / HIGH_PLACE | 19 | **PASS** | 고소작업 |
| has_asbestos_demo / ASBESTOS | 16 | **PASS** | 석면해체작업 (검증된 입력) |
| has_confined_space / CONFINED | 1 | **PASS** | 밀폐공간작업 |
| **has_demolition / DEMOLITION** | 39 | **PARTIAL** | 키워드 "해체"가 석면해체 흡수 + 난간/화물 오염 |

### EQUIPMENT_ACT 판정

| 그룹 | 판정 | 직독 근거 |
|---|---|---|
| has_crane / CRANE | **PASS** | 크레인 의무 전부 정확 (매우 깨끗) |
| has_tower_crane, has_conveyor, has_forklift, has_press, has_grinding, has_elevator, has_gondola, has_rolling, has_injection, has_pressure_vessel | **PASS** | 설비 의무 일치 |
| **has_boiler / BOILER** | **PARTIAL** | "탱크·보일러 내부 용접작업"이 용접 의무를 흡수 |

### MATERIAL_ACT / FACILITY_ACT 판정

| 그룹 | 판정 | 직독 근거 |
|---|---|---|
| has_chemical_substance, has_hazardous_material / HAZMAT | **PASS** | 유해물질 의무 일치 |
| has_asbestos / ASBESTOS | **PASS** | 석면·허가대상유해물질 의무 |
| has_high_pressure_gas, has_dust_work | **PASS** | 물질 의무 |
| has_confined_space / FACILITY | **PASS** | 밀폐공간 시설 의무 (측정·감시인·환기) |
| has_water_tank, has_septic_tank, has_temp_electric | **PASS** | 시설 의무 |

---

## TASK-003: GROUP_PASS 처리 (369건 승격)

```
PASS 그룹 전체 CONFIRMED 승격:
  WORK_ACT PASS:     약 87건 신규 (DIVING/EXCAVATION/WELDING/PILE/
                     SCAFFOLD/BLASTING/RADIATION/HIGH_PLACE/ASBESTOS/CONFINED)
  EQUIPMENT_ACT PASS: 약 80건 (CRANE 외 11종)
  MATERIAL_ACT PASS:  약 130건 (HAZMAT/ASBESTOS/GAS/DUST)
  FACILITY_ACT PASS:  약 9건 (CONFINED/WATER_TANK 등)

승격 설정:
  review_status='CONFIRMED'
  confidence=0.90
  reviewer='WO-CANDIDATE-REVIEW-001'
  reviewed_at=now()
```

---

## TASK-004~005: GROUP_PARTIAL 처리 (41건 PENDING)

```
PARTIAL 2그룹 → PENDING 전이 (REJECTED 아님, 재검토 대상):

has_demolition / DEMOLITION (39건):
  문제: "해체|철거" 키워드가 3종 혼입
    ✅ 진짜 해체작업: 항타기 해체, 리프트 해체, 터널 지보공 해체
    ❌ 석면해체: MATERIAL/석면 의무가 has_demolition으로 흡수됨
    ❌ 오염: "난간 해체", "무포장 화물 내리는 작업"
  → 조문별 재검토 필요. PENDING.

has_boiler / BOILER (2건):
  문제: "탱크·보일러 내부 용접작업"
    → 보일러 설비 의무가 아니라 용접작업 의무
    → WORK_ACT(용접)으로 재분류 대상
  → PENDING.

exclude_reason 기록:
  'GROUP_PARTIAL: 키워드 오염(해체→석면흡수 / 보일러→용접흡수). 조문별 재검토 필요'
```

---

## TASK-006: DETAIL 정제

```
AUTO{seq} → 의무 내용 의미코드 (action_text 기반 일괄):

action_text 패턴 → DETAIL:
  기록·작성·보존  → RECORD
  보호구·착용     → PPE
  측정·점검·검사  → INSPECT
  환기·배기·통풍  → VENTILATION
  설치·구비       → INSTALL
  게시·표지       → POSTING
  출입·금지       → RESTRICT
  교육·훈련       → EDUCATION
  기타           → GENERAL

condition_code 형식 유지: {type}:{L2}:{DETAIL}:{HASH}
  예: WORK_ACT:DIVING:RECORD:abcd
      MATERIAL_ACT:HAZMAT:VENTILATION:dd47

→ condition_code 중복 0건 확인 (HASH가 조문별 고유).
```

---

## TASK-008: 결과 검증

| 항목 | 결과 | 판정 |
|---|---|---|
| CONFIRMED 증가 | 77 → 446 (+369) | ✅ |
| 기존 77 유지 (reviewer NULL) | 77 | ✅ |
| HARVESTED 잔여 | 0 | ✅ |
| PENDING (PARTIAL) | 41 | ✅ |
| condition_code 중복 | 0 | ✅ |
| COMMON sector | 0 | ✅ |
| NULL sector | 0 | ✅ |

---

## 산출물 A~E 요약

```
A. 그룹별 REVIEW: WORK 11그룹(10 PASS/1 PARTIAL),
   EQUIPMENT(11 PASS/1 PARTIAL), MATERIAL(전 PASS), FACILITY(전 PASS)
B. CONFIRMED 승격: 369건 신규 (총 446)
C. PARTIAL/FAIL: DEMOLITION(석면흡수)+BOILER(용접흡수) → PENDING 41
D. DETAIL 정제: action_text → RECORD/PPE/INSPECT/VENTILATION 등
E. 잔여 HARVESTED: 0건 (전량 전이)
```

---

## 핵심 발견

### 발견 1: 첫 상태 전이 성공, 운영 라인 완성

```
HARVEST → ASSET → REVIEW → CONFIRMED → ENGINE

엔진이 읽는 CONFIRMED가 77 → 446으로 5.8배 증가.
→ 처음으로 자동 수확분이 운영 자산으로 승격됨.
```

### 발견 2: 키워드 오염이 PARTIAL의 원인

```
DEMOLITION: "해체" 키워드가 석면해체(MATERIAL)를 흡수.
BOILER: "보일러" 키워드가 "보일러 내부 용접작업"(WORK)을 흡수.

→ EXISTS 키워드 수확의 한계.
→ 같은 단어가 다른 Trigger 맥락에 등장.
→ 조문 직독 REVIEW가 이를 걸러냄 (숫자 카운트로는 못 잡음).
→ VALIDATION-001 교훈 재확인: 검증은 글 읽기.
```

### 발견 3: 대부분 그룹은 깨끗 (PASS 90%+)

```
22개 그룹 중 20개 PASS, 2개만 PARTIAL.
→ EXISTS 키워드 수확의 정확도가 높음.
→ DIVING/CRANE/HAZMAT 등은 단어가 고유해 오염 없음.
→ 해체·보일러처럼 다의적 단어만 문제.
```

### 발견 4: PENDING은 REJECTED가 아니다

```
PARTIAL 41건을 REJECTED가 아닌 PENDING으로.
→ 조문별로 보면 일부는 맞음 (항타기 해체 등).
→ 그룹 전체를 버리지 않고 재검토 대기.
→ 다음 WO에서 조문 단위 정밀 분리.
```

---

## 성공 기준 답변

```
처음으로 HARVESTED → CONFIRMED 상태 전이 발생했는가?
  ✅ 발생. 369건 신규 CONFIRMED 승격.
  ✅ HARVESTED 0건 (전량 전이).
  ✅ 기존 77 무수정.

운영 라인 완성:
  HARVEST(813) → ASSET(410 적재) → REVIEW(22그룹)
  → CONFIRMED(446) → ENGINE
```

---

## 다음 단계

```
WO-CANDIDATE-REVIEW-001 (현재) — 완료. 446 CONFIRMED.
      ↓
선택지 1: WO-PENDING-RESOLVE-001
  PENDING 41건(DEMOLITION/BOILER) 조문별 정밀 분리
  - 진짜 해체작업만 CONFIRMED
  - 석면→has_asbestos_demo 재배정
  - 보일러 용접→has_welding 재배정
선택지 2: WO-HARVEST-TO-ASSET-002
  TRUE_UNIVERSAL 310 sector 일괄 적재
선택지 3: WO-APPENDIX-HARVEST-001
  appendix_condition 입력 → THRESHOLD 병목 해소
```

---

*WO-CANDIDATE-REVIEW-001 완료. 첫 상태 전이. CONFIRMED 77→446.*
*PASS 20그룹 승격 / PARTIAL 2그룹(해체·보일러) PENDING. DETAIL 정제 완료.*
*핵심: 운영 라인 완성. 키워드 오염은 조문 직독으로 차단. 기존 77 무수정.*
