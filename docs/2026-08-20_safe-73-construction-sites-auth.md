# WORKORDER — §73 construction_sites 인증·회사스코프 (v2 · 공통모듈 재사용)

> 발행: 기획창 2026-08-20 (v2, v1 폐기). 실행: Cursor 권장(3파일·핵심 보안 라우터). 정본 모듈: `services/company_scope.py`(이미 존재). §80 `diagnosis.py` 와 동일 계열.
> **v1과의 차이**: 손으로 만든 `_site_company`/`_assert_scope` 폐기 → 이미 있는 공통 모듈 헬퍼 재사용. + `run_list_query` None-skip 가드 추가.

## 원인 (검증 완료)
`construction_sites_router.py` 8개 엔드포인트 전부 무인증. `SiteCreate.company_id: str`가 필수 클라 입력 → `build_site_create_payload`가 `body.model_dump()` 그대로 insert(P13). 목록은 클라 `company_id` 파라미터 그대로.

## 재사용할 공통 모듈 (신설 아님 — 이미 있음)
`from routers.auth import get_current_user`
`from services.company_scope import _is_admin, _scope, _ensure_own_company, _forced_company_id`
- `_is_admin(_scope(sb, role))` → `scope_type=="ALL"`(플랫폼 총관리자)만 True. 회사 안전관리자는 자기 회사로 스코프됨.
- `_ensure_own_company(res_company_id, current, sb, not_found)` → 비-ALL이 타사/무회사면 **404**(무회사=token_cid None도 404).
- `_forced_company_id(current, sb, company_id)` → 비-ALL이면 토큰 company_id 강제, ALL이면 클라 값 유지.

## ★ 결정적 nuance — 목록 None-skip
`services/construction_svc.run_list_query`는 `if value is None: continue` — **None 필터를 건너뛴다.** 따라서 무회사(company_id=None) 비-ALL에게 `_forced_company_id` 결과(None)를 그대로 넘기면 **전 회사가 노출된다.** 목록은 "무회사 → 빈 결과"를 라우터에서 명시 처리해야 한다.

## 변경 ① schemas/construction.py
- `SiteCreate.company_id: str` → `company_id: Optional[str] = None` (서버가 토큰에서 주입, 클라 값은 무시/덮어씀).

## 변경 ② services/construction_sites_svc.py
- `build_site_create_payload(body, now_iso_fn, company_id)` 파라미터 추가 → 본문에서 `data["company_id"] = company_id` 로 **강제 덮어쓰기**(body 값 무시).
- `list_sites(...)` 시그니처 불변.

## 변경 ③ routers/construction_sites_router.py (엔드포인트별)
공통: 각 함수 인자에 `current: dict = Depends(get_current_user)` 추가.

- **POST /sites** — `company_id = current.get("company_id")`; `if not company_id: raise HTTPException(403, "회사 등록이 필요합니다.")`; `build_site_create_payload(body, _now_iso, company_id)`. (body.company_id 무시.)
- **GET /sites** (목록) —
  ```python
  scoped_cid = _forced_company_id(current, supabase, company_id)
  if not _is_admin(_scope(supabase, current.get("role_code"))) and not scoped_cid:
      return {"status": "success", "data": {"items": [], "total": 0, "page": page, "size": size, "total_pages": 0}}
  # scoped_cid 를 list_sites 의 company_id 로 전달
  ```
  (무회사 비-ALL → 빈 결과. None-skip 노출 차단.)
- **GET /sites/{id}** · **PATCH** · **DELETE** · **GET /sites/{id}/stats** · **POST /sites/{id}/diagnose** · **POST /sites/{id}/generate-schedules** —
  site_id 처리 전에 소유 현장 조회 후 가드:
  ```python
  srow = supabase.table("construction_sites").select("company_id").eq("id", site_id).limit(1).execute()
  if not srow.data:
      raise HTTPException(404, "현장을 찾을 수 없습니다.")
  _ensure_own_company(srow.data[0].get("company_id"), current, supabase, "현장을 찾을 수 없습니다.")
  ```
  (무회사/타사 → 404. diagnose·generate 의 자동로직은 이 가드 통과 후 그대로.)

## 하지 말 것 (회귀 금지)
- 클라 `company_id`/`factory_id` 신뢰 금지(P13). 회사귀속은 토큰에서만.
- 관리자 판정은 `_is_admin(_scope(...))` 로만. role_code 직접 비교 금지.
- `_site_company`/`_assert_scope` 같은 개별 헬퍼 새로 만들지 말 것 — 공통 모듈만 사용(모듈화 목적).
- 자동 진단·일정 로직(`create_factory_for_site`·`auto_diagnose_and_schedule`) 불변, 인증만 앞에.
- 목록 무회사 케이스에서 None 을 `list_sites` 로 넘기지 말 것(전체 노출).

## 검증 (확인 한 줄)
1. 비로그인 `POST /construction/sites` → 401.
2. 로그인+회사있음, body에 타사 company_id → 저장 행 company_id가 **내 회사**면 통과.
3. 회사 미등록 계정으로 `GET /construction/sites` → **0건**이면 통과(전체 아님).
4. 타사 현장 UUID `DELETE` → 404. 자사 현장 삭제 성공.
5. 회사있는 계정 `GET /construction/sites` → 내 회사 현장만.

## 맥락
§73은 "전체 적용(모듈화)"의 **첫 케이스**. 이 라우터가 공통 모듈을 안 쓰던 것뿐. 완료 후 나머지 무모듈 safe 라우터 전수 스캔 → 동일 패턴 일괄 적용.
