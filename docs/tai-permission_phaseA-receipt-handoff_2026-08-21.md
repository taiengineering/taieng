# 권한 정리 Phase A 완료 + 코드단계 핸드오프 · 2026-08-21

- Goal: G-mt2y0gao (오픈전 구조 정합, 기존데이터 미보호) · DB vwlahtguyggrhvslabax
- 성격: DB 데이터정합만 수행(런타임 코드 미변경). 남은 건 코드/엔진 단계.

---

## 1. 이번 세션 DB 변경 (RECEIPT — 검증완료)

| # | 변경 | 대상 |
|---|---|---|
| 1 | `INSERT identity_role_mapping` ×4 | 003·004·005·006 (브릿지 완성 → 18/18) |
| 2 | `INSERT role_data_scope` ×9 | 010·011·012·014·015·016·020·021·022 (→ 18/18) |
| 3 | `UPDATE role_name='근로자'` | 004·014 (roles + identity_role_mapping) |
| 4 | `UPDATE is_active=false` | 005·006·020·021·022 (B안 도급 흡수, 0 users) |
| 5 | `UPDATE role_name='대표이사'` | 010 (roles + identity_role_mapping) |
| 6 | `INSERT 009 안전보건관리담당자` | roles + role_data_scope + identity_role_mapping (제19조) |
| 7 | `UPDATE scope_type='TEAM'` | 013 identity_role_mapping (role_data_scope와 정합) |

**검증**: 브릿지 18/18 · role_data_scope 18/18 · scope 충돌 **0** · 활성 role **10**.

---

## 2. 최종 활성 카탈로그 (법정 정합)

| code | role_name | identity | scope | 근거 |
|---|---|---|---|---|
| 001 | 최고관리자 | platform_admin | ALL | 플랫폼 |
| 002 | 관리자 | tenant_admin | COMPANY | 플랫폼 |
| 009 | 안전보건관리담당자 | tenant_operator | FACTORY | 제19조 |
| 010 | 대표이사 | tenant_admin | COMPANY | 제14조 |
| 011 | 안전보건관리책임자 | tenant_admin | COMPANY | 제15조 |
| 012 | 안전관리자 | tenant_operator | FACTORY | 제17조 |
| 013 | 관리감독자 | tenant_operator | TEAM | 제16조 |
| 014 | 근로자 | tenant_user | TEAM | 산안법 |
| 015 | 산업보건의 | tenant_user | ASSIGNED | 제22조 |
| 016 | 보건관리자 | tenant_operator | FACTORY | 제18조 |

**폐기(is_active=false)**: 003·004·005·006·007·008·020·021·022
(003·004 중복·007·008 기능役 — seed에서 기존 비활성 / 005·006·020·021·022 — 이번 B 흡수)

---

## 3. 코드단계 핸드오프 (데이터 골 밖 → Cursor/코드골)

| ID | 태스크 | 근거/현황 | 분업 |
|---|---|---|---|
| **T1** | **난수 해소 라우터** — `GET/PATCH/PUT /role-menu-permissions` + `GET /users/roles?site=tadmin` | 프론트 계약(useManagerPermissionList.ts) 이미 존재. role_menu_permissions 활성 141행 준비됨. menu_permissions는 vestigial(무관) | 신규 라우터 → MCP/Cursor |
| **T2** | **헤더 가드 permission_guard** (main.py 전역) | Layer0 entitlement(④⑤) + Layer1 action(⑥). ADVISORY→ENFORCE. 데이터 스코프는 company_scope 유지 | **코어 보안 → Cursor** |
| **T3** | **유료진단 회원가입 게이트**(③) | `/diagnosis/run` 유료분기 핸들러 JWT + `/diagnosis/upgrade` 라우트 JWT | Cursor |
| **T4** | **api_permissions 재정합+확장**(⑧) | 코드 0참조. 실제 route.path로 `{factory_id}`·`/api` 교정 + 커버리지. **T2와 동반** | T2와 함께 |
| **T5** | **플랫폼 권한 티어**(⑦) | 플랫폼-운영 permission_group 신설, 001 all-or-nothing 탈피, admin UI | 코드+DB |

### 엔진 조율 (GPT 소유, Claude 미착수)
- **도급인/수급인/관계수급인 = 회사 속성** (B안 회사측 반쪽). 법령엔진 도급 의무(제63조 등) 입력에 물림 → 엔진 오너(GPT)와 조율 후 스키마/입력 설계.

---

## 4. 플래그 (반영조건·잔여)

- **watch_engine 재시작 필요**: `watch_engine/identity/_role_mapping_cache`는 서버 시작 시 1회 로드 → 003/004/005/006/009/010/013 반영엔 재시작(코드배포 아님).
- **003 안전관리자(비활성)에 test 사용자 4명** 잔존 → 실사용자 정리 시 활성 012로 remap.
- **폐기 role 소프트(is_active=false)** 유지 + role_menu_permissions 44 stale행 **보존**(재활성 대비).
- **중복 잔존**: 003↔012 안전관리자, 004↔014 근로자 (활성은 012·014). role_code dedup은 users remap 수반 → 별도.
- **menu_permissions vestigial** — 코드 미사용, 스킵.

---

## 5. 산출물 계보
1. tai-permission_structure_as-is_2026-08-21.md
2. tai-api_permission-module_design_2026-08-21.md
3. tai-permission_onboarding_confirmed_2026-08-21.md
4. tai-permission_target-design_2026-08-21.md
5. **본 문서** (Phase A 리시트 + 코드 핸드오프)
