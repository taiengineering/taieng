# Runtime Integration Boundary v2

작성일: 2026-05-17
범위: 외부 Runtime 허용/금지

---

## 외부 Runtime 허용

| 항목 | 설명 |
|---|---|
| Event Publish | `wire_and_emit(event_type, payload)` 호출 |
| Truth Publish | severity_snapshot, incident_ref 제공 |
| Audience Hint | audience_key override |
| Payload Attach | payload에 임의 데이터 첨부 |
| Channel Hint | override_channel 제공 |
| Severity Override | override_severity 제공 |

---

## 외부 Runtime 금지

| 항목 | 이유 |
|---|---|
| Queue Mutation | Delivery Runtime 전용 |
| Retry Control | Delivery Runtime 전용 |
| Adapter Access | Delivery Runtime 전용 |
| Timeline Mutation | Delivery Runtime 전용 |
| Delivery Status Override | Delivery Runtime 전용 |
| Feed Direct INSERT | IN_APP Adapter 전용 |
| Policy Mutation | Notification Admin 전용 |
| Wiring Direct INSERT | Admin API 전용 |

---

## 핵심

**외부 Runtime은 Event를 발행할 뿐, 내부 처리를 제어하지 않는다.**
