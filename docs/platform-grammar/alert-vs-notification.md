# Alert vs Notification Boundary

## Alert
- **정의**: 운영 중요도 승격 판단
- **소유**: Watch Engine (Alert Layer)
- **역할**: "이 이슈가 알림 조건을 만족하는가"
- **저장**: `alert_rule_registry`
- **판단**: threshold + cooldown + dedupe + mute
- **결과**: "알려야 한다" 또는 "억제한다"

**Alert는 판단한다.**

## Notification
- **정의**: 실제 전달 행위
- **소유**: Notification Engine
- **역할**: "어디로, 누구에게, 어떻게 전달하는가"
- **저장**: `alert_history` (delivery result)
- **채널**: Telegram, SMS, Push, Email
- **결과**: 성공/실패/재시도

**Notification은 전달한다.**

## 경계 규칙

```
Watch Engine: "중요하다" (Alert)
     ↓
Identity Core: "누구에게" (Audience)
     ↓
Notification Engine: "전달한다" (Delivery)
```

| | Alert | Notification |
|---|-------|-------------|
| 역할 | 판단 | 전달 |
| 소유 | Watch Engine | Notification Engine |
| 판단 | threshold/cooldown | 없음 |
| Audience | 없음 | Identity에서 소비 |
| 채널 | 없음 | Telegram/SMS/Push |
| 실행 | 없음 | 발송 |
| 기록 | alert_history (판단) | alert_history (결과) |
