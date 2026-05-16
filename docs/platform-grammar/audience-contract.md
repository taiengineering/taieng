# Audience Contract

작성일: 2026-05-16

---

## Audience 최소 구조

```json
{
  "actor_id": "user_uuid",
  "tenant_id": "company_uuid",
  "audience_key": "operator | tenant_admin | tenant_user",
  "role_keys": ["001", "002"],
  "visibility_scope": ["factory_uuid_1", "factory_uuid_2"],
  "channel_preferences": [
    {"channel_key": "TELEGRAM", "enabled": true},
    {"channel_key": "SMS", "enabled": true, "mute_enabled": false}
  ]
}
```

## 핵심 원칙

**Audience는 Identity Core 결과 객체다.** Notification Engine이 생성하지 않는다.

## 관계

```
Identity Core
  → Audience Resolution (role, tenant, visibility)
  → Audience Contract (결과 객체)
  → Notification Engine (소비)
  → Delivery
```

## 현재 단계

Identity Core 미구현. Notification Engine은 `recipient_source` (OPERATOR/OWNER/TRIGGERED_BY) 기반 단순 resolution 사용.
