# WP-PERSISTENCE-02A STEP-4A — EXECUTION GATE

- 작성일: 2026-08-25
- 모드: READ-ONLY SQL PREPARATION. DB MUTATION = 0 / REPO MUTATION = 0 (이 문서 작성 시점).
- docs SoT: taieng@`221eb4f4`
- SQL artifact: tai-api@`9c027595` (docs/sql/20260825_WP_PERSISTENCE_02A_STEP4A_*.sql)

---

## 1. §30 최종 보고

```
WP-PERSISTENCE-02A STEP-4A

MODE
= READ-ONLY SQL PREPARATION

PREEXISTING GENERAL
MASTER    = 0
CANDIDATE = 0
RUNTIME   = 0

DB CONSTRAINT DRIFT
= 0

TARGET MATERIALIZATION
MASTER         = 1
CANDIDATE      = 1
RUNTIME_SCHEMA = 1
RUNTIME_FIELD  = 5
TOTAL          = 8

FORM_CODE
= GEN-INSPECT-RESULT-001

MASTER SECTOR    = NULL EXPLICIT
CANDIDATE SECTOR = NULL EXPLICIT

PROVENANCE
= document_form_master -> candidate -> runtime  (continuous)

FIELDS
inspection_subject   (text,      order 1)
inspected_at         (datetime,  order 2)
inspection_title     (text,      order 3)
inspector_display    (text,      order 4)
inspection_results   (multi_row, order 5)

UP SQL     = READY / NOT EXECUTED
VERIFY SQL = READY / NOT EXECUTED
DOWN SQL   = READY / NOT EXECUTED

ATOMICITY = CONFIRMED  (DO 블록 지원, 단일 statement 원자 실행)

DB MUTATION   = 0
REPO MUTATION = 0 (산출 시점; 이후 SQL/governance commit 은 승인된 별도 행위)

NEXT = WAIT FOR STEP-4B EXPLICIT APPROVAL
```

---

## 2. §16 field required_status/status 표 (5건) — B 확정

| # | field_key | input_type | order | required_status (4B initial) | 4D target | initial status |
|---|---|---|---|---|---|---|
| 1 | inspection_subject | text | 1 | CANDIDATE_ONLY | REQUIRED_BY_HUMAN | CANDIDATE |
| 2 | inspected_at | datetime | 2 | CANDIDATE_ONLY | REQUIRED_BY_HUMAN | CANDIDATE |
| 3 | inspection_title | text | 3 | CANDIDATE_ONLY | NOT_REQUIRED | CANDIDATE |
| 4 | inspector_display | text | 4 | CANDIDATE_ONLY | NOT_REQUIRED | CANDIDATE |
| 5 | inspection_results | multi_row | 5 | CANDIDATE_ONLY | REQUIRED_BY_HUMAN | CANDIDATE |

- **required_status = B 확정**: 4B INSERT 시 전건 CANDIDATE_ONLY (기존 1303건 관례와 일치).
- 4D target(사람 승인 후 UPDATE) = STEP-3 SEALED 값. SEALED 계약은 최종 target 으로 보존.
- initial status(승인 워크플로우) = 전건 CANDIDATE (§15).

---

## 3. 확정된 결정

**결정 1 — required_status = B 확정**
- 4B INSERT 시 전건 `CANDIDATE_ONLY`. UP.sql B로 고정.
- STEP-3 SEALED(REQUIRED_BY_HUMAN/NOT_REQUIRED)는 4D 사람 승인 후 UPDATE target 으로 보존.

**결정 2 — SQL artifact commit 후 실행**
- 검토한 SQL = 실제 실행 SQL 동일 고정. 커밋 후, 커밋된 UP.sql 과 동일 내용만 4B 실행.
- 실행 직전 파일 내용 drift 있으면 STOP.
- commit 위치:
  - SQL 3종 -> `tai-api/docs/sql/` (SQL-artifact-only, tai-api@`9c027595`)
  - governance 2종 -> `taieng/docs/` (docs-only, 이 커밋)

**결정 3 — STEP-4B 실행 승인 (대기)**
- 순서: SQL commit -> commit 검증 -> STEP-4B DB APPLY 승인.
- 승인 전까지 INSERT 0 유지. "STEP-4B APPROVED" 명시 필요.

---

## 4. 실행 게이트 상태

```
STEP-4A = SQL ARTIFACT COMMITTED (tai-api@9c027595) + governance docs commit
STEP-4B = DB APPLY         = NOT APPROVED (대기)
STEP-4C = POST VERIFY      = 4B 성공 후
STEP-4D = HUMAN PROMOTION  = NOT APPROVED (대기)

SQL DRAFT READY ≠ DB APPLY APPROVED
```

- UP/VERIFY/DOWN 전부 NOT EXECUTED.
- 실행 방식: 단일 DO 블록(원자적). 순차 분할 INSERT 로 대체하지 않음(§20).
- 실패 시 DO 블록 내부 RAISE EXCEPTION → 전체 자동 롤백(부분 materialization 0).

---

## 5. STEP-4B 예정 실행 절차 (승인 후)

```
1. required_status = B 확정 (4B initial = CANDIDATE_ONLY ×5). 커밋된 UP.sql 고정됨.
2. 커밋된 UP.sql 과 동일 내용을 단일 execute_sql 호출로 실행 (drift 있으면 STOP)
3. 즉시 VERIFY.sql SELECT 실행 -> 8-row invariant 전 항목 PASS 확인 (STEP-4C)
4. PASS 시에만 STEP-4D 사람 승인 절차로 진행
   (runtime_field ×5 -> APPROVED_BY_HUMAN, schema -> APPROVED_BY_HUMAN
    -> 최종 schema -> APPROVED_FOR_RUNTIME_USE
    + required_status 4D target 승격: subject/inspected_at/results=REQUIRED_BY_HUMAN,
      title/inspector_display=NOT_REQUIRED)
5. 실패/불일치 시 DOWN.sql 로 정확한 UUID chain 롤백(별도 승인)
```

STEP-4B/4C/4D 는 각각 별도 승인 게이트.

---

## 6. 절대 범위 밖 재확인 (§25)

이번 STEP-4 전체에서 하지 않음:
```
runtime_inspection_bridge UPDATE / false MAPPED 323 교정 / 324 set mapping /
runtime_document_data 생성 / source_inspection_id writer / inspection 완료 hook /
renderer enhancement / PDF 생성 / Storage object / generated_document 수정 /
submitted_by / B3 / transaction orchestration 구현 /
GENERAL schema 316 set 자동 연결
```
