# §82 EDUCATION ASSIGNMENT — Phase D 작업지시서 (Cursor): HTTP /expire 폐쇄(410)

- **BASE** = tai-api main `f6708f089a22ede0b966d1ab3b2cf8e5bd572e9b`
- **BRANCH(신규)** = `s82/expire-http-retire` (base = main `f6708f08`)
- **GOAL** = `G-mtchixh7-ab95bd`
- **MODE** = 구현 + pytest + commit/push. **MERGE/DEPLOY = 0** (별도 GPT 승인).
- 전제: Phase C 완료 — cron_job_master.EDU_EXPIRE_DAILY.endpoint_url = `direct://education_assignment_expire`, prod 프로세스는 restart 후 DIRECT 등록됨. 따라서 크론은 더는 HTTP `/expire`를 호출하지 않음 → HTTP 진입 폐쇄 안전.

## 변경 파일 (딱 2개)
- `routers/education_assign.py`
- `tests/test_education_assign_auth.py`

## FROZEN (재접촉 금지)
- `scheduler.py` (DIRECT handler·러너)
- `services/education_assignment_svc.py` (shared core — DIRECT가 계속 사용)
- `cron_job_master` (DB config — Phase C에서 이미 cutover, 재변경 0)
- `services/permission_guard.py` · `api_permissions`
- `routers/education.py` · `routers/worker_assets.py` · frontend
- education_assign.py 내 나머지 엔드포인트(master·assign·assignments·summary·complete·certificate·GET /{edu_id}·company-settings×3) 전부 무변경

---

## 변경 계약 — `POST /education/assignments/expire`

**현재 (BASE f6708f08, blob afab4877)**:
```python
@router.post("/assignments/expire")
def expire_assignments():
    """... core 는 DIRECT 와 공유."""
    try:
        data = expire_overdue_education_assignments(get_supabase())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"만료 처리 실패: {e}")
    return {"status": "success", "message": f"{data['updated']}건 만료 처리됐습니다.", "data": data}
```

**변경 후 (Phase D)**:
```python
@router.post("/assignments/expire")
def expire_assignments():
    """RETIRED (§82 Phase D). 만료 처리는 scheduler DIRECT 핸들러
    (direct://education_assignment_expire → services.education_assignment_svc)만 수행한다.
    HTTP 진입은 410 으로 폐쇄. core 호출·DB UPDATE 없음."""
    raise HTTPException(status_code=410, detail="CRON_DIRECT_ONLY")
```

계약 세부:
- **410 GONE**, `detail = "CRON_DIRECT_ONLY"` (정확히 이 문자열).
- **core 호출 = 0** (expire_overdue_education_assignments 미호출).
- **DB UPDATE = 0** (어떤 supabase update도 실행 안 함).
- try/except·get_supabase() 호출 제거(불필요).
- 라우트·경로·메서드는 유지(POST /education/assignments/expire). GET /{edu_id}의 reserved에 "expire" 유지(무변경).

**import 정리**:
- `from services.education_assignment_svc import expire_overdue_education_assignments` 는 이제 router에서 미사용 → **삭제**(unused import 제거). 이 심볼은 scheduler.py DIRECT 핸들러가 계속 import하므로 svc 자체는 그대로.
- 그 외 import 무변경.

**버전/문서**:
- VERSION `1.1.0` → `1.2.0`.
- 모듈 docstring의 expire 줄 갱신: `POST /education/assignments/expire  만료 처리 (Phase D: HTTP 410, DIRECT 전용)` 정도.

**DIRECT 경로 = 무변경 (반드시 유지)**:
- `scheduler.py` `DIRECT_HANDLERS["direct://education_assignment_expire"]` → `services.education_assignment_svc.expire_overdue_education_assignments(get_supabase())` 정상 호출 경로 그대로. 만료 로직은 이 core로만 수행.

---

## 필수 테스트 (`tests/test_education_assign_auth.py` 에 추가)
기존 매트릭스(M/A/L/S/C/T/D1–D7/F) 전량 유지. 아래 추가:

- **D8** `POST /education/assignments/expire` → **410**, body detail == `"CRON_DIRECT_ONLY"`.
- **D9** HTTP expire 호출 시 **core 호출 0** — `services.education_assignment_svc.expire_overdue_education_assignments` 를 spy로 monkeypatch 후 엔드포인트 호출, spy **미호출** 단언.
- **D10** HTTP expire 호출 시 **DB UPDATE 0** — FakeSB 주입 후 호출, `fake.updates == []` 단언(교육_assignment 무변경).
- **D11** DIRECT 경로 유지 — `sch._register_direct_handlers()` 후 `sch._execute_direct("direct://education_assignment_expire", {})` 가 shared core를 호출(기존 D2 계약 유지) · overdue 갱신 동작(D3~D6 유지).
- **D12** 기존 DIRECT/core regression(D1–D7) 전량 재통과.

참고: D8 라우트는 auth dependency 없음(무토큰이라도 410). 즉 410이 auth보다 먼저/독립적으로 반환되는지 확인(현 핸들러는 Depends 없음 → 그대로).

## BOUNDARY
- EXPECTED CHANGE = `routers/education_assign.py` · `tests/test_education_assign_auth.py`
- DDL = 0 · NEW RPC = 0 · PROD DB MUTATION = 0 · PROD BUSINESS MUTATION = 0 · MERGE = 0 · DEPLOY = 0
- scheduler.py = 0 · services/education_assignment_svc.py = 0 · cron_job_master = 0 · permission_guard = 0 · api_permissions = 0 · education.py = 0 · worker_assets.py = 0 · frontend = 0

## Push-fidelity
- push 전 두 파일 `git hash-object` 기록·commit 후 blob 대조(Korean drift 주의). 완료 후 NEW HEAD·blob SHA·pytest 결과를 §82 PHASE D IMPLEMENTATION REPORT 양식으로 보고.

## 후속 (Phase D 이후, 별도 승인)
- Phase D-MERGE/DEPLOY: PR base main `f6708f08` ← head `s82/expire-http-retire` → merge → Railway 배포검증. (이 지시서 범위 아님.)
- 배포 후: HTTP `/expire` 410 확인은 사후. cron DIRECT 실행 증거(다음 01:00 KST cron_job_log)는 이미 DEFERRED AUDIT/NON-BLOCKING.
