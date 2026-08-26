# WP-PERSISTENCE-03 STEP-0 REV-1 — AUTH & API INTEGRATION

- 모드: READ-ONLY audit. CODE = 0. HEAD: tai-api `35960ecf...`, tai-admin `94a5a800...`.

## 1. AUTH (정정 — require_company_id alone = NOT SUFFICIENT)

- `require_company_id`는 비-ALL 사용자의 company_id 존재만 요구 → 스코프 강제 아님. row-level 상세 접근에는 별도 검사 필요.
- documents.py 단건도 실제로는 get_current_user + `_ensure_own_company` 별도 사용.
- **기존 inspection 정본 가드 = `inspection_checklist.py`의 `_ensure_inspection_own()`**: inspection → assignment(work_schedule) → company_id 로 소유 검증.
- 보조: `services.company_scope`의 `scoped_filter` / `_ensure_own_company`.

**AUTH pipeline (정본):**
```
get_current_user
→ inspection row ownership/scope guard (inspection_checklist._ensure_inspection_own 패턴; scoped_filter/_ensure_own_company 비교하여 STEP-1 채택 가드 명시)
→ composer
```
- tenant 확인 **전** composer 오류 반환 금지(row existence leak 방지).
- UUID만 받는 무가드 raw endpoint 금지. legacy inspection_bridge.py(무가드) 모델 배제.

AUTH REUSE DECISION = **get_current_user + inspection row ownership guard (_ensure_inspection_own 계열)**. require_company_id 단독 = 불충분.

## 2. Tenancy 해소 근거

safety_inspections.factory_id, inspection_sets.company_id/factory_id (positive: aaaaaaaa-0003 / bbbbbbbb-0003), assignment→work_schedule→company_id 경로(_ensure_inspection_own).

## 3. negative 217f0c15 — 2-layer

internal = INSPECTION_SET_UNRESOLVED. public non-admin: assignment_id NULL·factory_id NULL legacy → _ensure_inspection_own에서 **404**(존재 은닉) 가능. auth 층이 composer 층보다 선행.

## 4. API PLACEMENT

권고: 신규 read endpoint (예시) `GET /inspections/{inspection_id}/view` — get_current_user + inspection ownership guard, View Model 반환. 기존 inspection 응답 계약 미오염, backward compat 우위. (무조건 신설 아님; 기존 확장 대비 계약 청결로 (B) 우위.)

## 5. Query shape (N+1 회피, 참고)

safety_inspections → work_schedules(assignment→set_id) → runtime_inspection_bridge(set→schema) → runtime_form_schema(status/version/support gate) → safety_inspection_results + inspection_set_items(join) → (asset_id 있으면) equipment_assets.asset_name → (inspector_id 있으면) users.name → inspection_sets.inspection_set_name. 대략 6–8 read, 결과·항목 IN 조인 배치. source 복제/denormalized snapshot/cache 금지(범위 밖).

## 6. FRONTEND (audit 완료 — §26 충족)

**result Web View canonical consumer = worker app `vue3/public/app/history.html`**:
- 목록 API: `GET {https://api.taieng.co.kr}/worker-check/history?worker_id=&phone=&page=&size=` (Bearer token).
- 현재 data shape: items[{id, submitted_at|created_at, asset_name|factory_name, type, items:[{name|label, result:'ok'|'bad'}]}].
- detail: 탭 시 bottom sheet가 client-side로 items 렌더(✅/❌ = ok/bad). "PDF 내보내기" = WIP placeholder(hist_pdf_wip) → 향후 PDF.
- **composer integration point**: 결과 상세/PDF가 소비할 View Model을 백엔드에서 제공 → history detail sheet + future PDF가 GEN-INSPECT-RESULT-001 View Model 소비. 현재 client-side items 렌더를 View Model 기반으로 대체/보강.
- **data shape 격차**: 현재 result='ok'/'bad'(이진) vs View Model raw_code=NORMAL/ABNORMAL/HOLD(3진, HOLD 처리 필요); item {name} vs {item_name, raw_code, note, checked_at, photo_urls}. 매핑은 소비자 계층.

기타:
- admin `vue3/src/pages/my-inspection/*` = 일정/세트 **관리** 페이지(GET /inspection/status·/inspection/schedules·/inspection-sets, POST /inspection/start·/complete). **결과 뷰 소비자 아님**.
- worker `inspect.html` = 결과 **기록**(write) 경로. 뷰 소비자 아님.

FRONTEND 수정 = 0 (조사만).
