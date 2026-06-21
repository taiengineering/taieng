# RESULT BACKTRACE — 소스 기반 정정 V2
# WO-RESULT-BACKTRACE-001 (정정: 연결점은 한 곳이 아님)

**작성일**: 2026-06-21
**계기**: V1에서 "소비자 결과 연결점 = V4 한 곳"이라 단정한 것이 오류.
        사장님 지적 → 소스(데이터 아님)로 읽기/쓰기 경로 전수 재추적.
**방법**: 데이터 카운트 금지(목업). 소스 코드의 read/write 경로만 추적.
**수정 0 / 삭제 0**.

---

## ★★★ 정정된 핵심 결론

```
소비자 결과(factory_diagnosis_results.result_data)를 만드는 경로는 한 곳이 아니다.
여러 세대의 진단 엔진이 공존하며 같은 result_data 테이블에 쓴다.
정제레이어는 누가 썼든 그 result_data를 읽어 화면에 준다.
```

---

## 읽기 경로 (소비자 화면이 호출, 확정)

```
routers/diagnosis_transform.py (정제레이어, BE-08, 읽기 전용):
  GET /diagnosis/transform/{diagnosis_id}
  GET /diagnosis/transform/latest/{factory_id}
  → factory_diagnosis_results.result_data(JSONB) 읽음
  → _extract_obligations: obligations/key_obligations/mandatory_obligations/
    critical_obligations + 카테고리별 _items 까지 폴백 체인
    = "여러 형태의 result_data"를 받아들이도록 설계됨
       (= 쓰기 경로가 여러 개임을 코드가 전제)
  권한: created_by 기준. 엔진 직접 호출 안 함(읽기 전용).
```

---

## 쓰기 경로 (result_data 생성, 소스 확인 — 최소 4세대 공존)

```
[A] V4 어댑터
    routers/obligation_adapter.py POST /{factory_id}/persist
    → obligation_adapter_service.build_result_data
    → 입력: applicability_conditions (= appendix_condition 기반)
    소스 주석: "안전관리자 선임 7건 파일럿". source=V4_OBLIGATION_ADAPTER_v1.
    근로자수 1개만 비교하는 파일럿.

[B] legal_runtime (v5.8.0)
    services/legal_runtime.py _save_diagnosis_result
    routers/legal_engine.py POST /legal-engine/apply/{factory_id}
    → 입력: master_building_legal_rules (sector별 is_active)
    → factory_diagnosis_results.result_data + factories.legal_result_json
      + legal_applications upsert 까지 3중 저장.
    rule_code(FIREACT/OSHRULE 형식) 사용 → diagnosis_rule_results 코드체계와 일치.

[C] v5.10 Canonical Runtime (최신)
    services/legal_v510_svc.run_diagnose_step1_v510
    routers/legal_engine.py POST /legal-engine/diagnose/step1
    소스 주석: "v510 Canonical Runtime: adapter + enrichment + obligation_contract"

[D] LEGACY (구형, 격리/제거 대상)
    routers/legal_engine.py POST /legal-engine/diagnose/step2, step3
    소스 주석: "LEGACY - ISOLATED: 구형 엔진 경로. runtime 전환 완료 후 제거 대상"
```

---

## 법령 원본 테이블도 여러 벌 (소스 확인)

```
[원본 1] law_master → semantic_clause → executable_draft → draft_slot
         → facility_applicability → task_candidate → compliance_package
         = 20세션 작업한 법령엔진. 소비자 결과로 안 감.
         (law_master는 semantic_clause_service / law_to_rules / collect_* 가 사용)

[원본 2] law_master → law_appendix → appendix_condition
         → applicability_conditions → V4 어댑터 [경로 A]
         (law_appendix는 applicability_api.py 1곳만 사용)

[원본 3] master_building_legal_rules → legal_runtime [경로 B]

→ 법령 원본이 최소 3벌. 소비자 결과 경로(A/B/C)와
  법령엔진 경로(원본1)가 서로 다른 테이블에서 출발.
```

---

## 역방향 연결지도 (소스 기반, 정정판)

```
[소비자 화면]
   ↓ 읽기 (확정)
diagnosis_transform (정제레이어, 읽기전용)
   ↓ 읽는 대상
factory_diagnosis_results.result_data
   ↑ 쓰기 (4세대 공존, 모두 YES로 존재)
   ├─ [A] V4 어댑터 ← applicability_conditions(선임 파일럿)
   ├─ [B] legal_runtime ← master_building_legal_rules
   ├─ [C] v5.10 Canonical ← legal_v510_svc
   └─ [D] LEGACY step2/3 (격리)
   ↑
compliance_package (법령엔진, 원본1)
   = 위 어느 쓰기 경로(A/B/C/D)도 compliance_package를 안 씀. NO.

끊김 지점 (정정):
  "한 곳"이 아니라, 소비자 결과 쓰기 경로가 4세대 공존하고,
  그 중 어느 것도 20세션 법령엔진(compliance_package)을 입력으로 쓰지 않는다.
  법령엔진과 소비자결과는 출발 법령 테이블부터 분리.
```

---

## V1 오류 정정 명시

```
V1 주장: "소비자 결과 연결점 = V4 한 곳."
정정: 틀림. V4는 4세대 쓰기 경로 중 하나일 뿐.
원인: obligation_adapter 주석만 보고 "→정제레이어로 간다"를 끝점으로 단정.
      정제레이어가 실제 무엇을 읽는지, 다른 쓰기 경로(legal_runtime/v510/legacy)가
      있는지 확인 전 결론냄.
교훈: 읽기 경로(정제레이어)부터 역으로, 그 테이블에 쓰는 경로를 전수 확인해야 함.
```

---

## 아직 끝까지 안 본 것 (정직)

```
- legal_v510_svc 내부 (경로 C가 무슨 법령 테이블을 쓰는지)
- anonymous_diagnosis_results(익명) 쓰기 경로 — 별도 추적 필요
- 4세대 중 "현재 운영에서 실제 호출되는 것"이 무엇인지
  (라우터는 다 존재하나, 프론트가 어느 엔드포인트를 부르는지는 tai-admin 확인 필요)
```

---

## 완료 문장 (정정판)

```
소비자 결과 화면을 읽기 경로(정제레이어)부터 소스로 역추적한 결과,
result_data를 쓰는 경로가 한 곳이 아니라 4세대(V4/legal_runtime/v5.10/legacy)
공존함을 확인하였다. 어느 경로도 20세션 법령엔진(compliance_package)을
입력으로 쓰지 않으며, 법령 원본 테이블부터 분리되어 있다.
V1의 "한 곳" 단정을 소스 근거로 정정한다. 수정 없이 기록하였다.
```
