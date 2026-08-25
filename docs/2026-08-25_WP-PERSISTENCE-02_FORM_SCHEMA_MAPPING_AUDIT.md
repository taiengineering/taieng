# WP-PERSISTENCE-02 — FORM SCHEMA MAPPING AUDIT

- 작성일: 2026-08-25
- 성격: 이번 WP 의 **최우선 BLOCKER 후보**. 여기서 SoT 부재가 확정되면 B1.
- 방식: DB 실측(SELECT-only) + 코드 직독. mutation 0.
- BASELINE tai-api@`2b10e3a6` / REVIEW-TIME main@`2780acf8` (drift +1 = building_register.py only, relevant diff 0)

---

## 0. 결론 (확정)

**FORM SCHEMA MAPPING SoT = NOT FOUND.**

"이 safety_inspection 은 어떤 runtime_form_schema 로 문서를 만들어야 하는가"에
답하는 살아있는 매핑 경로가 존재하지 않는다. 브릿지 테이블은 있으나 최종
runtime_form_schema_id 가 전건 비어 있고, 이를 채우는 writer 도 없다.

→ 지시서 §7·§20 에 따라 **B1 FORM_SCHEMA_MAPPING_MISSING** 판정.
  임의 default schema / 추론 매핑을 설계하지 않는다. 구현 지시서를 만들지 않는다.

---

## 1. runtime_form_schema 자체에 inspection 축이 없다

`runtime_form_schema` 컬럼(실측):
```
id, schema_candidate_id, document_family, form_type, form_name,
field_count, checklist_count, evidence_count, source_trace, status, version
```
→ inspection_type / inspection_set / obligation 같은 "어떤 점검이 이 스키마를
   쓰는가"를 가리키는 역참조 컬럼이 **없다.** 스키마는 서식 정의일 뿐이다.

## 2. safety_inspections 에도 schema 축이 없다

`safety_inspections` 에서 set/schema/form 관련 컬럼 검색 결과 = `asset_id` 뿐.
- form_schema_id 없음
- inspection_type 없음
- inspection_set_id 없음
→ 점검 레코드 자체가 form_schema 를 직접 가리키지 않는다.

## 3. 후보 매핑 테이블 전수 실측

form_schema_id / schema_id / inspection_type / form_code 컬럼을 가진 테이블을
전수 조사한 뒤, inspection → runtime_form_schema.id 로 이어질 수 있는 것만 평가.

| 테이블 | 매핑 축 | 출력 | 실측 | SoT 자격 |
|---|---|---|---|---|
| runtime_inspection_bridge | inspection_set_id | runtime_form_schema_id | 324 rows, **schema_id populated 0/324** | ✗ (최종 id 전건 NULL) |
| company_form_mapping | company | form_schema_id | **0 rows (빈 테이블)** | ✗ |
| obligation_form_mapping | obligation_code | form_**code** (not schema.id) | 11 rows | ✗ (축·출력 불일치) |
| document_form_master | form_code | — | (form_code 계열 schema 원천) | ✗ (inspection 축 없음) |
| work_schedules.form_code | — | form_code | **0/66 populated** | ✗ (전건 NULL) |

## 4. 가장 유력했던 경로의 붕괴 지점

이론적 경로:
```
safety_inspection.assignment_id
  → work_schedules.inspection_set_id           [실측 60/66 populated — OK]
  → runtime_inspection_bridge (inspection_set_id 조인)  [324 rows 존재]
  → runtime_form_schema_id                      [0/324 populated — ★붕괴]
```

즉 경로의 앞부분(inspection → inspection_set)은 데이터가 있으나,
**마지막 홉(inspection_set → form_schema)이 전건 비어 있어 끊긴다.**

### runtime_inspection_bridge.mapping_status 의 함정
```
mapping_status = MAPPED 323 / PARTIAL 1
그러나 runtime_form_schema_id populated = 0 (MAPPED 포함 전건)
```
mapping_detail(jsonb) 표본:
```
note = "Legacy inspection_set_items=0. Runtime checklist_item is authoritative."
law_name / law_article / legal_rule_id / cycle_* 만 존재
runtime_form_schema_id = null
```
→ "MAPPED" 는 **법령 ↔ 점검세트** 매핑을 뜻하지, **점검세트 ↔ form_schema**
   매핑이 아니다. 상태 라벨과 실제 스키마 연결이 불일치한다.

### 대체 경로(form_code)도 죽어 있음
- work_schedules.form_code = 0/66 (전건 NULL)
- obligation_form_mapping.form_code 는 obligation_code 축이라 safety_inspection
  에서 들어갈 키가 없다(safety_inspection 에 obligation_code 없음).

## 5. 코드 확인 — 매핑 writer 부재

`routers/inspection_bridge.py` (blob b6a4eb4c) 직독:
- 전 엔드포인트 **GET(읽기 전용)**.
- runtime_inspection_bridge / inspection_sets / runtime_checklist_item 을 조회만.
- safety_inspection.id 로부터 form_schema_id 를 선택·기록하는 로직 **없음**.

document_engine_svc.create_document 은 form_schema_id 를 **인자로 받기만** 하고,
그 인자를 inspection 기준으로 채워 호출하는 코드가 tai-api 어디에도 없다
(WP-PERSISTENCE-01 에서 source_inspection_id writer 0 과 동일 계열).

---

## 6. Q5–Q7 답변

**Q5. 한 inspection 에서 어떤 form_schema_id 를 선택해야 하는가?**
→ **결정 불가.** 살아있는 선택 규칙/데이터가 없다.

**Q6. form_schema_id 선택의 기존 SoT 가 존재하는가?**
→ **NOT FOUND.** 브릿지 구조는 존재하나 최종 id 전건 NULL + 채움 writer 부재.

**Q7. SoT 가 없다면 현재 구현은 BLOCKED 인가?**
→ **BLOCKED (B1).** 여기서 임의 매핑을 만들면 "또 하나의 추론 로직"이 되어
  지시서 §5 원칙 4(form_schema_id 추론 금지)를 정면으로 위반한다.

---

## 7. BLOCKER 판정

```
FORM SCHEMA MAPPING SoT = NOT FOUND
→ B1 FORM_SCHEMA_MAPPING_MISSING (CONFIRMED by data + code)
→ WP-PERSISTENCE-02 = DESIGN BLOCKED AT FORM-SCHEMA MAPPING
→ 구현 지시서(FIND/REPLACE) 생성 금지. blocker decision 을 운영자에게 제출.
```

### 7-1. WP-PERSISTENCE-02A STEP-1 로 확정된 설계 결정 (갱신)
```
MAPPING SoT   = runtime_inspection_bridge.runtime_form_schema_id
MAPPING UNIT  = inspection_set_id
CARDINALITY   = inspection_set → schema 0..1
                (runtime_form_schema 1 → inspection_set N 허용)
RUNTIME ELIGIBLE = runtime_form_schema.status = APPROVED_FOR_RUNTIME_USE ONLY
NO FALLBACK / NO INFERENCE / NO DEFAULT SCHEMA

CURRENT DATA:
  bridge runtime_form_schema_id = 0/324
  runtime-approved schema       = 0/323 (전건 CANDIDATE)

B1 = DESIGN PRINCIPLE RESOLVED / DATA POPULATION BLOCKED
```
근거: 02A STEP-1 MAPPING_EVIDENCE — inspection_set(법령규칙 legal_rule_id 축)과
runtime_form_schema(2계열: document_forms doc_id 260 + document_form_master form_code 63)가
공유 canonical key 를 갖지 않아(form_code 축 exact 비교도 0건) 자동 매핑 0건, 전건 HUMAN_REVIEW.

## 8. 운영자 결정이 필요한 선행 질문 (해소되어야 B1 해제)
- (a) inspection_set → runtime_form_schema 매핑을 무엇이 정본으로 채울 것인가?
  (누가/언제 runtime_inspection_bridge.runtime_form_schema_id 를 확정하는가)
- (b) 매핑 단위는 inspection_set 인가, 법령(legal_rule)인가, obligation 인가?
- (c) 한 inspection_set 이 복수 form_schema 를 가질 수 있는가(→ cardinality 와 연동)?
- 위 3개가 정해지기 전에는 source_anchor writer 의 form_schema_id 입력을
  어떤 값으로도 채울 수 없다.
