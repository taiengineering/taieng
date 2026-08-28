# §82 EDUCATION ASSIGNMENT AUTHORIZATION BOUNDARY — Phase A 구현 작업지시서 (Cursor)

- **BASE** = tai-api main `ac3f125bec94f0ad15b0b930b5e6ca149c002363`
- **GOAL** = `G-mtchixh7-ab95bd` (OPEN) / GPT FIX SCOPE 승인본
- **BRANCH(신규)** = `s82/education-assign-auth` (base = main `ac3f125b`)
- **MODE** = Phase A = CODE + TEST + COMMIT/PUSH. **MERGE/DEPLOY/PROD DB MUTATION = 0.**

## 확정 아키텍처 결정 (변경 금지)
- **GLOBAL GUARD = FROZEN**: `services/permission_guard.py` 무변경. `PERMISSION_GUARD_ENFORCE`·`api_permissions`·`role_permissions`·`role_menu_permissions` **무변경**.
  - (실측: prod `PERMISSION_GUARD_MODE=ENFORCE`, `PERMISSION_GUARD_ENFORCE=platform` → education는 advisory/fail-open. §82는 전역가드 아닌 **endpoint-local + Layer2**로 독립적으로 닫는다.)
- **AUTH = endpoint-local** (`Depends(get_current_user)`). **SCOPE = 기존 `services/company_scope.py` helper 재사용** (신규 auth/scope framework 발명 금지).

## FROZEN 라우트 (수정 금지)
- `GET /education/{edu_id}` — worker PWA read. **FROZEN.**
- `GET/PUT/DELETE /education/company-settings[/{education_id}]` — education.py 선등록 핸들러가 실제 live, education_assign 쪽은 shadowed. **FROZEN(교육_assign의 3핸들러 그대로 둠, 삭제/리팩터 0).**
- `routers/education.py` — import/reference only. **FROZEN.**
- §81 `POST /education/worker-complete` (routers/worker_assets.py) — **FROZEN.**
- `services/permission_guard.py`, `api_permissions` — **FROZEN.**

## 참조 파일/blob (BASE ac3f125b)
- 대상: `routers/education_assign.py` (blob `79db09d148a66f09feed5b006ce1ea84b903570c`, 20668B, prefix `/education`)
- scheduler: `scheduler.py` (blob `2685851b5324a7050487899d821e2e8bbe7d62b8`) — `DIRECT_HANDLERS` dict + `_execute_direct`
- 레퍼런스 헬퍼: `services/company_scope.py` (blob `8cb2ec0b4191244c8e43f57b9ce82567dfddc921`)
- 인증: `from routers.auth import get_current_user` (current = users dict: `id, company_id, factory_id, team_id, role_code`)

## company_scope 헬퍼 시맨틱 (그대로 사용)
- `_scope(sb, role_code)` → role_data_scope.scope_type (ALL/COMPANY/FACTORY/TEAM/ASSIGNED, 기본 TEAM)
- `_is_admin(scope)` → scope=="ALL" (플랫폼 총관리자만)
- `_ensure_factory_own(sb, factory_id, current)` → 비-ALL이 타사 factory면 404 ("시설을 찾을 수 없습니다"). ALL은 통과.
- `_forced_company_id(current, sb, company_id=None)` → 비-ALL이면 토큰 company_id 반환(클라 값 무시), ALL이면 인자 유지.
- `scoped_filter(current, sb, table_cols)` → `{}`(ALL) / `DENY` / dict. education_assignment는 company_id 컬럼 없음·factory_id만 → `scoped_filter(current, sb, {"factory_id"})` 사용 시 COMPANY tier는 `{"factory_id__in": [회사 factory ids]}` 반환, 미배정 factory tier는 DENY.
- `apply_scoped_filter(query, filt)` → DENY면 None 반환(라우터는 빈 결과 반환), {}면 그대로, dict면 eq/in 적용.

---

## education_assignment 스키마 사실 (prod 실측)
- 컬럼: id, factory_id, education_id, worker_id, user_id, assigned_at, due_date, status_code, completed_at, completed_hours, certificate_url, note, notified_at, reminded_at, **assigned_by**, created_at, updated_at.
- **company_id 컬럼 없음** (tenant scope는 factory→company 경유).
- 제약 = **PK(id)만, UNIQUE 없음**. 현재 0행.
- worker_id → `worker_registry.id` (worker_registry에 company_id·factory_id·user_id·is_active 존재).
- user_id → `users.id` (users에 company_id·factory_id 존재).

---

# 구현 상세

## 1) GET /education/master
- `current: dict = Depends(get_current_user)` 추가. (무토큰 → get_current_user가 401)
- education_master는 글로벌 마스터 → **company filter 불필요**. 기존 response·정렬 유지.
- 신규 role 발명 금지.

## 2) POST /education/assign
- `Depends(get_current_user)` 추가.
- **비-ALL 한정 tenant 강제** (ALL/platform은 기존 company_scope 관례대로 통과):
  1. `_ensure_factory_own(sb, body.factory_id, current)` — foreign factory → 404. (client factory_id는 대상선택값일 뿐 authz fact 아님)
  2. education_master **exact**: `id = body.education_id AND is_active = true` 1건 필수, 없으면 404.
  3. **TARGET VALIDATION (fail-closed, INSERT 이전에 전량 검증)**:
     - `worker_ids` 각각: `worker_registry`에 `id ∈ worker_ids AND factory_id = body.factory_id` 로 조회한 집합이 요청 집합과 **완전 일치**해야 함. 하나라도 누락(=foreign/absent) → **403, INSERT 0**.
     - `user_ids` 각각: `users`에 `id ∈ user_ids AND company_id = <token company>` 로 조회한 집합이 요청 집합과 **완전 일치**. 누락 → **403, INSERT 0**.
     - `<token company>` = `_forced_company_id(current, sb, None)`.
     - **partial cross-tenant insert 절대 금지** — 검증 실패 시 어떤 행도 insert하지 않는다.
  4. `assigned_by = current["id"]` (server-derived) 를 각 INSERT row에 설정.
- **DUPLICATE**: 신규 UNIQUE/DDL 없음. 기존 dup 업무정책 변경 없음(§82는 authorization만).
- ALL(platform) caller: `_ensure_factory_own`는 자동 통과, target membership 검증은 **생략**(플랫폼은 cross-tenant 허용). 단 assigned_by는 동일하게 설정.

## 3) GET /education/assignments
- `Depends(get_current_user)` 추가.
- **NO-QUERY 전사조회 금지.** caller 접근가능 company/factory 범위만.
  - `factory_id` 제공 시: `_ensure_factory_own(sb, factory_id, current)` 후 `.eq("factory_id", factory_id)`.
  - 미제공 시: `filt = scoped_filter(current, sb, {"factory_id"})` → `q = apply_scoped_filter(q, filt)`; `q is None`(DENY)이면 빈 목록(items=[], total=0) 반환.
- `company_id` query는 **authz source로 신뢰 금지** (기존 effective_url 병합용 factory→company 조회에만 사용). 비-ALL은 token company_scope 강제.
- ALL/platform: 기존 company_scope semantics 그대로.
- 반환 필드/effective_url 병합 로직은 유지.

## 4) GET /education/assignments/summary
- `Depends(get_current_user)` 추가.
- **`if company_id: pass` 제거.** list와 **동일 tenant scope** 적용:
  - `factory_id` 제공 → `_ensure_factory_own` 후 `.eq`.
  - 미제공 → `scoped_filter(current, sb, {"factory_id"})` + apply; DENY면 전부 0 집계 반환.
- cross-tenant aggregation = 0.

## 5) PATCH /education/assignment/{assignment_id}/complete
- `Depends(get_current_user)` 추가.
- 먼저 assignment 조회: `id, factory_id, status_code`. 없으면 404.
- `_ensure_factory_own(sb, assignment.factory_id, current)` 통과 후에만 UPDATE. foreign → 404, **UPDATE 0**.
- `completed_at` 등 업무계약(기존 `body.completed_at or now`)은 **재설계 금지** — authorization만 추가.
- **worker self-complete로 확장 금지.** worker self flow는 §81 `POST /education/worker-complete` 유지.

## 6) POST /education/assignment/{assignment_id}/certificate
- `Depends(get_current_user)` 추가.
- assignment 조회: `id, factory_id`. 없으면 404.
- `_ensure_factory_own(sb, assignment.factory_id, current)` 통과 후만 UPDATE. foreign → 404, **UPDATE 0**.
- certificate_url storage/url 정책은 재설계 금지 — authorization만.

## 7) CRON core 추출 + DIRECT handler
- **신규 파일 허용**: `services/education_assignment_svc.py`
  - `def expire_overdue_education_assignments(sb) -> dict:` — 책임: `status_code='PENDING' AND due_date < today` → `'OVERDUE'` UPDATE. 반환 `{"updated": int, "date": "<YYYY-MM-DD>"}`. (기존 `POST /education/assignments/expire` 로직을 이 core로 이동.)
- `routers/education_assign.py`의 `POST /education/assignments/expire`:
  - **Phase A에서는 HTTP route 유지**(아직 크론이 HTTP를 가리킴 — 잠그면 크론 파손). **AUTH 추가 금지.**
  - body 로직을 core 호출로 교체(`expire_overdue_education_assignments(get_supabase())`) — business SQL 중복 제거.
- `scheduler.py`:
  - `DIRECT_HANDLERS`에 `"direct://education_assignment_expire": _run_education_assignment_expire` 추가.
  - `_run_education_assignment_expire(p)` → `from services.education_assignment_svc import expire_overdue_education_assignments; from db.supabase_client import get_supabase; return expire_overdue_education_assignments(get_supabase())`.
  - **새 secret/header/auth protocol 생성 금지.** 기존 direct:// framework 그대로.
- ⚠ **cron_job_master.endpoint_url 변경은 Phase A 아님** (Phase C prod DB config cutover, 별도 GPT 승인). HTTP retire(410)는 Phase D.

---

## 필수 테스트 (`tests/test_education_assign_auth.py` 신규)
FakeSB 패턴(§81 참조). role_data_scope stub으로 ALL/COMPANY tier 모사.

- **MASTER**: M1 no token→401 · M2 auth→200
- **ASSIGN**: A1 no token→401 · A2 own factory→allowed · A3 foreign factory→deny/insert0 · A4 own worker→allowed · A5 foreign worker→deny/batch insert0 · A6 own user→allowed · A7 foreign user→deny/batch insert0 · A8 inactive/unknown education→404 · A9 assigned_by=token user id
- **LIST**: L1 no token→401 · L2 no-query→caller scope only · L3 own factory→own rows · L4 foreign factory→deny · L5 foreign tenant exposure=0
- **SUMMARY**: S1 no token→401 · S2 no-query→caller scope only · S3 company_id 더이상 무시 안 됨 · S4 foreign factory/company exposure=0
- **COMPLETE**: C1 no token→401 · C2 own→success · C3 foreign→deny · C4 foreign UPDATE count=0
- **CERTIFICATE**: T1 no token→401 · T2 own→success · T3 foreign→deny · T4 foreign UPDATE count=0
- **CRON DIRECT**: D1 direct handler registered · D2 direct handler가 정확히 shared core 호출 · D3 pending+overdue update · D4 non-overdue 무변경 · D5 completed 무변경 · D6 updated count exact · D7 direct mode에서 HTTP request 미사용
- **FROZEN**: F1 GET /education/{edu_id} worker contract 무변경 · F2 company-settings live=education.py 무변경 · F3 §81 worker-complete 무변경 · F4 permission_guard 무변경 · F5 api_permissions DB change 0

---

## Phase A 경계 (BOUNDARY)
- CODE CHANGE = YES (`routers/education_assign.py`, `scheduler.py`, `services/education_assignment_svc.py`, `tests/test_education_assign_auth.py`)
- TEST = YES · COMMIT/PUSH = YES (branch `s82/education-assign-auth`)
- **DDL = 0 · NEW RPC = 0 · PROD DB MUTATION = 0 · PROD HTTP MUTATION = 0 · MERGE = 0 · DEPLOY = 0**
- permission_guard change = 0 · api_permissions change = 0 · frontend change = 0
- cron_job_master change = 0 (Phase C)

## Push-fidelity 규율
- push 전 각 파일 `git hash-object` 기록, commit 후 blob 대조. Korean/SQL 문자열 drift 주의(실행코드는 byte-identical 유지).
- 완료 후 최종 blob SHA + 브랜치 head SHA + full-suite pytest 결과를 보고(§82 IMPLEMENTATION REPORT — PHASE A 양식).

## 후속 순서 (참고, Phase A 아님)
- Phase B: MERGE/DEPLOY → direct handler가 prod code에 먼저 존재.
- Phase C: cron_job_master.endpoint_url → `direct://education_assignment_expire` (PROD DB config 1행, 별도 GPT 승인) → scheduler reload → DIRECT 실행 증명(triggered_by=SCHEDULE, mode=DIRECT, HTTP status 의존 없음).
- Phase D: HTTP `POST /education/assignments/expire` → **410 GONE** (detail `CRON_DIRECT_ONLY`), 별도 소형 commit/deploy.
