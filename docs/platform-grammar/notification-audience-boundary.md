# Notification ↔ Audience Boundary

## Alert (알림 규칙)
- **정의**: 어떤 이슈를 언제 알릴지 규칙
- **저장**: `alert_rule_registry`
- **책임**: threshold + cooldown + dedupe 판단

## Notification (알림 전달)
- **정의**: Alert의 실제 전달 행위
- **저장**: `alert_history`
- **책임**: 채널 전달 (Telegram)

## Audience (수신 대상)
- **정의**: 알림을 받아야 할 역할/그룹
- **산출**: `resolve_notification_audience()`
- **기준**: Identity의 notification_level

## 경계 규칙
- Alert ≠ Notification: Alert는 규칙, Notification은 실행
- Audience ≠ Identity: Audience는 이벤트 기반 수신자 해석, Identity는 정적 역할
- Alert 폭탄 방지: threshold + cooldown + dedupe + mute
