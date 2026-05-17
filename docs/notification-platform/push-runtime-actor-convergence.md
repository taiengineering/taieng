# Push Runtime Actor Convergence

작성일: 2026-05-17
범위: Audience Resolver ↔ Push Token 연결

---

## 현재 구조

```
기존 Push: phone → _find_token_by_phone() → push_token
Notification Engine: audience_key → audience_resolver → actor list
```

---

## 연결 방법

```
wire_and_emit(event_type, payload={tenant_id: ...})
  → audience_resolver.resolve_audience(audience_key, tenant_id)
  → [{actor_id, phone, ...}]
  → 각 actor에 대해:
    → _find_token_by_phone(phone)
    → push_token 확인
    → context = {fcm_token: push_token, title, body}
    → Push Adapter send(message, context)
```

---

## 매핑 테이블

| Notification Engine | Push 시스템 | 연결 방법 |
|---|---|---|
| audience_key | — | audience_resolver 조회 |
| actor_id (user UUID) | users.id | users.push_token 직접 조회 |
| phone | worker_registry/users | `_find_token_by_phone()` |
| push_token | FCM 디바이스 토큰 | send_push() 파라미터 |

---

## 미해결

1. **user_id 기반 조회 미구현** — 현재 phone 기반만. user_id → push_token 직접 조회 추가 필요.
2. **다중 디바이스 미지원** — 1 user = 1 push_token. 복수 디바이스 시 별도 테이블 필요 (Phase 3).
3. **Token 유효성 미검증** — expired token 감지/정리 로직 없음.
