# WP-PERSISTENCE-02A STEP-3 — FINAL DECISION

- 작성일: 2026-08-25
- 모드: READ-ONLY FINAL DESIGN 완료. CODE 0 / DB SELECT ONLY / API 0 / REPO 0 / DEPLOY 0.
- docs SoT: taieng@`ad3ae0f3`

---

## 1. 한 문장 결론

safety_inspection 결과를 기존 Runtime Document Engine 안에서 손실 없이 보존하는
단일 범용 GENERAL_INSPECTION_RESULT schema 의 계약이 **실측 컬럼 기반으로 확정**됐다.
새 테이블/엔진/mapping table 없이 표현 가능하다. → **DESIGN PASS.**

---

## 2. Conceptual Example (지시서 §24) — 실데이터 INSERT 없음

실제 production 표본(inspection 217f0c15 + results 3건)을 근거로 한 SOURCE → GENERAL
payload 필드 매핑. **개념 예시일 뿐 INSERT 하지 않는다.**

### SOURCE (safety_inspection_results 실측 3행)
```
result_id=22cbf984 | item_name=보호구 착용 확인   | result_code=NORMAL | value_text=ok | note="" | set_item_id=null
result_id=524aa712 | item_name=설비 이상 유무     | result_code=NORMAL | value_text=ok | note="" | set_item_id=null
result_id=f2cb6fbd | item_name=작업 구역 정리정돈 | result_code=NORMAL | value_text=ok | note="" | set_item_id=null
(inspection_id 공통 = 217f0c15-...)
```

### GENERAL document (개념)
```
runtime_document_data:
  source_inspection_id = 217f0c15-...          ← FK anchor (identity SoT, payload 아님)
  form_schema_id       = <GENERAL schema id>
  factory_id/company_id = 서버 chain 파생
  runtime_data_json    = 아래

runtime_data_json = {
  "inspection_subject": "<asset/assignment 표시>",
  "inspected_at": "2026-08-09T23:45:52",
  "inspection_title": "<inspection_set 명>",
  "inspector_display": "<표시용>",
  "inspection_results": [
    { "result_id":"22cbf984","set_item_id":null,"item_name":"보호구 착용 확인",
      "raw_code":"NORMAL","value_text":"ok","value_number":null,"note":"",
      "checked_at":"2026-08-09T23:45:52","photo_url":null,"photo_urls":null },
    { "result_id":"524aa712","set_item_id":null,"item_name":"설비 이상 유무",
      "raw_code":"NORMAL","value_text":"ok","value_number":null,"note":"",
      "checked_at":"2026-08-09T23:45:52","photo_url":null,"photo_urls":null },
    { "result_id":"f2cb6fbd","set_item_id":null,"item_name":"작업 구역 정리정돈",
      "raw_code":"NORMAL","value_text":"ok","value_number":null,"note":"",
      "checked_at":"2026-08-09T23:45:52","photo_url":null,"photo_urls":null }
  ]
}
```
주: overall_result/corrective_summary/evidence_files 는 v1 payload 에 없다 — source
컬럼이 없는 파생/요약 필드이므로 제외(추론 방지). 종합판정은 승인된 aggregation rule
확정 후 별도 버전에서만 도입.

### lossless 검증
```
SOURCE RESULT COUNT   = 3
DOCUMENT RESULT COUNT = 3   (inspection_results 배열 길이)
→ 일치. silent drop 0 / silent merge 0.
각 result_id 로 source 행 1:1 역추적 가능.
raw_code(NORMAL) 원값 보존. display label 미저장.
source_inspection_id 는 anchor 에만, payload 중복 없음.
→ LOSSLESS MAPPING = 검증됨.
```

---

## 3. 최종 보고 (지시서 §28 형식)

```
WP-PERSISTENCE-02A STEP-3

GENERAL_INSPECTION_RESULT
= DESIGN PASS

FORM_TYPE
= CUSTOM

SECTOR POLICY
= NEUTRAL (schema 헤더 sector 미요구 / candidate.sector = NULL / master.sector = NULL)

SOURCE ANCHOR
= runtime_document_data.source_inspection_id

RESULT FIELD
= inspection_results / multi_row

SOURCE RESULT PRESERVATION
= PASS
  (result_id 1:1, count 불변식, raw_code 보존, note/value/photo 보존)

EVIDENCE CONTRACT
= PASS
  (photo_url/photo_urls 참조, binary 미저장, 기존 mechanism 재사용)

RENDERER
= ENHANCEMENT REQUIRED
  (저장 lossless 충족 / inspection_results 사람이 읽는 표 렌더는 후속)

GENERAL SHARING
BEFORE_WORK 188
INSPECT     128
= ELIGIBILITY RULE DEFINED
  (E1–E4 AND + operator explicit; 자동 매핑 금지)

FALSE MAPPED
= 323
= APPLY LATER

B1 DATA POPULATION
= READY FOR SCHEMA APPLY
  (GENERAL 계약 확정 → 다음은 schema 생성/승인 단계)

NEXT
= SCHEMA APPLY (GENERAL schema+candidate+fields 생성, 사람 승인 → APPROVED_FOR_RUNTIME_USE)
  + RENDERER ENHANCEMENT DESIGN (inspection_results 표 렌더, 별도)

CODE MUTATION = 0
DB MUTATION   = 0
API MUTATION  = 0
REPO MUTATION = 0
DEPLOY        = 0
```

---

## 4. PASS 기준 대조 (지시서 §26)

```
[x] GENERAL schema 1종 목적 확정 (canonical evidence document)
[x] 정확한 field contract 확정 (v1 = 5필드, field_key 명시, source-backed only)
[x] inspection_results multi_row contract 확정
[x] source result ↔ document result 1:1 보존 계약 확정 (result_id, count 불변식)
[x] source_inspection_id identity 경계 확정 (anchor only, payload 미저장)
[x] evidence 경계 확정 (photo 참조, binary 금지, 2층 분리)
[x] form_type 하나로 확정 (CUSTOM)
[x] sector 정책 확정 (neutral)
[x] renderer 요구 수준 확정 (저장 충분 / 표 렌더 ENHANCEMENT_REQUIRED)
[x] schema approval gate 확정 (G1–G10)
[x] 316 set 공유/제외 조건 확정 (E1–E4 / X1–X4)
[x] 구현에 추가 schema invention 불필요 (기존 3테이블로 표현 가능)
→ 전 항목 충족 → STEP-3 = DESIGN PASS
```

## 5. BLOCKED 기준 대조 (지시서 §27) — 해당 없음

```
[ ] multi_row 로 source result 표현 불가        → 아님(표현 가능)
[ ] engine 이 nested result lossless 보존 불가   → 아님(list 보존)
[ ] evidence identity 연결 구조 없음             → 아님(photo_url/photo_urls 존재)
[ ] GENERAL 1종으로 INSPECT/BEFORE_WORK 공통 불가 → 아님(공통 contract 성립)
[ ] 공식서식 ↔ GENERAL evidence 경계 분리 불가    → 아님(form_type/제외조건으로 분리)
→ BLOCKED 조건 해당 없음. SCHEMA GAP 없음(§23).
```

---

## 6. 경계 재확인 (건드리지 않은 것)

- schema/field/candidate INSERT 0, bridge UPDATE 0, renderer code 수정 0, false MAPPED 교정 0.
- runtime fallback 없음(§18/§19 explicit only).
- NEW TABLE/ENGINE/MAPPING TABLE 없음(§23).
- provenance = 기존 표준 계보 준수: document_form_master → document_schema_candidate
  (source_table CHECK={document_forms, document_form_master}) → runtime_form_schema.
  MANUAL_DESIGN 등 임의 source_table 금지(CHECK 위반). sector 는 master·candidate 양쪽
  NULL 명시(default BUILDING 오염 방지). document_family=DOCUMENT 재사용(신규 값 안 만듦).
- B3(§21) / B2 transaction(§22) / submitted_by(CD5-1) = 이번 설계에 섞지 않음.
  단 B2 관련: inspection complete → runtime document create → source anchor 의 failure
  semantics 는 GENERAL 계약과 충돌하지 않음(payload 는 anchor 확정 후 채워지므로,
  anchor 실패 시 문서 미생성 상태 = 데이터 손실 아님). 실제 transaction 설계는 구현 WP.
- FINAL mapping SoT = runtime_inspection_bridge 유지.

제출 후 STOP. DB UPDATE 하지 않는다.
