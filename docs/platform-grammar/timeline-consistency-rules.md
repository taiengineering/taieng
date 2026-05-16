# Timeline Consistency Rules

작성일: 2026-05-16

---

## 규칙

Timeline은 반드시 Queue Reality와 일치해야 함.

| Queue 상태 | Timeline 기대 | 위반 시 Gap |
|---|---|---|
| DELIVERED | AUDIT_DELIVERED step 존재 | TIMELINE_GAP |
| DEADLETTER | AUDIT_DEADLETTER step 존재 | TIMELINE_GAP |
| QUIET_HOUR_DELAYED | POLICY_QUIET_HOUR step 존재 | TIMELINE_GAP |
| QUIET_HOUR_RESUME | POLICY_QUIET_HOUR_RESUME step 존재 | TIMELINE_GAP |
| RETRY_PENDING | AUDIT_RETRY_N step 존재 | TIMELINE_GAP |

## 핵심

Timeline = Queue + Audit + Policy Audit 조합 쿼리.
Audit 누락 = Timeline 누락.
