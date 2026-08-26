# WP-PERSISTENCE-03 STEP-0 REV-1 — VIEW MODEL CONTRACT

- 모드: ARCHITECTURE CONTRACT. CODE/DB = 0. Composer = READ-ONLY lazy compose (문서/PDF/storage 생성 없음).

## 1. Success output (canonical)

```json
{
  "inspection_id": "UUID",
  "inspection_set_id": "UUID",
  "schema_id": "dc79ac3c-388c-42dc-b029-3dd9bda54a47",
  "form_code": "GEN-INSPECT-RESULT-001",
  "schema_version": 1,
  "fields": {
    "inspection_subject": "text | null",
    "inspected_at": "ISO8601 | null",
    "inspection_title": "text | null",
    "inspector_display": "text | null",
    "inspection_results": [
      { "result_id":"UUID", "set_item_id":"UUID|null", "item_name":"text|null",
        "raw_code":"NORMAL|ABNORMAL|HOLD|null", "value_text":"text|null", "value_number":"number|null",
        "note":"text|null", "checked_at":"ISO8601|null", "photo_url":"text|null", "photo_urls":"array|[]" }
    ]
  },
  "completeness": { "<required_field>": "OK | REQUIRED_SOURCE_FIELD_MISSING" }
}
```

## 2. Field binding (정정 반영, 정본은 SOURCE_MAP)

| field | binding | 결측 |
|---|---|---|
| inspection_subject | equipment_assets.asset_name via asset_id | null + completeness=REQUIRED_SOURCE_FIELD_MISSING (200 유지) |
| inspected_at | safety_inspections.inspection_date | null + completeness=REQUIRED_SOURCE_FIELD_MISSING |
| inspection_title | inspection_sets.inspection_set_name | null (NOT_REQUIRED) |
| inspector_display | safety_inspections.inspector_id→users.name **only** | null (ws.inspector_name fallback 금지, UUID 금지) |
| inspection_results[] | safety_inspection_results (+set_item join for item_name derivation) | set 미해소면 상위 오류 |

result row: result_id(primary)·set_item_id(secondary)·item_name(result 원문 우선, null이면 set_item 파생, 양측 mismatch→SOURCE_INTEGRITY_ERROR)·raw_code←result_code(rename)·나머지 동명.

## 3. Ordering (DESIGN CONTRACT)

`set_item.item_seq ASC NULLS LAST → result.created_at ASC NULLS LAST → result.id ASC`. item_name tie-break 금지.

## 4. Support gate

schema_id=dc79ac3c AND form_code=GEN-INSPECT-RESULT-001 AND version=1 일 때만 GENERAL 렌더. 그 외 approved schema → UNSUPPORTED_PRESENTATION_SCHEMA.

## 5. completeness

REQUIRED_BY_HUMAN 필드(inspection_subject/inspected_at/inspection_results) 충족 여부 명시. 미충족이어도 값 창작 없이 null + 표기(DECISION-1). source_refs/warnings 등 신규 필드는 소비자 필요성 확정 시 STEP-1에서만.

## 6. Error output

성공 형태 대신 deterministic error object, DB write=0 (정본 ERROR_TAXONOMY). auth/scope는 composer 오류보다 선행(§ AUTH).

## 7. Web View / PDF 공통

Web View(worker history detail 소비) ↘ View Model ↗ future PDF renderer(별도 WP). 본 STEP은 source contract만.
