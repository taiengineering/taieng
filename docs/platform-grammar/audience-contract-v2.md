# Audience Contract v2

작성일: 2026-05-17
범위: Notification Engine · Audience

---

## 정의

Audience는 **Identity Core 결과 객체**다. Notification이 권한 계산을 하지 않는다.

---

## Audience 객체 필드

| 필드 | 설명 | Phase |
|---|---|---|
| actor_id | 사용자 UUID | 1 |
| tenant_id | 회사/테넌트 ID | 1 |
| audience_key | operator / tenant_admin 등 | 1 |
| name | 사용자 이름 | 1 |
| phone | 전화번호 | 1 |
| email | 이메일 | 1 |
| role_keys | 역할 목록 | 2 |
| visibility_scope | 접근 범위 | 2 |
| preferred_channels | 선호 채널 | 2 |

---

## 표준 Audience Types

| audience_key | 설명 | role_code |
|---|---|---|
| operator | 운영자 | 002, 003 |
| tenant_admin | 테넌트 관리자 | 003 |
| safety_manager | 안전관리자 | 002 |
| company_admin | 회사 관리자 | 003 |
| worker | 작업자 | 004, 005 |
| inspector | 점검자 | 002, 006 |
| site_all | 현장 전체 | 002~006 |
| system_admin | 시스템 관리자 | 001 |
| platform_admin | 플랫폼 관리자 | 001 |

---

## Resolve 흐름

```
audience_key + tenant_id
  → audience_resolver.resolve_audience()
  → [{actor_id, name, phone, ...}]
  → 각 actor에게 알림 전달
```
