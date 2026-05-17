# Runtime Ownership Matrix

작성일: 2026-05-17
범위: 기능별 소유 Runtime

---

## Ownership

| 기능 | Owner | 파일/테이블 |
|---|---|---|
| Event Intake | Notification | event_intake.py |
| Recipient Resolve | Notification | recipient_resolver.py |
| Event Wiring | Notification | event_wiring.py |
| Audience Resolve | Notification | audience_resolver.py |
| Digest Check | Notification | digest_runtime.py |
| Policy Check | Notification | queue_manager.py (policy 부분) |
| Queue Insert | Delivery | queue_manager.py (queue 부분) |
| Worker Consume | Delivery | worker.py |
| Adapter Call | Delivery | adapters/*.py |
| Retry Logic | Delivery | retry_policy.py |
| DLQ Escalation | Delivery | worker.py |
| Policy Audit | Delivery | policy_audit INSERT |
| Timeline Record | Delivery | timeline INSERT |
| Feed Insert | Delivery | in_app adapter |
| Metrics Aggregate | Delivery | metrics_aggregator.py |
| Severity Decision | Control | Watch Engine (별도) |
| Incident Creation | Control | (미구현, 별도) |
| Anomaly Detection | Control | Watch Engine (별도) |

---

## 규칙

**중복 Owner 금지.** 하나의 기능에 하나의 Owner만 존재.
