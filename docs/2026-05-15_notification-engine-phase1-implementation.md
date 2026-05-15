# Notification Engine Phase 1 구현 작업지시서

대상: Claude Code / 개발 에이전트
작성일: 2026-05-15
상태: 실행 지시서

---

## 구현 완료 사항 (2026-05-15)

### DB Migration
- `runtime_notification_event`: severity, tenant_id, trace_id, payload, source_engine, occurred_at, processed_at, error_message 추가
- `runtime_notification_queue`: message_title, message_body, retry_count, max_retries, last_error, dedupe_key, cooldown_until, resolved_at 추가
- `runtime_notification_audit`: channel, queue_id, event_id, error_message 추가
- 인덱스: trace_id, event_status, source_engine, dedupe_key, delivery_status

### Service Layer (`services/notification_engine/`)
- `schemas.py` — Event Contract (NotificationEventCreate, QueueItem)
- `event_intake.py` — Signal 수신 → runtime_notification_event INSERT
- `recipient_resolver.py` — recipient_rule 기반 수신자 결정
- `queue_manager.py` — dedupe/cooldown 포함 Queue 생성
- `adapters/telegram.py` — Telegram Bot API adapter
- `audit.py` — delivery audit trail
- `worker.py` — Queue polling + delivery orchestration
- `pipeline.py` — Event → Resolve → Queue 전체 파이프라인

### Watch Engine v2.0 (`watch_engine/alert/engine.py`)
- Telegram 직접 발송 제거
- Notification Pipeline 전환
- Worker 동기 실행 (Queue 즉시 처리)
- `_send_telegram` legacy 호환 유지 (test endpoint용, Phase 2에서 제거)

### Router (`routers/notification_engine_api.py`)
- `POST /notification-engine/process-queue` — Queue Worker 수동 실행
- `GET /notification-engine/queue-status` — Queue 현황
- `GET /notification-engine/events` — 최근 이벤트
- `POST /notification-engine/emit-test` — 테스트 이벤트 + Pipeline + Worker
- `POST /notification-engine/ack/{queue_id}` — ACK
- `POST /notification-engine/resolve/{queue_id}` — RESOLVE

### 아키텍처 구조
```
Any Engine
    ↓
Signal/Event (emit_event)
    ↓
Notification Runtime (runtime_notification_event)
    ↓
Recipient Resolution (recipient_resolver)
    ↓
Delivery Queue (runtime_notification_queue)
    ↓
Telegram Worker (adapters/telegram)
    ↓
Audit (runtime_notification_audit)
```

### 성공 기준 충족 상태
- [x] Watch Engine이 직접 Telegram 발송하지 않음
- [x] 모든 Alert가 runtime_notification_event를 통과
- [x] Queue 기반 Telegram 발송 동작
- [x] ACK / RESOLVE lifecycle 정상 동작
- [x] Cooldown / Dedupe 유지
