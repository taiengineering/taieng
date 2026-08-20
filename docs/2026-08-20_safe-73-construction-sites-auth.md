# WORKORDER — §73 construction_sites 인증·회사스코프 (무인증 해소)

> 발행: 기획창 2026-08-20. 실행: Cursor(다중파일·핵심 보안 라우터, factories.py 선례와 동일 취급). 정답지: §80 `routers/diagnosis.py` v2.1.0 + `services/company_scope.py`.

## 원인 (검증된 사실)
`routers/construction_sites_router.py` 8개 엔드포인트 전부 무인증(`Depends(get_current_user)` 부재). 게다가 `schemas/construction.py` `SiteCreate.company_id: str` 가 **필수 클라이언트 입력**이고 `services/construction_sites_svc.build_site_create_payload` 가 `body.model_dump()` 를 그대로 insert → 클라이언트가 보낸 `company_id` 검증 없이 저장(P13 위반). `list_sites` 도 클라이언트 `company_id` 파라미터를 그대로 필터.

## 적용 범위 (★ 확인 필요 — 기본값: 전체 잠금)
지시서 원문 §73은 POST만 지목하나, **라우터 전체가 열려 있어 POST만 잠그면 DELETE·PATCH·조회가 남는다.** 기본 설계는 **전 엔드포인트 잠금**. POST만 원하면 회신 시 축소.

## 변경 ① schemas/construction.py
- `SiteCreate.company_id: str` → `company_id: Optional[str] = None` (서버가 토큰에서 주입, 클라이언트 값 무시).

## 변경 ② services/construction_sites_svc.py
- `build_site_create_payload(body, now_iso_fn, company_id)` 로 파라미터 추가.
  - 본문 첫 줄 뒤에 `data["company_id"] = company_id` 로 **강제 덮어쓰기**(body 값 무시, P13).
- `list_sites(...)` 는 시그니처 불변 — 라우터가 인증된 company_id 를 넘긴다.

## 변경 ③ routers/construction_sites_router.py
공통 import (diagnosis.py 와 동일):
```python
from fastapi import Depends
from routers.auth import get_current_user
from services.company_scope import _is_admin, _scope
```
헬퍼(파일 상단):
```python
def _site_company(supabase, site_id):
    r = supabase.table("construction_sites").select("company_id").eq("id", site_id).limit(1).execute()
    if not r.data:
        raise HTTPException(status_code=404, detail="현장을 찾을 수 없습니다.")
    return r.data[0].get("company_id")

def _assert_scope(supabase, current, company_id):
    if _is_admin(_scope(supabase, current.get("role_code"))):
        return
    if str(company_id) != str(current.get("company_id")):
        raise HTTPException(status_code=403, detail="타 회사 현장에 접근할 수 없습니다.")
```
엔드포인트별:
- **POST /sites** — `current = Depends(get_current_user)` 추가. `build_site_create_payload(body, _now_iso, current.get("company_id"))` 로 호출(인증 회사 주입). body.company_id 무시.
- **GET /sites** (목록) — `current` 추가. 비관리자면 `company_id = current.get("company_id")` 로 **강제**(쿼리 파라미터 무시). 관리자면 파라미터 허용.
- **GET /sites/{id}** · **PATCH** · **DELETE** · **GET /sites/{id}/stats** · **POST /sites/{id}/diagnose** · **POST /sites/{id}/generate-schedules** — 각 함수에 `current` 추가하고, site_id 처리 전 `_assert_scope(supabase, current, _site_company(supabase, site_id))` 호출.

## 하지 말 것 (회귀 금지)
- client 가 보낸 `company_id`/`factory_id` 를 신뢰해 스코프 완화 금지(P13).
- 관리자 판정은 `_is_admin(_scope(...))` 로만. role_code 문자열 직접 비교 금지.
- 자동 진단·일정(`create_factory_for_site`·`auto_diagnose_and_schedule`) 로직 불변 — 인증만 앞에 추가.
- size 상한·다른 라우터 변경 금지.

## 검증 (확인 한 줄)
1. 비로그인 `POST /construction/sites` → 401/403 이면 통과.
2. 로그인 후 body 에 **타 회사 company_id** 넣어 생성 → 저장된 행 company_id 가 **내 회사**면 통과(덮어쓰기 확인).
3. 타 회사 현장 UUID 로 `DELETE /construction/sites/{id}` → 403 이면 통과. 자사 현장은 삭제 성공.
4. 로그인 후 `GET /construction/sites` → **내 회사 현장만** 나오면 통과.

## LEDGER
§73(construction/sites 무인증). §80 과 동일 종류이나 라우터 전체가 대상. 관련: §59·§60·§62(건설 필드) 는 별건, 본 지시서는 인증·스코프만.
