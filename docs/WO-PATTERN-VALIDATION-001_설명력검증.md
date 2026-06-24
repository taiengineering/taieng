# WO-PATTERN-VALIDATION-001
# 기존 매핑 설명력 검증

**작성일:** 2026-06-24 | **상태:** 완료 (읽기 전용)
**선행:** WO-PATTERN-CROSSMAP-001
**금지:** 신규 매핑 / 후보군 / INSERT / UPDATE / Trigger 추가 / 패턴 추가 / DDL
**질문:** 입력패턴 → Trigger → 의무 구조가 기존 CONFIRMED 77건을 설명할 수 있는가?

---

## 결론 먼저

```
77건 중 77건(100%)이 입력패턴 → Trigger → 의무 구조로 설명된다.

전부 P1 BOOLEAN_EXISTENCE 입력.
전부 EXISTS 계열 Trigger (WORK/EQUIPMENT/MATERIAL/FACILITY).
EXPLAINABLE 73건 / PARTIAL 4건 / UNEXPLAINABLE 0건.

구조는 살아남았다. 단, 한 가지 발견:
  has_high_pressure_gas가 3개 개념(압력용기/잠함/항타기)에 과적재됨.
  → 구조 문제 아님. 입력필드 분리 문제(이미 알려진 이슈).
```

---

## 산출물 A: 77건 분류표

### 입력패턴 분류 (TASK-002)

| 입력필드 | 입력값 | 입력 패턴 | 건수 |
|---|---|---|---|
| has_asbestos_demo | true | **P1 BOOLEAN_EXISTENCE** | 7 |
| has_blasting | true | P1 BOOLEAN_EXISTENCE | 2 |
| has_boiler | true | P1 BOOLEAN_EXISTENCE | 4 |
| has_chemical_substance | true | P1 BOOLEAN_EXISTENCE | 24 |
| has_confined_space | true | P1 BOOLEAN_EXISTENCE | 16 |
| has_diving | true | P1 BOOLEAN_EXISTENCE | 14 |
| has_high_pressure_gas | true | P1 BOOLEAN_EXISTENCE | 5 |
| has_tower_crane | true | P1 BOOLEAN_EXISTENCE | 5 |

**77건 전부 P1 BOOLEAN_EXISTENCE.** 다른 입력 패턴 없음.

### Trigger 분류 (TASK-003)

| 입력필드 | condition_type | 법령 Trigger | 건수 |
|---|---|---|---|
| has_chemical_substance | MATERIAL_ACT | **MATERIAL_EXISTS** | 24 |
| has_confined_space | WORK_ACT | **WORK_EXISTS** | 16 |
| has_diving (WORK) | WORK_ACT | WORK_EXISTS | 9 |
| has_diving (EQUIP) | EQUIPMENT_ACT | **EQUIPMENT_EXISTS** | 5 |
| has_asbestos_demo | WORK_ACT | WORK_EXISTS | 7 |
| has_boiler | EQUIPMENT_ACT | EQUIPMENT_EXISTS | 4 |
| has_tower_crane (EQUIP) | EQUIPMENT_ACT | EQUIPMENT_EXISTS | 3 |
| has_tower_crane (WORK) | WORK_ACT | WORK_EXISTS | 2 |
| has_high_pressure_gas (EQUIP) | EQUIPMENT_ACT | EQUIPMENT_EXISTS | 2 |
| has_high_pressure_gas (WORK) | WORK_ACT | WORK_EXISTS | 2 |
| has_high_pressure_gas (FACILITY) | FACILITY_ACT | **FACILITY_EXISTS** | 1 |
| has_blasting (WORK) | WORK_ACT | WORK_EXISTS | 1 |
| has_blasting (FACILITY) | FACILITY_ACT | FACILITY_EXISTS | 1 |

### Trigger 분포 집계

```
MATERIAL_EXISTS:  24 (화학물질)
WORK_EXISTS:      37 (밀폐공간16+잠수9+석면7+타워크레인2+고압가스2+발파1)
EQUIPMENT_EXISTS: 14 (잠수5+보일러4+타워크레인3+압력용기2)
FACILITY_EXISTS:   2 (발파1+고압가스1)
─────────────────────
합계:             77
```

**기존 condition_type(WORK_ACT/EQUIPMENT_ACT/MATERIAL_ACT/FACILITY_ACT)이
새 Trigger 체계(WORK/EQUIPMENT/MATERIAL/FACILITY_EXISTS)와 정확히 1:1 대응.**

---

## 산출물 B: EXPLAINABLE / PARTIAL / UNEXPLAINABLE 분포

| 판정 | 건수 | 비율 |
|---|---|---|
| EXPLAINABLE | 73 | 95% |
| PARTIAL | 4 | 5% |
| UNEXPLAINABLE | 0 | 0% |

### EXPLAINABLE 73건 — 1문장 설명 성립

```
예시 (조문 직독 검증):

has_diving=true → WORK_EXISTS(잠수작업) → "잠수기록표 작성·3년 보존"
  설명: 잠수작업이 있으므로(입력) 잠수작업 트리거가 발동하여(Trigger)
        잠수기록 의무가 나온다(의무). ✅

has_boiler=true → EQUIPMENT_EXISTS(보일러) → "압력방출장치 설치"
  설명: 보일러가 있으므로 보일러 트리거가 발동하여
        압력방출장치 의무가 나온다. ✅

has_chemical_substance=true → MATERIAL_EXISTS(유해물질) → "국소배기장치 설치"
  설명: 화학물질을 취급하므로 물질 트리거가 발동하여
        국소배기 의무가 나온다. ✅

has_confined_space=true → WORK_EXISTS(밀폐공간) → "산소농도 측정"
  설명: 밀폐공간 작업이 있으므로 작업 트리거가 발동하여
        측정 의무가 나온다. ✅
```

---

## 산출물 C: 설명 불가/부분 사례 (PARTIAL 4건)

설명은 되나 입력필드가 부정확한 케이스:

### has_high_pressure_gas 과적재 (4건 PARTIAL)

```
입력필드 has_high_pressure_gas가 3개의 다른 개념을 트리거:

1. EQUIPMENT_ACT (압력용기) 2건
   "압력용기등에 덮개·울 설치"
   → 실제 트리거는 "압력용기 보유"이지 "고압가스"가 아님
   → 정확한 입력필드: has_pressure_vessel

2. WORK_ACT (잠함/항타기) 2건
   "잠함을 물속으로 가라앉히는 경우"
   "압축공기 동력원 항타기·항발기 사용"
   → 실제 트리거는 "잠함작업"/"항타기 사용"
   → 정확한 입력필드: has_caisson / has_pile_work

3. FACILITY_ACT (기압조절실) 1건 — EXPLAINABLE
   "작업실 또는 기압조절실 공기압축기"
   → 고압작업 시설 관련, 그나마 근접
```

**PARTIAL 판정 이유:**
```
입력 → Trigger → 의무 구조 자체는 작동.
단, has_high_pressure_gas라는 입력이
실제로는 압력용기/잠함/항타기 3개 트리거를 발생시킴.

→ 구조 문제 아님.
→ 입력필드 1개가 3개 트리거에 과적재된 문제.
→ 이미 WO-INPUT-MODEL-AUDIT-001에서 발견된 이슈.
→ 입력 boundary에서 has_pressure_vessel/has_pile_work가
  이미 별도 필드로 존재함이 확인됨(BOUNDARY-001).
```

---

## 산출물 D: 구조 보완 필요 목록

### 구조는 수정 불필요 — 입력필드만 정정

| 항목 | 판정 | 조치 |
|---|---|---|
| 입력 → Trigger → 의무 구조 | ✅ 유지 | 수정 불필요 |
| Trigger 체계 (4 EXISTS) | ✅ 유지 | WORK/EQUIPMENT/MATERIAL/FACILITY 검증됨 |
| 입력 패턴 (P1 BOOLEAN) | ✅ 유지 | 77건 전부 설명 |
| has_high_pressure_gas 과적재 | ⚠️ 정정 | has_pressure_vessel/has_caisson/has_pile_work로 분리 |
| APPENDIX 보강 | (해당없음) | 77건에 THRESHOLD 없음 |
| COMPOUND 보강 | (해당없음) | 77건에 COMPOUND 없음 |

---

## 핵심 발견

### 발견 1: 구조가 100% 설명력을 가진다

```
77건 전부 입력패턴 → Trigger → 의무로 설명됨.
UNEXPLAINABLE 0건.

→ WO-CROSSMAP에서 정의한 "P1 BOOLEAN ↔ EXISTS = DIRECT"가
  실제 CONFIRMED 데이터에서 100% 검증됨.
→ 구조는 살아남았다.
```

### 발견 2: 기존 condition_type = 새 Trigger 체계

```
기존 WORK_ACT     = WORK_EXISTS
기존 EQUIPMENT_ACT = EQUIPMENT_EXISTS
기존 MATERIAL_ACT  = MATERIAL_EXISTS
기존 FACILITY_ACT  = FACILITY_EXISTS

→ 우연이 아니라, 77건이 이미 Trigger 사고로 만들어졌음.
→ 새 패턴 체계가 기존 작업과 정합.
```

### 발견 3: 77건은 전부 P1 BOOLEAN/EXISTS만

```
THRESHOLD 0건
COMPOUND 0건
UNIVERSAL 0건
FRAGMENT 0건

→ 가장 쉬운 DIRECT 케이스만 CONFIRMED 되어 있음.
→ 어려운 케이스(THRESHOLD/UNIVERSAL)는 아직 미착수.
→ 다음 후보군 생성은 나머지 BOOLEAN(has_*) 먼저,
  그 다음 THRESHOLD로 가야 함.
```

### 발견 4: 입력필드 분리가 유일한 실제 보완점

```
has_high_pressure_gas 1개 → 3개 트리거 과적재.

이미 입력 boundary(BOUNDARY-001)에서 확인:
  has_pressure_vessel 존재
  has_pile_work 존재

→ 이 필드로 재매핑하면 PARTIAL 4건이 EXPLAINABLE로 전환.
→ 구조 수정 아니라 입력필드 교체 작업.
```

---

## 산출물 E: 다음 단계 권고

```
구조 판정: 현재 구조 유지 (수정 불필요)

근거:
  ✅ 77건 100% 설명 가능
  ✅ Trigger 체계 검증됨
  ✅ P1 BOOLEAN → EXISTS = DIRECT 확정
  ⚠️ has_high_pressure_gas 분리만 필요 (입력필드 문제, 구조 무관)

→ 구조가 살아남았으므로 후보군 생성 진행 가능.

다음 WO-PATTERN-CANDIDATE-GENERATION-001 범위:
  1순위: 나머지 P1 BOOLEAN has_* (현재 미매핑된 boolean들)
         has_press, has_crane, has_welding, has_excavation 등
         → EXISTS Trigger 후보 생성
  2순위: P2 THRESHOLD → DIRECT_THRESHOLD (building_area 등)
  보류:  APPENDIX_THRESHOLD (appendix 입력 선행)
  정정:  has_high_pressure_gas → 3개 필드 분리 후 재매핑
```

---

## 성공 기준 답변

> 현재 구조로 77개 CONFIRMED 매핑을 몇 % 설명 가능한가?

```
100% (77/77)
  EXPLAINABLE 73 (95%)
  PARTIAL 4 (5%) — 설명되나 입력필드 부정확
  UNEXPLAINABLE 0
```

> 설명 불가능한 매핑은 왜 설명이 안 되는가?

```
설명 불가능(UNEXPLAINABLE)은 0건.

부분 설명(PARTIAL) 4건의 원인:
  has_high_pressure_gas 입력필드가
  압력용기/잠함/항타기 3개 트리거에 과적재됨.

→ 구조의 문제가 아니라 입력필드 설계 문제.
→ 입력필드를 분리하면 100% EXPLAINABLE.
```

**결론: 구조는 살아남았다. 후보군 생성으로 진행 가능.**

---

*WO-PATTERN-VALIDATION-001 완료. 읽기 전용. INSERT/UPDATE 없음.*
*77건 100% 설명. 전부 P1 BOOLEAN → EXISTS Trigger. 구조 검증 통과.*
*유일 보완: has_high_pressure_gas 3개 필드 분리 (구조 무관, 입력필드 문제).*
