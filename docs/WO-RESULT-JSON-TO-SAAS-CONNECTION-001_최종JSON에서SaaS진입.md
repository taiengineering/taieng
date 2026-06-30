# WO-RESULT-JSON-TO-SAAS-CONNECTION-001 — Final Result JSON → SaaS 진입 함수 연결

**작성일:** 2026-06-30 | **범위:** Final Result JSON 이후만. 함수 호출 기준만(숫자/row count/runtime 건수 0). 입력→JSON 재분석 안 함.
**판정: BROKEN.** Final Result JSON을 SaaS 진입으로 전달하는 함수 호출이 **없음**.

---

## TASK-001 — Final Result JSON을 받는 호출자
```
services/anonymous_factory_service.run_anonymous_diagnosis(...) → result_data (Final Result JSON)
  ← 호출자: routers/anonymous_diagnosis.py
            _run_step1_via_service(supabase, step1_body)
              result_data = run_anonymous_diagnosis(...)
              return {"status":"success", "data": result_data}
  ← 그 호출자: create_anonymous_diagnosis(body)   (POST /anonymous-diagnosis)
              eng = _run_step1_via_service(...)
              full_result = eng["data"]            # ← Final Result JSON 수신 지점
```

## TASK-002 — 그 결과를 저장/전달하는 함수 (create_anonymous_diagnosis 내, 함수 호출만)
```
full_result 수신 후 호출되는 함수:
  _partial_from_full(full_result)                 → partial (요약본 생성)
  supabase.table("anonymous_diagnosis_results").insert(row)   → 진단결과 DB 저장(JSON 보관)
  activate_documents_for_workflow(...)            → watch_engine.document (문서 자동활성 훅, flow_key="law_diagnosis")
  return {publicToken, partialResult, hasFullResult, expiresAt}   → 응답 종료
```

## TASK-003 — SaaS 후보/setup 진입 함수 호출 여부
```
create_anonymous_diagnosis 가 호출하는 함수 전체를 직독한 결과:
  - SaaS 진입 함수 호출  없음
    (saas_setup_candidate 생성 함수, runtime_obligation 등록 함수, setup 진입 함수 — 어느 것도 호출되지 않음)
  - full_result는 anonymous_diagnosis_results 에 저장되고 응답으로 반환될 뿐,
    그 JSON을 받아 SaaS 셋업으로 넘기는 후속 함수 호출이 코드에 존재하지 않음.
  - 토큰 기반 후속 엔드포인트(/transform, /recommend-plan, /claim)는
    저장된 full_result를 "읽어 변환/추천/귀속"만 함 → SaaS 진입(셋업 생성) 함수 호출 아님.
참고: activate_documents_for_workflow 는 문서(watch_engine.document) 활성 훅이지 SaaS 셋업 진입 아님.
```

## TASK-004 — 함수 호출이 끊긴 첫 지점 1개
```
★ create_anonymous_diagnosis() 내부:
    full_result = eng["data"]  →  anonymous_diagnosis_results.insert(row)  →  return (응답)
  이 지점에서 끝난다. full_result(또는 token)를 인자로 받는 SaaS 진입 함수 호출이 그 다음에 없음.

  = Final Result JSON → SaaS 진입 = BROKEN (호출 부재)
  첫 BROKEN 지점: create_anonymous_diagnosis 의 저장·return 구간 (SaaS 진입 함수 미호출).
```

## TASK-005 — 그 뒤 분석 안 함
```
saas_setup_candidate / runtime / 진단서 단계는 분석하지 않음(범위 종료).
```

## 성공 기준 판정
```
Final Result JSON 이후 다음 함수 연결: BROKEN.
근거(함수 호출 기준): create_anonymous_diagnosis가 full_result를 저장·반환만 하고,
SaaS 진입 함수를 호출하지 않음. 진단(JSON 생성·저장)과 SaaS(셋업 진입)를 잇는 함수 호출이 코드에 없음.
```

## Boundary 준수
```
함수 호출 Connection 기준만. 숫자/COUNT/Row 수/runtime 건수 0. 입력→JSON 재분석 0. 첫 BROKEN 1개에서 종료.
읽기 전용(코드 직독). 수정 0.
```

*WO-RESULT-JSON-TO-SAAS-CONNECTION-001 — 판정 BROKEN. create_anonymous_diagnosis가 Final Result JSON을 anonymous_diagnosis_results에 저장·반환만 하고 SaaS 진입 함수를 호출하지 않음. 첫 BROKEN = 그 저장·return 구간(SaaS 진입 함수 미호출). 이후 미분석.*
