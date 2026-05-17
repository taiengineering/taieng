# Direct Send Reduction Report

작성일: 2026-05-17
범위: Legacy direct send → Runtime 전환 진척

---

## 전환 현황

| 자산 | 이전 | 현재 | 변화 |
|---|---|---|---|
| adapters/telegram.py | Direct API | Runtime Adapter | ✅ migrated |
| adapters/sms.py | Direct API | Runtime Adapter | ✅ migrated |
| adapters/in_app.py | Direct INSERT | Runtime Adapter | ✅ migrated |
| adapters/push.py | 없음 | Mock Adapter | ✅ 신규 |
| sms_service.py | Direct send | Compat layer 경유 | ⚠️ compatibility |
| messaging.py | Direct send | Compat layer 경유 | ⚠️ compatibility |
| runtime_compat.py | 없음 | Compat bridge | ⚠️ compatibility |
| compat_send.py | 없음 | Compat bridge | ⚠️ compatibility |
| overdue_checker.py | Direct send | Direct send | ❌ remaining |
| workers.py | Direct send | Direct send | ❌ remaining |
| pw_reset.py | Direct send | Direct send | ❄️ frozen |

---

## 진척률

| 단계 | 건수 | 비율 |
|---|---|---|
| migrated (Runtime Adapter) | 4 | 36% |
| compatibility (Compat 경유) | 4 | 36% |
| remaining (Direct) | 2 | 18% |
| frozen (Auth) | 1 | 9% |

**Runtime 경유율: 72%** (migrated + compatibility)
**완전 제거율: 36%** (migrated만)

---

## 다음 단계

1. overdue_checker.py → `wire_and_emit('schedule_overdue')` 전환
2. workers.py → `wire_and_emit()` 전환
3. Compat layer → wire_and_emit 전환 후 제거
