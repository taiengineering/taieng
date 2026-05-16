# Notification Runtime Scenarios

작성일: 2026-05-16

---

## NORMAL

```
Event Intake → Recipient Resolve → QUEUED → Worker → Adapter → DELIVERED
```

검증: Queue에 QUEUED 생성 → Audit에 DELIVERED 기록

## MUTE

```
Event Intake → Preference Check → SUPPRESSED (Queue 생성 안 함)
```

검증: Policy Audit에 MUTE/SUPPRESSED 기록

## QUIET_HOUR

```
Event Intake → Preference Check → QUIET_HOUR_DELAYED
  → next_retry_at (QH 종료)
  → Worker Resume → DELIVERED
```

검증: Policy Audit에 QUIET_HOUR/DELAYED + QUIET_HOUR_RESUME/DELIVERED

## CRITICAL_BYPASS

```
Event (severity=CRITICAL) → mute/QH bypass → QUEUED → DELIVERED
```

검증: Policy Audit에 CRITICAL_BYPASS/ALLOWED

## RETRY

```
QUEUED → PROCESSING → FAILED → RETRY_PENDING
  → next_retry_at → PROCESSING → DELIVERED
```

검증: retry_count 증가 + Audit에 RETRY_N 기록

## DLQ

```
RETRY_PENDING → max_retry 초과 → DEADLETTER
```

검증: runtime_notification_deadletter에 이동 + Audit에 DEADLETTER 기록

## E2E 테스트 API

```
POST /notification-engine/run-e2e-test?scenario=NORMAL&channel_key=TELEGRAM
POST /notification-engine/run-e2e-test?scenario=QUIET_HOUR
POST /notification-engine/run-e2e-test?scenario=CRITICAL_BYPASS
```
