# INSPECTION_DOCUMENT_COMPATIBILITY_MATRIX_v1  (CANONICAL · WP-DATA-ARCH-03 PASS/CLOSED)

```
WP        = WP-DATA-ARCH-03 · CORR-02  (Writer Inventory COMPLETE + 4-state Compatibility)
STAGE     = CANONICAL DOCUMENT (post CORR-02 PASS · WP-DATA-ARCH-03 CLOSED)
SOURCE API SHA     = e1506aa45d3b35bf4d99d3c123600e9f19ab6996
CANONICAL ARCH SHA = 5d87ac7063157db98b6965067095b35ef561f383
MODE      = PLANNING ONLY · MUTATION 0
근거표기   = [실측]=DB · [직독]=repo 본문 직독 확인
```

원칙: **object별 writer 전수를 확정·patch 완료하기 전에는 어떤 constraint/partition도 적용하지 않는다.**

---

## STEP 0 — WRITER INVENTORY (전수 직독, COMPLETE)

분류 = ACTIVE / LEGACY / NOT-WRITER / DB-FUNC. 모든 항목 본문 직독 확정.

### safety_inspections / safety_inspection_results
```
routers/worker_check.py            [직독] ACTIVE  (worker app 제출)
  auth=_optional_auth(Optional, 토큰없어도 제출·current_user 미사용) · inspector_id=phone→users, 없으면 worker_registry.id fallback(FK-break)
  si INSERT {inspector_id, inspection_date=now, status_code, assignment_id=schedule_ref(work_assignments.id→work_schedules.id 변환)}
  results INSERT {inspection_id✓, item_name(서버마스터), result_code, value_text, note, checked_at=now✓, [item_id 검증통과시]}
  → checked_at·inspection_id 항상 세팅. factory_id·submitted_by 미세팅.
routers/inspection_checklist.py    [직독] ACTIVE  (v1.5.0 관리경로, get_current_user+company_scope 보유)
  /start   si INSERT {assignment_id=work_schedule_id, inspection_date, status_code='in_progress'} — inspector_id 미세팅(= NULL 1건 원천[실측])
  /result  results INSERT {inspection_id✓, inspection_set_item_id(무검증), result_code, note, photo_url, checked_at=now✓}
  work_schedules writer 겸함(아래)
readers: services/document_engine/fetchers/inspection_fetcher.py [직독] SYSTEM-L reader (WHERE inspection_id ORDER BY created_at)
```

### work_assignments
```
INSERT creators (전부 factory_id 미기록·비원자 → WA 전환(§MIGRATION §2) + factory_id companion 대상):
  public.generate_daily_assignments()      [실측 DB-FUNC] ACTIVE(cron gated)
    plain INSERT {id, schedule_id, asset_id, assigned_user_id, scheduled_date=current_date, status_code='READY'} FROM work_schedules WHERE active_yn=true
    ON CONFLICT 없음 · factory_id 없음 · duplicate handling 없음
  routers/legal_engine_patch.py :: auto_assign_schedules  [직독] ACTIVE  (POST /work-schedules/auto-assign)
    batch INSERT {schedule_id, assigned_user_id=manager, scheduled_date=planned_date|today, status_code='PENDING', created_at}
    ON CONFLICT 없음 · factory_id 없음 · auth/scope 없음
  routers/work_schedules.py :: _apply_one_update  [직독] ACTIVE  (batch-update/bulk-assign/patch 경유)
    존재체크 후 없으면 INSERT {schedule_id, assigned_user_id, scheduled_date=today, status_code=ready, created_at}
    존재체크 가드(원자적 아님) · factory_id 없음 · auth+company_scope 보유
UPDATER (creator 아님):
  routers/work_schedules.py        [직독] ACTIVE  (assignment sync UPDATE, null→CANCELLED)
  routers/overdue_checker.py       [직독] ACTIVE  (status OVERDUE·overdue_level·resolved UPDATE; /check=머신 무인증, 그외 인증+scope)
NOT-WRITER (read-only): routers/worker_assets.py [직독] (list/items select) · routers/worker_check.py [직독] (id 변환 read)
```

### work_schedules  (부모 파티션 HASH(factory_id) 대상 — 별도 선행 migration)
```
INSERT creators (전부 factory_id 세팅 → ws companion gap 없음):
  services/inspection_sets_svc/schedules.py   [직독] ACTIVE  (anchor mode insert `_build_next_schedule_row`; law_engine mode는 law_engine.py 위임; 기존 SCHEDULED 가드·force시 delete-insert)
  services/inspection_sets_svc/law_engine.py  [직독] ACTIVE  (LAW_ENGINE mode `_build_law_engine_row`, 기존 LAW_ENGINE+PENDING dedup 가드)
  services/inspection_sets_svc/anchors.py     [직독] ACTIVE  (anchor 확정 set/patch delete(SCHEDULED)+insert `_build_next_schedule_row`)
  routers/inspection_checklist.py             [직독] ACTIVE  (generate-schedules bulk insert factory_id✓ · complete 다음회차 insert factory_id✓)
  routers/legal_engine_patch.py :: generate_schedules_from_diagnosis [직독] ACTIVE (진단→insert, source_type='LEGAL', factory_id✓, rule_code dedup 가드)
  routers/schedule_engine.py                  [직독] ACTIVE  (POST /schedule-engine/generate/{id} 단건 insert factory_id✓, (set,planned_date) dedup, auth 없음)
  routers/event_trigger.py                    [직독] ACTIVE  (source_type='EVENT' insert factory_id✓, 30일 window dedup, auth 없음; source=diagnosis_rule_results)
  services/equipment_engine_svc.py            [직독] ACTIVE  (run_patch_asset 설비수리 재스케줄 delete+insert `_build_schedules_for_repair`, factory_id via iset)
  services/construction_svc.py                [직독] ACTIVE  (run_generate_schedules 건설 자동진단→insert factory_id✓, rule_code dedup)
  routers/schedule_pipeline.py :: generate_schedules_from_diagnosis [직독] LEGACY (legal_engine_patch와 **동일 route path** POST /legal-engine/generate-schedules/{factory_id}, v1.0.0 구버전 → 등록순서상 shadowed; factory_id✓)
UPDATER: routers/work_schedules.py [직독] ACTIVE (batch-update/bulk-assign/confirm/patch UPDATE; row 생성 안 함)
NOT-WRITER(read): worker_check.py · worker_assets.py · notifications.py · overdue_checker.py · schedule_pipeline.trigger_due_alerts
```

### runtime_document_data / runtime_document_archive
```
services/document_engine/document_engine_svc.py (create_document)  [정본] ACTIVE
services/document_engine/document_confirm_svc.py (confirm→archive)  [정본] ACTIVE
(신규 설계) create_document_from_inspection command  = CD5-2
```

### runtime_inspection_bridge
```
routers/inspection_bridge.py  [정본] = READ-ONLY STALE CONTRACT · NOT WRITER (auto-map 미수행·read/contract 전용)
bridge 대상 작업 = 구조 하드닝(DB constraint/data task) + curated mapping apply(승인 DML) + admin workflow(운영도구) — writer patch 아님
```

**[COMPLETE] 전 writer 본문 직독·전수 분류 확정 — 미확정/보류/이월 표기 없음.**
핵심 결론:
- 모든 work_schedules INSERT creator = factory_id 세팅 → **ws companion gap 없음**.
- companion gap = **work_assignments.factory_id**(창 3개 전부 미기록) + **safety_inspections.factory_id**(창 2개 미기록).
- WA 전환 대상 = work_assignments INSERT creator 3개(gen_daily·auto_assign·_apply_one_update) — 전부 ON CONFLICT/원자성 없음 → maintenance 전환(WA-0..WA-6).

---

## §1. WRITER × 신규제약 영향표 (patch 소요)

```
worker_check.py / si+results / INSERT [직독]
  checked_at·inspection_id 이미 세팅 → C3-5/6 호환(패치 불요). 위험=auth optional·roster.id→inspector_id FK-break
  patch=auth REQUIRED · inspector_id=users.id(roster 폐기) · +submitted_by · +factory_id(companion) → CD5-1
inspection_checklist.py / si+results / INSERT+UPDATE [직독]
  /result checked_at·inspection_id 세팅 → C3-5/6 호환. /start inspector_id NULL(정상). 위험=item_id 무검증→C3-7시 INSERT 실패(동작변경)
  patch=+submitted_by · +factory_id · /start inspector_id 처리 · company_scope 불변 → CD5-1 / C3-7 게이트
generate_daily_assignments() / work_assignments / INSERT [실측]
  위험=재실행 중복→C3-8 UNIQUE 위반 함수 실패. patch=ON CONFLICT DO NOTHING + factory_id → WA 전환(WA-0..WA-6, C3-8=WA-3)
legal_engine_patch.auto_assign / work_assignments / INSERT [직독]
  위험=배치 중복→UNIQUE 위반. patch=ON CONFLICT + factory_id → WA 전환(maintenance)
work_schedules._apply_one_update / work_assignments / INSERT [직독]
  위험=존재체크 비원자→경합시 중복→UNIQUE 위반. patch=ON CONFLICT + factory_id → WA 전환(maintenance)
work_schedules INSERT creators(10) / work_schedules / INSERT [직독]
  factory_id 이미 세팅 → HASH 파티션 라우팅 안전. patch 불요(단 WS-MIG 시 child FK rewire와 별개)
document_engine_svc / runtime_document_data / INSERT [정본]
  신규 컬럼 nullable → 무영향. source는 orchestration만 세팅(CD5-2)
inspection_bridge.py / runtime_inspection_bridge / READ-ONLY
  writer 아님. bridge 하드닝(C3-1..4)은 DB constraint/data task로 수행(코드 patch 아님)
```

---

## §2. 4-STATE COMPATIBILITY MATRIX

각 변경을 (OLD DB=현스키마 / NEW DB=변경후) × (OLD CODE=현writer / NEW CODE=patch후) 4상태로 판정.
판정값 = SAFE / CONDITIONAL / BREAKS / N/A. Deployment Rule = schema-first / code-first / maintenance-only.

| Change | OLD DB+OLD CODE | OLD DB+NEW CODE | NEW DB+OLD CODE | NEW DB+NEW CODE | Deployment Rule |
|---|---|---|---|---|---|
| submitted_by (si +col nullable, FK users) | SAFE(현행) | **BREAKS**(NEW code가 없는 컬럼에 write→실패) | SAFE(구writer NULL 미기입) | SAFE | **schema-first** (스키마 先배포, 무중단) |
| safety_inspections.factory_id (companion nullable) | SAFE | **BREAKS**(NEW code write→컬럼 부재 실패) | SAFE(구writer 미기입) | SAFE | **schema-first** |
| retention_until (si +col nullable) | SAFE | **BREAKS**(resolver가 write 시 컬럼 부재 실패) | SAFE(구writer 미기입) | SAFE(미해소 NULL fail-closed) | **schema-first** (S1-5 先, resolver 後) |
| source_inspection_id (rdd +col nullable, FK RESTRICT) | SAFE | **BREAKS**(orch NEW code write→컬럼 부재 실패) | SAFE(구writer 미기입) | SAFE | **schema-first** (S1-1 先, CD5-2 後) |
| work_assignments.factory_id (companion nullable) | SAFE | **BREAKS**(WA patched writer write→컬럼 부재 실패) | SAFE(구 3창 미기입) | SAFE | **schema-first** (S1-6 先배포) |
| work_assignments UNIQUE(schedule_id, scheduled_date) | SAFE(현행) | **BREAKS**(NEW writer ON CONFLICT arbiter 부재→실패) | **CONDITIONAL/BREAKS**(구 plain INSERT 재실행→중복 위반) | SAFE(WA-6 WRITE ON 후) | **maintenance-only** (WA-0..WA-6 atomic transition — arbiter↔writer 상호선행 사이클) |
| work_schedules composite PK/FK (HASH 파티션 전환) | N/A | N/A | **BREAKS**(child 단일 FK·비파티션 참조 깨짐) | SAFE(child companion+FK rewire 후) | **maintenance-only** (WRITE OFF→migrate→rewire→WRITE ON) |
| safety_inspection_results PK(id, checked_at) (RANGE 파티션) | N/A | N/A | **BREAKS**(checked_at NULL 존재 시)·CONDITIONAL(NULL 0이면 재빌드 필요) | SAFE(C3-6 후 재빌드) | **maintenance-only** |
| results.inspection_id / checked_at NOT NULL (C3-5/C3-6) | SAFE([실측 NULL 0]) | SAFE | SAFE(두 writer 이미 세팅) | SAFE | **schema-first** (writer 무관, B2-3 gate) |
| results.item FK RESTRICT (C3-7) | SAFE([실측 위반 0]) | SAFE | **CONDITIONAL**(inspection_checklist 무검증 잘못된 ref INSERT→실패) | SAFE(patch 후) | **code-first** (데이터정합+앱 오류처리→FK) |
| bridge FK×2 (C3-1/C3-2) | SAFE([실측 위반 0]) | N/A(bridge writer 없음) | SAFE | SAFE | **schema-first** |
| bridge UNIQUE(set) (C3-3) | SAFE([실측 위반 0]) | N/A | SAFE | SAFE | **schema-first** |
| bridge CHECK(MAPPED→schema NN) (C3-4) | **BREAKS**([실측 323 위반]) | N/A | SAFE(P0-2 revert 후) | SAFE | **data-first** (P0-2 → CHECK) |

**결정 요약:**
```
schema-first (nullable additive — 스키마 先배포, 그 다음 NEW code. OLD DB+NEW CODE=BREAKS이므로 순서 역전 금지)
   = submitted_by · si.factory_id · retention_until · source_inspection_id · wa.factory_id · C3-5/6 · bridge FK/UNIQUE
data-first  = bridge CHECK (P0-2 323 revert 선행)
code-first  = results item FK RESTRICT (inspection_checklist 무검증 경로 데이터정합+앱 오류처리 선행)
maintenance-only = work_assignments UNIQUE (WA-0..WA-6: arbiter↔writer 상호선행 사이클 → WRITE OFF 원자전환)
                 · work_schedules HASH 전환 + child composite FK rewire · results RANGE 파티션 재빌드
```
