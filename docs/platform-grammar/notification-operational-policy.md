# Notification Operational Policy

작성일: 2026-05-17
범위: Notification Engine · 운영 규약

---

## 운영 정책

| 정책 | 값 | 근거 |
|---|---|---|
| Unread polling interval | 30초 | notification.js REFRESH_MS |
| Queue worker interval | 1분 | cron_job_master NOTIFICATION_QUEUE_WORKER |
| Metrics collection interval | 10분 | cron_job_master NOTIFICATION_METRICS |
| Retry max count | 3회 | retry_policy.py |
| Retry interval | 60s → 180s → 540s | Exponential backoff ×3 |
| Quiet Hour behavior | 큐 보류 → 종료 시 일괄 전달 | queue_manager QUIET_HOUR_DELAYED |
| CRITICAL bypass | Quiet Hour 무시, 즉시 전달 | CRITICAL_BYPASS policy |
| Feed suppression | MUTE/DISABLED → Feed 미생성 | Policy Audit 기록 |
| Read retention | 영구 보관 | notifications.is_read |
| Deadletter retention | 영구 보관 (수동 해제) | runtime_notification_deadletter |
| Badge cap | 99+ | 100 이상은 99+ 표시 |
| Feed page size | 20건 | notification-center LIMIT |
| Popup preview size | 5건 | notification.js limit=5 |

---

## 알림 우선순위

1. CRITICAL — 즉시 전달 (Quiet Hour bypass)
2. WARNING — 정상 큐 처리
3. INFO — 정상 큐 처리

---

## 채널 우선순위

1. IN_APP (priority 1) — 항상 전달
2. TELEGRAM (priority 2) — 외부 전달
3. SMS (priority 3) — 긴급 전달
4. PUSH (priority 5) — Phase 2
