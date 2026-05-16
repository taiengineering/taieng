# Notification Channel Architecture

작성일: 2026-05-16

---

## 구조

```
Notification Runtime
    ↓
Delivery Policy (cooldown, dedupe, mute, quiet_hour)
    ↓
Queue (runtime_notification_queue)
    ↓
Adapter (Channel-specific)
    ↓
External Channel
```

## 채널 정의

| channel_key | 상태 | Adapter | 설명 |
|---|---|---|---|
| `TELEGRAM` | ✅ 구현 완료 | `adapters/telegram.py` | Watch Engine 운영 알림 |
| `SMS` | ⚠️ Direct Send | 미구현 | MessageMi 경유, Runtime 미연동 |
| `IN_APP` | ⚠️ Direct Send | 미구현 | DB INSERT 직접, Runtime 미연동 |
| `EMAIL` | ❌ 미구현 | - | 계획만 |
| `PUSH` | ❌ 미구현 | - | 계획만 |
| `WEBHOOK` | ⚠️ Direct Send | 미구현 | Slack webhook 직접 |
| `DASHBOARD_FEED` | ⚠️ Direct Render | 미구현 | Frontend JS 직접 |

## 핵심 원칙

**채널 추가는 Adapter 추가로만 수행한다.**

Pipeline 로직 수정 금지. Worker는 `CHANNEL_ADAPTERS` dict에서 adapter_fn을 조회하는 구조.

## 다음 단계 (Phase 2+)

1. SMS Adapter 구현 (MessageMi → `adapters/sms.py`)
2. In-App Adapter 구현 (DB INSERT → `adapters/in_app.py`)
3. Email Adapter (SES/SMTP)
4. Push Adapter (FCM)
