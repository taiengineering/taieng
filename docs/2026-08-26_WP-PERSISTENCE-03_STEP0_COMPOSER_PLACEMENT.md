# WP-PERSISTENCE-03 STEP-0 REV-1 — COMPOSER PLACEMENT

- 모드: READ-ONLY repo audit. CODE = 0. tai-api HEAD `35960ecf...`. 라우터=routers/*.py, router_registry 10그룹 Safe Loading. DB=get_supabase.

## PLACEMENT MATRIX

| component | path | 책임 | read/write | reusable | composer candidate | reason |
|---|---|---|---|---|---|---|
| inspection_bridge router | routers/inspection_bridge.py | legacy set↔runtime checklist 조회 | READ | NO | NO | **무가드**(auth 없음), item source=runtime_checklist_item(legacy), presentation 경로와 별개 |
| inspection_checklist._ensure_inspection_own | routers/inspection_checklist.py | inspection→assignment(work_schedule)→company_id 소유 검증 | — | YES | YES(auth 정본) | Composer가 채택할 row ownership 가드 |
| services.company_scope | services/company_scope.py | scoped_filter / _ensure_own_company | — | YES | 참조 | 보조 스코프 |
| documents router | routers/documents.py | 문서 API (get_current_user + _ensure_own_company 단건) | R/W | 패턴 참조 | 참조 | 단건 소유검증 참조 |
| **inspection_fetcher** | services/document_engine/fetchers/inspection_fetcher.py | 문서엔진용 inspection dict 조립(asset_name/inspector/results) | READ | **REFERENCE ONLY** | **NO(direct reuse)** | document engine 경로, set/bridge/schema 해소 없음, result_code=ISSUE·factory_id 주석 drift. source read 패턴만 참고 |
| get_supabase | db/supabase_client | DB read | READ | YES | YES | 기존 read 재사용 |
| runtime_form_schema/runtime_field | 테이블 | presentation 정의 | READ | YES | YES | status gate + support gate + resolution |
| runtime_document_data/generated_document/renderer | 문서 생성 계열 | 생성 | WRITE | NO | NO | Composer READ-ONLY, 사용 금지 |
| Web View endpoint (result view) | 현재 부재(백엔드) | — | — | — | NEW(STEP-1) | worker history detail이 client-side 렌더 중; View Model 백엔드 부재 |

## 권고 (RECOMMENDED PATH — STEP-1 구현, 지금은 제안)

1. `services/inspection_view_composer.py` (READ-ONLY 순수함수): resolve_inspection_set(P-A/P-B) · resolve_presentation_schema(bridge+status+support gate) · compose_view_model(top-level 4 + results[] + completeness). 부작용 0.
2. 얇은 라우터 endpoint: **get_current_user + _ensure_inspection_own 계열 가드**(require_company_id 단독 금지). router_registry spec 등록.
3. schema = Option B(5필드 code contract 고정) + support gate(dc79ac3c/GEN-INSPECT-RESULT-001/v1).

COMPOSER PLACEMENT = service(inspection_view_composer) + ownership-guarded 라우터 endpoint, READ-ONLY. 무가드 bridge 라우터 패턴 배제. inspection_fetcher는 참고만.
