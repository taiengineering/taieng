# Real Usage Validation Matrix

작성일: 2026-05-17
범위: Notification Engine · 실사용 검증

---

## 검증 항목

| 검증 항목 | 상태 | 비고 |
|---|---|---|
| 실제 SMS 발송 | ⬜ 미검증 | MessageMi 연동 완료, 실발송 미확인 |
| 실제 Telegram 전달 | ⬜ 미검증 | Bot 설정 완료, 실채널 미확인 |
| 실제 Feed 읽음 | ⬜ 미검증 | UI 완료, 실사용자 읽음 미관찰 |
| 실제 운영자 사용 | ⬜ 미검증 | 알림센터 배포 완료, 실접속 미확인 |
| 실제 Alert Fatigue | ⬜ 미검증 | cooldown/mute 구조 완료, 실패턴 미관찰 |
| 실제 Quiet Hour | ⬜ 미검증 | DELAYED/RESUMED 구현, 실시간대 미확인 |
| 실제 Mobile 사용 | ⬜ 미검증 | site center 완료, 실디바이스 미확인 |
| 실제 Runtime 장애 | ⬜ 미검증 | Retry/DLQ 구현, 실장애 미발생 |
| 실제 Badge 정확성 | ⬜ 미검증 | extractCount 수정, 실데이터 미확인 |
| 실제 Timeline 추적 | ⬜ 미검증 | trace_id 구현, 실추적 미확인 |

---

## 검증률

**0/10 = 0%** — 모두 가설 단계

---

## 검증 우선순위

1. Telegram 실전달 (Bot token + chat_id 설정 후 emit-test)
2. Feed 실읽음 (운영자 로그인 후 알림센터 접속)
3. Badge 정확성 (unread-count API 실응답 확인)
4. SMS 실발송 (MessageMi 잔액 + 수신번호 확인)
