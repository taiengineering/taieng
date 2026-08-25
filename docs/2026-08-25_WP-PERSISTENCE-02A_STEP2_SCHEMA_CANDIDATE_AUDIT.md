# WP-PERSISTENCE-02A STEP-2 — SCHEMA CANDIDATE AUDIT

- 작성일: 2026-08-25
- 모드: READ-ONLY APPROVAL PREPARATION / EVIDENCE FIRST (DB SELECT only, mutation 0)
- docs SoT: taieng@`909bb825`
- 대상: 점검용 후보 38개(INSPECT 10 / BW 18 / STD 10) 구조검증

---

## 0. 핵심 결론

**38개 후보 중 APPROVE_CANDIDATE = 0.** AS-IS 로 점검 결과를 구조적으로 안전하게
연결할 수 있는 승인된 field contract 를 가진 schema 가 없다.

정정(중요): "checklist_count=0 이면 반복 결과 저장 불가" 또는 "field_count=0 이면
복수 결과 저장 불가"는 **부정확**하다. 현재 문서엔진은 runtime_data_json 에 list/dict
를 허용하고 renderer 가 schema 에 매핑되지 않은 값도 lossless 보존하며,
runtime_field.input_type='multi_row' 도 실재한다(STD-FIRE-001 에 실제 존재). 따라서
저장 무결성 자체는 기존 엔진으로 가능하다.

AS-IS 승인이 0인 진짜 이유는 별개다:
- **INSPECT-* 10 + BW-* 18 = 28개**: runtime schema field/checklist/evidence_count 0,
  원천 required_fields/template_fields NULL = 실제 필드 정의가 아직 없는 빈 스텁.
- **STD-* 10개**: 실제 runtime_field 는 있으나 **field_key 가 전건 NULL**
  (required_status=CANDIDATE_ONLY) → inspection_results 를 구조적으로 매핑할 **승인된
  field contract 가 없다.** 게다가 전건 sector=BUILDING + 특정 법령 종속.

이는 지시서 §20 STOP/BLOCKED("기존 schema 를 억지 사용해야만 mapping 가능 / 점검용
schema 가 실제로 없음")에 해당. 억지 PASS 하지 않는다.

---

## 1. 평가 기준 (지시서 §6)

R1 점검 식별정보 / R2 점검 결과 / R3 항목별 반복 결과 / R4 증거 / R5 domain
specificity / R6 결과문서 여부. 판정은 실제 runtime_field(field_key/input_type)와
원천 required_fields 로 내렸으며 이름/prefix 는 근거로 쓰지 않았다(§4).

주: R3(반복 결과)은 checklist_count>0 을 요구하지 않는다. multi_row 필드 또는
runtime_data_json list/dict 로 표현 가능하다. R3 의 실제 관문은 "그 반복 데이터를
구조적으로 받을 **승인된 field_key contract**가 있는가"이며, 후보 STD 는 field_key 가
전건 NULL 이라 이 contract 가 없다.

---

## 2. INSPECT-* 10개 (전건 빈 스텁)

| form_code | form_name | schema field/checklist/evid | 원천 required_fields | 판정 |
|---|---|---|---|---|
| INSPECT-BLD-001 | 건축물 정기점검 결과서 | 0/0/0 | NULL | NEW_SCHEMA_REQUIRED_SIGNAL |
| INSPECT-BOIL-001 | 압력용기·보일러 검사 성적서 | 0/0/0 | NULL | REJECT_RUNTIME (외부 검사 성적서, R6) |
| INSPECT-ELEC-001 | 전기설비 정기점검 결과서 | 0/0/0 | NULL | NEW_SCHEMA_REQUIRED_SIGNAL |
| INSPECT-ELEV-001 | 승강기 자체점검 기록부 | 0/0/0 | NULL | NEW_SCHEMA_REQUIRED_SIGNAL |
| INSPECT-ELEV-002 | 승강기 정기검사 성적서 | 0/0/0 | NULL | REJECT_RUNTIME (외부 검사 성적서, R6) |
| INSPECT-FIRE-001 | 소방시설 종합점검 결과보고서 | 0/0/0 | NULL | NEW_SCHEMA_REQUIRED_SIGNAL |
| INSPECT-FIRE-002 | 소방시설 작동기능점검 결과서 | 0/0/0 | NULL | NEW_SCHEMA_REQUIRED_SIGNAL |
| INSPECT-GAS-001 | 가스사용시설 정기점검 기록서 | 0/0/0 | NULL | NEW_SCHEMA_REQUIRED_SIGNAL |
| INSPECT-HAZ-001 | 위험물시설 정기점검 기록부 | 0/0/0 | NULL | NEW_SCHEMA_REQUIRED_SIGNAL |
| INSPECT-WORKEN-001 | 작업환경측정 결과보고서 | 0/0/0 | NULL | REJECT_RUNTIME (외부 측정기관 결과, R6) |

- 공통: runtime schema field_count=0, 원천 required_fields=NULL → 구조 자체 부재.
- "검사 성적서 / 측정 결과보고서"(BOIL/ELEV-002/WORKEN)는 외부 기관 발급 문서 →
  자체점검 결과 자동생성 용도로 사용 금지(§6 R6, §9).

## 3. BW-* 18개 (전건 빈 스텁, BEFORE_WORK 계열)

전건 동일: schema field/checklist/evid = 0/0/0, 원천 required_fields=NULL,
form_type=STANDARD, sector=CONSTRUCTION, document_family=UNRESOLVED.

form_code 목록: BW-BLAST/CCP/CONF/CRANE/EXC/FORM/GDL/HIGH/HST/LFT/MCR/REINF/
SCF/STEEL/TCR/TELEC/TUN/WELD-001 (총 18).

- 판정: 전건 **NEW_SCHEMA_REQUIRED_SIGNAL.**
- 작업 종류별 "작업 전 점검표" 이름은 명확하나 실제 필드/체크리스트 구조가 0.
  BEFORE_WORK 점검에 쓰려면 각 작업 종류별 체크항목 구조를 먼저 정의해야 함.
- 지시서 §10 대로 "작업 종류별 승인 후보표"까지만: 현재는 승인 가능한 구조가 없어
  전건 구조 신설 필요 신호로 기록.

## 4. STD-* 10개 (평면 6필드, field_key 전건 NULL, BUILDING 전용)

| form_code | form_name | field | law_name | sector | 판정 |
|---|---|---|---|---|---|
| STD-ACC-001 | 산업재해 발생 원인 기록서 | 6 | 산업안전보건법 | BUILDING | REJECT_RUNTIME (재해기록, 점검결과 아님) |
| STD-COST-001 | 안전관리비 사용명세서 | 6 | 산업안전보건법 | BUILDING | REJECT_RUNTIME (비용명세, R6) |
| STD-EDU-001 | 안전보건교육 실시기록부 | 5 | 산안법 시행규칙 | BUILDING | REJECT_RUNTIME (교육기록, R6) |
| STD-ELEC-001 | 전기설비 점검일지 | 6 | 전기안전관리법 시행규칙 | BUILDING | NEEDS_HUMAN_REVIEW (점검일지형, 단 field_key NULL·BUILDING 전용) |
| STD-ENV-001 | 작업환경측정 결과 보관대장 | 6 | 작업환경측정 고시 | BUILDING | REJECT_RUNTIME (외부측정 보관대장, R6) |
| STD-FIRE-001 | 소방시설 자체점검 결과서 | 6 | 화재예방법 | BUILDING | NEEDS_HUMAN_REVIEW (multi_row 실재하나 field_key NULL·BUILDING 전용) |
| STD-HEALTH-001 | 건강진단 결과 보관대장 | 6 | 산안법 시행규칙 | BUILDING | REJECT_RUNTIME (건강진단 대장, R6) |
| STD-INSPECT-001 | 안전점검 결과서 | 6 | 다중이용업소 특별법 | BUILDING | INSUFFICIENT (STD_INSPECT_DECISION 참조) |
| STD-MTG-001 | 안전보건위원회 회의록 | 5 | 산업안전보건법 | BUILDING | REJECT_RUNTIME (회의록, R6) |
| STD-RISK-001 | 위험성평가 결과서 | 5 | 산안법 시행규칙 | BUILDING | REJECT_RUNTIME (위험성평가, 별도 도메인) |

- STD 계열 공통 한계:
  - **field_key 전건 NULL** (required_status=CANDIDATE_ONLY) → inspection_results 를
    구조적으로 매핑해 받을 승인된 field contract 가 없음(R3 의 실제 관문 실패).
  - **전건 sector=BUILDING** → INDUSTRIAL/CONSTRUCTION 범용 사용 불가(R5 실패).
  - 전건 특정 법령 종속 → 범용 대체 금지.
- **STD-FIRE-001 실측(참고 원형)**: field_order=3 "점검 대상 소방시설 목록"이 실제
  `input_type='multi_row'` 로 정의되어 있음 → 반복 항목을 구조적으로 표현할 **패턴은
  이미 존재**한다. 다만 field_key=NULL 이라 현재 runtime 데이터와 정상 구조 매핑 불가.
  이 multi_row 패턴은 STEP-3 GENERAL schema 설계의 참고 원형으로 유효(FINAL_DECISION §6).
- STD-ELEC-001 / STD-FIRE-001 만 "점검일지/자체점검 결과" 성격이라 NEEDS_HUMAN_REVIEW
  로 남기되, field_key 부재·BUILDING 종속 때문에 그대로는 범용 승인 불가.

---

## 5. 집계 (개별 판정 합산, 합계 검증)

```
CANDIDATE POOL = 38  (INSPECT 10 / BW 18 / STD 10)

APPROVE_CANDIDATE      = 0
NEEDS_HUMAN_REVIEW     = 2    (STD-ELEC-001, STD-FIRE-001)
REJECT_RUNTIME         = 11   (INSPECT 외부성적서 3: BOIL/ELEV-002/WORKEN
                               + STD 8: ACC/COST/EDU/ENV/HEALTH/INSPECT-001/MTG/RISK)
NEW_SCHEMA_SIGNAL      = 25   (INSPECT 빈스텁 7 + BW 빈스텁 18)

합계 검증: 0 + 2 + 11 + 25 = 38  ✓
```

내역:
- INSPECT 10 = REJECT 3(BOIL/ELEV-002/WORKEN) + NEW_SCHEMA 7
- BW 18 = NEW_SCHEMA 18
- STD 10 = NEEDS_REVIEW 2(ELEC/FIRE) + REJECT 8(ACC/COST/EDU/ENV/HEALTH/INSPECT-001/MTG/RISK)

---

## 6. 왜 이런 결과인가 (구조적 원인)

- runtime_form_schema 는 원래 document_forms/document_form_master 의 **서식 메타를
  후보로 끌어온 것**이지, 점검 결과 입력용으로 승인된 field contract 가 아니다.
- 저장 무결성 자체(복수 항목을 list/dict/multi_row 로 보존)는 기존 엔진으로 가능하다.
  실제로 STD-FIRE-001 에는 multi_row 필드가 이미 있다.
- 그러나 후보 schema 는 (a) 빈 스텁(INSPECT/BW)이거나 (b) field_key 전건 NULL 이라
  inspection_results 를 **구조적으로 받을 승인된 field_key contract 가 없다.** 또한
  STD 는 전건 BUILDING·특정 법령 종속이라 범용 결과 보존용으로 부적합.
- 따라서 "기존 schema 를 골라 붙이는" AS-IS 접근으로는 점검→문서 연결을 안전하게
  완성할 수 없다. → 점검 결과용 **GENERAL schema(field contract 포함)를 설계**하는
  방향이 선행되어야 한다(FINAL_DECISION 참조).
