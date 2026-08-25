# WP-PERSISTENCE-02 — FINAL DESIGN DECISION

- 작성일: 2026-08-25
- 모드: READ-ONLY DESIGN 완료. mutation 0. repo commit 0 (승인 대기).
- ANALYSIS BASELINE: tai-api@`2b10e3a674cdcd607389ae468279283eb0569609`
- REVIEW-TIME MAIN: tai-api@`2780acf8095b6aa1b87e3a9936ac9ee08ac790e8`
  (DRIFT = +1 commit, `routers/building_register.py` only,
   WP-PERSISTENCE-02 relevant-code diff 0, re-analysis not required)
- DB: `vwlahtguyggrhvslabax`

---

## 1. 한 문장 결론

inspection.id 확보(result·worker-submit 경로)·companion 파생·tenant 권위는 설계
가능하고 actor 권위는 부분 확정(PARTIAL)이나,
**form_schema_id 의 정본(SoT)이 존재하지 않아**(B1) source_anchor writer 를
완성할 수 없다. → **IMPLEMENTATION READINESS = BLOCKED.**

---

## 2. DESIGN DECISION TABLE

| 항목 | 판정 |
|---|---|
| Inspection writer trace | **PARTIAL** — explicit id: result + worker-submit / manual-complete 미보장 |
| Trigger | **PARTIAL** — result-completion·worker-submit=candidate / manual-complete=unsuitable |
| Source inspection ID | explicit inspection.id ONLY (추론 전면 금지) — result/submit 경로에서 보장 |
| Form schema mapping SoT | **NOT FOUND → B1 (PRIMARY)** |
| Cardinality | NOT PROVEN (UNIQUE 는 N 허용, intended 미확정) |
| Idempotency | DB UNIQUE GUARDED (후보 확정, 적용은 B1 종속) |
| Transaction semantics | DECISION REQUIRED (근거상 inspection-authoritative 우세) — B2 OPEN |
| Tenant source | server-derived: inspection → factory → company (client 미신뢰) — CONFIRMED |
| Actor source | **PARTIAL** — 인증 있으면 user.id / 미인증 worker 경로는 NULL |
| runtime_data_json scope | 이번 WP WRITE 안 함(자동채움 금지) — CONFIRMED |
| Legacy backfill | 제외(별도 WP) — CONFIRMED |
| Implementation files | 확정 불가 (B1). 예상 surface 만 윤곽 |
| Test strategy | T1–T10 설계 완료(아래), 실행은 B1 종속 |

---

## 3. TEST CONTRACT (STEP 18) — 설계 완료 (실행은 B1 이후)

- T1 정상 inspection(완료) → anchor row 생성, source_inspection_id 정확
- T2 같은 inspection+schema 재호출 → duplicate 0 (UNIQUE guard)
- T3 없는 inspection_id → reject
- T4 없는/미정 form_schema_id → reject (B1 상태에선 이 입력 자체가 불가)
- T5 다른 factory/company mismatch(client 위조) → server 파생값으로 reject
- T6 source_inspection_id 값이 실제 현재 inspection.id 와 일치
- T7 기존 unrelated runtime_document row 불변
- T8 legacy NULL source row 불변 (backfill 없음)
- T9 concurrent duplicate attempt → 1 logical document (race → UNIQUE)
- T10 document anchor 실패 시 inspection 완료 semantics 검증 (A/B 결정에 따름)

실 production synthetic data 사용 금지. test DB / mock / rollback 환경 기준.

---

## 4. BLOCKER 분류 (STEP 20)

```
B1 FORM_SCHEMA_MAPPING_MISSING   = CONFIRMED / PRIMARY BLOCKER
                                   (02A STEP-1 후: DESIGN RESOLVED / DATA POPULATION BLOCKED)
B3 INSPECTION_ID_NOT_AVAILABLE   = CONFIRMED
                                   (only for /inspection/complete/{work_schedule_id};
                                    result·worker-submit 경로만 anchor trigger 로 삼으면 회피 가능)
B2 TRANSACTION_BOUNDARY_UNCLEAR  = OPEN (명시적 DB atomic transaction 경계 없음;
                                    A안 택할 경우 래핑 필요)
B7 (LEGACY_BACKFILL)             = 해당 없음 (이번 WP 제외로 정리)
```

### 02A STEP-1 확정 (B1 DESIGN RESOLVED)
```
MAPPING SoT   = runtime_inspection_bridge.runtime_form_schema_id
MAPPING UNIT  = inspection_set_id
CARDINALITY   = inspection_set → schema 0..1
RUNTIME ELIGIBLE = APPROVED_FOR_RUNTIME_USE ONLY
CURRENT: bridge schema_id 0/324, runtime-approved schema 0/323
자동매핑 근거 = exact key 부재 → AUTO_APPROVABLE 0, 전건 HUMAN_REVIEW
→ B1 DATA POPULATION = BLOCKED (운영자 정책결정 선행 필요)
```

B1 이 여전히 최상위 blocker. B3 은 trigger 경로 선택으로 회피 가능하므로 B1 만큼
근본적이지 않다. 어느 경우든 지시서 §20 대로 **구현 지시서를 만들지 않고** blocker
decision 을 제출한다.

---

## 5. B1 해제를 위해 운영자가 정해야 할 것

1. inspection_set → runtime_form_schema.id 매핑의 **정본 주체/시점**
   (runtime_inspection_bridge.runtime_form_schema_id 를 무엇이 채우는가)
2. 매핑 **단위**: inspection_set / legal_rule / obligation 중 무엇인가
3. 한 inspection_set 이 **복수 form_schema** 를 갖는가 (→ cardinality 연동)

위 3개가 확정되면 SOURCE_ANCHOR_CONTRACT 의 form_schema_id 행이 채워지고,
IDEMPOTENCY → TRANSACTION → CARDINALITY 가 순차 확정되어 구현 지시서 작성이 가능해진다.

---

## 6. STOP GATE (지시서 §23 형식)

```
WP-PERSISTENCE-02

INSPECTION WRITER TRACE       = PARTIAL
                                explicit id available on result + worker submit
                                not guaranteed on manual complete
FORM SCHEMA MAPPING           = NOT FOUND
SOURCE ID CONTRACT            = explicit inspection.id ONLY
CARDINALITY                   = NOT PROVEN
TRIGGER                       = PARTIAL
                                result-completion / worker-submit = candidates
                                manual-complete = unsuitable as-is
IDEMPOTENCY                   = DB UNIQUE GUARDED candidate
TRANSACTION SEMANTICS         = DECISION REQUIRED
TENANT AUTHORITY              = CONFIRMED / server-derived
ACTOR AUTHORITY               = PARTIAL
                                authenticated user when available
                                unauthenticated worker path exists
PAYLOAD BOUNDARY              = CONFIRMED (no runtime_data_json auto-fill)
IMPLEMENTATION SCOPE          = BLOCKED

IMPLEMENTATION READINESS
= BLOCKED

Blockers:
  B1 FORM_SCHEMA_MAPPING_MISSING = CONFIRMED / PRIMARY
  B3 INSPECTION_ID_NOT_AVAILABLE = CONFIRMED (manual complete path only)
  B2 TRANSACTION_BOUNDARY_UNCLEAR = OPEN

CODE MUTATION = 0
DB MUTATION   = 0
API MUTATION  = 0
REPO MUTATION = 0
DEPLOY        = 0
```

## 7. FINAL PASS GATE 체크 (§22)

```
[x] inspection writer path 확정 (2 writers)
[~] explicit inspection.id 확보 경로 확정  ← result/worker-submit YES, manual-complete NO (B3)
[ ] form_schema mapping SoT 확정      ← B1 미해제 (PRIMARY)
[ ] cardinality 확정                  ← B1 종속
[~] trigger 확정                      ← 후보 2경로 있으나 manual-complete 부적합 + B1 종속
[~] idempotency 확정                  ← 후보 확정, B1 종속
[ ] failure semantics 확정            ← DECISION REQUIRED (B2 OPEN)
[x] tenant source 확정                ← server-derived CONFIRMED
[~] actor source 확정                 ← PARTIAL (미인증 worker 경로 존재)
[x] runtime_data_json boundary 확정
[ ] exact implementation files 확정   ← B1
[x] tests 확정 (설계)

핵심 BLOCKER(B1) 존재 → WP-PERSISTENCE-02 = DESIGN PARTIAL / BLOCKED
```

설계 제출 후 STOP. 운영자 승인 전 구현 금지. repo commit 하지 않음.
