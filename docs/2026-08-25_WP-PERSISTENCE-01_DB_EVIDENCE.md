# WP-PERSISTENCE-01 — DB EVIDENCE

- 작성일: 2026-08-25
- DB: Supabase `vwlahtguyggrhvslabax` (Seoul)
- 방식: SELECT-only 실측. mutation 0. 모든 수치는 조회 시점(2026-08-24~25) 실값.

---

## 1. safety_inspections (점검 원장) — 2 rows

| id | assignment_id | inspector_id | status_code | submitted_by | factory_id |
|---|---|---|---|---|---|
| 217f0c15… | NULL | f267a20c | **COMPLETED** (대문자) | NULL | NULL |
| 3f9cf36f… | a99fdc96… | NULL | **completed** (소문자) | NULL | factory 0003 |

- OBSERVATION: status_code 에 `COMPLETED`/`completed` 혼재. linkage(assignment/factory)도 행마다 다름.
- 이 관찰은 기록만 한다. 이번 WP 에서 수정하지 않는다(지시서 STEP 7).

## 2. safety_inspection_results (항목별 결과) — 8 rows
- 8행 실측. 점검 결과 자체의 저장은 이루어진다. → INSPECTION RESULT SAVE = PASS.

## 3. defects — 0 rows
- 결함 테이블은 비어있음(현 데이터 기준).

---

## 4. runtime_document_data (런타임 문서) — 1 row

현재 유일한 런타임 문서:
```
id                 = 61055825-29a5-440a-a16d-44d74cbe6efa
status             = DRAFT
version            = 1
source_inspection_id = NULL          ← 점검과 연결 안 됨 (BREAK-1)
runtime_data_json  = {}              ← 빈 객체 (0 keys)
created_by         = e6d6da1b
updated_by         = NULL            ← PATCH 로 갱신된 흔적 없음
factory / company  = 0003 / aaaa…0003
```

- source_inspection_id = NULL → 점검 근거 연결 없음.
- runtime_data_json = {} + updated_by = NULL → **의미있는 payload 저장 흔적 없음.**
  (단, PATCH 실행 여부는 audit 로 교차확인 → §6)

---

## 5. generated_document — 총 1,544 rows

### 5-1. status 분포
```
PENDING          1,527
GENERATED            9
FAILED               4
TEMPLATE_MISSING     4
```

### 5-2. 파일 필드 채움 (전체 1,544건 대상)
```
storage_path  populated = 0
download_url  populated = 0
pdf_hash      populated = 0
snapshot_id   populated = 0
```
→ **1,544건 전체에서 실제 파일 위치를 가리키는 필드가 하나도 채워져 있지 않다.**
   GENERATED 9건도 예외 없이 전부 NULL.

### 5-3. GENERATED 9건 정밀 분해 (핵심 증거)

| id | form_code | runtime_doc | flow_key | storage | url | created_at |
|---|---|---|---|---|---|---|
| 8f533c39 | NULL | **YES** | NO | NO | NO | 2026-05-14 08:10:06 |
| 2d308882 | STD-RISK-001 | NO | YES | NO | NO | 2026-05-16 06:27:08 |
| 39586092 | STD-INSPECT-001 | NO | YES | NO | NO | 2026-05-16 06:27:08 |
| 5b43a637 | BW-HIGH-001 | NO | YES | NO | NO | 2026-05-16 06:27:08 |
| cf4b49b8 | STD-RISK-001 | NO | YES | NO | NO | 2026-05-16 06:27:08 |
| 31f2102d | STD-INSPECT-001 | NO | YES | NO | NO | 2026-05-16 06:27:08 |
| 7a1212dc | BW-HIGH-001 | NO | YES | NO | NO | 2026-05-16 06:27:08 |
| fd35d13e | STD-RISK-001 | NO | YES | NO | NO | 2026-05-16 06:27:08 |
| be773765 | STD-INSPECT-001 | NO | YES | NO | NO | 2026-05-16 06:27:08 |

판독:
- **8f533c39 (1건)**:
  = runtime_document lineage (runtime_document_id 있음)
  = form_code NULL
  = 그 parent runtime_document_data 의 source_inspection_id = NULL
  → **inspection-driven provenance NOT ESTABLISHED.**
    runtime_document 기반이라는 것과 "점검에서 비롯됐다(A 플로우)"는 별개다.
    이 행을 inspection-driven 으로 분류할 근거는 없다.
  render_pdf_gotenberg 는 form_code 필수라 이 행을 처리할 수 없음. 그런데 status=GENERATED
  → 현재 확인된 정상 live writer 경로로 승격된 데이터는 아니다.
- **나머지 8건**:
  = 동일 시각(2026-05-16 06:27:08) cohort
  = form_code + flow_key 존재
  = status GENERATED / storage_path·download_url NULL
  → 현재 확인된 live PDF writer(render_pdf_gotenberg) 정상 경로로 생성된 데이터는 아니다.
    (그 함수는 승격 시 storage_path 를 반드시 함께 기록하는데 전부 NULL)
  → 어떤 과거 writer / seed / manual path 가 status='GENERATED' 를 기록했는지는
    현재 증거로 확정할 수 없다. **PROVENANCE = NOT PROVEN.**

결론:
- GENERATED 9건 전부 **실제 파일을 가리키는 DB link 가 없다(DB LINK MISSING = CONFIRMED).**
- 정상 live writer 경로를 통과한 증거도 없다(NORMAL LIVE WRITER COMPLETION EVIDENCE = 0).
- Storage object 의 물리적 존재 여부는 직접 확인하지 않았으므로 **PHYSICAL OBJECT EXISTENCE = NOT PROVEN.**

---

## 6. runtime_lifecycle_audit_log (문서 61055825 이력) — 3 rows

```
CREATED  actor e6d6da1b  2026-05-14 08:09:14   (문서 생성)
CREATED  actor NULL      2026-05-14 08:10:06   (generate → PENDING 삽입 시각과 일치)
CREATED  actor NULL      2026-08-23 01:03:57   (또 다른 generate)
```

- **FIELD_EDIT 액션 = 0건.** update_document(PATCH)는 FIELD_EDIT 를 남기는데 하나도 없음.
- → runtime_data_json 을 채우는 PATCH 가 실행된 흔적 없음(강한 정황).
- 단, _audit 는 try/except 로 실패를 삼키는 구조이므로 "PATCH 100% 없음"으로 단정하지 않음.
  → RUNTIME PAYLOAD SAVE = **NOT PROVEN** (empty row + FIELD_EDIT 0 = 강한 근거, 확정 아님).

---

## 7. generated_document rows for 문서 61055825 — 2 rows
```
8f533c39  status=GENERATED  export=PDF   (파일필드 전부 NULL)  2026-05-14 08:10:06
327ae577  status=PENDING    export=HTML  (파일필드 전부 NULL)  2026-08-23 01:03:57
```
- 두 생성 시각이 audit 의 두 CREATED(actor NULL)와 정확히 일치 → 이 문서의 generate 는 2회.
- 두 건 모두 **실제 파일을 가리키는 DB link 가 없다.** 정상 live writer 경로 통과 증거도 없다.
  Storage object 물리 존재는 직접 확인하지 않음 → PHYSICAL OBJECT EXISTENCE = NOT PROVEN.

---

## 8. FK 지도 (pg_constraint 실측)

- child → safety_inspections:
  `defects.inspection_id`, `runtime_document_data.source_inspection_id`,
  `safety_inspection_results.inspection_id`
- safety_inspections →:
  `asset_id→equipment_assets`, `(assignment_id,factory_id)→work_schedules_p00..p15`,
  `inspector_id/submitted_by→users`

→ **runtime_document_data.source_inspection_id 는 FK 로 존재(SCHEMA PASS)**.
  문제는 이 값을 채우는 application writer 가 없다는 것(BREAK-1).
