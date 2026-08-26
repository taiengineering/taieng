# WP-PERSISTENCE-03 STEP-0 REV-1 — SAMPLE COMPOSE EVIDENCE

- 모드: source contract validation (수작업 compose, 코드 실행 아님). READ-ONLY. DB write = 0.
- source 없는 top-level 값은 임의 보완 없이 null/UNRESOLVED. **note 등 non-null source 손실 금지**.

## A. POSITIVE — 3f9cf36f-5bbc-4dad-9ba6-e71643020e9a

resolution: P-A assignment a99fdc96 → work_schedules.inspection_set_id **7fee7518**; P-B result 3행 distinct set=1=7fee7518 (수렴). set→bridge 3894ddb5→schema **dc79ac3c**(APPROVED, GEN-INSPECT-RESULT-001, v1 → support gate 통과).
top-level: asset_id/ws.asset_id NULL → inspection_subject 무source; inspection_date=2026-05-14; set_name=소방시설공사업법 점검; inspector_id=NULL → inspector_display=null (ws.inspector_name fallback 철회).

**SOURCE RESULT COUNT = 3 / VIEW RESULT COUNT = 3 / silent drop = 0.**

```json
{
  "inspection_id": "3f9cf36f-5bbc-4dad-9ba6-e71643020e9a",
  "inspection_set_id": "7fee7518-0e77-445c-b822-d5178d069b3c",
  "schema_id": "dc79ac3c-388c-42dc-b029-3dd9bda54a47",
  "form_code": "GEN-INSPECT-RESULT-001",
  "schema_version": 1,
  "fields": {
    "inspection_subject": null,
    "inspected_at": "2026-05-14T00:00:00",
    "inspection_title": "소방시설공사업법 점검",
    "inspector_display": null,
    "inspection_results": [
      { "result_id": "6b3ac8bb-eaad-4568-b4b9-ed2ca7103d99", "set_item_id": "eddb23a3-7c60-4c83-9832-945141d5284d", "item_name": "외관 상태 점검", "raw_code": "NORMAL", "value_text": null, "value_number": null, "note": "외관 정상", "checked_at": "2026-05-14T07:49:43.778781+00:00", "photo_url": null, "photo_urls": [] },
      { "result_id": "baf2a402-3bb8-4901-9e99-214b8b04e481", "set_item_id": "90c198f4-7290-47f1-b2b5-d7c3481cb999", "item_name": "작동 시험", "raw_code": "NORMAL", "value_text": null, "value_number": null, "note": "작동 정상", "checked_at": "2026-05-14T07:49:43.778781+00:00", "photo_url": null, "photo_urls": [] },
      { "result_id": "e707d159-c163-4e78-ab85-31101a50d3bf", "set_item_id": "5afdb267-0a37-40a2-8835-a8e3c42de287", "item_name": "안전장치 확인", "raw_code": "NORMAL", "value_text": null, "value_number": null, "note": "안전장치 정상", "checked_at": "2026-05-14T07:49:43.778781+00:00", "photo_url": null, "photo_urls": [] }
    ]
  },
  "completeness": {
    "inspection_subject": "REQUIRED_SOURCE_FIELD_MISSING",
    "inspected_at": "OK",
    "inspection_results": "OK"
  }
}
```
정정 반영:
- **note 원문 복원**: seq1 "외관 정상" / seq2 "작동 정상" / seq3 "안전장치 정상" (이전 초안 note:null → 오류였음, 수정).
- inspector_display = **null** (inspector_id NULL, ws.inspector_name fallback 철회 = DECISION-2).
- item_name = set_item 파생(result.item_name NULL). result_id primary / set_item_id secondary.
- raw_code = result_code(NORMAL) rename. value_text/value_number = null(원문). photo_urls=[] 원문.
- order = item_seq 1→2→3 (NULLS LAST → created_at → id 계약).

production 대조: 3행 값 전부 source와 일치, silent drop/merge = 0.

## B. NEGATIVE (ORPHAN) — 217f0c15-56d5-48a4-88ef-8027e0a06057

- assignment_id NULL → P-A 없음. result 5행 set_item_id 전부 NULL → P-B distinct=0 (fallback 조건 미충족). inspector_id f267a20c → users.name 김길동(해소되나 set과 무관).
- internal classification:
```json
{ "error": "INSPECTION_SET_UNRESOLVED", "inspection_id": "217f0c15-56d5-48a4-88ef-8027e0a06057",
  "detail": "assignment_id NULL (no work_schedules.inspection_set_id) AND result-derived distinct set = 0 (all inspection_set_item_id NULL). GENERAL fallback prohibited." }
```
- public non-admin endpoint: factory_id NULL·assignment_id NULL legacy row → _ensure_inspection_own에서 **404**(존재 은닉) 가능. 즉 auth 층(404)이 composer 층(INSPECTION_SET_UNRESOLVED)보다 선행. 2-layer 분리.
- GENERAL 강제 compose 금지. ✅

## C. READ-ONLY invariant

evidence 산출 전부 SELECT-only. runtime_document_data(1)/generated_document(1544)/safety_inspections/safety_inspection_results/runtime_inspection_bridge 불변. 향후 test: 호출 전후 count/hash 대조.
