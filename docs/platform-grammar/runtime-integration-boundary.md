# Runtime Integration Boundary

작성일: 2026-05-17
범위: 실제 코드 연결 경계

---

## 허용

| 방법 | 설명 |
|---|---|
| `wire_and_emit(event_type, payload)` | 정상 경로 — Wiring → Policy → Emit |
| `compat_send_sms()` | 임시 호환 — 제거 예정 |
| `pipeline.emit_notification()` | Runtime 직접 — E2E 테스트 전용 |
| Policy routing | policy_key 기반 channel/severity 결정 |

---

## 금지

| 방법 | 대안 |
|---|---|
| `send_sms(phone, msg)` 직접 | `wire_and_emit()` |
| `telegram.send(msg)` 직접 | `wire_and_emit()` |
| Template-only (엔진 없이 템플릿만) | Wiring 등록 필수 |
| Queue bypass (Adapter 직접) | Queue → Worker 경유 |
| 하드코딩된 channel/severity | Policy registry 사용 |

---

## 연결 패턴

```python
# ✅ 올바른 패턴
from services.notification_engine.event_wiring import wire_and_emit

async def on_payment_failed(company_id, amount, reason):
    await wire_and_emit(
        event_type='payment_failed',
        payload={'company_id': company_id, 'amount': amount, 'reason': reason,
                 'title': f'결제 실패: {amount}원',
                 'body': f'사유: {reason}'}
    )
```
