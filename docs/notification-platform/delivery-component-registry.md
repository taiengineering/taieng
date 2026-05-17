# Delivery Component Registry

작성일: 2026-05-17
범위: Delivery 관련 구성 전수

---

## 구성 목록

| 구성 | 역할 | 파일/테이블 | 상태 |
|---|---|---|---|
| Queue Manager | 큐 INSERT + 상태 관리 | `queue_manager.py` | ✅ Active |
| Worker | 큐 consume + adapter 호출 | `worker.py` | ✅ Active (cron 1분) |
| Telegram Adapter | Telegram Bot API 발송 | `adapters/telegram.py` | ✅ Active |
| SMS Adapter | MessageMi API 발송 | `adapters/sms.py` | ✅ Active |
| IN_APP Adapter | notifications INSERT | `adapters/in_app.py` | ✅ Active |
| Push Adapter | FCM 발송 | `adapters/push.py` | ⬜ Mock (dev) |
| Retry Policy | 재시도 로직 (3회, exponential) | `retry_policy.py` | ✅ Active |
| Deadletter | 최종 실패 격리 | `runtime_notification_deadletter` | ✅ Active |
| Metrics Aggregator | 10분 집계 | `metrics_aggregator.py` | ✅ Active |
| Policy Audit | 정책 결정 기록 | `runtime_notification_policy_audit` | ✅ Active |
| Timeline | 단계별 추적 | `runtime_notification_timeline` | ✅ Active |
| Channel Registry | 채널 설정 | `notification_channel_registry` | ✅ Active (5 channels) |
| Queue Table | 전달 대기열 | `runtime_notification_queue` | ✅ Active |

---

## 요약

| 분류 | 건수 |
|---|---|
| Active | 11 |
| Mock | 1 (Push) |
| 미구현 | 0 |
