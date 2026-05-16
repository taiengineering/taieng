# Feed Consistency Rules

작성일: 2026-05-16

---

## 규칙

| 조건 | 기대 상태 | 위반 시 Gap 유형 |
|---|---|---|
| IN_APP DELIVERED | notifications에 항목 존재 | FEED_GAP |
| READ 상태 | notifications.is_read=true | FEED_GAP |
| SUPPRESSED | Queue 미생성 + notifications 미생성 | 정상 |
| TELEGRAM/SMS DELIVERED | notifications 미생성 | 정상 (외부 채널) |
| DEADLETTER | notifications 미생성 | 정상 (발송 실패) |

## 핵심

- Feed는 IN_APP 채널 전용
- 외부 채널(Telegram/SMS)은 Feed 대상 아님
- SUPPRESSED는 Queue/Feed 모두 없는 것이 정상
