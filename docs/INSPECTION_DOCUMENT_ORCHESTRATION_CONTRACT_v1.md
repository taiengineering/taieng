# INSPECTION_DOCUMENT_ORCHESTRATION_CONTRACT_v1  (CANONICAL · WP-DATA-ARCH-02 PASS/CLOSED)

```
WP                 = WP-DATA-ARCH-02 · PD-1  (CORR-03)
STAGE              = CANONICAL DOCUMENT (post CORR-03 PASS · WP-DATA-ARCH-02 CLOSED)
SOURCE API SHA     = e1506aa45d3b35bf4d99d3c123600e9f19ab6996
CANONICAL ARCH SHA = e83feabd80c7c515f0bfb9a859579213e9de9342
MODE               = READ ONLY / PHYSICAL DESIGN · MUTATION 0
근거표기            = [실측] / [코드근거] / [설계] / [BLOCKER]
```

목표: safety_inspection_results → schema resolution → runtime_document_data → submit → confirm
→ runtime_document_archive 를 **기존 자산 + 최소 additive**로 연결하는 물리 계약.

---

## 1. Trigger — 단일 계약으로 확정 (CORR-01)

```
PASSIVE PREVIEW / OPEN
  = READ ONLY lazy compose (safety_inspection_results 조회만)
  = runtime_document_data INSERT 없음

EXPLICIT CREATE / EDIT / SUBMIT INTENT
  = create_document_from_inspection()
  = working document(runtime_document_data) 생성
```

[설계 확정]
- INSPECTION.SUBMITTED → 자동 DRAFT 생성 = 아님.
- 화면 미리보기/열람 → DRAFT 생성 = 아님.
- **사용자가 문서 작업을 명시적으로 시작할 때만 working row 생성.**
근거: 조기 DRAFT 남발/강결합 방지, 정본 "새 event bus 금지 · 기존 service call 우선".

---

## 2. Source identity + cardinality (CORR-01)

```
CARDINALITY 계약
  inspection-backed runtime document 1건  → source inspection 정확히 1건
  inspection 1건                          → 서로 다른 form_schema 문서 N건 가능
  ∴ 1:1 bijection 아님.
```

```
CHOSEN
  runtime_document_data.source_inspection_id  (ADDITIVE uuid)
  FK → safety_inspections(id)  ON DELETE NO ACTION / RESTRICT   ← SET NULL 폐기(CORR-01)

IDEMPOTENCY
  UNIQUE(source_inspection_id)         = 금지 (N 문서 불가하게 만듦)
  UNIQUE(source_inspection_id, form_schema_id) = canonical inspection document 단위 (필요 시)
```

[설계 근거]
- [코드근거] InspectionFetcher = "발행 단위 = 점검 1건, inspection_id 하나" → source 1건 모델 정합.
- RESTRICT 이유: DRAFT는 lazy source 의존. source inspection 삭제 시 SET NULL이면 조용히 source-less DRAFT 발생.
  Confirm 이후 source results를 HOT에서 내리는 것과, source inspection **identity**를 지우는 것은 별개.
  DRAFT=source 조회 / Confirm 이후=snapshot 독립 원칙 유지.

---

## 3. Schema Resolution — bridge는 아직 SoT가 아님 (CORR-01 핵심)

```
[실측] runtime_inspection_bridge
  rows 324 / distinct inspection_set_id 324 (1:1)
  inspection_sets 327 / bridge 없는 set 3
  runtime_form_schema_id populated = 0
  mapping_status='MAPPED' = 323
  제약 = PK(id) + CHECK 만
  inspection_set_id FK = 없음 · runtime_form_schema_id FK = 없음 · UNIQUE(inspection_set_id) = 없음
→ 현재는 "mapping 모양의 데이터 테이블". 물리적으로 Schema Resolution SoT라 부를 수 없음.
```

### Cardinality 계약 (선결)
```
이번 Runtime orchestration 범위
  = inspection_set 1개 → canonical runtime_form_schema 1개
SYSTEM-L derived documents = 별도 유지 (범위 밖)
```

### bridge 물리 계약 (target)
```
FK  inspection_set_id     → inspection_sets.id
FK  runtime_form_schema_id → runtime_form_schema.id
UNIQUE(inspection_set_id)
CHECK: mapping_status='MAPPED' → runtime_form_schema_id IS NOT NULL
정체성 = CURATED CONFIGURATION SoT  (이름 유사도 자동매핑 금지)
```

[BLOCKER · CORR-01]
- 이름 유사도 auto-mapping 금지: mapping_detail은 법령/공장 메타만 보유, runtime schema와 결정적 공통키 없음.
- 323건(MAPPED·schema_id NULL)은 **전부 NEEDS_HUMAN_REVIEW 로 되돌릴 대상 (정확 enum: PENDING/MAPPED/PARTIAL/NOT_MAPPABLE/NEEDS_HUMAN_REVIEW)**. 자동 populate 가정 금지.
- bridge 없는 inspection_set 3건도 curated 대상.
- 판정: runtime_inspection_bridge = REDEFINE AS CURATED CONFIG SoT (구조 부족 → 제약 신설 + 상태 revert).
  신규 테이블은 만들지 않음(기존 테이블에 제약 additive).

---

## 4. Command — factory/company ownership 해소 포함 (CORR-01)

기존 Confirm 계약은 문서 company/factory ownership을 fail-closed 확인한다. 제출자 본인이어도
ownership 불명확이면 Confirm 안 함. 따라서 command가 scope를 반드시 채운다.

```
create_document_from_inspection(source_inspection_id, current_user)

  1. inspection 존재 확인
  2. inspection_set 해소 (assignment_id → work_schedules.inspection_set_id)
  3. factory/company scope 해소 (work_schedules → factory_id → company_id)
  4. runtime_form_schema 해소 (curated bridge)
  5. ownership 검증 (current_user ↔ factory/company)
  6. idempotency 확인 (source_inspection_id, form_schema_id)
  7. runtime_document_data INSERT
       source_inspection_id / form_schema_id / factory_id / company_id / created_by=current_user.id / DRAFT

FAIL-CLOSED: 2~5 중 해소·검증 실패 시 DRAFT 생성하지 않음.
```

### DOCUMENTABLE INSPECTION v1 (CORR-03)
command은 assignment_id → work_schedules → inspection_set/factory/company 만 사용한다.
따라서 이번 범위의 문서화 가능 대상을 명시한다.

```
DOCUMENTABLE INSPECTION v1 = schedule-backed inspection (assignment_id 해소 가능)
assignment_id / work_schedule 해소 불가
  = inspection 자체는 보존 (execution SoT 유지)
  = runtime document create = FAIL-CLOSED (DRAFT 생성 안 함)
standalone(unscheduled) inspection document support = DEFER
```
[실측] inspections 2건 중 assignment_id NULL = 1 → 이 경계 없으면 "모든 inspection 문서화 가능"으로 오독됨.

[실측 근거] runtime_document_data.factory_id / company_id 컬럼 이미 존재(nullable) → command가 채움.

---

## 5. Draft / Confirm 정책 (유지 + CORR-01 정합)

```
DRAFT   = source reference 우선. runtime_data_json lazy compose (결과값 조기복제 안 함).
CONFIRM = document_confirm_svc 원자 TX 유지.
          runtime_values_snapshot = 최종 값 봉인
          source_trace_snapshot(jsonb NN, 기존) = {source_inspection_id, inspection_set_id, form_schema_id,
            factory_id, company_id, result_ids, resolved_at} 봉인 (스키마 무변경)
          confirmed_by(NN) = document.submitted_by 와 동일 authenticated principal (IDENTITY_CONTRACT)
```

---

## 6. Evidence 연결 계약 (통합 아님)

```
운영 evidence = photo_urls / runtime_inspection_evidence / runtime_compliance_evidence / evidence_vault_link (FEDERATED 유지)
DRAFT   = source reference (evidence_links에 참조 연결, 복제 안 함)
CONFIRM = archive.evidence_links_snapshot + evidence_manifest(jsonb NN)에 confirmed snapshot 봉인
ownership change = NONE
```

---

## 7. Event / Command Contract

```
INSPECTION.SUBMITTED        = source becomes available (자동 DRAFT 생성 아님)
DOCUMENT.CREATE_REQUESTED   = explicit user intent
DOCUMENT.CREATE_REQUESTED → create_document_from_inspection() → DOCUMENT.DRAFT_CREATED
PHYSICAL 실현  = 새 event bus 금지. DOCUMENT.CREATE_REQUESTED는 논리 command/event taxonomy 명칭, 실현은 service call.
후속           = 기존 change_status(SUBMITTED_FOR_REVIEW) / document_confirm_svc(CONFIRMED) 재사용
```
[CORR-02] §1 trigger 계약과 정합: INSPECTION.SUBMITTED → DRAFT_CREATED 직결 삭제(둘은 동시 참 불가).

---

## 결론 (PD-1, CORR-01)

```
trigger              = 단일 계약 (PASSIVE open=READ ONLY / EXPLICIT intent=create), event bus 없음
source reference      = source_inspection_id (additive, FK RESTRICT) + archive.source_trace_snapshot
idempotency          = UNIQUE(source_inspection_id, form_schema_id) (source 단독 UNIQUE 금지)
schema resolution     = runtime_inspection_bridge = REDEFINE AS CURATED CONFIG SoT
                       (FK×2 + UNIQUE(set) + CHECK, 323 false-MAPPED→NEEDS_HUMAN_REVIEW revert, auto-map 금지)
ownership derivation  = command이 factory_id/company_id 해소·검증, fail-closed
draft/confirm         = source-reference + confirm snapshot(스키마 무변경)
new asset required     = NO table. additive column 1 (source_inspection_id).
BLOCKER               = bridge curated 재정의 + 323건 revert (자동 populate 아님)
```
