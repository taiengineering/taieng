# Runtime Monitoring Dashboard

작성일: 2026-05-17
범위: Notification Engine · 운영 관찰 지표

---

## 핵심 지표

| 지표 | 소스 | 갱신 주기 | 임계값 |
|---|---|---|---|
| Unread Count | `/notification-inbox/unread-count` | 30초 | 50+ → HIGH |
| Retry Count | `runtime_notification_queue` status=RETRY_PENDING | 1분 | 5+ → WARNING |
| DLQ Count | `runtime_notification_deadletter` | 10분 | 1+ → CRITICAL |
| Delayed Count | `runtime_notification_queue` status=QUIET_HOUR_DELAYED | 1분 | 정보성 |
| Delivery Latency | timeline RECEIVED→DELIVERED 시간차 | 10분 | 60s+ → WARNING |
| Ignored Ratio | 24h+ unread / total | 1일 | 30%+ → HIGH |
| Queue Depth | PENDING count | 1분 | 100+ → WARNING |
| Feed Growth | notifications 일간 신규 | 1일 | 정보성 |

---

## 관찰 도구

| 도구 | 용도 |
|---|---|
| admin 알림센터 Health 위젯 | Unread/Delayed/Retry/DLQ/상태 |
| `/notification-engine/runtime-summary` | API 기반 상태 조회 |
| `runtime_notification_metrics` | 집계 지표 테이블 |
| cron_job_master 로그 | scheduler 실행 상태 |

---

## 주의

현재 단계: **관찰 중심**. 자동화된 알림/대시보드 구축은 Phase 2.
