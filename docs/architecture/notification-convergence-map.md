# Notification Convergence Map

작성일: 2026-05-17
범위: Notification Engine · Runtime Convergence

---

## 수렴 구조

```
┌────────────────────────────────────────┐
│          Legacy Direct Send             │
│  sms_service.send_sms()                 │
│  messaging.py 직접 호출                   │
│  overdue_checker SMS                    │
└───────────────┬────────────────────────┘
                │ (전환 중)
┌───────────────▼────────────────────────┐
│        Compatibility Layer               │
│  compat_send_sms()                      │
│  compat_send_in_app()                   │
│  runtime_compat.py                      │
└───────────────┬────────────────────────┘
                │ (목표)
┌───────────────▼────────────────────────┐
│          Event Wiring                    │
│  wire_and_emit(event_type)              │
│  → wiring registry lookup               │
│  → policy resolve                       │
│  → audience resolve                     │
└───────────────┬────────────────────────┘
                │
┌───────────────▼────────────────────────┐
│          Runtime Queue                   │
│  Queue Manager → Worker → Adapter       │
│  Policy Audit → Timeline → Feed          │
└────────────────────────────────────────┘
```

---

## 수렴 진행률

| 계층 | 상태 |
|---|---|
| Runtime Adapter | ✅ 완료 (Telegram/SMS/IN_APP/Push mock) |
| Event Wiring | ✅ 완료 (14 wiring, 8 policy) |
| Compatibility Layer | ✅ 존재 (3 compat 함수) |
| Legacy Direct | ⚠️ 2건 remaining |

**수렴률: 80%**
