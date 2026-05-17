# Notification Wiring Matrix

작성일: 2026-05-17
범위: Notification Engine · Event Wiring

---

## Wiring 매트릭스

| Event | Source | Policy | Audience | Channel | Cooldown | Escalation |
|---|---|---|---|---|---|---|
| workflow_stuck | watch | POLICY_RUNTIME_CRITICAL | operator | TELEGRAM | 0s | ✅ |
| workflow_resumed | watch | POLICY_SERVICE_NOTICE | operator | IN_APP | 300s | ❌ |
| sla_breach | sla | POLICY_SLA_BREACH | tenant_admin | SMS | 0s | ✅ |
| sla_warning | sla | POLICY_RUNTIME_WARNING | tenant_admin | IN_APP | 600s | ❌ |
| schedule_due | scheduler | POLICY_SCHEDULE_REMINDER | safety_manager | IN_APP | 86400s | ❌ |
| schedule_overdue | scheduler | POLICY_WORKFLOW_ALERT | safety_manager | TELEGRAM | 3600s | ✅ |
| payment_success | payment | POLICY_PAYMENT_NOTICE | company_admin | IN_APP | 0s | ❌ |
| payment_failed | payment | POLICY_RUNTIME_WARNING | company_admin | IN_APP | 0s | ❌ |
| subscription_expiring | payment | POLICY_PAYMENT_NOTICE | company_admin | IN_APP | 86400s | ❌ |
| education_due | education | POLICY_EDUCATION_NOTICE | worker | IN_APP | 86400s | ❌ |
| inspection_failed | inspection | POLICY_WORKFLOW_ALERT | safety_manager | TELEGRAM | 0s | ✅ |
| weather_work_stop | external | POLICY_RUNTIME_CRITICAL | site_all | TELEGRAM | 0s | ✅ |
| queue_deadletter | notification | POLICY_RUNTIME_CRITICAL | system_admin | TELEGRAM | 300s | ❌ |
| cron_failure | scheduler | POLICY_RUNTIME_WARNING | system_admin | IN_APP | 600s | ❌ |

---

## 정책 요약

| Policy | Channel | Severity | Quiet Bypass | Digest |
|---|---|---|---|---|
| POLICY_RUNTIME_CRITICAL | TELEGRAM | CRITICAL | ✅ | ❌ |
| POLICY_RUNTIME_WARNING | IN_APP | WARNING | ❌ | ❌ |
| POLICY_SERVICE_NOTICE | IN_APP | INFO | ❌ | ✅ |
| POLICY_WORKFLOW_ALERT | TELEGRAM | WARNING | ❌ | ❌ |
| POLICY_SLA_BREACH | SMS | CRITICAL | ✅ | ❌ |
| POLICY_SCHEDULE_REMINDER | IN_APP | INFO | ❌ | ❌ |
| POLICY_PAYMENT_NOTICE | IN_APP | INFO | ❌ | ❌ |
| POLICY_EDUCATION_NOTICE | IN_APP | INFO | ❌ | ✅ |

---

## Coverage

- Source engines: 7개 (watch, sla, scheduler, payment, education, inspection, external, notification)
- Wiring entries: 14건
- Policy entries: 8건
- Audience types: 6개 (operator, tenant_admin, safety_manager, company_admin, worker, site_all, system_admin)
