# WP-PERSISTENCE-01 — GAP DECISION AID

- 작성일: 2026-08-25
- 성격: READ-ONLY. 아래는 **판단을 돕는 정리**이며, 이번 WP 에서 코드/DB 를 고치지 않는다.
- 결정권: 대표(심태왕). 각 항목은 "무엇을/왜/어디를" 만 제시.

---

## GAP-1 — 점검이 문서를 만들지 않는다 (BREAK-1)

- 현상: safety_inspection 을 저장해도 그것을 근거로 하는 runtime_document 가
  자동 생성/연결되지 않는다. source_inspection_id 를 쓰는 writer 가 0.
- 원인 위치:
  - tai-api `services/document_engine_svc.py :: create_document()` — 파라미터에
    source_inspection_id 자체가 없음.
  - 점검 저장 경로 어디에도 "점검→문서" 트리거가 없음.
- 결정 필요:
  - (a) 점검 완료 시 runtime_document 를 생성하고 source_inspection_id 로 묶는
    writer 를 신설할 것인가? (A 플로우 배선)
  - (b) 아니면 점검과 문서를 계속 분리 운영하고, 문서는 B 플로우(document-forms)로만
    작성하게 둘 것인가?
- 영향: (a) 를 택하면 create_document 계약 확장 + 점검 완료 훅 필요.
  (b) 를 택하면 "점검 결과가 자동으로 안전관리설계서/서식에 반영"되는 기능은 포기.

## GAP-2 — 생성 문서에 실제 파일 DB link 가 없다 (BREAK-2)

- 현상: generated_document 1,544건 중 파일 위치 필드가 0건. GENERATED 9건도
  storage_path/download_url NULL. 유일 파일 writer(render_pdf_gotenberg)의
  정상 성공 경로를 통과한 증거가 없음(DB link FAIL 확정 / 물리 object 존재는 NOT PROVEN).
- 원인 위치:
  - `services/document_engine_svc.py :: generate_document()` 는 PENDING 만 만들고
    끝난다(설계상 파일 생성은 별도).
  - 실제 파일 생성은 `watch_engine/document/__init__.py :: render_pdf_gotenberg()`
    에만 존재하는데, 이 함수를 PENDING 문서에 대해 호출·완주시키는 배선이
    현재 데이터에는 반영돼 있지 않음(승격 흔적 0).
- 결정 필요:
  - generate 요청 시 render_pdf_gotenberg 를 실제로 호출·완주하도록 연결할 것인가?
  - form_code 없는 runtime_document 기반 문서는 render_pdf_gotenberg 가
    처리 못 하므로(form_code 필수), 그 경로용 렌더러/템플릿 매핑을 별도로 정의할 것인가?
    (주: "runtime_document 기반" ≠ "inspection-driven". 현 표본은 source_inspection_id=NULL
     이라 점검 계보로 확정할 수 없음.)
- 영향: 이 배선 없이는 "문서 생성" 버튼이 눌려도 다운로드 가능한 실제 PDF 가
  남지 않는다(현재 상태).

## GAP-3 — 문서 값(payload) 저장이 데이터로 증명되지 않는다

- 현상: 유일 런타임 문서의 runtime_data_json={} + FIELD_EDIT 0.
- 원인 후보: 프론트 PATCH(syncRuntimeFields)는 배선돼 있으나, 이 문서에 대해
  실제 완주·성공 반영된 기록이 없음(생성만 되고 값 저장 없이 방치된 형태).
- 결정 필요: 이번 관찰은 단일 문서 표본이다. 실사용 시 syncRuntimeFields 가
  정상 반영되는지 **정상 입력 1건으로 재현 테스트**가 필요(READ-ONLY 범위 밖).
- 영향: 표본이 1건뿐이라 "기능 결함"인지 "미사용 잔여물"인지 단정 불가.

## GAP-4 — status_code 어휘 혼재 (관찰만)

- 현상: safety_inspections.status_code 에 `COMPLETED`/`completed` 혼재.
- 처리: 이번 WP 에서 **수정 금지**(지시서 STEP 7). OBSERVATION 으로만 기록.
- 참고: C-2 canonical 은 소문자 계열이 정본. 정합화가 필요하면 별도 WP 로.

---

## 우선순위 관점 (참고, 결정 아님)

- 대표의 관심("DB 저장 + 문서 저장")기준으로 보면:
  - DB 저장(점검/결과)은 이미 PASS.
  - "문서 저장"의 실질(=점검이 문서로 남고, 그 문서가 파일로 존재)은
    GAP-1(연결) → GAP-2(파일) 순으로 배선해야 완성된다.
  - GAP-1 없이 GAP-2 만 고치면 B 플로우(수동 서식) 파일만 생성되고,
    점검→문서 자동화는 여전히 비어 있다.

## 이번 WP 의 경계 (재확인)
- 위 GAP 들의 **수정/구현/배포는 이번 WP 범위가 아니다.**
- 다음 단계(구현 WP)로 넘길지, 어느 GAP 부터 닫을지는 대표 결정 사항.
