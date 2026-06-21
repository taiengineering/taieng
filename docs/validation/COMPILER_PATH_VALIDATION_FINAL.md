# COMPILER PATH VALIDATION — Canonical Path 검증 최종
# WO-COMPILER-PATH-VALIDATION-001

**작성일**: 2026-06-21
**목적**: compiler_core 경로가 실제 운영 정답 경로인지 의미까지 검증.
**방법**: 결과 글읽기(카운트 아닌 의미 분류). 수정 0(코드/DB/sector/binding/법령).
**샘플**: 건설(token 16cea20b, 근로30) 114건 + 산업(ef9766ee, KSIC C20 화학) 97건.
  (건물 프로브는 engine-test에 부재 → 건설20·산업20 중심 검증, 건물은 후속)

---

## STEP-1: 검증 샘플 (COMPILER_PATH_SAMPLE_SET)

```
paid-result 엔드포인트로 전체 rules_table 확보(무료 5건 제한 우회):
  건설: applicable_count 138, rules_table 114건(dedupe 후)
  산업: applicable_count 118, rules_table 97건(dedupe 후)
각 행: law_name / remarks(=law_article.article_title) / rule_type / category 확보.
```

---

## STEP-2: 결과 역추적 (RESULT_LINEAGE_VALIDATION)

```
앞 WO(RESULT_FIELD_LINEAGE)에서 소스로 확정한 계보를 샘플에 적용:
  결과 문장(remarks) ← law_article.article_title       YES
  rule_type ← draft_slot.family_name → _ACTION_TO_TASK  YES
  law_name ← law_master.law_name                        YES
  연결 ← facility_applicability → executable_draft       YES
판정: 전 샘플 계보 YES. 결과 문장이 법령엔진 테이블에서 정상 유래.
```

---

## STEP-3: 의미 검증 (RESULT_MEANING_REVIEW) — 글 읽기

```
검증 질문: 이 결과가 해당 업종·시설·입력에 실제로 맞는가?

[건설] 근로자 30명 건설현장 결과 114건을 읽음:
  법령 분포 상위 = 소방시설 설치·관리법/소방시설공사업법/NFPC 화재안전기준
    (옥내소화전·미분무·포·CO2·할론·분말소화설비 ...)
  건설 고유 의무(안전관리계획/안전점검/안전교육) = 결과에 0건.
  판정: 오적용 다수. 근로30 건설현장에 소방설비 화재안전기준은 부적합
    (이는 소방시설 설치된 건물의 소방안전관리 의무이지 공사현장 안전의무 아님).

[산업] KSIC C20 화학제조 결과 97건을 읽음:
  산안법/산안법시행규칙/작업환경측정 고시 = 산업 고유 의무로 정상 유입(13건).
  그러나 나머지 다수가 건설과 동일한 소방 NFPC 법령.
  판정: 정상(산업 고유) + 오적용(소방) 혼재.

★ 공통 패턴: 건설·산업 입력이 달라도 소방 NFPC 법령 세트가 양쪽에 동일 유입.
  = 소방 법령이 sector·입력과 무관하게 모든 진단에 공통으로 들어옴.
```

---

## STEP-4: LAW_UNKNOWN 영향 (LAW_UNKNOWN_IMPACT_REPORT)

```
글 읽기로 소방/전기/기타 분류한 의미 비율:

[건설 114건]
  소방·화재 105건 (92%)   ← LAW_UNKNOWN_PASS (미매핑 보수적 통과)
  전기설비 6건            ← LAW_UNKNOWN_PASS
  정상매핑 추정 3건: 작업환경측정1 / 방사선1 / 친환경주택1
  건설 고유 의무 0건

[산업 97건]
  소방·화재 80건 (82%)    ← LAW_UNKNOWN_PASS
  전기설비 2건            ← LAW_UNKNOWN_PASS
  정상매핑 13건: 작업환경측정6 / 산안법시행규칙4 / 산안법3 + 방사선1·교육1

원인(앞 WO 소스 확정): _load_sector_allowed_draft_ids에서
  law_sector_mapping에 secs=None(미매핑) → allowed.add(did) 보수적 통과.
  소방 NFPC·전기설비규정이 law_sector_mapping 미등록 → 전 섹터 유입.
```

---

## STEP-5: Canonical Path 적합성 (CANONICAL_PATH_EVALUATION)

```
판정 기준 대조:
  A(95%+ 정상) → 아님 (오적용 82~92%)
  B(연결 맞음 + 오염 다수 → 데이터 정화) → ★ 해당
  C(경로 자체 오류) → 아님

근거 — 경로는 정답이다:
  - 산업에 산안법·작업환경측정이 정상 유입 = compiler_core가 sector/입력 반영.
  - 결과 문장 계보(law_article.article_title) 정상.
  - 산업 고유 13건이 올바르게 분류됨.
근거 — 데이터가 오염:
  - 소방 NFPC가 law_sector_mapping 미매핑 → 보수적 통과로 전 섹터 유입.
  - 건설 92%/산업 82% 오염.

판정: B (경로 승인 가능, 단 law_sector_mapping 정화 선행 필요).
```

---

## STEP-6: 격리 후보 (RUNTIME_ISOLATION_CANDIDATES)

```
앞 WO(RESULT_PAGE_BACKTRACE)에서 실행버튼 경로 확정:
  실행버튼 → factory-test-run → run_step1_via_compiler → run_anonymous_diagnosis
  = compiler_core 단일 경로.

타 경로의 실행버튼 사용 여부:
  V4 Adapter (obligation_adapter)  → 미사용 (별도 /obligation-adapter 라우터)
  legal_runtime (apply)            → 미사용 (별도 /legal-engine/apply)
  v510 (diagnose/step1)            → 미사용 (별도 엔드포인트, 실행버튼 아님)
  legacy (step2/step3)             → 미사용 ("LEGACY-ISOLATED" 주석)

분류: 위 4경로 = 격리 가능(실행버튼 미사용). 단 삭제 금지(검증 WO).
  격리 실행은 후속 WO-RUNTIME-CANONICAL-PATH-001.
```

---

## STEP-7: 최종 판정 (COMPILER_PATH_VALIDATION_FINAL)

```
[CONDITIONAL PASS]

compiler_core 경로 = 실제 운영 정답 경로로 인정.
단, Canonical Path 지정은 law_sector_mapping 정화(소방 NFPC·전기설비 sector 등록)
후로 조건부.

이유:
  - 경로 존재·계보·sector반영 모두 YES (경로는 맞음).
  - 그러나 현재 결과의 82~92%가 소방 법령 오적용(LAW_UNKNOWN_PASS).
  - 경로 오류가 아니라 매핑 데이터 미완 → CONDITIONAL.

정화 대상(이 WO 범위 아님, 법령해석=GPT):
  law_sector_mapping에 소방 NFPC(~30종)·한국전기설비규정 등의 sector 등록.
  "어느 소방법이 어느 섹터에 적용되나"는 법령 판단 → GPT.
  (단 소방 설비 의무는 대개 "건물" 섹터 또는 시설 보유시 적용이지
   공사현장/제조공정 자체 의무가 아님 → 매핑 시 이 구분이 핵심)
```

---

## 성공 기준

```
CPV-01 결과 샘플 확보       → ✅ 건설114 + 산업97 (paid-result 전체)
CPV-02 계보 검증 완료       → ✅ 전 샘플 YES (law_article/draft_slot/executable_draft)
CPV-03 의미 검증 완료       → ✅ 건설 오적용92% / 산업 정상13+오적용82%
CPV-04 LAW_UNKNOWN 영향 분석 → ✅ 보수적 통과로 소방 전섹터 유입 확정
CPV-05 Canonical Path 판정  → ✅ B (경로맞음+데이터정화)
CPV-06 격리 후보 식별       → ✅ V4/legal_runtime/v510/legacy 미사용=격리가능
CPV-07 수정 0건             → ✅
```

---

## 완료 문장

```
발견된 compiler_core 경로가 실제 운영 정답 경로인지 검증하였다.
경로 존재·계보·sector반영은 모두 YES이나, 결과 의미는 소방 법령이
82~92% 오적용된 상태(law_sector_mapping 미매핑 보수적 통과)임을
글 읽기로 확인하였다. 판정: CONDITIONAL PASS — 경로는 정답,
law_sector_mapping 정화 후 Canonical Path 지정.
경로 자체 오류는 아니므로 재조사(FAIL)는 불필요.
수정 없이 검증만 수행하였다.
```

---

## 다음 (사장님 판단)

```
1. WO-RUNTIME-CANONICAL-PATH-001 (V4/legal_runtime/v510/legacy 격리) — 경로 확정용.
2. law_sector_mapping 정화 WO — 소방 NFPC·전기설비 sector 등록 (GPT 법령해석 인계).
   이게 CONDITIONAL → PASS 전환의 핵심.
3. 건물 프로브 추가 검증 (engine-test에 건물 없음 → 무료진단 플로우로 생성 필요).
```
