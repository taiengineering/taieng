# WP-PERSISTENCE-02A STEP-3 — RESULT PAYLOAD CONTRACT

- 작성일: 2026-08-25
- 성격: inspection_results(multi_row) 저장 계약. safety_inspection_results **실제 컬럼**
  기반(지시서 §4·§7·§8). 예상 shape 를 먼저 정하지 않고 실측 컬럼으로 확정.
- 방식: DB SELECT only. mutation 0.

---

## 1. source 실제 컬럼 (직독, 없는 컬럼 가정 금지)

```
safety_inspections
  id, assignment_id, asset_id, inspector_id, inspection_date,
  status_code, submitted_by, factory_id

safety_inspection_results
  id                    uuid   NOT NULL   ← item identity 1순위
  inspection_id         uuid              ← 부모 FK
  inspection_set_item_id uuid             ← checklist/item canonical id (부분 채움: 3/8)
  item_name             text              ← 원문 item text
  result_code           text              ← result/status raw
  value_text            text              ← 값(텍스트)
  value_number          numeric           ← 값(수치)
  note                  text              ← 비고
  photo_url             text              ← evidence(단일)
  photo_urls            jsonb             ← evidence(복수)
  checked_at            timestamptz       ← 점검시각
  created_at            timestamp
```

실측 값:
- result_code = 전건 `NORMAL` (C-2 canonical NORMAL/ABNORMAL/HOLD 와 일치. PASS/FAIL/NA 아님)
- inspection_set_item_id = 3/8 채움(nullable)
- photo_url / photo_urls = 전건 비어있음(컬럼은 존재)

---

## 2. inspection_results multi_row 계약 (지시서 §7)

```
field_key  = inspection_results
input_type = multi_row
value      = JSON array  (runtime_data_json["inspection_results"])
```

각 배열 원소(1개) = safety_inspection_results 1행(정확히 1:1). 계약 shape 는 **실측
컬럼만** 사용:

```json
{
  "result_id":   "<safety_inspection_results.id>",          // item identity 1순위(필수)
  "set_item_id": "<inspection_set_item_id | null>",          // 2순위(nullable)
  "item_name":   "<item_name>",                              // 원문 텍스트(서버 마스터)
  "raw_code":    "<result_code>",                            // raw 보존(§9)
  "value_text":  "<value_text | null>",
  "value_number":"<value_number | null>",
  "note":        "<note | null>",
  "checked_at":  "<checked_at | null>",
  "photo_url":   "<photo_url | null>",                       // evidence 연결(§10)
  "photo_urls":  "<photo_urls jsonb | null>"                 // evidence 연결(§10)
}
```

- 필드 이름은 source 컬럼명을 그대로 따른다(발명 최소화). 없는 컬럼은 넣지 않는다.
- display label 은 여기에 truth 로 저장하지 않는다(§9). raw_code 가 truth.

---

## 3. Item-level identity (지시서 §8) — 실측 검증된 우선순위

```
1. result_id   = safety_inspection_results.id   (NOT NULL, 항상 존재 → primary identity)
2. set_item_id = inspection_set_item_id         (nullable, 3/8 채움 → 보조 identity)
3. item_name   = 원문 item text                 (텍스트, 재생성 근거로 쓰지 않음)
4. raw_code    = result_code
5. note
```
- 각 result item 은 **result_id 로 source 를 다시 특정**할 수 있다(1순위 항상 존재).
- 이름/텍스트만으로 identity 를 재생성하지 않는다(§8, §10 준수).

---

## 4. 필수 불변식 (지시서 §7)

```
SOURCE RESULT COUNT = DOCUMENT RESULT COUNT
silent drop  = 0
silent merge = 0
semantic summary 로 원본 대체 = 금지
```
- writer 구현 시 `len(inspection_results 배열) == count(safety_inspection_results WHERE
  inspection_id = anchor)` 를 불변식으로 검증(구현 WP 에서 테스트).
- 요약/종합 필드는 GENERAL v1 에 포함하지 않는다(source 컬럼 부재 → 추론 방지). 따라서
  "요약이 원본 배열을 대체"하는 위험 자체가 v1 에는 없다. 원본 배열 = 유일한 result truth.

---

## 5. Result Code Preservation (지시서 §9)

- raw_code = safety_inspection_results.result_code 원값 그대로 저장(현재 관측값 NORMAL).
- 문서 생성 과정에서 다른 의미로 변환 금지.
- 표시용 한글 label 이 필요하면 renderer 단계에서 `raw_code → display_label` 매핑
  (예: NORMAL→정상, ABNORMAL→이상, HOLD→보류)을 적용하되, **display_label 은
  payload 의 truth 가 아니다.** payload 에는 raw_code 만 저장.
- display 매핑 테이블은 C-2 canonical 기준(NORMAL/ABNORMAL/HOLD)으로 renderer 가 소유.

---

## 6. source_inspection_id 경계 (지시서 §5)

- payload(runtime_data_json)에 source_inspection_id 를 **중복 truth 로 저장하지 않는다.**
- identity SoT = runtime_document_data.source_inspection_id (FK anchor, WP-02).
- 표시용 inspection number/code 가 필요하면 헤더 표시 필드로 넣을 수 있으나 identity
  SoT 로 사용 금지. (현재 safety_inspections 에 사람이 읽는 번호 컬럼은 없음 → 표시용도
  당장 필요 없음.)

---

## 7. SOURCE RESULT PRESERVATION 판정

```
result_id (NOT NULL) 로 1:1 식별 가능       → PASS
result_code raw 보존 가능                    → PASS
note / value_text / value_number 보존 가능   → PASS
photo 연결정보(photo_url/photo_urls) 보존 가능 → PASS
count 불변식 표현 가능                        → PASS
→ SOURCE RESULT PRESERVATION = PASS
```
현재 runtime_field.multi_row + runtime_data_json(list) 로 위 전부 표현 가능.
SCHEMA GAP 없음(§23 해당 없음).
