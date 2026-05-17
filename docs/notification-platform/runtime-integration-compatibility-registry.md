# Runtime Integration Compatibility Registry

작성일: 2026-05-17
범위: Legacy → Runtime 수렴 현황

---

## Compat 현황

| Legacy | Runtime Integration | 상태 | 비고 |
|---|---|---|---|
| sms_service.py | SMS Adapter | ⚠️ Compat | wire_and_emit 전환 대기 |
| messaging.py | SMS Adapter | ⚠️ Compat | wire_and_emit 전환 대기 |
| fcm.py send-push | Push Adapter v2.0 | ⚠️ Compat | wire_and_emit 전환 대기 |
| overdue_checker.py | wire_and_emit('schedule_overdue') | ✅ **Injected** | dev `d6c44b1e` |
| billing_return | wire_and_emit('payment_failed') | ✅ **Injected** | dev `d229766c` |
| weather.py | wire_and_emit('weather_work_stop') | ✅ **Injected** | dev `d6c44b1e` |
| tbm.py push | 직접 fcm_utils | ❌ Remaining | wire_and_emit 전환 필요 |
| emergency_report.py | 직접 fcm_utils | ❌ Remaining | wire_and_emit 전환 필요 |
| equipment_checkins.py | 직접 fcm_utils | ❌ Remaining | wire_and_emit 전환 필요 |
| safety_reports.py | 직접 fcm_utils | ❌ Remaining | wire_and_emit 전환 필요 |
| workers.py | 직접 fcm_utils | ❌ Remaining | wire_and_emit 전환 필요 |

---

## 수렴률

| 분류 | 건수 | 비율 |
|---|---|---|
| Injected (wire_and_emit) | 3 | 27% |
| Compat (Legacy 유지) | 3 | 27% |
| Remaining (직접 호출) | 5 | 46% |

**Runtime 경유율: 54%** (Injected + Compat)
