# WP-PERSISTENCE-01 — DOCUMENT PERSISTENCE AUDIT

- 작성일: 2026-08-25
- 구성: (A) READBACK 추적, (B) ID continuity chain, (C) 저장 단계별 판정

---

## A. READBACK TRACE (WRITE → READ API → FRONTEND RENDER)

| 데이터 | WRITE | READ API | FRONTEND | READBACK |
|---|---|---|---|---|
| safety_inspection_results | 점검 저장 경로 (8 rows 실측) | 조회 경로 존재 | 목록 렌더 | 저장·조회 성립 (PASS) |
| runtime_data_json | PATCH /document-engine/documents/{id} (프론트 배선 O) | GET /document-engine/documents/{id} | document-forms 렌더 | WRITE 배선은 있으나 현 row `{}` → 값 왕복 **NOT PROVEN** |
| generated_document(메타) | generate_document → PENDING INSERT | GET …/generated | 목록 | 메타 왕복 성립 (PASS) |
| generated_document(파일) | render_pdf_gotenberg (유일) | download_url | iframe/새탭 | storage/url NULL → 파일 왕복 **FAIL(DB LINK) / NOT PROVEN(object)** |

요약:
- 점검 결과는 WRITE→READ 왕복이 성립한다.
- 문서 **값(runtime_data_json)** 왕복은 현재 데이터로 증명되지 않는다(빈 payload).
- 문서 **파일** 왕복은 DB 링크가 비어 있어 성립하지 않는다.

---

## B. ID CONTINUITY CHAIN

각 edge 를 CONFIRMED FK / APPLICATION LINK / OPTIONAL / MISSING 으로 표시.

```
work_schedule
   │  edge: (assignment_id, factory_id) → work_schedules_p00..p15
   │  = CONFIRMED FK   (safety_inspections → work_schedules 파티션 FK 실측)
   ▼
work_assignment / schedule
   │  edge: safety_inspections.assignment_id → work_schedules
   │  = CONFIRMED FK (nullable) — 단 데이터상 한 행은 assignment_id NULL (OPTIONAL 실사용)
   ▼
safety_inspection
   │  edge: safety_inspection_results.inspection_id → safety_inspections
   │  = CONFIRMED FK   (결과 8행이 점검에 묶임)
   │
   │  edge: runtime_document_data.source_inspection_id → safety_inspections
   │  = SCHEMA FK 존재하나 값 미기록 → **MISSING (application link 없음)**  ★BREAK-1
   ▼
runtime_document
   │  edge: generated_document.runtime_document_id → runtime_document_data
   │  = CONFIRMED FK (nullable) — 1,544건 중 2건만 채워짐 → 대부분 OPTIONAL/미연결
   ▼
generated_document
   │  edge: generated_document → 실제 파일 object
   │  = storage_path/download_url NULL → **DB LINK MISSING (CONFIRMED)**  ★BREAK-2
   │    (물리 object 존재는 직접 미확인 → NOT PROVEN)
   ▼
(실제 제출 가능한 문서 파일)  = DB 상 도달 경로 없음 (물리 존재 NOT PROVEN)
```

체인 판정:
- work_schedule ↔ safety_inspection: **연결됨 (FK).**
- safety_inspection → runtime_document: **끊김 (BREAK-1, source anchor 미기록).**
- runtime_document → 파일: **끊김 (BREAK-2, DB link 부재 CONFIRMED / 물리 object NOT PROVEN).**
- 따라서 "점검에서 출발해 제출 문서 파일까지" 도달하는 연속 체인은 **성립하지 않는다.**

IDENTITY CONTINUITY = **PARTIAL**
(legacy standalone 행과 linked 행이 혼재하고, 핵심 두 edge 가 MISSING)

---

## C. 저장 단계별 판정 (최종)

```
INSPECTION DB SAVE            = PASS         (safety_inspections 실측)
INSPECTION RESULT SAVE        = PASS         (safety_inspection_results 8 rows)
IDENTITY CONTINUITY           = PARTIAL      (legacy/linked 혼재 + 2 edge MISSING)

SOURCE ANCHOR SCHEMA          = PASS         (컬럼+FK LIVE)
SOURCE ANCHOR WRITE           = NOT IMPLEMENTED
                                (writer 0 + create_document 계약에 param 없음 — 확인 완료)

RUNTIME DOCUMENT CREATE       = PASS         (create_document, 1 row)
RUNTIME PAYLOAD SAVE          = NOT PROVEN   (현 row runtime_data_json={}, FIELD_EDIT 0;
                                              프론트 PATCH 배선은 존재)

GENERATED METADATA SAVE       = PASS         (generate_document → PENDING 메타 row)
GENERATED FILE DB LINK        = FAIL         (storage/download/hash/snapshot populated 0)
ACTUAL FILE OBJECT EXISTENCE  = NOT PROVEN   (유일 writer render_pdf_gotenberg 미통과;
                                              GENERATED 9건 storage 전부 NULL)

READBACK                      = PARTIAL      (결과 PASS / 문서값·파일 미성립)
END-TO-END PERSISTENCE        = FAIL / NOT WIRED
```

---

## D. NOT PROVEN 을 FAIL 로 올리지 않은 이유 (증거 규율)

- RUNTIME PAYLOAD SAVE: 현재 단일 문서가 비어 있고 FIELD_EDIT 가 0이라는 것은
  "이 문서에 대해 의미있는 저장이 일어나지 않았다"는 강한 정황이나, _audit 가
  예외를 삼키는 구조이고 프론트 PATCH 배선은 실재하므로 "기능 자체가 저장 불가"로
  단정하지 않는다. → NOT PROVEN.
- ACTUAL FILE OBJECT EXISTENCE: DB 링크 부재(FAIL)는 확정이나, Storage 버킷을
  직접 열람하지 않았으므로 "파일이 물리적으로 0"이라고까지 단정하지 않는다.
  다만 유일 writer 미통과 + 링크 전무로, 실재 가능성은 매우 낮다. → NOT PROVEN.
