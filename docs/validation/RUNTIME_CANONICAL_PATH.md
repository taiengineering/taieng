# RUNTIME CANONICAL PATH — 운영 경로 고정 + 비운영 격리
# WO-RUNTIME-CANONICAL-PATH-001

**작성일**: 2026-06-21
**목적**: 소비자 결과 생성 경로를 compiler_core로 Canonical 고정, 나머지 격리.
**원칙**: 삭제 금지 / 기능제거 금지 / compiler_core·law_sector_mapping·result_data 수정 금지.
**격리 방식 결정**: 코드 변경 없는 **문서화 격리(deprecated 명세)**.
  (이유: 비운영 라우터에 정상 엔드포인트가 섞여 있을 수 있어 route disable은 위험.
   오픈 전 회귀 방지 위해 검증 WO 단계에선 문서화가 안전한 격리.)

---

## ★ Canonical Path (고정)

```
[실행버튼 / 소비자 무료·유료 진단]
  POST /diagnosis/factory-test-run         (routers.diagnosis_factory_test)
   또는 POST /diagnosis/run (UI 무료진단, 동일 엔진)
    → run_step1_via_compiler               (services.diagnosis_integrated_svc)
    → run_anonymous_diagnosis              (services.anonymous_factory_service)
       = compiler_core (temp-factory lifecycle)
       법령엔진 직접: facility_applicability / executable_draft /
         draft_slot / law_article / law_master (+ sector filter law_sector_mapping)
    → anonymous_diagnosis_results.full_result 저장
  GET /diagnosis/result/{token}            (routers.diagnosis_result_web, 읽기/정제)
  GET /diagnosis/transform/...             (routers.diagnosis_transform, 정제)
    → 결과 화면

Canonical 서명(스모크 기준): engine_version = "v3.0-compiler-core-anonymous"
  factory-test 경로는 "v3.0-compiler-core-factory-test"
router_registry 등록: router_registry/diagnosis.py (정상)
```

---

## 비운영 경로 목록 (격리 대상)

```
[1] V4 Adapter
    라우터: routers.obligation_adapter  (router_registry/diagnosis.py 등록됨)
    엔드포인트: /obligation-adapter/{factory_id} (+/persist)
    서비스: services.obligation_adapter_service
    입력원: applicability_conditions (안전관리자 선임 7건 파일럿)
    저장: factory_diagnosis_results.result_data (source=V4_ADAPTER_v1)
    프론트 호출(tai-admin): 검색상 미발견

[2] legal_runtime (v5.8)
    라우터: routers.legal_engine  POST /legal-engine/apply/{factory_id}
            (router_registry/legal_engine.py 등록됨)
    서비스: services.legal_runtime
    입력원: master_building_legal_rules
    저장: factory_diagnosis_results + factories.legal_result_json + legal_applications
    프론트 호출: 검색상 미발견 (문서/HTML만)

[3] v510
    라우터: routers.legal_engine  POST /legal-engine/diagnose/step1
    서비스: services.legal_v510_svc
    입력원: fetch_diagnosis_rules (플래그 3분기: v2/runtime/legacy)
    저장: factory_diagnosis_results + diagnosis_rule_results
    프론트 호출: 검색상 미발견

[4] legacy step2/3
    라우터: routers.legal_engine  POST /legal-engine/diagnose/step2, step3
    소스 주석: "LEGACY - ISOLATED. runtime 전환 완료 후 제거 대상"
    프론트 호출: 미발견
```

---

## 운영 호출 가능 여부 (수행 4)

```
              router등록  엔드포인트열림  프론트호출(tai-admin)  실행버튼사용
Canonical     YES        YES            (결과페이지 호출)      YES ★
V4 Adapter    YES        YES            미발견                 NO
legal_runtime YES        YES            미발견                 NO
v510          YES        YES            미발견                 NO
legacy        YES        YES            미발견                 NO

★ 비운영 4경로 모두 라우터에 등록되어 외부 호출은 가능하나,
  실행버튼(소비자 결과 경로)은 어느 것도 사용하지 않음.
  = 운영 결과는 compiler_core만 생성. 나머지는 "열려있으나 미사용".
```

---

## 격리 방식 결정 (수행 5)

```
선택: [문서화 격리] (코드 변경 0)
  - deprecated 명세를 본 문서로 고정.
  - 각 비운영 라우터/서비스 상단에 deprecated 주석 추가는
    "후속 별도 커밋"으로 분리(이 검증 WO에선 명세만).

배제한 방식과 이유:
  - route disable: legal_engine 라우터에 정상 엔드포인트 동반 가능 → 위험.
  - feature flag OFF: compiler_core 무관하나 회귀 테스트 부담 → 오픈 전 보류.
  - 삭제: 금지(WO 명시).

후속 실행 WO(별도): 비운영 라우터 4개에 @deprecated 주석 +
  router_registry에서 분리 그룹(isolated)로 이동 검토.
  단 compiler_core/diagnosis_result_web/diagnosis_transform/diagnosis_factory_test는
  절대 미변경.
```

---

## 스모크 테스트 (수행 7, 격리 전 기준선)

```
GET /diagnosis/result/16cea20b... (건설 프로브):
  status: success
  engine_version: "v3.0-compiler-core-anonymous"   ← compiler_core 서명 정상
  sector: CONSTRUCTION
  applicable_count: 138
  first rule_type: APPOINTMENT_TASK_CANDIDATE       ← 정상 유지
  first remarks: "특정소방대상물의 소방안전관리"      ← 정상 유지

= 코드 수정 0이므로 결과 동일. compiler_core 경로 정상 가동 확인.
  격리 실행 후에도 이 값이 동일해야 함(회귀 판정 기준선).
```

---

## 성공 기준

```
- Canonical Path 문서화        → ✅
- 비운영 경로 목록화           → ✅ (V4/legal_runtime/v510/legacy)
- 격리 방식 확정               → ✅ (문서화 격리, 코드변경 0)
- 실행버튼=compiler_core만 사용 → ✅ (소스+router_registry 확인)
- 기존 결과페이지 정상 동작     → ✅ (스모크 기준선 확보)
- 수정 0건                     → ✅ (이 WO는 문서만, 코드 0)
```

---

## 완료 문장

```
실제 소비자 결과 생성 경로를 compiler_core(run_anonymous_diagnosis)로
Canonical 지정하고, V4/legal_runtime/v510/legacy 경로를 운영 경로에서
격리(문서화 격리)하였다. 네 경로 모두 라우터에 등록되어 호출은 가능하나
실행버튼·결과페이지는 compiler_core만 사용함을 소스와 router_registry로
확인하였다. 코드 수정 0건이며, compiler_core 서명
(engine_version=v3.0-compiler-core-anonymous)으로 회귀 기준선을 기록했다.
```

---

## 다음 (순서)

```
1. (선택) 후속 실행 WO: 비운영 라우터 4개 @deprecated 주석 (코드 최소 수정).
2. WO-LAW-SECTOR-MAPPING-UNKNOWN-001:
   소방 NFPC·전기설비 법령의 law_sector_mapping sector 등록 (GPT 법령해석 인계).
   = CONDITIONAL PASS → PASS 전환 핵심.
3. 결과페이지 재검증: 정화 후 소방 오적용 비율(현 건설92%/산업82%) 감소 확인.
```
