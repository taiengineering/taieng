# INSPECTION_DOCUMENT_TEST_ROLLBACK_PLAN_v1  (CANONICAL · WP-DATA-ARCH-03 PASS/CLOSED)

```
WP    = WP-DATA-ARCH-03 · CORR-02
STAGE     = CANONICAL DOCUMENT (post CORR-02 PASS · WP-DATA-ARCH-03 CLOSED)
MODE  = PLANNING ONLY · MUTATION 0
공통   = SUCCESS 아니면 다음 단계 금지 · FAILED=즉시 롤백 · 각 단계 RECEIPT(전/후·SHA·판정) · 불변가드(company_scope/permission_guard/C-2/engine) 회귀=즉시 롤백
```

테스트 계층 = UNIT / INTEGRATION / DB INTEGRITY / REGRESSION / ROLLBACK.

---

## §A. UNIT
```
- identity/delegation: inspector_id=users.id 확정 · roster fallback 폐기 · submitted_by=current · impersonation guard
- retention resolver: 유형/법령→기간 매핑 · 미해소=NULL fail-closed · deletion_allowed=false 존중
- mapping validation: curated mapping만 승격 · 이름 유사도 auto-map 거부
- orchestration idempotency: 동일 inspection 중복 create_document 방지(UNIQUE(source_inspection_id, form_schema_id))
- WA 멱등 동작: ON CONFLICT(schedule_id, scheduled_date) DO NOTHING 단위 동작 · factory_id 파생
```

## §B. INTEGRATION
```
- worker_check 제출: 토큰없음 401 · checked_at·inspection_id 세팅 · inspector_id=users.id · submitted_by 세팅
- inspection_checklist /start·/result: 인증+scope · checked_at·inspection_id 세팅 · submitted_by 세팅 · item_id 유효 ref만
- inspection → document: DOCUMENTABLE INSPECTION v1(schedule-backed)만 생성 · unresolved(scope/schema/curated) fail-closed
- duplicate document create: 동일 source 재요청 → UNIQUE 차단(중복 문서 0)
- cross-company: 타사 inspection→document 차단(scope 해소 fail-closed)
- unscheduled fail-closed: schedule 없는 inspection → 문서 미생성
```

## §C. DB INTEGRITY
```
- FK: source_inspection_id(RESTRICT) · results.item(RESTRICT) · bridge FK×2 · wa/si/equipment_checkins composite FK(rewire 후)
- UNIQUE: rdd(source_inspection_id, form_schema_id) · bridge(inspection_set_id) · work_assignments(schedule_id, scheduled_date)
- CHECK: bridge(MAPPED→schema NOT NULL) — P0-2 후 위반 0
- NOT NULL: results.inspection_id · results.checked_at (B2-3 검증 후)
- partition routing: checked_at 값 → 올바른 월 파티션 · 범위밖 → DEFAULT
- full-row equality: 아래 §D 파티션 절차
```

## §D. REGRESSION (필수 — 전 ACTIVE writer 무회귀)
```
safety writers:
  worker_check (제출·recent·history)
  inspection_checklist (/start·/result·generate-schedules·complete)
worker app:
  worker history · InspectionFetcher(문서 fetch) · Document Confirm 05B
work_assignments writers(전 ACTIVE):
  generate_daily_assignments() (재실행 멱등)
  legal_engine_patch auto-assign (배치 멱등)
  work_schedules.py assignment sync (INSERT/UPDATE/CANCELLED)
  overdue_checker (OVERDUE·resolve UPDATE)
work_schedules writers(전 ACTIVE):
  schedules.py · law_engine.py · anchors.py · inspection_checklist(generate/complete)
  · legal_engine_patch(generate-from-diagnosis) · schedule_engine · event_trigger
  · equipment_engine_svc(repair) · construction_svc(auto)
  (schedule_pipeline = LEGACY 중복경로 — 회귀대상 아님, 단 shadow 여부 확인)
각 writer: 신규 constraint/partition 적용 후 INSERT/UPDATE smoke 통과 + /health 200
```

## §E. ROLLBACK
```
additive(PHASE1)  = DROP COLUMN/CONSTRAINT (nullable, 데이터 무손실)
backfill(PHASE2)  = SET NULL 단일 TX 롤백
writer patch      = git revert (해당 파일만)
constraint(PHASE3)= DROP CONSTRAINT (즉시, 데이터 무변)
partition(PHASE4) = old 원본 _bak swap-back (아래 rollback anchor)
code(PHASE5)      = git revert
old table restoration · FK restoration · code rollback 호환 · 신규 유입행 reconciliation 포함
```

---

## §F. RESULTS PARTITION 운영계약 (최종 확정)

```
[확정] partition interval    = MONTHLY  RANGE(checked_at)   (retention 3Y/5Y·DROP eligibility 세분화 근거; 5년 ≈ 60 파티션 관리가능)
[확정] DEFAULT partition     = YES      (범위밖·late-arriving 포착; DEFAULT는 절대 DROP 안 함 = fail-safe)
[확정] future partition 생성  = 유지보수 잡이 N+1개월 파티션을 사전 생성(owner=Claude MCP apply_migration, 월 1회 선행). 미생성 시 DEFAULT가 흡수(무손실)
[확정] late-arriving checked_at = DEFAULT 파티션에 안착. 과거 파티션 없어도 손실 0. DEFAULT는 DROP 대상 아님 → 오삭제 없음(fail-safe)
[확정] concurrent write 전략  = MAINTENANCE WINDOW (현 8행 trivial; swap 중 WRITE OFF. dual-write 불채택 — 복잡도>이득)
[확정] DEFAULT reconciliation = DEFAULT는 fail-safe landing zone(임시)이지 영구 cold archive 아님.
       순서 = MOVE OUT → CREATE/ATTACH PARTITION → MOVE IN  (★ CREATE 먼저 금지: DEFAULT에 대상범위 행이 있으면 새 range 파티션 ATTACH가 DEFAULT 제약과 충돌)
       future partition 생성(N+1):
         DEFAULT의 target-range count 확인
           = 0 → 월 파티션 정상 생성/attach
           > 0 → MAINTENANCE/WRITE OFF → target rows staging 복사 → staging vs source full-row equality
                 → DEFAULT에서 target rows 제거(MOVE OUT) → target month 파티션 생성/attach → staging rows 새 파티션 INSERT(MOVE IN)
                 → DEFAULT target-range count = 0 재확인 → target 파티션 full-row equality → WRITE ON
       DEFAULT 상주 행은 retention_until 기준 삭제만 개별 가능(파티션-whole DROP 대상 아님). DEFAULT 자체는 DROP 금지.
[확정] rollback anchor 보존   = old _bak 테이블을 (a)swap 후 full-row equality PASS + (b)PHASE 6 첫 Confirm 성공 검증까지 유지. 그 전 DROP 절대 금지
```

### PT4-1 무손실 swap 절차 + 검증 (테이블명 명시)
```
명칭  = old_current = safety_inspection_results (현 canonical) · new_shadow = safety_inspection_results_new · _bak = safety_inspection_results_bak(swap 후 생성)
1) new_shadow(safety_inspection_results_new) PARTITION BY RANGE(checked_at) 생성 · PK(id, checked_at) · 월 파티션 + DEFAULT
2) PRE-state 캡처(아래 preservation) → old_current → new_shadow 데이터 복사 INSERT ... SELECT
3) new_shadow LOCAL INDEX(inspection_id, created_at) 생성 · outgoing FK(inspection_id→safety_inspections) 재생성
4) PRE-SWAP full-row equality (★ 이 시점 백업본 미생성 — 현 canonical old table 사용):
     SELECT count(*) FROM (TABLE safety_inspection_results EXCEPT TABLE safety_inspection_results_new) d;  = 0   -- old_current EXCEPT new_shadow
     SELECT count(*) FROM (TABLE safety_inspection_results_new EXCEPT TABLE safety_inspection_results) d;  = 0   -- new_shadow EXCEPT old_current
     + WHERE inspection_id=? 조회 동일 · 파티션 routing 표본
   ↓ PASS
5) 트랜잭션 내 RENAME swap: safety_inspection_results → safety_inspection_results_bak · safety_inspection_results_new → safety_inspection_results
6) POST-SWAP full-row equality (★ swap 후부터 _bak 참조):
     SELECT count(*) FROM (TABLE safety_inspection_results_bak EXCEPT TABLE safety_inspection_results) d;  = 0
     SELECT count(*) FROM (TABLE safety_inspection_results EXCEPT TABLE safety_inspection_results_bak) d;  = 0
7) PRE-state 재적용(아래) → /health 200 · 대상 reader(InspectionFetcher) 무회귀
검증 분리 = PRE-SWAP equality(old_current vs new_shadow) + POST-SWAP equality(_bak vs canonical) — 두 번
```

### PRE-state preservation (swap 전 캡처 → 후 재적용, exact-copy)
```
owner · RLS enabled/forced · policies · grants(+ grant option) · comments · indexes · constraints · triggers
(캡처 = pg_catalog introspection 스냅샷; 재적용 후 diff 0 확인)
```

### 롤백(파티션) — WRITE ON 기준 2분기
```
ROLLBACK-A (WRITE ON 前 = swap 직후~검증구간): 신규 파티션에 신규 유입 없음
  TRIGGER = full-row equality ≠ 0 / 조회 상이 / swap 오류
  STEP    = _bak 유지 상태에서 즉시 RENAME swap-back (원복). 유입 없으므로 reconciliation 불요
  POST    = old 원복 · 앱 정상 · 원인분석 후 재시도

ROLLBACK-B (WRITE ON 後 = 신규 파티션에 유입 발생): 단순 swap-back 시 유입행 소실 → 금지
  STEP 1 = WRITE OFF (유입 정지)
  STEP 2 = reconciliation 산출:
             new EXCEPT old_bak  = WRITE ON 이후 신규 유입행(보존 대상)
             old_bak EXCEPT new  = swap 후 유실/변경행(정합 확인)
  STEP 3 = PK 충돌 precheck (old PK=(id) vs new PK=(id, checked_at) 차이):
             SELECT id FROM new_parent GROUP BY id HAVING count(*)>1;  = 0
             (신규 파티션은 동일 id가 다른 파티션에 공존 가능 → old (id) 단일 PK로 되돌릴 때 충돌. 위 0 아니면 swap-back 금지·수동해소)
  STEP 4 = 신규 유입행(new EXCEPT old_bak)을 old_bak에 병합(id PK 충돌 0 확인 후)
  STEP 5 = full-row equality 재확인(old_bak' EXCEPT new =0 / new EXCEPT old_bak' =0) → RENAME swap-back
  POST    = 유입행 무손실 원복 확인 · 앱 정상
공통 = old _bak DROP은 rollback anchor 조건 충족 전 금지
```

---

## §G. Controlled First Confirm (PHASE 6, HOLD)
```
전제 = PHASE 1~5 전부 SUCCESS + 명시 승인. 첫 confirm = 단건 controlled → archive UNIQUE/immutable/confirmed_by 검증 후 확대.
archive immutable → 잘못된 confirm 사전 차단(사전검증 최우선). 롤백 = confirm 이전(DRAFT) 유지.
```
