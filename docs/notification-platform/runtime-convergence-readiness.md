# Runtime Convergence Readiness

작성일: 2026-05-17
범위: Notification Engine · 수렴 평가

---

## 평가 항목

| 항목 | 점수 | 상태 |
|---|---|---|
| Direct Send 제거율 | 7/10 | 70% Runtime 경유 (compat 포함) |
| Runtime Coverage | 9/10 | 4 adapter + queue + worker + timeline |
| Audience Coverage | 7/10 | 9 audience types, tenant DB resolve |
| Policy Coverage | 9/10 | 8 policies, 14 wirings |
| Compatibility 감소율 | 6/10 | 3 compat 함수 잔존, 2 remaining |
| Wiring API | 9/10 | GET wirings + GET policies + POST test |
| Audience Resolver | 7/10 | Foundation (mock + tenant DB) |

---

## Convergence Score

**54/70 = 77% — B+ 등급**

---

## 전환 로드맵

| 단계 | 내용 | 상태 |
|---|---|---|
| 1 | Runtime Adapter 완성 | ✅ |
| 2 | Event Wiring Registry | ✅ |
| 3 | Policy Registry | ✅ |
| 4 | Audience Resolver Foundation | ✅ |
| 5 | Compat Layer 경유 | ✅ 70% |
| 6 | overdue_checker 전환 | ⬜ 다음 |
| 7 | workers.py 전환 | ⬜ 다음 |
| 8 | Compat Layer 제거 | ⬜ Phase 2 |
| 9 | Identity Core 연동 | ⬜ Phase 2 |
