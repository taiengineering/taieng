# Runtime Truth Source Registry

작성일: 2026-05-17
범위: Truth Source 단일화

---

## Truth Source

| Truth | Source Runtime | 비고 |
|---|---|---|
| severity | Control Runtime | Watch Engine / Alert Layer |
| incident | Control Runtime | Incident Manager |
| anomaly | Control Runtime | Watch Engine |
| shutdown | Control Runtime | 작업중단 판단 |
| escalation level | Control Runtime | Escalation Manager |
| audience | Notification Intelligence | audience_resolver |
| channel | Notification Intelligence | policy_registry |
| quiet_hour | Notification Intelligence | preference + policy |
| digest | Notification Intelligence | digest_policy_registry |
| suppression (mute) | Notification Intelligence | notification_preferences |
| cooldown | Notification Intelligence | policy_registry + wiring |
| queue_status | Delivery Runtime | runtime_notification_queue |
| delivery_result | Delivery Runtime | adapter 반환값 |
| retry_count | Delivery Runtime | retry_policy |
| timeline | Delivery Runtime | runtime_notification_timeline |
| audit | Delivery Runtime | runtime_notification_policy_audit |
| feed (is_read) | Delivery Runtime | notifications 테이블 |

---

## 핵심

**하나의 Truth에 하나의 Source.** 중복 판단 금지.
