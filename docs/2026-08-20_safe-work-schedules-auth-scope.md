# 작업지시서 — work_schedules.py 인증·회사스코프 (Wave 2)

> 대상 `taiengineering/tai-api` `routers/work_schedules.py` (v1.2.4, blob `dbbf1b2d`, 14.5KB). 설계: `2026-08-20_safe-auth-scope-module-design.md`. 참조: companies·documents. 테이블 `work_schedules`(+`work_assignments` 동기화). **생성 없음(엔진 생성)** — 조회·변경 스코프만. 업무 로직(`_apply_one_update`·assignments 동기화·confirm 계산) 불변.

## 규율
- client id/`company_id`/`factory_id` 신뢰 금지(P13). 소유는 행의 company_id로 확인.
- 관리자 판정은 헬퍼 내부 `_is_admin(ALL)`만. 공개 엔드포인트 없음 → 전 엔드포인트 로그인.
- `_is_uuid` 가드 유지. 전체 재작성 금지 — 아래 지점만.

## 변경 ① import (상단)
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from routers.auth import get_current_user
from services.company_scope import (
    scoped_list_company, _ensure_own_company, _ensure_factory_own, _scope, _is_admin,
)
```

## 변경 ② 배치 소유필터 헬퍼 (파일 내 신설)
`_apply_one_update` 아래에 추가:
```python
def _owned_ids(supabase, ids, current):
    """비-ALL: 자기 회사 소유 schedule id 집합만. ALL: 전체 그대로."""
    if _is_admin(_scope(supabase, current.get("role_code"))):
        return set(ids)
    cid = current.get("company_id")
    if not cid or not ids:
        return set()
    res = supabase.table("work_schedules").select("id").in_("id", list(ids)).eq("company_id", cid).execute()
    return {r["id"] for r in (res.data or [])}
```

## 변경 ③ 목록 — 무회사 빈 결과
`get_work_schedules(...)`:
- 시그니처 끝에 `current: dict = Depends(get_current_user)` 추가.
- `supabase = get_supabase()` 다음:
```python
    scoped_cid, deny_all = scoped_list_company(current, supabase, company_id)
    if deny_all or not scoped_cid:
        return {"status": "success", "data": {"items": [], "total": 0, "page": page, "size": size, "total_pages": 0}}
    company_id = scoped_cid
```
- 이후 `if company_id: q = q.eq("company_id", company_id)`는 이제 항상 스코프된 값으로 필터.

## 변경 ④ 공장별·확정 — 시설 소유 확인
`get_factory_work_schedules(factory_id)` · `confirm_schedules(factory_id, body)`:
- `current: dict = Depends(get_current_user)` 추가.
- `supabase = get_supabase()` 다음 첫 줄:
```python
    _ensure_factory_own(supabase, factory_id, current)   # 타사 시설 404
```

## 변경 ⑤ 점검세트별 — 자사 후필터
`get_inspection_set_work_schedules(inspection_set_id)`:
- `current` 추가. 조회 후 반환 전:
```python
    data = result.data or []
    if not _is_admin(_scope(supabase, current.get("role_code"))):
        cid = current.get("company_id")
        data = [d for d in data if d.get("company_id") == cid]
    return data
```

## 변경 ⑥ 단건 조회 — 소유 확인
`get_work_schedule(schedule_id)`:
- `current` 추가. `_is_uuid` 가드 뒤, 조회 후:
```python
    if not result.data:
        raise HTTPException(status_code=404, detail="일정을 찾을 수 없습니다")
    _ensure_own_company(result.data[0].get("company_id"), current, supabase, "일정을 찾을 수 없습니다")
    return result.data
```

## 변경 ⑦ 단건 변경 — 소유 확인 선행
`patch_work_schedule(schedule_id, body)`:
- `current` 추가. `_is_uuid` 가드 뒤, `_apply_one_update` **전**:
```python
    _own = supabase.table("work_schedules").select("company_id").eq("id", schedule_id).limit(1).execute()
    if not _own.data:
        raise HTTPException(status_code=404, detail="일정을 찾을 수 없습니다")
    _ensure_own_company(_own.data[0].get("company_id"), current, supabase, "일정을 찾을 수 없습니다")
```

## 변경 ⑧ 배치 변경 — id별 소유필터
`batch_update_schedules(body)` · `bulk_assign_schedules(body)`:
- `current: dict = Depends(get_current_user)` 추가.
- `supabase = get_supabase()` 다음, 루프 전:
```python
    # batch_update:
    owned = _owned_ids(supabase, [it.id for it in body.updates], current)
    # bulk_assign:
    owned = _owned_ids(supabase, body.ids, current)
```
- 루프 안에서 대상 id가 owned가 아니면 skip:
```python
    # batch_update 루프 첫 줄:
    if item.id not in owned:
        continue
    # bulk_assign 루프의 _is_uuid 체크 다음:
    if sid not in owned:
        continue
```
→ 타사 일정은 변경되지 않음(조용히 skip, updated 카운트에서 제외).

## 배포 후 (수행자 보고)
- commit·origin/main sha, Railway SUCCESS, `GET /health` 200
- 블랙박스: 비로그인 `GET /work-schedules` → **401**; 비로그인 `PATCH /work-schedules/batch-update` → **401**

## 기획창 사후 검증 (본 창)
- import, `_owned_ids` 신설, 목록 scoped, factory·confirm `_ensure_factory_own`, inspection-set 후필터, 단건 조회·변경 소유확인, batch·bulk owned 필터 — GET 대조.
- batch/bulk가 타사 id를 skip하는지(소유필터) 확인.
