# WP-PERSISTENCE-02A STEP-1 — BLOCKER DECISION

- 작성일: 2026-08-25
- 모드: READ-ONLY. mutation 0. repo commit 0 (승인 대기).

---

## 1. 최종 보고 (지시서 §27 형식)

```
WP-PERSISTENCE-02A STEP-1

INSPECTION SETS             = 324
RUNTIME FORM SCHEMAS        = 323

AUTO_APPROVABLE             = 0
HUMAN_REVIEW                = 324
UNMAPPED                    = 0
CONFLICT                    = 0
(합계 324 = TOTAL ✓)

MAPPING SoT
= runtime_inspection_bridge.runtime_form_schema_id

CARDINALITY
= inspection_set → schema 0..1

RUNTIME SCHEMA ELIGIBILITY
= APPROVED_FOR_RUNTIME_USE ONLY
= 현재 0/323 (전건 CANDIDATE)

B1 DESIGN
= RESOLVED   (SoT/unit/cardinality/eligibility 원칙 확정)

B1 DATA POPULATION
= BLOCKED    (exact key 부재 + runtime-approved schema 0)

IMPLEMENTATION READINESS
= BLOCKED

CODE MUTATION = 0
DB MUTATION   = 0
API MUTATION  = 0
REPO MUTATION = 0
DEPLOY        = 0
```

## 2. 왜 BLOCKED 인가 (2개 독립 축)

**축 1 — exact structural key 부재:**
inspection_set 의 원천은 법령규칙(legal_rule_id: `AIRACT-002` 코드).
runtime_form_schema 의 원천은 **2계열**:
- document_forms 260건 (doc_id `DOC-OSH-050` / form_code NULL)
- document_form_master 63건 (form_code populated / doc_id NULL)

두 축을 잇는 canonical key 없음:
- document_forms 계열 접점 = law_ref(자유텍스트) ↔ legal_rule_id → 텍스트 매칭(E4, §3 금지)
- document_form_master 계열 form_code 63건 ↔ inspection_set_code / legal_rule_id /
  legal_rule_code exact 비교 = **전건 0**; template_id ↔ schema.source_id = 0
- work_schedules.form_code(현행/old/migration snapshot 전부 0/66), 그리고 DB·live code
  에 별도 canonical mapping record 부재
→ E1=0, E2=0 → AUTO_APPROVABLE 0.

**축 2 — runtime-approved schema 0:**
323 schema 전건 CANDIDATE. RUNTIME ELIGIBLE(APPROVED_FOR_RUNTIME_USE) 기준상
연결할 승인 schema 자체가 0. → 매핑을 채우려 해도 대상 없음.

두 축 모두 **사람 판단이 선행**되어야 해제된다.

## 3. B1 상태 갱신

```
B1 FORM_SCHEMA_MAPPING_MISSING
= DESIGN PRINCIPLE RESOLVED   (이번 STEP 로 SoT·단위·cardinality·eligibility 확정)
= DATA POPULATION BLOCKED     (증거 있는 자동매핑 0 → 채울 값 없음)
```
이번 STEP 만으로 B1 을 자동 해제하지 않는다(§20 준수). 해제 조건 7단계 중
현재 1(matrix 작성)만 완료, 2~7(근거검증·HUMAN_REVIEW 판정·CONFLICT 해결·schema
승인·운영자 mapping 승인·DB population)은 미완.

## 4. 운영자 결정이 필요한 지점 (B1 DATA 해제의 실제 관문)

이번 STEP 이 드러낸 핵심: **자동 매핑으로는 한 건도 못 채운다.** 따라서 다음은
"코드/데이터 조사"가 아니라 **정책·설계 결정**이다.

1. inspection_set(법령규칙 legal_rule_id 축) 과 runtime_form_schema
   (2계열: document_forms doc_id 260 + document_form_master form_code 63)를
   무엇으로 이을 것인가?
   - (a) legal_rule_id ↔ document_forms 를 잇는 **명시적 매핑 테이블을 신설**하고
     사람이 채우는가? (새 SoT 아님 — bridge 는 그대로, 이 테이블은 evidence 원천)
   - (b) 아니면 inspection 도메인에 맞는 "점검 결과 문서" schema 를 **새로 정의**
     하는가? (다수 set 이 대응 문서 부재일 가능성 — NEW_FORM_REQUIRED 후보)
2. runtime_form_schema 323건 중 어떤 것을 APPROVE_FOR_RUNTIME_USE 로 승인하는가?
   (schema 품질/적합성 사람 검토 — 매핑과 분리)
3. 대응 문서가 없는 inspection_set 은 어떻게 처리하는가?
   (UNMAPPED 유지 / NEW_FORM_REQUIRED / 해당 set 은 문서화 대상 제외)

위 3개가 정해지기 전에는 runtime_inspection_bridge.runtime_form_schema_id 를
어떤 값으로도 안전하게 채울 수 없다.

## 5. 경계 재확인 (건드리지 않은 것)

- B3(manual complete single id 미보장) = 이번 STEP 흡수 안 함(§21).
- submitted_by(CD5-1) = 수정 안 함(§22).
- generated file / PDF / Storage = WP-PERSISTENCE-03(§23).
- 1:N 확장 = 하지 않음. MULTI-DOCUMENT REQUIREMENT 발견 시 별도 design change(§14).
- company_form_mapping = 새 SoT 로 만들지 않음(§15).
- obligation_form_mapping = FINAL SoT 로 승격 안 함, 다리 역할도 실패 확인(§16).

## 6. 다음 안전한 순서

```
현재 STEP-1 산출 = "승인 가능한 mapping matrix" 준비 시도
결과 = 자동 승인 가능 매핑 0 / 전건 HUMAN_REVIEW

→ 다음은 DB population 이 아니라, §4 의 3개 정책 결정.
→ 운영자가 매핑 방식을 정한 뒤에야 STEP-2(근거 있는 매핑 채우기)로 진행.
→ 그 전까지 runtime_inspection_bridge UPDATE 금지.
```

repo commit 은 승인 후. 이번 STEP 산출물 4종은 outputs 에만 둔다.
