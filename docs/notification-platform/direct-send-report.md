# Direct Send Report

작성일: 2026-05-16
상태: 조사 완료 (수정 금지)

---

## Backend Direct Send 위치

| 위치 | 함수 | 채널 | Runtime 우회 | 수정 필요 |
|---|---|---|---|---|
| `services/sms_service.py` | MessageMi HTTP call | SMS | ✅ 우회 | ✅ Adapter 전환 |
| `routers/messaging.py` | sms_service 호출 | SMS | ✅ 우회 | ✅ Pipeline 경유 |
| `routers/_messaging_compat.py` | legacy SMS 직접 | SMS | ✅ 우회 | ✅ 제거 또는 전환 |
| `routers/pw_reset.py` | sms_service 호출 | SMS | ✅ 우회 | ⚠️ Auth 특수 채널 |
| `routers/auth.py` | sms_service 호출 | SMS | ✅ 우회 | ⚠️ Auth 특수 채널 |
| `routers/auth_oauth.py` | sms_service 호출 | SMS | ✅ 우회 | ⚠️ Auth 특수 채널 |
| `routers/watch_engine_alert_api.py` | `_send_telegram` test | Telegram | ✅ 우회 | ✅ Pipeline 전환 |
| `routers/notifications.py` | DB 직접 INSERT | In-App | ✅ 우회 | ✅ Pipeline 경유 |
| `services/inbox_notify_svc.py` | DB INSERT | In-App | ✅ 우회 | ✅ Pipeline 경유 |
| `routers/overdue_checker.py` | sms_service 직접 | SMS | ✅ 우회 | ✅ Pipeline 경유 |
| `services/slack_dispatcher.py` | Webhook 직접 | Slack | ✅ 우회 | ⚠️ Phase 2+ |

## 요약

- **총 Direct Send**: 11개
- **즉시 전환 필요 (P1)**: 5개 (messaging, notifications, inbox_notify, overdue_checker, watch_alert_api)
- **Auth 특수 채널 (별도 검토)**: 3개 (pw_reset, auth, auth_oauth)
- **Phase 2+ 검토**: 3개 (_messaging_compat, slack_dispatcher, legacy compat)

## 현재 단계 원칙

수정 금지. 조사만 수행.
