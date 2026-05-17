# Digest Runtime Readiness

작성일: 2026-05-17
범위: Notification Engine · Digest 평가

---

## 평가 항목

| 항목 | 점수 | 상태 |
|---|---|---|
| Digest Policy Registry | 9/10 | 5 policies seeded, DB 완료 |
| Digest Queue | 9/10 | 테이블 + 인덱스 완료 |
| Digest Runtime Service | 8/10 | lookup + append + check_and_append |
| Digest API | 9/10 | GET policies + GET candidates + POST test |
| Duplicate Suppression | 6/10 | grouped_key 기반 (시간창 검사 미구현) |
| Density Governance | 8/10 | 4단계 수준 정의 |
| Runtime Compatibility | 9/10 | shadow mode, emit 차단 없음 |
| Wiring → Digest 연결 | 7/10 | event_wiring.wire_and_emit()에서 check_and_append() 호출 가능 |

---

## Digest Readiness Score

**65/80 = 81% — A- 등급**

---

## 미완료

1. **시간창 기반 중복 억제** — window_minutes 내 동일 grouped_key 중복 검사
2. **실제 Digest 전달** — shadow mode 해제 후 묶음 전달
3. **Digest Summary 생성** — mode='summary' 시 요약 본문 생성
4. **wire_and_emit 내부 연결** — digest_enabled wiring에서 자동 호출
