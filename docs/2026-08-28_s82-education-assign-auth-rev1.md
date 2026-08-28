# §82 EDUCATION ASSIGNMENT AUTH — Phase A **REV-1** 작업지시서 (Cursor)

- **PRE HEAD** = `8596b94b0b02c2c8d6a22937aefcb73aca13a162` (branch `s82/education-assign-auth`)
- **BASE** = tai-api main `ac3f125b`
- **GOAL** = `G-mtchixh7-ab95bd`
- **SCOPE = 2 CONTRACTS ONLY** — GPT REVISE 반영. 같은 브랜치 위 새 커밋.

## 변경 파일 (딱 2개)
- `routers/education_assign.py`
- `tests/test_education_assign_auth.py`

## FROZEN (재접촉 금지)
`services/education_assignment_svc.py` · `scheduler.py` · HTTP `/expire` · MASTER auth · COMPLETE · CERTIFICATE · CRON core · DIRECT handler · worker GET `/{edu_id}` · company-settings×3 · `services/permission_guard.py` · api_permissions · frontend.
→ REV-1은 **ASSIGN target membership**과 **LIST/SUMMARY company filter** 두 계약만 수정.

---

## A. ASSIGN TARGET MEMBERSHIP — ALL도 검증 (`_assert_assign_targets` 재작성)

**문제**: 현재 `_assert_assign_targets`가 `_is_admin(_scope(...))`면 early-return → 플랫폼(ALL) caller가 `factory_id=회사B` + `worker_id=회사A 작업자` 혼합 INSERT 가능. 이는 authorization이 아니라 **assignment referential/domain integrity** 결함. ALL은 "타사 factory 선택 가능"이지 "target 관계검증 생략"이 아님.

**재작성 계약 (ALL 포함 모든 scope 동일 적용, early-return 제거)**:

```python
def _assert_assign_targets(sb, current: dict, body: "AssignBody") -> None:
    """모든 scope: 선택 factory와 target(worker/user)의 관계 정합성 강제.
    worker_ids → worker_registry.factory_id == body.factory_id
    user_ids   → users.company_id == 선택 factory의 company_id
    불일치 시 403, INSERT 0 (호출은 INSERT 이전)."""
    # 1) SELECTED FACTORY FACT (server-side)
    fac = sb.table("factories").select("id, company_id").eq("id", body.factory_id).limit(1).execute()
    if not fac.data:
        raise HTTPException(status_code=404, detail="시설을 찾을 수 없습니다")
    selected_company_id = fac.data[0].get("company_id")

    # 2) WORKER TARGET — 모든 scope
    worker_ids = list(body.worker_ids or [])
    if worker_ids:
        found = (
            sb.table("worker_registry").select("id")
            .in_("id", worker_ids).eq("factory_id", body.factory_id).execute()
        )
        if {r["id"] for r in (found.data or [])} != set(worker_ids):
            raise HTTPException(status_code=403, detail="발령 대상이 올바르지 않습니다")

    # 3) USER TARGET — 모든 scope (선택 factory의 company 기준)
    user_ids = list(body.user_ids or [])
    if user_ids:
        found = (
            sb.table("users").select("id")
            .in_("id", user_ids).eq("company_id", selected_company_id).execute()
        )
        if {r["id"] for r in (found.data or [])} != set(user_ids):
            raise HTTPException(status_code=403, detail="발령 대상이 올바르지 않습니다")
```

- **`if _is_admin(...): return` 제거**. `_is_admin`/`_scope`/`_forced_company_id`가 이 helper에서 더는 필요 없으면 helper 내부 사용만 정리(파일 import는 다른 곳에서 쓰므로 유지).
- assign 핸들러 흐름 유지: `_ensure_factory_own(supabase, body.factory_id, current)` (non-ALL foreign factory→404) → master `id+is_active`→404 → `_assert_assign_targets(...)` → INSERT. (non-ALL은 factory가 토큰 회사 소속임이 이미 보장되고, helper의 factory 재조회로 selected_company_id 확보; ALL은 helper의 조회가 유일한 존재확인.)
- ALL SEMANTICS: 회사 A·B factory 모두 선택 가능하나 **선택 factory와 어긋난 target 혼합 불가**. AUTHORIZATION ≠ DOMAIN INTEGRITY.

---

## B. LIST / SUMMARY COMPANY FILTER — `_scoped_assignment_query` 재작성

**문제**: 현재 `_ = company_id`로 값을 버림 → ALL이 `company_id=B`를 줘도 `scoped_filter={}` 때문에 전사 노출. `company_id no longer ignored` 계약 위반.

**재작성 계약**: role data scope(`scoped_filter`) **∩** optional/forced company scope 교집합.

```python
def _scoped_assignment_query(sb, current: dict, factory_id, company_id, select_spec, **select_kw):
    """role scope ∩ company scope. DENY/모순 → None(라우터는 빈 결과)."""
    q = sb.table("education_assignment").select(select_spec, **select_kw)
    effective_company_id = _forced_company_id(current, sb, company_id)  # non-ALL→토큰, ALL→caller값/None

    # C. factory_id 명시
    if factory_id:
        _ensure_factory_own(sb, factory_id, current)  # non-ALL foreign→404
        if effective_company_id:
            fac = sb.table("factories").select("company_id").eq("id", factory_id).limit(1).execute()
            if not fac.data or fac.data[0].get("company_id") != effective_company_id:
                return None  # factory ↔ company 모순 → empty (전사 확대 금지)
        return q.eq("factory_id", factory_id)

    # factory_id 미제공: role scope ∩ company scope
    filt = scoped_filter(current, sb, {"factory_id"})
    q = apply_scoped_filter(q, filt)  # DENY→None
    if q is None:
        return None
    if effective_company_id:
        facs = sb.table("factories").select("id").eq("company_id", effective_company_id).execute()
        fac_ids = [r["id"] for r in (facs.data or [])]
        if not fac_ids:
            return None
        q = q.in_("factory_id", fac_ids)  # role의 factory_id__in 과 AND 교집합(PostgREST/FakeSB 동일)
    return q
```

**호출부 (LIST·SUMMARY 핸들러)**:
- `_ = company_id` **삭제**. 대신 `q = _scoped_assignment_query(supabase, current, factory_id, company_id, <select>...)`.
- `q is None` → 기존대로 빈 목록(LIST) / 0 집계(SUMMARY) 반환.
- LIST의 이후 `.eq("education_id")·.eq("status_code")·.order·.range` 및 effective_url 병합 로직 유지.
- SUMMARY는 `select("id, status_code")` 그대로.

**결과 표**:
- NON-ALL + foreign `company_id` → `_forced_company_id`가 토큰 강제 → 토큰 scope only(확대 0).
- ALL + `company_id=B` → B factory rows only.
- ALL + `company_id` 생략 → 전사 허용.
- ALL + `factory_id=B` + `company_id=A` → 모순 → empty(B 노출 0).

---

## D. 추가 테스트 (REV-1, ADMIN=ALL fixture 사용; 기존 seed의 FAC_OTHER/CO_OTHER/W_OTHER/OTHER_USER 활용)

- **A10** ALL + factory=FAC_OTHER + worker=W_OWN(타 factory) → 403 / INSERT 0
- **A11** ALL + factory=FAC_OTHER + user=USER(company A) → 403 / INSERT 0
- **A12** ALL + factory=FAC_OTHER + worker=W_OTHER(매칭) → success
- **L6** ALL + company_id=CO_OTHER → FAC_OTHER rows only (ASG_OTHER)
- **L7** ALL + company_id 생략 → 전 rows 허용 (ASG_OWN·ASG_OWN2·ASG_OTHER)
- **L8** NON-ALL(CALLER) + company_id=CO_OTHER(foreign) → 토큰 company scope only (ASG_OTHER 제외)
- **S5** ALL + company_id=CO_OTHER → B 집계만 (total=1)
- **S6** ALL + company_id 생략 → 전사 집계 (total=3)
- **S7** NON-ALL + foreign company_id → 토큰 집계만 (total=2)
- **X1** ALL + factory_id=FAC_OTHER + company_id=CO_OWN → 모순 → empty (B 데이터 노출 0)

기존 M/A1–A9/L1–L5/S1–S4/C/T/D/F 전량 유지·재통과. **Phase A total = 50 tests** 목표.
ADMIN dict(role_code ALL, company_id None)로 `dependency_overrides[get_current_user]` override. role_data_scope seed에 ALL 매핑 이미 존재.

---

## E. BOUNDARY
- EXPECTED CHANGE = `routers/education_assign.py`, `tests/test_education_assign_auth.py`
- **FROZEN**: services/education_assignment_svc.py · scheduler.py · (그 외 상단 FROZEN 목록 전부)
- DDL=0 · NEW RPC=0 · PROD DB MUTATION=0 · PROD HTTP MUTATION=0 · MERGE=0 · DEPLOY=0
- permission_guard=0 · api_permissions=0 · frontend=0 · cron_job_master=0

## Push-fidelity
- push 전 두 파일 `git hash-object` 기록·commit 후 blob 대조(Korean/SQL drift 주의). 완료 후 NEW HEAD·blob SHA·pytest 결과를 §82 PHASE A REV-1 SUBMIT 양식으로 보고.
