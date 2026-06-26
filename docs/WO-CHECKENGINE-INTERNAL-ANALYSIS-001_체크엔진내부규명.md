# WO-CHECKENGINE-INTERNAL-ANALYSIS-001 — Check Engine 내부 역할 규명

**작성일:** 2026-06-26 | **상태:** 완료 (읽기 전용 역공학 — 코드/DB 수정 0)
**방법:** 실제 커밋 코드 직독 (routers/services) + 코드 전역 검색. 추측 0.

> 목적은 설계가 아니라 **증명**. Q1~Q8을 실제 코드 근거로 YES/NO 답한다.

---

## Boundary Check

```
Applicability 내부 작업인가?   NO     Boundary 변경?   NO
Data Contract 변경?           NO     Breaking?        NO
→ 읽기 전용. 코드/DB/문서(코드) 무수정. 문서 작성만 산출.
```

---

## 분석한 실제 파일 (근거)

```
routers/check_adapter_api.py            POST /check-adapter/run-track-a (진입점)
services/check_engine_adapter.py        load_track_a_results() — Track A 본체
routers/obligation_adapter.py           obligation 경로 진입점
services/obligation_instance_adapter.py Glue (obligation_instance+semantic_clause)
services/obligation_adapter_service.py  Adapter (obligations 스키마 변환)
schemas/check_input_schema.py           CheckResult 스키마 (계약서 기확인)
+ 코드 전역 검색: law_appendix / law_article_citation / delegation
```

---

## 1. Call Graph (실측)

### 경로 ① Track A "Check Engine" (facility_applicability 관찰)
```
POST /check-adapter/run-track-a (check_adapter_api.run_track_a)
  └─ load_track_a_results(supabase, facility_id, status_filter)   [check_engine_adapter]
       ├─ read facility_applicability (id, draft_id, applicability_status, match_details)
       ├─ draft_id  → executable_draft (article_id)
       ├─ article_id→ law_article (law_id, article_no, article_title)
       ├─ law_id    → law_master (law_name)
       └─ assemble CheckResult(verdict=_status_to_verdict, reason=_status_to_reason,
                               check_method="track_a_facility_applicability")
```

### 경로 ② Obligation 경로 (우리 171 = trigger 기반)
```
obligation_instance (Generator 산물)
  └─ fetch_obligation_instance_rows()                 [obligation_instance_adapter = Glue]
       └─ obligation_instance + semantic_clause JOIN
          (executor_text, condition_text, action_text, content_type)
  └─ obligation_instances_to_candidates() → candidates
  └─ build_obligations_from_trigger_candidates()      [obligation_adapter_service = Adapter]
       └─ _build_obligation_from_candidate()
          category = _category_from_trigger(trigger_code)   ← 룰 매핑
          law_name = ""  law_article = ""  evidence = []     ← 빈 값
  └─ build_result_data() → result_data.{obligations, key_obligations}
  └─ diagnosis_transform (정제레이어 = Check Layer)   → 표현/category
```

**두 경로는 평행하다.** ②는 ①(Track A Check Engine)을 호출하지 않는다.

---

## 2. Trace Flow (실측)

```
rich Legal Trace (citation·delegation·appendix·definition·inheritance·family_tree·relation)
  → 런타임 엔진 코드에서 호출 0건.
  - law_appendix      : applicability_api.py(① Applicability 조건매칭)에서만 사용. Check Engine/Layer 아님.
  - law_article_citation : scripts/...partial_collect.py(데이터 수집 스크립트)에만. 런타임 0.
  - delegation/inheritance/family_tree/relation : 런타임 호출 0.

존재하는 "trace" = 최소 법령 식별 JOIN 뿐:
  ① Track A: draft → article → law_master  (law_name 해결)
  ② Obligation Adapter: 해결 안 함 (law_name="" 빈 값, 주석 "이후 JOIN으로 보강 가능")
     ※ LEGAL-TRACE-001의 clause→article→law_master는 분석용 SQL이며 엔진 코드 미구현.
```

---

## 3. Option 존재 여부 (실측)

```
mode / flag / type / option / strategy / builder / trace_only / verify_only → 전부 없음.
  - run-track-a 파라미터: status(MATCH_CANDIDATE/POSSIBLE_CANDIDATE) 필터뿐.
  - check_method = "track_a_facility_applicability" 상수 (전략 스위치 아님).
→ "같은 엔진을 옵션만 바꾸는 구조"가 아니다. 단일 고정 흐름.
```

---

## 4. 실행 순서 (요청 1건 기준)

```
[Track A]  run_track_a → load_track_a_results → (facility_applicability read)
           → draft/article/law JOIN → CheckResult 조립 → 반환. 끝. (판정+법령식별만)

[Obligation/우리 171]
  Generator(trigger_obligation_generator) → obligation_instance 적재
  → Glue(fetch_obligation_instance_rows: embedded join, 실패 시 2-step 폴백)
  → candidates 변환
  → Adapter(_build_obligation_from_candidate: category 룰매핑, law/evidence 공란)
  → build_result_data
  → 정제레이어(diagnosis_transform): category/표현
```

---

## 5. Layer 책임도 (실측)

```
Applicability(V4, applicability_api)  판정 + 별표/조건 매칭 (appendix_no 사용)        [GPT]
Generator(trigger_obligation_*)       obligation_instance 생성
Glue(obligation_instance_adapter)     변환만 (executor/condition/action passthrough)
Adapter(obligation_adapter_service)   obligations 스키마 변환 + category 룰매핑. trace/6W/evidence 생성 X
Check Engine(Track A, check_engine_adapter)  facility_applicability → verdict + 최소 법령식별. 별도 관찰 경로
Check Layer(정제레이어, diagnosis_transform) 표현/category. 자체 rich trace X, Check Engine 호출 X
```

---

## 6. 최종 구조도 (증명된 실체)

```
                 ┌─────────────────────────── 경로 ① (관찰/판정) ───────────────────────────┐
facility_applicability → Track A Check Engine(load_track_a_results)
                          → CheckResult(verdict, reason, law_name, check_method=const)
                          [draft→article→law 최소 식별. 6W/evidence/required_data/rich trace = 없음]

                 ┌─────────────────────────── 경로 ② (우리 171, 운영) ──────────────────────┐
obligation_instance → Glue → Adapter(law/evidence 공란, category 룰매핑)
                       → result_data → 정제레이어(Check Layer: 표현/category)
                       [rich Legal Trace = 없음. law_name JOIN조차 어댑터 미수행]

두 경로는 평행. ②는 ①을 호출하지 않음. rich Legal Trace는 어느 경로에도 코드로 없음(문서 SQL만).
```

---

## 7. Q1 ~ Q8 답변 (추측 없이)

```
Q1. Check Engine이 Legal Trace를 수행하는가?
    NO (rich). 단, draft→article→law_master 최소 법령식별은 YES(제한적).
    citation/delegation/appendix/definition/inheritance/family_tree/relation 호출 0.

Q2. 6W를 생성하는가?
    NO. CheckResult = verdict/reason/법령식별/check_method. who/when/where/what/how 없음.
    (Glue가 executor/condition/action을 passthrough하나 6W로 분해하지 않음.)

Q3. Evidence를 생성하는가?
    NO(생성 아님). V4 경로는 evidence=[law_name+appendix_no] = 기존 필드 조합.
    Trigger 경로(우리 171)는 evidence=[] 빈 값. → 생성 0, 조합 일부.

Q4. Required Data를 생성하는가?
    NO. 코드 어디에도 required_data 생성 없음.

Q5. Trace를 Option으로 호출할 수 있는가?
    NO. mode/flag/strategy/builder/trace_only/verify_only 없음. status 필터뿐. check_method 상수.

Q6. Check Layer는 Check Engine을 호출하는가?
    NO. 정제레이어는 Adapter의 result_data.obligations를 소비. Track A Check Engine 미호출(평행).

Q7. 아니면 별도 Trace를 수행하는가?
    별도 rich trace도 NO. 정제레이어는 category/표현만. 시스템 전체에서 rich trace = 0.
    최소 법령식별만 ①Track A에 존재(②어댑터는 그것조차 공란).

Q8. 중복 Trace가 존재하는가?
    rich trace 기준 NO(애초에 0). 평행한 두 어댑터(facility_applicability vs obligation_instance)가
    각자 최소/무 법령식별을 할 뿐. 중복된 rich Legal Trace는 없음.
```

---

## 역할 결정 (CASE A/B/C)

WO의 세 CASE 중 **CASE C에 가장 가깝다(정정 포함):**

```
CASE C(정정): Check Engine(Track A) → 판정(verdict) + 최소 법령식별
              Check Layer(정제) → 별도(표현/category)
  단, "별도 Trace"의 실체는 rich Legal Trace가 아니라 표현 변환이며,
  두 레이어는 순차 호출이 아니라 평행 경로다(②는 ①을 부르지 않음).
  rich Legal Trace는 어느 레이어에도 코드로 존재하지 않는다 — 문서(LEGAL-TRACE-001 SQL)로만 존재.
```

CASE A(Check Layer→Check Engine→Legal Trace), CASE B(Check Engine→Trace→Check Layer→6W)는
**코드 근거로 모두 거짓.**

---

## 부가 발견 (사실만 기록)

```
- Trigger 경로 Adapter는 law_name/law_article를 공란으로 둔다(주석: "이후 JOIN으로 보강 가능").
  → 우리 171의 obligations는 운영 어댑터 출력에서 법령명이 비어 있다.
    LEGAL-TRACE-001이 채운 law_name은 분석용 SQL 결과이지 어댑터 출력이 아니다.
- category는 기존 엔진이 룰 매핑(_category_from_trigger / action_type)으로 생성 중.
  (TRACE-001에서 우리가 "category 생성 금지"라 한 것과 별개로, 운영 엔진은 이미 룰 매핑함.)
- tai-api/docs/ 에 출력매핑 문서 사본 존재(이전 창 잔여 추정). 문서 단일경로 규칙(taieng/docs)과 불일치 — 정리 별도 판단.
```

---

*WO-CHECKENGINE-INTERNAL-ANALYSIS-001 완료. 가설이 아니라 코드로 증명했다.*
*rich Legal Trace는 런타임에 없다(문서 SQL만). Check Layer는 Check Engine을 호출하지 않는다(평행). 옵션 구조 없음.*
