# Existing Push Call Registry

작성일: 2026-05-17
범위: Push 호출 7개 전수 분류

---

## 호출 전수 목록

| 위치 | 이벤트 | 직접 발송 | Runtime 전환 가능 | 상태 |
|---|---|---|---|---|
| `routers/fcm.py` send-push | 전화번호 push | ✅ 직접 | ✅ | **compatibility** |
| `routers/fcm.py` push-test | 토큰 테스트 | ✅ 직접 | ❌ (테스트 전용) | **frozen** |
| `routers/fcm.py` fcm-token | 토큰 등록 | — (발송 아님) | — | **유지** |
| `routers/tbm.py` | TBM 참석 push | ✅ 직접 | ✅ `wire_and_emit('tbm_attendance')` | **remaining** |
| `routers/overdue_checker.py` | 미이행 push | ✅ 직접 | ✅ `wire_and_emit('schedule_overdue')` | **remaining** |
| `routers/emergency_report.py` | 긴급 push | ✅ 직접 | ✅ `wire_and_emit('accident_reported')` | **remaining** |
| `routers/workers.py` | 작업자 push | ✅ 직접 | ✅ `wire_and_emit()` | **remaining** |
| `routers/equipment_checkins.py` | 설비 체크인 push | ✅ 직접 | ✅ `wire_and_emit('equipment_checkin')` | **remaining** |
| `routers/safety_reports.py` | 안전보고 push | ✅ 직접 | ✅ `wire_and_emit('safety_report')` | **remaining** |

---

## 분류 요약

| 상태 | 건수 |
|---|---|
| 유지 (토큰 등록) | 1 |
| frozen (테스트 전용) | 1 |
| compatibility (API 경유) | 1 |
| remaining (전환 필요) | 6 |

---

## 전환 우선순위

1. `overdue_checker.py` — 기존 SMS+Push 이중 발송, wire_and_emit으로 통합
2. `tbm.py` — TBM 참석 push, 빈도 높음
3. `emergency_report.py` — 긴급 push, CRITICAL
4. `equipment_checkins.py` — 설비 체크인
5. `safety_reports.py` — 안전보고
6. `workers.py` — 작업자 일반
