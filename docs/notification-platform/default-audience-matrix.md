# Default Audience Matrix

작성일: 2026-05-17
범위: 이벤트별 기본 수신 대상

---

## Matrix

| event_key | 기본 audience | fallback audience |
|---|---|---|
| signup_completed | tenant_admin | system_admin |
| login_detected | tenant_admin | — |
| new_device_login | tenant_admin | system_admin |
| password_reset | actor | — |
| otp_requested | actor | — |
| account_locked | tenant_admin | system_admin |
| payment_success | company_admin | tenant_admin |
| payment_failed | company_admin | tenant_admin |
| invoice_issued | company_admin | tenant_admin |
| subscription_expiring | company_admin | tenant_admin |
| subscription_expired | company_admin | tenant_admin |
| refund_processed | company_admin | tenant_admin |
| member_invited | actor | — |
| member_joined | tenant_admin | — |
| role_changed | actor | tenant_admin |
| organization_updated | tenant_admin | — |
| approval_requested | approver | tenant_admin |
| approval_completed | requester | — |
| schedule_due | safety_manager | operator |
| schedule_overdue | safety_manager | operator |
| inspection_completed | safety_manager | — |
| inspection_failed | safety_manager | operator |
| workflow_stuck | operator | system_admin |
| workflow_resumed | operator | — |
| weather_work_stop | site_all | operator |
| accident_reported | safety_manager | operator |
| violation_detected | safety_manager | — |
| education_due | worker | safety_manager |
| education_completed | safety_manager | — |
| risk_assessment_due | safety_manager | operator |
| maintenance_notice | tenant_admin | — |
| incident_notice | tenant_admin | — |
| deployment_completed | system_admin | — |
| backup_failed | system_admin | — |
| scheduler_failed | system_admin | — |
| service_degraded | system_admin | — |

---

## Audience Types

| audience_key | 역할 |
|---|---|
| actor | 이벤트 당사자 |
| approver | 승인권자 |
| requester | 요청자 |
| tenant_admin | 테넌트 관리자 |
| company_admin | 회사 관리자 |
| safety_manager | 안전관리자 |
| operator | 운영자 |
| worker | 작업자 |
| site_all | 현장 전체 |
| system_admin | 시스템 관리자 |
