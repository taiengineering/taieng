# Push Actor Mapping Analysis

작성일: 2026-05-17
범위: Push가 누구에게 가는가

---

## 현재 구조

```
Push 대상 식별:
  전화번호 (phone) → push_token 조회

대상 테이블:
  1. worker_registry (phone → push_token)
  2. users (phone → push_token) fallback
```

---

## Actor 매핑

| 식별자 | 테이블 | Push 연결 |
|---|---|---|
| user_id (UUID) | users | users.push_token |
| worker_id (UUID) | worker_registry | worker_registry.push_token |
| phone (전화번호) | users + worker_registry | `_find_token_by_phone()` |
| company_id | users.company_id | 간접 (회사 → 사용자 → push_token) |
| factory_id | 시설 → 사용자 | 미구현 |

---

## Notification Engine Audience 연결

| audience_key | Push 연결 가능성 |
|---|---|
| operator | users.push_token (role_code 002/003) |
| safety_manager | users.push_token (role_code 002) |
| worker | worker_registry.push_token |
| company_admin | users.push_token (role_code 003) |
| tenant_admin | users.push_token (role_code 003) |
| site_all | 전체 push_token 조회 필요 |
| system_admin | users.push_token (role_code 001) |

---

## 핵심

현재 Push는 **전화번호 기반**으로 동작. Notification Engine은 **audience_key 기반**.
연결 시 audience_resolver에서 phone 조회 후 push_token 확인 필요.
