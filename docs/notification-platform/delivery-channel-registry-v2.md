# Delivery Channel Registry v2

작성일: 2026-05-17
범위: 전체 채널 상태

---

## Channel Registry (9채널)

| Channel | channel_key | 상태 | Adapter | enabled | 비고 |
|---|---|---|---|---|---|
| In-App Feed | IN_APP | **operational** | in_app.py | ✅ | notifications INSERT |
| Push (FCM) | PUSH | **compat** | push.py v2.0 | ✅ | fcm_utils 실연결 |
| SMS | SMS | **compat** | sms.py | ✅ | MessageMi |
| Telegram | TELEGRAM | **partial** | telegram.py | ✅ | Bot 설정 완료, 실채널 대기 |
| Gmail (SMTP) | EMAIL_GMAIL | **phase2** | gmail.py (예정) | ❌ | SMTP adapter 구현 예정 |
| 알림톡 | ALIMTALK | **phase2** | alimtalk.py (예정) | ❌ | 카카오 비즈 채널 |
| Slack | SLACK | **phase2** | slack.py (예정) | ❌ | Webhook 기반 |
| Email (Legacy) | EMAIL | **deprecated** | — | ❌ | EMAIL_GMAIL으로 대체 |
| Webhook | WEBHOOK | **phase3** | — | ❌ | 외부 연동 |

---

## 요약

| 상태 | 건수 |
|---|---|
| operational | 1 (IN_APP) |
| compat | 2 (PUSH, SMS) |
| partial | 1 (TELEGRAM) |
| phase2 | 3 (EMAIL_GMAIL, ALIMTALK, SLACK) |
| deprecated | 1 (EMAIL) |
| phase3 | 1 (WEBHOOK) |
