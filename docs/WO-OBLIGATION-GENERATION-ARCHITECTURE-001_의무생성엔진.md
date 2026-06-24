# WO-OBLIGATION-GENERATION-ARCHITECTURE-001
# 의무 생성 엔진 아키텍처

**작성일:** 2026-06-24 | **상태:** 완료 (아키텍처 정의, 읽기 전용)
**선행:** WO-ENGINE-CODE-AUDIT-001
**금지 (전부 준수):** Harvest/Review/Confirmed/Mapping/Trigger/Pattern/INSERT/UPDATE/DELETE/DDL 없음
**목적:** 입력 → 의무후보 → 의무생성 과정을 정의한다.

> 매핑 생성을 멈추고, 의무 생성 엔진 자체를 정의.

---

## 최종 질문 답변 (가장 중요)

```
Q: CONFIRMED 452는 엔진의 최종 결과인가, 의무 생성 엔진의 원재료인가?

A: 원재료다.

근거 (실측):
  CONFIRMED 452의 조문 345개 part 중
    166개(48%)가 실제 엔진의 rule_candidate에도 존재
    65개(19%)가 executable_draft까지 도달

  → cmc와 실제 엔진은 "같은 법령 조문"을 다르게 가공.
  → cmc = "입력→Trigger→조문" 관점의 원재료.
  → 엔진 = "조문→rule→draft→factory적용" 관점의 가공물.
  → 452는 결과가 아니라, 의무 생성의 입력 재료.
```

---

## TASK-001: CONFIRMED 452의 실제 의미

```
CONFIRMED 1건 = "입력조건 → Trigger → 조문" 연결 1개.

구조:
  input_field (has_welding)
  + condition_type (WORK_ACT = Trigger)
  + semantic_clause_id (조문)
  + condition_code (WORK_ACT:WELDING:VENTILATION:hash)

표현하는 것:
  "용접작업이 있으면(입력) → 작업 Trigger 발동 →
   이 조문(국소배기장치 설치)이 적용된다"

→ CONFIRMED는 "의무 그 자체"가 아니라
  "어떤 입력일 때 어떤 조문이 켜지는가"의 규칙.
→ 즉 적용성 규칙(applicability rule).
→ 의무(task)는 그 조문에서 추가로 파생되어야 함.
```

---

## TASK-002: 의무 생성 최소 단위

```
4개 후보 중 결정:

A. semantic_clause      — 조문 (너무 큼, 한 조문에 여러 의무)
B. condition_mapping_candidate — 입력↔조문 규칙 (적용성)
C. 의무군               — 모호
D. 체크항목             — 너무 작음 (실행 단위)

결정: 최소 단위는 두 층위로 분리된다.

  층위 1: obligation_instance (의무 인스턴스)
    = "이 factory에 이 조문이 적용된다" (적용성)
    ≈ 실제 엔진의 facility_applicability

  층위 2: task_instance (실행 과제)
    = "그 의무를 위해 무엇을 해야 하는가" (REPORT/INSTALL/INSPECT)
    ≈ 실제 엔진의 task_candidate

→ cmc(452)는 층위 1(적용성)의 원재료.
→ 의무 생성 엔진은 cmc → obligation_instance → task_instance.
```

---

## TASK-003: 생성 순서 (평가 순서)

```
입력(sector, has_*, numeric, process, equipment, material)이
들어왔을 때 평가 순서:

1. SCOPE      범위 필터 (산안법 대상인가, 범위밖 191 제거)
2. UNIVERSAL  sector baseline (입력 무관, condition_type='NONE')
3. EXISTS     has_* → WORK/EQUIPMENT/MATERIAL/FACILITY 조문
4. THRESHOLD  numeric → 본조 직접 수치 (DIRECT)
5. APPENDIX   numeric → 별표 위임 (appendix_condition 필요)
6. FRAGMENT   parent 조문 상속 (독립 평가 안 함)

근거:
  - SCOPE 먼저 (SCOPE-FILTER-001: 오탐 원천 차단)
  - UNIVERSAL이 baseline (sector만으로 발동, 가장 많음)
  - EXISTS가 특화 의무 (입력값 매칭)
  - THRESHOLD/APPENDIX는 수치 판정 (현재 병목)
  - FRAGMENT는 마지막 (parent 의존)

→ 이 순서가 후보 생성의 표준 파이프라인.
```

---

## TASK-004: 후보 생성 엔진

```
입력 1개 → 의무후보 N개 생성 규칙:

EXISTS형:
  has_welding=true
    → condition_type=WORK_ACT AND input_field=has_welding
    → cmc에서 매칭되는 조문 모두 (실측 18개)
    → 18개 obligation_instance 후보

UNIVERSAL형:
  sector=INDUSTRIAL (입력 무관)
    → condition_type='NONE' AND sector IN applicable_sectors
    → 226개 baseline obligation_instance 후보

THRESHOLD형:
  worker_count=50
    → DIRECT_THRESHOLD: 본조 수치 직접 비교
    → APPENDIX_THRESHOLD: appendix_condition 조회 후 비교
    → (현재 appendix 7건 병목으로 거의 0)

생성 규칙 공식:
  obligation_candidate =
    SELECT * FROM condition_mapping_candidate
    WHERE review_status='CONFIRMED'
      AND (
        (condition_type='NONE' AND sector ∈ applicable_sectors)  -- UNIVERSAL
        OR (input_field ∈ 입력된_has_* AND input_value='true')    -- EXISTS
        OR (THRESHOLD 조건 충족)                                  -- THRESHOLD
      )
```

---

## TASK-005: 후보 제거 엔진

```
후보 생성 후 제거 규칙:

1. SCOPE 불일치
   condition_type='OUT_OF_SCOPE' → 제거
   (범위밖 191건 — 주택법/파견법/보험료)

2. SECTOR 불일치
   sector ∉ applicable_sectors → 제거
   (제조업 입력에 건설 전용 의무 제거)

3. FRAGMENT
   조문이 "이 경우/전항" 단편 → parent 없으면 제거

4. APPENDIX 미충족
   APPENDIX_THRESHOLD인데 appendix_condition 미입력 → 보류(제거 아님)

5. THRESHOLD 미충족
   worker_count=10인데 기준=50 → 제거

6. REJECTED
   review_status='REJECTED' (35건) → 애초에 조회 안 됨

→ 제거는 "조회 시 WHERE 절"로 구현 (사후 삭제 아님).
→ 핵심: SCOPE/SECTOR 먼저, THRESHOLD 나중.
```

---

## TASK-006: 체크엔진 인계 규격

```
질문: 체크엔진은 cmc를 받는가, obligation_instance를 받는가?

답: obligation_instance를 받아야 한다.

이유:
  - cmc는 "규칙"(어떤 입력→어떤 조문).
  - 체크엔진은 "특정 factory의 확정된 의무"가 필요.
  - cmc를 factory 입력에 적용한 결과 = obligation_instance.

실제 엔진 확인 (CODE-AUDIT-001):
  체크엔진(diagnosis_candidate)은
  facility_applicability(=obligation_instance)를 받음.
  cmc를 직접 받지 않음.

→ 인계 규격: obligation_instance (factory별 확정 의무).
→ cmc → [생성엔진] → obligation_instance → [체크엔진].
```

---

## TASK-007: 생성 엔진 출력 규격

```
obligation_instance 출력 규격:

{
  obligation_id:       uuid,          -- 인스턴스 고유 ID
  factory_id:          uuid,          -- 대상 사업장
  source_clause_id:    uuid,          -- semantic_clause_id (근거 조문)
  source_cmc_id:       uuid,          -- 어느 매핑규칙에서 나왔는가
  trigger:             text,          -- WORK_ACT/EQUIPMENT_ACT/NONE 등
  trigger_l2:          text,          -- WELDING/BOILER/UNIVERSAL
  detail:              text,          -- RECORD/PPE/INSPECT/VENTILATION
  reason:              text,          -- "has_welding=true → 용접작업"
  input_field:         text,          -- 발동시킨 입력 (NULL=UNIVERSAL)
  applicable_sectors:  text[],        -- 적용 sector
  confidence:          numeric,       -- cmc.confidence 승계
  status:              text,          -- ACTIVE/MISSING_DATA/AMBIGUOUS
  task_hints:          jsonb          -- 파생 task 힌트 (REPORT/INSTALL)
}

예시:
{
  obligation_id: "...",
  factory_id: "factory-123",
  source_clause_id: "clause-abc",
  trigger: "WORK_ACT",
  trigger_l2: "WELDING",
  detail: "VENTILATION",
  reason: "has_welding=true → 용접작업 → 국소배기장치 설치",
  input_field: "has_welding",
  applicable_sectors: ["INDUSTRIAL"],
  confidence: 0.90,
  status: "ACTIVE"
}
```

---

## 전체 아키텍처

```
[입력]
  sector + has_* + numeric + process/equipment/material
        ↓
[후보생성]  (TASK-004)
  SCOPE → UNIVERSAL → EXISTS → THRESHOLD → APPENDIX → FRAGMENT 순
  cmc(CONFIRMED 452)에서 입력 매칭 조문 추출
  = obligation_candidate N개
        ↓
[후보제거]  (TASK-005)
  SCOPE 불일치 / SECTOR 불일치 / FRAGMENT / THRESHOLD 미충족 제거
  (WHERE 절로 구현)
        ↓
[의무생성]  (TASK-007)
  obligation_instance 생성 (factory별 확정 의무)
  reason/trigger/detail/confidence 부여
        ↓
[체크엔진]  (TASK-006)
  obligation_instance 입력 받음
  → 체크항목/일정/담당자 배정
  (실제 엔진: diagnosis_candidate)
```

---

## 두 시스템 관계 재정의 (CODE-AUDIT 후속)

```
실제 엔진 (GPT Compiler):
  part → rule_candidate → executable_draft
  → facility_applicability(394만) → task_candidate
  = "조문 중심" 의무 생성 (조문마다 적용성 사전계산)

우리 자산 (Trigger 매핑):
  input → pattern → trigger → cmc(452)
  = "입력 중심" 적용성 규칙

연결점 (실측):
  cmc 조문 345 part 중 166개가 rule_candidate와 공유.
  → 같은 조문을 두 관점으로 처리 중.

관계 결정:
  cmc(452) = 입력→조문 적용성 규칙 (원재료)
  실제 엔진 = 조문→factory 적용성 사전계산 (대량)
  → cmc는 실제 엔진의 "입력 인터페이스 레이어"가 될 수 있음.
  → 단, 실제 엔진(GPT Compiler)은 Claude 수정 금지 영역.
  → cmc를 obligation_instance 생성기로 쓸지,
     실제 엔진에 입력 신호로 넣을지는 대표님 결정.
```

---

## 핵심 발견

### 발견 1: CONFIRMED 452는 "적용성 규칙"이지 "의무"가 아니다

```
452 = "어떤 입력일 때 어떤 조문이 켜지는가"의 규칙.
의무(task)는 그 조문에서 추가 파생 필요.

→ 452는 의무 생성 엔진의 입력(원재료).
→ 출력은 obligation_instance (factory별 확정).
```

### 발견 2: 의무는 2층위다 (적용성 + 실행과제)

```
층위1 obligation_instance: "이 조문이 적용된다" (facility_applicability)
층위2 task_instance: "무엇을 해야 하나" (task_candidate, REPORT/INSTALL)

→ cmc는 층위1의 원재료.
→ 실제 엔진은 이미 양 층위를 가짐(394만 + 9.4만).
```

### 발견 3: 생성 순서가 정확도를 결정

```
SCOPE → UNIVERSAL → EXISTS → THRESHOLD → APPENDIX → FRAGMENT
→ SCOPE 먼저가 오탐 차단(SCOPE-FILTER-001 교훈).
→ 제거는 사후 삭제가 아니라 조회 WHERE 절.
```

### 발견 4: cmc와 실제 엔진은 같은 조문을 공유 (연결 가능)

```
cmc 345 part 중 166이 rule_candidate와 공유.
→ 두 시스템은 단절이 아니라 "같은 조문, 다른 관점".
→ cmc를 실제 엔진의 입력 인터페이스로 연결 가능성 있음.
→ 단 실제 엔진 수정은 GPT 영역.
```

---

## 다음 단계 권고 (판단 보류, 사실 기반)

```
이번 WO로 의무 생성 엔진 아키텍처가 정의됨.
다음은 대표님 전략 결정:

1. cmc를 obligation_instance 생성기로 구현
   - cmc(452) → 입력 적용 → obligation_instance 테이블
   - 별도 경로 (실제 엔진 안 건드림)

2. cmc와 facility_applicability 정합성 비교
   - 같은 factory에 두 시스템 결과 비교 (읽기 전용)
   - 166 공유 part가 일치하는지 검증

3. run_facility_applicability.py 배치 로직 확인
   - 실제 엔진이 무엇을 근거로 적용성 판정하는지
   - cmc 신호를 넣을 지점이 있는지 (읽기 전용)
```

---

*WO-OBLIGATION-GENERATION-ARCHITECTURE-001 완료. 읽기 전용 아키텍처 정의.*
*핵심: CONFIRMED 452 = 원재료(적용성 규칙), 결과 아님.*
*의무는 2층위(적용성+실행과제). 생성순서 SCOPE→UNIVERSAL→EXISTS→THRESHOLD.*
*cmc 166 part가 실제 엔진과 공유 — 연결 가능하나 GPT 영역 주의.*
