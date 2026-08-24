# WP-PERSISTENCE-01 — FINAL VERDICT

- 작성일: 2026-08-25
- 모드: READ-ONLY ANALYSIS 완료. mutation 0. repo commit 0 (승인 대기).
- SoT: tai-admin `94a5a800` / tai-api `2b10e3a6` / DB `vwlahtguyggrhvslabax`

---

## 1. 한 문장 결론

점검의 DB 저장은 정상(PASS)이나, **점검이 문서로 이어져 파일로 남는 끝단**은
두 지점에서 끊겨 있어 END-TO-END PERSISTENCE = **FAIL / NOT WIRED** 이다.

---

## 2. 최종 판정표

```
INSPECTION DB SAVE            = PASS
INSPECTION RESULT SAVE        = PASS
IDENTITY CONTINUITY           = PARTIAL
SOURCE ANCHOR SCHEMA          = PASS
SOURCE ANCHOR WRITE           = NOT IMPLEMENTED
RUNTIME DOCUMENT CREATE       = PASS
RUNTIME PAYLOAD SAVE          = NOT PROVEN
GENERATED METADATA SAVE       = PASS
GENERATED FILE DB LINK        = FAIL
ACTUAL FILE OBJECT EXISTENCE  = NOT PROVEN
READBACK                      = PARTIAL
END-TO-END PERSISTENCE        = FAIL / NOT WIRED

BREAK-1 = SCHEMA ONLY / WRITER NOT FOUND
BREAK-2 = GENERATED FILE DB LINK MISSING
          PHYSICAL OBJECT EXISTENCE       = NOT PROVEN
          HISTORICAL GENERATED PROVENANCE = NOT PROVEN
```

---

## 3. 10개 질문 답변

**Q1. 사용자가 입력한 점검 결과는 DB에 저장되는가?**
→ 예. safety_inspections + safety_inspection_results(8행) 실측. PASS.

**Q2. 그 점검 결과가 문서(runtime_document)로 연결되는가?**
→ 아니오. source_inspection_id 를 쓰는 writer 가 0. 스키마만 있고 연결 안 됨. (BREAK-1)

**Q3. runtime_document 는 생성되는가?**
→ 예. create_document 로 DRAFT 생성됨(1행). 단 점검과 무관한 B 플로우 산물.

**Q4. runtime_document 에 실제 값(payload)이 저장되는가?**
→ NOT PROVEN. 현 유일 문서 runtime_data_json={}, audit FIELD_EDIT 0.
   프론트 PATCH 배선은 존재하나 이 문서엔 반영 흔적 없음.

**Q5. generated_document 는 만들어지는가?**
→ 메타행은 예(PENDING). 그러나 이는 "파일이 생겼다"가 아니라 "생성 요청 큐"에 가깝다.

**Q6. 실제 출력 파일(PDF object)은 존재하는가?**
→ 파일을 가리키는 **DB link 는 없다(FAIL, CONFIRMED)**: 1,544건 전체
   storage_path/download_url/pdf_hash/snapshot = 0, GENERATED 9건도 전부 NULL.
   정상 live writer 경로 통과 증거도 0. 단 Storage object 물리 존재는 직접
   확인하지 않았으므로 **PHYSICAL OBJECT EXISTENCE = NOT PROVEN.**

**Q7. GENERATED 9건은 어떻게 생겼나? (누가 승격했나)**
→ 현재 확인된 정상 live writer(render_pdf_gotenberg) 경로로 생성된 데이터는 아니다
   (그 함수는 승격 시 storage_path 를 반드시 함께 기록하는데 9건 전부 NULL).
   - 1건(8f533c39): runtime_document lineage 이나 parent 의 source_inspection_id=NULL →
     inspection-driven provenance NOT ESTABLISHED. form_code 없어 이 함수가 처리 불가한 형태.
   - 8건: 동일시각(2026-05-16 06:27:08) cohort, form_code+flow_key 존재.
   → 어떤 과거 writer / seed / manual path 가 status='GENERATED' 를 기록했는지는
     현재 증거로 확정할 수 없다. **HISTORICAL GENERATED PROVENANCE = NOT PROVEN.**

**Q8. 점검→문서→파일의 ID 연속성은 이어지는가?**
→ 아니오. work_schedule↔inspection 은 FK 로 연결되나,
   inspection→runtime_document(BREAK-1)와 runtime_document→파일(BREAK-2)이 끊김.

**Q9. 재조회(READBACK) 시 값이 되살아나는가?**
→ 점검 결과는 예(PASS). 문서 값/파일은 아니오(payload NOT PROVEN, 파일 FAIL).

**Q10. status_code 어휘 문제는?**
→ safety_inspections 에 COMPLETED/completed 혼재. OBSERVATION 으로만 기록.
   이번 WP 수정 금지(STEP 7). 필요 시 별도 정합화 WP.

---

## 4. 두 단절점 최종 정리

### BREAK-1 — 점검 → 문서 앵커 미기록
- 위치: create_document 계약에 source_inspection_id 없음 + 점검 완료 훅 없음.
- 상태: SCHEMA ONLY / WRITER NOT FOUND (writer 0 + API 계약 부재 확인 완료).

### BREAK-2 — 문서 → 실제 파일 (GENERATED FILE DB LINK MISSING)
- 위치: generate_document 는 PENDING 만 생성. 실제 파일 writer 는
  render_pdf_gotenberg 하나뿐인데, 이를 호출·완주한 흔적이 데이터에 없음.
- 현재 확인된 live PDF writer = render_pdf_gotenberg()
  정상 성공 경로 = PDF 생성 → Storage upload → GENERATED → storage_path/download_url 기록
- production evidence = GENERATED rows 존재하나 storage_path/download_url = NULL
- 판정:
  - NORMAL LIVE WRITER COMPLETION EVIDENCE = 0
  - GENERATED FILE DB LINK = FAIL (CONFIRMED)
  - PHYSICAL OBJECT EXISTENCE = NOT PROVEN
  - HISTORICAL GENERATED PROVENANCE = NOT PROVEN
- 참고: 현재 SHA 검색상 render_pdf_gotenberg 의 live caller 미발견(호출 흔적은 archive router).

---

## 5. 범위·규율 준수 확인

- MODE: READ-ONLY. Production SQL 은 SELECT-only 만 사용.
- Mutation: CODE 0 / DB 0 / API 0 / REPO 0 / DEPLOY 0.
- No synthetic data, no schema change, no backfill, no writer 구현.
- 모든 "정상/확정" 판정은 코드 직독 + DB 실측 교차 후에만 내렸다.
- NOT PROVEN 2건(payload / file object)은 성급히 FAIL 로 올리지 않았다(증거 규율).
- status_code 혼재는 관찰만, 수정하지 않았다.

## 6. 다음 단계 (결정 대기)
- 본 분석은 여기서 STOP. repo commit 하지 않음(승인 게이트).
- 구현 여부/순서(GAP-1 연결 → GAP-2 파일)는 GAP_DECISION 참조하여 대표 결정.
