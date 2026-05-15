# 45cm Core Platform Concepts

## 목적

본 문서는 45cm / TAI Platform의 핵심 개념 경계를 정의한다.

핵심 목표:

- 개념 충돌 방지
- 엔진 중복 구현 방지
- 플랫폼 철학 유지
- AI/개발자 공통 사고체계 구축

---

# Event

플랫폼에서 발생한 구조화된 사건.

특징:
- immutable
- trace 가능
- workflow reconstruction 가능
- 시스템 중심

Event는 단일 사건이다.

---

# Workflow

의미 있는 Event Sequence.

예:
submit → validate → approve → complete

Workflow는 상태 흐름이다.

Event와 Workflow는 다르다.

- Event = 단일 사건
- Workflow = 사건 흐름

---

# State

현재 시스템의 상태.

Workflow는 State Transition을 만든다.

---

# Integrity

Workflow가 정상 흐름인지 평가.

예:
- stuck
- timeout
- sequence violation
- mismatch

Integrity는 시스템 건강성이다.

---

# Alert

운영 개입이 필요한 Integrity/Event.

모든 Event가 Alert는 아니다.

핵심:

```text
Event ≠ Alert
```

---

# Notification

Alert/Event를 누구에게 어떻게 전달할 것인가.

Notification은 메시지 기능이 아니다.

정의:

```text
운영 커뮤니케이션 레이어
```

---

# Trace

Event / Workflow 연결 흐름.

목적:
- workflow reconstruction
- observability
- root cause tracking

---

# Rule

Event / Workflow / Alert 처리 규칙.

예:
- alert rule
- escalation rule
- dedupe rule
- cooldown rule

---

# Synthetic

실제 사용자 흐름을 시뮬레이션하는 운영 관측.

Infra Monitoring이 아니라:

```text
Business Workflow Monitoring
```

관점.

---

# SLA

Business Workflow 기준 서비스 수준.

중요:

- Infra SLA 아님
- Workflow Completion SLA 중심

Integrity와 SLA는 다르다.

- Integrity = 흐름 정상성
- SLA = 시간/품질 기준

---

# Reaction

Event/Alert 이후 시스템 반응.

예:
- retry
- pause
- escalation
- quarantine

---

# Coverage

플랫폼이 실제 비즈니스 흐름을 얼마나 관측 가능한가.

Synthetic + Event + Workflow 조합으로 측정.
