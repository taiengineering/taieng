# Permission System Interface — 기존 권한체계 연결

## 아키텍처

```
[기존 Auth]           [Identity Core Interface]       [Watch Engine]
                                                       
users.role_code  ──→  identity_role_mapping  ──→  actor_type
users.factory_id ──→  tenant_id 도출         ──→  visibility_scope
users.company_id ──→                         ──→  governance_level
                                              ──→  notification_level
roles            ──→  (참조만)                     
role_permissions ──→  (기존 유지)                   
role_menu_perm   ──→  get_menu_visibility()        
role_data_scope  ──→  visibility_scope 매핑         
```

**핵심: 기존 auth/token 구조 변경 없음. 인터페이스만 표준화.**

---

## 기존 role_code → Identity Core 매핑

| role_code | 역할명 | Identity Core | actor_type | visibility | governance |
|:---------:|--------|--------------|------------|-----------|-----------|
| 001 | 최고관리자 | platform_admin | platform_admin | platform | admin |
| 002 | 관리자 | tenant_admin | tenant_admin | tenant | operator |
| 010 | 대표 | tenant_admin | tenant_admin | tenant | operator |
| 011 | 안전보건관리책임자 | tenant_admin | tenant_admin | tenant | operator |
| 012 | 안전관리자 | tenant_operator | tenant_user | tenant | operator |
| 013 | 관리감독자 | tenant_operator | tenant_user | tenant | viewer |
| 016 | 보건관리자 | tenant_operator | tenant_user | tenant | operator |
| 008 | 승인자 | tenant_operator | tenant_user | tenant | operator |
| 014 | 작업자 | tenant_user | tenant_user | self | viewer |
| 015 | 산업보건의 | tenant_user | tenant_user | self | viewer |
| 007 | 점검자 | tenant_user | tenant_user | self | viewer |
| 020 | 하도급대표 | partner_user | partner_user | self | viewer |
| 021 | 하도급안전관리자 | partner_user | partner_user | self | viewer |
| 022 | 하도급직원 | partner_user | partner_user | self | viewer |

## 기존 scope_type → visibility_scope 매핑

| scope_type (기존) | visibility_scope (Identity Core) |
|:---------:|:----------:|
| ALL | platform |
| COMPANY | tenant |
| FACTORY | tenant |
| TEAM | team |
| ASSIGNED | self |

## Actor Context Resolution 흐름

```
1. actor_id 입력 (UUID 또는 "founder")
2. "founder"/"admin"/"system" → 즉시 platform_admin
3. users 테이블 조회 → role_code, factory_id, company_id
4. identity_role_mapping 조회 → Identity Core 속성 도출
5. tenant_id = company_id 또는 factory_id
6. 결과: actor_type, visibility_scope, governance_level, notification_level
```

## Menu Visibility 규칙

| 메뉴 | platform | tenant_admin | operator | viewer |
|------|:---:|:---:|:---:|:---:|
| Watch Engine | ✅ | ❌ | ✅ | ❌ |
| 메시지 템플릿 | ✅ | ✅ | ❌ | ❌ |
| 알림 라우팅 | ✅ | ✅ | ❌ | ❌ |
| 워크플로우 | ✅ | ❌ | ✅ | ❌ |

## Notification Audience Resolution 흐름

```
1. Event 발생 (event_type + severity + tenant_id)
2. notification_routing_registry 조회 (event_type 매칭)
   → audience_key, channel, escalation_level, template_key
3. Fallback: identity_role_registry → notification_level 기반
4. 결과: [{role_key, channel, reason, tenant_id}]
```

## 변경하지 않은 것 (기존 유지)

- users 테이블 구조
- roles 테이블 구조
- role_permissions (149건)
- role_menu_permissions (185건)
- role_site_permissions (15건)
- role_data_scope (8건)
- localStorage token 기반 auth
- login/auth flow
