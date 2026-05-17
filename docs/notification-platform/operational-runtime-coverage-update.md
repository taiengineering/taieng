# Operational Runtime Coverage Update

작성일: 2026-05-17
범위: Pack별 실제 Runtime 연결 현황

---

## Pack별 Coverage

| Pack | 정의 | Wiring | Real wire_and_emit | 실사용 |
|---|---|---|---|---|
| Auth (6) | ✅ | ❌ 0 | ❌ 0 | ❌ |
| Billing (6) | ✅ | ✅ 3 | ⬜ Cursor 대기 | ❌ |
| Organization (6) | ✅ | ✅ 4 | ❌ 0 | ❌ |
| Workflow (6) | ✅ | ✅ 6 | ⬜ Cursor 대기 | ❌ |
| Safety (6) | ✅ | ✅ 4 | ⬜ Cursor 대기 | ❌ |
| System (6) | ✅ | ✅ 2 | ❌ 0 | ❌ |
| Marketing (3) | ✅ | ❌ 0 | ❌ 0 | ❌ |

---

## 요약

| 단계 | 건수 | 비율 |
|---|---|---|
| 정의 | 43 | 100% |
| Wiring | 21 | 49% |
| Cursor 코드 삽입 대기 | 4 | 9% |
| 실제 wire_and_emit 호출 | 0 | 0% |
| 실사용 검증 | 0 | 0% |

---

## 핵심

**문서 정의 ≠ 실제 Runtime.** Cursor 작업 후 4건 연결 예정.
