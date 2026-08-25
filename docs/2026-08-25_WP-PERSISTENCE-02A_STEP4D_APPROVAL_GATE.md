# WP-PERSISTENCE-02A STEP-4D-PREP — APPROVAL GATE

- 작성일: 2026-08-25
- 모드: READ-ONLY APPROVAL PREPARATION. DB MUTATION = 0.
- docs SoT: taieng@`d90b462b` / SQL SoT: tai-api@`35960ecf` (UP/VERIFY 방어 보강 2차)
- 대상 schema UUID: `dc79ac3c-388c-42dc-b029-3dd9bda54a47`

---

## 1. §21 최종 보고

```
WP-PERSISTENCE-02A STEP-4D-PREP

MODE = READ-ONLY APPROVAL PREPARATION

CURRENT SCHEMA STATUS   = CANDIDATE
CURRENT FIELD STATUS    = CANDIDATE ×5
CURRENT REQUIRED_STATUS = CANDIDATE_ONLY ×5
BRIDGE REF / RUNTIME DOCUMENT REF = 0 / 0

APPROVAL CONVENTION
= 정식 status-승격 writer 미확인 (직접 UPDATE = 현행 유효 경로) + runtime_form_audit_log audit(A-2)

INTERMEDIATE STATE = APPROVED_BY_HUMAN REQUIRED (생략 안 함)
CANDIDATE STATUS   = CANDIDATE UNCHANGED (§3)
G1-G10             = 10/10 PASS

TARGET FIELD STATUS    = APPROVED_BY_HUMAN ×5
TARGET REQUIRED_STATUS = REQUIRED_BY_HUMAN 3 (subject/inspected_at/results)
                         / NOT_REQUIRED 2 (title/inspector_display)
TARGET SCHEMA STATUS   = APPROVED_FOR_RUNTIME_USE

UP/VERIFY/DOWN SQL = READY / NOT EXECUTED
DB MUTATION = 0
NEXT = WAIT FOR STEP-4D EXPLICIT EXECUTION APPROVAL
```

---

## 2. §8 G1~G10 재검증 (실측 근거)

| Gate | 기준 | 실측 근거 | 판정 |
|---|---|---|---|
| G1 | 공식 법정서식 오인 방지 | form_type=CUSTOM / master.sector=NULL / law_name·article·basis=NULL | PASS |
| G2 | source anchor 충돌 없음 | source_inspection_id 필드 부재(0), anchor=runtime_document_data | PASS |
| G3 | inspection metadata 표현 | subject/inspected_at/title/inspector_display 4필드 | PASS |
| G4 | result N→N 보존 | inspection_results multi_row 1개 | PASS |
| G5 | raw result code 보존 | raw_code=result_code (payload 계약, STEP-3 SEALED) | PASS |
| G6 | value/note 손실 없음 | value_text/value_number/note/checked_at (payload) | PASS |
| G7 | photo evidence 보존 | photo_url/photo_urls (payload) | PASS |
| G8 | tenant boundary | schema 가 tenant truth 신규 생성 안 함 | PASS |
| G9 | actor/inspector boundary | inspector_display ≠ authenticated actor | PASS |
| G10 | silent-drop 없음 | 금지필드 부재(0) + counts 5/0/0 + payload lossless | PASS |

→ **G1~G10 = 10/10 PASS** (= DB structural gate + STEP-3 sealed payload contract).
- DB structural 입증: G1/G2/G3/G4/G8/G9/G10.
- STEP-3 SEALED payload 의존(DB 재입증 아님): G5/G6/G7.
- VERIFY SQL gate 이름 = `promotion_state_gate_status` (DB 상태+승격 검증), G1~G10 전체와 구분.
- UP.sql GATE ASSERT 로 in-transaction 재검증(G1 은 law_article 포함). FAIL 시 전체 롤백.

---

## 3. 결정 (확정)

**핵심 질문 답 (§5)**: schema status 승격 정식 writer 미확인. 범용 review 프레임워크
(runtime_review_decision 5101 / authority 6)는 SCHEMA 승격 도메인이 없다. → 직접 SQL
UPDATE = 현행 유효 승급 경로. (§5 STOP 미해당.)

**결정 A = A-2 확정**: status 승격 + runtime_form_audit_log audit row 1건.
**결정 B = B-1 확정**: reviewer_id=NULL. review_comment 에 canonical identity 계약 부재 명시.
**결정 C = STEP-4D 실행 승인 (대기)**: SQL commit → 독립 검증 → "STEP-4D APPROVED" → 실행.

---

## 4. §17 절대 범위 밖 재확인

이번 4D 에서 하지 않음:
```
document_schema_candidate status 변경 / runtime_inspection_bridge UPDATE /
false MAPPED 323 교정 / 316 set mapping / runtime_document_data 생성 /
source anchor writer / inspection completion hook / renderer enhancement /
generated_document / PDF / Storage / B3 / submitted_by / 새 approval table / 새 engine
```
특히: APPROVED_FOR_RUNTIME_USE 가 되어도 **316 inspection_set 자동 연결 금지**(§7).
schema approval ≠ mapping approval.

---

## 5. 실행 게이트 상태

```
STEP-4D-PREP = SQL COMMITTED
  최초:   tai-api@2c143311 (UP/VERIFY/DOWN 3종) + taieng@7b507838 (governance 2종)
  보강2차: tai-api@35960ecf (UP/VERIFY 방어 보강, DOWN 불변)
          + taieng governance 2종 SQL SoT SHA 갱신 (본 commit)
STEP-4D 실행  = NOT APPROVED (대기)

SQL DRAFT READY ≠ UPDATE APPROVED
```

- UP/VERIFY/DOWN 전부 NOT EXECUTED.
- 실행 방식: 단일 DO 블록(원자적). precondition→field 승격→schema APPROVED_BY_HUMAN
  →GATE→schema APPROVED_FOR_RUNTIME_USE→final assert→audit. 실패 시 전체 롤백.
- 승격 완료 시 GEN-INSPECT-RESULT-001 = 시스템 최초 APPROVED_FOR_RUNTIME_USE runtime schema.

### 5.1 UP/VERIFY 방어 보강 (2차) 요약 — tai-api@`35960ecf`

```
UP:     ① total runtime_field count=5 guard  ② preexisting promotion audit=0 guard
        ③ audit INSERT rowcount=1 assertion   ④ final promotion audit count=1 assertion
VERIFY: ⑤ audit CTE source_table exact         ⑥ gate CASE 에 field_count=5 + schema_header_ok
DOWN:   변경 없음 (promotion-only rollback + audit 보존)
```

---

## 6. STEP-4D 예정 실행 절차 (승인 후)

```
1. tai-api HEAD=35960ecf 확인 + UP.sql drift 없음 확인
2. UP.sql 단일 execute_sql 1회 실행
3. 즉시 VERIFY.sql SELECT → 전 항목 PASS 확인
   (schema=APPROVED_FOR_RUNTIME_USE, schema_header_ok=true, field_count=5,
    field 5 APPROVED_BY_HUMAN, required 3/2/0, exact 5, candidate=CANDIDATE,
    bridge/doc ref 0, audit 1, promotion_state_gate_status=PASS)
4. PASS → STEP-4D = COMPLETE. GENERAL schema runtime 사용 가능.
5. 불일치 → PROMOTION_MISMATCH → 결과 제출 후 STOP → 필요 시 DOWN(별도 승인)
```

제출 후 STOP. UPDATE 실행하지 않는다.
