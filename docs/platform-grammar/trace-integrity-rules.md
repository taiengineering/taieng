# Trace Integrity Rules

작성일: 2026-05-16

---

## 규칙

| 규칙 | 설명 | 검증 API |
|---|---|---|
| Feed item은 trace_id를 가져야 한다 | IN_APP Adapter INSERT 시 trace_id 저장 | `/runtime-consistency/{trace_id}` |
| Audit는 동일 trace_id를 유지해야 한다 | Pipeline → Queue → Worker → Audit 전체 전파 | `/notification-engine/timeline/{trace_id}` |
| Policy Audit는 Runtime Trace에 연결되어야 한다 | queue_manager에서 trace_id 전달 | `/notification-engine/policy-audit` |
| Queue item은 event trace_id를 상속한다 | Pipeline 생성 시 전파 | Queue 조회 |
| DLQ item은 원본 trace_id를 보존한다 | deadletter.move_to_deadletter() | DLQ 조회 |

## Trace 경로

```
Pipeline (trace_id 생성)
  → runtime_notification_event.trace_id
  → runtime_notification_queue.trace_id
  → runtime_notification_audit.trace_id
  → runtime_notification_policy_audit.trace_id
  → notifications.trace_id (IN_APP)
```

## 위반 시

trace_id 누락 = **운영 추적 불가**

`/runtime-consistency/{trace_id}`에서 FEED_GAP 또는 AUDIT_GAP으로 보고.
