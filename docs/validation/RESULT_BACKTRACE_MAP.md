# RESULT BACKTRACE MAP
# WO-RESULT-BACKTRACE-001

**작성일**: 2026-06-21
**목적**: 소비자 결과 화면 기준 역추적으로 실제 데이터 연결·단절 지점 특정.
**금지 준수**: 수정 0 / 삭제 0. 추적·Reading·YES/NO/UNKNOWN만.
**방법**: 결과 → 부모 → 부모 역방향. (순방향 20테이블 추적 대신)

---

## ★★★ 역추적 핵심 결론 (먼저)

```
소비자가 보는 결과는 "법령엔진 파이프라인"에서 오지 않는다.
별도의 작은 어댑터 계통(applicability_conditions 14건 → V4 어댑터)에서 온다.

= "체크엔진이 끊긴 것"이 아니라,
  소비자 결과와 법령엔진이 애초에 다른 두 시스템이다.
```

---

## STEP-1: 결과 객체 식별 (RESULT_OBJECT_MAP)

```
소비자가 보는 최종 결과 테이블:
  factory_diagnosis_results  (4건, factory 3개) — 로그인 사업장 결과
  anonymous_diagnosis_results (40건) — 익명/공개 진단 결과

구조: 결과를 정규화 테이블이 아니라 JSONB 한 덩어리로 저장.
  factory_diagnosis_results.result_data (jsonb)
  anonymous_diagnosis_results.full_result / partial_result (jsonb)
연결키: factory_diagnosis_results.factory_id → factories
```

---

## STEP-2: 결과 1건 추적 (RESULT_SAMPLE_TRACE)

```
가장 최근 결과 1건 (id 216fd7b0, factory e9c56af6=화성제2공장, 6/19):
  result_data 내용:
    "source": "V4_ADAPTER_v1"        ← ★ 출처 명시
    "verdict": "REQUIRED"
    "rule_count": 8
    "obligations": [8개]
      - 안전관리자 1명 선임 (산안법 시행령 별표3)
      - 관리감독자 지정 (제16조)
      - 정기/채용시/변경시 안전보건교육 (제29조)
      - 일반건강진단 (제129조)
      - 위험성평가 (제36조)
      - 경보용 설비 설치 (산안기준규칙 제19조)

★ 이 의무들은 "완성된 문장 + 정확한 법령출처"다.
  법령엔진 task_candidate의 "보고하여야 한다"(추상동사)와 전혀 다름.
```

---

## STEP-3: 직전 부모 찾기 (코드 + 데이터)

```
result_data.source = "V4_ADAPTER_v1" → 코드 추적:
  services/obligation_adapter_service.py (주석 명시):
    "B안 어댑터: V4 verdict → result_data.obligations 변환"
    "V4(applicability_api/applicability_condition_service) 판정만"
    "이 어댑터는 그 사이 변환만"

  build_obligations_from_v4(v4_result, conditions_by_id):
    → applicability_conditions 테이블의
      law_name / appendix_no / action_text / action_type 사용.

부모 체인 (역방향):
  factory_diagnosis_results.result_data
   ← obligation_adapter_service (변환)         YES
   ← V4 evaluate (applicability_condition_svc) YES
   ← applicability_conditions (14건, 법령 3종)  YES

판정: 소비자 결과의 부모 = applicability_conditions (YES, 명확).
```

---

## STEP-4: 체크레이어2 추적 (CHECK_LAYER2)

```
질문: 체크항목이 실제 실행 결과를 갖는가?
  runtime_checklist_execution = 0건
  → 실행 결과 없음.
판정: NO.

단 이 계통(runtime_checklist)은 소비자 결과 경로가 아님.
  소비자 결과는 V4 어댑터 경로이지 checklist 경로가 아님.
  → checklist 계통은 소비자 결과와 무관(별도 미가동 계통).
```

---

## STEP-5: 체크레이어1 추적 (CHECK_LAYER1)

```
질문: 법령 의무가 체크 질문으로 변환되었는가?
  checklist_item_candidate = 802 (존재)
  checklist_coverage_candidate = 0 (비어있음)
  → 체크항목 정의는 있으나 coverage 미생성.

판정: 부분(항목 802 존재) / 실행연결 NO.
단 이 계통도 소비자 결과 경로가 아님 (법령엔진→checklist 분기).
  소비자 결과(V4)는 "의무 목록"을 주지 "체크 질문"으로 변환하지 않음.
  → 소비자 결과 기준 Layer1(체크 질문 변환) = NO.
```

---

## STEP-6: 체크엔진 추적 (CHECK_ENGINE)

```
질문: Compliance Package가 체크항목 생성에 사용되는가?
  compliance_package(344) → checklist_item_candidate 참조 FK = 없음.
  checklist_item_candidate ← document_schema_candidate (다른 부모).
판정: NO (compliance_package는 checklist 생성에 미사용).

질문 확장: Compliance Package가 소비자 결과에 사용되는가?
  소비자 결과 = V4 어댑터 ← applicability_conditions.
  compliance_package = 무관.
판정: NO (compliance_package는 소비자 결과 경로에 없음).
```

---

## STEP-7: 역방향 연결지도 (RESULT_BACKTRACE_MAP)

```
[소비자 결과 경로 — 실제 살아있는 경로]
  ConsumerResult (factory_diagnosis_results.result_data)
    ↑ YES
  정제레이어 (diagnosis_transform — 표현 변환)
    ↑ YES
  V4 어댑터 (obligation_adapter_service)
    ↑ YES
  V4 판정 (applicability_condition_service)
    ↑ YES
  applicability_conditions (14건, 법령 3종)
    ↑ (뿌리)

[법령엔진 경로 — 소비자 결과와 분리됨]
  CompliancePackage (344)
    ↓ NO (소비자 결과로 안 감)
  CheckEngine / CheckLayer1 / CheckLayer2
    = 소비자 결과 경로에 없음 (별도 미가동 계통)

역방향 단계 판정:
  결과 ← 정제레이어        YES
       ← V4 어댑터          YES
       ← V4 판정            YES
       ← applicability_conditions  YES (뿌리, 14건)
       ← CompliancePackage  NO  ← ★ 여기서 연결 없음

끊김 지점:
  CompliancePackage(법령엔진) 와 소비자 결과(V4 어댑터)가
  애초에 연결되지 않음. 두 개의 독립 계통.
```

---

## ★ 단절의 정체 (정직)

```
"체크엔진이 어디서 끊겼는가"의 답:
  끊긴 게 아니라, 소비자 결과가 두 경로 중 "작은 쪽"에서 나온다.

  [경로 1 — 현재 소비자 결과가 쓰는 길]
    applicability_conditions (14건, 법령 3종)
     → V4 어댑터 → 정제레이어 → 소비자 결과
    = 손으로 만든 소량 조건. 산업만. 완성 문장.

  [경로 2 — 20세션 작업한 법령엔진]
    factories → applicability(394만) → task(9만)
     → ... → compliance_package(344)
    = 대량. 전 섹터. 단 "보고하여야 한다" 추상 동사 수준.
    = 소비자 결과로 연결 안 됨.

→ 지금 소비자가 보는 결과는 경로1(14건)에서 나오고,
  20세션 만든 법령엔진(경로2)은 아직 소비자 화면에 연결 안 됨.
```

---

## 성공 기준 점검

```
RB-01 결과 객체 확인        → ✅ (factory_diagnosis_results JSONB)
RB-02 결과 1건 추적         → ✅ (source=V4_ADAPTER_v1)
RB-03 부모 연결 확인        → ✅ (applicability_conditions 14건)
RB-04 체크레이어2 확인      → ✅ (NO, 소비자 경로 아님)
RB-05 체크레이어1 확인      → ✅ (부분, 소비자 경로 아님)
RB-06 체크엔진 확인         → ✅ (NO, package 미사용)
RB-07 역방향 연결지도 작성  → ✅
RB-08 수정 0건              → ✅
RB-09 데이터 삭제 0건       → ✅
```

---

## 완료 문장

```
소비자 결과 화면 기준으로 역추적을 수행하였다.
체인의 존재 여부가 아니라 실제 데이터 연결 여부를 확인하였다.

소비자 결과는 applicability_conditions(14건) → V4 어댑터 → 정제레이어
경로에서 생성되며, 20세션 구축한 법령엔진(compliance_package 344)과는
연결되지 않은 별도 계통임을 특정하였다.
끊김 지점 = CompliancePackage ↔ 소비자 결과 (두 독립 계통).
수정 없이 기록하였다.
```

---

## 이것이 바꾸는 그림 (다음 과제 후보, 이 WO 범위 아님)

```
지금까지: "법령엔진을 완성하면 소비자 결과가 좋아진다"고 가정.
실제: 소비자 결과는 법령엔진을 안 쓰고 있다(applicability_conditions 14건만 씀).

→ 진짜 과제는 "건설 의무 더 만들기"도 "체크엔진 잇기"도 아닐 수 있음.
  법령엔진(경로2, 대량)을 V4 어댑터 자리에 연결하는 것
  = compliance_package/task_candidate → 소비자 결과 경로로 잇기.
  (단 task의 "보고하여야 한다" 추상 동사를 V4의 완성 문장 수준으로
   올리는 변환이 필요 — 이는 별도 설계/GPT 판단 영역)
```
