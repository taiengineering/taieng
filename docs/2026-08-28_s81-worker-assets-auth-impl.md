# §81 — WORKER ASSETS AUTHORIZATION BOUNDARY · 구현 작업지시서 (Cursor)

- BASE = tai-api main `bae1349b80a92b9bf76cd20bcf5e126249dc2063`
- TARGET = `routers/worker_assets.py` (+ `services/upload_service.py` 최소 노출 · `tests/`)
- GOAL = `G-mtce7l8v-ab95bd` (WorkerAssets Authorization Boundary) · STATE = OPEN
- 권한 = SOURCE IMPLEMENT + TEST + BRANCH COMMIT/PUSH. **DDL=0 · NEW RPC=0 · PROD DB MUTATION=0 · MERGE=0 · DEPLOY=0**
- 실행 = Cursor 로컬 구현 + `pytest` 통과 확인 후 브랜치 push. (MCP 창은 push 후 직독 검증)

> §81 은 복원된 옛 번호가 아니라 **신규 부여** 번호다. company-docs 는 **PRIVATE bucket**이다("public bucket vulnerability" 표현 금지).

---

## 0. 직독 GROUNDING (base bae1349b, READ-ONLY 확정)

1. **get_current_user** — `routers/auth.py` 정의. `from routers.auth import get_current_user`.
   - `get_current_user(authorization: Optional[str] = Header(None)) -> dict`
   - 토큰 없음/형식오류 → **401** "토큰이 없습니다" · 무효 → 401 · users(auth_id) 행 없음 → **404**.
   - 반환 = users 전체 행 dict (`id`, `company_id`, `factory_id` 포함). `_optional_auth` 성공 반환과 동일 shape.
2. **upload_service.py** — 재사용은 **검증 로직만**. `upload_inspection_photo()` 전체 호출 금지.
   - 이유: `BUCKET="inspections"` + `get_public_url` 이라 그대로 쓰면 **company-docs 아닌 잘못된 버킷**에 씀.
   - 재사용 대상: `_validate_file(file, contents) -> ext` (>5MB→413, magic MIME 검사, 미허용→415, canonical ext 반환) / `_detect_mime(data)` (JPEG `ff d8 ff` · PNG `89 50 4e 47 0d 0a 1a 0a` · WEBP `RIFF....WEBP`). `MAX_SIZE=5MB`, `ALLOWED_MIMES={jpeg,png,webp}`, `MIME_TO_EXT`.
   - `_validate_file` 는 underscore-private → **public 래퍼 `validate_image_file(file, contents) -> str` 를 upload_service.py 에 추가**(내부에서 `_validate_file` 호출)하고 worker_assets 는 그 public 함수를 import. private 직접 import 금지.
3. **attachments 스키마** — `id, table_name, record_id(uuid), file_category, file_url(text), description, created_at, sort_order, is_primary, uploaded_by(uuid), file_name, file_size, file_ext, mime_type, image_*, taken_at, gps_*, device_*, orientation, exif_json, file_hash, is_photo`. **전용 storage_path/bucket 컬럼 없음** → stable ref 는 `file_url` 에 저장.
4. **education_master** — `id(uuid)`, `education_code(text NOT NULL)`, `is_active(bool)`, `cycle_type`, `cycle_value` 등. prod 20행 **전부 is_active=true** → `WHERE is_active=true` 게이트가 라이브 flow 파손 없음.
5. **education_history** — prod 9행 **전부 canonical code_form, UUID-form=0** → worker-complete 경로가 **아직 prod 미실행**(9행은 admin create 산물). **백필/마이그레이션 불필요**, canonical code 전환·is_active 게이트 회귀 위험 0.
6. **verify-otp (auth.py)** — `worker_id = user["id"]` (= users.id) + `access_token` 발급. PWA `_user.worker_id||_user.id`, `_user.phone` 는 모두 **본인 = current_user.id**. → "동일할 때만 허용" 게이트가 **라이브 PWA 무파손** → **tai-admin/FE 수정 = 0** 확정.
7. PWA 콜러(tai-admin, ref e3e6011c): `_utils.js TAI.apiFetch` 가 localStorage access_token 을 `Authorization: Bearer` 자동 주입. `TAI.uploadPhoto`(FormData file/context/inspection_id?/factory_id?/site_id?), `index.html` work-assignments (`assigned_user_id=self&status=PENDING,OVERDUE&overdue_only=true`), `education.html` worker-complete(body edu_id/worker_id=self/phone=self/signature_data PNG dataURL/completed_at). **셋 다 이미 토큰 포함** → 서버 강제만 추가하면 됨.

---

## A. PHOTO — `POST /uploads/inspection-photo` (route rename 금지)

- **AUTH REQUIRED**: `current_user: dict = Depends(get_current_user)` (Optional 제거). 무토큰 → 401.
- **파일 검증**: `contents = await file.read()`; 빈 파일 400 유지; `ext = upload_service.validate_image_file(file, contents)` (5MB/magic/canonical). client `filename`/`content_type` 을 storage identity 로 신뢰 금지 — mime/ext 는 검증 결과만 사용.
- **context allowlist**: `{"inspect","construction_inspect","report"}` 등 확정 집합만 허용. UNKNOWN → **422**. context 문자열을 storage path identity 로 직접 신뢰하지 않되(allowlist 통과값만 경로에 사용).
- **object ownership**:
  - `inspection_id` 존재 시 UUID format 검사만 하지 말고 **실제 소유권 검증**: inspection → work_assignment/work_schedule → `assigned_user_id == current_user["id"]` 확인. foreign → **403**, 부재 → **404**. (검증 helper 는 inspection_sets_svc `_iss` 또는 work_assignments 조회로 구성. 실제 연결 컬럼은 Cursor 가 inspection→assignment 관계를 직독해 배선.)
  - `inspection_id` 미존재 시(report 등): authenticated user 만 허용, `record_id` 를 임의 foreign object 에 붙이지 않음(부재 시 record_id 미설정 + description 로그 유지).
  - caller `factory_id`/`site_id` 는 authorization fact 로 사용 금지. 회사/시설 scope 는 `current_user` DB fact(`company_id`/`factory_id`)에서 파생.
- **storage (company-docs private 유지)**:
  - path = `worker-photos/{context}/{yyyy-mm}/{uuid4}.{ext}` (기존 구조 유지, ext=검증값).
  - upload → PHOTO_BUCKET(`company-docs`).
  - **attachments 정본 = stable ref**: `file_url = f"company-docs/{storage_path}"` (기존의 get_public_url 결과 저장 제거). `uploaded_by = current_user["id"]`. `file_ext/mime_type = 검증값`. `record_id = inspection_id`(소유권 통과 시).
  - **응답 preview url = 단명 signed URL**: `supabase.storage.from_(PHOTO_BUCKET).create_signed_url(storage_path, <expiry초>)` 로 생성해 top-level `{status, url, data}` 의 `url` 에 실음(PWA 호환). signed URL 을 DB 정본으로 저장 금지.
  - ⚠️ **supabase-py 버전별 signed-url 메서드명/반환키 확인 필요**(`create_signed_url` 반환 dict 의 `signedURL`/`signed_url`). Cursor 가 설치 버전으로 실검증. private bucket 이라 종전 get_public_url 은 이미 비작동 URL 이었음 → stable-ref 전환은 회귀 아님. (read-side 소비자가 서명 URL 이 필요하면 별건. §81 write-side 범위 밖.)

## B. WORK ASSIGNMENTS — `GET /work-assignments`

- **AUTH REQUIRED**: `current_user: dict = Depends(get_current_user)` 추가(현재 Depends 전무). 무토큰 → 401.
- **subject = current_user["id"]**:
  - `assigned_user_id` 미지정 → `current_user["id"]` 로 강제 필터(전체 row 반환 금지).
  - `assigned_user_id` 지정 → `current_user["id"]` 와 동일하면 허용, 다르면 **403**.
- tenant-wide/admin bypass = 0. ADMIN consumer 없음 확인 → worker endpoint 는 자기 배정 전용으로 축소.
- `status`/`overdue_only`/`limit` 필터·응답 shape(`{status,data:{items,total}}`) 유지.

## C. EDUCATION COMPLETE (AUTH) — `POST /education/worker-complete`

- **AUTH REQUIRED**: `Depends(get_current_user)`. 무토큰/무인증 완료 = 금지(401).
- **effective user_id = current_user["id"]**:
  - `body.worker_id` 없음 → current_user.id. 있음+동일 → 허용. 있음+**foreign → 403**.
  - `body.phone` 있음 → server resolver(`_resolve_worker`) 로 users.id 해소; resolved != current_user.id → **403**; resolved 없음 → 403. phone/worker_id 는 authorization identity 아님.
- company/factory = **DB fact**(current_user.id → users 행). body 신뢰 금지(현행 유지).

## D. EDUCATION OBJECT VALIDATION

- `body.edu_id` = education_master.id(UUID). 서버에서:
  - `SELECT education_code FROM education_master WHERE id = body.edu_id AND is_active = true` → exact 1건.
  - 없음/비활성 → **404 EDUCATION_NOT_FOUND**.
- **canonical code 저장**: `education_history.education_code = master.education_code`(서버 조회값). **client edu_id UUID 를 education_code 로 저장 금지**(E12). 이 매핑을 테스트로 고정.

## E. EDUCATION ASSIGNMENT — 이번 §81 assignment 필수화 **금지**

- prod `education_assignment=0행`, PWA 는 master edu_id 기반(assignment_id 미전송). 필수화 시 정상 기능 전면 차단.
- §81 object gate = **AUTH 자기 identity + active master existence** 까지만. 교육 회차 identity(assignment.id 정본화)는 후속 별건.

## F. EDUCATION IDEMPOTENCY — code-level, **DDL=0**

- 금지: `UNIQUE(user_id, education_code)`(반복/정기 교육 정상 재이수 가능). ATOMIC 과장 선언 금지(동시 double-submit 완전 원자성은 DDL/receipt 없이 미보장 — 주석·테스트에 v1 한계 명시).
- **canonical completion date = server date**. `body.completed_at` 은 호환 입력으로 받되 **dedup identity 에 사용 금지**.
- **DEDUP KEY v1** = `current_user.id + canonical education_code + server completion date`.
  - INSERT 전 exact existing **COMPLETED** history 조회:
    - 존재 → INSERT 0 · 200 · `mode=REPLAY` · 기존 history id 반환.
    - 없음 → INSERT 1 · `mode=CREATED`.
  - "동일 교육 영구 중복 금지"가 아니라 **동일 날짜 retry/double-click dedup** 임을 주석·테스트 명시.

## G. SIGNATURE SECURITY

- `signature_data` = base64. decode 후: size ≤ 5MB, **magic MIME = image/png 만 허용**(JPEG/WebP 불필요; canvas `toDataURL('image/png')` 정합).
  - invalid base64 → 422/400 · non-PNG → **415** · oversize → **413**.
- storage = company-docs private. path = server-generated `signatures/education/{uuid4}.png`(client filename 개념 없음). 정본 저장 방식은 A 와 동일 원칙(stable ref).

## H. COMPANY / FACTORY

- `education_history.company_id/factory_id` = current_user.id → users DB fact(현행 유지). body 신뢰 금지.

---

## I. TEST MATRIX (pytest, service/endpoint 단위 · 모든 케이스 PASS 필요)

**PHOTO** — P1 무토큰→401 · P2 본인 inspection→성공 · P3 foreign inspection→403/404 · P4 무효 inspection→404 · P5 >5MB→413 · P6 invalid magic→415 · P7 filename `evil.exe`+PNG bytes→canonical `.png` · P8 unknown context→422 · P9 uploaded_by=current_user.id · P10 attachments.file_url=stable `company-docs/...` ref · P11 응답 url=signed/preview 이며 DB 정본 아님.

**WORK ASSIGNMENTS** — W1 무토큰→401 · W2 assigned_user_id 미지정→본인 row 만 · W3 본인 assigned_user_id→본인 row · W4 foreign assigned_user_id→403 · W5 무쿼리 전체 노출=0 · W6 status/overdue 필터 보존.

**EDUCATION AUTH** — E1 무토큰→401 · E2 worker_id 없음→current user · E3 본인 worker_id→성공 · E4 foreign worker_id→403 · E5 본인 phone→성공 · E6 foreign phone→403 · E7 미해소 phone→403.

**EDUCATION OBJECT** — E8 valid active master id→canonical code · E9 unknown master→404 · E10 inactive master→404 · E11 history.education_code=master.education_code · E12 raw client UUID 저장=0.

**EDUCATION RETRY** — E13 first→CREATED/INSERT 1 · E14 동일 user+code+server-date retry→REPLAY/INSERT 0 · E15 동일 code 타 날짜→글로벌 차단 안 됨.

**SIGNATURE** — E16 valid PNG→성공 · E17 invalid base64→reject · E18 non-PNG→415 · E19 >5MB→413.

**REGRESSION** — 기존 `GET /work-assignments/{id}/items` 소유권 PASS · worker auth PASS · worker PWA contract(응답 shape) PASS · 전체 회귀 스위트 PASS/0 fail.

---

## J. CHANGE BOUNDARY

- 예상 소스: `routers/worker_assets.py` · `services/upload_service.py`(public `validate_image_file` 노출만) · `tests/…`.
- **tai-admin/FE 변경 = 0** (직독 grounding 6 으로 확인: worker_id==users.id, 응답 shape 유지 → 불필요). API shape 때문에 최소 FE 수정이 불가피하면 이유+diff 제출 후 별도 승인(임의 확장 금지).
- DDL=0 · SQL artifact=0 · NEW RPC=0 · PROD SELECT=허용 · PROD DB MUTATION=0 · PROD HTTP MUTATION=0 · COMMIT/PUSH=허용 · MERGE=0 · DEPLOY=0.
- push 전 `git hash-object` 기록 → push 후 커밋 blob 대조(Korean-Unicode/dollar-quote drift 점검).

---

## SUBMIT (구현 후 이 양식으로 제출)

```
§81 IMPLEMENTATION REPORT
BASE = / HEAD = / BRANCH = / GOAL =
PHOTO   AUTH= OWNERSHIP= CONTEXT ALLOWLIST= MAX= MAGIC MIME= CANONICAL EXT= BUCKET= STABLE REF= PREVIEW=
WORK ASSIGNMENTS  AUTH= IDENTITY= NO-QUERY= FOREIGN ID= ALL-ROW EXPOSURE=
EDUCATION  AUTH= USER ID= PHONE= WORKER ID= MASTER CHECK= CANONICAL EDUCATION CODE= COMPANY/FACTORY= IDEMPOTENCY KEY= CREATED= REPLAY= SIGNATURE VALIDATION=
CHANGED FILES =
PHOTO TEST= ASSIGNMENT TEST= EDUCATION AUTH TEST= EDUCATION RETRY TEST= SIGNATURE TEST= REGRESSION=
DDL=0 NEW RPC=0 PROD DB MUTATION=0 PROD HTTP MUTATION=0 MERGE=0 DEPLOY=0
FINAL = / HARD STOP
```
