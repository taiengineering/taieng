# Existing Notification Endpoint Registry

작성일: 2026-05-17
범위: 실제 외부 전달 경로

---

## 엔드포인트

| 채널 | 엔드포인트 | 상태 | 위치 |
|---|---|---|---|
| SMS | MessageMi API | ✅ Active | `services/sms_service.py` |
| Telegram | Telegram Bot API | ✅ Active | `adapters/telegram.py` |
| Push (FCM) | Firebase Cloud Messaging | ✅ Active | `utils/fcm_utils.py` |
| IN_APP | Supabase notifications INSERT | ✅ Active | `adapters/in_app.py` |
| Email | ❌ 미구현 | Phase 2 | — |
| Kakao | ❌ 금지 | 사용 금지 | — |

---

## API 엔드포인트

| API | 경로 | 역할 |
|---|---|---|
| POST /workers/fcm-token | FCM 토큰 등록 | Push |
| POST /workers/send-push | 전화번호 push 발송 | Push |
| POST /workers/push-test | Push 테스트 | Push |
| POST /notification-engine/emit-test | Runtime 전달 테스트 | 전체 |
| POST /notification-engine/wirings/test | Wiring 테스트 | 전체 |
| POST /send-sms | SMS 발송 | SMS |
| GET /notification-inbox/feed | Feed 조회 | IN_APP |

---

## 환경변수

| 변수 | 용도 |
|---|---|
| TELEGRAM_BOT_TOKEN | Telegram Bot |
| TELEGRAM_CHAT_ID | Telegram 채널 |
| MESSAGEMI_API_KEY | SMS API |
| GOOGLE_APPLICATION_CREDENTIALS | Firebase (FCM) |
