# 45cm / TAI Notification Engine

## 개발 목표 및 범위 고정 기획서 (Phase 1)

작성일: 2026-05-15
상태: 개발 범위 고정 초안
대상: 45cm Platform / TAI Runtime

---

# 1. 작성 목적

현재 Notification / Alert 구조는:

- 관제
- 운영
- Workflow
- Runtime
- 업무전달
- Escalation

등으로 빠르게 확장 중이다.

플랫폼 구조 특성상 확장 가능성이 매우 크기 때문에, 목표와 범위를 고정하지 않으면 무한 엔진 개발 상태로 진입할 위험이 있다.

따라서 본 문서는 Phase 1 Notification Engine의 명확한 목표, 역할, 범위, 제외사항을 정의한다.

---

# 2. 현재 상황 정의

현재 시스템에는 아래 3개 계층이 혼재되어 있다.

## 2.1 Legacy Notification

기존 업무 알림 시스템.

예:

- notifications
- notification_queue
- overdue_history

특징:

- 사용자 알림 중심
- 업무 overdue 중심
- SMS / Push 중심

## 2.2 Watch Alert System

관제 중심 시스템.

예:

- alert_rule_registry
- alert_history
- Telegram alert

특징:

- 운영 감시
- integrity alert
- cooldown / dedupe

## 2.3 Runtime Notification Layer

차세대 구조.

예:

- runtime_notification_event
- runtime_notification_queue
- runtime_escalation_queue

특징:

- Event 기반
- Runtime 기반
- 역할 기반 확장 가능

---

# 3. 핵심 전략 결정

Notification Engine은 메시지 발송 기능이 아니다.

현재 플랫폼 기준 정의는 다음과 같다.

```text
Event 기반 운영 커뮤니케이션 엔진
```

---

# 4. Phase 1 최종 목표

Phase 1의 목표는 다음과 같다.

```text
모든 엔진의 이벤트를 중앙 Notification Runtime으로 수렴
```

즉 Watch Engine, Workflow Engine, Runtime Engine, Approval Engine 등은 직접 메시지 발송을 하지 않는다.

---

# 5. 핵심 원칙

## 5.1 Engine은 Signal만 발생

모든 엔진은 Event / Signal 생성만 수행한다.

## 5.2 Notification Engine만 Delivery 수행

실제 발송은 Notification Engine만 수행한다.

## 5.3 Event Contract 통일

모든 엔진은 공통 Event 규약을 사용한다.

필수 필드:

- event_type
- source_engine
- severity
- tenant_id
- trace_id
- occurred_at
- payload

## 5.4 Alert ≠ Notification

구조:

```text
Event
→ Integrity
→ Alert
→ Notification
```

## 5.5 사람은 마지막 Escalation

우선순위:

```text
자동 처리
→ Retry
→ Queue
→ Escalation
→ Human
```

---

# 6. Phase 1 범위

포함 범위:

- Event Intake Layer
- Unified Notification Event
- Recipient Resolution (기본)
- Unified Delivery Queue
- Telegram Delivery
- ACK / RESOLVE Lifecycle
- Cooldown / Dedupe
- Cockpit UI 연동

---

# 7. 제외 범위

현재 단계에서 제외:

- 조직도 엔진
- Inbox Platform
- Slack-style 협업
- AI Routing
- Multi-region Messaging
- Notification Marketplace
- 완전한 BPM

---

# 8. 핵심 개발 범위

## 8.1 Notification Event Adapter

각 엔진 Event → Notification Event 변환.

## 8.2 Recipient Resolver

누가 받아야 하는가 결정.

## 8.3 Delivery Queue Worker

Queue → Telegram 발송.

## 8.4 Delivery Audit

발송 기록 저장.

## 8.5 ACK Lifecycle

운영 개입 상태 관리.

---

# 9. 기존 시스템 처리 방향

## 9.1 Watch Engine

Telegram 직접 발송 제거.

대신:

```text
runtime_notification_event 생성
```

## 9.2 Legacy Notification

즉시 삭제 금지.

유지 + 점진 통합 전략 사용.

## 9.3 runtime_notification_* 계층

플랫폼 Notification Core로 승격.

---

# 10. 성공 기준

- 모든 운영 Alert가 runtime_notification_event로 수렴
- Watch Engine이 직접 발송하지 않음
- Telegram Delivery가 Queue 기반으로 동작
- ACK / RESOLVE lifecycle 정상 동작
- Cooldown / Dedupe 유지

---

# 11. 금지사항

- Notification Engine 안에 비즈니스 로직 넣기
- Engine 간 직접 발송
- AI 기반 recipient 추론
- 채널별 로직 분산

---

# 12. 최종 정의

Phase 1 Notification Engine은:

```text
모든 플랫폼 이벤트를 중앙 운영 커뮤니케이션 Queue로 수렴시키는 엔진
```

이다.

현재 목표는 완전한 협업 플랫폼 구축이 아니다.

현재 목표는:

```text
운영 Alert / Runtime Notification / Escalation의 중앙화와 규약 통일
```

이다.

---

# 13. 최종 결론

현재 단계에서 가장 중요한 것은 기능 수 증가가 아니다.

핵심은:

- Event 규약 통일
- Notification 중앙화
- Engine 간 역할 분리

이다.

그리고 반드시 유지해야 하는 핵심 철학은:

```text
Engine은 감지한다
Notification Engine은 전달한다
사람은 마지막에만 개입한다
```

이다.
