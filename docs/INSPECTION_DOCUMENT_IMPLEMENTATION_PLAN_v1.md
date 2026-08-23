# INSPECTION_DOCUMENT_IMPLEMENTATION_PLAN_v1  (CANONICAL · WP-DATA-ARCH-03 PASS/CLOSED)

```
WP                 = WP-DATA-ARCH-03  (Implementation Planning)
STAGE     = CANONICAL DOCUMENT (post CORR-02 PASS · WP-DATA-ARCH-03 CLOSED)
SOURCE API SHA     = e1506aa45d3b35bf4d99d3c123600e9f19ab6996  (taiengineering/tai-api)
CANONICAL ARCH SHA = 5d87ac7063157db98b6965067095b35ef561f383  (taiengineering/taieng HEAD, WP-01+02 봉인)
MODE               = PLANNING ONLY
MUTATION           = DB 0 / CODE 0 / DDL 0 / MIGRATION 0 / DML 0 / DEPLOY 0 / REAL CONFIRM 0
근거표기            = [실측]=DB 직독 / [정본]=canonical baseline / [설계]=계획 / [BLOCKER]=선결
```

이 문서는 봉인된 9개 정본(WP-01 아키텍처 5 + WP-02 물리설계 4)의 DEFER-EXEC 항목을
**순서·의존·롤백 안전**하게 배열한 구현계획이다. 실행은 포함하지 않는다.
각 단계는 실행 시점에 **개별 mutation 승인**을 받는다(이 WP는 계획 확정만).

---

## 0. 범위 / 비목표

```
포함  = 순서화된 migration/backfill/constraint/partition/code 단계 + 의존 DAG + 롤백/검증/owner
비목표 = 실제 DDL/DML/migration/deploy 실행 · 첫 실제 Confirm · 정본 재설계 · 엔진 변경
불변 가드 (건드리지 않음) = company_scope · permission_guard · C-2 canonical values · law engine architecture
```

## 0-1. Owner 모델

```
Claude MCP (guri)   = DDL(apply_migration) · DML/검증(execute_sql) · 정본/PR 관리
Cursor / Claude Code = 코드 패치(routers/services, 200줄+ · core router) · local git push
Operator / Legal     = RETENTION POLICY RESOLUTION(법령 직독) · bridge curated 인간검수 결정
GPT                  = REVIEW / APPROVAL GATE (실행자 아님) — 각 단계 계획·결과 판정, mutation 0
```

## 0-2. 위험/롤백 규약

```
LOW    = nullable additive column · 위반 0 constraint add · DML revert · backfill
MEDIUM = NOT NULL 강화(데이터 clean 전제) · FK RESTRICT add
HIGH   = 파티션 rebuild(table swap) · core auth router 패치
HOLD   = 첫 실제 Confirm (별도 게이트)
롤백    = additive→DROP COLUMN/CONSTRAINT · 파티션→원본 유지 후 swap-back · 코드→git revert
검증    = 각 단계 실행 후 execute_sql 재조회 또는 live QA. SUCCESS 전 다음 단계 금지.
```

## 0-3. Migration Precondition Scan [실측, 계획 grounding]

```
wa_dup(schedule_id,scheduled_date)      = 0     → UNIQUE 적용 clean
results.inspection_id NULL              = 0     → NOT NULL clean
results.checked_at NULL                 = 0     → NOT NULL clean / RANGE 키 가능
results.item FK 위반                     = 0     → FK RESTRICT clean
bridge UNIQUE(inspection_set_id) 위반    = 0     → UNIQUE clean
bridge FK(inspection_set_id) 위반        = 0     → FK clean
bridge FK(runtime_form_schema_id) 위반   = 0     → FK clean (전부 NULL, nullable FK OK)
bridge CHECK(MAPPED→schema NOT NULL) 위반 = 323  → ★ CHECK는 323 revert 이후에만 적용
safety_inspections assignment NULL      = 1/2   → factory_id backfill 1건 잔존 NULL
results/insp rows                        = 8 / 2 → 파티션 rebuild 현시점 trivial (미래 대비 절차 설계)
```

---

## 0-4. CORR-02 DELTA (writer-safety 반영)

```
STEP 0 Writer Inventory + Compatibility = INSPECTION_DOCUMENT_COMPATIBILITY_MATRIX_v1 (별도)
Migration DAG (work_schedules 통합·순서교정·cycle해소) = INSPECTION_DOCUMENT_MIGRATION_DEPENDENCY_v1 (별도)
Backfill 검증 = INSPECTION_DOCUMENT_BACKFILL_VALIDATION_PLAN_v1 (별도)
Test/Rollback = INSPECTION_DOCUMENT_TEST_ROLLBACK_PLAN_v1 (별도)

핵심 규칙 = object별 writer 전수 확정·patch 완료 前 constraint/partition 금지.
Writer Inventory = COMPLETE(전 후보 본문 직독·전수 분류 — 미확정/보류 표기 없음. COMPATIBILITY_MATRIX STEP 0).
patch/순서 노드:
  CD5-1(WP-SI) si/results 이중 writer(worker_check + inspection_checklist) patch(auth/identity/submitted_by/factory_id) → C3-7 선행
               (C3-5/C3-6는 B2-3 소관 — 두 writer 이미 checked_at·inspection_id 세팅[직독], WP-SI 무관)
  WA 전환(maintenance) work_assignments 3 creator: 준비(WA-0)↔배포(WA-4) 분리 · WA-2 WRITE OFF → WA-3 UNIQUE → WA-6 WRITE ON (ON CONFLICT arbiter 사이클, code-first 불가)
  bridge 하드닝  = inspection_bridge.py는 READ-ONLY STALE CONTRACT(writer 아님). C3-1..4는 DB constraint/data task로 수행
  WS-MIG   child companion(wa/si factory_id) 先 → WRITE OFF → work_schedules HASH → child FK rewire(wa/si/equipment_checkins) → deploy → WRITE ON (MIGRATION_DEPENDENCY §1)
cycle 해소 = P0-3A(결정) → P0-3B(적용) → CD5-2(go-live). CD5-4(admin 도구)는 P0-3 선결 아님(CD5-4→P0-3 의존 삭제)
```

---

## 1. PHASE 0 — Precondition Resolution (스키마 변경 없음)

```
P0-1 [BLOCKER②] RETENTION POLICY RESOLUTION
  owner = Claude(설계) + Operator/Legal(법령 직독)
  type  = 분석/구성 (DB 변경 없음)
  산출  = inspection 유형/법령 → retention_period 매핑 (runtime_evidence_retention_policy=reference/default,
          NOT legal SoT). B2-2 입력.
  gate  = 모든 DELETE의 선결. additive schema 선결 아님.
  검증  = 매핑 vs 법조문 대조(직독). 롤백 = n/a(문서)

P0-2 [BLOCKER①a] bridge 323 MAPPED → NEEDS_HUMAN_REVIEW revert
  owner = Claude MCP execute_sql (DML)
  선결  = 없음.  후행 = C3-4(CHECK)의 필수 선결
  검증  = bridge_check_violations → 0.  롤백 = 상태 재update
  [실측] 대상 323건

P0-3A [BLOCKER①b] CURATED MAPPING DECISION (runtime_form_schema_id 인간검수 결정)
  owner = Operator/인간검수 · type = artifact(결정 산출), mutation 0
  방식  = inspection_set 단위 curated 결정. 이름 유사도 auto-map 금지.
  선결  = 없음(CD5-4 admin 도구는 선결 아님 — 도구 없이 결정 artifact 작성 가능)
P0-3B CURATED MAPPING APPLY (승인 mapping DML)
  owner = Claude MCP execute_sql · 선결 = P0-3A 승인 · 개별 mutation 승인 필요
  gate  = orchestration go-live(CD5-2) 선결. constraint 선결 아님.
  검증  = schema_populated 증가 / NEEDS_HUMAN_REVIEW 감소
```

---

## 2. PHASE 1 — Additive Schema (nullable, LOW, rollback=DROP COLUMN)

```
S1-1 runtime_document_data.source_inspection_id uuid + FK safety_inspections(id) ON DELETE RESTRICT
     owner=Claude MCP · 선결=없음(safety_inspections regular → single-id FK OK) · 롤백=DROP COLUMN
S1-2 runtime_document_data UNIQUE(source_inspection_id, form_schema_id)
     owner=Claude MCP · 선결=S1-1 · (현재 전부 NULL clean) · 롤백=DROP CONSTRAINT
S1-3 safety_inspections.submitted_by uuid + FK users(id)
     owner=Claude MCP · 선결=없음 · 롤백=DROP COLUMN
S1-4 safety_inspections.factory_id uuid (companion, nullable)
     owner=Claude MCP · 선결=없음 · 롤백=DROP COLUMN
S1-5 safety_inspections.retention_until timestamptz
     owner=Claude MCP · 선결=없음 · 롤백=DROP COLUMN
S1-6 work_assignments.factory_id uuid (companion, nullable) ★신규 — WS-MIG child FK rewire 준비
     owner=Claude MCP · 선결=없음 · 롤백=DROP COLUMN
검증(공통) = information_schema 재조회로 컬럼/FK/UNIQUE 존재 확인
※ equipment_checkins.factory_id = 신규 아님(기존 컬럼) — WS-MIG WS-7 FK rewire 대상(MIGRATION_DEPENDENCY §1)
```

---

## 3. PHASE 2 — Backfill (DML, LOW)

```
B2-1 factory_id backfill = assignment_id → work_schedules.factory_id
     owner=Claude MCP execute_sql · 선결=S1-4
     [실측] 1/2 row assignment NULL → 잔존 NULL(결정적 불가). 검증=채워진 곳 정합. 롤백=SET NULL
B2-2 retention_until backfill = P0-1 매핑 적용
     owner=Claude MCP · 선결=S1-5 + P0-1
     미해소 → NULL (fail-closed, 삭제 금지). 검증=매핑 정합. 롤백=SET NULL
B2-3 results 데이터 검증 (inspection_id/checked_at NULL)
     owner=Claude MCP (검증 전용) · [실측] 이미 NULL 0 → backfill 불요. C3-5/6 gate
B2-4 work_assignments.factory_id backfill = schedule_id → work_schedules.factory_id  ★신규
     owner=Claude MCP · 선결=S1-6 · 고아(schedule 없음) NULL 유지. 검증=정합 100%. 롤백=SET NULL
※ submitted_by / source_inspection_id = 무backfill(NULL 유지, future write부터) · runtime_form_schema_id = P0-3(HUMAN REVIEW)
  (BACKFILL_VALIDATION_PLAN 8항목 참조)
```

---

## 3-5. PHASE 2.5 — PRE-CONSTRAINT WRITER PREPARATION (constraint 前 필수)

```
실제 실행순서 = PHASE 3 constraint보다 앞. (DAG: CD5-1 → C3-7 · WA 전환 → C3-8)
CD5-1 = WP-SI: si/results 이중 writer patch (worker_check.py + inspection_checklist.py) [body직독 확정]
  worker_check      = auth REQUIRED · inspector_id=users.id(roster fallback 폐기) · +submitted_by · +factory_id(companion)
  inspection_checklist = auth 이미 보유(get_current_user+company_scope) · +submitted_by · +factory_id · /start inspector_id 처리
  + delegation/impersonation guard [구현주의·비차단]
  [직독] 두 writer 모두 checked_at·inspection_id 세팅 → C3-5/6 무관(B2-3 소관). GATE = C3-7 선행
  배포 timing = schema-first(S1-3/S1-4 先) 준수 — OLD DB+NEW CODE=BREAKS이므로 컬럼 추가 후 배포
  선결=S1-3·S1-4 · 불변가드=company_scope/permission_guard 미변경 · owner=Cursor
  검증=live QA(worker_check 토큰없음 401 / 두 경로 submitted_by·factory_id 세팅 / inspector users.id)
C3-7 앱 사전작업 = inspection_checklist 무검증 item_id 경로 데이터정합 + 앱 오류처리(FK RESTRICT 위반 UX) → C3-7 선행
WA-0 = work_assignments 3 creator patched artifact 준비 (ON CONFLICT + factory_id) — 준비만, deploy는 PHASE 2.5 WA 전환(WA-2 WRITE OFF 이후)
  ★ WA patch = "준비(WA-0)"와 "배포(WA-4)" 분리 (UNIQUE maintenance gate 때문)
```

---

## 4. PHASE 3 — Constraint Tightening (MEDIUM, 데이터 clean 후)

```
C3-1 bridge FK inspection_set_id → inspection_sets(id)          [위반 0] 롤백=DROP
C3-2 bridge FK runtime_form_schema_id → runtime_form_schema(id) [위반 0, nullable] 롤백=DROP
C3-3 bridge UNIQUE(inspection_set_id)                           [위반 0] 롤백=DROP
C3-4 bridge CHECK(mapping_status='MAPPED' → runtime_form_schema_id NOT NULL)
     ★ 선결 = P0-2 (미이행 시 323 위반 → 실패). 롤백=DROP
C3-5 results.inspection_id SET NOT NULL      선결=B2-3 [NULL 0] 롤백=DROP NOT NULL
C3-6 results.checked_at    SET NOT NULL      선결=B2-3 [NULL 0] · PHASE 4 선결. 롤백=DROP NOT NULL
C3-7 results.inspection_set_item_id FK → inspection_set_items(id) ON DELETE RESTRICT [위반 0] 롤백=DROP
C3-8 work_assignments UNIQUE(schedule_id, scheduled_date)  [위반 0]
     ★ MAINTENANCE SUB-GATE — code-first 불가 (ON CONFLICT arbiter↔writer 상호선행 사이클).
       적용 = PHASE 2.5 WA 전환의 WA-3 (WA-0 준비 → WA-2 WRITE OFF → WA-3 UNIQUE → WA-4 deploy → WA-6 WRITE ON). MIGRATION_DEPENDENCY §2. 롤백=DROP
owner(공통)=Claude MCP apply_migration · 검증=제약 존재 + 위반 0 재확인
```

---

## 5. PHASE 4 — Partition Migration (results, HIGH, 격리)

```
PT4-1 safety_inspection_results → PARTITION BY RANGE(checked_at)  MONTHLY
  PK=(id, checked_at) · PARTITION LOCAL INDEX (inspection_id, created_at) · DEFAULT 파티션
  선결 = C3-6(checked_at NOT NULL) · C3-5 · C3-7
  concurrent write = MAINTENANCE WINDOW / WRITE OFF (dual-write 불채택)
  절차 = new_shadow 생성 → 복사 → index/FK → PRE-SWAP full-row equality → RENAME swap → POST-SWAP full-row equality → PRE-state 재적용
         (TEST_ROLLBACK §F PT4-1 상속)
  incoming FK = 0 → child re-point 없음. outgoing FK(inspection_id→safety_inspections) 보존.
  owner = Claude MCP apply_migration (Cursor 앱 조율)
  검증 = full-row equality (A EXCEPT B = 0 · B EXCEPT A = 0) + FK/index/파티션 routing + consumer(InspectionFetcher) smoke + /health 200
  롤백 = TEST_ROLLBACK §F ROLLBACK-A / ROLLBACK-B 계약 상속 (WRITE ON 前/後 분기 + post PK 충돌 precheck)
  DEFAULT operation = reconciliation/drain 계약 상속 (MOVE OUT → CREATE/ATTACH → MOVE IN)
```

---

## 6. PHASE 5 — Orchestration / Remaining Code (Cursor 도메인, HIGH)

```
(CD5-1 = PHASE 2.5로 이동 — constraint 前 writer preparation)
CD5-2 create_document_from_inspection command (7-step, fail-closed, DOCUMENTABLE INSPECTION v1 guard)
  선결=S1-1/2 + P0-3A/P0-3B(curated bridge 결정+적용) + factory/company scope 해소 · owner=Cursor
  검증=live QA(unresolved 시 fail-closed) · 롤백=git revert
CD5-3 document_confirm_svc: source_trace_snapshot inspection trace 봉인
  선결=CD5-2 + S1-1 · owner=Cursor · 검증=confirm snapshot 계보 확인 · 롤백=git revert
CD5-4 curated mapping ADMIN WORKFLOW (반복운영 편의도구)
  owner=Cursor+Claude · **P0-3A/P0-3B 선결 아님(독립)** · 검증=curated 반복반영 편의
```

---

## 7. PHASE 6 — Controlled First Confirm (HOLD, 별도 게이트)

```
Runtime document lifecycle 첫 실제 Confirm
  = PHASE 1~5 전부 SUCCESS 검증 + 명시 승인 후에만.
  = 정본의 CONTROLLED FIRST CONFIRM = HOLD 유지.
```

---

## 8. 의존 DAG (핵심 간선)

```
P0-2 ─────────────────────────► C3-4
P0-3A ─► P0-3B ─► CD5-2(go-live)
S1-1 ─► S1-2 ─► CD5-2 ─► CD5-3
S1-3 ─► CD5-1
S1-4 ─► B2-1 ─► WS-3
S1-5 + P0-1 ─► B2-2
S1-6 ─► B2-4 ─► WS-1/WS-2
B2-3 ─► C3-5, C3-6
C3-6 ─► PT4-1
CD5-1(WP-SI) ─► C3-7
WA 전환(PHASE 2.5) ─► C3-8=WA-3 (maintenance)
WS-1..WS-4 ─► WS-5(WRITE OFF) ─► WS-6(HASH) ─► WS-7(child FK rewire: wa/si/equipment_checkins) ─► WS-8 ─► WS-9(WRITE ON)
(PHASE 1~5 전부) ─► PHASE 6 [HOLD]

병렬 가능 = S1-1..S1-6(단 S1-2←S1-1) · C3-1/2/3(revert 무관) · P0-1(법령, 조기 착수)
순서 hazard(전수) = MIGRATION_DEPENDENCY §5 (H1 P0-2→C3-4 · H2 WA maintenance 전환(WA-0..WA-6) · H3 CD5-1→C3-7 · H4 bridge하드닝→C3-1..4 · H5 P0-3A→P0-3B→CD5-2 · H6 WS-MIG 체인)
```

## 9. 실행 게이트 모델

```
본 WP-03 = PLANNING ONLY. 위 어떤 단계도 지금 실행하지 않음.
실행은 단계별 개별 mutation 승인(후속 WP/게이트)에서. SUCCESS = 다음 단계 진입 gate.
FAILED = 즉시 롤백.
```

## 10. 비차단 구현주의 (정본에서 이월)

```
① retention resolver = deletion_allowed=false 실데이터 → 숫자만으로 삭제 허용 금지. 미해소 retention_until=NULL fail-closed. (P0-1/B2-2)
② inspector delegation = authenticated submitter ≠ inspector 가능 → phone/worker_id 타인 지정 시 assignment/delegation 검증. (CD5-1)
```

## 11. 본 WP mutation ledger

```
DB 0 / CODE 0 / DDL 0 / MIGRATION 0 / DML 0 / DEPLOY 0 / REAL CONFIRM 0
산출 = 구현계획 초안(미커밋). 판정 대기.
```
