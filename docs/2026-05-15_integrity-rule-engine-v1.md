# Integrity Rule Engine v1 — TASK 06

## 구조

```
watch_engine/integrity/
  __init__.py
  evaluator.py              ← evaluate_recent_events() 진입점
  rules/
    __init__.py
    field_mismatch.py       ← submit vs read 값 비교
    sequence_violation.py   ← step_order 연속성 검증
    stuck_detected.py       ← flow 중단 탐지
    timeout_exceeded.py     ← step timeout 초과 탐지
```

## 검증 결과 (8건 integrity event 생성)

| Rule | trace_id | 결과 |
|------|----------|------|
| field_mismatch | procreg_test02mismatch | KCSC→kcsc 검출 |
| sequence_violation | login_test02def | session_issued 누락 |
| sequence_violation | procreg_stuck01 | save_db, read_result 누락 |
| stuck_detected | procreg_stuck01 | step 1/3, 586s > 60s |
| stuck_detected | login_test02def | step 1/2, 544s > 30s |
| timeout_exceeded | login_timeout01 validate_auth | 15000ms > 5000ms |
| timeout_exceeded | login_timeout01 session_issued | 15000ms > 3000ms |
| timeout_exceeded | procreg_stuck01 validate_input | 60000ms > 5000ms |

Dedupe: (trace_id, event_type, step_key) 기준 중복 0건.