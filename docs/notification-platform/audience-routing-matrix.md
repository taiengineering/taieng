# Audience Routing Matrix

작성일: 2026-05-17
범위: Notification Engine · 누구에게 어떤 알림을

---

## Routing Matrix

| Event | Audience | Channel | Policy | Severity | Escalation |
|---|---|---|---|---|---|
| workflow_stuck | operator | TELEGRAM | CRITICAL | CRITICAL | ✅ |
| workflow_resumed | operator | IN_APP | SERVICE_NOTICE | INFO | ❌ |
| sla_breach | tenant_admin | SMS | SLA_BREACH | CRITICAL | ✅ |
| sla_warning | tenant_admin | IN_APP | RUNTIME_WARNING | WARNING | ❌ |
| schedule_due | safety_manager | IN_APP | SCHEDULE_REMINDER | INFO | ❌ |
| schedule_overdue | safety_manager | TELEGRAM | WORKFLOW_ALERT | WARNING | ✅ |
| payment_success | company_admin | IN_APP | PAYMENT_NOTICE | INFO | ❌ |
| payment_failed | company_admin | IN_APP | RUNTIME_WARNING | WARNING | ❌ |
| subscription_expiring | company_admin | IN_APP | PAYMENT_NOTICE | INFO | ❌ |
| education_due | worker | IN_APP | EDUCATION_NOTICE | INFO | ❌ |
| inspection_failed | safety_manager | TELEGRAM | WORKFLOW_ALERT | WARNING | ✅ |
| weather_work_stop | site_all | TELEGRAM | RUNTIME_CRITICAL | CRITICAL | ✅ |
| queue_deadletter | system_admin | TELEGRAM | RUNTIME_CRITICAL | CRITICAL | ❌ |
| cron_failure | system_admin | IN_APP | RUNTIME_WARNING | WARNING | ❌ |

---

## Audience 별 수신 알림 요약

| Audience | 수신 알림 수 | CRITICAL | WARNING | INFO |
|---|---|---|---|---|
| operator | 2 | 1 | 0 | 1 |
| tenant_admin | 2 | 1 | 1 | 0 |
| safety_manager | 3 | 0 | 2 | 1 |
| company_admin | 3 | 0 | 1 | 2 |
| worker | 1 | 0 | 0 | 1 |
| site_all | 1 | 1 | 0 | 0 |
| system_admin | 2 | 1 | 1 | 0 |
