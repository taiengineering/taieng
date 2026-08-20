# 작업지시서 — companies.py 인증·회사스코프 (Wave 1)

> 대상 `taiengineering/tai-api` `routers/companies.py` (v2.2.0, 현재 blob `6190e758`). 설계: `2026-08-20_safe-auth-scope-module-design.md`. 참조 구현: §73 `construction_sites_router.py`. **엔드포인트별 배선**(라우터 단위 게이트 금지 — 공개 등록 유틸 혼재).

## 규율
- 업무 로직(국세청 호출·온보딩·파일 업로드·중복확인) **불변**. 인증·스코프만 앞단 추가.
- client `company_id`/id 신뢰 금지(P13). by-id는 path의 `company_id`를 토큰과 대조.
- 관리자 판정은 `_ensure_own_company`/`_require_admin` 내부의 `_is_admin(ALL)`만. role_code 직접 비교 금지.
- 전체 재작성 금지 — 아래 지점만 수술 편집.

## 변경 ① import (파일 상단)
```python
# 기존:  from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from routers.auth import get_current_user
from services.company_scope import _ensure_own_company, _require_admin
```

## 변경 ② 공개 유지 (수정 없음)
- `POST /nts-verify` · `POST /nts-status` · `GET /check-biz`
- 등록 전 유틸이므로 인증 붙이지 않는다.

## 변경 ③ 로그인만 (스코프 없음 — 회사 생성 전)
각 함수 시그니처에 `current` 파라미터만 추가. 본문 로직 불변.
- `onboarding(req: OnboardingBody)` → `onboarding(req: OnboardingBody, current: dict = Depends(get_current_user))`
- `create_company(req: CompanyCreate)` → `create_company(req: CompanyCreate, current: dict = Depends(get_current_user))`

## 변경 ④ 어드민 전체목록 — ALL만
- `get_companies(...)` 시그니처 끝에 `current: dict = Depends(get_current_user)` 추가.
- 함수 본문 `supabase = get_supabase()` **다음 줄**에 삽입:
```python
    _require_admin(current, supabase)   # 전체 목록은 플랫폼 총관리자(ALL)만
```

## 변경 ⑤ by-id 전부 — 로그인 + 자기 회사 대조
아래 **모든** 엔드포인트: ①시그니처에 `current: dict = Depends(get_current_user)` 추가 ②`supabase = get_supabase()` **직후**에 가드 삽입.
```python
    _ensure_own_company(company_id, current, supabase, "사업장을 찾을 수 없습니다")
```
대상 함수(패스에 `{company_id}` 있는 전부):
- `get_company` (GET /{company_id})
- `update_company` (PATCH /{company_id})
- `delete_company` (DELETE /{company_id})
- `get_company_users` (GET /{company_id}/users)
- `get_company_factories` (GET /{company_id}/factories)
- `get_company_contacts` (GET /{company_id}/contacts)
- `get_company_contracts` (GET /{company_id}/contracts)
- `add_company_contact` (POST /{company_id}/contacts)
- `update_company_contact` (PATCH /{company_id}/contacts/{contact_id})
- `delete_company_contact` (DELETE /{company_id}/contacts/{contact_id})
- `add_company_file` (POST /{company_id}/files)
- `upload_company_file` (POST /{company_id}/upload-file) — async, `current` 파라미터는 `file_type: str = Form(...)` **뒤**에 둔다(Depends는 위치 무관하나 Form/File 뒤 권장)
- `delete_company_file` (DELETE /{company_id}/files/{file_id})
- `set_contract_url` (PATCH /{company_id}/contract-url)

주의: `update_company`·`delete_company` 등은 본문에서 다시 `existing = ...single()`으로 존재 확인을 하는데, 가드를 **그 앞**(supabase 직후)에 둬야 타사 자원이 404로 먼저 막힌다.

## 배포 후 (지시서 수행자 보고 항목)
- commit sha, origin/main sha
- Railway `tai-api-prod` SUCCESS, `GET /health` 200
- 블랙박스: 비로그인 `GET /companies/{임의uuid}` → **401**; 비로그인 `GET /companies`(목록) → **401**; `GET /companies/check-biz?business_number=…` → **200**(공개 유지 확인)

## 기획창 사후 검증 (본 창)
- import 3줄 반영, 공개 3엔드포인트 무변경, by-id 14개 가드 삽입, get_companies `_require_admin`, create/onboarding 로그인만 — GET으로 대조.
- **별도 플래그(수정 아님)**: `onboarding`/`create_company`가 `users.company_id`를 세팅하지 않으면 등록 직후 자기 회사 조회가 404. 등록 플로우 링크 여부를 별건으로 확인.
