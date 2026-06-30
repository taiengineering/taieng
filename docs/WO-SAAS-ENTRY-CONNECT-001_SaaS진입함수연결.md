# WO-SAAS-ENTRY-CONNECT-001 — SaaS 진입 함수 연결 (Cursor 적용)

**작성일:** 2026-06-30 | **모드:** Execution. SaaS 진입 함수 = **존재(YES)**. 본 WO는 Cursor 적용 지시서.

---

## 연결 대상 (확정)
```
함수:     SaaSSetupService.extract_setup_candidates(sb, session_id)
          → approve(sb, setup_id, user_id) → register_to_runtime(sb, setup_id, user_id)
파일:     services/saas_setup_service.py
호출 위치: routers/anonymous_diagnosis.py  create_anonymous_diagnosis()
          full_result 저장(anonymous_diagnosis_results.insert) 직후, return 직전
```

## 입력 계약 (extract_setup_candidates가 요구하는 것)
```
인자: session_id (str)
내부 조회:
  diagnosis_session(id=session_id).diagnosis_status ∈ {COMPLETED_WITH_CANDIDATES, NEEDS_HUMAN_REVIEW}
  diagnosis_candidate(session_id, candidate_type='OBLIGATION')
  diagnosis_schedule_hint(session_id)
출력: saas_setup_candidate insert (approval_status='PENDING_USER_APPROVAL')
```

## ⚠ 적용 전 Cursor가 먼저 확정할 것 (단일 분기)
```
create_anonymous_diagnosis 경로는 현재 session_id / diagnosis_candidate(OBLIGATION) 행을 생성하지 않는다.
extract_setup_candidates는 session_id + diagnosis_candidate 행을 전제한다.
→ 따라서 둘 중 하나를 Cursor가 코드에서 확인 후 적용한다:
  (1) anonymous 경로가 diagnosis_session/diagnosis_candidate를 이미 적재하는 다른 함수를 호출하는지 grep
      (services/, routers/ 에서 diagnosis_session insert / diagnosis_candidate insert 호출 지점).
      → 있으면: 그 session_id를 받아 extract_setup_candidates(sb, session_id) 1줄 호출 연결.
  (2) 없으면: anonymous 경로는 session 트랙이 아니므로, "소비자 입력→SaaS"의 정식 경로는
      diagnosis_session 트랙(로그인/유료)일 수 있다 → 그 트랙의 생성 엔드포인트에서 동일하게
      extract_setup_candidates 호출이 연결돼 있는지 확인하고, 없으면 그 지점에 연결.
```

## 적용 (위 (1) 확인 후)
```python
# routers/anonymous_diagnosis.py — create_anonymous_diagnosis()
# anonymous_diagnosis_results.insert(row) 성공 직후, clear_trace()/return 직전에 추가:

try:
    from services.saas_setup_service import SaaSSetupService
    # session_id 출처: (1)에서 확인한 anonymous 경로의 diagnosis_session.id
    SaaSSetupService.extract_setup_candidates(supabase, session_id)
except Exception as _saas_err:
    import logging
    logging.getLogger("saas.setup.hook").warning(
        "SaaS setup extract hook failed (non-blocking): %s", _saas_err
    )
```
- **non-blocking**: 진단 응답/저장 흐름을 깨지 않도록 try/except (문서훅 activate_documents_for_workflow와 동일 패턴).
- approve / register_to_runtime 은 사용자 승인 단계 → 이번 연결 범위 아님(extract까지만).

## E2E 실행 (대표 curl 또는 Cursor — Claude는 네트워크 OFF로 실행 불가)
```
1. POST https://api.taieng.co.kr/anonymous-diagnosis
   body: {"site_kind":"manufacturing","scale":"small","workers":12,"region":"인천"}
2. 응답 publicToken 확보.
3. 검증(SELECT, 글 읽기):
   - saas_setup_candidate 에 신규 row 생성 여부 (approval_status='PENDING_USER_APPROVAL')
   - related_candidate_id / setup_type / task_title_candidate 가 진단 의무와 일치하는지 글로 확인
4. /health 200 유지 확인.
```

## PASS 기준
```
소비자 입력 1건 → create_anonymous_diagnosis → extract_setup_candidates 호출 →
saas_setup_candidate 에 후보 row 생성(글 읽기로 의무 일치 확인). 기존 진단 응답/저장 흐름 무파손.
PASS 시 다음 연결점(approve → register_to_runtime → runtime)으로 이동.
```

## Boundary
```
편집 파일: routers/anonymous_diagnosis.py (Cursor 로컬 편집 + git push).
extract_setup_candidates 본체(saas_setup_service.py) 수정 금지 — 호출만.
diagnosis_candidate/diagnosis_session 적재가 없으면(분기 2) GPT/Cursor 구현 영역으로 넘김(임의 브릿지 작성 금지).
/health 503 금지. obligation 엔진/legal_engine 미접촉.
```

*WO-SAAS-ENTRY-CONNECT-001 — SaaS 진입 함수 존재(YES): SaaSSetupService.extract_setup_candidates(services/saas_setup_service.py). 연결 위치=create_anonymous_diagnosis full_result 저장 직후 1줄 호출(non-blocking). 단 session_id/diagnosis_candidate 적재 유무를 Cursor가 먼저 grep 확인 후 적용. E2E=대표/Cursor curl. Claude 네트워크 OFF로 실행 불가.*
