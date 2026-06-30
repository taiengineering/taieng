# CURSOR-WO-SAAS-ENTRY-CONNECT-001 — SaaS 진입 함수 연결 (의존성 확정판)

**작성일:** 2026-06-30 | **대상:** Cursor (로컬 편집 + git push) | **모드:** Execution. 폭주 방지.
**한 줄:** SaaS 진입 함수는 **존재**. 단 그 입력은 anonymous 트랙이 아니라 **`diagnosis_session` 트랙**이다. 연결 지점을 잘못 잡으면 0건 + 설계 위반이므로, 아래 의존성대로만 적용한다.

---

## 0. 폭주 방지 규칙 (필독)
```
- 이 WO 범위 밖 파일 수정 금지. 한 번에 1개 연결만.
- saas_setup_service.py 본체 수정 금지 (호출만).
- 새 브릿지/어댑터/FieldMap/정규화 생성 금지.
- diagnosis_candidate/diagnosis_session 적재 로직 신규 작성 금지 (없으면 STOP → 보고).
- commit 전 git log 확인(중복 작업 적재 금지). PR 단위로 분리.
- /health 503 금지. legal_engine/obligation 엔진 미접촉.
```

## 1. 확정된 의존성 (HANDOFF_DIAGNOSIS_SAAS.md + DB 실측)
```
SaaS 진입 함수: SaaSSetupService.extract_setup_candidates(sb, session_id)   [services/saas_setup_service.py]
입력 계약(의존):
  session_id → diagnosis_session(id, diagnosis_status ∈ {COMPLETED_WITH_CANDIDATES, NEEDS_HUMAN_REVIEW})
            → diagnosis_candidate(session_id, candidate_type='OBLIGATION')
            → diagnosis_schedule_hint(session_id)
  출력: saas_setup_candidate insert (approval_status='PENDING_USER_APPROVAL')

설계 정식 플로우(HANDOFF):
  사업장 입력 → POST /diagnosis-engine/evaluate → diagnosis_session + diagnosis_candidate 생성
            → POST /saas-setup/extract/{session_id} → saas_setup_candidate
            → approve/{id} → register/{id}

DB 실측(의존성 검증):
  diagnosis_session 1행 / diagnosis_candidate 159 (OBLIGATION 59) / diagnosis_schedule_hint 22
  anonymous_diagnosis_results 172 — 이 경로는 session_id/diagnosis_candidate를 생성하지 않음(별도 트랙).
```

## 2. 연결 지점 판정 (★ 중요 — anonymous 아님)
```
✗ create_anonymous_diagnosis(anonymous 트랙)에 extract_setup_candidates를 붙이면
  session_id가 없고 diagnosis_candidate 행이 없어 후보 0건 + 설계 위반.
✔ 정식 연결 지점 = /diagnosis-engine/evaluate 가 diagnosis_session을 생성하는 그 직후.
  → 진단 평가가 diagnosis_session + diagnosis_candidate(OBLIGATION)를 적재하는 엔드포인트에서,
    세션 생성 완료 직후 extract_setup_candidates(sb, session_id)를 1줄 호출(non-blocking).
```

## 3. Cursor 적용 절차 (순서 고정)

### STEP 1 — 연결 지점 grep (수정 전 확인)
```
grep -rn "diagnosis_session" services/ routers/ | grep -i insert
grep -rn "diagnosis_candidate" services/ routers/ | grep -i insert
목적: diagnosis_session + diagnosis_candidate(OBLIGATION)를 INSERT하는 함수/엔드포인트를 1개 특정.
      (HANDOFF상 POST /diagnosis-engine/evaluate. 실제 라우터 파일·함수명을 grep으로 확정.)
```

### STEP 2 — 분기 판정
```
(A) 위 엔드포인트가 존재하고 diagnosis_session+diagnosis_candidate(OBLIGATION)를 적재한다
    → STEP 3 진행 (1줄 연결).
(B) 적재하는 엔드포인트가 없다 / candidate_type='OBLIGATION' 행을 만들지 않는다
    → STOP. 코드 수정하지 말고 "진단평가가 diagnosis_candidate(OBLIGATION) 미생성"으로 보고.
      이 경우는 GPT 구현 영역(진단평가→candidate 적재)이며 본 WO 범위 밖.
```

### STEP 3 — 1줄 연결 (분기 A일 때만)
```python
# 해당 라우터(예: routers/diagnosis_engine*.py)의 evaluate 핸들러,
# diagnosis_session 생성 + diagnosis_candidate 적재가 끝난 직후, 응답 return 직전:

try:
    from services.saas_setup_service import SaaSSetupService
    SaaSSetupService.extract_setup_candidates(sb, session_id)  # sb, session_id = 해당 핸들러의 기존 변수
except Exception as _saas_err:
    import logging
    logging.getLogger("saas.setup.hook").warning(
        "SaaS setup extract hook failed (non-blocking): %s", _saas_err
    )
```
```
규칙:
  - non-blocking try/except (진단 응답 흐름 무파손).
  - extract_setup_candidates까지만. approve/register는 사용자 승인 단계 → 이번 범위 아님.
  - 변수명(sb, session_id)은 해당 핸들러의 실제 변수에 맞춤. 새 변수/새 조회 추가 금지.
```

### STEP 4 — commit & push
```
브랜치: feature/saas-entry-connect-001
커밋:   "feat: connect diagnosis evaluate → SaaSSetupService.extract_setup_candidates (non-blocking)"
PR:     main 대상. 단일 파일 변경만.
```

## 4. E2E 검증 (대표 또는 Cursor — Claude 네트워크 OFF로 실행 불가)
```
1. POST /api/v1/diagnosis-engine/evaluate  (사업장 입력 1건)
2. 응답 session_id 확보.
3. SELECT 검증(글 읽기):
   - saas_setup_candidate WHERE session_id=<해당> → 신규 row 생성 확인
   - approval_status='PENDING_USER_APPROVAL'
   - setup_type / task_title_candidate / source_trace(law_name·article)가 진단 의무와 일치하는지 글로 확인
   - RECURRING_TYPES(INSPECTION/EDUCATION/REPORT/MEASUREMENT/PRESERVATION/PERMIT_RENEWAL/PRE_WORK_CHECK)만
     추출되고 HOLD_STATUSES(UNKNOWN/UNRESOLVED/AMBIGUOUS/NEEDS_HUMAN_REVIEW)는 제외됐는지 확인
4. /health 200 유지.
```

## 5. PASS / ROLLBACK
```
PASS:   진단 평가 1건 → extract_setup_candidates 호출 → saas_setup_candidate 후보 row 생성
        (글 읽기로 의무 일치 확인) + 기존 진단 응답/저장 흐름 무파손.
        → 다음 연결점(approve → register_to_runtime → runtime)으로 이동.
ROLLBACK: 후보 0건이거나 의무 불일치 또는 기존 흐름 파손 → 커밋 revert, 분기 (B) 보고로 전환.
```

## 6. 유관 파일·의존성 맵 (수정 금지, 참조용)
```
[수정 대상]  routers/diagnosis_engine*.py (STEP 1에서 grep으로 확정) — evaluate 핸들러 1곳에 1줄
[호출 대상]  services/saas_setup_service.py  SaaSSetupService.extract_setup_candidates  (수정 금지)
[읽는 테이블] diagnosis_session, diagnosis_candidate, diagnosis_schedule_hint
[쓰는 테이블] saas_setup_candidate
[무관/미접촉] anonymous_diagnosis_results, create_anonymous_diagnosis, legal_engine, obligation_instance,
            run_facility_applicability, facility_profiles
```

*CURSOR-WO-SAAS-ENTRY-CONNECT-001 — SaaS 진입 함수 존재. 정식 입력은 diagnosis_session 트랙(/diagnosis-engine/evaluate)이지 anonymous 아님. grep으로 evaluate 핸들러 확정→세션 생성 직후 extract_setup_candidates(sb, session_id) 1줄(non-blocking). diagnosis_candidate(OBLIGATION) 미적재면 STOP→GPT영역. E2E=대표/Cursor curl. 단일파일 PR.*
