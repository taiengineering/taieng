# Runtime Injection Registry

작성일: 2026-05-17
범위: 실제 Runtime 진입 현황
최종 업데이트: 2026-05-17 (Cursor 033 `d6c44b1e` + 034 `d229766c` 반영)

---

## 이벤트 Runtime 연결 현황

| 이벤트 | 기존 방식 | wire_and_emit 연결 | 코드 삽입 | 상태 |
|---|---|---|---|---|
| subscription_activated | 없음 | WIRE 미등록 | ✅ `d229766c` billing_return 성공 시 | **코드 삽입 완료** (dev) |
| payment_failed | 없음 | WIRE_PAYMENT_FAILED | ✅ `d229766c` _fail_subscription_by_oid 중앙화 | **코드 삽입 완료** (dev) |
| schedule_overdue | SMS + push 직접 | WIRE_SCHEDULE_OVERDUE | ✅ `d6c44b1e` overdue_checker.py | **코드 삽입 완료** (dev) |
| weather_work_stop | SMS + push 직접 | WIRE_WEATHER_ALERT | ✅ `d6c44b1e` weather.py (/work-stoppage, /now, /alert) | **코드 삽입 완료** (dev) |
| approval_requested | 없음 | WIRE_APPROVAL_REQUESTED | ⬜ 워크플로우 미구현 | Wiring Ready |
| workflow_stuck | 없음 | WIRE_WORKFLOW_STUCK | ⬜ | Wiring Ready |
| accident_reported | push 직접 | WIRE_ACCIDENT_REPORTED | ⬜ | Wiring Ready |
| tbm_attendance | push 직접 | — | ⬜ wiring 추가 필요 | 미등록 |

---

## 요약

| 단계 | 건수 |
|---|---|
| Wiring Ready (DB 등록) | 21 |
| **코드 삽입 완료 (dev)** | **4** (billing/overdue/weather) |
| 실제 운영 (main 배포) | 0 (dev→main merge 필요) |

---

## Cursor 033+034 변경 내역

| 커밋 | 파일 | 내용 |
|---|---|---|
| `d6c44b1e` (033) | payment_billing.py, overdue_checker.py, weather.py | wire_and_emit 삽입 (billing/overdue/weather) |
| `d229766c` (034) | payment_billing.py | _fail_subscription_by_oid 중앙화, subscription_activated 추가 |

---

## 규칙

- Legacy SMS/push 유지 (제거 없음)
- try/except on all wiring paths
- wire_and_emit import inside helpers
- dev branch only (main merge 별도)
