# WP-PERSISTENCE-02A STEP-4A — PRE-FLIGHT

- 작성일: 2026-08-25
- 모드: READ-ONLY SQL PREPARATION. INSERT/UPDATE/DELETE/DDL = 0.
- docs SoT: taieng@`221eb4f4`
- 목적: GENERAL v1 materialization 전 production DB SELECT-only 확인(§10) + UP/VERIFY/DOWN 문안 근거 확정.
- SQL artifact: tai-api@`9c027595` (docs/sql/20260825_WP_PERSISTENCE_02A_STEP4A_*.sql)

---

## 0. 결론

```
PREEXISTING GENERAL rows = 0  (master 0 / candidate 0 / runtime 0)
DB CONSTRAINT DRIFT      = 0  (모든 CHECK = STEP-3 SEALED 와 일치)
ATOMICITY                = CONFIRMED (DO 블록 지원)
STOP 조건(§29)           = 해당 없음
→ STEP-4A = READY
```

---

## 1. §10(A)(B)(C) — 기존 존재 여부 (반드시 0)

실측 결과:
```
document_form_master     form_code=GEN-INSPECT-RESULT-001   = 0
document_schema_candidate form_code=GEN-INSPECT-RESULT-001  = 0
runtime_form_schema      source_trace.form_code 동일        = 0
runtime_form_schema      form_name="점검 결과 기록서 (범용)" = 0
```
→ 전부 0. DUPLICATE STOP(§11) 해당 없음. PREEXISTING_GENERAL_SCHEMA_FOUND 아님.

---

## 2. §10(D) — CHECK / nullable / default drift (STEP-3 SEALED 대조)

```
document_schema_candidate.source_table CHECK
  = {document_forms, document_form_master}                    <- SEALED 와 일치
document_schema_candidate.status CHECK
  = {CANDIDATE, NEEDS_HUMAN_REVIEW, AMBIGUOUS, UNRESOLVED}    <- 신규 관측(runtime status 와 다름)
    우리가 쓸 값 'CANDIDATE' 허용됨
runtime_form_schema.form_type CHECK
  = {OFFICIAL, CUSTOM, INTERNAL}                              <- SEALED 와 일치
runtime_form_schema.status CHECK
  = {CANDIDATE, NEEDS_HUMAN_REVIEW, APPROVED_BY_HUMAN,
     APPROVED_FOR_RUNTIME_USE, REJECTED_BY_HUMAN, ARCHIVED}   <- SEALED 와 일치
runtime_field.input_type CHECK
  = {..., signature, measurement, table, multi_row}           <- SEALED 와 일치 (multi_row 존재)
runtime_field.required_status CHECK
  = {CANDIDATE_ONLY, NEEDS_HUMAN_REVIEW, REQUIRED_BY_HUMAN, NOT_REQUIRED} <- SEALED 일치
runtime_field.status CHECK
  = {CANDIDATE, NEEDS_HUMAN_REVIEW, APPROVED_BY_HUMAN, REJECTED_BY_HUMAN} <- SEALED 일치
runtime_field.field_candidate_id                              = nullable (field_candidate INSERT 불필요)
document_form_master.sector default                           = 'BUILDING' (§4 sector=NULL 명시 필수 확인)
```
→ DB CONSTRAINT DRIFT = 0.

---

## 3. 컬럼 계약 (INSERT 문안 근거, NOT NULL / default 실측)

**document_form_master** (NOT NULL: form_code, form_name, form_type[default STANDARD])
```
form_code     NOT NULL         -> 'GEN-INSPECT-RESULT-001'
form_name     NOT NULL         -> '점검 결과 기록서 (범용)'
form_type     NOT NULL default 'STANDARD'  -> 'STANDARD' 명시
form_category nullable         -> 'DOCUMENT'
sector        nullable default 'BUILDING'  -> NULL 명시(★§4)
required_fields jsonb nullable  -> 5필드 라벨 배열(§13 convention)
template_fields jsonb nullable  -> NULL
law_name/law_article/legal_basis nullable -> 전부 미기입(§13, GENERAL 법령 미종속)
is_active     default true / sort_order default 0
```

**document_schema_candidate** (NOT NULL: source_table, source_id, status[default CANDIDATE])
```
source_table NOT NULL  -> 'document_form_master' (CHECK 허용값)
source_id    NOT NULL  -> 신규 master.id
doc_id nullable -> NULL / doc_name -> '점검 결과 기록서 (범용)'
form_code -> 'GEN-INSPECT-RESULT-001' / form_type -> 'STANDARD' / category -> 'DOCUMENT'
sector nullable -> NULL 명시(★§4)
field_count 5 / checklist_count 0 / evidence_count 0
status NOT NULL default 'CANDIDATE' -> 'CANDIDATE'
```

**runtime_form_schema** (NOT NULL: schema_candidate_id, document_family, form_type, status, version)
```
schema_candidate_id NOT NULL -> 신규 candidate.id
document_family NOT NULL -> 'DOCUMENT' (기존 값 재사용)
form_type NOT NULL -> 'CUSTOM' / form_name nullable -> '점검 결과 기록서 (범용)'
field_count 5 / checklist_count 0 / evidence_count 0
source_trace jsonb default '{}' -> {doc_id:null, form_code, source_id, source_table}
status NOT NULL default 'CANDIDATE' -> 'CANDIDATE' / version NOT NULL default 1 -> 1
```

**runtime_field** (NOT NULL: form_schema_id, field_label, input_type, required_status, status)
```
form_schema_id NOT NULL -> 신규 schema.id
field_candidate_id nullable -> NULL (§8, field_candidate INSERT 0)
field_label NOT NULL -> STEP-3 SEALED 라벨 / field_key nullable -> STEP-3 SEALED key
input_type NOT NULL default 'text' -> STEP-3 SEALED input_type
field_order default 0 -> 1..5
required_status NOT NULL default 'CANDIDATE_ONLY' -> §5 (B 확정: CANDIDATE_ONLY)
status NOT NULL default 'CANDIDATE' -> 'CANDIDATE'
```

---

## 4. §13 — required_fields convention 직독 (기존 STANDARD/DOCUMENT)

기존 대표 3건:
```
STD-ACC-001  required_fields = ["재해 발생 일시 및 장소","재해자 인적사항", ...]  (한글 라벨 문자열 배열)
STD-COST-001 required_fields = ["사용 항목","사용 금액", ...]
STD-EDU-001  required_fields = ["교육 실시일시","교육 내용", ...]
template_fields = 전건 null
```
→ convention = **JSON 문자열 배열(한글 필드 라벨)**. GENERAL 도 동일 형태로:
```
required_fields = ["점검 대상","점검 일시","점검 세트/제목","점검자(표시)","점검 항목별 결과"]
template_fields = NULL
```
새 JSON shape 발명 안 함(§13 준수).

---

## 5. §16 — required_status 정책 (B 확정)

STEP-3 SEALED 는 required_status 를 subject/inspected_at/results=REQUIRED_BY_HUMAN,
title/inspector_display=NOT_REQUIRED 로 지정했다.

**긴장점**: 실측상 기존 runtime_field 1303건 전건이 `required_status='CANDIDATE_ONLY'`
이고, §15 는 INSERT 시 field.status=CANDIDATE(승인 전)를 요구한다. REQUIRED_BY_HUMAN 은
"사람이 필수로 결정함"을 뜻하므로, 아직 사람 승인(4D) 전인 CANDIDATE 단계에 넣으면
상태 불일치가 생긴다.

**확정 = 해석 B**: INSERT 시 전건 `CANDIDATE_ONLY`. 근거 (1) 기존 DB 관례 전건
CANDIDATE_ONLY 와 일치, (2) §15 "INSERT 직후는 승인 상태 아님"과 정합, (3) 필수성 확정을
STEP-4D 사람 승인으로 미뤄 승인 게이트의 의미 보존.

STEP-3 SEALED(REQUIRED_BY_HUMAN/NOT_REQUIRED)는 **4D 사람 승인 후 UPDATE target**으로
해석 → SEALED 계약 보존. UP.sql 은 B로 고정, VERIFY.sql 에 required_status=CANDIDATE_ONLY
5/5 검증 포함. field.status = CANDIDATE (§15).

---

## 6. §20 atomicity 확인

```
DO $$ ... $$ (PL/pgSQL 익명 블록) 지원 = CONFIRMED (READ-ONLY 테스트 통과)
```
- DO 블록은 단일 statement 로 실행되어 내부 예외 시 블록 전체 자동 롤백.
- master->candidate->schema->field ×5 를 DECLARE 변수로 id 를 넘기며 한 블록에서 원자적
  materialize 가능. 블록말 assertion(개수/불변식) 실패 시 RAISE EXCEPTION → 전체 롤백.
- → ATOMIC MATERIALIZATION 가능. 순차 분할 INSERT 불필요(§20 원칙 충족).

---

## 7. STOP 조건(§29) 대조

```
[ ] GEN-INSPECT-RESULT-001 기존 존재      -> 아님 (0/0/0)
[ ] DB constraint drift                   -> 아님 (drift 0)
[ ] 필수 컬럼 미확정                        -> 아님 (전 컬럼 실측)
[ ] required_fields convention 불명        -> 아님 (직독 확인)
[ ] required_status 정책 불명              -> 아님 (B 확정: CANDIDATE_ONLY, §5)
[ ] atomic transaction 불가               -> 아님 (DO 블록 지원)
[ ] source provenance chain 불가          -> 아님 (master->candidate->runtime 성립)
[ ] sector=NULL 저장 불가                  -> 아님 (nullable, 명시 INSERT 가능)
[ ] 5 runtime_field CHECK 위반            -> 아님 (input_type multi_row 등 전부 허용)
[ ] rollback guard 작성 불가              -> 아님 (UUID chain 기반 DOWN 작성 가능)
→ STOP 조건 해당 없음. STEP-4A READY.
```
