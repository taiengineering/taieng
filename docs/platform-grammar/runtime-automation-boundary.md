# Runtime Automation Boundary

작성일: 2026-05-16

---

## 자동화 영역

| 영역 | 자동화 | 주기 | 방식 |
|---|---|---|---|
| Queue Poll (QUEUED) | ✅ 자동 | 1분 | NOTIFICATION_QUEUE_WORKER cron |
| Retry Poll (RETRY_PENDING) | ✅ 자동 | 1분 | 동일 Worker |
| Quiet Hour Resume | ✅ 자동 | 1분 | 동일 Worker (next_retry_at) |
| Metrics Collection | ✅ 자동 | 10분 | NOTIFICATION_METRICS cron |
| Feed Read | ❌ 수동 | - | 사용자 액션 |
| ACK | ❌ 수동 | - | 운영자 액션 |
| Resolve | ❌ 수동 | - | 운영자 액션 |
| Preference 변경 | ❌ 수동 | - | 사용자 설정 |

## 핵심

```
Operational Runtime과 Human Operation은 다르다
```

- **Operational Runtime**: 시스템이 자동 순환 (Queue/Retry/QH/Metrics)
- **Human Operation**: 사람이 의도적으로 수행 (Read/ACK/Resolve/Preference)

## Scheduler 등록

- `cron_job_master`: NOTIFICATION_QUEUE_WORKER (1분), NOTIFICATION_METRICS (10분)
- `scheduler.py` v1.8: direct handler 등록
- 시작: Railway deploy 시 `start_scheduler()` 자동 호출
