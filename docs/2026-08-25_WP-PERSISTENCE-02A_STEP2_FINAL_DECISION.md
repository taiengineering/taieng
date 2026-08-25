# WP-PERSISTENCE-02A STEP-2 — FINAL DECISION

- 작성일: 2026-08-25
- 모드: READ-ONLY APPROVAL PREPARATION 완료. mutation 0. repo commit 0 (승인 대기).
- docs SoT: taieng@`909bb825`

---

## 1. 한 문장 결론

점검용 후보 38개를 구조검증한 결과 **AS-IS 로 점검 결과를 구조적으로 받을 승인된
field contract 를 가진 runtime schema 가 0개**다(저장 무결성 자체는 기존 엔진으로
가능). 기존 schema 를 골라 붙이는 경로는 성립하지 않으며, 다음 관문은 "매핑"이 아니라
**단일 범용 GENERAL_INSPECTION_RESULT schema 1종의 설계**다.
→ B1 DATA POPULATION = 여전히 BLOCKED (blocker 성격이 구체화됨).

---

## 2. 왜 BLOCKED 인가 (구조 근거)

- **INSPECT-* 10 + BW-* 18 = 28개**: runtime schema field/checklist/evidence_count
  전부 0, 원천 required_fields/template_fields NULL = 실제 필드 정의가 없는 빈 스텁.
- **STD-* 10개**: 실제 runtime_field 는 있으나 **field_key 전건 NULL**
  (required_status=CANDIDATE_ONLY) → inspection_results 를 구조적으로 받을 승인된
  field contract 없음. + 전건 sector=BUILDING·특정 법령 종속.
- **STD-INSPECT-001**(범용 후보 1순위): INSUFFICIENT — 다중이용업소 특별법·BUILDING
  전용 + multi_row/field_key 부재.

정정(중요): 저장 무결성 자체는 기존 엔진으로 가능하다. runtime_data_json 이 list/dict
를 lossless 보존하고, runtime_field.input_type='multi_row' 도 실재한다(STD-FIRE-001).
BLOCKED 인 이유는 "복수 항목을 저장 못 해서"가 아니라, **AS-IS 후보 중 점검 결과를
구조적으로 받을 승인된 field contract 를 가진 schema 가 0개**이기 때문이다. → 억지
PASS 금지(§20).

## 3. 최종 보고 (지시서 §21 형식)

```
WP-PERSISTENCE-02A STEP-2

CANDIDATE POOL
INSPECT = 10
BW      = 18
STD     = 10

STD-INSPECT-001
= INSUFFICIENT_AS_GENERAL_RESULT_FORM
  (다중이용업소 특별법·BUILDING 전용 + multi_row/field_key contract 부재)

INSPECT SCHEMAS
APPROVE_CANDIDATE = 0
NEEDS_REVIEW      = 0
REJECT            = 3   (BOIL/ELEV-002/WORKEN = 외부 성적서·측정결과, R6)
NEW_SCHEMA_SIGNAL = 7   (나머지 INSPECT 빈 스텁)

BW SCHEMAS
APPROVE_CANDIDATE = 0
NEEDS_REVIEW      = 0
REJECT            = 0
NEW_SCHEMA_SIGNAL = 18  (전건 빈 스텁)

STD SCHEMAS
APPROVE_CANDIDATE = 0
NEEDS_REVIEW      = 2   (STD-ELEC-001, STD-FIRE-001; field_key NULL·BUILDING 한계)
REJECT            = 8   (STD-INSPECT-001 INSUFFICIENT 포함, 나머지 대장/기록/재해 등)

TOTAL: APPROVE 0 / NEEDS_REVIEW 2 / REJECT 11 / NEW_SCHEMA_SIGNAL 25  (합계 38 ✓)

FALSE MAPPED ROWS
= 323  (mapping_status='MAPPED' AND runtime_form_schema_id IS NULL; true MAPPED 0)

MAPPING REVIEW UNIT
= legal_rule_id grouped (~151종) / explicit operator approval

B1 DATA POPULATION
= BLOCKED
  (AS-IS 승인 가능한 결과 schema 0 → 채울 값 없음)

NEXT
= NEW FORM DESIGN — 단일 범용 GENERAL_INSPECTION_RESULT schema 1종
  (도메인별 세트 선행 아님. 기존 runtime document engine 재사용, 새 엔진 없음)

CODE MUTATION = 0
DB MUTATION   = 0
API MUTATION  = 0
REPO MUTATION = 0
DEPLOY        = 0
```

## 4. 다음 안전한 순서 (수정된 경로)

STEP-1 예상(기존 schema 승인 → 매핑)과 달리, STEP-2 실측으로 경로가 바뀌었다:

```
(신) STEP-3: GENERAL_INSPECTION_RESULT schema 1종 FINAL DESIGN (READ-ONLY DESIGN)
     - 단일 범용 schema 1종으로 시작 (도메인별 5~20종 선행 아님)
     - form_type = INTERNAL 또는 CUSTOM (OFFICIAL 금지)
     - sector = 범용 / sector-neutral, 특정 법령 서식 아님
     - 목적 = safety_inspection 결과의 canonical evidence document
     - 반복 결과 = 기존 엔진(runtime_form_schema/runtime_field/runtime_data_json) 재사용
       inspection_results = input_type multi_row (STD-FIRE-001 패턴 참고)
       payload item: inspection_set_item_id/item_name/result_code/note/checked_at/photo_urls
     - source_inspection_id = 이미 runtime_document_data FK anchor → payload 에서 identity 재추론 안 함
     - renderer 의 multi_row 표 렌더링 개선 여부는 STEP-3 에서 결정(저장 무결성과 분리)
     → schema 구조 확정 → CANDIDATE → 구조검증 통과분만 APPROVED_FOR_RUNTIME_USE(사람 승인)
     → legal_rule_id 그룹 단위 매핑 승인 (GENERAL 1종을 다수 set 이 명시적 공유 가능)
     → bridge population + false MAPPED 교정 (APPLY WP)
     → source-anchor writer 구현 (WP-PERSISTENCE-02 IMPLEMENTATION)
```

법정 신고서/공식 성적서/기관 제출양식은 GENERAL schema 가 대체하지 않는다.
점검 사실 보존 → GENERAL_INSPECTION_RESULT / 법정 제출 → 기존 별도 document flow 로 분리.

## 5. 경계 재확인 (건드리지 않은 것)

- runtime fallback = 만들지 않음(§14). explicit pre-approved mapping 만 허용.
- schema 승인 ⊥ mapping 승인 분리 유지(§17). 이번 STEP 에서 status UPDATE 0(§7).
- bridge UPDATE 0, 실행 SQL 작성 0(§18).
- B3 / submitted_by(CD5-1) / generated file(WP-03) = 흡수 안 함.
- 새 mapping table 금지(§1 SEALED) — FINAL SoT 는 runtime_inspection_bridge 유지.

## 6. 운영자 결정 (STEP-3 방향 — 이미 확정된 지침 반영)

- STEP-3 = **단일 범용 GENERAL_INSPECTION_RESULT schema 1종** FINAL DESIGN (READ-ONLY).
  도메인별 schema 선행 = NO / 새 엔진 = NO / 기존 runtime document engine 재사용 = YES.
- STD-FIRE-001 의 multi_row 필드를 inspection_results 표현의 **참고 원형**으로 사용.
- false MAPPED 323건 교정은 **아직 하지 않음** — GENERAL schema 설계·승인 계약 확정 후
  APPLY 단계에서 함께 정리(기존 방침 유지).

## 7. STEP-2 판정

```
WP-PERSISTENCE-02A STEP-2 = DISCOVERY COMPLETE
AS-IS 승인 가능 schema = 0
결론 = GENERAL_INSPECTION_RESULT schema 설계 필요 (STEP-3)
```

제출 후 STOP. DB UPDATE 하지 않는다.
