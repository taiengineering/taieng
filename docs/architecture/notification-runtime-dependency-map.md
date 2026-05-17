# Notification Runtime Dependency Map

작성일: 2026-05-17
범위: Notification Engine · 의존 구조

---

## 의존 구조

```
┌─────────────────────────────────────────┐
│              Supabase (Seoul)            │
│  ├─ notifications                       │
│  ├─ runtime_notification_queue          │
│  ├─ runtime_notification_timeline       │
│  ├─ runtime_notification_policy_audit   │
│  ├─ runtime_notification_metrics        │
│  ├─ runtime_notification_deadletter     │
│  ├─ notification_channel_registry       │
│  ├─ notification_recipient_rules        │
│  ├─ notification_preferences            │
│  └─ notification_event_registry         │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│          FastAPI (Railway SG)            │
│  ├─ Event Intake                        │
│  ├─ Recipient Resolver                  │
│  ├─ Queue Manager                       │
│  ├─ Worker                              │
│  ├─ Pipeline                            │
│  ├─ Feed Query                          │
│  ├─ Timeline Service                    │
│  ├─ Preference Service                  │
│  ├─ Metrics Aggregator                  │
│  └─ Scheduler (cron_job_master)         │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│           External Services              │
│  ├─ Telegram Bot API                    │
│  ├─ MessageMi (SMS)                     │
│  └─ FCM (Phase 2)                       │
└─────────────────────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│          Frontend (Cloudflare Pages)     │
│  ├─ notification.js (벨 팝업)           │
│  ├─ notification-center.html (센터)     │
│  └─ menu-tadmin.js / menu-nav.js       │
└─────────────────────────────────────────┘
```

---

## 운영 영향도

| 컴포넌트 장애 | 영향 | 심각도 |
|---|---|---|
| Supabase 다운 | 전체 알림 중단 | CRITICAL |
| Railway 다운 | Queue/Worker 중단 | CRITICAL |
| Telegram API 장애 | Telegram 채널만 실패 | MEDIUM |
| MessageMi 장애 | SMS 채널만 실패 | MEDIUM |
| Cloudflare 장애 | UX만 중단, Runtime 정상 | LOW |
