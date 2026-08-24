# WP-PERSISTENCE-01 — PIPELINE MAP

- 작성일: 2026-08-25
- 모드: READ-ONLY ANALYSIS (mutation 0 / SELECT-only / 코드 직독)
- SoT 앵커: tai-admin main `94a5a800`, tai-api main `2b10e3a6`
- 대상: 사용자 점검결과 입력이 UI→API→DB→문서→재조회까지 실제로 영속되는가

---

## 0. 핵심 결론 (요약)

점검 자체의 DB 저장은 된다. 그러나 "점검 결과가 문서로 영속화되는" 파이프라인은
**끝까지 연결되어 있지 않다(NOT WIRED).** 두 개의 독립된 단절점이 있다.

```
BREAK-1  safety_inspection.id → runtime_document_data.source_inspection_id
         = SCHEMA ONLY / WRITER NOT FOUND
         (컬럼·FK는 LIVE, 그러나 이 값을 쓰는 코드가 tai-api/tai-admin 어디에도 없음)

BREAK-2  generated_document → 실제 생성 파일(object) 영속
         = GENERATED FILE DB LINK MISSING
         · GENERATED FILE DB LINK        = FAIL      (storage/download/hash/snapshot 0, CONFIRMED)
         · NORMAL LIVE WRITER COMPLETION = 0         (render_pdf_gotenberg 정상경로 통과 증거 없음)
         · PHYSICAL OBJECT EXISTENCE     = NOT PROVEN (Storage 직접 미확인)
         · HISTORICAL GENERATED PROVENANCE = NOT PROVEN (9건이 어떤 경로로 GENERATED 됐는지 확정 불가)
```

---

## 1. 두 개의 플로우는 서로 다르다 (절대 혼동 금지)

이 시스템에는 이름이 비슷하지만 **계보가 완전히 분리된** 두 문서 경로가 있다.
"문서 엔진이 존재한다"는 사실이 "점검이 문서로 저장된다"를 의미하지 않는다.

### A 플로우 — INSPECTION-DRIVEN DOCUMENT (점검 → 문서)
```
work_schedule
  → safety_inspection (점검 실측 저장)         [PASS]
  → safety_inspection_results (항목별 결과)     [PASS]
  → runtime_document_data (점검 근거 문서)      [★BREAK-1: 연결 writer 없음]
      · source_inspection_id 로 점검과 묶여야 함
      · 실제로는 이 값을 채우는 코드가 0
  → generated_document (출력물)                 [★BREAK-2: FILE DB LINK MISSING]
```
이 경로를 **끝까지 실행하는 writer가 존재하지 않는다.** 점검을 저장해도
그 점검을 근거로 하는 runtime_document 를 자동 생성/연결하는 코드가 없다.

### B 플로우 — STANDALONE DOCUMENT FORMS (서식 직접 작성)
```
document-forms 화면 (사용자가 서식 선택 후 직접 입력)
  → POST /document-engine/documents  (ensureRuntimeDocument)
      · form_schema_id / factory_id / company_id / created_by
      · source_inspection_id 없음 (점검과 무관)
  → PATCH /document-engine/documents/{id}  (syncRuntimeFields)
      · runtime_data_json = 폼 입력값
  → POST /document-engine/documents/{id}/generate
      · generated_document 를 status=PENDING 으로만 INSERT
        (이 함수에는 PDF object 생성 / Storage 업로드 로직 없음)
```
B 플로우는 **점검과 무관한 독립 문서 작성**이다. 정상 동작해도 A 플로우(점검→문서)를
대체하지 못한다.

---

## 2. 파이프라인 노드별 상태

| 노드 | 테이블/엔드포인트 | writer(코드) | 상태 |
|---|---|---|---|
| 점검 저장 | safety_inspections | (점검 저장 경로) | PASS (2 rows 실측) |
| 결과 저장 | safety_inspection_results | (점검 저장 경로) | PASS (8 rows 실측) |
| 점검→문서 연결 | runtime_document_data.source_inspection_id | **없음** | **BREAK-1 (writer 0)** |
| 문서 생성(초안) | runtime_document_data | document_engine_svc.create_document | PASS (1 row) |
| 문서 값 저장 | runtime_document_data.runtime_data_json | document_engine_svc.update_document (PATCH) | NOT PROVEN (현 row `{}`) |
| 출력물 메타 | generated_document (PENDING) | document_engine_svc.generate_document | PASS (메타 row) |
| 출력물 승격+파일 | generated_document (GENERATED)+storage | watch_engine/document render_pdf_gotenberg | **BREAK-2 (DB link 0 / object NOT PROVEN)** |

---

## 3. 유일한 파일 생성 지점 (그리고 그것을 거치지 않은 데이터)

실제 PDF 파일을 만들어 Supabase Storage 에 올리고 generated_document 를
`GENERATED` + storage_path + download_url 로 **원자적으로** 승격하는 코드는
**단 하나** 뿐이다:

```
watch_engine/document/__init__.py :: render_pdf_gotenberg()
  1) Gotenberg 로 HTML→PDF 변환
  2) Supabase Storage(form-outputs) 업로드
  3) generated_document.update(status=GENERATED, storage_path=…, download_url=…)
     ← 승격과 파일경로 기록이 같은 UPDATE 문에서 함께 일어난다
```

그런데 DB 의 GENERATED 9건은 **storage_path 가 전부 NULL** 이다.
render_pdf_gotenberg 는 승격 시 storage_path 를 반드시 함께 기록하므로,
**GENERATED 9건 중 어느 것도 이 함수의 정상 성공 경로를 통과한 증거가 없다**
(NORMAL LIVE WRITER COMPLETION EVIDENCE = 0). 또한 현재 SHA 검색상 이 함수의
live caller 는 발견되지 않는다(호출 흔적은 archive router 쪽만).
9건이 어떤 과거 writer/seed/manual path 로 GENERATED 가 됐는지는 확정 불가(PROVENANCE = NOT PROVEN).
파일 DB link 부재는 CONFIRMED 이나, Storage object 물리 존재는 직접 확인하지 않았으므로 NOT PROVEN.
(상세 근거는 DB_EVIDENCE / DOCUMENT_PERSISTENCE_AUDIT 참조)

---

## 4. 한 줄 요약

- 점검 DB 저장: 된다.
- 점검이 "문서로" 저장·출력: **파이프라인이 연결되어 있지 않다.**
- 문서 엔진(B 플로우)은 존재하나 점검(A 플로우)과 이어져 있지 않고,
  실제 파일 생성도 현재 데이터에서 증명되지 않는다.
