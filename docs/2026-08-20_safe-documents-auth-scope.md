# 작업지시서 — documents.py 인증·회사스코프 (Wave 1)

> 대상 `taiengineering/tai-api` `routers/documents.py` (v1.0.0, 현재 blob `6aea6801`, 4.9KB). 설계: `2026-08-20_safe-auth-scope-module-design.md`. 참조: §73·companies. 업무 로직(`services.document_svc`) 불변, 인증·스코프만 앞단 추가.

## 규율
- client `company_id`/`factory_id` 신뢰 금지(P13). 회사귀속은 토큰에서만.
- 관리자 판정은 헬퍼 내부 `_is_admin(ALL)`만.
- 전체 재작성 금지 — 아래 지점만 수술 편집.

## 변경 ① import (상단)
```python
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from db.supabase_client import get_supabase
from routers.auth import get_current_user
from services.company_scope import require_company_id, scoped_list_company, _ensure_own_company
```

## 변경 ② 업로드 (생성) — 토큰 회사 강제
`upload_document`·`upload_multiple`:
- 시그니처에 `current: dict = Depends(get_current_user)` 추가. 기존 `company_id: str = Form(...)`는 `Form(None)`으로 완화(클라 값 무시).
- 함수 본문 첫 줄에:
```python
    sb = get_supabase()
    company_id = require_company_id(current, sb)   # 무회사 403, 토큰 회사 강제
```
- 이후 `document_svc.upload_document(..., company_id=company_id, ...)`에 이 값 전달(기존 인자 이름 그대로, 값만 토큰 기반).

## 변경 ③ 목록·통계·만료 (조회) — 무회사 빈 결과
`list_documents`·`document_stats`·`expiring_documents`:
- 시그니처에 `current: dict = Depends(get_current_user)` 추가. 기존 `company_id: str = Query(...)`는 `Query(None)`으로 완화.
- 본문 첫 줄:
```python
    sb = get_supabase()
    scoped_cid, deny = scoped_list_company(current, sb, company_id)
    if deny:
        return {"status": "success", "data": [], "total": 0}   # list_documents
        # stats/expiring는 각 함수의 빈 반환형에 맞춰 빈 결과
    company_id = scoped_cid
```
- 이후 svc 호출에 `company_id=company_id`(스코프된 값) 전달.

## 변경 ④ 단건 (get/download/patch/delete) — 소유 확인
`get_document`·`download_document`·`update_document`·`delete_document`:
- 시그니처에 `current: dict = Depends(get_current_user)` 추가.
- 본문에서 **작업 수행 전** 문서 소유 확인:
```python
    sb = get_supabase()
    doc = await document_svc.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    _ensure_own_company(doc.get("company_id"), current, sb, "Document not found")
```
- get_document은 이미 doc를 조회하므로 그 결과를 재사용. download/patch/delete는 위 조회를 앞에 추가한 뒤 기존 로직 수행.
- **확인 필요(Cursor)**: `document_svc.get_document(doc_id)` 반환 dict에 `company_id`가 포함되는지 로컬 확인. 없으면 svc select에 `company_id` 추가.

## 변경 ⑤ by-entity — 회사 필터
`by_entity(table, record_id)`:
- `current: dict = Depends(get_current_user)` 추가.
- `get_attachments` 결과를 비-ALL이면 current 회사로 후필터(첨부 문서행의 company_id 기준). svc가 company_id를 반환하지 않으면 select 보강.
```python
    sb = get_supabase()
    data = await document_svc.get_attachments(table, record_id)
    from services.company_scope import _scope, _is_admin
    if not _is_admin(_scope(sb, current.get("role_code"))):
        cid = current.get("company_id")
        data = [d for d in (data or []) if d.get("company_id") == cid]
```

## 배포 후 (수행자 보고)
- commit·origin/main sha, Railway SUCCESS, `GET /health` 200
- 블랙박스: 비로그인 `GET /documents?company_id=x` → **401**; 비로그인 `GET /documents/{임의}/download` → **401**

## 기획창 사후 검증 (본 창)
- import 4줄, upload 2개·list/stats/expiring 3개·단건 4개·by-entity 스코프 배선 — GET 대조.
- get_document company_id 포함 여부 확인 결과 확인.
