# RESULT PAGE BACKTRACE — 실행버튼→결과 실제 추적 (브라우저 Network 증거)
# WO-RESULT-PAGE-BACKTRACE-001

**작성일**: 2026-06-21
**방법**: 추정 금지. taieng.co.kr/engine-test 실제 실행 + 브라우저 Network + 소스 추적.
**증거**: 브라우저 Network 탭(실제 API 호출) + GitHub 소스. 수정 0.

---

## ★★★ 핵심: 실제 결과 엔진은 4세대가 아니라 "compiler_core"였다

```
이전 WO에서 추적한 4세대(V4/legal_runtime/v510/legacy)는
실행 버튼이 쓰는 엔진이 아니었다.

실행 버튼 → run_step1_via_compiler (compiler-core)
  = UI 무료진단(/diagnosis/run)과 동일 엔진.
  = legal_runtime_fetch.py 주석 "소비자 진단은 compiler_core 경로"와 일치.
```

---

## STEP-1: 실행 버튼이 호출하는 실제 API (Network 증거)

```
브라우저 Network 탭 (engine-test 페이지, 실행 버튼 클릭):

  POST https://api.taieng.co.kr/diagnosis/factory-test-run       (200)
  GET  https://api.taieng.co.kr/diagnosis/factory-test-verify/{token}  (200)

★ /legal-engine/diagnose/step1 아님. factory-test-run/verify임.
  소스: routers/diagnosis_factory_test.py ("Factory-based Engine Test Harness")
```

---

## STEP-2: Payload → DB (소스)

```
POST factory-test-run body: { factory_id }
  → factories 테이블 조회 (status_code='TEST_HARNESS' 검증 전용 사업장)
  → _factory_to_step1_body: factories 행 → DiagnoseStep1Body
  검증 factory_id (Network에서 확인):
    건설: 16cea20b-69eb-4abd-9366-a63fa21712d3
    산업: ef9766ee-824b-42d8-b7a3-d74a096ef871
판정: YES (factory_id 실재, DiagnoseStep1Body로 변환)
```

---

## STEP-3: 실제 API 응답 원본 (raw, 화면 아님)

```
GET factory-test-verify 응답 (fetch raw):

[건설]  result_sector=CONSTRUCTION, sector_health=WARN
  summary: total_laws 39 / ok 9 / mismatch 0 / unmapped 30 / total_rules 138
  unmapped_laws: 한국전기설비규정(7), 자동화재탐지 NFPC203(6),
                 스프링클러 NFPC103(4), 피난기구 NFPC301(3) ...
                 = 소방·전기 설비 화재안전기준이 sector 미매핑

[산업]  result_sector=MANUFACTURING, sector_health=WARN
  summary: total_laws 38 / ok 8 / mismatch 0 / unmapped 30 / total_rules 118
```

---

## STEP-4: 응답 데이터 출처 (소스, 필드별)

```
factory-test-run 저장:
  run_step1_via_compiler(compiler-core) → full_result
  → anonymous_diagnosis_results 저장 (public_token, source_type='factory_test')
  → 결과페이지 paid-diagnosis-result.html?token=public_token 재사용

factory-test-verify 검증 (별도):
  full_result.rules_table 의 law_name 수집
  → law_master(id) → law_sector_mapping(sectors)  ← 어댑터가 읽음
  → check_engine.check(items, expected_sector)    ← 범용 대조기
  → verdict: MATCH/MISMATCH/NO_RULE
  → sector_health: FAIL(mismatch>0)/WARN(unmapped>0)/PASS
```

---

## STEP-5: 응답 생성 함수 (확정)

```
[결과 생성]  run_step1_via_compiler  (services/diagnosis_integrated_svc.py)
   = compiler-core 엔진. ENGINE_VERSION="v3.0-compiler-core-factory-test".
   = 실제 UI 무료진단과 동일. ★ 이것이 진짜 결과 엔진.

[sector 검증]  check_engine.check  (services/check_engine.py)
   = 범용 체크엔진. sector/법령 모르는 대조기(오염 격리).
   = factory-test-verify가 어댑터로 호출.
   ★ Check Engine이 살아있고 실제 호출됨 (단 용도=sector 적합성 역검증).

[저장]  anonymous_diagnosis_results (factory_test 경로)
   = factory_diagnosis_results 아님. anonymous 테이블 사용.
```

---

## STEP-6: 최종 연결지도 (소스+Network 확정)

```
[실행 버튼] (engine-test 화면)
   ↓ POST
/diagnosis/factory-test-run  (routers/diagnosis_factory_test.py)
   ↓ factories 조회 + _factory_to_step1_body
DiagnoseStep1Body
   ↓
run_step1_via_compiler  ← ★ compiler-core 엔진 (진짜 결과 생성)
   ↓ full_result
anonymous_diagnosis_results 저장 (public_token)
   ↓
결과페이지 paid-diagnosis-result.html?token=...

[검증 경로 — 별도]
/diagnosis/factory-test-verify/{token}
   ↓ rules_table 법령명 수집
law_master → law_sector_mapping (어댑터)
   ↓ CheckItem 변환
check_engine.check(items, expected_sector)  ← ★ Check Engine 실제 가동
   ↓ verdict (MATCH/MISMATCH/NO_RULE)
sector_health (FAIL/WARN/PASS) → 검증 화면
```

---

## ★ 이 추적이 확정한 것 (이전 WO들 정정·종합)

```
1. 진짜 결과 엔진 = compiler_core (run_step1_via_compiler).
   - 이전에 추적한 V4/legal_runtime/v510/legacy는 곁가지였음.
   - compiler_core가 UI 무료진단 + 검증하니스 공통 엔진.

2. Check Engine은 "없는" 게 아니라 살아있다.
   - services/check_engine.py 실재. factory-test-verify가 호출.
   - 단 용도 = "의무→체크 변환"이 아니라 "sector 적합성 역검증".
   - 오염 격리 설계: 코어는 sector/법령 모르는 범용 대조기.

3. 현재 결과의 실제 상태 (검증 화면 = 살아있는 프로브):
   - mismatch 0 = 섹터 누수(잘못된 섹터 법령 섞임) 없음.
     (sector filter 작업 효과로 추정 — 단 이 엔진은 compiler_core라 별도 확인 필요)
   - unmapped 30 = 소방·전기 설비 화재안전기준이 law_sector_mapping 미등록.
     → 건설/산업 양쪽 다 WARN. 진짜 미해결 과제는 "오매핑"이 아니라
       "law_sector_mapping에 NFPC·전기설비규정 등이 누락"임.
```

---

## 성공 기준 / 미확인

```
RPB-01 호출 API 확정       → ✅ factory-test-run/verify (Network 증거)
RPB-02 Payload→DB          → ✅ factory_id → factories → step1_body
RPB-03 raw response 확보    → ✅ verify 응답 원본 (sector_health/summary)
RPB-04 필드별 출처          → ✅ compiler-core + law_sector_mapping + check_engine
RPB-05 응답 생성 함수       → ✅ run_step1_via_compiler / check_engine.check
RPB-06 연결지도            → ✅

미확인(다음):
  - run_step1_via_compiler 내부: compiler_core가 읽는 법령 테이블이 무엇인가
    (master_rule_v2? semantic_clause? law_sector_mapping?)
  - factory-test-run 응답의 rules_table 실제 내용(의무 문장 수준)
  - unmapped 30개를 law_sector_mapping에 등록하면 WARN 해소되는가
```

---

## 완료 문장

```
engine-test 결과 페이지를 실행 버튼부터 브라우저 Network로 역추적하여,
실제 결과 엔진이 compiler_core(run_step1_via_compiler)이며,
Check Engine(services.check_engine)이 sector 적합성 역검증으로 실제 가동 중임을
확정하였다. 현재 두 프로브(건설/산업) 모두 mismatch 0 / unmapped 30(WARN)이며,
미해결 핵심은 섹터 오매핑이 아니라 소방·전기 설비 법령의 law_sector_mapping 누락이다.
추정 없이 Network·소스로 확인하였다.
```
