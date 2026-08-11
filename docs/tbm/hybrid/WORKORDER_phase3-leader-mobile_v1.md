---
class: plans
type: WORKORDER
scope: tbm
project: hybrid
title: "Phase 3 — TBM 리더 모바일 + 계정 배선"
version: v1
status: draft
owner: taiwang
---

# WORKORDER — Phase 3: TBM 리더 모바일 + 계정 배선

- 작성일: 2026-08-11
- 대상: 모바일(작업자/리더 앱) 담당 창
- 선행: Phase 1(조직 골격)·Phase 2(TBM 그룹화) 완료·배포됨
- 상위 설계: `taieng/docs/2026-08-11_TBM-team-group-hybrid-design.md`
- 상태: 지시(TODO). 아래 "검증된 사실"은 실제 DB/코드 직독으로 확인됨.

---

## 0. 목표 (한 줄)

**TBM 리더(관리감독자·반장)가 현장에서 모바일로 로그인해, 자기 팀/그룹의 TBM을 직접 만들고·실행하고·QR 서명을 받고·미서명자를 추적**할 수 있게 한다. 안전관리자는 웹에서 세팅(조직·팀·그룹·템플릿)을 계속 담당(하이브리드).

---

## 1. 지금까지 된 것 (모바일이 의존하는 백엔드·DB — 검증됨)

### 1-1. 조직 계층 (Phase 1, 배포됨)
- 테이블: `departments`, `groups`, `worker_group`(다중소속), `teams`(확장: department_id·construction_site_id·lead_worker_id).
- 계층: 회사 > 시설(factory|construction_site) > 부서 > 팀 > 그룹 > 근로자.
- 팀 리더 = `teams.lead_worker_id`(1명). 그룹 조장 = `worker_group.is_lead`.
- 엔드포인트(`routers/org.py`):
  - `GET/POST /departments`, `PATCH/DELETE /departments/{id}`
  - `GET/POST /teams`, `PATCH/DELETE /teams/{id}`
  - `GET/POST /groups`, `PATCH/DELETE /groups/{id}`
  - `GET/POST /worker-group`(배정, is_lead), `PATCH/DELETE /worker-group/{id}`
  - `GET /worker-registry/{id}/org-assignment` (근로자의 그룹→팀→부서 해석)

### 1-2. TBM 그룹화 (Phase 2, 배포됨)
- `tbm_meetings`에 `group_id`·`team_id` 기록됨.
- `POST /tbm-templates/{id}/use` — `group_id` 지정 시 **그룹원(worker_group) 자동 소집**(tbm_attendees에 worker_id 연결, sign_status=PENDING).
- `GET /tbm`·`GET /tbm/{id}` — 팀·그룹명 임베드(groups(group_name), teams(team_name)).
- 팀 템플릿 스코핑: `tbm_templates.team_id`.

### 1-3. TBM 서명·푸시 (기존, `routers/tbm.py` v1.3.0 — 그대로 재사용 가능)
- `GET  /tbm/{id}/sign-info?attendee_id=` — 서명 페이지 정보(JWT 불필요, 비공개 링크 방식).
- `POST /tbm/{id}/sign` — base64 PNG 서명 → Supabase Storage `signatures` 버킷 업로드 + tbm_attendees 갱신.
- `POST /tbm/{id}/request-sign` {attendee_ids[]} — 참석자 worker_registry.push_token 으로 **FCM 서명요청 푸시**.
- `GET  /tbm/{id}/attendees` — 참석자·서명현황.
- 즉 **모바일 서명·미서명추적은 기존 엔드포인트로 대부분 커버됨.** 신규 개발은 "리더 인증/스코프"와 "리더용 화면"이 핵심.

### 1-4. 계정·인증 인프라 (검증됨 — `users` 22행, "인프라 O, 배선 X")
- `users` 컬럼: company_id·factory_id·**team_id**·role_id·role_code·department·position·sector · username·password_hash · **kakao_id·naver_id·google_id·social_provider** · **biometric_enabled·biometric_key·biometric_device** · **identity_ci·identity_di·identity_verified**(본인인증/PASS) · **signature_url** · **push_token·push_platform** · email_verified · last_login_at · is_active.
- RBAC: `roles`·`role_permissions`·`role_menu_permissions`·`role_site_permissions`·**`role_data_scope`**·`rule_pos_to_role`.
- **미배선(핵심)**: `worker_registry.user_id` = **0건**, `worker_registry.app_installed` = **0건**. `send_invite`(POST /worker-registry/{id}/invite)는 현재 `invite_sent_at`만 찍고 **실제 SMS·계정생성 미구현**.

---

## 2. Phase 3 범위 (해야 할 것)

### A. worker ↔ users 계정 배선 (백엔드)
목적: 근로자가 앱 계정(users)을 갖고, 리더는 자기 팀/그룹 스코프 권한을 가진다.

- **A-1. 초대→계정 연결 흐름 정의**
  - `POST /worker-registry/{id}/invite` 를 실제 동작으로: (1) 초대 토큰/링크 생성, (2) SMS 발송(**MessageMi 연동** — 기존 채널), (3) `invite_sent_at` 기록.
  - 근로자가 링크로 앱 최초 진입 → **본인인증(PASS/identity_*) 또는 소셜(kakao/naver/google) 로그인** → `users` 레코드 생성/연결 → `worker_registry.user_id = users.id`, `app_installed = true` 세팅.
  - 매칭 키: worker_registry.phone ↔ users.phone(또는 identity_phone). **중복 계정 방지** 필수.
- **A-2. 리더 식별**
  - 리더 = `teams.lead_worker_id` 인 worker + 그 worker의 `user_id`(users 계정).
  - users.role_code 에 리더 역할 부여(예: `TBM_LEADER`). role 없으면 `roles`에 추가.
- **A-3. 스코프 권한 (`role_data_scope`)**
  - 리더 role_data_scope = 자기 `team_id`(및 그 팀의 group_id들)로 제한.
  - **모든 리더용 조회/생성 API는 이 스코프로 필터** — 리더는 남의 팀 TBM에 접근 불가.
  - ⚠️ `role_data_scope` 실제 스키마(컬럼)를 **먼저 직독**하고 설계할 것(scope_type/scope_value 형태 추정, 확인 필요).

### B. 리더 인증 (백엔드)
- 앱 로그인: `users`의 username/password_hash **또는** 소셜 **또는** 생체(biometric_*).
- 로그인 성공 → JWT(또는 기존 Supabase auth) 발급. 리더 컨텍스트(user_id·team_id·role_code) 포함.
- ⚠️ **기존 앱 인증 방식(Supabase auth vs 자체 JWT)을 먼저 확인** — `routers/auth.py` 직독 후 그 방식에 편승(신규 인증 만들지 말 것).

### C. 리더 모바일 화면 (앱)
현장 사용이므로 **모바일 우선**. 최소 4개 화면:
1. **내 팀/그룹** — 리더의 team_id 하위 그룹·그룹원 목록(`GET /groups?team_id=`, `GET /worker-group?group_id=`).
2. **TBM 만들기** — 팀 템플릿 선택(`GET /tbm-templates?factory_id=&team_id=`) → 그룹 선택 → `POST /tbm-templates/{id}/use` {group_id, conductor_name=리더} → 그룹원 자동 소집. (템플릿 없으면 즉석 위험/안전 입력도 허용 검토.)
3. **TBM 실행/서명** — 생성된 TBM의 참석자(`GET /tbm/{id}/attendees`) → 각자 QR/링크로 서명(`/tbm/{id}/sign-info`→`/tbm/{id}/sign`). 리더가 한 명씩 대면 서명받거나 `POST /tbm/{id}/request-sign`으로 푸시.
4. **미서명 추적** — 참석자 sign_status로 미서명자 하이라이트 + 재요청 버튼. 전원 서명 시 `POST /tbm/{id}/complete`.

### D. 작업자(비리더) 화면
- 기존 `/app/tbm.html`(서명 전용) 흐름 유지·재사용. 필요 시 "내 TBM 목록"만 추가.

---

## 3. 단계별 순서 (리스크 낮은 순)

1. **조사(직독) 먼저** — 신규 개발 전 반드시:
   - `routers/auth.py` (현 앱 인증 방식·JWT/Supabase).
   - `role_data_scope` 테이블 스키마(컬럼·기존 데이터).
   - 기존 앱(`/app/*.html` 또는 앱 레포)의 로그인·TBM 서명 화면 구조.
   - `users` 생성/연결이 이미 어딘가(회원가입·소셜) 구현돼 있는지(중복 개발 방지).
2. **A. 계정 배선** (invite→계정→user_id 연결, 스코프) — 백엔드.
3. **B. 리더 인증/스코프** — 백엔드.
4. **C. 리더 모바일 화면** — 앱. (서명·푸시는 기존 API 재사용.)
5. **D. 작업자 화면** 보완.

각 단계 후 **직독·런타임 검증**(카운트가 아니라 실제 응답·데이터 확인). 완료 선언은 검증 후에만.

---

## 4. 반드시 지킬 원칙 (이 프로젝트 규범)

- **추측 금지, 직독 우선**: 스키마·엔드포인트·기존 화면을 먼저 읽고 편승. 없는 걸 가정하지 말 것.
- **기존 인증/계정 인프라 재사용**: `users`·RBAC·소셜·생체·본인인증·서명·푸시는 **이미 있다**. 새로 만들지 말고 **배선만**.
- **스코프 격리**: 리더는 자기 팀/그룹만. 서버측 `role_data_scope` 강제(클라이언트 신뢰 금지).
- **파일 크기 규칙**: 200줄+/20KB+ 파일은 로컬편집(가급적), MCP는 짧은 파일·DB·PR.
- **/health 200 유지**, 신규 라우터는 `router_registry/*` 그룹에 스펙 등록(직접 import 금지).
- **법령엔진 불가침** — Phase 3는 SaaS 운영 영역(엔진 무관).
- **중복 계정·중복 배정 방지**: worker↔user 매칭 키 명확화, `ON CONFLICT`/UNIQUE 활용.
- **개인정보**: 본인인증(CI/DI)·전화·서명은 민감정보 — 스코프·접근통제 준수.

---

## 5. 미결정(착수 전 확정 필요)

1. **앱 인증 방식**: 리더 로그인을 Supabase auth로 갈지, 자체 JWT로 갈지 — `auth.py` 확인 후 결정.
2. **초대 채널**: SMS(MessageMi) 링크 방식 확정? 카카오 알림톡 병행?
3. **리더 role_code 명칭**과 role_data_scope 표현 방식(team 단위 vs group 단위).
4. **즉석 TBM**(템플릿 없이 리더가 현장에서 바로 위험/안전 입력) 허용 여부.
5. **작업자 앱**과 리더 앱을 하나의 앱에서 role로 분기할지, 별도 진입점일지.

---

## 6. 참고 — 기존 관련 파일/엔드포인트 인덱스

- 조직: `routers/org.py`, `routers/worker_org.py`
- TBM: `routers/tbm.py`(서명·푸시·CRUD), `routers/tbm_templates.py`(템플릿·/use 그룹소집)
- 근로자: `routers/worker_registry.py`(등록·초대 stub)
- 인증/사용자: `routers/auth.py`, `routers/users.py`(직독 요망)
- 프론트(웹 참고): `tai-admin/vue3/src/pages/org-setting`, `.../worker-list`, `.../tbm-setting`, `.../tbm-list`
- DB(Seoul): project_ref `vwlahtguyggrhvslabax`
- 외부: MessageMi(SMS)·FCM(푸시, `utils/fcm_utils.send_push`)·Supabase Storage `signatures` 버킷

---

## 변경 이력
- v1 (2026-08-11): 초안. Phase 1·2 완료 상태 기준. 모바일 창 인계용 자족 지시서.
