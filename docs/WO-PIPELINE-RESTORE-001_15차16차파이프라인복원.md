# WO-PIPELINE-RESTORE-001 — 15차~16차 표준 입출력 파이프라인 복원 검증

**작성일:** 2026-06-29 | **성격:** 읽기 전용 규명. Source of Truth = **15~16차 설계 문서**(현재 코드 아님). 새 Engine/Adapter/Mapper/Binding/FieldMap/Pipeline 0.
**판정: C — 원래 파이프라인 위에, 평가기·표준객체 부분이 "중간 구현/미완"으로 들어오며 일부 우회가 생겼다.** (A·B의 요소를 포함하나 최종은 C)

> 기준 문서: `2026-06-11_PIPELINE_TRACE_FWD_REV.md`(15차 정/역추적), `2026-06-15_ENGINE_4PROBLEMS_AND_ORIGINAL_PLAN_LOCATION.md`(4대 문제+v4 위치), v4 LAYER_REDESIGN(2026-06-11), `WO-INPUT-BINDING-ARCHITECTURE-001`, `WO-DIAGNOSIS-TO-OBLIGATION-PIPELINE-001`.

---

## TASK-001 — 15~16차가 정의한 입력 표준
```
입력 계약:   DiagnoseStep1Body (sector별 필드) — 15차 ①
표준화:      normalize_consumer_inp → _input_to_facility_context — 15차 ②
표준 객체:   v4 = FacilityProfile (사업장 표준, TriValue 결측=UNKNOWN)
표준 저장소: facility_profiles (영구 입력표준; WO-INPUT-BINDING-ARCHITECTURE-001)
입력 JSON:   worker_count/total_floor_area/ksic_major/project_amount/electric_capacity/has_*
```

## TASK-002 — 15~16차가 정의한 출력 표준
```
출력 계약:   anonymous_diagnosis_results / paid-diagnosis-result — 15차 ⑥
의무:        obligation_instance (WO-OBLIGATION-INSTANCE-IMPLEMENTATION-001)
check:       6W / Check Engine (WO-CHECK-PIPELINE-001)
transform:   diagnosis_transform (Refinement, 171→169 dedup)
표준 객체:   v4 = ApplicabilityCondition (조문 표준, actor 1급)
```

## TASK-003 — 15~16차 전체 파이프라인 (문서 그대로 재현)
15차 `PIPELINE_TRACE_FWD_REV` §1.1 그대로:
```
① 소비자입력   UI → DiagnoseStep1Body
② 표준화입력   normalize_consumer_inp → _input_to_facility_context → create_temp_factory → 임시 factories
③ 법령엔진     law_article → Parser → rule_candidate → compatibility_validation → executable_draft → draft_slot(binding)  [배치·정적]
④ 체크엔진     sector 필터 → draft_slot(IF) 적재 → facility_applicability_eval (factory 값 대조)  [런타임]
⑤ 정제레이어   fetch_compiler_candidates → _compiler_result_to_step1_format
⑥ 출력         anonymous_diagnosis_results → 결과화면
```
v4 LAYER_REDESIGN 레이어 대응: **B(법 번역, 배치)=③ / A(사업장 번역, 런타임)=② / C(대조, 런타임)=④, C2가 판단 유일 지점.**

## TASK-004 — 현재 코드의 생존 지점 (15차 기준 대조)
```
① 소비자입력          살아있음
② 표준화입력          살아있음 (normalize_consumer_inp + create_temp_factory 라이브)
   └ 표준저장소 적재    미연결 — ②가 임시 factories까지만 가고 facility_profiles(영구 입력표준)로 안 감
③ 법령엔진(배치)       부분 — compatibility_validation PASS 31%, binding 커버 7% (★병목1·2, GPT영역)
④ 체크엔진(C 대조)     살아있음(작동) — 단 scope 무력통과·0값매치·actor 미검증 (관대함)
⑤ 정제레이어          살아있음
⑥ 출력               살아있음
표준객체(v4)          미구축 — FacilityProfile/ApplicabilityCondition/Registry Phase0/1 미착수
obligation_instance   부분 — 테스트 1시설만(대량 미생성)
```

## TASK-005 — "문제" 구성요소: 원래 파이프라인 vs 중간 구현 구분
```
facility_profiles      = 원래 파이프라인 (v4 FacilityProfile 표준저장소). 설계 정식 구성요소. 단 ②와 미연결.
normalize_consumer_inp = 원래 파이프라인 (②). 정식. 라이브.
create_temp_factory    = 중간 구현 — 15차 ②에 "임시 factories"로 기재돼 있으나, 이는 v4 FacilityProfile
                         (영구 표준객체)이 미구축이라 그 자리에 들어온 임시 대체물. 설계의 종착(facility_profiles)이 아님.
cleanup(temp 삭제)      = 중간 구현 — 임시 factory 전제의 부산물. 영구 입력표준 설계엔 없음.
anonymous(경로)         = 원래 파이프라인 (①·⑥ 소비자 경로). 정식.
FIELD_MAP              = 중간 구현 — v4가 IF/THEN·binding "폐지"하고 객체 필드(ApplicabilityCondition)로
                         대체 설계했으나, 그 전 세대 binding 잔재가 평가기(facility_applicability_eval)에 남음.
run_facility_applicability = 중간 구현 — ④ 체크엔진의 배치 러너. factories 직접 읽음(표준객체 우회).
```

## TASK-006 — 최종 판정: **C**
```
A(살아있고 연결만 끊김)  부분 사실 — ①②④⑤⑥은 살아있음. 그러나 ②→표준저장소(facility_profiles) 연결 끊김.
B(원래 일부 미구현)      부분 사실 — v4 표준객체(FacilityProfile/ApplicabilityCondition/Registry) Phase0/1 미착수.
                         ③ PASS 31%·binding 7%도 원래 목표 미달(미완).
C(다른 구현이 우회 생성)  ★최종 — v4 표준객체가 미구축인 상태에서 그 자리에
                         create_temp_factory(임시 factories)+FIELD_MAP(구 binding 잔재)+run_facility_applicability
                         라는 중간 구현이 들어와, 입력표준(facility_profiles)과 v4 객체를 우회하는 경로가 생김.
                         "폭주가 두 번 헤집은 엔진"(15차 대표 지적)의 실체 = 이 우회.
```

## 결론 — Source of Truth는 15~16차 설계
```
1. 원래 표준 파이프라인(①~⑥ + v4 B/A/C 레이어 + FacilityProfile/ApplicabilityCondition 표준객체)은 문서로 확정되어 있다.
2. 현재 코드는 ②의 종착을 facility_profiles(영구 입력표준)가 아니라 임시 factories로 두고,
   ④를 v4 ApplicabilityCondition 객체가 아니라 구 binding(FIELD_MAP)+run_facility_applicability로 우회한다.
3. 따라서 직전 WO들에서 "끊김"으로 본 temp/cleanup은 부재가 아니라
   v4 표준객체 미구축으로 인한 중간 구현이며, 복원의 기준점은 현재 코드가 아니라 v4 설계다.
4. 입력표준 복원(②→facility_profiles)도, 출력표준(obligation/check/transform)도
   v4 표준객체(FacilityProfile/ApplicabilityCondition) 기준으로 정렬해야 한다 — 현재 코드 기준 재설계 금지.
```

## 미해결로 남기는 것 (다음 정독 대상 — 이번 WO 범위 밖)
```
docs/law-engine/ Phase 2.1→2.2→v3→v3.1→v4 정독(GPT 영역) → ③ PASS31%·binding7%가
폭주 손상인지 원래 미완인지 최종 판정. 본 WO는 15~16차 docs 기준 파이프라인 대조까지만 수행.
```

## Boundary 준수
```
읽기 전용. 코드/DB 수정·INSERT/UPDATE/DELETE 0. 새 Engine/Adapter/Mapper/Binding/FieldMap/Pipeline 0.
현재 코드 기준 재설계 금지 — 15~16차 설계 기준 대조만. obligation_instance 생성·Applicability 실행 없음.
```

*WO-PIPELINE-RESTORE-001 — 판정 C. 원래 표준(①~⑥ + v4 B/A/C + FacilityProfile/ApplicabilityCondition)은 문서로 확정. 현재 코드는 ②종착을 임시 factories로, ④를 FIELD_MAP/run_facility_applicability로 우회(v4 표준객체 미구축 탓의 중간 구현). 복원 기준 = 현재 코드 아닌 15~16차 설계.*
