# Notification Engine Phase 1 구현 + 안정화 완료

대상: Claude Code / 개발 에이전트
작성일: 2026-05-15
상태: Phase 1 Complete

---

## 1차 구현 완료 (작업지시서-001)

### DB Migration
- `runtime_notification_event`: severity, tenant_id, trace_id, payload, source_engine, occurred_at, processed_at, error_message 추가
- `runtime_notification_queue`: message_title, message_body, retry_count, max_retries, last_error, dedupe_key, cooldown_until, resolved_at, trace_id, next_retry_at 추가
- `runtime_notification_audit`: channel, queue_id, event_id, error_message, trace_id 추가
- 인덱스: trace_id, event_status, source_engine, dedupe_key, delivery_status, next_retry_at

### Service Layer (`services/notification_engine/`)
- `schemas.py` — Event Contract (NotificationEventCreate, QueueItem)
- `event_intake.py` — Signal 수신 → runtime_notification_event INSERT
- `recipient_resolver.py` — recipient_rule 기반 수신자 결정
- `queue_manager.py` — dedupe/cooldown 포함 Queue 생성 + trace_id 전파
- `adapters/telegram.py` — Telegram Bot API adapter
- `audit.py` — delivery audit trail + trace_id 전파
- `worker.py` — Queue polling + delivery + retry + DLQ 연동
- `pipeline.py` — Registry 검증 → Event → Resolve → Queue

### Watch Engine v2.0 (`watch_engine/alert/engine.py`)
- Telegram 직접 발송 제거 → Notification Pipeline 전환
- Worker 동기 실행 (Queue 즉시 처리)
- `_send_telegram` legacy 호환 유지 (test endpoint용, Phase 2에서 제거)

---

## 2차 안정화 완료 (작업지시서-002)

### DB Migration (Stabilization)
- `notification_event_registry` 신규 테이블 + 8개 이벤트 타입 Seed
- `runtime_notification_deadletter` 신규 테이블 (DLQ)
- `runtime_notification_recipient_rule` CHECK 제약조건 확장 (TELEGRAM, OPERATOR, OWNER 추가)
- Recipient Rule Seed Data 10건

### 추가 서비스 레이어
- `registry.py` — Event Type Registry 조회 + 인메모리 캐시
- `retry_policy.py` — Exponential backoff (base=30s, max=300s, multiplier=2x)
- `deadletter.py` — DLQ 이동 로직 (max_retry 초과 시)

### Worker v2.0 안정화
- PROCESSING 상태 추가 (발송 중 표시)
- RETRY_PENDING + next_retry_at 기반 재시도 poll
- Exponential backoff 적용
- max_retry 초과 시 DLQ 자동 이동
- Audit에 trace_id 전파

### Router v2.0
- `GET /notification-engine/health` — 운영 상태 관측 (queue별 건수, DLQ, 상태 판정)
- `GET /notification-engine/registry` — Event Type Registry 목록
- `GET /notification-engine/deadletters` — DLQ 목록
- 기존 API 모두 유지

### Queue Status 규약 통일
```
QUEUED → PROCESSING → DELIVERED → ACKNOWLEDGED → RESOLVED
                   → RETRY_PENDING → (재시도) → DELIVERED | DEADLETTER
                   → FAILED
                   → IGNORED
```

### 아키텍처 구조 (최종)
```
Any Engine
    ↓
Signal/Event (emit_event)
    ↓
Registry Check (notification_event_registry)
    ↓
Notification Runtime (runtime_notification_event)
    ↓
Recipient Resolution (recipient_resolver + recipient_rule)
    ↓
Delivery Queue (runtime_notification_queue)
    ↓
Worker [PROCESSING → Adapter → Audit]
    ↓
Telegram Adapter (adapters/telegram)
    ↓
Success: DELIVERED → Audit
Fail: RETRY_PENDING (backoff) → 재시도 | DEADLETTER (DLQ)
```

### 성공 기준 충족 상태
- [x] Watch Engine이 직접 Telegram 발송하지 않음
- [x] 모든 Alert가 runtime_notification_event를 통과
- [x] Queue 기반 Telegram 발송 동작
- [x] ACK / RESOLVE lifecycle 정상 동작
- [x] Cooldown / Dedupe 유지
- [x] Notification Event Registry 정상 동작
- [x] Recipient Rule Seed 기반 recipient resolve 성공
- [x] Retry/backoff 정상 동작
- [x] 반복 실패 시 Dead Letter 이동
- [x] Trace ID End-to-End 유지
- [x] Health API 정상 응답
- [x] Queue Status 규약 통일 완료

### 등록된 Event Types
| event_type | severity | source_engine |
|---|---|---|
| WORKFLOW_STUCK | CRITICAL | watch_engine |
| WORKFLOW_TIMEOUT | CRITICAL | watch_engine |
| INTEGRITY_VIOLATION | CRITICAL | watch_engine |
| SLA_BREACH | CRITICAL | watch_engine |
| BROWSER_SYNTHETIC_FAIL | WARNING | watch_engine |
| APPROVAL_REQUIRED | INFO | workflow_engine |
| APPROVAL_TIMEOUT | WARNING | workflow_engine |
| SYSTEM_DEGRADED | CRITICAL | watch_engine |
