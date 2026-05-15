# TAI Notification / Alert Engine
## 플랫폼 커뮤니케이션 레이어 설계 정리

작성일: 2026-05-15
프로젝트: 45cm / TAI Platform
상태: 개념 정리 및 플랫폼 코어 승격 단계

---

# 1. 시작 배경

초기 Watch Engine 개발 중,
Alert 기능은 단순히:

```text
운영자에게 Telegram 알림 발송
```

정도로 인식되었다.

그러나 플랫폼 구조를 확장하며 아래 문제가 발견되었다.

- SaaS에서 발생하는 이벤트량은 매우 많다.
- 모든 이벤트를 사람에게 보내면 운영이 붕괴한다.
- 알림 대상은 운영자만이 아니다.
- 사용자 / 관리자 / 직원 / 협력사 / 승인자 등 다양한 계층이 존재한다.
- 권한과 조직 구조에 따라 전달 대상이 달라진다.
- 엔진별로 각각 알림을 구현하면 Notification Chaos가 발생한다.

따라서 Alert 기능은:

```text
Watch Engine의 부속 기능
```

이 아니라,

```text
플랫폼 공통 운영/커뮤니케이션 레이어
```

로 재정의되었다.

---

# 2. 핵심 철학

## 2.1 모든 Event가 Alert가 되면 안 된다

플랫폼은 수많은 이벤트를 발생시킨다.

하지만 실제 운영자가 알아야 하는 것은 극히 일부다.

따라서:

```text
Event ≠ Alert
```

가 핵심 원칙이다.

---

## 2.2 Alert의 본질은 “반응(Reaction)”이다

플랫폼 개념:

```text
Event
→ Workflow
→ Integrity 판단
→ Reaction
→ 필요 시 Human Escalation
```

즉:

- 시스템 자동 반응
- workflow retry
- auto pause
- escalation
- issue 생성
- 통계 집계

등이 모두 Alert Layer의 일부가 될 수 있다.

---

## 2.3 Notification은 역할 기반 업무 전달 시스템이다

플랫폼에서는 같은 이벤트라도:

- 일반 사용자
- 관리자
- 운영자
- 승인자
- 협력사
- tenant owner

등 대상이 달라진다.

따라서 Notification Engine은:

```text
권한/역할 기반 업무 전달 시스템
```

으로 정의된다.

---

# 3. 플랫폼 구조 내 위치

```text
Service
  ↓
emit_event()
  ↓
business_event
  ↓
Integrity Evaluator
  ↓
engine_integrity_event
  ↓
Alert Rule Engine
  ↓
Notification / Reaction Layer
```

---

# 4. 핵심 개념 정의

## Event
플랫폼에서 발생한 구조화된 사건.

## Workflow
의미 있는 Event Sequence.

## Integrity
Workflow가 정상적으로 완료되었는지 판단.

## Alert
운영 중요도로 승격된 Integrity/Event.

## Notification
누구에게 어떤 채널로 어떻게 전달할 것인가를 담당하는 계층.

---

# 5. Notification Engine 핵심 역할

- Audience Resolution
- Permission-aware Delivery
- Channel Routing
- Priority / Severity
- Delivery Policy
- ACK / RESOLVE

---

# 6. Notification Chaos 문제

엔진별 직접 구현 시:

- dedupe 불가능
- cooldown 불일치
- mute 불가능
- severity 기준 충돌
- 운영 피로(alert fatigue)

발생.

따라서 Notification은 반드시 중앙화되어야 한다.

---

# 7. 핵심 운영 원칙

## Event는 많이 저장

플랫폼은 모든 사건을 기록 가능해야 한다.

## Alert는 극도로 적게

진짜 중요한 것만 운영 이슈로 승격.

## 사람은 마지막 Escalation 단계

반복 작업은 시스템이 처리.

---

# 8. Alert Engine → Notification Platform 진화

초기:

```text
Telegram 발송 기능
```

현재 방향:

```text
Event-driven Reaction Platform
```

---

# 9. 현재 구현 상태

구현 완료:

- alert_rule_registry
- alert_history
- cooldown
- dedupe
- mute/unmute
- Telegram test
- ACK/RESOLVE/IGNORE
- Cockpit UI

---

# 10. 현재 부족한 부분

아직 미구현:

- role-based routing
- audience resolution
- organization delivery
- escalation chain
- inbox
- read status
- digest delivery
- multi-channel fallback
- notification template engine

---

# 11. 장기 방향

장기적으로 Notification Engine은:

```text
플랫폼 공통 커뮤니케이션 레이어
```

로 발전 가능.

연결 대상:

- Workflow Engine
- Permission Engine
- Audit Engine
- Rule Engine
- Watch Engine

---

# 12. 최종 정리

Notification Engine은:

```text
메시지 발송 기능
```

이 아니다.

플랫폼 단계에서는:

```text
권한 / 역할 / Workflow / Event / Integrity와 연결된
운영 커뮤니케이션 및 반응 레이어
```

로 정의된다.
