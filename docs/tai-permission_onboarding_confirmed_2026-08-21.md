# TAI 권한·Entitlement·온보딩 구조 확정본 · 2026-08-21

- 운영자 구술 로직 + DB/코드 실측 종합. **오픈 전 권한 정리의 기준선(as-is + 확정 규칙).**
- 프론트: taeing.co.kr(마케팅) · safe.taieng.co.kr(제품) · admin.taieng.co.kr(운영)

---

## 1. 접근 사다리 (온보딩 퍼널 — 확정 규칙)

```
무료진단   → 핸드폰인증(diagnosis_auth_log, free_limit 3회)         [계정 불요]
   ↓ 회원가입 = 인증번호(ci/phone)로 계정 매핑(linked_user_id) → 무료결과 귀속
회원(계정) → 유료진단(견적·실행) 가능                                [계정 필수]
   ↓ SaaS 결제(subscriptions / contracts)
SaaS 구독  → safe 접속·입력 가능                                     [구독 필수]
   ↓ 만료
만료       → safe 조회 O / 입력 X (read-only)                        [write 차단]
```

**Entitlement 게이트 2개:**
1. **계정(회원가입)** → 유료진단 진입 허용
2. **SaaS 구독(유효)** → safe 접근 허용, 만료 시 write 차단

---

## 2. 3층 접근 모델 + 온보딩 퍼널

```
[Layer 0] Entitlement — safe 진입 = 유효 구독/계약. 만료 시 write 차단·read 허용
[Layer 1] Action 권한 — api_permissions(RBAC 매트릭스)
[Layer 2] Data 스코프 — company_scope(role_data_scope)
```
- Layer 0가 운영자가 추가한 층(구독 게이트). Layer 1·2는 기존 RBAC.

---

## 3. DB 백본 (실측 — 스키마는 전부 존재)

| 목적 | 테이블·핵심 컬럼 |
|---|---|
| 무료진단 폰인증·3회 | `diagnosis_auth_log`: ci·ci_hash·phone·verified_at · **free_count·free_limit**·last_free_at · **linked_user_id**·auth_token |
| 무료 결과 저장 | `anonymous_diagnosis_results`: public_token·input_data·full_result·**claimed_user_id**·status |
| 유료진단 견적/계약 | `quotes`(REQUESTED) → `contracts`: status_code·start_date·**end_date**·max_factory_count·max_user_count·service_type |
| SaaS 구독 | `subscriptions`: user_id·company_id·product_type·plan_code·**status**·started_at·**next_billing_at·ended_at**·factory_id |
| 결제 | `payments`·`billing_keys`·`inicis_order_id` |
| RBAC | `roles`(18)·`permissions`(45)·`role_permissions`(149)·`api_permissions`(28)·`role_menu_permissions`(185)·`role_data_scope`(9)·`menu_permissions`(**0**) |
| 아이덴티티 | `identity_role_registry`(7: platform_admin/tenant_admin/operator/user/partner/system/synthetic) · `identity_role_mapping`(14/18 브릿지) |

---

## 4. 두 축 (권한 관리 주체)

### 축1 · 어드민(admin.taieng.co.kr) = 플랫폼 운영
- 개념: identity `platform_admin`. 현재 role **001**만 매핑, 하드코딩(`_is_admin`=scope 'ALL').
- **플랫폼-운영 권한 카탈로그 없음**(계약·고객·전문가·정산 미권한화). 관리 UI 없음.

### 축2 · safe(safe.taieng.co.kr) = 테넌트 사용자 부여
- 개념: tenant_admin(COMPANY)→operator(FACTORY)→user(self)→partner(하도급).
- UI: `manager-permission`(vue3) **완성** — `GET/PATCH/PUT /role-menu-permissions`·`GET /users/roles` 호출. **백엔드 라우터 미마운트 + menu_permissions 빔 → 랜덤 폴백("난수")**.

---

## 5. 헤더 가드 하나로 흡수 (모듈-우선 핵심)

`main.py` 전역 의존성 1개가 라우트를 티어로 분류·강제:

| 티어 | 예 | 규칙 |
|---|---|---|
| 공개/폰게이트 | 무료진단(anonymous) | allowlist |
| 계정 필수 | request-quote·유료진단·claim | 인증 O |
| SaaS entitled | safe 제품 CRUD | 유효 구독 + (write면 만료 아님) + 액션권한(api_permissions) |

- 데이터 스코프(행 필터)는 헤더로 못 풂 → company_scope 유지(Layer 2).
- "무료=폰 / 유료진단=계정 / safe=구독, 만료 시 write 차단"이 **한 가드의 티어 규칙**으로 성립. 라우터 무수정.

---

## 6. 확정된 판정

- **C-0 request-quote 잠금** = 보안 추론이 아니라 **비즈니스 규칙**("유료진단=회원가입 필수"). 현재 무인증 = 규칙 위반. → 잠금 확정.
- **매칭 조인키 = 전화번호(ci)**, token-only 아님. `diagnosis_auth_log`(신원·게이트) ↔ `anonymous_diagnosis_results`(결과)는 auth_token/phone로 연결.

---

## 7. 미확정 — 강제(배선) 실측 대상 (다음 단계)

패턴상 **스키마 선행 · 런타임 강제 미배선** 가능성 높음. 코드로 대조 필요:
1. `diagnosis_auth_log.free_limit` **3회 강제**가 무료진단 진입에 실제 있는지
2. **가입 시 linked_user_id 매핑**(phone 기준) — 진행 중 작업. 현 `claim`은 token 기반 → phone 기반 전환/병행 필요
3. **safe 라우트 entitlement 게이트**(유효 구독 확인) 존재 여부 — 아마 없음 → 헤더로 신설
4. **read-only-on-expiry** 강제 — 없음 → 헤더 write-gate로 신설
5. safe 권한부여 백엔드(`/role-menu-permissions` + `menu_permissions` 카탈로그) — 미마운트/빔 → 신설
6. RBAC 런타임 강제 — api_permissions/role_permissions 미사용(company_scope 이진만) → 헤더 가드로 배선
7. 축1 플랫폼-운영 권한 티어 — 미존재 → 신설
8. `api_permissions` 경로 재정합(`/api/` 접두·`{id}`↔`{factory_id}`) + 커버리지 확장
9. role_data_scope NULL 9롤 + 직책 중복(003↔012, 004↔014) + 브릿지 미매핑 4롤(003·004·005·006) 정리

---

## 8. 산출물 (이 세션)
- `tai-permission_structure_as-is_2026-08-21.md` (역할 2체계·브릿지·두 축)
- `tai-api_permission-module_design_2026-08-21.md` (헤더 가드 설계·롤아웃)
- `tai-api_C-decision_ledger_2026-08-21.md` (C-0 잠금 결정)
- **본 문서**(통합 확정본)
- 문서 배치: taieng/docs/ 이동은 운영자(R-013).
