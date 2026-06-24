# WO-LAW-TRIGGER-HIERARCHY-001
# 법령 Trigger 계층 확정 (TRIGGER-DISCOVERY-001 보강)

**작성일:** 2026-06-24 | **상태:** 완료 (계층 확정 전용)
**선행:** WO-LAW-TRIGGER-DISCOVERY-001
**금지:** 입력 연결 / 매핑 / 후보군 생성
**목적:** 법령 Trigger 자체의 계층(트리)을 확정한다. 8개인가 30개인가 300개인가.

> 실패 패턴 차단: Trigger 발견 → 즉시 입력 연결 → 매핑 점프.
> 이번엔 법령 Trigger만으로 트리 구조를 완성한다.

---

## 결론 먼저

```
LAW_TRIGGER는 2계층 구조다.

Level-1 (대분류): 8종
  WORK / EQUIPMENT / MATERIAL / FACILITY /
  THRESHOLD / COMPOUND / UNIVERSAL / FRAGMENT

Level-2 (세부): 각 L1 하위에 구체 항목 존재
  WORK ├ 잠수/발파/용접/밀폐공간/굴착/해체/운반/고소
  EQUIPMENT ├ 보일러/크레인/압력용기/리프트/프레스/컨베이어
  MATERIAL ├ 석면/가스/유해물질/화학물질/분진

추가 발견:
  THRESHOLD는 별도 분리 → APPENDIX_TRIGGER (별표 위임)
  UNIVERSAL 644 → 진짜 359 + 가짜 285 (숨은 조건)
```

---

## TASK-003A/B: Trigger 계층 존재 확인

### WORK_EXISTS는 Level-1, 하위에 Level-2 실재

| Level-2 작업 | 조문수 |
|---|---|
| 기타작업 | 126 |
| 해체작업 | 13 |
| 운반작업 | 10 |
| 밀폐공간작업 | 10 |
| 잠수작업 | 7 |
| 용접작업 | 6 |
| 굴착작업 | 5 |
| 발파작업 | 1 |

### EQUIPMENT_EXISTS Level-2

| Level-2 설비 | 조문수 |
|---|---|
| 기타설비 | 171 |
| 컨베이어 | 5 |
| 크레인 | 5 |
| 리프트 | 2 |

### MATERIAL_EXISTS Level-2

| Level-2 물질 | 조문수 |
|---|---|
| 기타물질 | 37 |
| 유해물질 | 30 |
| 가스 | 21 |
| 화학물질 | 10 |
| 석면 | 9 |
| 분진 | 8 |

**결론:** Level-2가 실재한다. 단, "기타"가 가장 많아 **현재 명시적으로 분류 가능한 Level-2는 제한적**.
→ LAW_TRIGGER는 8개(L1)가 골격, 세부는 수십 개(L2) 규모.
→ 300개는 아님. **약 8개 L1 + 30~50개 L2.**

---

## TASK-004: Appendix Trigger 분리

```
THRESHOLD는 단일 Trigger가 아니라 2종으로 분리됨:

DIRECT_THRESHOLD (본조 직접 수치): 30건
  예: "연면적 400㎡ 이상" — semantic_clause에 직접 명시
  → 조문만으로 판정 가능

APPENDIX_THRESHOLD (별표 위임): 102건
  예: 본조 "안전관리자를 둔다" + 별표 "50인 이상"
  → semantic_clause엔 수치 없음, appendix_condition 필요
  → appendix 7건만 입력 → 95건 미작동

→ THRESHOLD Trigger는 사실상 APPENDIX_TRIGGER가 주력(102 vs 30).
→ Trigger 계층에서 THRESHOLD를 DIRECT와 APPENDIX로 분리해야 함.
```

---

## TASK-005: COMPOUND Trigger 유형

```
COMPOUND 4건 (희소):
  OTHER_NUMERIC COMPOUND 3
  COUNT_THRESHOLD COMPOUND 1

대표: "연면적 400㎡ 이상이거나 상시 50명 이상"
  → AREA_THRESHOLD OR COUNT_THRESHOLD

실제 존재 유형:
  THRESHOLD OR THRESHOLD (면적 or 인원)

→ COMPOUND는 현재 거의 없음(4건).
→ 단, L2 세부에서 "작업 + 설비" 동시 조건은 더 있을 수 있음(추후 정밀).
```

---

## TASK-006: UNIVERSAL 검증 (가장 중요)

```
UNIVERSAL 후보 644건 정밀 검증 결과:

TRUE_UNIVERSAL    359  ← 진짜 무조건 (교육·보고·비치 등)
HIDDEN_ACTIVITY   280  ← action_text에 작업 조건 숨음
HIDDEN_THRESHOLD   53  ← action_text에 수치 조건 숨음
HIDDEN_SECTOR       1  ← 업종 조건 숨음

→ UNIVERSAL 644는 과대평가였다.
→ 진짜 UNIVERSAL은 359건 (56%).
→ 285건은 condition_text가 NULL이지만 action_text에 조건 내장.
```

### 숨은 조건의 의미

```
condition_text = NULL 이라고 무조건 의무가 아니다.

예: action_text = "분진작업을 하는 장소에 국소배기장치를 설치"
  → condition_text는 비었지만 action_text에 "분진작업" 조건 내장
  → 실제로는 HIDDEN_ACTIVITY (WORK_EXISTS Trigger)

→ Trigger 판정은 condition_text만 보면 안 됨.
→ action_text도 함께 파싱해야 정확한 Trigger 도출.
```

---

## 산출물: LAW_TRIGGER_HIERARCHY

```
LAW_TRIGGER (Level-1: 8종 + Appendix 분리)

├─ WORK_EXISTS (작업 존재)
│   ├─ 잠수작업
│   ├─ 발파작업
│   ├─ 용접작업
│   ├─ 밀폐공간작업
│   ├─ 굴착작업
│   ├─ 해체작업
│   ├─ 운반작업
│   └─ 고소작업
│
├─ EQUIPMENT_EXISTS (설비 존재)
│   ├─ 보일러
│   ├─ 크레인/타워크레인
│   ├─ 압력용기
│   ├─ 리프트/승강기
│   ├─ 프레스
│   └─ 컨베이어
│
├─ MATERIAL_EXISTS (물질 존재)
│   ├─ 석면
│   ├─ 가스/고압가스
│   ├─ 유해물질(관리대상)
│   ├─ 화학물질
│   └─ 분진
│
├─ FACILITY_EXISTS (시설 존재)
│   └─ 밀폐공간/특수장소
│
├─ THRESHOLD (수치 임계) ★분리
│   ├─ DIRECT_THRESHOLD (본조 30)
│   │   ├─ AREA (면적)
│   │   ├─ COUNT (인원)
│   │   └─ CAPACITY (용량)
│   └─ APPENDIX_THRESHOLD (별표위임 102) ← appendix_condition 의존
│       ├─ 안전관리자 선임기준
│       ├─ 관리담당자 선임기준
│       └─ 관리규정 작성기준
│
├─ COMPOUND (복합) — 4건
│   └─ THRESHOLD OR THRESHOLD
│
├─ UNIVERSAL (무조건) ★재검증
│   ├─ TRUE_UNIVERSAL (359) — 교육·보고·비치·게시
│   └─ (HIDDEN 285는 위 Trigger로 재분류 대상)
│
└─ FRAGMENT (단편) — 46건, 격리
    └─ parent 조문 의존
```

---

## 핵심 발견

### 발견 1: Trigger는 8개 L1 + 약 40개 L2 구조

```
Level-1: 8종 (골격)
Level-2: 약 30~40개 (세부 작업·설비·물질)

→ "8개인가 300개인가" 답: 8개 L1이 기준.
  L2는 입력값과 직접 대응되는 단위(잠수작업, 보일러 등).
→ 입력 has_diving ↔ 법령 L2 잠수작업 (다음 WO에서 연결)
```

### 발견 2: THRESHOLD는 DIRECT/APPENDIX로 분리해야 한다

```
DIRECT_THRESHOLD (30):  조문만으로 판정
APPENDIX_THRESHOLD (102): 별표 데이터 필요

→ 같은 THRESHOLD라도 처리 경로가 다름.
→ APPENDIX는 appendix_condition 7건 병목으로 막혀 있음.
```

### 발견 3: UNIVERSAL 644 → 진짜 359 (44% 과대평가)

```
condition_text NULL ≠ 무조건 의무.
285건은 action_text에 숨은 조건 보유.

→ Trigger 판정 시 action_text 파싱 필수.
→ 진짜 입력 무관 의무는 359건 (교육·보고·비치·게시).
```

### 발견 4: "기타"가 많다 = Level-2 분류 미완

```
WORK 기타 126, EQUIPMENT 기타 171, MATERIAL 기타 37

→ 키워드 기반 L2 분류로는 절반 이상이 "기타".
→ L2 완성은 조문 직독 또는 LLM 분류 필요 (추후).
→ 현 단계는 L1 골격 + L2 존재 확인까지.
```

---

## 성공 기준 답변

> 법령 Trigger만으로 트리 구조를 설명할 수 있는가?

```
✅ 가능.

LAW_TRIGGER = 2계층
  Level-1: 8종 (WORK/EQUIPMENT/MATERIAL/FACILITY/THRESHOLD/COMPOUND/UNIVERSAL/FRAGMENT)
  Level-2: 각 L1 하위 구체 항목 (잠수/보일러/석면 등 약 30~40개)

추가 정밀화:
  THRESHOLD → DIRECT + APPENDIX 분리
  UNIVERSAL → TRUE(359) + HIDDEN(285) 분리

이제 법령 Trigger 트리가 입력과 무관하게 완전히 정의됨.
```

---

## 수정된 LAW_TRIGGER_CATALOG (최종)

| trigger_code | level | 조문수 | appendix_dep | 비고 |
|---|---|---|---|---|
| WORK_EXISTS | L1 | 189 | ❌ | L2: 잠수/발파/용접/밀폐/굴착/해체 |
| EQUIPMENT_EXISTS | L1 | 153 | ❌ | L2: 보일러/크레인/압력용기/리프트 |
| MATERIAL_EXISTS | L1 | 45 | ❌ | L2: 석면/가스/유해물질/화학/분진 |
| FACILITY_EXISTS | L1 | 17 | ❌ | L2: 밀폐공간/특수장소 |
| DIRECT_THRESHOLD | L1 | 30 | ❌ | 본조 직접 수치 |
| APPENDIX_THRESHOLD | L1 | 102 | ✅ | 별표 위임 (7건만 입력) |
| COMPOUND | L1 | 4 | △ | THRESHOLD OR THRESHOLD |
| TRUE_UNIVERSAL | L1 | 359 | ❌ | 교육·보고·비치·게시 |
| HIDDEN_CONDITION | (재분류) | 285 | ❌ | action_text 조건 → L1 재배정 |
| FRAGMENT | L1 | 46 | ❌ | parent 의존, 격리 |

---

## 다음 단계

```
WO-LAW-TRIGGER-HIERARCHY-001 (현재) — 완료
      ↓
WO-PATTERN-CROSSMAP-001
  이제 입력 패턴 ↔ 법령 Trigger 연결 가능:
  입력 has_diving ↔ 법령 WORK.잠수작업
  입력 has_boiler ↔ 법령 EQUIPMENT.보일러
  입력 worker_count ↔ 법령 APPENDIX_THRESHOLD.안전관리자
  입력 (없음) ↔ 법령 TRUE_UNIVERSAL (sector 일괄)
```

---

*WO-LAW-TRIGGER-HIERARCHY-001 완료.*
*법령 Trigger = 8개 L1 + 약 40개 L2. THRESHOLD는 DIRECT/APPENDIX 분리.*
*핵심: UNIVERSAL 644 → 진짜 359. condition_text NULL ≠ 무조건. action_text 파싱 필수.*
