# INSPECTION_DOCUMENT_EVENT_TAXONOMY_v1

```
WP        = WP-DATA-ARCH-01
STAGE     = CANONICAL DOCUMENT (post CORR-01 PASS / CLOSED)
SOURCE REPO      = taiengineering/tai-api
SOURCE MAIN SHA  = e1506aa45d3b35bf4d99d3c123600e9f19ab6996
CANONICAL REPO   = taiengineering/taieng
CANONICAL PATH   = docs/
DATE      = 2026-08-23
MODE      = READ ONLY (문서화 전용)
MUTATION  = 0
근거표기   = [실측]=DB 직독 / [코드근거]=repo 직독 / [판정]=아키텍처 판정
```

이 문서는 점검→문서 생명주기의 **이벤트 표면(event surface)을 명명·분류**한다. 구현이 아니라
분류다. WP-DATA-ARCH-02의 orchestration 설계 입력으로 쓴다.

---

## 1. 상태 표기

```
PRESENT(STATE)  = 테이블 상태컬럼 전이는 존재하나 이벤트로 방출/소비되지 않음 (암묵 상태변화)
PRESENT(EVENT)  = 이벤트/로그 레코드가 실제 존재
MISSING         = 상태전이도 이벤트도 없음 (orchestration 공백)
DORMANT         = 코드상 전이 정의는 있으나 데이터 0으로 미가동
```

---

## 2. 도메인별 이벤트 분류

### D1. Inspection Execution
```
EVT.INSPECTION.SUBMITTED
  현행 = PRESENT(STATE)   [코드근거 worker_check POST /submit:
          safety_inspections INSERT + safety_inspection_results INSERT]
  방출 = 없음. 후속 문서생성으로 이어지는 이벤트 신호 없음.
  identity = inspector_id (users-resolved, actor binding NOT ENFORCED — CONNECTION_MAP §2)

EVT.INSPECTION.RESULT_RECORDED
  현행 = PRESENT(STATE)   [safety_inspection_results row 생성]
  방출 = 없음.

EVT.RUNTIME_INSPECTION.SESSION_* (IN_PROGRESS / REVIEW_PENDING)
  현행 = DORMANT   [코드근거 my_inspection_bridge: session_status, review_status 전이 정의]
  데이터 = 0  [실측]
```

### D2. Document Lifecycle
```
EVT.DOCUMENT.DRAFT_CREATED
  현행 = PRESENT(STATE)   [코드근거 document_engine_svc.create_document → status=DRAFT]
  주의 = form_schema_id 입력으로 빈 DRAFT 생성. inspection 미소비.

EVT.DOCUMENT.SUBMITTED_FOR_REVIEW
  현행 = PRESENT(STATE)   [코드근거 change_status → SUBMITTED_FOR_REVIEW]

EVT.DOCUMENT.CONFIRMED
  현행 = PRESENT(STATE)   [코드근거 document_confirm_svc 원자 TX]
  atomic effects
    = runtime_document_archive snapshot INSERT
    + runtime_document_approval INSERT
    + runtime_document_data seal
  무결성 = UNIQUE(runtime_document_id, document_version)  [실측]
  CONFIRMED SNAPSHOT RECORD = runtime_document_archive

  ※ EVT.DOCUMENT.ARCHIVED 는 별도 lifecycle event 가 아님
    = Confirm transaction 에서 생성되는 immutable snapshot record.
      evidence_manifest = Confirm 시점 snapshot representation (운영 evidence store 아님).

EVT.DOCUMENT.GENERATED
  현행 = PRESENT(STATE)   [generated_document record — derived artifact]
  링크 = runtime_document_id linked 2 / 1,544 · snapshot_id linked 0 / 1,544  [실측]

EVT.DOCUMENT.SUBMISSION_CREATED
  현행 = PRESENT(STATE)   [코드근거 submission_bridge 가 runtime_submission 생성]
  generated_document linkage = OPTIONAL LOGICAL REFERENCE · DB FK 없음 · linked submission 0  [실측]
  → GENERATED ↔ SUBMISSION 을 현재 CONNECTED E2E 로 표현 금지.
```

### D3. Identity
```
EVT.WORKER.ROSTER_REGISTERED
  현행 = PRESENT(STATE)   [코드근거 worker_registry create / bulk_import — user_id write 없음]

EVT.WORKER.INVITED
  현행 = PRESENT(STATE)   [코드근거 POST /{id}/invite — SMS 발송, user_id 미연결]

EVT.WORKER.PRINCIPAL_LINKED
  현행 = PRESENT(STATE)   [코드근거 auth/verify-otp → _link_worker_registry:
          worker_registry.user_id + app_installed=True]
  실측 = worker_registry.user_id linked 1 / roster→authenticated principal 1 (28 중) [실측] → IDENTITY BREAK
```

### D4. Evidence
```
EVT.EVIDENCE.OPERATIONAL_ATTACHED
  현행 = FEDERATED / PRESENT(STATE)
  저장계 = photo_urls / runtime_inspection_evidence(0) / runtime_compliance_evidence / evidence_vault_link
  통합 소유 = NOT ESTABLISHED

EVT.EVIDENCE.CONFIRMED_SNAPSHOT
  현행 = PRESENT(STATE)   [runtime_document_archive.evidence_manifest — Confirm 시점 snapshot]
  주의 = 운영 evidence store가 아니라 confirmed snapshot representation.
```

### D5. Orchestration (핵심 공백)
```
EVT.INSPECTION_TO_DOCUMENT.ORCHESTRATED
  현행 = MISSING
  [판정] safety_inspection_results → (문서 type/schema 선택 + 필드 채움) → runtime_document_data
         를 잇는 이벤트/호출 orchestration 없음.
  - 매핑 데이터(WHAT): runtime_inspection_bridge 구조 존재하나 runtime_form_schema_id populated 0 [실측]
  - 실행 연결(HOW): document_engine_svc가 inspection 미참조 [코드근거]
  → MISSING ORCHESTRATION BRIDGE. WP-DATA-ARCH-02의 1차 설계 대상.
```

---

## 3. 관찰된 이벤트/로그 인프라 (참고)

```
runtime_lifecycle_audit_log     — 존재 [실측: STEP1 테이블 열거]
runtime_notification_event      — 존재 (대량, 참고용 est)
runtime_compliance_evidence     — immutable_hash 중복차단(evidence_bridge) [코드근거]
```

[한계] 위 로그계의 이벤트 스키마·소비자 매핑은 본 감사 범위 밖. LOG MERGE는 deferred.

---

## 4. Orchestration 공백 지도 (요약)

```
[EXEC]                          [DOC]
safety_inspections/results  ──❌ MISSING ORCHESTRATION ──>  runtime_document_data
      │                                                          │
      │ (identity: actor binding NOT ENFORCED)                   │ status lifecycle PRESENT(STATE)
      ▼                                                          ▼
  submitted_by 미확정                                    confirmed_by / archived (immutable)
```

[판정] 이벤트 표면 대부분은 도메인 내부 상태전이로 존재하나, **도메인 간(EXEC→DOC)을
잇는 orchestration 이벤트가 부재**하다. 정본 baseline은 이 공백을 확정하는 데서 멈춘다.
설계·구현은 WP-DATA-ARCH-02에서 승인 후 진행한다.
