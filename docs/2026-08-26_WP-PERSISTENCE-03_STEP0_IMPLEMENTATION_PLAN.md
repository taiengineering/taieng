# WP-PERSISTENCE-03 STEP-0 REV-1 — IMPLEMENTATION PLAN (계획만, 코드 0)

## GPT 확정 정책 (반영됨)
- DECISION-1: REQUIRED source missing → 200 partial + value null + completeness=REQUIRED_SOURCE_FIELD_MISSING, fabrication 금지.
- DECISION-2: inspector_display = safety_inspections.inspector_id→users.name ONLY; 없으면 null; ws.inspector_name fallback 금지.
- DECISION-3: P-A(assignment→ws.inspection_set_id) PRIMARY; P-B(result→set_item→set) CORROBORATION; P-A 없을 때 P-B fallback은 [rows>0 AND 전 row set_item_id non-null AND 전 참조 유효 AND distinct=1]일 때만. partial coverage 금지.
- Support gate: schema_id=dc79ac3c / form_code=GEN-INSPECT-RESULT-001 / version=1 외 approved schema → UNSUPPORTED_PRESENTATION_SCHEMA.
- item_name: result 원문 우선; null+set_item→set_item 파생; 양측 non-null mismatch→SOURCE_INTEGRITY_ERROR(silent overwrite 금지).
- ROW ORDER: item_seq ASC NULLS LAST → created_at ASC NULLS LAST → id ASC (item_name tie-break 금지).
- AUTH: get_current_user + inspection ownership guard(_ensure_inspection_own 계열); require_company_id 단독 불충분.

## STEP-1 (구현 계약) 예정 범위
1. services/inspection_view_composer.py (READ-ONLY): resolve_inspection_set / resolve_presentation_schema(+support gate) / compose_view_model(+completeness). 부작용 0.
2. 얇은 라우터 endpoint (예시 GET /inspections/{id}/view), get_current_user + ownership guard, router_registry 등록.
3. 소비자 통합: worker history.html detail sheet + future PDF가 View Model 소비(현재 client-side items 렌더 대체/보강); result vocab ok/bad ↔ NORMAL/ABNORMAL/HOLD 매핑(HOLD 포함) 계약.
4. 테스트: positive(3f9cf36f)=성공 View Model(note 3건 보존), negative(217f0c15)=INSPECTION_SET_UNRESOLVED + public 404 2-layer, 각 오류 케이스, before/after count/hash 불변.

## 비범위 (WP 전체)
renderer/HTML→PDF/storage/download/completion hook/payload writer/source anchor writer, runtime_document_data·generated_document write, 추가 bridge mapping(323 EXCEPTION/SOURCE_MISMATCH), schema 수정, frontend 코드 수정.
