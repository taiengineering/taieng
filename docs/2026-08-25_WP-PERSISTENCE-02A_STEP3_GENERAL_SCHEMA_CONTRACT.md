# WP-PERSISTENCE-02A STEP-3 — GENERAL SCHEMA CONTRACT

- 작성일: 2026-08-25
- 모드: READ-ONLY FINAL DESIGN. CODE 0 / DB SELECT ONLY / API 0 / REPO 0 / DEPLOY 0.
- schema INSERT 금지, runtime_field INSERT 금지, bridge UPDATE 금지, renderer 수정 금지.
- docs SoT: taieng@`ad3ae0f3`

---

## 0. 목적 (지시서 §3)

GENERAL_INSPECTION_RESULT = safety_inspection 1건의 실제 점검 사실(대상/시각/수행자/
개별 항목/결과/비고/시정조치/증거)를 기존 Runtime Document Engine 안에서 손실 없이
보존하는 **범용 canonical evidence document** schema 1종.

법정 공식서식이 아니다. 공식 신고서/검사성적서/법정 지정양식을 대체하면 FAIL.

이 문서는 **계약 정의**이며 어떤 row 도 INSERT 하지 않는다.

---

## 1. 엔진 계약 실측 (설계 근거, CHECK 제약 직독)

```
runtime_form_schema
  form_type ∈ {OFFICIAL, CUSTOM, INTERNAL}                              (chk_rfs_form_type)
  status    ∈ {CANDIDATE, NEEDS_HUMAN_REVIEW, APPROVED_BY_HUMAN,
               APPROVED_FOR_RUNTIME_USE, REJECTED_BY_HUMAN, ARCHIVED}   (chk_rfs_status)
  NOT NULL  : id, schema_candidate_id, form_type, document_family, status,
              version, created_at, updated_at

runtime_field
  input_type      ∈ {text, textarea, number, date, datetime, checkbox, radio,
                     select, file, image, signature, measurement, table, multi_row}
  required_status ∈ {CANDIDATE_ONLY, NEEDS_HUMAN_REVIEW, REQUIRED_BY_HUMAN, NOT_REQUIRED}
  status          ∈ {CANDIDATE, NEEDS_HUMAN_REVIEW, APPROVED_BY_HUMAN, REJECTED_BY_HUMAN}
  NOT NULL        : id, form_schema_id, field_label, input_type, required_status,
                    status, created_at

document_schema_candidate  (schema_candidate_id 의 원천)
  NOT NULL: id, source_table, source_id, status
  nullable: doc_id, doc_name, form_code, form_type, category, sector, *_count, created_at
```

함의:
- schema.status 에 APPROVED_FOR_RUNTIME_USE 존재 → 승격 목표값 유효.
- field.status 에는 APPROVED_FOR_RUNTIME_USE 없음 → field 최종 승인값 = APPROVED_BY_HUMAN.
- schema_candidate_id NOT NULL → GENERAL 도 원천 candidate 1건 선행 필요.
- input_type 에 multi_row / measurement / file / image / signature 사용 가능.

---

## 2. form_type 결정 (지시서 §13) — FINAL = CUSTOM

관례 직독 결과:
```
CUSTOM   = 실사용 점검/기록 문서 (전기설비 점검일지, 안전점검 결과서, 소방 자체점검
           결과서, 각종 작업 전 점검표 …) → 운영 데이터를 담는 실제 문서
INTERNAL = "자유서식 작성 가이드라인", "위험성평가 자유서식 예시", "TBM 시트 예시" …
           → 가이드/예시/템플릿(내부 참고용)
```
GENERAL_INSPECTION_RESULT 는 실제 점검 결과 데이터를 담는 실사용 evidence document 다.
"가이드/예시"인 INTERNAL 이 아니라 실사용 문서 계열인 **CUSTOM** 이 시스템 의미에 정확히
맞는다. OFFICIAL 은 금지(법정서식 아님).

→ **form_type = CUSTOM (FINAL, 단일 확정).** 애매하게 둘 다 허용하지 않음. 새 enum 없음.

---

## 3. sector 정책 (지시서 §14) — sector-neutral

- runtime_form_schema 에는 sector 컬럼이 **없다**(실측). sector 는 document_form_master
  및 document_schema_candidate 에만 있고 nullable.
- **주의(실측)**: document_form_master.sector 의 DB default = `'BUILDING'`. INSERT 시
  sector 를 생략하면 BUILDING 으로 채워져 범용 schema 가 다시 BUILDING 전용으로 오염된다.
  → **계보 [1] master, [2] candidate 양쪽에서 sector=NULL 을 명시적으로 INSERT** 해야 한다.
- BUILDING/MANUFACTURING/CONSTRUCTION 전용 분리 안 함. 임의 값 생성 없음.
→ **SECTOR POLICY = NEUTRAL (master.sector=NULL, candidate.sector=NULL 명시). BLOCKER 아님.**

---

## 4. GENERAL schema 헤더 계약 (runtime_form_schema 1 row 정의)

```
form_name       = "점검 결과 기록서 (범용)"
form_type       = CUSTOM
document_family = "DOCUMENT"                 (NOT NULL; 기존 값 재사용, 신규 값 안 만들음)
status          = CANDIDATE                  (생성 시작값; 사람 승인 후 APPROVED_FOR_RUNTIME_USE)
version         = 1
schema_candidate_id = (신규 document_schema_candidate 1건, §6 계보)
source_trace    = { "doc_id": null,
                    "form_code": "GEN-INSPECT-RESULT-001",
                    "source_id": "<document_form_master.id>",
                    "source_table": "document_form_master" }
field_count     = 5
checklist_count = 0                          (반복은 multi_row 로 표현; checklist 테이블 미사용)
evidence_count  = 0                          (runtime_evidence_field 미생성; 사진은 result payload 에 보존)
```

---

## 5. GENERAL schema 필드 계약 (runtime_field rows 정의) — v1 = 5필드

field_key 를 **명시 부여**한다(후보 STD 들이 전건 NULL 이라 매핑 불가였던 문제의 직접 해소).
field_key 는 runtime_data_json 저장 키가 된다(RESULT_PAYLOAD_CONTRACT 참조).

v1 원칙: **source-backed 데이터만** 필드로 둔다. source 컬럼이 없는 파생/요약 필드는
GENERAL v1 에서 제외한다(아래 "제외" 참조).

| order | field_label | field_key | input_type | required_status | source(§4 실측) |
|---|---|---|---|---|---|
| 1 | 점검 대상 | inspection_subject | text | REQUIRED_BY_HUMAN | asset/assignment 파생(표시용) |
| 2 | 점검 일시 | inspected_at | datetime | REQUIRED_BY_HUMAN | safety_inspections.inspection_date |
| 3 | 점검 세트/제목 | inspection_title | text | NOT_REQUIRED | inspection_set 명(표시용) |
| 4 | 점검자(표시) | inspector_display | text | NOT_REQUIRED | inspector 표시용(§11, actor 아님) |
| 5 | **점검 항목별 결과** | inspection_results | **multi_row** | REQUIRED_BY_HUMAN | ★safety_inspection_results (RESULT_PAYLOAD_CONTRACT) |

```
field_count = 5 / checklist_count = 0 / evidence_count = 0
```

### v1 제외 필드 (근거)
- **overall_result 제외**: safety_inspections/results 에 "inspection 전체 종합 판정"
  컬럼이 **없다**(실측: status_code=완료상태, result_code=개별항목). 종합값을 만들면
  승인되지 않은 aggregation rule 로 계산한 **파생값(추론)**이 된다 → v1 제외.
- **corrective_summary 제외**: 대응하는 source 컬럼 없음 → v1 제외.
- **evidence_files 제외**: evidence_count 는 runtime_evidence_field row 수와 일치하는
  개념(실측)이며 일반 runtime_field(file)와 다르다. v1 은 runtime_evidence_field 를
  만들지 않으므로 evidence_count=0. 점검항목 사진은 이미 inspection_results[].photo_url
  / photo_urls 로 source 값 그대로 보존됨. 문서 전체 첨부가 향후 필요하면 기존
  evidence_vault_link 경로 사용(새 evidence field 발명 안 함).

메모:
- signature 필수화 안 함(작업자 앱 미인증 경로 존재; ACTOR=PARTIAL 과 정합).
- factory/site 는 헤더 필드로 두지 않는다: tenant(factory_id/company_id)는 서버가
  anchor chain 에서 확정하는 값이지 사용자 입력 필드가 아님(§12, TENANT boundary).

---

## 6. provenance 정본 계보 (지시서 정정 — DB CHECK 준수)

runtime_form_schema.schema_candidate_id 는 NOT NULL 이고, document_schema_candidate.
source_table 은 **CHECK 로 {document_forms, document_form_master} 만 허용**한다(실측).
따라서 임의 source_table(MANUAL_DESIGN 등)은 INSERT 실패한다. GENERAL 도 기존 표준
계보(STD-INSPECT-001 과 동일 경로)를 따른다:

```
[1] document_form_master (신규 1 row)
    form_code     = "GEN-INSPECT-RESULT-001"
    form_name     = "점검 결과 기록서 (범용)"
    form_type     = "STANDARD"          (master 계열 관례)
    form_category = "DOCUMENT"
    sector        = NULL                ← ★ 반드시 명시 (컬럼 default='BUILDING' 이므로
                                            생략 시 BUILDING 오염 → 범용성 파괴)

[2] document_schema_candidate (신규 1 row)
    source_table = "document_form_master"   (CHECK 허용값)
    source_id    = <위 [1] master.id>
    form_code    = "GEN-INSPECT-RESULT-001"
    form_type    = "STANDARD"
    category     = "DOCUMENT"
    sector       = NULL                     ← 명시
    status       = "CANDIDATE"
    field_count=5 / checklist_count=0 / evidence_count=0

[3] runtime_form_schema (신규 1 row)
    schema_candidate_id = <위 [2] candidate.id>
    form_type       = "CUSTOM"          (runtime 계열 관례: master STANDARD → runtime CUSTOM)
    document_family = "DOCUMENT"         (기존 값 재사용, 신규 값 만들지 않음)
    status          = "CANDIDATE"        (사람 승인 후 APPROVED_FOR_RUNTIME_USE)
    version         = 1
    field_count     = 5
    checklist_count = 0
    evidence_count  = 0
    source_trace    = { "doc_id": null,
                        "form_code": "GEN-INSPECT-RESULT-001",
                        "source_id": "<document_form_master.id>",
                        "source_table": "document_form_master" }
```

- 계보 근거(STD-INSPECT-001 실측): master(STANDARD/DOCUMENT/BUILDING) → candidate
  (document_form_master/STANDARD/DOCUMENT) → runtime(CUSTOM/DOCUMENT). GENERAL 은 여기서
  sector 만 NULL 로 바꿔 범용화한다(STD-INSPECT-001 이 BUILDING 오염된 것과 대비).
- source_trace 도 기존 패턴(doc_id/form_code/source_id/source_table) 그대로. 신규 형식
  발명 안 함.

---

## 7. 이번 STEP 이 만들지 않는 것 (경계)

- schema/field/candidate INSERT = 0 (계약 정의만).
- bridge UPDATE = 0, mapping = 이후 단계.
- runtime fallback = 없음(explicit 승인·매핑만, §18/§19).
- NEW TABLE/ENGINE/MAPPING TABLE = 없음. 기존 3테이블 재사용.
- 도메인별 schema = 없음. GENERAL 1종만.
