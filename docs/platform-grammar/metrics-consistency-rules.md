# Metrics Consistency Rules

작성일: 2026-05-16

---

## 규칙

| 조건 | 기대 Metrics | 위반 시 Gap 유형 |
|---|---|---|
| DEADLETTER 존재 | dlq_count 증가 | METRIC_GAP |
| QUIET_HOUR_DELAYED 존재 | delayed_count 증가 | METRIC_GAP |
| DELIVERED 증가 | success_throughput 증가 | METRIC_GAP |
| FAILED 증가 | fail_throughput 증가 | METRIC_GAP |
| RETRY_PENDING 존재 | avg_retry_count > 0 | METRIC_GAP |

## 제한

Metrics는 10분 window snapshot. trace_id 기반 정합성 검증은 제한적.
권장: collect-metrics 후 확인.
