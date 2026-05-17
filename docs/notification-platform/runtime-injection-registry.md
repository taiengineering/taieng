# Runtime Injection Registry

작성일: 2026-05-17
범위: 실제 Runtime 진입 현황

---

## 이벤트 Runtime 연결 현황

| 이벤트 | 기존 방식 | wire_and_emit 연결 | 코드 삽입 | 상태 |
|---|---|---|---|---|
| payment_success | 없음 | WIRE_PAYMENT_SUCCESS | ⬜ Cursor 대기 | Wiring Ready |
| payment_failed | 없음 | WIRE_PAYMENT_FAILED | ⬜ Cursor 대기 | Wiring Ready |
| subscription_activated | 없음 | — | ⬜ wiring 추가 필요 | 미등록 |
| schedule_overdue | SMS + push 직접 | WIRE_SCHEDULE_OVERDUE | ⬜ Cursor 대기 | Wiring Ready |
| weather_work_stop | SMS + push 직접 | WIRE_WEATHER_ALERT | ⬜ Cursor 대기 | Wiring Ready |
| approval_requested | 없음 | WIRE_APPROVAL_REQUESTED | ⬜ Cursor 대기 | Wiring Ready |
| workflow_stuck | 없음 | WIRE_WORKFLOW_STUCK | ⬜ | Wiring Ready |
| accident_reported | push 직접 | WIRE_ACCIDENT_REPORTED | ⬜ | Wiring Ready |
| tbm_attendance | push 직접 | — | ⬜ wiring 추가 필요 | 미등록 |

---

## 요약

| 단계 | 건수 |
|---|---|
| Wiring Ready (DB 등록) | 21 |
| Cursor 코드 삽입 대기 | 4 (billing/overdue/weather/approval) |
| 실제 wire_and_emit 호출 중 | 0 |

---

## 전환 전략

1. **Cursor로 코드 삽입** — 대형 파일 (payment_billing 52KB, overdue_checker 15KB+)
2. **try/except 감싸기** — wire_and_emit 실패가 기존 로직 막지 않음
3. **기존 로직 유지** — compat 공존 (wire_and_emit 추가만, 제거 없음)
