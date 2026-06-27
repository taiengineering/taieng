# WO-LEGAL-ENGINE-STEP1-INTERNAL-SWITCH-001 — Step1 내부 엔진 전환 가능성 분석

**작성일:** 2026-06-27 | **성격:** 읽기 전용 분석·판정(legal_engine=GPT 소유, Claude 무수정). 프론트/URL/계약 변경 0.
**판정: B — 일부 Mapping 추가 필요 (단일 seam + 매핑 어댑터).** A 아님(이유 하단). C까지는 아님.

> 목표: 소비자 UX·버튼·URL·응답 계약 전부 유지하고, `POST /legal-engine/diagnose/step1` 내부의 **룰매칭 엔진만** Applicability 파이프로 교체 가능한지. 결론: 교체 지점은 함수 1곳(중간 블록)으로 국소화되지만, 출력형태·입력소스가 달라 **매핑 어댑터 1개 신설이 필수**.

---

## TASK-001 — 현재 Call Graph (코드 직독, 추측 0)
```
POST /legal-engine/diagnose/step1            routers/legal_engine_v510.py
  → legal_v510_svc.run_diagnose_step1_v510(supabase, body, allowed_sectors, engine_version)
     1. sector 검증 (BUILDING/MANUFACTURING/CONSTRUCTION/SPECIAL_FACILITY)
     2. factory_id 존재 검증 (factories)
     3. sector_db = _normalize_sector_db(sector)
  ┌─ 엔진(데이터+로직) ──────────────────────────────────────────────┐
  │  4. all_rules = fetch_diagnosis_rules(stage=1, sector_db, factory_id)   ← services.legal_diagnosis_rules
  │  5. inp = body.input + 상위필드 merge → _apply_construction_conditions
  │  6. eval_ctx = normalize_input(inp); eval_ctx['sector']=sector          ← services.input_normalizer
  │  7. applicable, not_applicable = _evaluate_conditions(eval_ctx, all_rules)  ← services.legal_rules ★레거시 엔진
  │  8. _classify_rules_db(applicable, triggered)  → appointment/inspection/notify/report/action 버킷
  │  9. raw_leg = {summary, appointment_required[], inspection_required[], action_required[], report_required[], ...}
  └──────────────────────────────────────────────────────────────────┘
     10. candidate_contract = to_candidate_contract(raw_leg)               ← services.leg_candidate_adapter
     11. candidate_contract['presentation'] = build_candidate_presentation(...)  ← Phase 8-B
     12. result_data = {factory_id, sector, step, engine_version, facility_context, candidate_contract, total_rules_checked, applicable_count}
     13. PERSIST: factory_diagnosis_results.insert({diagnosis_stage:1, input_data:inp, result_data, rule_count, is_latest:true})  → diagnosis_id
         (※ created_by 없음)  + diagnosis_rule_results 행 삽입(applicable별)
     14. candidate_contract['diagnosis_id'] = diagnosis_id
     15. return {status:"success", data: candidate_contract}
DB:   factories, (diagnosis rule 소스), factory_diagnosis_results, diagnosis_rule_results
JSON: candidate_contract (아래 TASK-003)
화면: diagnosis-result.html (sessionStorage 'tai_diagnosis_step1'=data, 폴백 GET /legal-engine/diagnose/{factory}/latest)
```
**엔진 = (4) fetch_diagnosis_rules + (7) _evaluate_conditions + (8) _classify_rules_db → raw_leg.** 이 블록이 유일한 교체 대상.

## TASK-002 — 입력 Payload 호환표
프론트 getFormInput → body.input. 레거시는 `_evaluate_conditions`가 **요청 payload를 직접** 평가(입력 구동). Applicability(`v4_evaluate(factory_id, save=False)`)는 **factory_id로 DB 저장 시설속성**을 평가(요청 payload 미사용).

| 입력항목 | 레거시 사용 | Applicability 사용 | 추가 Mapping |
|---|---|---|---|
| sector | ✓ 요청 | ✓ (factories.sector) | 불요 |
| worker_count / direct·subcon | ✓ 요청 | △ 시설속성 저장값 | **입력→시설 브리지** |
| has_hazardous_material / gas / chemical / boiler | ✓ 요청 | △ 시설속성 | **브리지** |
| contract_amount_eok / construction_type / tunnel | ✓ 요청 | △ 시설속성 | **브리지** |
| ksic_major / building_use / facility_type | ✓ 요청 | △ 시설속성 | **브리지** |
| total_floor_area / floor_count / electric_capacity / beds / students | ✓ 요청 | △ 시설속성 | **브리지** |

**판정: 부분 호환.** 의미 필드는 양측에 존재하나 **입력 소스가 다름**(요청 payload vs DB 시설속성). 입력 구동 동작을 보존하려면 요청 input을 시설속성으로 반영 후 evaluate하는 **브리지**가 필요(누락 아님, 소스 변환).

## TASK-003 — 기존 Step1 출력 JSON (실제 기준)
```
return = { status:"success", data: candidate_contract }
candidate_contract = {
  engine_version, mode, evaluated_at, adapter_version,
  candidates[]        // _make_candidate: candidate_id, source_type, source_bucket,
                      //   law_name, article_no, article_title, article_text,
                      //   who/when/where/what/how/why, condition_*, evidence_chain,
                      //   schedule_type, cycle_unit/int, due_days, executor_type,
                      //   qualification, penalty_summary, submit_org, submit_method, form_name/url, system_url
  metadata{ candidate_count, total_rules_checked, laws_count, source_type_counts, adapter_stats.input_buckets },
  evidence_refs[]{ law_name, count },
  presentation,       // Phase 8-B
  diagnosis_id, sector, step, factory_id, [construction_summary]
}
persist result_data = { factory_id, sector, step, engine_version, evaluated_at,
                        facility_context, candidate_contract, total_rules_checked, applicable_count }
```
요청 항목 대비: `rules`=top-level 없음(candidates[] + diagnosis_rule_results 테이블). `summary`=raw_leg 내부/metadata 카운트. `counts`=metadata. `risk`=**출력에 없음**(_risk_level 미사용). `headline`=**없음**. `diagnosis_id`=persist insert. 기타=facility_context/evidence_refs/presentation/construction_summary.

## TASK-004 — 신규 파이프 산출물과 필드 Diff
| 레거시 step1 (candidate_contract) | Applicability→Obligation→transform | 차이 |
|---|---|---|
| candidates[] (rule 기반, who/when/schedule/executor/penalty/form 풍부) | obligations[] {category,title,risk_level,description,evidence,law_name,law_article,trigger_sources,auto_schedulable} | **형태·필드 상이** |
| 버킷: appointment/inspection/action/report | 카테고리: 선임/점검/신고/교육/서류 | **분류 체계 상이(매핑 필요)** |
| schedule_type/cycle/executor/qualification/penalty/submit_org/form | (obligation 출력에 없음) | **메타 누락(저충실)** |
| metadata/evidence_refs/presentation | roi/inspection_schedule/headline/169 dedup | 용도 상이 |
| 입력 구동(요청 payload) | factory_id 구동(저장 시설속성) | **입력소스 상이** |

→ obligations → candidate_contract 재현은 **카테고리→버킷 매핑 + 필드 매핑(다수 공란)** 필요. 구조는 채울 수 있으나 schedule/executor/penalty/form 등은 **저충실(빈값)**.

## TASK-005 — 교체 대상 (딱 한 곳)
```
run_diagnose_step1_v510() 내부, TASK-001의 [엔진 블록 4~9] 만 치환:

  [현재]  all_rules = fetch_diagnosis_rules(...)
          applicable,_ = _evaluate_conditions(eval_ctx, all_rules)
          _classify_rules_db(applicable, triggered) → raw_leg

  [전환]  obligations = <Applicability 파이프>(factory_id, inp)   # 기존 엔드포인트/서비스 재사용
          raw_leg     = map_obligations_to_raw_leg(obligations)   # ★신설 매핑 어댑터(유일한 신규 코드)

이후 10~15(to_candidate_contract / presentation / persist / diagnosis_id / return) 전부 불변.
→ 새 Router/Engine/Adapter(라우팅) 없음. API·URL·응답 동일. 매핑 어댑터 1개만 추가.
```
**단일 seam이지만 `map_obligations_to_raw_leg`(+입력 브리지) 신설이 필수 → 순수 A(무매핑 1함수 스왑)는 아님.**

## TASK-006 — 교체 후 보존 검증(설계상)
```
POST URL 동일        ✓ (router 미변경)
Response 동일        ✓ {status, data: candidate_contract} 유지 (매핑이 버킷 채움)
diagnosis_id 방식    ✓ 동일 persist insert
Frontend/JS/HTML     ✓ 0
API 계약             ✓ 구조 유지
주의                 △ 저충실: schedule/executor/penalty/form 필드가 obligation 출력에 없어 공란 →
                       presentation/일정생성 등 후속 품질 저하 가능(품질 이슈, 계약 깨짐 아님)
```

## TASK-007 — 최종 판단: **B**
```
A 순수 엔진 1함수 스왑              ✗ — obligations↔raw_leg 형태·입력소스 상이, 무매핑 불가
B 일부 Mapping 추가 (선택)         ✔ — seam 1곳 + map_obligations_to_raw_leg + 입력→시설 브리지
C 구조 변경 필요                   ✗ — DB schema/router/contract/architecture 변경 불필요
```
**근거:** 교체는 `run_diagnose_step1_v510` 중간 블록 1곳으로 국소화(=A에 근접)되나, ① 출력형태(버킷 vs 카테고리) ② 입력소스(payload vs 시설속성) ③ 필드셋(누락 메타) 세 가지 때문에 **매핑 어댑터가 반드시 필요 → B**.

## 구현 핸드오프 (legal_engine=GPT 소유 → GPT 구현, Claude 미수정)
```
신설(엔진 영역): services/ 에 map_obligations_to_raw_leg(obligations) -> raw_leg
  - 카테고리→버킷: 선임→appointment / 점검→inspection / 신고→report(+notify) / 교육·서류→action
  - 필드: title|obligation_summary→what, law_name/law_article→law_name/article_no,
          risk_level→(필요시 risk 별도), 누락 메타(schedule/executor/penalty/form)는 공란 허용
  - 입력 브리지: body.input → 시설속성 반영 후 Applicability evaluate (입력 구동 보존)
교체: run_diagnose_step1_v510 [4~9] → [Applicability + 매핑]. 10~15 불변.
검증: 동일 factory로 응답 키/형태 동치 + diagnosis-result.html 무변경 렌더 + diagnosis_id 생성 확인.
```

## Boundary 준수
```
Applicability 내부 분석: YES(읽기). Frontend/URL/DataContract/DB Schema/신규 Engine/Breaking: 전부 NO.
legal_engine 코드 수정: 0 (GPT 소유 — 분석·교체지점 특정·매핑 스펙만 제공).
```

*WO-LEGAL-ENGINE-STEP1-INTERNAL-SWITCH-001 — 판정 B. 교체 seam=run_diagnose_step1_v510 중간 블록 1곳, 신규=map_obligations_to_raw_leg(+입력 브리지). 프론트/URL/계약 무변경. 구현은 GPT.*
