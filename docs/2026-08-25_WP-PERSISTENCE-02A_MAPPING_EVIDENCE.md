# WP-PERSISTENCE-02A STEP-1 — MAPPING EVIDENCE

- 작성일: 2026-08-25
- 방식: DB SELECT-only 실측. 모든 수치는 조회 시점 실값.
- 목적: AUTO_APPROVABLE=0 / 전건 HUMAN_REVIEW 판정의 실측 근거 제시.

---

## 1. inspection_set 원천 축 (STEP 1 수집 결과)

bridge 대상 324 set 의 원천 식별자 채움율(실측):
```
legal_rule_id       315/324   (distinct 151종)   ← 주 canonical 축
inspection_set_code 315/324
obligation_type     324/324   (동사분류: BEFORE_WORK 188 / INSPECT 128 / REPORT 2 / ACTION 2 / ...)
legal_rule_code       8/324   (거의 비어있음)
template_id           1/324   (거의 없음)
```
legal_rule_id 표본: `AIRACT-002, ELECBIZ-001, FIREACT-011, CON3-SCF-001,
OSHHIGH-002-CON, OSHSTD-004-CON ...` → **법령규칙 코드 체계.**

## 2. runtime_form_schema 원천 축 (STEP 2 수집 결과)

status: **CANDIDATE 323/323 (전건).**

source_trace 는 **2계열**이다(실측):
```
source_table = document_forms       : 260건  → doc_id populated / form_code NULL
source_table = document_form_master :  63건  → form_code populated / doc_id NULL
```
- document_forms 계열(260) 표본:
  `{ "doc_id": "DOC-OSH-050", "form_code": null, "source_id": "<uuid>",
     "source_table": "document_forms" }`
- document_form_master 계열(63)은 form_code 를 가진다(예: OSHACT-FORM-xxx 형태).
- form_name 표본: "안전작업절차서(SOP)", "위험물 제조소등 변경허가 신청서",
  "화학사고예방관리계획서 변경검토 신청서", "검사대상기기 개조검사 신청서" ...
  → 대부분 **신청서/신고서/허가서** 계열.

document_family 분포(표본): 일상 98 / 정기 72 / 작업시 24 / 착공전 23 / 사고시 22 /
UNRESOLVED(CUSTOM 21 + OFFICIAL 15) / 변경시 15 / ... / 안전점검 1 / 위험성평가 1 / 검사 1.
→ "점검 결과 문서"로 명확한 것은 소수. 다수는 행정 신청/신고/보고 서식.

## 3. STEP 3 — 공통 KEY 탐색 결과: exact key 부재

세 식별자 체계가 서로 다름(실측 대조):
```
inspection_set.legal_rule_id  = AIRACT-002 / ELECBIZ-001 / FIREACT-011   (코드)
document_forms.law_ref        = "산안법 제57조" / "위험물안전관리법 제6조"   (자유텍스트)
document_forms.doc_id         = DOC-BLD-001 / DOC-OSH-050                  (문서일련번호)
```
- document_forms 계열(260) 축(doc_id / law_ref) 과 inspection_set 축(legal_rule_id
  코드) 사이에 공유 exact identifier 없음. 접점은 law_ref 자유텍스트뿐 → E4(금지).

### 3-1. document_form_master 계열(63)의 form_code exact 비교 — 전건 0
form_code 를 가진 63개 schema 를 inspection_set 원천 식별자와 **직접 exact 비교**:
```
63 schema.form_code ↔ inspection_sets.inspection_set_code = 0건 일치
63 schema.form_code ↔ inspection_sets.legal_rule_id       = 0건 일치
63 schema.form_code ↔ inspection_sets.legal_rule_code     = 0건 일치
inspection_sets.template_id ↔ schema.source_id            = 0건 일치
```
→ form_code 축(document_form_master 계열)으로도 inspection_set 과 exact 연결 0.

### 3-2. 중간 연결(work_schedules.form_code)도 전건 비어있음
```
current work_schedules.form_code = 0/66
work_schedules_old.form_code     = 0/66
migration snapshot.form_code     = 0/66
```
→ inspection → work_schedules.form_code → schema 경유 경로도 데이터 부재로 불가.

### 3-3. canonical mapping record 부재 (DB + live code)
inspection_set / legal_rule → form_code / schema 를 잇는 다른 canonical mapping 이
DB 에서 확인되지 않았고, tai-api live code 에도 이를 연결하는 별도 하드코딩 mapping 이
확인되지 않았다.

### document_forms 컬럼 확인
`doc_id, has_legal_form, law_ref, obligation, submit_method_legal, submit_org_code`
→ legal_rule_id 같은 canonical rule UUID/코드 컬럼 **없음.** law_ref 는 자유텍스트.

## 4. obligation_form_mapping 은 다리가 되지 못함 (§16 확인)

obligation_form_mapping (11건 전량 실측):
```
obligation_code          form_code           성격
OSH_MGR_REPORT      →    OSHACT-FORM-002     안전관리자 선임 보고서
OSH_ACCIDENT_REPORT →    OSHACT-FORM-030     산업재해조사표
ELEC_MGR_APPOINT    →    ELEC-FORM-001       전기안전관리자 선임신고서
FIRE_SELFCHECK_REPORT →  FIRE-FORM-002       소방시설 점검결과보고서
...
```
- 이것은 **선임/사고/신고 등 행정보고 의무 → 신고서식** 매핑. "점검 결과 문서" 아님.
- obligation_code(`OSH_MGR_REPORT`) 는 inspection_set.obligation_type
  (`BEFORE_WORK`/`INSPECT`/...) 과 **완전히 다른 코드체계** → 조인 불가.
- 출력 form_code(`OSHACT-FORM-002`) 는 runtime_form_schema 의 document_form_master
  계열 form_code 와 exact 비교해도(위 §3-1 계열 검증과 동일 축) inspection_set 원천과
  0건 일치 → obligation 경유로도 inspection_set↔schema 연결 성립 안 함.
- → obligation_form_mapping = EVIDENCE SOURCE 로도 inspection_set↔schema 다리
  역할 불가. FINAL MAPPING SoT(runtime_inspection_bridge)와 혼동하지 않음(§16 준수).

## 5. 기존 명시적 mapping record 부재 (E1 확인)

- document_requirement_rule = form_code ↔ 문서필드 정의(field_code/field_name).
  legal_rule_id ↔ schema 매핑 아님. form_code 축이라 inspection_set 과 접점 없음.
- company_form_mapping = 0 rows(빈 테이블, §15 대로 SoT 로 쓰지 않음).
- 그 외 legal_rule_id ↔ runtime_form_schema.id 를 직접 잇는 record 를 가진 테이블
  = 발견되지 않음.
→ **E1(DIRECT IDENTITY) 매핑 record 0건.**

---

## 6. 분류별 표본 (지시서 §19)

### AUTO_APPROVABLE 표본 — 해당 없음 (0건)
exact structural evidence 가 0 이므로 AUTO_APPROVABLE 표본을 제시할 수 없다.
이것이 이번 STEP 의 핵심 결과다.

### HUMAN_REVIEW 표본 (전건 이 분류, 대표 3건)
| inspection_set (법령축) | pool 내 텍스트 근접 후보(참고) | 왜 HUMAN_REVIEW |
|---|---|---|
| legal_rule_id=FIREACT-011 (소방 작동기능 점검) | schema "소방시설 점검결과보고서" 계열 존재 가능 | 근접은 law_ref 텍스트뿐, exact key 없음 → 사람 확인 필요 |
| legal_rule_id=OSHACT-010 (위험성평가) | schema document_family="위험성평가"(1건) 존재 | 1:1 확정할 canonical key 없음, 목적 부합 여부 사람 판단 |
| legal_rule_id=ELECBIZ-001 (전기 사용전검사) | schema "검사" 계열 후보 다수 가능 | 후보 복수 가능 + exact key 없음 → 사람 검토 |

주: 위 "근접 후보"는 **참고용 관찰**일 뿐, 자동 매핑 근거로 쓰지 않는다(§3).

### UNMAPPED 표본 — 이번 STEP 자동 확정 없음 (0건)
schema pool 이 존재하므로 "대응 없음"을 자동 단정하지 않는다. 개별 UNMAPPED /
NEW_FORM_REQUIRED 확정은 사람 검토 산물.

### CONFLICT — 해당 없음 (0건, 빈 표)
exact direct mapping 이 0 이므로 direct 근거 충돌이 성립하지 않음.

---

## 7. 결론

```
E1 (DIRECT IDENTITY)          = 0
E2 (EXPLICIT STRUCTURAL TRACE)= 0
E3 (PARTIAL STRUCTURAL)       = 0 (구조 접점 자체가 없음)
E4 (NAME/TEXT ONLY)           = 잠재적으로 다수 (그러나 AUTO 금지)
E0 (NO EVIDENCE)              = 나머지

AUTO_APPROVABLE = 0
전건 HUMAN_REVIEW = 324
```
inspection_set(법령규칙 legal_rule_id 축)과 runtime_form_schema(2계열: document_forms
doc_id 축 260 + document_form_master form_code 축 63)는 **공유 canonical key 를 갖지
않는다.** form_code 축조차 inspection_set 원천과 exact 비교 0건이었다. 이것이 B1 DATA
POPULATION 이 여전히 BLOCKED 인 근본 이유다.
