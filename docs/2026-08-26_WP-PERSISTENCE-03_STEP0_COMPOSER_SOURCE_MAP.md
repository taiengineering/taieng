# WP-PERSISTENCE-03 STEP-0 REV-1 — COMPOSER SOURCE MAP

- 모드: READ-ONLY CORRECTION. DB/CODE/DEPLOY/COMMIT = 0.
- repo 기준점(HEAD): taieng `a832afe36a0b37e47c91f62ce38fd0c47bbaf245` · tai-api `35960ecf3ed76d50c0d40ce51f0cd2d3210a356d` · tai-admin `94a5a800554985b601cc31c71787c2ac84d65488`.
- mapped set `7fee7518` → schema `dc79ac3c` (GEN-INSPECT-RESULT-001, APPROVED, v1). positive `3f9cf36f`; negative(orphan) `217f0c15`.

## 0. GENERAL schema field (실측)

runtime_field(form_schema_id=dc79ac3c), order 1..5: inspection_subject(점검 대상,text,REQUIRED_BY_HUMAN) · inspected_at(점검 일시,datetime,REQUIRED_BY_HUMAN) · inspection_title(점검 세트/제목,text,NOT_REQUIRED) · inspector_display(점검자(표시),text,NOT_REQUIRED) · inspection_results(점검 항목별 결과,multi_row,REQUIRED_BY_HUMAN). source_trace는 form 정의 출처(document_form_master)만 → inspection source 바인딩은 본 계약에서 확정.

## 1. INSPECTION → SET (P-A primary / P-B corroboration)

safety_inspections에 inspection_set_id 직접 컬럼 없음. FK: assignment_id→work_schedules.(id) [복합 (assignment_id,factory_id)], inspector_id→users.id, asset_id→equipment_assets.id. **work_schedules.inspection_set_id → inspection_sets.id FK 보유.** writer는 신규 점검 시 schedule 참조 없으면 생성 거부, work_schedules.id를 safety_inspections.assignment_id에 저장 → schedule-backed flow에서 P-A가 canonical primary.

- **P-A (PRIMARY)**: inspection.assignment_id → work_schedules.inspection_set_id. positive: a99fdc96 → **7fee7518**.
- **P-B (CORROBORATION)**: result.inspection_set_item_id → inspection_set_items.inspection_set_id (DISTINCT). positive: distinct=1 → **7fee7518**. (P-A=P-B 수렴)

**Resolution 계약 (DECISION-3, 확정):**
- P-A 존재 → work_schedules.inspection_set_id 채택(PRIMARY).
- P-B는 corroboration. P-A 없을 때 P-B fallback 허용 조건 **전부 충족 시에만**: result rows>0 AND 모든 row set_item_id non-null AND 모든 set_item 참조 유효 AND resolved distinct set = exactly 1.
- 일부 row만 set_item_id 보유(partial coverage) → fallback 금지.
- distinct>1 또는 P-A·P-B 불일치 → MIXED_INSPECTION_SET_SOURCE. distinct=0/불가 → INSPECTION_SET_UNRESOLVED. GENERAL 자동 fallback 금지.

negative 217f0c15: assignment_id NULL(P-A 없음) AND result 5행 set_item_id 전부 NULL(P-B distinct=0) → **INSPECTION_SET_UNRESOLVED**.

## 2. SET → SCHEMA + SUPPORT GATE

set_id → runtime_inspection_bridge → runtime_form_schema_id (non-null) → runtime_form_schema.status=APPROVED_FOR_RUNTIME_USE. 7fee7518 → dc79ac3c(APPROVED). 오류: BRIDGE_NOT_FOUND / PRESENTATION_SCHEMA_NOT_MAPPED / SCHEMA_NOT_APPROVED / SCHEMA_NOT_FOUND.

**SUPPORTED PRESENTATION gate (Option B 필수):** GENERAL composer는 schema_id=dc79ac3c AND form_code=GEN-INSPECT-RESULT-001 AND version=1 만 렌더. 다른 APPROVED schema가 bridge에 연결돼도 GENERAL 5필드로 렌더하지 않음 → **UNSUPPORTED_PRESENTATION_SCHEMA**.

## 3. TOP-LEVEL FIELD SOURCE (정정)

| field | source (정정) | sample(positive) | classification |
|---|---|---|---|
| inspection_subject | **equipment_assets.asset_name** via safety_inspections.asset_id | asset_id=NULL, ws.asset_id=NULL → 값 없음 | SOURCE-BACKED(asset 있을 때) / asset 없으면 NOT_AVAILABLE. GENERAL SEALED 계약의 "asset/assignment 표시용 파생" 경계 유지, source-backed만 허용 |
| inspected_at | safety_inspections.inspection_date | 2026-05-14 00:00:00 | SOURCE-BACKED / PROVEN |
| inspection_title | inspection_sets.inspection_set_name | 소방시설공사업법 점검 | DERIVABLE / PROVEN |
| inspector_display | **safety_inspections.inspector_id → users.name ONLY** | inspector_id=NULL → **null** | DECISION-2: inspector_id만. work_schedules.inspector_name fallback **금지**(예정/스케줄 표시명이 실제 수행자라는 증거 없음). UUID 출력 금지 |

- 정정: 이전 초안의 `equipment_assets.name` → **`equipment_assets.asset_name`** (실측 컬럼: id, asset_name, asset_code). inspection_fetcher.py도 asset_name 사용.
- 정정: inspector_display에서 ws.inspector_name("심태왕") fallback **철회** → positive의 inspector_display = **null**.

## 4. RESULT ROW SOURCE (정정: item_name / raw_code)

| view_key | source | rule |
|---|---|---|
| result_id | safety_inspection_results.id | **PRIMARY identity** |
| set_item_id | safety_inspection_results.inspection_set_item_id | **SECONDARY identity** |
| item_name | (아래 계약) | result 원문 우선, silent overwrite 금지 |
| raw_code | safety_inspection_results.result_code | semantic rename만 (result_code→raw_code) |
| value_text/value_number/note/checked_at/photo_url/photo_urls | 동명 컬럼 | 직접, fabrication 금지 |

**item_name 계약 (정정, 기존 RESULT PAYLOAD CONTRACT 정합):**
```
if result.item_name IS NOT NULL:
    item_name = result.item_name
    if set_item_id resolves AND set_item.item_name != result.item_name:
        SOURCE_INTEGRITY_ERROR      # master로 조용히 덮지 않음
elif result.item_name IS NULL AND valid set_item_id resolves:
    item_name = set_item.item_name  # legacy presentation derivation
else:
    item_name = NULL
```
positive: result.item_name=NULL + valid set_item → set_item.item_name(외관 상태 점검/작동 시험/안전장치 확인). (writer가 신규 데이터에서 master명을 result.item_name에 저장하므로 정상 데이터에서는 양측 수렴.)

**raw_code**: DB 컬럼 = result_code(raw_code 아님). raw_code←result_code rename만. 값 = C-2 정본 NORMAL/ABNORMAL/HOLD. ⚠ drift 주의: inspection_fetcher.py는 ISSUE로 카운트, worker history.html은 ok/bad 이진 → 소비자 매핑 계층 존재(Composer는 source result_code 그대로 방출, 정규화는 Composer 책임 아님).

## 5. ITEM IDENTITY

inspection_set_items(id, item_seq, item_name). 7fee7518 = seq 1–16. positive 3행 = seq 1/2/3 (set_item eddb23a3/90c198f4/5afdb267).

## 6. ROW ORDER (정정: DESIGN CONTRACT, not globally PROVEN)

item_seq는 nullable·unique 제약 없음 → global invariant 아님. 정본 ordering(설계 계약):
```
ORDER BY set_item.item_seq ASC NULLS LAST,
         result.created_at ASC NULLS LAST,
         result.id ASC
```
item_name tie-break **금지**(이름 수정이 화면 순서를 바꾸면 안 됨).

## 7. NULL / MISSING POLICY (DECISION-1 확정)

REQUIRED source missing → HTTP 200 partial View Model, value=NULL, completeness=REQUIRED_SOURCE_FIELD_MISSING, fabrication 금지. passive preview/open이므로 compose 자체를 422로 막지 않음. inspection_title/inspector_display(NOT_REQUIRED) 없으면 NULL_ALLOWED.

## 8. FIELD-DEFINITION USAGE = Option B + support gate

GENERAL 5필드 code contract 고정, runtime_form_schema/runtime_field는 eligibility(status gate + support gate)·resolution만. 근거: runtime_field.source_trace가 inspection source를 바인딩하지 않음.

## 9. EXISTING FETCHER inventory

services/document_engine/fetchers/inspection_fetcher.py = **REFERENCE ONLY / DIRECT REUSE = NO**. 사유: document engine 경로(current Web View canonical architecture와 별개), set/bridge/schema 해소 없음, result_code를 ISSUE로 집계(vocab drift), 주석 "factory_id 없음"은 현재 스키마와 drift. 참고 가치: asset→equipment_assets.asset_name, inspector_id→users.name, result.item_name 원문 사용 패턴.
