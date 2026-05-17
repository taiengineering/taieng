# Operational Truth Ownership Matrix

작성일: 2026-05-17
범위: Truth Source 단일화 재정리

---

## Truth Ownership

| Truth | Owner Runtime | 소스 | 비고 |
|---|---|---|---|
| severity_truth | **Control Runtime** | Watch Engine / Alert Layer | 현재: Policy default 임시 사용 |
| incident_truth | **Control Runtime** | Incident Manager | 현재: 미구현 |
| escalation_truth | **Control Runtime** | Escalation Manager | 현재: 미구현 (플래그만) |
| recovery_truth | **Control Runtime** | Recovery Manager | 현재: 미구현 |
| operator_state_truth | **Control Runtime** | Watch Engine | 현재: 미구현 |
| audience_truth | **Notification Intelligence** | audience_resolver | ✅ 정상 |
| channel_truth | **Notification Intelligence** | policy_registry | ✅ 정상 |
| communication_priority | **Notification Intelligence** | severity snapshot 기반 | ✅ 정상 |
| quiet_hour_truth | **Notification Intelligence** | preference + policy | ✅ 정상 |
| digest_truth | **Notification Intelligence** | digest_policy_registry | ✅ 정상 |
| suppression_truth (mute) | **Notification Intelligence** | notification_preferences | ✅ 정상 |
| queue_status_truth | **Delivery Runtime** | runtime_notification_queue | ✅ 정상 |
| delivery_result_truth | **Delivery Runtime** | adapter 반환값 | ✅ 정상 |
| retry_truth | **Delivery Runtime** | retry_policy | ✅ 정상 |
| ack_truth | **Delivery Runtime** | queue ACKNOWLEDGED | ✅ 정상 |
| timeline_truth | **Delivery Runtime** | runtime_notification_timeline | ✅ 정상 |
| audit_truth | **Delivery Runtime** | runtime_notification_policy_audit | ✅ 정상 |

---

## 핵심

**하나의 Truth에 하나의 Owner.** Control Runtime 미구현 항목(5건)은 Notification이 임시 대체 중 — Control 구현 시 이관.
