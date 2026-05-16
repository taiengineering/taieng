# Runtime Truth Matrix

작성일: 2026-05-16

---

| Runtime State | Queue | Feed (IN_APP) | Audit | Policy Audit | Metrics | Timeline |
|---|---|---|---|---|---|---|
| QUEUED | ✅ 항목 존재 | ❌ 미생성 | ❌ 아직 | ✅ ALLOWED 가능 | ✅ queue_count | ✅ QUEUE step |
| PROCESSING | ✅ status=PROCESSING | ❌ | ❌ | - | ✅ processing_count | ✅ PROCESSING step |
| DELIVERED | ✅ status=DELIVERED | ✅ 생성 (IN_APP) | ✅ DELIVERED | - | ✅ delivered_count | ✅ DELIVERED step |
| FAILED | ✅ status=FAILED | ❌ | ✅ FAILED | - | ✅ failed_count | ✅ FAILED step |
| RETRY_PENDING | ✅ status=RETRY | ❌ | ✅ RETRY_N | - | ✅ retry_count | ✅ RETRY step |
| DEADLETTER | ✅ + DLQ 테이블 | ❌ | ✅ DEADLETTER | - | ✅ dlq_count | ✅ DLQ step |
| QUIET_HOUR_DELAYED | ✅ status=QH_DELAYED | ❌ | ❌ | ✅ QUIET_HOUR/DELAYED | ✅ delayed_count | ✅ POLICY_QH |
| SUPPRESSED | ❌ Queue 미생성 | ❌ | ❌ | ✅ MUTE/SUPPRESSED | ❌ | ✅ POLICY_MUTE |
| READ | ✅ (IN_APP) | ✅ is_read=true | ❌ | ❌ | ❌ | ❌ |
| ACKNOWLEDGED | ✅ status=ACK | ❌ | ✅ ACK | ❌ | ✅ ack_count | ✅ ACK step |
