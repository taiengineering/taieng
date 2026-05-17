# Operational Notification Reality

작성일: 2026-05-17
범위: 구조 vs 현실 구분

---

## Pack별 상태

| Pack | 상태 | 설명 |
|---|---|---|
| Auth (6) | 정의만 존재 | wiring 0건, pw_reset frozen |
| Billing (6) | Wiring Ready | 3 wiring 등록, wire_and_emit 미연결 |
| Organization (6) | Wiring Ready | 4 wiring 등록, wire_and_emit 미연결 |
| Workflow (6) | Wiring Ready | 6 wiring 등록, wire_and_emit 미연결 |
| Safety (6) | Wiring Ready | 4 wiring 등록, wire_and_emit 미연결 |
| System (6) | Wiring Ready | 2 wiring 등록, wire_and_emit 미연결 |
| Marketing (3) | 정의만 존재 | Campaign Runtime Phase 2 |

---

## 현실 사용 상태

| 단계 | Pack 수 | 비율 |
|---|---|---|
| 정의만 존재 | 2 (Auth, Marketing) | 29% |
| Wiring Ready | 5 (Billing~System) | 71% |
| 실제 wire_and_emit 호출 | 0 | 0% |
| 실사용 검증 | 0 | 0% |

---

## 핵심

**구조와 현실을 구분해야 한다.**

Wiring Ready ≠ 실제 사용 중.
실제 코드에서 wire_and_emit()을 호출하는 시점부터 실사용.
