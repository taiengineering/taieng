# Delivery Runtime Topology

작성일: 2026-05-17
범위: 현재 Runtime 내부 Delivery Layer 가시화

---

## 현재 구조

```
Notification Runtime (판단)
  │  event_intake → recipient_resolver → queue_manager
  │  policy_check (mute/quiet_hour/CRITICAL bypass)
  ↓
Delivery Layer (실행)
  │
  ├─ runtime_notification_queue (DB)
  │    status: PENDING → PROCESSING → DELIVERED/FAILED
  │
  ├─ Worker (cron 1분)
  │    queue consume → channel_registry 조회 → adapter 호출
  │
  ├─ Adapters
  │    ├─ telegram.py → Telegram Bot API
  │    ├─ sms.py → MessageMi API
  │    ├─ in_app.py → notifications INSERT
  │    └─ push.py → fcm_utils.send_push() (mock→실연동 예정)
  │
  ├─ Retry (max 3, exponential backoff)
  │    FAILED → RETRY_PENDING → Worker 재처리
  │
  ├─ Deadletter
  │    3회 실패 → runtime_notification_deadletter
  │
  ├─ Audit
  │    runtime_notification_policy_audit (정책 결정 기록)
  │    runtime_notification_timeline (단계별 추적)
  │
  └─ Metrics
      runtime_notification_metrics (10분 집계)
```

---

## Delivery Layer 파일 위치

| 구성 | 파일 |
|---|---|
| Queue Manager | `services/notification_engine/queue_manager.py` |
| Worker | `services/notification_engine/worker.py` |
| Adapters | `services/notification_engine/adapters/` |
| Retry | `services/notification_engine/retry_policy.py` |
| Channel Registry | `notification_channel_registry` (DB) |
