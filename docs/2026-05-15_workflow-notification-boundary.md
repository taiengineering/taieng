# Workflow Engine ↔ Notification Runtime Boundary 정의

작성일: 2026-05-15
상태: Phase 1 Complete

---

## 핵심 원칙

```
Workflow는 상태를 만든다
Notification은 상태를 전달한다
```

Workflow와 Notification은 **직접 연결되지 않는다**.

---

## 영역별 책임

| 영역 | 책임 | 예시 |
|---|---|---|
| **Workflow Engine** | 상태 흐름 (State Transition) | CREATED → VALIDATING → APPROVED |
| **Integrity Layer** | 흐름 정상성 평가 | 부적합 전이 감지, 데이터 무결성 검증 |
| **SLA Layer** | 기준 측정 | 승인 타임아웃, 처리 지연 감지 |
| **Alert Layer** | 운영 중요도 판단 | INFO → WARNING → CRITICAL 승격 |
| **Notification Runtime** | 전달 | Telegram 발송, Queue, Audit |

---

## 아키텍처 흐름

```
Workflow Engine
    ↓
Workflow Event (Contract)
    ↓
Event Layer (workflow_event_log)
    ↓
Integrity Layer (integrity_hooks)
    ↓
Alert Layer (severity 판단)
    ↓
Notification Runtime (Pipeline → Queue → Worker → Adapter)
```

---

## 금지사항

1. Workflow Engine에서 직접 Telegram/SMS/Email 호출 금지
2. Notification Runtime 내부에서 workflow state 변경 금지
3. Notification Runtime 내부에서 business transition / approval 처리 금지
4. Workflow와 Notification 직접 연결 금지 (반드시 Event Layer 경유)

---

## DB 구조

### Workflow Engine 영역
- `workflow_state_registry` — 상태 정의 (COMMON: 8개 상태)
- `workflow_transition_registry` — 전이 규칙 (COMMON: 10개 전이)
- `workflow_event_log` — 상태 전이 이벤트 로그 (Timeline 기반)

### Notification Engine 영역
- `notification_event_registry` — 이벤트 타입 정의
- `runtime_notification_event` — 이벤트 수신
- `runtime_notification_queue` — Delivery Queue
- `runtime_notification_audit` — Audit Trail
- `runtime_notification_deadletter` — DLQ
- `runtime_notification_metrics` — Metrics
- `runtime_notification_recipient_rule` — 수신자 규칙

---

## API 경계

### Workflow Engine (`/workflow/*`)
- `GET /workflow/states` — 상태 레지스트리
- `GET /workflow/transitions` — 전이 레지스트리
- `GET /workflow/allowed-next/{state}` — 다음 허용 상태
- `POST /workflow/validate-transition` — 전이 검증
- `POST /workflow/emit` — 상태 변화 이벤트 발행
- `GET /workflow/timeline/{workflow_id}` — 상태 전이 타임라인

### Notification Engine (`/notification-engine/*`)
- `GET /notification-engine/health` — Runtime Health
- `GET /notification-engine/runtime-summary` — 실시간 요약
- `GET /notification-engine/metrics` — Metrics 이력
- `POST /notification-engine/collect-metrics` — Metrics 집계
- `GET /notification-engine/timeline/{trace_id}` — Trace Timeline
- `GET /notification-engine/registry` — Event Registry
- `GET /notification-engine/deadletters` — DLQ
- `POST /notification-engine/process-queue` — Worker 실행
- `POST /notification-engine/emit-test` — E2E 테스트

---

## 철학

```
Workflow는 상태를 만든다
Integrity는 상태를 평가한다
Alert는 운영 중요도를 판단한다
Notification은 전달한다
```
