# SaaS Notification Catalog

작성일: 2026-05-17
범위: TAI Safe 플랫폼 기본 알림 체계

---

## 목적

**플랫폼이 기본적으로 어떤 알림을 제공하는가** 공식화.

---

## Pack 구성 (8개)

| Pack | 이벤트 수 | 목적 |
|---|---|---|
| Auth | 6 | 인증/보안 |
| Billing | 6 | 결제/재무 |
| Subscription | 4 | 구독 관리 |
| Organization | 6 | 조직/협업 |
| Workflow | 6 | 안전 워크플로우 |
| Safety | 6 | 안전 관리 |
| System | 6 | 시스템 운영 |
| Marketing | 3 | 마케팅 (Phase 2) |

---

## 전체 Catalog

| event_key | Pack | audience | severity | channel |
|---|---|---|---|---|
| signup_completed | Auth | tenant_admin | INFO | IN_APP |
| login_detected | Auth | tenant_admin | INFO | IN_APP |
| new_device_login | Auth | tenant_admin | WARNING | SMS |
| password_reset | Auth | actor | INFO | SMS |
| otp_requested | Auth | actor | INFO | SMS |
| account_locked | Auth | tenant_admin | CRITICAL | SMS+IN_APP |
| payment_success | Billing | company_admin | INFO | IN_APP |
| payment_failed | Billing | company_admin | WARNING | SMS+IN_APP |
| invoice_issued | Billing | company_admin | INFO | IN_APP |
| subscription_expiring | Subscription | company_admin | WARNING | IN_APP |
| subscription_expired | Subscription | company_admin | CRITICAL | SMS+IN_APP |
| subscription_activated | Subscription | company_admin | INFO | IN_APP |
| subscription_plan_changed | Subscription | company_admin | INFO | IN_APP |
| refund_processed | Billing | company_admin | INFO | IN_APP |
| member_invited | Organization | actor | INFO | IN_APP |
| member_joined | Organization | tenant_admin | INFO | IN_APP |
| role_changed | Organization | actor | WARNING | IN_APP |
| organization_updated | Organization | tenant_admin | INFO | IN_APP |
| approval_requested | Organization | approver | WARNING | IN_APP+TELEGRAM |
| approval_completed | Organization | requester | INFO | IN_APP |
| schedule_due | Workflow | safety_manager | INFO | IN_APP |
| schedule_overdue | Workflow | safety_manager | WARNING | TELEGRAM |
| inspection_completed | Workflow | safety_manager | INFO | IN_APP |
| inspection_failed | Workflow | safety_manager | WARNING | TELEGRAM |
| workflow_stuck | Workflow | operator | CRITICAL | TELEGRAM |
| workflow_resumed | Workflow | operator | INFO | IN_APP |
| weather_work_stop | Safety | site_all | CRITICAL | TELEGRAM |
| accident_reported | Safety | safety_manager | CRITICAL | SMS+TELEGRAM |
| violation_detected | Safety | safety_manager | WARNING | IN_APP |
| education_due | Safety | worker | INFO | IN_APP |
| education_completed | Safety | safety_manager | INFO | IN_APP |
| risk_assessment_due | Safety | safety_manager | WARNING | IN_APP |
| maintenance_notice | System | tenant_admin | INFO | IN_APP |
| incident_notice | System | tenant_admin | WARNING | IN_APP |
| deployment_completed | System | system_admin | INFO | IN_APP |
| backup_failed | System | system_admin | CRITICAL | TELEGRAM |
| scheduler_failed | System | system_admin | WARNING | IN_APP |
| service_degraded | System | system_admin | CRITICAL | TELEGRAM |
| campaign_sent | Marketing | tenant_admin | INFO | IN_APP |
| newsletter_published | Marketing | tenant_admin | INFO | IN_APP |
| feature_announcement | Marketing | tenant_admin | INFO | IN_APP |

---

## 총 이벤트: 43개
