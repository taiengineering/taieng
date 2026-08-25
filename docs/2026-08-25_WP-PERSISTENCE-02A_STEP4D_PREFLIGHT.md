# WP-PERSISTENCE-02A STEP-4D-PREP — PRE-FLIGHT

- 작성일: 2026-08-25
- 모드: READ-ONLY APPROVAL PREPARATION. UPDATE/INSERT/DELETE/DDL/BRIDGE = 0.
- docs SoT: taieng@`d90b462b` / SQL SoT: tai-api@`2c143311`
- GENERAL schema UUID: `dc79ac3c-388c-42dc-b029-3dd9bda54a47`

---

## 0. 결론

```
PRECONDITION            = PASS (schema/field 전건 CANDIDATE, exact contract 5/5)
BRIDGE/DOCUMENT REF      = 0 / 0
APPROVAL WRITER          = 정식 status-승격 writer 미확인 (§5)
                           → 직접 UPDATE = 현행 유효 경로. audit = A-2 확정.
G1~G10                   = 10/10 PASS (실측 근거 확보)
CANDIDATE 비승격          = 확정 (candidate.status enum 에 승격값 없음)
중간 상태 APPROVED_BY_HUMAN = 사용 (생략 안 함)
→ STEP-4D-PREP = READY. 결정 A-2 / B-1 확정.
```

---

## 1. §2 PRE-CONDITION 재확인 (실측)

```
schema_id             = dc79ac3c-388c-42dc-b029-3dd9bda54a47
runtime_form_schema.status = CANDIDATE
runtime_field ×5 status    = CANDIDATE (5/5)
runtime_field ×5 required_status = CANDIDATE_ONLY (5/5)
exact contract (key/type/order) = 5/5
  inspection_subject / text / 1
  inspected_at / datetime / 2
  inspection_title / text / 3
  inspector_display / text / 4
  inspection_results / multi_row / 5
runtime_evidence_field = 0
runtime_inspection_bridge ref = 0
runtime_document_data ref = 0
```
→ PROMOTION_PRECONDITION_MISMATCH 아님. 전 항목 일치.

---

## 2. §3 candidate 비승격 확정 (실측)

```
document_schema_candidate.status CHECK
  = {CANDIDATE, NEEDS_HUMAN_REVIEW, AMBIGUOUS, UNRESOLVED}
  → APPROVED_BY_HUMAN / APPROVED_FOR_RUNTIME_USE 값 없음.
```
→ candidate.status = CANDIDATE 유지. **candidate UPDATE = 0.** (runtime approval 상태가
아니라 source-derived candidate 계보 상태로 본다.)

---

## 3. ★ §5 승인 관례 직독 — 핵심 질문 답

**질문: GENERAL schema 승인이 단순 UPDATE인가, 기존 approval writer를 거쳐야 하는가?**

**(A) 기존 APPROVED 전례 = 0건**
```
runtime_form_schema: 전건 CANDIDATE (324건, 우리 것 포함)
runtime_field:       전건 CANDIDATE / CANDIDATE_ONLY (1308건 = 기존 1303 + 우리 5)
```
→ APPROVED_BY_HUMAN / APPROVED_FOR_RUNTIME_USE 로 승격된 row 가 시스템 전체에 **0건**.
GEN-INSPECT-RESULT-001 이 승격되면 **시스템 최초의 APPROVED runtime schema** 가 된다.

**(C) 승인 metadata 컬럼 = 없음**
```
runtime_form_schema / runtime_field 에 approved_by/reviewed_by/approved_at 등 없음.
status 컬럼만 승격.
```

**(D) 별도 approval writer 확인**
```
runtime_form_audit_log (0건) — source_table/source_id/action/before_state/after_state/
  reviewer_id/review_comment/rollback_snapshot/rollback_available.
  → runtime_form_schema 승격을 기록하도록 설계된 audit writer. 그러나 0건(미사용).
runtime_review_decision (5101건) — review_domain 전건 INSPECTION. schema 승격 도메인 아님.
runtime_review_authority (6건) — WORK_ORDER/INSPECTION/EVIDENCE/DOCUMENT/SCHEDULE/OBLIGATION.
  SCHEMA/FORM_SCHEMA 승인 도메인 없음.
document_schema_audit (0) / human_review_decisions (0) — 미사용.
```

**판정**:
- schema status 를 CANDIDATE→APPROVED 로 바꾸는 **정식 서비스/writer 미확인**.
- 따라서 **직접 SQL UPDATE = 현행 유효한 승급 경로**. §5 STOP 조건 미해당
  (그 writer 가 schema 승격을 다룬 전례 0, status 승격 서비스 미확인).
- **단** runtime_form_audit_log 는 runtime_form_schema 승격 감사용으로 설계된 테이블.
  승격 시 audit row 를 함께 남기는 것이 설계 의도에 부합 → A-2 확정.

---

## 4. 결정 (확정)

**결정 A = A-2 확정**: status 승격 + runtime_form_audit_log audit row 1건.
action='PROMOTE_TO_RUNTIME_USE', before/after_state, rollback_snapshot 포함.

**결정 B = B-1 확정**: reviewer_id=NULL (nullable 확인, action CHECK 없음).
review_comment 에 "no canonical schema-governance reviewer identity contract currently
exists" 명시(승인자 부재가 아니라 canonical identity 계약 부재 의미).

**결정 C = STEP-4D 실행 승인 (대기)**: SQL commit → 독립 검증 → "STEP-4D APPROVED" → 실행.

---

## 5. §6 중간 상태 정책

- 승격 전례 0 → 참고할 기존 흐름 없음. 설계 원칙대로 **APPROVED_BY_HUMAN 중간 상태 생략 안 함**:
  ```
  1. runtime_field ×5: CANDIDATE→APPROVED_BY_HUMAN + required_status→target
  2. runtime_form_schema: CANDIDATE→APPROVED_BY_HUMAN
  3. G1~G10 / exact assertion
  4. runtime_form_schema: APPROVED_BY_HUMAN→APPROVED_FOR_RUNTIME_USE
  ```
- CANDIDATE→APPROVED_FOR_RUNTIME_USE 직접 승격 금지(§10). 단일 DO 블록 원자 실행.

---

## 6. §8 G1~G10 재점검 (실측 근거)

```
G1 공식서식 오인 방지: form_type=CUSTOM, sector=NULL, law_name/article/basis=NULL → PASS
G2 anchor 충돌 없음: source_inspection_id 필드 부재(0), anchor=runtime_document_data → PASS
G3 metadata 표현: subject/inspected_at/title/inspector_display 4필드 → PASS
G4 result N→N 보존: inspection_results multi_row 1개 → PASS
G5 raw code 보존: raw_code=result_code (STEP-3 SEALED payload) → PASS
G6 value/note 손실 없음: value_text/value_number/note/checked_at (payload) → PASS
G7 photo 보존: photo_url/photo_urls (payload) → PASS
G8 tenant boundary: schema 가 tenant truth 신규 생성 안 함 → PASS
G9 actor/inspector boundary: inspector_display ≠ authenticated actor → PASS
G10 silent-drop 없음: 금지필드 부재(0) + counts 5/0/0 + payload lossless → PASS
→ G1~G10 = 10/10 PASS (= DB structural gate + STEP-3 sealed payload contract)
  DB structural 입증: G1/G2/G3/G4/G8/G9/G10
  STEP-3 SEALED payload 의존: G5/G6/G7 (DB 재입증 아님)
  → VERIFY SQL gate 이름 = promotion_state_gate_status (DB 상태+승격 검증).
```

---

## 7. §20 STOP 조건 대조

```
[ ] GENERAL 상태가 CANDIDATE 아님        → 아님 (전건 CANDIDATE)
[ ] 5 field drift                     → 아님 (exact 5/5)
[ ] bridge reference 이미 생김            → 아님 (0)
[ ] runtime_document_data 이미 생김       → 아님 (0)
[ ] 기존 공식 approval writer 우회        → 아님 (schema 승격 writer/도메인 미확인)
[ ] approval actor mandatory 인데 미확정   → 아님 (reviewer_id nullable, B-1 확정)
[ ] APPROVED_BY_HUMAN 중간 상태 충돌      → 아님 (enum 존재, 전례 0)
[ ] G1~G10 하나라도 FAIL                  → 아님 (10/10)
[ ] atomic promotion 불가                → 아님 (DO 블록, STEP-4B 실증)
[ ] DOWN 안전성 확보 불가                 → 아님 (promotion-only rollback + audit 보존)
→ STOP 조건 해당 없음.
```
