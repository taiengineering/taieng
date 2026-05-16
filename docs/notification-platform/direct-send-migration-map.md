# Direct Send Migration Map

작성일: 2026-05-16
상태: Inventory + Migration Path 정의

---

## Migration Map

| Legacy 위치 | 현재 방식 | Runtime 흡수 방식 | 현재 상태 | 제거 가능 |
|---|---|---|---|---|
| `services/sms_service.py` | MessageMi HTTP 직접 | `adapters/sms.py` 전환 | ✅ Adapter 구현 완료 | Phase 2 |
| `services/inbox_notify_svc.py` | DB INSERT 직접 | `adapters/in_app.py` 전환 | ✅ Adapter 구현 완료 | Phase 2 |
| `routers/overdue_checker.py` | Edge Function SMS+FCM+DB 직접 | `compat_send_sms()` 경유 | ⚠️ Cursor 작업 필요 | Phase 2 |
| `routers/watch_engine_alert_api.py` | `_send_telegram` test endpoint | Pipeline 경유 (완료) | ✅ engine.py는 Pipeline 전환 완료 | Phase 2 |
| `routers/notifications.py` | Legacy notification CRUD | Freeze (\uc2e0\uaddc \uc0ac\uc6a9 \uae08\uc9c0) | ✅ Freeze 선\uc5b8 | \uc0ad\uc81c \uae08\uc9c0 |
| `routers/messaging.py` | sms_service 경\uc720 SMS | `compat_send_sms()` | ⚠\ufe0f Cursor \uc791\uc5c5 \ud544\uc694 | Phase 2 |
| `routers/_messaging_compat.py` | Legacy SMS compat | \uc81c\uac70 \ub610\ub294 \uc804\ud658 | ⚠\ufe0f Phase 3 | Phase 3 |
| `routers/pw_reset.py` | Auth SMS | Auth \ubcc4\ub3c4 \uac80\ud1a0 | \u23f8 \ubcf4\ub958 (Auth \ud2b9\uc218) | N/A |
| `routers/auth.py` / `auth_oauth.py` | Auth SMS | Auth \ubcc4\ub3c4 \uac80\ud1a0 | \u23f8 \ubcf4\ub958 (Auth \ud2b9\uc218) | N/A |
| `services/slack_dispatcher.py` | Webhook \uc9c1\uc811 | Slack Adapter (Phase 2+) | \u274c \ubbf8\uad6c\ud604 | Phase 3 |

---

## overdue_checker.py \ud2b9\uc774 \uc0ac\ud56d

\uc774 \ud30c\uc77c\uc740 19KB\ub85c Cursor \uc791\uc5c5 \ud544\uc694.

### \ud604\uc7ac Direct Send 3\uac1c:

1. `_send_sms()` \u2014 Supabase Edge Function (`send-sms`) \uacbd\uc720
2. `_send_fcm()` \u2014 Supabase Edge Function (`send-push`) \uacbd\uc720  
3. `_write_notification()` \u2014 `notifications` \ud14c\uc774\ube14 \uc9c1\uc811 INSERT

### \uc804\ud658 \uacc4\ud68d:

1. `_send_sms()` \u2192 `compat_send_sms()` \uacbd\uc720 (phone \ud30c\ub77c\ubbf8\ud130 \uc804\ub2ec)
2. `_write_notification()` \u2192 `compat_send_in_app()` \uacbd\uc720
3. `_send_fcm()` \u2192 Phase 2 Push Adapter \uad6c\ud604 \ud6c4 \uc804\ud658

### \uc8fc\uc758:

- Edge Function SMS\uc640 MessageMi SMS\ub294 \ub2e4\ub978 \uacbd\ub85c (\ud1b5\ud569 \uac80\ud1a0 \ud544\uc694)
- FCM\uc740 Push Adapter \ubbf8\uad6c\ud604 \uc0c1\ud0dc\ub85c \ud604\uc7ac \uc804\ud658 \ubd88\uac00
- \uc5d0\uc2a4\ucf08\ub808\uc774\uc158 \ub808\ubca8\ubcc4 \ub2e4\ub978 \uc218\uc2e0\uc790 (\uc791\uc5c5\uc790/\uad00\ub9ac\uc790) \u2192 Recipient Resolution \ud655\uc7a5 \ud544\uc694

---

## \uc6d0\uce59

- Legacy \uc0ad\uc81c \uae08\uc9c0
- \uc810\uc9c4\uc801 Runtime \uacbd\uc720 \uc720\ub3c4
- Auth SMS\ub294 \ubcc4\ub3c4 \ub3c4\uba54\uc778
