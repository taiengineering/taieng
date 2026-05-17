# Notification Observation Log

작성일: 2026-05-17
범위: Notification Engine · 운영 관찰 기록

---

## 목적

실제 운영 패턴을 **기록**한다. 분석보다 기록 중심.

---

## 관찰 항목

| 항목 | 관찰 포인트 | 기록 방법 |
|---|---|---|
| 운영자 행동 | 알림센터 접속 빈도, 체류 시간 | GA4 이벤트 |
| Unread 패턴 | 미읽음 누적 속도, 최대 누적 수 | runtime_notification_metrics |
| Mute 패턴 | mute 설정 빈도, 대상 source_type | notification_preferences |
| Quiet Hour 패턴 | quiet hour 설정 시간대, bypass 빈도 | policy_audit |
| Ignored Notification | 읽지 않고 24시간 경과한 알림 비율 | notifications.is_read + created_at |
| Delayed Response | 읽음까지 평균 시간 | notifications.read_at - created_at |
| Dismiss 패턴 | 팝업 닫기 빈도 vs 클릭 빈도 | notification.js 이벤트 (Phase 2) |

---

## 기록 양식

```
[날짜] [관찰자]
- 관찰 내용
- 수치 (있으면)
- 특이사항
```

---

## 첫 번째 관찰 (대기 중)

실사용 시작 후 기록 예정.
