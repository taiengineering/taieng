# Notification Routing Governance

작성일: 2026-05-17
범위: Notification Engine · Routing 절차

---

## 새 알림 추가 절차

1. **event_type 정의** — `notification_event_registry`에 등록
2. **wiring 등록** — `notification_event_wiring_registry`에 event → policy → audience 연결
3. **audience 확인** — `audience_resolver.py`에서 resolve 가능한지 확인
4. **policy 확인** — `notification_policy_registry`에 적합한 policy 존재 확인
5. **발송 테스트** — `POST /notification-engine/wirings/test` 로 검증

---

## 금지 패턴

```python
# ❌ 금지 — direct send
from services.sms_service import send_sms
send_sms(phone, message)

# ❌ 금지 — adapter 직접 호출
from services.notification_engine.adapters.telegram import send
send(message)

# ✅ 올바른 방법 — event wiring
from services.notification_engine.event_wiring import wire_and_emit
await wire_and_emit(event_type="schedule_overdue", payload={...})
```

---

## 예외

- `pw_reset.py` SMS: auth 플로우 (frozen — 전환 대상 아님)
- E2E 테스트 `emit-test`: wiring 없이 직접 발송 허용
