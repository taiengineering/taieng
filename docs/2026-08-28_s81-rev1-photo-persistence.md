# §81 REV-1 — WORKER PHOTO PERSISTENCE CONTRACT · 작업지시서 (Cursor)

- REPO = taiengineering/tai-api
- PRE HEAD = `9b3e897f2bf920420df0a56f906d43c5e44848f4` (branch `s81/worker-assets-auth`, parent bae1349b)
- BRANCH = `s81/worker-assets-auth` (RENAME=0, 현재 이름 수용) · GOAL = `G-mtce7l8v-ab95bd`
- SCOPE = **PHOTO contract만**. 권한 = SOURCE EDIT + TEST + COMMIT/PUSH. MERGE=0 · DEPLOY=0 · DDL=0 · NEW RPC=0 · PROD MUTATION=0.
- 판정 배경 = GPT REVISE/merge HOLD. AUTH/assignment/education 3축 PASS. PHOTO 축 2 blocker + ref format + preview-failure.

## FROZEN (건드리지 말 것)
- work-assignment AUTH · education AUTH/object/idempotency · `services/upload_service.py`(9b3e897f 그대로) · frontend(tai-admin).

---

## 0. 직독 GROUNDING (tai-admin ref cb47d468, 실 PWA 콜러 확정)

3 콜러 전부 `TAI.uploadPhoto(...)` 반환 `up.url`을 `photo_urls[]`에 넣어 **업무 payload에 영속**:
- `vue3/public/app/inspect.html` (산업+건설 겸용, isCon 분기): `uploadPhoto(file,'inspection',{factory_id})` → `photo_urls.push(up.url)` → `POST /worker-check/submit` body.items[].photo_urls.
- `vue3/public/app/construction_inspect.html`: `uploadPhoto(file,'inspection',{factory_id})` → 동일 → `/worker-check/submit`.
- `vue3/public/app/report.html`: `uploadPhoto(file,'report',{factory_id,site_id})` → `photo_urls.push(up.url)` → `POST /safety-reports` body.photo_urls.

확정 사실:
1. 실제 context 값 = **`"inspection"` / `"report"`** 뿐. `"inspect"`/`"construction_inspect"` 는 **실 소비자 없음**.
2. `up.url` = 업무 데이터에 영구 저장됨 → top-level `url` 은 **PERSISTENCE REF(stable)** 이어야 하며 만료 signed URL 금지.
3. 세 콜러 모두 `inspection_id` **미전송**(ids=factory_id/site_id만) → 소유권 분기는 latent(악의적 클라이언트 대비 유지), happy-path 는 "inspection_id 미존재=인증만" 분기.
4. FE 는 `up.url` 만 읽음(로컬 미리보기는 업로드 전 dataURL 썸네일) → **top-level url 을 stable ref 로 바꾸면 FE 수정 0 으로 올바른 영속화**.

---

## 1. CONTEXT ALLOWLIST (worker_assets.py)

```
PHOTO_CONTEXTS = frozenset({"inspection", "report"})
```
- 현재 `{"inspect","construction_inspect","report"}` 는 실 context `"inspection"` 을 422 로 막음 → **merge blocker**. 위로 교체.
- 실 소비자 없는 `"inspect"`,`"construction_inspect"` 임의 허용 금지. UNKNOWN → 422 유지.

## 2. STABLE REF (canonical, 점검영역 확정 형식)

```
def _stable_ref(storage_path: str) -> str:
    return f"storage://{PHOTO_BUCKET}/{storage_path}"
```
- 즉 `storage://company-docs/<storage_path>` (현재 `company-docs/<path>` → `storage://` prefix 추가).
- `attachments.file_url` = 이 stable ref.
- education 서명 memo 도 같은 `_stable_ref` 를 쓰므로 자동으로 `storage://company-docs/signatures/education/<uuid>.png` 로 통일(= GPT R12). education 로직/dedup/auth 는 무변경, ref 문자열 형식만 바뀜.

## 3. RESPONSE CONTRACT (top-level url = persistence)

```
return {
    "status": "success",
    "url": stable_ref,                       # ← preview 아님. PWA 가 photo_urls 에 저장하는 정본
    "data": {
        "url": stable_ref,
        "preview_url": preview_or_none,      # signed URL 또는 null/""
        "file_name": file_name,
        "size": len(contents),
    },
}
```
- top-level `url` = `data.url` = **stable_ref**.
- `data.preview_url` = signed preview(있으면) / 실패 시 null 또는 "".
- signed URL 을 attachments / inspection result / report business payload / education history 정본으로 저장 금지.

## 4. SIGNED PREVIEW FAILURE (비치명적)

- storage upload + attachments insert **성공 후** signed preview 생성만 실패 → **500 금지**.
  - `preview_url = None`(또는 "") 로 두고 **success 반환**.
- 이유: 정본(stable ref)은 이미 저장됨. 500 반환 시 client retry → 중복 업로드/attachment. signed preview 는 convenience, stable ref 가 SoT.
- 주의: storage upload 실패·attachments insert 실패는 **기존대로 500 유지**(정본 저장 실패이므로).

## 5. FRONTEND

- **FRONT CHANGE = 0**. FE 는 `up.url` 만 읽어 photo_urls 에 저장하므로, backend top-level url 을 stable ref 로 바꾸면 그대로 올바른 영속. 로컬 미리보기는 업로드 전 dataURL 이라 signed preview 불요.

## 6. TEST (worker_assets 테스트 파일에 REV-1 반영 + 기존 photo 계약 테스트 갱신)

신규/갱신:
- R1 context="inspection" → accepted
- R2 context="report" → accepted
- R3 context="inspect" → 422 reject
- R4 context="construction_inspect" → 422 reject
- R5 stable ref exact = `storage://company-docs/...`
- R6 attachments.file_url = stable ref
- R7 response top-level url = stable ref
- R8 response data.url = stable ref
- R9 response data.preview_url = signed URL
- R10 signed preview 생성 실패 → upload success · top-level url = stable ref · attachment canonical 유지(500 아님)
- R11 attachments 에 signed URL 저장 안 됨(file_url 에 "signed"/"http" 없음)
- R12 education 서명 memo = `storage://company-docs/...` ref

**기존 §81 photo 테스트 갱신 필수**(현재 old contract 가정 → REV-1 계약으로 수정):
- 기존 P2(top-level url 이 `https://signed...` 로 시작) → **stable ref `storage://company-docs/worker-photos/...`** 로 변경.
- 기존 P10(`file_url == "company-docs/%s"`) → **`storage://company-docs/%s`** 로 변경.
- 기존 P11(top-level url = signed) → top-level url = stable ref, signed 는 `data.preview_url` 로 이동해 검증.
- 기존 E16(memo startswith `company-docs/signatures/...`) → `storage://company-docs/signatures/...`.

REGRESSION(무변경 확인): §81 AUTH(P1/W1/E1) · assignment(W2–W6) · education auth/object/retry(E2–E15) · signature(E17–E19) · items 소유권(R1–R4 items) · contract shape · import-guard(get_public_url 부재) 전부 PASS.

## 7. BOUNDARY

- SOURCE CHANGE = `routers/worker_assets.py` + 관련 tests only. `services/upload_service.py` = FROZEN(9b3e897f). frontend = 0.
- DDL=0 · NEW RPC=0 · PROD MUTATION=0 · MERGE=0 · DEPLOY=0. push 전 `git hash-object` 기록 → 커밋 blob 대조.

---

## SUBMIT
```
§81 REV-1
PRE HEAD = 9b3e897f... / NEW HEAD = / PARENT =
PHOTO_CONTEXTS = / STABLE REF = / TOP-LEVEL URL = / DATA.URL = / PREVIEW_URL = / PREVIEW FAILURE =
INSPECTION PWA CONTRACT = / CONSTRUCTION PWA CONTRACT = / REPORT PWA CONTRACT =
AUTH REGRESSION = / ASSIGNMENT REGRESSION = / EDUCATION REGRESSION = / PHOTO TEST = / TOTAL TEST =
FRONT CHANGE = 0 / DDL = 0 / NEW RPC = 0 / PROD MUTATION = 0 / MERGE = 0 / DEPLOY = 0
HARD STOP
```
