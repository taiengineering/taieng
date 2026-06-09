# 세션 작업 내역 — 의무 출력 버그 + 입구 sector 필터 + 검증 하니스

- 날짜: 2026-06-09
- 작업 주체: Claude(기획창) — 직접 수정 + 검증
- 범위: 법령진단 결과 출력 정상화, sector 누수 차단, 검증 하니스 정비, 결과페이지 UX

---

## 1. 한 줄 요약

제조업(화학공장) 검증 진단에서 (a) 의무 유형이 전부 ACTION으로 뭉치고, (b) 의무 제목에 코드 토큰이 그대로 노출되며, (c) 제조업과 무관한 타 sector 법령(의료법·특수교육법·주택법 등)이 섞여 나오던 3대 문제를 해결했다. 추가로 검증 하니스 목록 정비, 결과페이지 로딩 스피너를 적용했다.

---

## 2. 해결한 이슈

### 이슈 A — obligation_type 전부 ACTION 오분류 (해결)
- 증상: 선임·점검·신고·보고 의무가 전부 "조치(ACTION)" 블록에 묶임.
- 원인: `_task_to_rule_row` / `_applicability_to_rule_row`에서
  `obl_type = task_type if task_type in ("APPOINT","INSPECT",...) else "ACTION"`.
  실제 들어오는 값은 `APPOINTMENT_TASK_CANDIDATE` 등이라 화이트리스트에 없어 전부 ACTION으로 강등.
- 수정: 이미 정확히 계산되는 `_bucket_for_task_type` 결과(bucket)에서
  `_BUCKET_TO_OBLIGATION`으로 obligation_type을 직접 도출(재판정·추측 없음).
- 검증: 선임 35 / 점검 11 / 신고 66 / 조치 142로 정상 분산 확인.

### 이슈 B — obligation_summary 코드 토큰 노출 (해결)
- 증상: 의무 제목에 `"APPOINTMENT_TASK_CANDIDATE: APPOINT_FAMILY"` 같은 내부 토큰 노출.
- 원인: `title = f"{task_type}: {source_fam}"`를 그대로 obligation_summary로 사용.
- 수정: `_obligation_summary_text()` 추가 — 법조문 제목(description) 우선,
  토큰이면 "법령명 조문" → fallback 순. 토큰 판별 `_is_token_text()`(TASK_CANDIDATE/_FAMILY).
  원본 토큰은 `then_action_token` 필드에 별도 보관(증적 보존).

### 이슈 C — description 토큰 오염 (해결)
- 증상: 자연어 설명까지 토큰으로 덮임.
- 원인: `_load_draft_fallback_context`에서 `ctx[did]["description"] = token`(THEN_ACTION raw_token)이
  법조문 제목(art_title)을 덮어씀.
- 수정: 덮어쓰기 제거. art_title 유지, raw_token은 `then_action_token`에 별도 보관.

### 이슈 D — 타 sector 법령 누수 (해결, 핵심)
- 증상: 제조업 화학공장 진단에 의료법·특수교육법(SPECIAL_FACILITY 전용),
  주택법·주거약자법(BUILDING/CONSTRUCTION) 등 무관 법령이 적용됨.
- 근본 원인: compiler_core 경로(`evaluate_single_factory`)가 sector 무관하게
  전체 draft(약 10,725건)를 평가. 엔진 판정부(`facility_applicability_eval`)는
  수치/범위 조건만 보고 sector를 전혀 보지 않는 구조(=엔진 내부에 sector 필터 없음).
- 분류 자산은 이미 존재했음: `law_sector_mapping`(law_id, sectors[], ...) — sector 분류 장치.
  단, 수집(domain_code)·분류(law_sector_mapping)는 만들어져 있었으나 진단 경로에 연결 안 됨.
- 해결(입구 분리): `evaluate_single_factory` 입구에서 `factory.sector`로
  `law_sector_mapping`을 그대로 읽어 허용 draft만 평가 대상으로 적재(`_load_sector_allowed_draft_ids`).
  - 해당 sector 포함 법령 → 통과
  - 미매핑 법령 → 가지고 감(나중에 매핑 채운 뒤 제외; 누락 방지 — 사장님 결정)
  - 타 sector 전용 법령 → 입구에서 분리(제외)
  - 매핑 데이터 없거나 조회 실패 시 None 폴백 → 전체 평가(안전)
- 표준 보존: 엔진 내부 표준 용어는 MANUFACTURING, 입력 표준은 INDUSTRIAL.
  입구에서 INDUSTRIAL→MANUFACTURING 변환한 구조이므로, 매핑 대조 시에만
  `_mapping_sector_key`로 MANUFACTURING→INDUSTRIAL 역환원. 표준 자체는 변경 안 함(주석 명시).
- 판정 로직(`evaluate_draft_for_facility`) 불변 — 평가 대상 draft 목록만 필터.
- 검증: 총 의무 254 → 159건. 타 sector 전용 누수 0건(의료법·특수교육법·주택법 제거 확인).
  매핑 법령 29개 전부 INDUSTRIAL 정상. 미매핑(대부분 NFPC 화재기준)은 결정대로 유지.

---

## 3. 검증 하니스 (factory 기반 엔진 검증 도구)

- 목적: 본인인증·결제·횟수제한 없이 factories 사업장으로 진단 실행 →
  결과를 anonymous_diagnosis_results에 public_token으로 저장 →
  기존 결과페이지(paid-diagnosis-result.html) 재사용.
- 라우터: `routers/diagnosis_factory_test.py`
  - `POST /diagnosis/factory-test-run {factory_id}` → 진단 실행·저장·result_page 반환
  - `GET /diagnosis/factory-test-cases` → 검증 사업장 목록
- 목록 정비: status_code='TEST_HARNESS'인 검증 전용 사업장만, 최신순(created_at desc) 노출.
  기존 ACTIVE(335) 등 실데이터가 안 섞이도록 분리.
- 화면: `nexas/engine-test.html` (가로 10열, 입력/결과/검증).

### 등록된 목업
- id `7e8764c5-be59-4dab-9027-fb19bfb5c86c`, '대한정밀화학(목업)',
  sector=INDUSTRIAL, 80명, 8000㎡, ksic C20, 위험물·화학물질·고압가스·보일러=true,
  status_code='TEST_HARNESS'.

---

## 4. 결과페이지 UX

- `nexas/paid-diagnosis-result.html`에 로딩 오버레이(전체화면 스피너 #taiLoading) 추가.
  fetch~렌더 동안 표시, init 완료/실패/네트워크오류 시 hideLoading()으로 숨김, 인쇄 시 숨김.
- 표시 보정(이전 세션): obTitle()/isToken()으로 토큰이면 description 우선 표시.
  엔진 수정 후에도 무해(정상값을 그대로 통과).
- 주의: 한 번 부분 컨텐츠로 덮어써 파일이 깨졌다가(746B) 전체본으로 즉시 복구함.
  → 교훈: 30KB+ HTML은 부분 수정 도구로 통째 재작성하지 말 것(전체 교체형 도구 주의).

---

## 5. SPECIAL_FACILITY — 의도적 보류(dormant) 섹터 (중요 기록)

- SPECIAL_FACILITY(병원·학교 등 특수시설)는 버그로 비활성된 게 아니라 의도적으로 감춰둔 정식 섹터.
- 이유: 해당 분야 법령이 지나치게 분산되어 현 법령엔진 정확도가 부족 → 서비스 노출만 보류.
- 데이터는 보존: `constants.sectors.VALID_SECTORS`에 포함,
  `law_sector_mapping`에 SPECIAL_FACILITY 전용 법령 113건(전부 전용, BUILDING과 공유 0).
- 하니스의 `_SECTOR_FROM_FACTORY`는 SPECIAL_FACILITY→BUILDING으로 보냄(임시).
  → 함부로 "SPECIAL_FACILITY→SPECIAL_FACILITY"로 고치지 말 것(정확도 미확보 섹터 강제 노출 위험).
  해당 코드에 경고 주석 추가함.
- 부활: 법령엔진 정확도 확보 후 별도 결정.
- 실제 서비스 입구(`/diagnosis/run`)는 SPECIAL_FACILITY를 독립 sector로 정상 수용
  (`_ALLOWED_DIAGNOSE_SECTORS`, normalize_sector_db 유지). 즉 부활 시 데이터·입구 준비됨.

---

## 6. 커밋 이력 (이번 세션)

### tai-api (`taiengineering/tai-api`, main, Railway 자동배포)
- `940e1d0` fix(engine): compiler_core rule_row 의무 출력 정상화 (이슈 A·B·C)
- `53017a65` fix(diagnosis): 검증 하니스 목록 TEST_HARNESS 전용 + 최신순
- `96f596cb` feat(engine): 입구 sector 필터 — law_sector_mapping으로 타 sector 분리 (이슈 D)
- `3126f139` docs(harness): SPECIAL_FACILITY→BUILDING '의도적 보류' 주석 추가
- 파일: `services/anonymous_factory_service.py`(최신 SHA 582521b2),
  `routers/diagnosis_factory_test.py`(최신 SHA 9196ace1)

### taieng (`taiengineering/taieng`, main, Cloudflare Pages)
- `742888c` (이전 세션) 결과페이지 토큰→description 표시 보정
- `465fa04` docs: GPT 작업지시서(초기본)
- `2f7a067` fix(paid-result): 파일 복구 + 로딩 스피너 적용
- 파일: `nexas/paid-diagnosis-result.html`(최신 SHA 31f4a0c8)
- 문서: `docs/2026-06-09_GPT_WORKORDER_OBLIGATION_OUTPUT_BUG.md`

### DB (Supabase `vwlahtguyggrhvslabax`, Seoul)
- factories: '대한정밀화학(목업)' status_code → 'TEST_HARNESS' 변경(UPDATE)
- 그 외 스키마 변경 없음(읽기 검증 위주)

---

## 7. 남은 일 / 다음 작업

1. 미매핑 법령에 sector 채우기: 현재 "가지고 감"이라 학교복합시설·공동주택·도로터널
   화재기준 등 일부 부정확 항목이 제조업 결과에 남음. law_sector_mapping의 미매핑(sectors=null)을
   채우면 입구 필터가 자동으로 제외 → 점진 정확도 개선. (법적 분류 판단 = 사장님/GPT 영역)
2. 결과페이지 로딩 속도: `enrich_rules_with_candidate_slots`가 조회 시 per-law 반복 쿼리 +
   Railway(SG)↔Supabase(Seoul) 왕복. 입구 sector 필터로 평가량 절반↓ 되어 일부 개선됨.
   근본 개선(저장 시점 enrich로 이동 / 배치 쿼리)은 미적용 — 별도 결정 대기.
3. SPECIAL_FACILITY 부활: 엔진 정확도 확보 후. 데이터·입구 준비 완료 상태.

---

## 8. 원칙 메모 (이번 세션에서 재확인)

- 엔진 판정 로직(GPT 영역, `facility_applicability_eval` 등)은 수정하지 않음.
  이번 수정은 모두 rule_row 생성·출력 변환·입구 필터 단계.
- 입력 표준은 3입구(BUILDING/INDUSTRIAL/CONSTRUCTION)로 나뉘어 있음 — 입력값 구조 자체가 sector마다 다르기 때문.
  법령 분류는 그 위에 따라온 것. sector 필터는 이 입구 층위와 같은 위치에서 작동.
- 문제 생길 때마다 표준을 바꾸지 말 것. 표준은 그대로 읽어서 거른다.
- 30KB+ 파일은 전체 교체형 도구로 부분 수정하다 통째 날아갈 수 있음 — 전체본 확보 후 신중히.
