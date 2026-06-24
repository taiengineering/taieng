# WO-CANDIDATE-HARVEST-001
# Trigger 기반 후보군 수확

**작성일:** 2026-06-24 | **상태:** 완료 (수확 전용)
**선행:** WO-SCOPE-FILTER-001
**금지:** CONFIRMED 판정 / condition_mapping INSERT / REVIEW 상태 변경 / 정확도 평가 / 오탐 제거
**목적:** 현재 구조로 몇 개의 후보 의무를 자동 수확할 수 있는가?

> 이 단계는 수확(Harvest)이다. 맞다/틀리다 판단 안 함. CONFIRMED 아님.
> 신규 테이블 candidate_harvest 사용 (condition_mapping_candidate 무수정).

---

## 결론 먼저

```
현재 구조로 813건 후보 자동 수확.
distinct 조문 기준 649건.

수확 분포:
  TRUE_UNIVERSAL    310  (sector 기반, 입력 무관)
  WORK_EXISTS       233  (작업 12종)
  MATERIAL_EXISTS   157  (물질 5종)
  EQUIPMENT_EXISTS   90  (설비 12종)
  FACILITY_EXISTS    21  (시설 4종)
  DIRECT_THRESHOLD    2  (본조 직접 수치)
  ─────────────────────
  합계              813건 (중복 포함)

3단계 상태 구조:
  HARVESTED → REVIEW → CONFIRMED
  현재 전부 HARVESTED.
```

---

## TASK-001: SCOPE FILTER 적용 (먼저)

```
모든 수확 쿼리에 SCOPE FILTER를 Trigger 매핑보다 먼저 적용:

NOT (source_text||action_text ~
  '(사업주체|입주자|공급계약|분양|사용검사|간선시설|
    파견사업주|사용사업주|파견근로|근로자파견|
    관리비|장기수선|충당금|입주자대표|
    보험료|월별보험료|징수|
    출산전후|육아휴직|모성보호)')

→ 범위 밖 191건이 애초에 수확 대상에서 제외됨.
→ 분양·파견·관리비·보험료 의무가 후보에 안 들어옴.
```

---

## TASK-002: EXISTS Trigger 군 수확 (501건)

### WORK_EXISTS — 233건

| 입력필드 | L2 | 수확 |
|---|---|---|
| has_demolition | DEMOLITION | 39 |
| has_diving | DIVING | 27 |
| has_asbestos_demo | ASBESTOS | 23 |
| has_excavation | EXCAVATION | 23 |
| has_scaffold | SCAFFOLD | 22 |
| has_confined_space | CONFINED_SPACE | 22 |
| has_high_place_work | HIGH_PLACE | 19 |
| has_welding | WELDING | 18 |
| has_pile_work | PILE_WORK | 17 |
| has_radiation | RADIATION | 12 |
| has_dust_work | DUST | 7 |
| has_blasting | BLASTING | 4 |

### MATERIAL_EXISTS — 157건

| 입력필드 | 수확 |
|---|---|
| has_hazardous_material | 68 |
| has_dust_work (분진) | 37 |
| has_chemical_substance | 29 |
| has_asbestos | 23 |

### EQUIPMENT_EXISTS — 90건

| 입력필드 | 수확 |
|---|---|
| has_crane | 25 |
| has_elevator (리프트) | 14 |
| has_conveyor | 7 |
| has_pressure_vessel | 7 |
| has_forklift | 7 |
| has_tower_crane | 7 |
| has_grinding | 6 |
| has_boiler | 5 |
| has_press | 4 |

### FACILITY_EXISTS — 21건

| 입력필드 | 수확 |
|---|---|
| has_confined_space | 21 |

---

## TASK-003: DIRECT_THRESHOLD 수확 (2건)

```
APPENDIX 제외, 본조 직접 수치만:
  AREA (연면적): 1건
  DEPTH (굴착깊이): 1건

→ 예상대로 본조 직접 수치는 희소(2건).
→ 대부분의 THRESHOLD는 APPENDIX(별표)에 위임 (이번 수확 제외).
→ worker_count 등 APPENDIX_THRESHOLD는 appendix_condition 입력 후 수확.
```

---

## TASK-004: TRUE_UNIVERSAL 수확 (310건)

```
condition_text NULL + action_text에 숨은조건 없음 = 진짜 무조건:

EDUCATION  교육·훈련
REPORT     보고·신고·제출
POSTING    비치·게시·부착
DOCUMENT   작성·기록·보존
INSPECT    점검·검사·측정
GENERAL    기타 일반

→ sector 소속만으로 발동. 입력 무관.
→ 진단의 baseline. ksic_major 선택 시 일괄 후보.
→ HIERARCHY-001에서 추정한 359건과 근접(310, SCOPE 필터로 일부 제거됨).
```

---

## TASK-005: 후보군 저장 형식

```
candidate_harvest 테이블 (신규):
  status = 'HARVESTED' (전체)

3단계 상태 구조:
  HARVESTED  ← 현재 (자동 수확)
      ↓
  REVIEW     ← 다음 (조문 직독 검증)
      ↓
  CONFIRMED  ← 최종 (확정)

→ condition_mapping_candidate(기존 77 CONFIRMED)와 분리.
→ 수확과 확정을 물리적으로 다른 테이블에 보관.
```

---

## TASK-006: Trigger별 후보량

| Trigger L1 | 수확량 | distinct 입력필드 |
|---|---|---|
| TRUE_UNIVERSAL | 310 | (sector) |
| WORK_EXISTS | 233 | 12 |
| MATERIAL_EXISTS | 157 | 4 |
| EQUIPMENT_EXISTS | 90 | 9 |
| FACILITY_EXISTS | 21 | 1 |
| DIRECT_THRESHOLD | 2 | 2 |
| **합계** | **813** | |

```
distinct 조문: 649건
중복 포함:     813건
중복분:        164건
```

---

## TASK-007: 오탐 유형 수집 (제거 안 함, 기록만)

### 측정된 오탐 유형

| 오탐 유형 | 건수 | 설명 |
|---|---|---|
| MULTI_TRIGGER (Trigger 중복) | 88 조문 | 한 조문이 2개+ Trigger에 수확 |
| MULTI_FIELD (입력필드 중복) | 81 조문 | 한 조문이 2개+ 입력필드에 수확 |

### Trigger 중복 대표 사례 (직독)

```
사례 1: 곤돌라형 달비계 설치
  → EQUIPMENT(GONDOLA) + WORK(SCAFFOLD) 동시 수확
  → 곤돌라(설비)이면서 비계(작업) — 둘 다 맞음 (중복 정상)

사례 2: 석면해체 개인보호구 지급
  → MATERIAL(ASBESTOS) + WORK(ASBESTOS) + WORK(DEMOLITION)
  → 석면(물질)이면서 해체작업(작업) — 3중 수확
  → 같은 의무가 여러 입력에서 도달 가능 (정상적 다중경로)

사례 3: 자동차정비용 리프트 탑승금지
  → EQUIPMENT(LIFT) + TRUE_UNIVERSAL(GENERAL)
  → 리프트 의무인데 UNIVERSAL에도 잡힘 (오분류 가능)
  → UNIVERSAL 수확이 EXISTS와 겹침 → REVIEW에서 정리 필요

사례 4: 밀폐공간 환기
  → FACILITY(CONFINED) + WORK(CONFINED_SPACE)
  → 밀폐공간이 시설이자 작업 — 경계 중첩 (정상)
```

### 오탐 유형 분류 (제거 안 함)

```
TYPE-A 정상 다중경로 (제거 불필요):
  석면=물질+작업, 곤돌라=설비+비계
  → 같은 의무에 여러 입력이 도달. 진단상 문제없음.

TYPE-B UNIVERSAL 중첩 (REVIEW 필요):
  EXISTS로 수확된 게 UNIVERSAL에도 잡힘
  → 리프트 탑승금지가 양쪽에. UNIVERSAL 과수확 가능성.
  → REVIEW에서 EXISTS 우선 배정.

TYPE-C 키워드 광범위 (REVIEW 필요):
  has_dust_work가 WORK(7)+MATERIAL(37) 양쪽
  → 분진이 작업이자 물질. L1 경계 모호.

TYPE-D 범위 잔여 (SCOPE 추가 검토):
  현재 SCOPE 필터 통과했으나 의심스러운 것
  → REVIEW에서 추가 확인.
```

---

## 핵심 발견

### 발견 1: 현재 구조로 813건 자동 수확

```
사람 개입 없이 입력→Trigger→법령 구조만으로
813개 후보 의무를 자동 추출.

→ 기존 CONFIRMED 77건 대비 10배 규모.
→ 17회차 만에 처음으로 "자동 수확"이 작동.
```

### 발견 2: UNIVERSAL이 최대 수확 (310건, 38%)

```
sector 기반 무조건 의무가 가장 많이 수확됨.
→ 진단의 baseline은 sector 선택만으로 310건.
→ has_* 입력은 그 위에 EXISTS 503건 추가.
→ 전형적 사업장: UNIVERSAL 310 + 해당 EXISTS 수십개.
```

### 발견 3: 중복 164건은 대부분 정상 다중경로

```
석면=물질+작업, 곤돌라=설비+비계 등
같은 의무에 여러 입력이 도달하는 것은 자연스러움.

→ 제거 대상이 아니라 "어느 입력으로 도달했는지" 기록.
→ REVIEW에서 대표 입력 1개 선정 또는 다중 유지 결정.
```

### 발견 4: DIRECT_THRESHOLD 2건 = APPENDIX 병목 재확인

```
본조 직접 수치 의무는 2건뿐.
worker_count, 면적 기준 등 대부분이 APPENDIX(별표) 위임.
→ appendix_condition 7건 입력이 THRESHOLD 수확의 병목.
→ 별표 데이터 입력이 다음 큰 과제.
```

---

## 성공 기준 답변

> 현재 구조만으로 몇 개 후보를 자동 수확할 수 있는가?

```
813건 (distinct 조문 649건).
  TRUE_UNIVERSAL 310 / WORK 233 / MATERIAL 157 /
  EQUIPMENT 90 / FACILITY 21 / DIRECT_THRESHOLD 2
```

> 수확된 후보의 주요 오탐 패턴은 무엇인가?

```
TYPE-A 정상 다중경로 (석면=물질+작업) — 제거 불필요
TYPE-B UNIVERSAL 중첩 (EXISTS와 겹침) — REVIEW 정리
TYPE-C 키워드 광범위 (분진=작업+물질) — L1 경계 정리
TYPE-D 범위 잔여 — SCOPE 추가 검토

중복 164건 = 88 Trigger중복 + 81 입력필드중복.
대부분 TYPE-A(정상). TYPE-B/C가 REVIEW 대상.
```

---

## 다음 단계

```
WO-CANDIDATE-HARVEST-001 (현재) — 완료
      ↓
WO-CANDIDATE-REVIEW-001
  HARVESTED 813건 → 조문 직독 REVIEW
  - TYPE-B UNIVERSAL 중첩 정리 (EXISTS 우선)
  - TYPE-C 키워드 경계 정리 (분진 등)
  - 각 후보 1문장 설명 검증 (VALIDATION-001 방식)
  - REVIEW 통과분만 CONFIRMED 승격
  주의: 숫자 아닌 조문 텍스트 직독으로 검증
      ↓
WO-APPENDIX-HARVEST-001 (병행 가능)
  appendix_condition 별표 데이터 입력
  → APPENDIX_THRESHOLD 수확 (worker_count 등)
```

---

*WO-CANDIDATE-HARVEST-001 완료. 813건 자동 수확. HARVESTED 상태.*
*UNIVERSAL 310 최대. EXISTS 501. 중복 164(대부분 정상 다중경로).*
*핵심: 17회차 만에 자동 수확 작동. condition_mapping_candidate 무수정. REVIEW는 다음 단계.*
