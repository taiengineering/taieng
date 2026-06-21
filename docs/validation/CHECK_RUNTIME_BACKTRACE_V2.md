# CHECK RUNTIME BACKTRACE V2 — 결과 생성 엔진의 정체
# WO-CHECK-RUNTIME-BACKTRACE-002

**작성일**: 2026-06-21
**목적**: 소비자 결과를 만드는 "진짜 엔진"을 소스로 확정. 법령엔진과의 연결점 발견.
**방법**: 데이터 아닌 소스 추적. 수정 0 / 삭제 0.

---

## ★★★ 가장 중요한 발견: 법령엔진→결과 연결은 이미 코드에 존재한다(플래그로 꺼져 있음)

```
결과 생성 엔진(v510)이 읽는 법령 원본은 환경변수로 3중 분기:

  services/legal_diagnosis_rules.py  fetch_diagnosis_rules():
    if TAI_USE_RUNTIME_ENGINE:  → runtime projection (법령엔진 연결!)
    elif TAI_USE_V2_ENGINE:     → master_rule_v2 (+scope/relation/threshold)
    else (기본):                → master_building_legal_rules_legacy_contaminated

= 결과 엔진을 법령엔진(v2 / runtime)에 잇는 길이 이미 3개 구현됨.
  현재 기본값은 "legacy_contaminated"(오염된 레거시).
```

---

## STEP-1: 활성 런타임 진입점 (소스)

```
routers/legal_engine.py:
  POST /legal-engine/diagnose/step1  → run_diagnose_step1_v510  ← 최신 운영 엔진
  POST /legal-engine/apply/{id}      → legal_runtime (v5.8)     ← 구버전
  POST /legal-engine/diagnose/step2,3 → "LEGACY - ISOLATED, 제거 대상"

→ 현재 결과 생성의 중심 = v5.10 (diagnose/step1).
  (프론트가 실제 호출하는 엔드포인트는 tai-admin 확인 필요 — 미확정)
```

---

## STEP-2: v5.10 런타임 흐름 (소스)

```
run_diagnose_step1_v510 (services/legal_v510_svc.py):
  입력: DiagnoseStep1Body (sector, factory_id, employee_count, contract_amount_eok 등)
  법령 fetch: fetch_diagnosis_rules(sector_db, diagnosis_stage=1)  ← 위 3중 분기
  평가: _evaluate_conditions(eval_ctx, all_rules)
  변환 체인:
    _classify_rules_db → triggered(appointment/inspection/notify/report/action)
    to_candidate_contract(raw_leg)            ← 후보 계약 변환
    build_candidate_presentation(candidates)  ← Phase 8-B 표현 레이어
  저장:
    factory_diagnosis_results.result_data = {candidate_contract, presentation, ...}
    diagnosis_rule_results (rule별 행 insert)
  출력: {status, data: candidate_contract}
```

---

## STEP-3: result_data writer 맵 (소스, 확정)

```
factory_diagnosis_results.result_data 를 쓰는 곳:
  [A] obligation_adapter_service.build_result_data   (V4, obligations 구조)
  [B] legal_runtime._save_diagnosis_result            (v5.8, rules 구조)
  [C] legal_v510_svc.run_diagnose_step1_v510          (v5.10, candidate_contract 구조) ★
  [C2] legal_v510_svc.run_diagnose_step2_v510         (v5.10 step2, _save_diagnosis_result 재사용)

→ v510도 result_data를 쓴다 = YES (STEP-3 답).
  구조가 셋 다 다름: obligations / rules / candidate_contract.
```

---

## STEP-4: 정제레이어 입력 스펙 (소스)

```
diagnosis_transform._extract_obligations 가 받는 키 (폴백 순서):
  obligations → key_obligations → mandatory_obligations → critical_obligations
  → 그 외 카테고리별 _items

문제: v510의 result_data는 "candidate_contract / presentation" 구조.
  정제레이어 폴백 키에 candidate_contract 없음.
  → v510 결과를 정제레이어가 그대로 읽으면 obligations 추출 실패 가능성.
  (단 v510 출력은 라우터가 candidate_contract를 직접 반환 →
   정제레이어 안 거치고 프론트로 갈 수도 있음. 경로 분기 확인 필요)
```

---

## STEP-5: 체크레이어1 (result_data → 체크 질문) 판정

```
질문: result_data를 "체크 질문"으로 바꾸는 코드가 있는가?
발견: build_candidate_presentation (Phase 8-B) = 후보를 표현형으로 변환.
  단 이것은 "표시용 정리"이지 "점검 질문/증빙/방법" 변환인지는
  candidate_presentation.py 본문 확인 필요(미확인).
판정: UNKNOWN (presentation 레이어 존재하나 체크 질문 변환인지 미확정).
```

---

## STEP-6: 체크레이어2 (질문→증빙→판단) 판정

```
질문: 체크 질문 → 증빙 → 판단 변환 코드가 있는가?
발견: runtime_checklist_execution = 비어있음(앞 WO).
  v510 경로에 evidence/판단 변환 코드는 안 보임.
판정: NO (또는 UNKNOWN — v510은 candidate까지, 체크 실행은 별 계통).
```

---

## STEP-7: 최종 연결도 (소스 기반)

```
[결과]  factory_diagnosis_results.result_data
   ↑ 읽기 (정제레이어 — 단 candidate_contract 구조와 키 불일치 가능)
[정제레이어]  diagnosis_transform                         YES(읽기존재)
   ↑
[체크레이어2]  질문→증빙→판단                              NO/UNKNOWN
   ↑
[체크레이어1]  result_data→체크질문 (presentation?)        UNKNOWN
   ↑
[결과 생성 엔진]  v5.10 (run_diagnose_step1_v510)          YES ★중심
   ↑ 법령 fetch (환경변수 3중 분기)
[법령 원본]
   ├─ 기본:           master_building_legal_rules_legacy_contaminated  ← 현재
   ├─ V2 플래그:       master_rule_v2 (+scope/relation/threshold)       ← 법령엔진 v2
   └─ RUNTIME 플래그:  runtime projection
        → facility_applicability→executable_draft→rule_candidate
          →law_article→runtime_metadata_resolution
        = 20세션 법령엔진(semantic_clause 계열)과 연결되는 경로 ★

★ 결론: "법령엔진→결과" 연결은 이미 코드에 3길 존재(v2/runtime/legacy).
  현재는 legacy_contaminated(기본)가 활성.
  법령엔진을 결과에 쓰려면 TAI_USE_V2_ENGINE 또는 TAI_USE_RUNTIME_ENGINE 전환.
  (실제 Railway 환경변수 현재값 = 미확인, 확인 필요)
```

---

## 두 체인이 따로 살아있다 (사장님 통찰 = 소스로 확인됨)

```
[체인 1: 법령엔진]
  semantic_clause → ... → compliance_package
  + master_rule_v2 (58,495행) / runtime_metadata_resolution
  = 법령 데이터 자산. 단 기본 결과 경로에 미연결(플래그 off).

[체인 2: 결과 생성]
  v5.10 (diagnose/step1) → result_data → 정제레이어 → 화면
  = 현재 살아서 도는 소비자 결과 엔진.
  단 기본 법령원본이 legacy_contaminated.

두 체인의 접점 = fetch_diagnosis_rules의 환경변수 플래그.
  플래그를 V2/RUNTIME로 켜면 체인1(법령엔진)이 체인2(결과)에 연결됨.
```

---

## 성공 기준 / 미확인 (정직)

```
CRB-01 활성 진입점       → v5.10 diagnose/step1 (소스상 최신). 프론트 실호출 미확인.
CRB-02 v510 흐름         → ✅ 입력/평가/변환(candidate_contract)/저장 확인
CRB-03 result_data writer→ ✅ V4/legal_runtime/v510 셋 다 씀
CRB-04 정제레이어 입력   → ✅ 단 v510 candidate_contract와 키 불일치 가능성 발견
CRB-05 체크레이어1       → UNKNOWN (presentation이 체크질문 변환인지 미확정)
CRB-06 체크레이어2       → NO/UNKNOWN
CRB-07 연결도            → ✅ (법령엔진 연결 3길 = 플래그 발견)

미확인(다음):
  - Railway 환경변수 TAI_USE_V2_ENGINE / TAI_USE_RUNTIME_ENGINE 현재값
  - candidate_presentation.py 본문 (체크 질문 변환 여부)
  - 프론트(tai-admin)가 실제 호출하는 엔드포인트
  - v510 candidate_contract vs 정제레이어 키 불일치 실제 영향
```

---

## 완료 문장

```
소비자 결과를 만드는 진짜 엔진은 v5.10(diagnose/step1)이며,
이 엔진이 읽는 법령 원본은 환경변수 플래그로 3분기(legacy / master_rule_v2 / runtime projection)된다.
법령엔진(master_rule_v2 · runtime_metadata_resolution · facility_applicability 계열)을
결과에 연결하는 경로는 이미 코드에 존재하나, 현재 기본값(legacy_contaminated)으로
꺼져 있다. 두 체인은 fetch_diagnosis_rules의 플래그에서 만난다.
수정 없이 소스로 확인하였다.
```
