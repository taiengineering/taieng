# INSPECTION_DOCUMENT_PHYSICAL_DESIGN_v1  (CANONICAL · WP-DATA-ARCH-02 PASS/CLOSED)

```
WP                 = WP-DATA-ARCH-02  (Inspection + Document Physical Design · CORR-03)
STAGE              = CANONICAL DOCUMENT (post CORR-03 PASS · WP-DATA-ARCH-02 CLOSED)
SOURCE API SHA     = e1506aa45d3b35bf4d99d3c123600e9f19ab6996  (taiengineering/tai-api)
CANONICAL ARCH SHA = e83feabd80c7c515f0bfb9a859579213e9de9342  (taiengineering/taieng)
MODE               = READ ONLY / PHYSICAL DESIGN
MUTATION           = DB 0 / CODE 0 / DDL 0 / DEPLOY 0 / REAL CONFIRM 0
근거표기            = [실측]=DB 직독 / [코드근거]=repo 직독 / [설계]=제안 / [BLOCKER]=선결조건
```

동반 초안: ORCHESTRATION_CONTRACT_v1 (PD-1) / IDENTITY_CONTRACT_v1 (PD-3) / PARTITION_DESIGN_v1 (PD-4, WP-RETENTION-01 포함).
이 문서 = 마스터 + PD-2(실행계 물리계약) + Physical Design Matrix.

---

## 0. 상속 고정 (재기획 금지)

```
Current Inspection Execution SoT = safety_inspections + safety_inspection_results
Runtime Inspection               = DORMANT PARALLEL IMPLEMENTATION
Document Working / Confirmed      = runtime_document_data / runtime_document_archive
                                   (UNIQUE(runtime_document_id, document_version))
work_schedules physical          = HASH(factory_id) MOD 16 (상속, 재설계 금지)
Missing                          = Inspection → Document MISSING ORCHESTRATION BRIDGE
```

## 0-1. 두 문서 시스템 (설계 전제)

```
SYSTEM-L (Legacy Generation) = document_type_registry + InspectionFetcher → generated_document(1,544) [inspection 읽음]
SYSTEM-R (Runtime Lifecycle) = runtime_form_schema → runtime_document_data → confirm → runtime_document_archive
                               [inspection 미소비] ← MISSING BRIDGE 대상, 정본 confirm 축
∴ orchestration 종점 = SYSTEM-R archive. SYSTEM-L generated_document = 파생 유지, 통합 안 함.
```

---

## PD-2. Inspection Execution Physical Contract (CORR-02)

safety_inspections / safety_inspection_results = 현 Operational SoT 유지. Runtime 전환 안 함. ALTER 없음(판정만).

```
A. safety_inspections.assignment_id  이름 ≠ FK 대상(work_schedules.id) [실측]
   판정 = KEEP (DECISION_safety-inspections-assignment-fk_2026-08-17 상속. RENAME 미채택)

B. safety_inspections.inspector_id  FK = users.id [실측]
   판정 = KEEP + inspector_id = users.id 고정 (roster direct fallback 폐기 — IDENTITY_CONTRACT)
   ADDITIVE = safety_inspections.submitted_by uuid→users.id (INSPECTION SUBMITTER 분리)

C. safety_inspection_results.inspection_id  nullable [실측 NULL 0/8, broken 0]
   판정 = ADDITIVE FIX → NOT NULL (validation 후 강화 가능) · FK 유지(→safety_inspections.id) · DEFER

C2. safety_inspection_results.checked_at  nullable [실측 NULL 0/8]
   판정 = NOT NULL 강화 가능 (RANGE(checked_at) 파티션 키 전제) · DEFER

D. safety_inspection_results.inspection_set_item_id  논리참조, FK 없음 [실측 NULL 5/8, broken 0]
   판정 = nullable 유지 + ADDITIVE FK ON DELETE NO ACTION/RESTRICT (soft-delete provenance)

E. tenant/factory trace
   판정 = ADDITIVE safety_inspections.factory_id = work_schedules composite FK companion ONLY (nullable)
        · canonical tenant key = NO · HASH partition key = NO
   [CORR-02] safety_inspection_results.factory_id = 불필요 → 삭제
   [실측] inspections 2건 중 assignment 無 1건 → factory 결정적 backfill 불가 row 존재

F. retention (CORR-03, PD-4 연계)
   ADDITIVE = safety_inspections.retention_until timestamptz = EFFECTIVE NOT-BEFORE-DELETE
     NULL   = retention unresolved OR active hold → deletion blocked (fail-closed)
     finite = 모든 법정/정책/hold 반영한 최종 삭제 가능 시각
     parent 보유(child results 동일 provenance 공유). [실측] safety_inspections hold 컬럼 0 → legal_hold_count 별도조건 삭제.
   REFERENCE = runtime_evidence_retention_policy (existing asset, reference/default, legal SoT 아님 — 아래 참조)
```

---

## 9. PHYSICAL DESIGN MATRIX (CORR-02)

형식: OBJECT / CURRENT / PROBLEM / CHOSEN / SCHEMA / MIGRATION / STATUS

### safety_inspections
```
CURRENT   = assignment_id→work_schedules, inspector_id→users, inspection_date(no tz), status_code.
            factory_id/submitted_by/retention_until 없음. rows 2 (inspector_id NULL 1, assignment 有 1) [실측]
            incoming FK = defects.inspection_id, safety_inspection_results.inspection_id [실측]
PROBLEM   = inspector/submitter 미분리 · companion/retention 부재 · (파티션 시 PK ripple)
CHOSEN    = DO NOT PARTITION (regular table, PK(id) 보존) · inspector_id=users.id 고정
            +submitted_by(additive) +factory_id(companion) +retention_until(timestamptz)
SCHEMA    = +submitted_by, +factory_id, +retention_until (전부 nullable)
MIGRATION = ADD COLUMN + 부분 backfill — DEFER
STATUS    = DESIGN / DEFER-EXEC · P1 partition = DEFER
```

### safety_inspection_results
```
CURRENT   = inspection_id(nullable,FK→safety_inspections), item_id(논리참조), checked_at(tz,nullable), created_at(no tz).
            rows 8 [실측: inspection_id NULL 0, checked_at NULL 0, item NULL 5, broken 0]. incoming FK = 0 [실측]
PROBLEM   = 제약 미비. P0 최대 성장축(F×S×E×I)
CHOSEN    = inspection_id→NOT NULL · checked_at→NOT NULL · item_id nullable + FK RESTRICT
            · RANGE(checked_at) 파티션 (incoming FK 0 → 독립) · factory_id 없음(삭제)
            · PK = (id, checked_at) [partition key 포함 필수] · LOCAL INDEX (inspection_id, created_at)
            · Application identity = id 유지 / DB physical identity = (id, checked_at)
SCHEMA    = NOT NULL 강화 + FK(item) RESTRICT + PK(id,checked_at) + RANGE(checked_at) + local idx
MIGRATION = validation 후 제약 + 파티션 — DEFER
STATUS    = DESIGN / DEFER-EXEC
```

### work_assignments
```
CURRENT   = generate_daily_assignments()(cron inactive), rows 5,991, UNIQUE(schedule_id,scheduled_date) 없음 [실측]
CHOSEN    = NO REDESIGN. +factory_id companion + UNIQUE(schedule_id,scheduled_date) 후보 (DEFER)
STATUS    = DESIGN / DEFER-EXEC
```

### runtime_inspection_bridge  ← CURATED CONFIG SoT
```
CURRENT   = inspection_set_id(NN)→runtime_form_schema_id(nullable). rows 324/distinct 324,
            insp_sets 327(bridge 없는 set 3), schema populated 0, MAPPED 323.
            제약 = PK + CHECK(mapping_status ∈ {PENDING,MAPPED,PARTIAL,NOT_MAPPABLE,NEEDS_HUMAN_REVIEW}) [실측]
            FK 없음, UNIQUE(set) 없음 [실측]
CHOSEN    = REDEFINE AS CURATED CONFIGURATION SoT (기존 테이블에 제약 additive, 신규 아님)
            +FK inspection_set_id→inspection_sets · +FK runtime_form_schema_id→runtime_form_schema
            +UNIQUE(inspection_set_id) · +CHECK(MAPPED → schema_id NOT NULL)
            323건 false-MAPPED(schema NULL) → NEEDS_HUMAN_REVIEW 로 revert (정확 enum). 이름 유사도 auto-map 금지.
SCHEMA    = FK×2 + UNIQUE + CHECK
MIGRATION = 제약 additive + 상태 revert(DML) — DEFER
STATUS    = DESIGN / [BLOCKER] curated (자동 populate 아님)
```

### runtime_document_data  ← 핵심 NEW COLUMN
```
CURRENT   = form_schema_id(NN), factory_id/company_id(nullable), created_by/submitted_by, status. inspection ref 없음 [실측]
CHOSEN    = +source_inspection_id uuid(nullable) FK→safety_inspections ON DELETE NO ACTION/RESTRICT
            idempotency = UNIQUE(source_inspection_id, form_schema_id) (source 단독 UNIQUE 금지)
            (safety_inspections regular table → single-id FK 유지 가능)
SCHEMA    = +source_inspection_id + UNIQUE(source_inspection_id, form_schema_id)
MIGRATION = ADD COLUMN — DEFER
STATUS    = DESIGN / DEFER-EXEC
```

### runtime_document_archive
```
CURRENT   = confirmed_by(NN), source_trace_snapshot(jsonb NN), evidence_manifest(jsonb NN),
            UNIQUE(runtime_document_id, document_version), rows 0 [실측]
CHOSEN    = NO SCHEMA CHANGE. confirm 시 source trace를 source_trace_snapshot(jsonb)에 봉인
STATUS    = DESIGN / NO SCHEMA CHANGE (partition DEFER, 05B 재오픈 금지)
```

### generated_document / runtime_submission
```
generated_document = SYSTEM-L derived. KEEP, 범위 밖.
runtime_submission = filing_registry_id FK만, generated_document_id FK 없음. KEEP, 범위 밖.
STATUS = OUT-OF-SCOPE
```

### worker_registry / users / auth bridge
```
CHOSEN = IDENTITY_CONTRACT: inspector_id=users.id 고정, roster direct fallback 폐기, submitted_by additive,
         canonical worker_check submission Authorization REQUIRED, Submitter-as-Confirmer(role 고정 삭제)
STATUS = DESIGN (IDENTITY_CONTRACT 참조)
```

---

## 10. 종합 (CORR-02)

```
NEW TABLES        = NONE
NEW COLUMNS (설계) = runtime_document_data.source_inspection_id
                     safety_inspections.submitted_by
                     safety_inspections.factory_id (companion)      ← results.factory_id 삭제(CORR-02)
                     safety_inspections.retention_until             ← retention(CORR-02)
NEW CONSTRAINTS   = bridge(FK×2+UNIQUE+CHECK) · results(inspection_id/checked_at NOT NULL, item FK RESTRICT)
                     runtime_document_data UNIQUE(source_inspection_id, form_schema_id)
                     work_assignments UNIQUE(schedule_id, scheduled_date)
PARTITION         = safety_inspection_results RANGE(checked_at) 만. safety_inspections = REGULAR(DO NOT PARTITION)
MIGRATION REQUIRED = YES (전부 DEFER)
CODE PATCH REQUIRED= YES (create_document_from_inspection / confirm source_trace / worker_check auth REQUIRED /
                     inspector_id=users.id / bridge curate — DEFER)
BLOCKERS =
  ① runtime_inspection_bridge = CURATED 재정의 (323 false-MAPPED → NEEDS_HUMAN_REVIEW, auto-populate 아님)
  ② RETENTION POLICY RESOLUTION = inspection 유형/법령별 기간 → retention_until 채움
     기존자산 runtime_evidence_retention_policy(rows 8, evidence_type UNIQUE, MANUAL_CONFIG)
       = REUSE AS REFERENCE / DEFAULT CANDIDATE, NOT LEGAL RETENTION SoT (evidence_type 축 과대·법령 재검증 필요)
     → default 참조 + inspection 법적 provenance 확정(법령 직독)
  ③ worker_check Authorization REQUIRED 이행 + roster fallback 폐기 (IDENTITY_CONTRACT)
  ④ DOCUMENTABLE INSPECTION v1 = schedule-backed only. unscheduled → document create FAIL-CLOSED (standalone DEFER)
```
