# TAI / 45cm Platform

## 워크플로우엔진작업지시서-2026-05-15-001

### Workflow Integrity Evaluator Foundation

작성일: 2026-05-15
상태: 실행 지시서
대상: Claude Code / 개발 에이전트

---

# 1. 이번 작업 목적

현재 Workflow Engine은:

```
상태(State)
전이(Transition)
타임라인(Timeline)
이벤트(Event)
```

를 기록 가능하게 되었다.

다음 단계 목표는:

```
Workflow 흐름의 정상성(Integrity)을 평가
```

하는 것이다.

중요:

이번 작업은:

```
Workflow Runtime 구현
```

이 아니다.

이번 작업 목표는:

```
Workflow Integrity Evaluation Layer 구축
```

이다.

---

# 2. 절대 원칙

---

## 원칙 1

```
Workflow ≠ Integrity
```

Workflow는 상태 흐름 생성.

Integrity는 흐름 평가.

---

## 원칙 2

Integrity Layer는:

```
판단(Evaluation)
```

만 수행.

상태 변경 금지.

---

## 원칙 3

Integrity Layer는:

```
Notification 직접 호출 금지
```

반드시:

```
Integrity Event
→ Alert Layer
→ Notification Runtime
```

경유.

---

## 원칙 4

현재 단계는:

```
Business Workflow Integrity
```

구축 단계.

Infra Monitoring 방향 금지.

---

## 원칙 5

Integrity Layer는:

```
Business State 흐름 평가
```

중심.

CPU/memory 관제 아님.

---

# 3. 이번 작업 범위

---

# 3.1 Integrity Rule Registry 구축

신규 테이블:

예:

```
workflow_integrity_rule_registry
```

목적:

```
Workflow Integrity 규칙 중앙화
```

필수 필드:

* rule_code
* workflow_type
* rule_type
* severity
* enabled
* description
* evaluation_window_sec
* created_at

초기 rule_type:

```
TIMEOUT
INVALID_TRANSITION
STUCK
SEQUENCE_VIOLATION
MISSING_STEP
```

---

# 3.2 Workflow Integrity Event 테이블 구축

신규 테이블:

예:

```
workflow_integrity_event
```

목적:

```
Integrity 이상 탐지 결과 저장
```

필수 필드:

* workflow_id
* workflow_type
* integrity_type
* severity
* trace_id
* detected_at
* payload
* resolved
* resolved_at

---

# 3.3 Integrity Evaluator Engine 구현

신규 서비스:

예:

```
integrity_evaluator.py
```

역할:

```
Workflow Timeline 기반 정상성 평가
```

현재 범위:

* timeline 조회
* rule 조회
* 이상 탐지
* integrity event 생성

현재 단계에서:

```
자동 수정 금지
```

---

# 3.4 Timeout Detection 구현

목적:

```
Workflow 정지 탐지
```

예:

```
APPROVAL_PENDING 상태 1시간 초과
```

탐지 가능해야 함.

현재:

* detect only
* auto transition 금지

---

# 3.5 Invalid Transition Detection 구현

목적:

```
허용되지 않은 상태 전이 탐지
```

기준:

```
workflow_transition_registry
```

참조.

---

# 3.6 Sequence Violation Detection 구현

목적:

```
Workflow 흐름 순서 이상 탐지
```

예:

```
APPROVED 없이 COMPLETED
```

---

# 3.7 Missing Step Detection 구현

목적:

```
필수 상태 누락 탐지
```

예:

```
VALIDATING 없이 APPROVAL_PENDING
```

---

# 3.8 Integrity Timeline API

신규 API:

```
/workflow/integrity/{workflow_id}
```

반환:

* integrity events
* triggered rules
* timeline correlation

---

# 3.9 Integrity ↔ Alert Hook 정의

현재 범위:

* interface 정의만
* Alert Runtime 직접 구현 금지

예:

```
emit_integrity_alert()
```

---

# 4. 작업 제외 범위

절대 구현 금지.

---

## 제외 1

Workflow auto recovery 금지.

---

## 제외 2

Workflow auto transition 금지.

---

## 제외 3

AI integrity 판단 금지.

---

## 제외 4

Business decision logic 금지.

---

## 제외 5

Notification direct send 금지.

---

## 제외 6

Infra monitoring 금지.

---

## 제외 7

Workflow orchestration 금지.

---

# 5. 핵심 아키텍처 목표

목표 구조:

```
Workflow Engine
    ↓
Workflow Timeline
    ↓
Integrity Evaluator
    ↓
Integrity Event
    ↓
Alert Layer
    ↓
Notification Runtime
```

핵심:

```
Integrity는 Workflow를 평가한다
Notification은 전달한다
```

---

# 6. 성공 기준

---

## 성공 기준 1

Integrity Rule Registry 구축 완료.

---

## 성공 기준 2

Integrity Event 저장 완료.

---

## 성공 기준 3

Timeout Detection 정상 동작.

---

## 성공 기준 4

Invalid Transition Detection 정상 동작.

---

## 성공 기준 5

Sequence Violation 탐지 가능.

---

## 성공 기준 6

Missing Step 탐지 가능.

---

## 성공 기준 7

Integrity Timeline API 정상 동작.

---

# 7. 코드 구조 요구사항

신규 구조:

```
workflow_integrity/

  registry/
  evaluator/
  detectors/
  events/
  timeline/
  hooks/
```

---

# 8. 중요한 설계 철학

현재 가장 중요한 것은:

```
Workflow 흐름을 평가 가능한 상태로 만드는 것
```

이다.

즉:

```
"무슨 상태인가?"
```

가 아니라,

```
"정상 흐름인가?"
```

를 판단하는 단계로 진입하는 것이다.

그리고 반드시 유지해야 하는 핵심 철학:

```
Workflow는 상태를 만든다
Integrity는 상태를 평가한다
Alert는 운영 중요도를 판단한다
Notification은 전달한다
```

이다.
