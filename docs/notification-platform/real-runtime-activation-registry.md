# Real Runtime Activation Registry

작성일: 2026-05-17
범위: 실제 Runtime 진입 추적

---

## 이벤트 활성화 현황

| 이벤트 | Wiring | wire_and_emit 코드 | 실제 호출 | 상태 |
|---|---|---|---|---|
| payment_failed | ✅ WIRE_PAYMENT_FAILED | ⬜ Cursor 034 대기 | ⬜ | Wiring Ready |
| subscription_activated | ⬜ 미등록 | ⬜ Cursor 034 대기 | ⬜ | 미등록 |
| schedule_overdue | ✅ WIRE_SCHEDULE_OVERDUE | ⬜ Cursor 034 대기 | ⬜ | Wiring Ready |
| weather_work_stop | ✅ WIRE_WEATHER_ALERT | ⬜ Cursor 034 대기 | ⬜ | Wiring Ready |
| approval_requested | ✅ WIRE_APPROVAL_REQUESTED | ⬜ 워크플로우 미구현 | ⬜ | Wiring Ready |
| workflow_stuck | ✅ WIRE_WORKFLOW_STUCK | ⬜ | ⬜ | Wiring Ready |
| accident_reported | ✅ WIRE_ACCIDENT_REPORTED | ⬜ | ⬜ | Wiring Ready |
| violation_detected | ✅ WIRE_VIOLATION_DETECTED | ⬜ | ⬜ | Wiring Ready |

---

## 요약

| 단계 | 건수 |
|---|---|
| Wiring 등록 | 21 |
| Cursor 코드 삽입 대기 | 3 (billing/overdue/weather) |
| 실제 wire_and_emit 호출 중 | 0 |
| 실사용 검증 | 0 |
