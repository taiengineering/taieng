# WO-CREATEDBY-FIX-001 — persist created_by 보강 (운영 안정화)

**작성일:** 2026-06-27 | **상태:** 구현 완료 → **PR #113 리뷰 대기**
**PR:** https://github.com/taiengineering/tai-api/pull/113 (branch `fix/persist-created-by`)
**목적:** persist 시 `factory_diagnosis_results.created_by` 정상 저장 → `diagnosis_transform` 인증 조회 정상화. 기능 추가 아니라 권한 컴럼 보강.

---

## TASK-001 — 조사 (읽기 전용)
```
- 기존 _persist_result_data는 created_by 미설정 → null.
- /persist, /from-instances 엔드포인트는 인증 의존성 없음 → 무인증 호출.
- diagnosis_transform: created_by == str(current_user["id"]) (= public.users.id, uuid) 비교.
- 컬럼 타입: factory_diagnosis_results.created_by = uuid, public.users.id = uuid (일치).
- get_current_user는 필수-인증(토큰 없으면 401 raise). 옵션 변형 없음.
```

## 수정 파일 목록
```
routers/obligation_adapter.py  (단일 파일, PR #113, v1.3.2)
  + _optional_user_id(authorization)   기존 get_current_user(lazy import) 재사용.
                                        유효 토큰→users.id, 없음/무효→None. 새 판단 로직 0.
  ~ _persist_result_data(created_by=None)  created_by 있으면 row에만 추가, 나머지 불변.
  ~ /persist            authorization: Optional[str] = Header(None) 추가 → created_by 전달.
  ~ /from-instances     authorization: Optional[str] = Header(None) 추가 → created_by 전달.
```

## TASK-002~005 — 구현 원칙 준수
```
TASK-002  인증 사용자 존재 → created_by = users.id 저장.
TASK-003  서비스/시스템(토큰 없음) → _optional_user_id None → created_by 미설정(기존 동작, 억지 ID 금지).
TASK-004  build_result_data→persist 흐름 불변. persist 직전 created_by만 추가.
TASK-005  result_data/obligations/rule_count/verdict/category/reason/description 불변 — 권한 컬럼만.
```

## TASK-006 — 회귀
```
무인증 호출(현 curl)  → created_by 미설정 → 기존 동작 바이트 동일.
인증 호출(Bearer)   → created_by=users.id → diagnosis_transform 인증 조회 성공.
raw 171 / display 169(Dedup) 영향 0. HTML(anonymous_diagnosis_results)·SaaS 영향 0.
```

## 머지 후 검증 절차
```
1. PR #113 머지 → Railway 자동배포
2. POST /auth/login (admin@tai.com / tai1234!) → access_token
3. POST /obligation-adapter/from-instances/{factory_id}?persist=true
     헤더 Authorization: Bearer <token>  → diagnosis_id
4. GET /diagnosis/transform/latest/{factory_id} (동일 토큰) → 200 + obligations 169
5. (Claude) Supabase로 신규 row.created_by = 해당 users.id 확인
```

---

*WO-CREATEDBY-FIX-001 — created_by 보강. get_current_user 재사용, 권한 컬럼만 추가, 기존 파이프·Data Contract 불변. PR #113 리뷰 대기.*
