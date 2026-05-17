# Runtime Event Ownership Matrix

작성일: 2026-05-17
범위: 이벤트 카테고리별 소유 Runtime

---

## Ownership

| Event Category | Owner Runtime | truth_source | 예시 |
|---|---|---|---|
| control | Control Runtime | `control` | workflow_stuck, sla_breach |
| workflow | Workflow Runtime | `workflow` | schedule_due, schedule_overdue, inspection_completed |
| billing | Billing Runtime | `billing` | payment_failed, subscription_activated |
| auth | Auth Runtime | `auth` | login_detected, account_locked |
| organization | Organization Runtime | `organization` | member_invited, approval_requested |
| safety | Safety Runtime | `safety` | accident_reported, weather_work_stop, violation_detected |
| education | Education Runtime | `education` | education_due, education_completed |
| system | System Runtime | `system` | backup_failed, scheduler_failed, service_degraded |
| marketing | Marketing Runtime | `marketing` | campaign_sent, feature_announcement |

---

## 규칙

1. **하나의 event_type에 하나의 Owner** — 이중 발행 금지
2. **truth_source = Owner Runtime** — 발생 주체가 truth_source
3. **event_type 명명은 Owner 기준** — billing 이벤트는 `payment_*`, safety는 `accident_*`
