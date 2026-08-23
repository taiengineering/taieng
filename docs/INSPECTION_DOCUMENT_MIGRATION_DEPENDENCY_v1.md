# INSPECTION_DOCUMENT_MIGRATION_DEPENDENCY_v1  (CANONICAL · WP-DATA-ARCH-03 PASS/CLOSED)

```
WP    = WP-DATA-ARCH-03 · CORR-02  (Migration Dependency DAG)
STAGE     = CANONICAL DOCUMENT (post CORR-02 PASS · WP-DATA-ARCH-03 CLOSED)
SOURCE API SHA     = e1506aa45d3b35bf4d99d3c123600e9f19ab6996
CANONICAL ARCH SHA = 5d87ac7063157db98b6965067095b35ef561f383
MODE  = PLANNING ONLY · MUTATION 0
```

writer-safety 우선: writer(멱등/식별) patch → 그 다음 constraint/partition. (COMPATIBILITY_MATRIX 게이트 준수)

---

## 1. WS-MIG 통합 순서 (work_schedules HASH 파티션 + child companion)

**방향(확정): child companion 선(先) → parent 파티션 → child FK rewire.**
(work_schedules는 부모. child companion 컬럼이 없으면 parent 전환·FK rewire를 먼저 끝낼 수 없다.)

```
WS-1  work_assignments.factory_id ADD (nullable companion)
        ↓
WS-2  work_assignments.factory_id deterministic backfill (schedule_id→ws.factory_id; 고아 NULL)
        ↓
WS-3  safety_inspections.factory_id ADD + deterministic backfill where possible (assignment_id→ws.factory_id; assignment NULL 1건 NULL)
        ↓
WS-4  affected writers NEW-schema compatible
        (work_assignments 3 creator = factory_id 세팅 patch[WA 전환 §2 동반] · si 2 writer = factory_id 세팅 patch[CD5-1])
        ↓
WS-5  MAINTENANCE / WRITE OFF
        ↓
WS-6  work_schedules HASH(factory_id) MOD 16 migration  (tai-api WORK_SCHEDULES_PARTITION_DESIGN_FINAL_v1 확정본)
        ↓
WS-7  child composite FK rewire
        ├─ work_assignments        (기존 schedule_id FK → (schedule_id, factory_id) composite)
        ├─ safety_inspections      (assignment_id companion (schedule_id, factory_id))
        └─ equipment_checkins      (★ 신규 컬럼 아님 — existing factory_id 이용한 FK rewire 대상)
        ↓
WS-8  patched writers deploy / validation
        ↓
WS-9  WRITE ON
```
주의 = 본 WP는 work_schedules 부모 파티션을 재설계하지 않음(확정본 참조). 위 순서만 통합.
[직독] 모든 work_schedules INSERT creator는 이미 factory_id 세팅 → ws 자체 companion gap 없음. gap = child(wa/si)만.

---

## 2. work_assignments UNIQUE 전환 (WA maintenance atomic transition)

**code-first 불가**: `ON CONFLICT (schedule_id, scheduled_date)` conflict target은 그 조합의 UNIQUE arbiter가 **먼저 존재**해야 동작.
그러나 UNIQUE를 먼저 만들면 구 plain INSERT writer 재실행이 중복 위반. → arbiter↔writer 상호선행 사이클 = **maintenance 원자전환**으로만 해소.

```
WA-0  patched code 준비 (ON CONFLICT + factory_id) — 아직 deploy 금지
WA-1  duplicate precheck = 0  [실측 wa_dup(schedule_id,scheduled_date)=0]
WA-2  WRITE OFF  (generate_daily_assignments 정지 · legal_engine_patch.auto_assign 차단 · work_schedules._apply_one_update assignment sync 차단)
WA-3  UNIQUE(schedule_id, scheduled_date) 적용
WA-4  patched writers deploy (gen_daily · auto_assign · _apply_one_update)
WA-5  smoke / idempotency test (2회 재실행 중복 0)
WA-6  WRITE ON

의미 구분:
  UNIQUE          = final database integrity guard (마지막 방어선)
  idempotent 동작  = writer behavior (ON CONFLICT DO NOTHING)
  (UNIQUE = idempotency 아님)
```

---

## 3. P0-3 사이클 제거 (CD5-4 의존 삭제)

```
P0-3A  CURATED MAPPING DECISION  = 인간검수 artifact · mutation 0
P0-3B  CURATED MAPPING APPLY     = 승인된 mapping DML · 개별 mutation 승인 필요
CD5-4  CURATED ADMIN WORKFLOW    = 반복운영 편의도구 · **P0-3A/B 선결 아님**

사이클 제거: (구) CD5-4 가 P0-3 의 선결이던 역방향 의존 삭제 — 이제 CD5-4 는 독립(운영도구)
go-live: P0-3A + P0-3B 완료 → CD5-2 사용 가능
```

---

## 4. Dependency DAG (writer-safe)

```
[PHASE 0]
  P0-1 RETENTION POLICY RESOLUTION(법령 직독) ─► B2-2/B2-3-retention
  P0-2 bridge 323 MAPPED→NEEDS_HUMAN_REVIEW (DML) ─► C3-4
  P0-3A curated mapping decision(인간검수) ─► P0-3B curated apply(DML) ─► CD5-2(go-live)

[PHASE 1 · additive nullable]
  S1-1 rdd.source_inspection_id(+FK RESTRICT) ─► S1-2 UNIQUE(source_inspection_id, form_schema_id) ─► CD5-2/CD5-3
  S1-3 si.submitted_by(+FK users) ─► CD5-1
  S1-4 si.factory_id(companion) ─► WS-3
  S1-5 si.retention_until ─► B2-2
  S1-6 work_assignments.factory_id(companion) ─► WS-1/WS-2   ★신규(추가됨)

[PHASE 2 · backfill]  (BACKFILL_VALIDATION_PLAN)
  B2-si.factory_id · B2-wa.factory_id · B2-retention · B2-3 results 검증(NULL 0)
  submitted_by/source_inspection_id = 무backfill(NULL 유지) · runtime_form_schema_id = P0-3(HUMAN REVIEW)

[PRE-CONSTRAINT WRITER PATCH]  (constraint 前 필수)
  CD5-1(WP-SI) worker_check + inspection_checklist : auth/identity/submitted_by/factory_id
      ─► C3-7  (C3-5/C3-6는 B2-3 소관, WP-SI 무관 — 두 writer 이미 checked_at·inspection_id 세팅[직독])
  WA 전환(maintenance) work_assignments 3 creator: §2 WA-0..WA-6 (C3-8 UNIQUE = WA-3, WRITE OFF 구간 내)
  bridge 하드닝(writer patch 아님 — DB constraint/data task) ─► C3-1..4

[PHASE 3 · constraints]
  B2-3 ─► C3-5(results.inspection_id NN) · C3-6(results.checked_at NN)
  C3-6 ─► PT4-1
  CD5-1 ─► C3-7(results.item FK RESTRICT)
  P0-2 ─► C3-4(bridge CHECK)
  C3-1/C3-2 bridge FK · C3-3 bridge UNIQUE(set)
  C3-8(wa UNIQUE) = §2 WA-3 (maintenance 원자전환 내부 — code-first 아님)

[PHASE 4 · partition]
  C3-5/C3-6/C3-7 ─► PT4-1 results RANGE(checked_at) MONTHLY  (TEST_ROLLBACK §F 운영계약)

[PHASE 5 · code 잔여]
  CD5-2 create_document_from_inspection  ← S1-1/2 + P0-3A/B
  CD5-3 confirm source_trace_snapshot    ← CD5-2 + S1-1
  CD5-4 curated admin workflow(운영도구)  ← P0-3 선결 아님(독립)

[PHASE 6 · HOLD] Controlled First Confirm ← PHASE 1~5 전부 SUCCESS + 명시 승인

[WS-MIG] §1 순서 (child companion → WRITE OFF → parent HASH → child FK rewire → deploy → WRITE ON)
```

---

## 5. 임계 순서 hazard (전수)
```
H1  P0-2(323 revert) → C3-4(bridge CHECK)                         [실측 323]
H2  WA maintenance 전환 §2 (WA-0 준비 → WA-2 WRITE OFF → WA-3 UNIQUE → WA-4 deploy → WA-6 WRITE ON) — arbiter↔writer 사이클
H3  CD5-1(WP-SI item 처리) → C3-7(results item FK RESTRICT)
H4  bridge 하드닝(구조/데이터) → C3-1..4
H5  P0-3A(결정) → P0-3B(적용) → CD5-2(go-live)                     [cycle 제거]
H6  WS-1..WS-4(child companion+backfill+writer ready) → WS-5 WRITE OFF → WS-6 HASH → WS-7 child FK rewire(wa/si/equipment_checkins) → WS-8 deploy → WS-9 WRITE ON
B2-3 → C3-5/C3-6 · C3-6 → PT4-1  (WP-SI 무관)
```
mutation 0. 각 노드 execution 시 개별 승인.
