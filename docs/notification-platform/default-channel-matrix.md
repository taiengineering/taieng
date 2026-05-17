# Default Channel Matrix

작성일: 2026-05-17
범위: 이벤트별 기본 채널

---

## Matrix

| event_key | primary | secondary | feed |
|---|---|---|---|
| signup_completed | IN_APP | — | ✅ |
| login_detected | IN_APP | — | ✅ |
| new_device_login | SMS | IN_APP | ✅ |
| password_reset | SMS | — | ❌ |
| otp_requested | SMS | — | ❌ |
| account_locked | SMS | IN_APP | ✅ |
| payment_success | IN_APP | — | ✅ |
| payment_failed | SMS | IN_APP | ✅ |
| invoice_issued | IN_APP | — | ✅ |
| subscription_expiring | IN_APP | — | ✅ |
| subscription_expired | SMS | IN_APP | ✅ |
| refund_processed | IN_APP | — | ✅ |
| member_invited | IN_APP | — | ✅ |
| member_joined | IN_APP | — | ✅ |
| role_changed | IN_APP | — | ✅ |
| organization_updated | IN_APP | — | ✅ |
| approval_requested | IN_APP | TELEGRAM | ✅ |
| approval_completed | IN_APP | — | ✅ |
| schedule_due | IN_APP | — | ✅ |
| schedule_overdue | TELEGRAM | IN_APP | ✅ |
| inspection_completed | IN_APP | — | ✅ |
| inspection_failed | TELEGRAM | IN_APP | ✅ |
| workflow_stuck | TELEGRAM | IN_APP | ✅ |
| workflow_resumed | IN_APP | — | ✅ |
| weather_work_stop | TELEGRAM | SMS | ✅ |
| accident_reported | SMS | TELEGRAM | ✅ |
| violation_detected | IN_APP | — | ✅ |
| education_due | IN_APP | — | ✅ |
| education_completed | IN_APP | — | ✅ |
| risk_assessment_due | IN_APP | — | ✅ |
| maintenance_notice | IN_APP | — | ✅ |
| incident_notice | IN_APP | — | ✅ |
| deployment_completed | IN_APP | — | ✅ |
| backup_failed | TELEGRAM | IN_APP | ✅ |
| scheduler_failed | IN_APP | — | ✅ |
| service_degraded | TELEGRAM | IN_APP | ✅ |

---

## 채널 우선순위

1. SMS — 긴급 (결제실패, 계정잠금, 사고)
2. TELEGRAM — 실시간 운영 (장애, 워크플로우, 점검초과)
3. IN_APP — 일반 (대부분)
4. PUSH — Phase 2 (FCM)
5. EMAIL — Phase 2 (Digest/공지)
