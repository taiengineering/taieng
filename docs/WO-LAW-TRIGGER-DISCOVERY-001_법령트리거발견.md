# WO-LAW-TRIGGER-DISCOVERY-001
# 법령 Trigger 패턴 발견

**작성일:** 2026-06-24 | **상태:** 완료 (법령세계 Trigger 압축 전용)
**선행:** WO-LAW-PATTERN-DISCOVERY-001
**금지:** 입력필드 연결 / 입력패턴 연결 / 매핑 생성 / condition_mapping 수정 / 후보군 생성
**목적:** 58,495 조문을 "무슨 의무인가"가 아니라 "왜 그 의무가 발생하는가(Trigger)"로 분류한다.

> Role은 매핑 대상이 아니다. 실제 매핑되는 것은 입력 → Trigger → 의무.
> 이번 WO는 법령세계의 Trigger만 본다.

---

## 결론 먼저

```
법령 의무의 발생 원인(Trigger)은 8종으로 압축된다.

WORK_EXISTS       작업 수행이 원인
EQUIPMENT_EXISTS  설비 보유가 원인
MATERIAL_EXISTS   물질 취급이 원인
FACILITY_EXISTS   시설·장소가 원인
THRESHOLD         수치 초과가 원인 (본조 30 + 별표위임 102)
COMPOUND          복합 조건이 원인
UNIVERSAL         조건 없이 sector 소속만으로 발동 (644)
FRAGMENT          상위 조문 의존 (46, 격리)
```

---

## TASK-001~002: L1 ACTIVITY Trigger 원인 귀납

L1 ACTIVITY_OBLIGATION의 의무 발생 원인 분류:

| Trigger | 건수 | 원인 |
|---|---|---|
| WORK_EXISTS | 189 | "~작업하는 경우" — 작업 수행이 원인 |
| OTHER | 188 | 복합/기타 표현 |
| EQUIPMENT_EXISTS | 153 | "~설치/사용/운전" — 설비 보유가 원인 |
| MATERIAL_EXISTS | 45 | "~취급/물질/가스" — 물질 취급이 원인 |
| FACILITY_EXISTS | 17 | "~장소/공간/작업장" — 시설이 원인 |

**핵심:** 작업(WORK) + 설비(EQUIPMENT)가 의무 발생 원인의 대부분.
"무슨 작업을 하는가", "무슨 설비가 있는가"가 의무를 촉발.

---

## TASK-003: L4 NUMERIC 본조 수치 유형

| threshold_type | compound | 건수 |
|---|---|---|
| OTHER_NUMERIC | SINGLE | 10 |
| CAPACITY_THRESHOLD (톤/리터/kg) | SINGLE | 7 |
| OTHER_NUMERIC | COMPOUND | 3 |
| COUNT_THRESHOLD (명) | COMPOUND | 1 |

**본조 직접 수치는 희소(약 21건).** 대부분 별표로 위임(L5).

---

## TASK-004: L5 DELEGATION_THRESHOLD — Appendix 의존

```
사업주·관리주체 위임 조문 (별표/대통령령 참조): 25건
appendix_condition 실제 입력: 7건

→ 위임 구조:
  본조 "안전관리자를 둔다" (수치 없음)
    ↓ 대통령령으로 정한다
  시행령 별표 "50인 이상" (실제 임계값)
    ↓
  appendix_condition (7건만 입력 — 병목)

THRESHOLD 의무의 진짜 원인은 별표(appendix)에 있으나
현재 7건만 입력되어 대부분의 THRESHOLD Trigger가 비어 있음.
```

**대표 사례:**
```
법17조 안전관리자 → 시행령 별표3 → appendix(50/500/1000인)
법19조 관리담당자 → 시행령 별표5 → appendix(20인)
법25조 관리규정   → 시행규칙 별표2 → appendix(100인)
```

---

## TASK-005: COMPOUND Trigger

```
수치 조건 중 COMPOUND: 4건
  OTHER_NUMERIC COMPOUND 3
  COUNT_THRESHOLD COMPOUND 1

예: "연면적 400㎡ 이상이거나 상시 50명 이상"
    → AREA_THRESHOLD OR COUNT_THRESHOLD

→ COMPOUND는 희소하지만 존재. 단일 Trigger와 분리 필요.
```

---

## TASK-006: UNIVERSAL Trigger (L2 PLAIN 644건)

조건 없이 발동하는 무조건 의무의 행위 유형:

| universal_action | 건수 |
|---|---|
| OTHER | 371 |
| INSTALL (설치·구비) | 111 |
| INSPECT (점검·측정) | 54 |
| POSTING (비치·게시) | 44 |
| REPORT (보고·신고) | 42 |
| DOCUMENT (작성·기록) | 29 |
| PROVIDE (지급·착용) | 23 |
| EDUCATION (교육) | 19 |

**핵심:** UNIVERSAL Trigger는 입력값과 무관.
sector 소속만으로 발동 (교육·보고·비치·게시 등).
→ 입력 패턴에 대응 없음. sector 단위 일괄 적용 대상.

---

## LAW_TRIGGER_CATALOG (8종)

| trigger_code | trigger_name | description | 조문수 | appendix_dep | compound |
|---|---|---|---|---|---|
| **WORK_EXISTS** | 작업 존재 | 특정 작업 수행이 의무 발생 원인 | 189 | ❌ | ❌ |
| **EQUIPMENT_EXISTS** | 설비 존재 | 설비 보유·사용이 원인 | 153 | ❌ | ❌ |
| **MATERIAL_EXISTS** | 물질 존재 | 물질 취급이 원인 | 45 | ❌ | ❌ |
| **FACILITY_EXISTS** | 시설 존재 | 장소·공간이 원인 | 17 | ❌ | ❌ |
| **THRESHOLD** | 수치 임계 | 수치 초과가 원인 | 30(본조)+102(위임) | ✅ | △ |
| **COMPOUND** | 복합 조건 | 2개 이상 조건 결합 | 4 | △ | ✅ |
| **UNIVERSAL** | 무조건 | sector 소속만으로 발동 | 644 | ❌ | ❌ |
| **FRAGMENT** | 단편 의존 | 상위 조문 없이 불완전 | 46 | ❌ | ❌ |

---

## Trigger별 특징 (행동 기술)

### WORK_EXISTS (189) — 최대 작업 트리거
```
"근로자가 밀폐공간에서 작업하는 경우 → 산소농도 측정"
의무 발생 원인 = 그 작업을 하는가
```

### EQUIPMENT_EXISTS (153)
```
"크레인을 사용하는 경우 → 방호장치 설치"
의무 발생 원인 = 그 설비가 있는가
```

### THRESHOLD (132)
```
본조 직접(30): "400㎡ 이상 → 경보설비"
별표 위임(102): "50인 이상 → 안전관리자" (appendix)
의무 발생 원인 = 수치가 기준을 넘는가
→ appendix_condition 7건 병목으로 대부분 미작동
```

### UNIVERSAL (644) — 최대 트리거
```
"안전보건교육을 실시하여야 한다" (조건 없음)
의무 발생 원인 = 없음. sector 소속 자체가 트리거
→ 입력값 불필요. 일괄 적용
```

### FRAGMENT (46) — 격리 대상
```
"이 경우 ~하여야 한다"
단독으로 Trigger 불명. parent 조문 필요
```

---

## 핵심 발견

### 발견 1: Trigger는 2개 군으로 양분된다

```
조건부 Trigger (입력값 필요):
  WORK + EQUIPMENT + MATERIAL + FACILITY + THRESHOLD = 약 536건
  → "입력값에 따라 발동"

무조건 Trigger (입력값 불필요):
  UNIVERSAL = 644건
  → "sector 소속만으로 발동"

→ 법령 의무는 "입력 의존"과 "입력 무관"으로 나뉜다.
→ UNIVERSAL이 가장 많다 (644).
```

### 발견 2: 엔진 구조가 명확해짐

```
입력 → Trigger → 의무 구조에서:

조건부 의무:
  입력값 (밀폐공간 있음) → WORK_EXISTS Trigger → 측정 의무

무조건 의무:
  sector (제조업) → UNIVERSAL Trigger → 교육 의무
  (입력값 불필요)

→ 두 경로가 완전히 다름.
→ UNIVERSAL은 입력 매핑 불필요, sector 일괄 적용.
```

### 발견 3: THRESHOLD가 가장 취약

```
THRESHOLD Trigger 132건 중:
  본조 직접 수치: 30건 (작동 가능)
  별표 위임: 102건 (appendix 7건만 입력 → 대부분 미작동)

→ THRESHOLD는 가장 중요하지만 가장 미완성.
→ appendix_condition 입력이 최우선 과제.
```

### 발견 4: 입력 Trigger ↔ 법령 Trigger 대응 윤곽 (관찰만)

```
법령 WORK_EXISTS/EQUIPMENT/MATERIAL/FACILITY (404)
  ←관찰→ 입력 P1 BOOLEAN_EXISTENCE (55)

법령 THRESHOLD (132)
  ←관찰→ 입력 P2 NUMERIC_THRESHOLD (18)

법령 UNIVERSAL (644)
  ←관찰→ 입력 대응 없음 (sector만 필요)

주의: 이번 WO에서 연결 안 함. 다음 WO-PATTERN-CROSSMAP-001에서 비교.
```

---

## 성공 기준 답변

> 법령세계를 Trigger로 설명할 수 있는가?

```
✅ 가능. 8개 Trigger:

WORK_EXISTS       189   작업 수행
EQUIPMENT_EXISTS  153   설비 보유
MATERIAL_EXISTS    45   물질 취급
FACILITY_EXISTS    17   시설·장소
THRESHOLD         132   수치 임계 (본조30+위임102)
COMPOUND            4   복합 조건
UNIVERSAL         644   무조건 (sector)
FRAGMENT           46   단편 (격리)

이제 법령을 "무슨 의무"가 아니라
"왜 그 의무가 발생하는가(Trigger)"로 설명할 수 있다.
```

---

## 두 세계 압축 완료 현황

```
입력세계:  98필드 → 7패턴 (BOOLEAN 55 + THRESHOLD 18 지배)
법령세계:  58,495조문 → 8 Role → 8 Trigger (UNIVERSAL 644 + WORK 189 지배)

다음 WO-PATTERN-CROSSMAP-001에서:
  입력 패턴 ↔ 법령 Trigger 비교
  P1 BOOLEAN ↔ WORK/EQUIPMENT/MATERIAL/FACILITY
  P2 THRESHOLD ↔ THRESHOLD
  UNIVERSAL(644) 처리 방안 (입력 무관)
  FRAGMENT(46) 격리 방안
```

---

## 다음 단계

```
WO-LAW-TRIGGER-DISCOVERY-001 (현재) — 완료
      ↓
WO-PATTERN-CROSSMAP-001
  입력 패턴 7개 ↔ 법령 Trigger 8개 실제 비교
  엔진 핵심 구조: 입력 → Trigger → 의무
```

---

*WO-LAW-TRIGGER-DISCOVERY-001 완료.*
*58,495 조문 → 8개 Trigger. UNIVERSAL(644)+WORK(189)+EQUIPMENT(153) 지배.*
*핵심: Trigger는 조건부(입력필요)와 무조건(sector만)으로 양분. THRESHOLD는 appendix 병목.*
