# Real Runtime Coverage Matrix

작성일: 2026-05-17
범위: Pack별 실제 연결 현황

---

## Coverage

| Pack | 정의 | Wiring | 실제 호출 | 실사용 |
|---|---|---|---|---|
| Auth (6) | ✅ 6 | ❌ 0 | ❌ 0 | ❌ |
| Billing (6) | ✅ 6 | ✅ 3 (payment_failed, subscription_expiring, subscription_expired) | ❌ 0 | ❌ |
| Organization (6) | ✅ 6 | ✅ 4 (approval_requested/completed, member_invited/joined) | ❌ 0 | ❌ |
| Workflow (6) | ✅ 6 | ✅ 6 (schedule_due/overdue, inspection_completed/failed, workflow_stuck/resumed) | ❌ 0 | ❌ |
| Safety (6) | ✅ 6 | ✅ 4 (weather_work_stop, education_due, accident_reported, violation_detected) | ❌ 0 | ❌ |
| System (6) | ✅ 6 | ✅ 2 (queue_deadletter, cron_failure) | ❌ 0 | ❌ |
| Marketing (3) | ✅ 3 | ❌ 0 | ❌ 0 | ❌ |

---

## 요약

| 단계 | 건수 | 비율 |
|---|---|---|
| 정의만 존재 | 43 | 100% |
| Wiring 등록 | 21 | 49% |
| 실제 wire_and_emit 호출 | 0 | 0% |
| 실사용 검증 | 0 | 0% |

---

## 공백

- Auth Pack: wiring 0건 (pw_reset frozen, 나머지 Phase 2)
- Marketing Pack: wiring 0건 (Campaign Runtime Phase 2)
- 전체 wire_and_emit 실제 호출: 0건 (코드 연결 필요)
