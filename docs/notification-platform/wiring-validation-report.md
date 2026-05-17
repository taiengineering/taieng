# Wiring Validation Report

작성일: 2026-05-17
범위: 21 Wiring 검증

---

## 검증 결과

| wiring_key | wiring | policy | audience | emit 가능 | feed 가능 | timeline 가능 | 결과 |
|---|---|---|---|---|---|---|---|
| WIRE_WORKFLOW_STUCK | ✅ | ✅ CRITICAL | ✅ operator | ✅ | ✅ | ✅ | **PASS** |
| WIRE_WORKFLOW_RESUMED | ✅ | ✅ INFO | ✅ operator | ✅ | ✅ | ✅ | **PASS** |
| WIRE_SLA_BREACH | ✅ | ✅ CRITICAL | ✅ tenant_admin | ✅ | ✅ | ✅ | **PASS** |
| WIRE_SLA_WARNING | ✅ | ✅ WARNING | ✅ tenant_admin | ✅ | ✅ | ✅ | **PASS** |
| WIRE_SCHEDULE_DUE | ✅ | ✅ INFO | ✅ safety_manager | ✅ | ✅ | ✅ | **PASS** |
| WIRE_SCHEDULE_OVERDUE | ✅ | ✅ WARNING | ✅ safety_manager | ✅ | ✅ | ✅ | **PASS** |
| WIRE_PAYMENT_SUCCESS | ✅ | ✅ INFO | ✅ company_admin | ✅ | ✅ | ✅ | **PASS** |
| WIRE_PAYMENT_FAILED | ✅ | ✅ WARNING | ✅ company_admin | ✅ | ✅ | ✅ | **PASS** |
| WIRE_SUBSCRIPTION_EXPIRING | ✅ | ✅ INFO | ✅ company_admin | ✅ | ✅ | ✅ | **PASS** |
| WIRE_EDUCATION_DUE | ✅ | ✅ INFO | ✅ worker | ✅ | ✅ | ✅ | **PASS** |
| WIRE_INSPECTION_FAILED | ✅ | ✅ WARNING | ✅ safety_manager | ✅ | ✅ | ✅ | **PASS** |
| WIRE_WEATHER_ALERT | ✅ | ✅ CRITICAL | ✅ site_all | ✅ | ✅ | ✅ | **PASS** |
| WIRE_QUEUE_DEADLETTER | ✅ | ✅ CRITICAL | ✅ system_admin | ✅ | ✅ | ✅ | **PASS** |
| WIRE_CRON_FAILURE | ✅ | ✅ WARNING | ✅ system_admin | ✅ | ✅ | ✅ | **PASS** |
| WIRE_APPROVAL_REQUESTED | ✅ | ✅ WARNING | ✅ tenant_admin | ✅ | ✅ | ✅ | **PASS** |
| WIRE_APPROVAL_COMPLETED | ✅ | ✅ INFO | ✅ tenant_admin | ✅ | ✅ | ✅ | **PASS** |
| WIRE_MEMBER_INVITED | ✅ | ✅ INFO | ✅ tenant_admin | ✅ | ✅ | ✅ | **PASS** |
| WIRE_MEMBER_JOINED | ✅ | ✅ INFO | ✅ tenant_admin | ✅ | ✅ | ✅ | **PASS** |
| WIRE_SUBSCRIPTION_EXPIRED | ✅ | ✅ CRITICAL | ✅ company_admin | ✅ | ✅ | ✅ | **PASS** |
| WIRE_ACCIDENT_REPORTED | ✅ | ✅ CRITICAL | ✅ safety_manager | ✅ | ✅ | ✅ | **PASS** |
| WIRE_VIOLATION_DETECTED | ✅ | ✅ WARNING | ✅ safety_manager | ✅ | ✅ | ✅ | **PASS** |

---

## 요약

**21/21 = 100% PASS** (Wiring → Policy → Audience → Runtime emit 가능)

실제 wire_and_emit() 코드 연결은 별도 작업 필요 (현재 Wiring Ready 상태).
