# Quiet Hour Runtime Flow

작성일: 2026-05-16

---

## 흐름

```
Notification Request
    ↓
Preference Check (queue_manager._check_preferences)
    ↓
── severity=CRITICAL → QUEUED (즉시, bypass)
── muted/disabled → SUPPRESSED (Queue 생성 안 함)
── quiet_hour 범위 내 → QUIET_HOUR_DELAYED
── 정상 → QUEUED
    ↓
QUIET_HOUR_DELAYED
  • delivery_status = QUIET_HOUR_DELAYED
  • next_retry_at = preference quiet_hour_end (KST → UTC)
  • policy_audit: QUIET_HOUR / DELAYED
    ↓
Worker Poll (next_retry_at 도래 시)
  • QUIET_HOUR_DELAYED 항목 poll
  • PROCESSING 전환
  • Adapter 실행
    ↓
DELIVERED
  • policy_audit: QUIET_HOUR_RESUME / DELIVERED
  • audit: DELIVERED
```

## 시간 계산

- KST 단일 timezone
- actor의 `quiet_hour_end` preference 기반
- 기본값: KST 07:00
- UTC 변환: KST - 9시간

## E2E 테스트

```
POST /notification-engine/emit-test?force_quiet_hour=true
→ QUIET_HOUR_DELAYED Queue 생성
→ process-queue 호출 (next_retry_at 도래 후)
→ DELIVERED
```

## 핵심

**Quiet Hour는 Queue Delay 정책이다.** Suppression이 아님.
