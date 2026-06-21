# RESULT FIELD LINEAGE — 결과 문장 한 줄의 100% 계보
# WO-RESULT-RUNTIME-BACKTRACE-003

**작성일**: 2026-06-21
**목적**: 소비자 결과 문장 한 줄이 어디서 생성되는지 끝까지 소스 추적.
**방법**: 추정 0, DB 건수 0. 결과페이지→API→service→compiler→법령엔진 소스만.
**수정 0**.

---

## ★★★ 결론: compiler_core가 법령엔진 테이블을 직접 읽는다 (플래그 아님, 기본 경로)

```
이전 WO에서 본 "환경변수 플래그 3분기(v2/runtime/legacy)"는
실행 버튼이 쓰는 경로가 아니었다.

실제 소비자 결과 경로 = compiler_core(run_anonymous_diagnosis)가
법령엔진 테이블(executable_draft/draft_slot/law_article/law_master/
facility_applicability)을 직접, 기본으로 읽는다.
= 두 체인이 "이미 연결되어 살아있다".
```

---

## STEP-1: 결과 페이지 진입점 (확정)

```
GET /diagnosis/result/{token}
  → get_diagnosis_result_web (routers/diagnosis_result_web.py)
  → _build_result_payload(token, free_preview_limit=5)
  → anonymous_diagnosis_results.full_result 를 "읽기"
  → _refine_rules_table (표시용 정제: dedupe + 코드토큰→사람텍스트)
  ★ 이 API는 결과를 생성하지 않음. 저장된 full_result를 읽어 정제만.
  ★ 무료는 rules_table 5건만 노출(free_preview_limit=5). 화면 138은 summary.total.
```

---

## STEP-2: rules_table 생성 위치 (확정)

```
full_result(=rules_table 원본)을 만든 곳:
  factory_test_run → run_step1_via_compiler
    → run_anonymous_diagnosis (services/anonymous_factory_service.py)
      → _compiler_result_to_step1_format → rules_table 조립

rules_table[i] 조립 함수:
  _task_to_rule_row (task_candidate 있을 때)
  _applicability_to_rule_row (applicability만 있을 때, fallback)
```

---

## STEP-3: rule_type 출처 (확정)

```
rule_type = APPOINTMENT_TASK_CANDIDATE 등.
출처: draft_slot.family_name → _ACTION_TO_TASK 변환 (중간 변환 있음).

  _ACTION_TO_TASK = {
    "APPOINT_FAMILY":  "APPOINTMENT_TASK_CANDIDATE",
    "INSPECT_FAMILY":  "INSPECTION_TASK_CANDIDATE",
    "REPORT_FAMILY":   "REPORT_TASK_CANDIDATE", ...
  }

판정: task_candidate 테이블 직접 아님. 중간 변환(YES).
  draft_slot(THEN_ACTION).family_name → task_type enum.
```

---

## STEP-4: remarks "특정소방대상물의 소방안전관리" 출처 (확정)

```
remarks/description 출처: law_article.article_title (법조문 제목).

  _load_draft_fallback_context:
    executable_draft.article_id → law_article(article_no, article_title)
                                → law_master(law_name)
    ctx[did]["description"] = art_title or law_name
    # 주석: "description = 법조문 제목(사람이 읽는 텍스트)"

= "특정소방대상물의 소방안전관리" = law_article.article_title 원문.
  법령엔진 law_article에서 직접 옴. 별도 enum/하드코딩 아님.
```

---

## STEP-5: 결과 JSON 전체 계보 (확정)

```
result_data.rules_table[i]
  ├ .law_name      ← law_master.law_name
  ├ .law_article   ← law_article.article_no
  ├ .remarks       ← law_article.article_title
  ├ .description   ← _obligation_summary_text(article_title 우선)
  ├ .rule_type     ← draft_slot.family_name → _ACTION_TO_TASK
  ├ .category      ← _bucket_for_task_type(task_type) → 선임/점검/조치/신고/보고
  ├ .obligation_type ← _BUCKET_TO_OBLIGATION[bucket]
  └ .source        ← SOURCE_DIAGNOSIS ("DIAGNOSIS")

  연결 체인:
   facility_applicability(평가결과)
    → executable_draft (draft_id → article_id, rule_candidate_id, part_id)
    → law_article (article_title, article_no, law_id)
    → law_master (law_name)
   + draft_slot (THEN_ACTION family_name → task_type)
```

---

## STEP-6: compiler_core 사용 여부 (확정)

```
compiler_core 사용 = YES.

  run_step1_via_compiler
   → run_anonymous_diagnosis (temp-factory lifecycle):
     1. create_temp_factory       (임시 factories 행, status='ANON_TEMP')
     2. evaluate_single_factory   (facility_applicability 평가)
        ★ _load_sector_allowed_draft_ids = sector filter 여기 있음
     3. fetch_compiler_candidates (services/compiler_core_svc.py)
     4. _compiler_result_to_step1_format (rules_table 조립)
     5. cleanup_temp_factory      (임시 factory 삭제)

  파일 주석: "Phase 2: replaces runtime_metadata_resolution path for consumer step1"
  = compiler_core가 runtime 경로를 대체함(소비자 step1).
```

---

## STEP-7: 최종 연결지도 (소스 확정)

```
[실행 버튼] (engine-test)                              YES
  ↓ POST /diagnosis/factory-test-run
[Router] diagnosis_factory_test                         YES
  ↓ run_step1_via_compiler
[Service] diagnosis_integrated_svc                      YES
  ↓ run_anonymous_diagnosis
[Compiler] anonymous_factory_service (temp-factory)     YES
  ↓ create_temp_factory → evaluate_single_factory
[Rule Source] 법령엔진 테이블 직접:                     YES ★
   executable_draft / draft_slot / law_article /
   law_master / facility_applicability
   (+ sector filter: law_sector_mapping)
  ↓ fetch_compiler_candidates
[Compiler Core] compiler_core_svc                       YES
  ↓ _compiler_result_to_step1_format
[Presentation] rules_table 조립(_task_to_rule_row 등)   YES
  ↓ anonymous_diagnosis_results.full_result 저장
[result_data]                                           YES
  ↓ GET /diagnosis/result/{token} → _refine_rules_table
[정제레이어] diagnosis_result_web + diagnosis_transform YES(읽기/정제)
  ↓
[결과 화면]                                             YES

★ 전 구간 YES. 죽은 구간 없음. compiler_core가 법령엔진을 직접 사용.
```

---

## ★ 이 추적이 확정한 것 (종합)

```
1. 결과 문장 계보 100% 확정:
   remarks="특정소방대상물의 소방안전관리" = law_article.article_title.
   rule_type=APPOINTMENT_TASK_CANDIDATE = draft_slot.family_name→_ACTION_TO_TASK.
   둘 다 법령엔진 테이블에서 옴(하드코딩/별도enum 아님).

2. compiler_core가 진짜 엔진이고, 법령엔진을 직접 읽는다:
   facility_applicability/executable_draft/draft_slot/law_article/law_master.
   = "법령엔진→결과" 연결은 이미 살아있는 기본 경로.
   = 이전 WO의 "플래그로 꺼져있다"는 v510 경로 얘기였고,
     실제 소비자 경로(compiler)는 처음부터 법령엔진에 붙어 있었다.

3. sector filter(사장님 작업)의 실제 위치 확정:
   _load_sector_allowed_draft_ids (anonymous_factory_service).
   executable_draft→law_article→law_master←law_sector_mapping.
   미매핑 법령은 "보수적 통과"(allowed.add) → 소방 NFPC가 건설에 들어온 이유.
   = verify unmapped 30과 동일 원인. 코드로 확정.
```

---

## 완료 문장

```
소비자 결과 문장 한 줄("특정소방대상물의 소방안전관리")의 계보를
끝까지 추적하여, 그것이 law_article.article_title이며,
rule_type은 draft_slot.family_name의 _ACTION_TO_TASK 변환임을 확정했다.
실제 결과 엔진은 compiler_core(run_anonymous_diagnosis)이고,
법령엔진 테이블(executable_draft/draft_slot/law_article/law_master/
facility_applicability)을 직접 읽는 기본 경로이다.
실행 버튼→결과 화면 전 구간이 YES로 살아있으며,
소방 법령 오적용은 sector filter의 미매핑 보수적 통과(코드 명시)가 원인이다.
추정·DB건수 없이 소스로 100% 확정했다.
```
