# Notification Runtime Maturity

작성일: 2026-05-16

---

## Maturity Levels

| Level | 의미 | 상태 |
|---|---|---|
| **Level 1** | Direct Send | ✅ 통과 (기존 상태) |
| **Level 2** | Queue Runtime | ✅ 통과 (Pipeline→Queue→Worker→Adapter) |
| **Level 3** | Retry / DLQ | ✅ 통과 (Exponential backoff + Deadletter) |
| **Level 4** | Feed Surface | ✅ 통과 (Inbox API + Unified Feed) |
| **Level 5** | Preference Enforcement | ✅ 통과 (Mute/Disabled/QH/CRITICAL) |
| **Level 6** | Delayed Delivery Runtime | ✅ 통과 (Quiet Hour→Resume→Delivered) |
| **Level 7** | Operational Communication Platform | ⚠️ 부분 (Cron 자동화 + Frontend UI 필요) |

## 현재 위치

```
███████████████████████████░░░  Level 6.5 / 7
```

## Level 7 달성 요건

1. Worker Cron 자동화 (1분 주기)
2. Metrics Cron 자동화 (10분 주기)
3. Frontend 알림 센터 UI
4. Push/Email Adapter (필수는 아님)
5. Permission Layer (필수는 아님)

## Phase 1 성과 요약

- DB 테이블: 11개 신규 + 3개 기존 확장
- 서비스 파일: 20+ (services/notification_engine/)
- 라우터: 5개 (engine, inbox, preference, workflow_alert, workflow_engine)
- 문서: 25+ (platform-grammar + notification-platform)
- Adapter: 3개 (Telegram, SMS, In-App)
- E2E 시나리오: 7개 (NORMAL, MUTE, QUIET_HOUR, CRITICAL_BYPASS, RETRY, FAILED, DLQ)
