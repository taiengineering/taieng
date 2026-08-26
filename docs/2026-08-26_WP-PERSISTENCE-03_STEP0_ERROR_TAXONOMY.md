# WP-PERSISTENCE-03 STEP-0 REV-1 — COMPOSER ERROR TAXONOMY

- 모든 오류에서 DB write = 0. 자동 GENERAL fallback / 임의 선택 금지. HTTP는 후보(STEP-1 확정).
- **auth/scope는 composer 오류보다 선행**: tenant 미충족 시 composer 오류 이전에 404(존재 은닉). row existence leak 금지.

| error | condition | HTTP 후보 | persistence |
|---|---|---|---|
| INSPECTION_NOT_FOUND | safety_inspections 행 없음(또는 scope 밖 → 404로 은닉) | 404 | 0 |
| INSPECTION_SET_UNRESOLVED | P-A 없음 AND P-B fallback 조건 미충족(distinct=0 또는 partial coverage) | 422 | 0 |
| MIXED_INSPECTION_SET_SOURCE | P-B distinct>1 또는 P-A·P-B 불일치 | 409 | 0 |
| BRIDGE_NOT_FOUND | set_id bridge 행 없음 | 422 | 0 |
| PRESENTATION_SCHEMA_NOT_MAPPED | bridge.runtime_form_schema_id NULL (GENERAL fallback 금지) | 422 | 0 |
| SCHEMA_NOT_APPROVED | status ≠ APPROVED_FOR_RUNTIME_USE | 409 | 0 |
| SCHEMA_NOT_FOUND | schema 참조 행 없음 | 422 | 0 |
| UNSUPPORTED_PRESENTATION_SCHEMA | approved지만 schema_id≠dc79ac3c / form_code≠GEN-INSPECT-RESULT-001 / version≠1 | 409 | 0 |
| REQUIRED_SOURCE_FIELD_MISSING | REQUIRED 필드 source 결측 | **200 + completeness**(DECISION-1) | 0 |
| RESULT_ITEM_UNRESOLVED | result.set_item_id 있으나 inspection_set_items 참조 실패 | 409 | 0 |
| ITEM_NAME_CONFLICT (SOURCE_INTEGRITY) | result.item_name 과 set_item.item_name 둘 다 non-null·상이 | 409 | 0 |
| SOURCE_INTEGRITY_ERROR | 불변 위반(bridge set_id ↔ 해소 set_id 불일치 등) | 500 | 0 |

## 원칙
- deterministic. name inference / latest·closest schema / LLM mapping / GENERAL hard fallback 금지.
- REQUIRED 결측을 값 창작으로 메우지 않음(→200 partial).
- non-null source를 master로 silent overwrite 금지(→ITEM_NAME_CONFLICT).
- 오류 시 어떤 테이블도 write 금지(READ-ONLY invariant).

## 2-layer 분리 (negative 217f0c15)
- internal composer classification = INSPECTION_SET_UNRESOLVED.
- public non-admin endpoint (assignment_id NULL·factory_id NULL legacy row) = auth/scope상 **404**(_ensure_inspection_own 계열) 가능 → 존재 은닉이 우선.
