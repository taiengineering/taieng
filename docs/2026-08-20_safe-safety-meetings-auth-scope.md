# 작업지시서 — safety_meetings.py 인증·회사스코프 (Wave 2)

> 대상 `taiengineering/tai-api` `routers/safety_meetings.py` (v1.2.1, blob `5bd9ee4b`, 17.5KB). 설계: `2026-08-20_safe-auth-scope-module-design.md`. 참조: companies·documents. 테이블 `safety_committee_meetings`(+attendees). 업무 로직·참석자 헬퍼·주기준수 계산 불변, 인증·스코프만 앞단.

## 규율
- client `company_id`/`factory_id` 신뢰 금지(P13). 회사귀속은 토큰에서만.
- 관리자 판정은 헬퍼 내부 `_is_admin(ALL)`만. 공개 엔드포인트 없음 → 전 엔드포인트 로그인.
- 전체 재작성 금지 — 아래 지점만 수술 편집. `_is_uuid` 가드는 유지(가드 뒤에 스코프).

## 변경 ① import (상단)
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from routers.auth import get_current_user
from services.company_scope import require_company_id, scoped_list_company, _ensure_own_company
```

## 변경 ② 생성 — 토큰 회사 강제
`create_meeting(body)` → `create_meeting(body, current: dict = Depends(get_current_user))`:
- 본문 `supabase = get_supabase()` 다음:
```python
    body.company_id = require_company_id(current, supabase)   # 무회사 403, 클라 company_id 무시
```
(이후 row["company_id"] = body.company_id 그대로 사용)

## 변경 ③ 목록·주기현황 — 무회사 빈 결과
`list_meetings(...)` · `get_meeting_schedule(...)`:
- 시그니처에 `current: dict = Depends(get_current_user)` 추가.
- 본문 `supabase = get_supabase()` 다음:
```python
    scoped_cid, deny_all = scoped_list_company(current, supabase, company_id)
    if deny_all or not scoped_cid:
        # list_meetings:
        return {"status": "success", "data": {"items": [], "total": 0, "page": page, "size": size, "total_pages": 0}}
        # get_meeting_schedule: 빈 준수현황
        # return {"status": "success", "data": {"company_id": None, "year": target_year, "safety_committee": [], "contractor_council": [], "summary": {"committee_compliant":0,"committee_overdue":0,"council_compliant":0,"council_overdue":0}}}
    company_id = scoped_cid
```
- 이후 쿼리 `.eq("company_id", company_id)`에 스코프된 값 사용. (schedule은 이미 company_id로 필터하므로 company_id만 치환.)

## 변경 ④ 단건 조회 — 소유 확인
`get_meeting(meeting_id)`:
- `current` 추가. `_is_uuid` 가드 뒤, 조회 후:
```python
    _ensure_own_company(record.get("company_id"), current, supabase, "회의록을 찾을 수 없습니다.")
```
(record는 이미 select("*")로 company_id 포함. return 직전에 배치.)

## 변경 ⑤ 단건 변경 — 소유 확인 선행 (hard delete 포함)
`update_meeting` · `attach_file` · `complete_meeting` · `delete_meeting`:
- 각 `current: dict = Depends(get_current_user)` 추가.
- 본문 **첫 DB 작업 전**(update/delete/attach 직전)에 소유 확인 삽입:
```python
    supabase = get_supabase()
    _own = supabase.table("safety_committee_meetings").select("company_id").eq("id", meeting_id).limit(1).execute()
    if not _own.data:
        raise HTTPException(status_code=404, detail="회의록을 찾을 수 없습니다.")
    _ensure_own_company(_own.data[0].get("company_id"), current, supabase, "회의록을 찾을 수 없습니다.")
```
- `update_meeting`은 `_is_uuid` 가드 뒤에 배치. 기존 로직(참석자 교체·payload update)은 그대로.
- **delete_meeting(hard delete)**: 위 소유 확인을 delete 직전에 반드시 선행 → 타사 회의록 삭제 404.

## 배포 후 (수행자 보고)
- commit·origin/main sha, Railway SUCCESS, `GET /health` 200
- 블랙박스: 비로그인 `GET /safety-meetings` → **401**; 비로그인 `DELETE /safety-meetings/{임의uuid}` → **401**

## 기획창 사후 검증 (본 창)
- import 3줄, create require_company_id, list·schedule scoped(빈결과), get 소유확인, update·attach·complete·delete 소유확인 선행 — GET 대조.
- delete가 소유확인 뒤에만 실행되는지(hard delete 안전) 확인.
