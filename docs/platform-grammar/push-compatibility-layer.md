# Push Compatibility Layer

작성일: 2026-05-17
범위: 기존 Push → Notification Runtime 수렴 전략

---

## 전략

기존 Push 시스템(`fcm_utils.send_push`)을 **그대로 사용**하면서
Notification Runtime의 Queue/Retry/Audit/Timeline을 **추가**하는 방향.

---

## 수렴 흐름

```
wire_and_emit(event_type, payload)
  → Wiring Registry lookup
  → Policy resolve (channel=PUSH)
  → Queue Manager → runtime_notification_queue INSERT
  → Worker consume
  → Push Adapter (push.py)
  → audience_resolver → phone 조회
  → _find_token_by_phone() → push_token
  → fcm_utils.send_push(token, title, body, data)
  → FCM → 디바이스
  → delivery result → timeline + policy_audit
```

---

## Compat 계층 역할

| 계층 | 역할 |
|---|---|
| Push Adapter (`push.py`) | Runtime Worker에서 호출 → `fcm_utils.send_push()` 위임 |
| Token Resolver | audience_key → user phone → push_token 조회 |
| Delivery Normalizer | send_push 결과 → (success, error) 표준화 |

---

## 핵심

**새 Push 시스템 구축 불필요.** `push.py`에서 기존 `fcm_utils.send_push()`를 호출하면 끝.
Runtime이 제공하는 Queue/Retry/Audit/Timeline이 자동으로 추가됨.
