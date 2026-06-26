# WO-CHECK-PIPELINE-VERIFY-001 — 6W Engine 운영 경로 누락 검증보고서

**작성일:** 2026-06-26 | **상태:** 완료 (읽기 전용 — 코드/DB/Push 0)
**방법:** 커밋 코드 직독 + Call Graph + Commit History. 추측·"아마"·"같다" 0.

> 목적: 6W Engine이 존재하는데 왜 현재 171 경로에서는 실행되지 않는가를 코드로 증명.

---

## Boundary Check

```
Applicability 내부 작업  NO     Check Engine 분석  YES (읽기전용)
Boundary/Contract 변경  NO     Breaking  NO     코드수정/Push  NO
```

---

## TASK-001 — Trigger-Diagnosis Pipeline 전체 추적 (6W 포함 경로)

```
Router   routers/trigger_diagnosis.py :: evaluate_factory()
         POST /trigger-diagnosis/{factory_id}/evaluate
  ↓ Step1  services/trigger_generator.py :: generate_trigger_codes()
  ↓ Step2  services/trigger_obligation_generator.py :: generate_obligation_candidates()
  ↓ Step3  services/trigger_applicability_adapter.py :: evaluate_candidates_batch()
  ↓ Step4  services/trigger_six_w_service.py :: extract_six_w_for_candidate()   ← 6W
              ↓ engine/six_w_heuristic.py :: extract_six_w()
  ↓ Step5  _build_output_obligation({obligation, law_basis="", six_w, source_article_id})
  ↓        JSON 반환 (factory_diagnosis_results 저장 없음)
```

---

## TASK-002 — Obligation Pipeline 전체 추적 (우리 171 경로)

```
Router   routers/obligation_adapter.py :: adapt_from_obligation_instances()
         POST /obligation-adapter/from-instances/{factory_id}
  ↓ Glue   services/obligation_instance_adapter.py :: obligation_instances_to_trigger_candidates()
              (obligation_instance + semantic_clause JOIN → candidates)
  ↓ Adapter services/obligation_adapter_service.py :: build_obligations_from_trigger_candidates()
              ↓ _build_obligation_from_candidate()        ← 6W 없음
  ↓        JSON 반환

[운영·저장 경로]
Router   routers/obligation_adapter.py :: persist_obligations()
         POST /obligation-adapter/{factory_id}/persist
  ↓ V4    routers/applicability_api.py :: evaluate()
  ↓ Adapter obligation_adapter_service.py :: build_obligations_from_v4() → build_result_data()  ← 6W 없음
  ↓        factory_diagnosis_results 저장 → 정제레이어(diagnosis_transform) → HTML
```

---

## TASK-003 — 두 Pipeline Diff

```
단계 | Trigger Diagnosis (/trigger-diagnosis/evaluate) | Obligation Adapter (/from-instances, /persist)
-----|------------------------------------------------|-----------------------------------------------
Step1| generate_trigger_codes                          | (from-instances) obligation_instance 조회
Step2| generate_obligation_candidates                  | semantic_clause JOIN → candidates
Step3| evaluate_candidates_batch                       | build_obligations_from_trigger_candidates
Step4| extract_six_w_for_candidate()  ← 6W ★          | _build_obligation_from_candidate()  (6W 없음)
Step5| _build_output_obligation (six_w 포함) / JSON     | JSON / (persist는 factory_diagnosis_results)

6W가 빠지는 지점: "후보 → 의무" 단계(Step4).
  Trigger는 trigger_six_w_service를 경유(6W O), Obligation은 obligation_adapter_service를 경유(6W X).
```

---

## TASK-004 — Git History (신규/legacy/운영 판별)

```
[obligation_adapter 라인 = 운영]
  06-19 07:59  obligation_adapter_service v1.0.0 (V4 verdict→obligations 변환, B안)
  06-19 08:01  obligation_adapter router v1.0.0 (GET /{factory_id})
  06-19 08:02  register obligation_adapter in diagnosis router group
  06-19 12:27  obligation_adapter_service v1.1.0 (build_result_data, factory_diagnosis_results 스키마)
  06-19 12:28  obligation_adapter router v1.1.0 (POST /persist, "Track A 마지막 배선")
  06-19 12:29  diagnosis_transform v1.0.2 (정제레이어가 factory_diagnosis_results 읽음)

[trigger_diagnosis 라인 = 6W 포함, 병렬 E2E]
  06-23 00:10  CURSOR-TASK-001 trigger_generator + trigger_obligation_generator (six_w_heuristic 무수정)
  06-23 00:31  CURSOR-TASK-002 run-trigger → obligation_adapter_service 연결 (6W 없음)
  06-23 01:28  IMPLEMENT-001 TASK-003~006: trigger_applicability_adapter + trigger_six_w_service(TASK-005)
               + trigger_diagnosis(TASK-006, /evaluate). ISSUE-006 "law_basis 빈문자열 → JOIN 보강 Post-MVP"
  06-23 01:28  router_registry에 trigger_diagnosis 등록 (ISSUE-005 해결)

[Glue 라인 = 우리 171, 운영 어댑터 재사용]
  06-25 09:44  CURSOR-TASK-001 obligation_instance Glue → 기존 Adapter 연결.
               POST /from-instances. "obligation_adapter_service 무수정" (6W 없는 어댑터 재사용)

판독: trigger_diagnosis는 06-23 구현된 병렬 E2E(6W 포함, persist 없음, ISSUE-006 미완).
      06-25 우리 171 작업은 이 E2E를 쓰지 않고 기존 obligation_adapter_service를 재사용하도록 배선됨.
      즉 6W 서비스는 trigger_diagnosis 라인에만 연결되었고, 운영 obligation_adapter 라인에는 애초부터 미배선.
```

---

## TASK-005 — Router Reachability (main.py)

```
main.py v6.0.2 :: _load_all_modules()
  → 10개 그룹 ROUTERS import → load_module_group(app, name, routers)  (= include_router, Safe Loading)

/trigger-diagnosis  → router_registry/diagnosis.py ["routers.trigger_diagnosis"]   → 등록 O (reachable)
/from-instances     → router_registry/diagnosis.py ["routers.obligation_adapter"]   → 등록 O (reachable)
/run-track-a        → router_registry/legal_engine.py ["routers.check_adapter_api"] → 등록 O (reachable)

∴ 세 엔드포인트 모두 등록됨. "등록 여부"는 운영 여부와 별개(등록되어도 persist/소비 없으면 운영 흐름 아님).
```

---

## TASK-006 — 현재 운영 Pipeline 확정

```
사용 Endpoint   POST /obligation-adapter/{factory_id}/persist  (사용자 화면 도달 유일 저장 경로)
  ↓ Service     applicability_api.evaluate (V4) + obligation_adapter_service
  ↓ Adapter     build_obligations_from_v4 → build_result_data
  ↓ Store       factory_diagnosis_results (is_latest)
  ↓ 정제레이어   diagnosis_transform → HTML
6W 호출 여부   NO

(참고: /from-instances는 171을 JSON으로 반환하나 persist 없음 → 정제레이어/HTML 미도달. 역시 6W 없음.)
```

---

## TASK-007 — 최종 판정

```
■ 판정: B — 운영 경로가 obligation_adapter

근거 3종:
  (1) Router      : 사용자 화면으로 가는 유일한 persist→정제레이어 경로는 obligation_adapter /persist.
                    trigger_diagnosis /evaluate는 등록되었으나 persist 없음.
  (2) Call Graph  : 운영 obligation_adapter 라인(/persist, /from-instances)은 obligation_adapter_service 경유
                    → _build_obligation_from_candidate / _build_obligation 에 extract_six_w 호출 없음.
                    6W는 trigger_six_w_service(trigger_diagnosis 전용)에만 연결.
  (3) Commit      : 운영 라인(obligation_adapter)은 06-19 구축(6W 이전). 6W 라인(trigger_diagnosis)은
                    06-23 병렬 E2E(persist 없음, ISSUE-006 미완). 06-25 171 작업은 6W E2E를 쓰지 않고
                    obligation_adapter_service 재사용("무수정").

보강 판정(다른 옵션 배제):
  A(운영=trigger_diagnosis) 거짓: trigger_diagnosis는 persist 없음, 사용자 화면 미도달.
  C(둘 다 운영) 거짓: factory_diagnosis_results를 쓰는 건 obligation_adapter뿐.
  D(trigger_diagnosis legacy) 부분참: 등록되어 reachable이므로 "제거/legacy"는 아니며,
     정확히는 "등록되었으나 persist·소비 없는 병렬 E2E"(운영 흐름 미편입). → 주판정 B.
```

---

## 왜 6W가 운영 경로에서 빠졌는가 (핵심)

```
6W는 제거되지 않았다. 다만 운영 라인(obligation_adapter)이 6W 라인(trigger_diagnosis)보다 먼저(06-19) 만들어졌고,
171/obligation_instance 작업(06-25)이 6W E2E를 쓰지 않고 기존 obligation_adapter_service를 재사용하도록 배선되면서,
6W 서비스(trigger_six_w_service)는 운영 라인에 애초부터 배선되지 않았다. ISSUE-006(law_basis Post-MVP)가
trigger_diagnosis E2E가 미완·비운영 택임을 보여준다. → 판정 B.
```

---

*WO-CHECK-PIPELINE-VERIFY-001 완료. Router·Call Graph·Commit 3증거로 판정 B. 운영=obligation_adapter, 6W 미호출.*
