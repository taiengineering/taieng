# WP-PERSISTENCE-01 — FRONTEND / BACKEND WRITER TRACE

- 작성일: 2026-08-25
- 방식: GitHub 직독 (tai-admin `94a5a800`, tai-api `2b10e3a6`)
- 목적: WRITE 경로가 실제로 존재/호출되는지, source_inspection_id 를 쓰는 코드가 있는지

---

## 1. source_inspection_id 전수 검색 결과

### tai-api
`source_inspection_id` 히트 = **문서/SQL 3건뿐, .py writer 0건**
```
docs/WP-DATA-ARCH-04A_SOURCE_ANCHOR_STATIC_VERIFICATION.md   (문서)
docs/sql/20260824_inspection_document_source_anchor_up.sql   (스키마)
docs/sql/20260824_inspection_document_source_anchor_down.sql (스키마)
```
- router/service 어디에도 이 컬럼에 값을 쓰는 코드 없음.

### tai-admin
- `source_inspection_id` 히트 = **0건.**

### create_document 계약 (document_engine_svc.py 직독)
```python
def create_document(form_schema_id, factory_id, company_id, created_by):
    # runtime_data_json={} , evidence_links=[] , status='DRAFT' 로 INSERT
    # ★ source_inspection_id 파라미터 자체가 없음
```

→ **BREAK-1 확정 계열**: 스키마(컬럼+FK)는 LIVE 이나,
   점검 id 를 이 컬럼에 기록하는 writer 가 프론트·백엔드 통틀어 존재하지 않는다.
   판정: SOURCE ANCHOR WRITE = **NOT IMPLEMENTED** (writer 0 + create_document 계약에도 없음).

---

## 2. B 플로우 프론트 write 경로 (document-forms) — 실제 호출 확인

파일: `vue3/src/pages/document-forms/useDocumentFormsGenerate.ts` (직독)

```
collectFieldValues()      동적 폼의 모든 필드값 수집
ensureRuntimeDocument()   runtimeDocumentId 없으면
    → POST /document-engine/documents
      { form_schema_id, factory_id, company_id, created_by }
      ★ source_inspection_id 없음 → 점검과 무관한 standalone 문서
syncRuntimeFields()       ensureRuntimeDocument 후
    → PATCH /document-engine/documents/{docId}
      { runtime_data_json: collectFieldValues(), updated_by }
      ★ 폼값을 실제로 PATCH 로 전송 (정상 실행 시 runtime_data_json 채워짐)
postGenerate(exportType)  ensure+sync 후
    → POST /document-engine/documents/{docId}/generate
      { export_type }
```

관찰:
- 프론트에는 PATCH(syncRuntimeFields) 가 **분명히 배선되어 있다.**
- 그러나 현재 유일 런타임 문서(61055825)는 runtime_data_json={} + FIELD_EDIT 0.
  → 이 문서는 **폼 저장(PATCH)이 완주된 적 없이 CREATE+generate 만 실행된 흔적.**
  → 프론트 코드에 PATCH 가 있다는 사실과, 그 PATCH 가 이 문서에 실제로 성공 반영됐다는 것은
    별개다. 후자는 데이터로 증명되지 않음 → RUNTIME PAYLOAD SAVE = NOT PROVEN.

---

## 3. 백엔드 문서 write 경로 (document_engine_svc.py 직독)

```
create_document()   runtime_data_json={} / status=DRAFT 로 INSERT (source_inspection_id 없음)
update_document()   field_keys 검증 후 runtime_data_json 기록 + audit FIELD_EDIT
generate_document() generated_document 를 status='PENDING' 으로만 INSERT
                    · 주석: "object 미생성이므로 GENERATED 금지"
                    · storage_path/download_url/pdf_hash 기록 없음
change_status()     runtime_document_data 상태 전이(SUBMITTED/APPROVED 등)
```

- generate_document 는 **절대 GENERATED 를 만들지 않는다**(PENDING only).
- 따라서 DB 의 GENERATED 9건은 이 서비스가 만든 것이 아니다 → §4.

---

## 4. GENERATED 승격 + 파일 writer 전수 추적

검색어: `GENERATED generated_document`, `generated_document update status` (tai-api)
live 코드 후보 전량 직독 결과:

| 파일 | generated_document 를 GENERATED 로 승격? | 파일(object) 생성? |
|---|---|---|
| routers/submission_bridge.py | 아니오 (runtime_submission 만 다룸) | 아니오 |
| routers/document_engine_api.py | 아니오 (svc 위임만) | 아니오 |
| services/document_engine_svc.py | 아니오 (PENDING only) | 아니오 |
| services/document_snapshot_integrity.py | 아니오 (hash 순수함수, DB 접근 0) | 아니오 |
| services/stats_fulfillment_svc.py | 아니오 (GENERATED 카운트만, 읽기전용) | 아니오 |
| **watch_engine/document/__init__.py** | **예 (render_pdf_gotenberg)** | **예 (Gotenberg+Storage)** |

### 유일한 파일 writer: render_pdf_gotenberg() (watch_engine/document/__init__.py)
```
1) generated_document 조회 → form_code 필수 (없으면 즉시 return "no form_code")
2) document_form_master 에서 HTML 템플릿 경로
3) Gotenberg 로 HTML→PDF
4) Supabase Storage(form-outputs) 업로드
5) generated_document.update(
     status='GENERATED', storage_path=…, download_url=…, document_name=…)
   ← 승격과 파일경로가 같은 UPDATE 에서 원자적으로 기록됨
실패 시: status='FAILED'
```

교차검증 (DB_EVIDENCE §5-3 과 대조):
- 이 함수는 승격할 때 storage_path 를 **반드시 함께** 기록한다.
- DB 의 GENERATED 9건은 storage_path 전부 NULL.
- → **9건 중 어느 것도 이 함수의 정상 성공 경로를 통과한 증거가 없다**
  (NORMAL LIVE WRITER COMPLETION EVIDENCE = 0).
  - 8f533c39: runtime_document lineage 이나 parent 의 source_inspection_id=NULL →
    inspection-driven provenance NOT ESTABLISHED. form_code 없어 이 함수가 처리 불가한 형태.
  - 나머지 8건: 동일시각 cohort, form_code+flow_key 존재. 어떤 과거 writer/seed/manual
    path 가 GENERATED 를 기록했는지 현재 증거로 확정 불가 → PROVENANCE = NOT PROVEN.
- 추가로, 현재 SHA 코드 검색상 render_pdf_gotenberg 의 **live caller 는 발견되지 않고**,
  호출 흔적은 archive router 쪽에서만 검색된다(호출 배선 부재 정황).

판정: GENERATED FILE DB LINK = **FAIL (populated 0, CONFIRMED)**
      PHYSICAL OBJECT EXISTENCE = **NOT PROVEN** (Storage 직접 미확인)
      HISTORICAL GENERATED PROVENANCE = **NOT PROVEN**

---

## 5. activate_documents_for_workflow (같은 파일) — 참고

```
workflow 완료 시 workflow_document_registry 를 읽어
runtime_document_activation INSERT + (auto_generate 시) generated_document 를
status='PENDING' 으로 INSERT
```
- 이것도 PENDING 만 만든다. 승격은 별도(render_pdf_gotenberg) 호출 필요.
- 이 경로 역시 점검(safety_inspection)과 직접 연결되지 않는다(flow_key/trace 기반).
