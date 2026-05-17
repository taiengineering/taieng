# Delivery Channel Matrix

작성일: 2026-05-17
범위: 채널별 Delivery 상태

---

## Channel Matrix

| 채널 | channel_key | Runtime 상태 | 실제 운영 | 엔진화 준비 | 비고 |
|---|---|---|---|---|---|
| SMS | SMS | ✅ Active | ✅ MessageMi 연동 | ✅ | 건당 비용 발생 |
| Telegram | TELEGRAM | ✅ Active | ⬜ Bot 설정 완료, 실채널 미전달 | ✅ | 무료 |
| Push (FCM) | PUSH | ⬜ Mock | ✅ fcm_utils 존재, 2명 등록 | ✅ 연결만 필요 | 무료 |
| IN_APP | IN_APP | ✅ Active | ✅ notifications 테이블 | ✅ | Feed 표시 |
| Email | EMAIL | ❌ 미구현 | ❌ | ⬜ Phase 2 | SMTP/SES 필요 |
| SITE | SITE | ✅ Active (registry) | ⬜ 미확인 | ⬜ | 웹 알림 |
| KAKAO | KAKAO | ✅ Active (registry) | ❌ 사용 금지 | ❌ | Kakao API 금지 |
| Webhook | — | ❌ 미구현 | ❌ | ⬜ Phase 3 | 외부 연동 |

---

## 운영 가능 채널

| 등급 | 채널 |
|---|---|
| Production Ready | SMS, IN_APP |
| Near-Ready | TELEGRAM (Bot 설정 완료), PUSH (FCM 존재) |
| Phase 2 | EMAIL |
| 금지 | KAKAO |
