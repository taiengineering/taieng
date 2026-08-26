# WP-PERSISTENCE-02B B2 STEP-1 REV-2 — PREFLIGHT

- 상태: APPLY PREP FINAL / PENDING GPT VERIFICATION
- 모드: CONCURRENCY HARDENING ONLY. **DB MUTATION = 0, BRIDGE UPDATE = 0, CODE = 0, DEPLOY = 0, REPO COMMIT = 0**
- 소스: production `vwlahtguyggrhvslabax` (SELECT-only), 2026-08-26
- 부모 정본: STEP-0 `01d4519b` / B1 REV-2 (PASS/SEALED)
- REV-2 근거: REV-1 SQL 하드닝 PASS. UNIQUE/FK 부재 DB에서 precondition~COMMIT 구간 concurrent write를 봉쇄하기 위한 잠금 추가. 설계·대상·schema·preflight 재조사 없음.

## 목적 (불변)

B1이 판정한 유일 ELIGIBLE inspection_set(`7fee7518`)의 bridge row에 승인된 GENERAL presentation schema(`dc79ac3c`)를 **explicit binding**. STEP-0 invariant("bridge = presentation schema resolution SoT / APPROVED_FOR_RUNTIME_USE만") 준수. 대상 1행.

## 프리체크 (live 실측, 유효 유지)

| # | 항목 | 결과 | 판정 |
|---|---|---|---|
| P1 | target set `7fee7518` | 소방시설공사업법 점검 / FIRE / INSPECT / is_active=true, 1행 | PASS |
| P2 | target bridge (set=7fee7518) | id `3894ddb5-df96-4dc9-8cf0-940d3300b38a`, 1행, `runtime_form_schema_id IS NULL` | PASS |
| P2b | mapping_status / mapping_detail | `MAPPED` / legacy note(FIRECONST-002) — **변경 대상 아님** | 보존 |
| P3 | GENERAL schema `dc79ac3c` | status=APPROVED_FOR_RUNTIME_USE, field_count=5 | PASS |
| P4 | bridge 제약/트리거 | PK(id) + CHECK(mapping_status) 만. `runtime_form_schema_id` FK 없음 / **UNIQUE 없음** / 트리거 없음 / updated_at 없음 | PASS (동시성 잠금 필요 근거) |
| P5 | baseline 카운트 | bridge_total=324, bridge_with_schema=0, bridge_to_general=0, target_rows=1 | PASS |
| P6 | side-effect baseline | runtime_document_data=1, generated_document=1544 | PASS (VERIFY invariant) |

## REV-2 동시성 하드닝 (신규)

- **runtime_inspection_bridge: `LOCK TABLE ... IN SHARE ROW EXCLUSIVE MODE`** (UP·DOWN 트랜잭션 시작 직후)
  = APPLY 트랜잭션 동안 concurrent bridge **INSERT/UPDATE/DELETE 봉쇄**(SELECT 허용).
  precondition(324/0/0) → UPDATE → postcondition(324/1/1) → COMMIT 구간 전체에서 모집단 drift 금지.
- **runtime_form_schema target row: `SELECT ... WHERE id='dc79ac3c...' FOR SHARE`** 로 정확히 그 행만 잠근 뒤 status/field_count assert (aggregate COUNT + FOR SHARE 조합 미사용)
  = APPLY 트랜잭션 동안 GENERAL schema **approval state(status/field_count) concurrent mutation 봉쇄**.

## REV-1 방어 (전부 유지, 삭제·완화 없음)

UP: target rows=1 · target NULL=1 · baseline 324/0/0 · GENERAL status=APPROVED/field_count=5 · UPDATE 후 `GET DIAGNOSTICS ROW_COUNT` affected=1 · target schema exact=dc79ac3c · mapping_status=MAPPED 불변 · 전역 postcondition 324/1/1.
DOWN: UPDATE 후 affected=1 · target `IS NULL` · 전역 324/0/0.
VERIFY: target_bridge_rows=1 · target_schema_id=dc79ac3c · target_mapping_status=MAPPED · 324/1/1 · side-effect zero(runtime_document_data=1, generated_document=1544). (VERIFY는 read-only, 잠금 불필요 → REV-1 대비 무변경.)

## 변경 명세 (UP, 핵심 흐름)

```
BEGIN;
LOCK TABLE runtime_inspection_bridge IN SHARE ROW EXCLUSIVE MODE;   -- 동시성 봉쇄
DO $$ ...
  SELECT ... FROM runtime_form_schema WHERE id='dc79ac3c...' FOR SHARE;  -- schema row lock + assert
  precondition asserts (target 1/1, 324/0/0)         → RAISE-on-mismatch
  UPDATE ... SET runtime_form_schema_id='dc79ac3c...' WHERE set='7fee7518...' AND runtime_form_schema_id IS NULL;
  GET DIAGNOSTICS affected = ROW_COUNT; IF affected<>1 → RAISE
  target postcondition (schema=dc79ac3c, mapping_status=MAPPED) → RAISE-on-fail
  global postcondition (324/1/1)                     → RAISE-on-fail
$$;
COMMIT;
```
mutation 허용 컬럼 = `runtime_form_schema_id` only. 변경 금지 = mapping_status / mapping_detail / inspection_set_name / runtime_checklist_count / GENERAL schema / runtime_field / runtime_document_data / generated_document.

## VERIFY 기대값 (UP 후, 전부 참)

```
target_bridge_rows          = 1
target_schema_id            = dc79ac3c-388c-42dc-b029-3dd9bda54a47
target_mapping_status       = MAPPED
bridge_total                = 324
bridge_with_schema          = 1
bridge_to_general           = 1
runtime_document_data_total = 1
generated_document_total    = 1544
```

## 산출물 / SHA256 (REV-2)

```
UP.sql       a1ea312ea0d49569b3d304a52cdc45d7cbe727c43851dbc81f211c5e63782a75
VERIFY.sql   ae5885ef7c84cd28b6cf6c825392bb58dae218e87f92a48c2a58b7075e3d9fe0   (REV-1 대비 무변경)
DOWN.sql     eae95038cb36141f454d2b89a9848f46466f04dab82cc3ef7d628eba4463d706
PREFLIGHT.md (본 문서; 자기참조 불가 → 제출 메시지에 별도 명시)
```

## 게이트

```
DB MUTATION   = 0
BRIDGE UPDATE = 0
CODE          = 0
DEPLOY        = 0
REPO COMMIT   = 0
EXECUTION     = STEP-2 (operator 별도 승인 대기) — 실행 금지
```
제출 후 STOP. STEP-2(runtime_form_schema_id UPDATE 실제 실행)는 GPT REV-2 검증 + operator STEP-2 승인 전까지 절대 금지.
