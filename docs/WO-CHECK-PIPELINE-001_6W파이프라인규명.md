# WO-CHECK-PIPELINE-001 — Check Engine → 6W Pipeline 실제 호출경로 규명보고서

**작성일:** 2026-06-26 | **상태:** 완료 (읽기 전용 — 코드/DB/Commit/PR 0)
**방법:** 실제 커밋 코드 직독 + 전역 심볼 검색. 추측·"아마"·"같다" 0.

> 성공기준: 6W가 어디서 생성되는지(또는 생성되지 않는지)를 실제 호출경로로 증명.

---

## Boundary Check

```
Applicability 내부(읽기전용)  YES     Boundary 변경  NO     Data Contract 변경  NO
Breaking  NO     DDL/Migration  NO     코드수정  NO     Git Commit  NO
```

---

## TASK-001 — engine/six_w_heuristic.py 실존 여부

```
파일 존재    O  (engine/six_w_heuristic.py, 3,157B)
클래스     없음
함수       extract_six_w(tok_json, source_text) -> dict   (public)
           _meaningful(tok_json) -> list                  (private)
Export     extract_six_w
import     engine.morpheme.PUNCT_TAGS
동작       Kiwi 토큰 + 원문 정규식 휴리스틱 (LLM 없음)
출력 키    executor/recipient/what/when_value/where_value/how/condition
docstring  "명세 §5.6: 첫 매칭만, 없으면 NULL. runner에서 NULL만 채움"
```

---

## TASK-002 — Call Graph 역추적

```
extract_six_w()                         [engine/six_w_heuristic.py]
  ↑ 호출
 extract_six_w_for_candidate(candidate, supabase)   [services/trigger_six_w_service.py]
   (who=executor∨"사업주", where=_TRIGGER_WHERE_FALLBACK, why="Trigger:{code}", completeness)
  ↑ 호출
 routers/trigger_diagnosis.py :: evaluate_factory()
   POST /trigger-diagnosis/{factory_id}/evaluate   ← router_registry/diagnosis.py 등록됨(reachable)

[별도] scripts/track_e_phase2_run.py → extract_six_w  (일회성 스크립트, 런타임 아님)
```

---

## TASK-003 — Repository 전역 검색

```
extract_six_w   사용 4곳:
  engine/six_w_heuristic.py        (정의)
  routers/trigger_diagnosis.py     (라우터 — 런타임 호출)
  services/trigger_six_w_service.py(서비스 래퍼)
  scripts/track_e_phase2_run.py    (스크립트)
six_w_heuristic 사용 2곳: trigger_six_w_service.py, track_e_phase2_run.py

Dead Code 여부: 아니오(NOT dead). 등록된 라우터(trigger_diagnosis)가 런타임 호출.

metadata_resolution / runtime_metadata_resolution:
  → 6W와 무관한 별도 서브시스템(runtime projection).
    legal_runtime_fetch.py / diagnosis_runtime_projection.py / rule_candidate_projection.py /
    leg_parent_trace_resolver.py 등. six_w_heuristic과 연결 없음.
```

---

## TASK-004 — Trigger Pipeline 비교 (분기점 증명)

```
① POST /trigger-diagnosis/{factory_id}/evaluate   [routers/trigger_diagnosis.py]
   generate_trigger_codes
   → generate_obligation_candidates
   → evaluate_candidates_batch
   → extract_six_w_for_candidate()          ←←← 6W 호출 (Step 4)
   → _build_output_obligation({..., six_w, law_basis="", ...})
   → JSON 반환 (persist 없음)

② POST /obligation-adapter/from-instances/{factory_id}   [routers/obligation_adapter.py]  (우리 171)
   obligation_instances_to_trigger_candidates   [obligation_instance_adapter = Glue]
   → build_obligations_from_trigger_candidates  [obligation_adapter_service = Adapter]
   → _build_obligation_from_candidate()         ←←← 6W 호출 없음
   → JSON 반환

③ POST /obligation-adapter/{factory_id}/persist   [routers/obligation_adapter.py]  (운영 저장)
   V4 evaluate → build_obligations_from_v4 → build_result_data
   → factory_diagnosis_results 저장 → 정제레이어 → HTML       ←←← 6W 호출 없음

분기점: "후보 → 의무" 단계.
  ①은 trigger_six_w_service를 경유(6W 포함).
  ②③는 obligation_adapter_service를 경유(6W 없음).
  즉 같은 candidate를 서로 다른 서비스로 보내면서 갈라진다.
```

---

## TASK-005 — 현재 Runtime Flow (가정 없음)

```
[운영 진단 = 사용자 화면까지 도달하는 경로]
Router(obligation_adapter /persist)
  → Service(applicability V4 evaluate → obligation_adapter_service)
  → result_data → Router(diagnosis_transform = 정제레이어) → HTML
  ∴ 6W 엔진이 이 흐름에 없다.

[6W가 살아있는 경로 — 별도 엔드포인트]
Router(trigger_diagnosis /evaluate)
  → Service(trigger_six_w_service.extract_six_w_for_candidate)
  → Engine(six_w_heuristic.extract_six_w)
  → JSON 출력 (factory_diagnosis_results 미저장 → 정제레이어/HTML 미연결)
```

---

## TASK-006 — 설계서와 비교

```
WO-PLAN-001 / WO-CHECK-001 / WO-ARCH-001:
  → taieng·tai-api 두 repo 검색 결과 0건. 커밋된 소스에 존재하지 않음.
    (따라서 해당 문서 대 코드 직접 diff는 커밋 소스 기준으로 수행 불가.)

설계 의도(코드 docstring에 인코딩됨):
  routers/trigger_diagnosis.py 첫줄: "입력 → Trigger Generator → Obligation Generator
  → Applicability Adapter → 6W → 최종 의무 출력"
  → 이 설계 파이프라인은 /trigger-diagnosis/{factory_id}/evaluate에 그대로 구현됨.

차이점 / 우회된 단계:
  설계(trigger_diagnosis)는 6W를 포함하지만,
  운영·저장 경로(obligation-adapter → factory_diagnosis_results → 정제레이어 → HTML)는 6W를 우회.
  6W 출력(trigger-diagnosis)은 persist가 없어 다운스트림(정제레이어/HTML)에 소비되지 않는다.
```

---

## TASK-007 — 최종 판정

```
■ 판정: B
   6W Engine은 존재하지만 (운영) Trigger 경로에서 호출되지 않는다.

코드 근거:
  - A(설계대로 동작) 거짓: 운영 진단 경로(obligation-adapter)의 _build_obligation_from_candidate에
    extract_six_w 호출 없음.
  - C(Dead Code) 거짓: routers/trigger_diagnosis.py가 extract_six_w_for_candidate를 호출하고,
    해당 라우터는 router_registry/diagnosis.py에 등록됨(reachable).
  - D(제거됨) 거짓: engine/six_w_heuristic.py(3,157B) 및 호출 체인 모두 main에 존재.
  - B 참: 6W는 /trigger-diagnosis/{factory_id}/evaluate에서만 살아있고,
    우리 171이 타는 /obligation-adapter/from-instances 및 저장 경로(/persist)→정제레이어→HTML에서에는
    호출되지 않는다.

파일명·함수명 증거:
  호출 O : routers/trigger_diagnosis.py::evaluate_factory → services/trigger_six_w_service.py::extract_six_w_for_candidate → engine/six_w_heuristic.py::extract_six_w
  호출 X : routers/obligation_adapter.py::adapt_from_obligation_instances / persist_obligations → services/obligation_adapter_service.py::_build_obligation_from_candidate (6W 없음)
```

---

## 핵심 결론 (한 줄)

```
6W 엔진은 Dead도 제거도 아니다. 단, 별도 엔드포인트(/trigger-diagnosis/evaluate)에서만 호출되며
그 출력은 persist되지 않는다. 운영 진단(obligation-adapter → 정제레이어 → HTML, 우리 171)은
6W를 호출하지 않는다. → 판정 B.
```

---

*WO-CHECK-PIPELINE-001 완료. 가설 없이 호출경로로 증명. 판정 B.*
