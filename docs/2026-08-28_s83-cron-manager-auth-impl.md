# §83 CRON MANAGER AUTHORIZATION BOUNDARY — 구현 작업지시서 (Cursor)

- **BASE** = tai-api main `49616f261927cb382e24133dbb4a2e00615e03bd`
- **BRANCH(신규)** = `s83/cron-manager-auth` (base = main `49616f26`)
- **GOAL** = `G-mtcrc6ot-ab95bd`
- **MODE** = 구현 + pytest + commit/push. **MERGE/DEPLOY = 0** · PROD DB/cron mutation 0 · manual run 0 · scheduler reload 0.

## 확정 아키텍처 (조사 PASS 반영)
cron manager는 tenant 업무 API가 아니라 **platform control-plane**. `/cron/*` 전체를 **기존 ALL-scope(플랫폼 최고관리자 role 001, 유일) 전용**으로 게이트.
- IDENTITY = 기존 `get_current_user`
- AUTHORIZATION = 기존 `services.company_scope._require_admin(current, sb)` (실재 헬퍼: `_is_admin(_scope(sb, role_code))` 아니면 403)
- **새 role/permission/menu 체계 생성 금지. company_scope 로직 수정 금지(import만).** company_id/factory_id tenant scope 미적용(cron은 tenant 자원 아님).

## 변경 파일 (딱 2개)
- `routers/cron_manager.py`
- `tests/test_cron_manager_auth.py` (신규)

## FROZEN (재접촉 금지)
`scheduler.py` · `services/permission_guard.py` · `services/company_scope.py`(수정 0, import만) · `routers/auth.py` · `cron_job_master`/`cron_schedule_config`(DB) · `api_permissions`·`role_permissions`·`role_menu_permissions`·`menu_catalog` · `PERMISSION_GUARD_MODE/ENFORCE` · frontend · `CronJobCreate` 스키마 · endpoint_url/http_method 검증 · DIRECT handler registry · HTTP requests 실행 · `INTERNAL_API_SECRET`/`INTERNAL_API_URL`.
→ **system job PATCH/RUN 정책 = FROZEN**(새 is_system 제한 추가 금지; DELETE의 기존 403만 유지). **HTTP transport hardening·create validation = PARK**(§83 범위 아님).

---

## 구현 상세

### imports (routers/cron_manager.py)
```python
from fastapi import APIRouter, Depends, HTTPException   # Depends 추가
from routers.auth import get_current_user
from services.company_scope import _require_admin
```
(`from db.database import get_supabase` 는 기존 유지.)

### 공통 패턴 — 10개 endpoint 전부
각 endpoint에 `current: dict = Depends(get_current_user)` 파라미터를 추가하고, **본문 최상단(민감 DB read/write·scheduler op·log INSERT보다 먼저)** 에서:
```python
sb = get_supabase()
_require_admin(current, sb)      # 비-ALL → 403, 무토큰은 get_current_user가 이미 401
```
- 이미 `sb = get_supabase()` 로 시작하는 endpoint는 그 **직후** 에 `_require_admin(current, sb)` 삽입.
- `POST /reload` 는 현재 sb를 만들지 않음 → try 진입 전에 `_require_admin(current, get_supabase())` 를 두어 `load_jobs_from_db()`·`scheduler.start()` **이전** 에 인가.
- 계약: NO TOKEN → 401 · authenticated NON-ALL → 403 · authenticated ALL → 기존 기능 그대로.

적용 대상(전부):
`GET /cron/jobs` · `GET /cron/jobs/{job_code}` · `POST /cron/jobs` · `PATCH /cron/jobs/{job_code}` · `DELETE /cron/jobs/{job_code}` · `POST /cron/jobs/{job_code}/run` · `POST /cron/reload` · `GET /cron/scheduler-status` · `GET /cron/logs` · `GET /cron/stats`.
(GET도 platform-only — endpoint_url·payload·cron log·error_message·scheduler topology 등 control-plane 정보 포함.)

### MANUAL RUN — `POST /cron/jobs/{job_code}/run` (L4 audit identity)
- 시그니처에서 `user_email: str = "admin"` **삭제**. 대신 `current: dict = Depends(get_current_user)` 추가.
- 본문 최상단: `sb = get_supabase(); _require_admin(current, sb)` (job 조회·log INSERT·`_execute_direct`·`requests` 호출 **모두 이전**).
- audit identity 서버파생:
```python
audit_user = current.get("email") or str(current["id"])
```
  cron_job_log INSERT의 `triggered_by_user = audit_user` (client 값 불신). `triggered_by="MANUAL"` 유지.
- **DIRECT/HTTP 실행 로직 자체는 무변경**(그대로). 클라가 `?user_email=…` 보내도 audit identity 영향 0.

### SYSTEM JOB — 무변경
- DELETE: `is_system=true → 403` 기존 계약 유지.
- PATCH/RUN: ALL admin은 기존대로 실행 가능. **새 is_system 제한 추가 금지**(정본 의미가 "삭제 불가"까지만 확정).

---

## 테스트 (`tests/test_cron_manager_auth.py` 신규)
FakeSB 인메모리 + `dependency_overrides[get_current_user]` + role_data_scope seed(ALL=admin role, COMPANY=non-admin). `routers.cron_manager.get_supabase` monkeypatch. 실행류는 monkeypatch로 스파이:
`scheduler._execute_direct` · `requests`(get/post) · `scheduler.load_jobs_from_db` · `scheduler.scheduler`(start).

**auth matrix (10 routes)**: 각 route에 대해
- no token → 401
- authenticated NON-ALL → 403
- authenticated ALL → 기존 동작(200/기존 path)

구체:
- **J1/J2/J3** GET /cron/jobs
- **D1/D2/D3** GET /cron/jobs/{job_code}
- **C1/C2/C3** POST /cron/jobs (C1/C2 → INSERT 0)
- **P1/P2/P3** PATCH /cron/jobs/{job_code} (P1/P2 → UPDATE 0)
- **X1/X2/X3/X4** DELETE (X1/X2 → DELETE 0; X3 ALL+non-system 삭제; X4 ALL+system → 기존 403 유지)
- **R1** no token → 401 · DIRECT 0 · HTTP 0 · cron_job_log INSERT 0
- **R2** non-ALL → 403 · execution 0 · log INSERT 0
- **R3** ALL + DIRECT fake job → 기존 DIRECT path(_execute_direct 호출됨, monkeypatched)
- **R4** ALL + HTTP fake job → 기존 HTTP path(requests monkeypatch only)
- **R5** audit identity = current email or current id
- **R6** caller가 `?user_email=evil@x.com` 보내도 triggered_by_user 불변(서버파생)
- **RL1** no token → 401 · load_jobs_from_db 0 · scheduler.start 0
- **RL2** non-ALL → 403 · scheduler mutation 0
- **RL3** ALL → 기존 reload path
- **status/logs/stats**: 각 no token→401 · non-ALL→403 · ALL→기존 response

**authorization ORDER (핵심)**: no-token / non-ALL 요청에서 다음이 **전부 0**임을 단언:
`cron_job_master INSERT/UPDATE/DELETE = 0` · `_execute_direct 호출 0` · `requests.get/post 0` · `load_jobs_from_db 0` · `scheduler.start 0` · `cron_job_log INSERT 0`.
(즉 인가 실패 시 민감 read/write·실행이 선행되지 않음.)

---

## BOUNDARY
- EXPECTED CHANGE = `routers/cron_manager.py` · `tests/test_cron_manager_auth.py`
- CODE CHANGE = YES · TEST = YES · COMMIT/PUSH = YES
- DDL = 0 · NEW RPC = 0 · PROD DB MUTATION = 0 · CRON MUTATION = 0 · MANUAL RUN = 0 · SCHEDULER RELOAD = 0 · MERGE = 0 · DEPLOY = 0
- scheduler.py=0 · permission_guard=0 · company_scope=0(수정) · auth.py=0 · cron DB=0 · api_permissions/role/menu=0 · frontend=0

## Push-fidelity
- push 전 두 파일 `git hash-object` 기록·commit 후 blob 대조(Korean drift 주의). 완료 후 NEW HEAD·blob SHA·pytest 결과를 §83 IMPLEMENTATION REPORT 양식으로 보고.

## 후속 (별도, §83 아님)
- CRON TRANSPORT HARDENING(HTTP manual-run service-auth 또는 DIRECT-only 축소) · CREATE endpoint validation(endpoint_url/method allowlist) · 전역 guard defense-in-depth(/cron → PLATFORM_* api_permissions) — 각각 별도 gate.
