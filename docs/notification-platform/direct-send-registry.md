# Direct Send Registry

작성일: 2026-05-17
범위: Notification Engine · Legacy 제거 추적

---

## Direct Send 위치 전수 목록

| 위치 | 채널 | 호출 방식 | 상태 |
|---|---|---|---|
| `services/sms_service.py` | SMS | `send_sms()` 직접 | **compatibility** |
| `routers/messaging.py` | SMS | `sms_service.send_sms()` | **compatibility** |
| `routers/overdue_checker.py` | SMS | `sms_service.send_sms()` | **remaining** |
| `routers/pw_reset.py` | SMS | `sms_service.send_sms()` | **frozen** (auth 플로우) |
| `routers/workers.py` | SMS | `sms_service.send_sms()` | **remaining** |
| `services/notification_engine/runtime_compat.py` | SMS/IN_APP | `compat_send_sms()` | **compatibility** |
| `services/notification_engine/compatibility/compat_send.py` | SMS/IN_APP | compatibility layer | **compatibility** |
| `services/notification_engine/adapters/sms.py` | SMS | Runtime Adapter | **migrated** ✅ |
| `services/notification_engine/adapters/telegram.py` | TELEGRAM | Runtime Adapter | **migrated** ✅ |
| `services/notification_engine/adapters/in_app.py` | IN_APP | Runtime Adapter | **migrated** ✅ |

---

## 상태 분류

| 상태 | 설명 | 건수 |
|---|---|---|
| **migrated** | Runtime Adapter로 전환 완료 | 3 |
| **compatibility** | Compat layer 경유 (임시) | 4 |
| **frozen** | 변경 금지 (auth 등 권한 플로우) | 1 |
| **remaining** | 전환 필요 | 2 |
| **blocked** | 외부 의존으로 전환 불가 | 0 |

---

## 제거율

**migrated: 3/10 = 30%**
**compatibility + migrated: 7/10 = 70%** (Runtime 경유)
**remaining: 2/10 = 20%** (전환 필요)
