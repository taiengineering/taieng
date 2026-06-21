# CHECK ENGINE TRACE — END TO END
# WO-CHECK-ENGINE-TRACE-001

**작성일**: 2026-06-21
**목적**: 법령엔진 결과가 소비자 결과까지 관통하는지 추적(검증 WO, 기능구현 아님).
**금지 준수**: 카운트로 성공판단 안 함. 법령/binding/엔진 수정 0. 추적·Reading·YES/NO/UNKNOWN만.
**통합**: STEP-1~6 산출물을 본 문서에 섹션으로 통합(CHAIN_MAP/SINGLE_TRACE/CONSUMER_EXISTENCE/READING_LOG/LAYER_EXISTENCE/E2E_MAP).

---

## STEP-1: Check Engine 체인 식별 (CHAIN_MAP)

### WO가 가정한 이름의 테이블은 부재

```
'check_engine' / 'check_layer_1' / 'check_layer_2' 테이블 = DB에 없음.
→ WO가 가정한 명칭의 체인은 존재하지 않음.
  대신 관련 계통이 두 갈래로 실재(아래).
```

### 실재하는 두 계통 (FK 추적)

```
[계통 A: 법령엔진 → 체크리스트] (compliance_package 계열과 별개 분기)
  document_schema_candidate → checklist_item_candidate (802)
    → runtime_checklist_item (802)
      → runtime_checklist_execution (0)  ← 비어있음
  form_mapping_candidate → checklist_coverage_candidate (0)  ← 비어있음
  evidence_candidate (275,934, law_article_part 참조)

[계통 B: 소비자 진단] (완전 별개)
  diagnosis_session → diagnosis_candidate (159)
  factories → factory_diagnosis_results (4) → diagnosis_rule_results (306)
  users → anonymous_diagnosis_results (40)

[compliance_package (344)]
  → 참조하는 자식 FK 없음.
  → 계통 A/B 어느 것과도 FK로 직접 연결되지 않음.
```

### ★ 핵심: compliance_package ↔ 소비자 결과 = 데이터 연결 없음

```
compliance_package(법령엔진 최종) 를 참조하는 하위 테이블 = 0.
소비자 결과(diagnosis_rule_results)는 compliance_package/task_candidate를
참조하는 컬럼이 없음 (rule_code/rule_name 자체 보유).
→ 법령엔진 결과와 소비자 진단 결과는 데이터로 끊겨 있음.
```

---

## STEP-2: 입력 1건 추적 (SINGLE_TRACE)

```
법령엔진 계통 (실데이터 factory 기준):
  facility → task → schedule → penalty → package
    YES     YES    YES         YES        YES   (앞 WO들에서 관통 확인)
  package → check_engine → check_layer → 결과
    NO (compliance_package 자식 FK 없음 → check 단계로 데이터 안 감)

소비자 진단 계통 (diagnosis 기준):
  diagnosis_session → diagnosis_candidate → factory_diagnosis_results
    YES                YES                   YES (단 4건)
    → diagnosis_rule_results (306, 의무 목록)
  단 이 계통의 rule_code는 법령엔진 part_id와 무관.

연결 단계 판정:
  facility → package           YES (법령엔진 내부)
  package → check_engine        NO  (테이블/FK 부재)
  package → 소비자결과           NO  (데이터 연결 없음)
  소비자결과 자체 존재            YES (별도 계통, 정적)
```

---

## STEP-3: 최종 사용자 결과 존재 확인 (CONSUMER_EXISTENCE)

```
소비자 결과(diagnosis_rule_results) 구조 기준:

  항목         존재    근거
  질문         NO     체크 질문 컬럼 없음
  체크항목      부분    checklist_item_candidate(802)는 별 계통, diagnosis엔 미연결
  판단         부분    status 컬럼 있음(충족/미충족 단순)
  증빙         NO     evidence는 별 계통(275,934), diagnosis_rule_results엔 없음
  후속조치      NO     후속조치 컬럼 없음

소비자가 보는 결과 = "의무 목록 + 법령출처(law_name/article) + 기한(due_date)".
  = 법령 의무 나열 수준. 체크(질문/증빙/판단/후속) 변환은 이 결과에 없음.
```

---

## STEP-4: Compliance Package Reading (READING_LOG)

```
앞 WO(MASS_READING)에서 확인된 것과 동일 계통 Reading:
  법령엔진 task 의무 문장 = "보고/제출/점검/측정/관리하여야 한다" (추상 동사).
  주체/대상/기한/증빙이 본문 토큰에 미포함.

소비자 결과(diagnosis_rule_results) Reading:
  rule_name 예:
    "소방시설을 설치하고 적절하게 관리할 의무"
    "고압·특고압 전로의 피뢰기 설치 및 적절한 조치 의무"
    "조치 의무 (산업안전보건법 시행규칙 제16조)"
  → 법령엔진보다 완성된 문장(법령명+조항+의무).
    단 이 문장들은 별 룰셋(FIREACT/OSHRULE 코드)에서 옴.

변환(법령 문장 → 체크 문장) 존재 여부:
  법령 문장 → "체크 질문/증빙/방법"으로의 변환 = 발견 안 됨.
  소비자 결과는 "의무 서술"에 머무름. 체크 형태로 변환되지 않음.
```

---

## STEP-5: Check Layer 존재 여부 (LAYER_EXISTENCE)

```
판단 기준(WO): 법령 그대로 출력=Layer 없음 / 체크 질문·증빙·방법 변환=Layer 존재.

Layer 1 (법령→체크 변환):
  소비자 결과가 "의무 서술"(소방시설 설치·관리 의무) 형태.
  "소방시설이 설치되어 있습니까? / 증빙: 설치확인서 / 방법: 육안점검"
  같은 체크 변환 = 없음.
  → Layer 1: 동작 안 함 (NO).

Layer 2 (체크 실행/판정):
  runtime_checklist_execution = 0건 (비어있음).
  checklist_coverage_candidate = 0 / evidence_coverage_candidate = 0.
  → Layer 2: 동작 안 함 (NO).

checklist_item_candidate(802)는 존재하나:
  - runtime_checklist_execution(0)으로 실행 단계 미도달.
  - diagnosis(소비자) 계통과 미연결.
  → 체크 항목 정의는 있으나 실행·소비자연결 없음 = Layer 미가동.
```

---

## STEP-6: 최종 연결지도 (E2E_MAP)

```
                          단계              판정    근거
입력                                        YES    diagnosis_input_fields
  ↓
FacilityProfile                             YES    build_facility_profile
  ↓
Applicability                               YES    facility_applicability
  ↓
Task                                        YES    task_candidate
  ↓
Schedule                                    YES    schedule_candidate
  ↓
Penalty                                     YES    penalty_candidate
  ↓
CompliancePackage                           YES    compliance_package(344)
  ↓
CheckEngine                                 NO     테이블/FK 부재, package 자식 없음
  ↓
CheckLayer1 (법령→체크 변환)                 NO     변환 산출물 없음
  ↓
CheckLayer2 (체크 실행/판정)                 NO     runtime_checklist_execution 0
  ↓
ConsumerResult                              부분   diagnosis_rule_results(별 계통)
                                                   = 의무 목록은 있으나 법령엔진과 미연결

★ 끊김 지점 = CompliancePackage → CheckEngine.
  법령엔진은 package까지 YES로 관통.
  그 뒤 Check Engine/Layer는 테이블·실행·연결이 부재(NO).
  소비자가 보는 결과(diagnosis)는 존재하나 법령엔진과 별개 정적 계통.
```

---

## 성공 기준 점검

```
CE-01 체인 식별 완료        → ✅ (계통 A/B + check 명칭 부재 확인)
CE-02 입력 1건 추적 완료    → ✅ (package까지 YES, check부터 NO)
CE-03 소비자 결과 존재 확인 → ✅ (의무목록 YES, 질문/증빙/후속 NO)
CE-04 Package Reading 완료  → ✅ (법령→체크 변환 없음 확인)
CE-05 Check Layer 존재 확인 → ✅ (Layer1/2 NO)
CE-06 최종 연결지도 작성    → ✅ (E2E_MAP)
CE-07 수정 0건              → ✅
CE-08 법령 수정 0건         → ✅
CE-09 엔진 수정 0건         → ✅
```

---

## 완료 문장

```
실제 소비자가 보게 되는 결과까지 데이터 흐름을 추적하여,
법령엔진 이후 Check Engine 및 Check Layer 체인의 존재와 연결 상태를 확인하였다.

결과:
  법령엔진은 CompliancePackage까지 관통(YES).
  Check Engine / Check Layer 1·2는 테이블·실행·연결이 부재(NO) —
    법령 의무를 "체크 질문·증빙·판단·후속조치"로 변환하는 단계가 아직 없음.
  소비자 결과(diagnosis)는 존재하나 법령엔진과 데이터로 연결되지 않은 별개 계통.
  끊김 단일 지점 = CompliancePackage → CheckEngine.
```

---

## 정직한 결론 (이 추적이 드러낸 것)

```
지금까지 만든 것 = 법령엔진(입력→package)은 살아서 관통.
아직 없는 것 = 그 의무를 "사용자가 실제 점검하는 체크"로 바꾸는
  Check Engine / Check Layer.
소비자 화면 결과(diagnosis)는 별도 정적 계통으로 존재하나,
  현재 법령엔진 산출물이 그 화면으로 흐르지는 않음.

→ 다음 과제 후보(이 WO 범위 아님): CompliancePackage → Check 변환 연결.
  단 이것은 "건설 의무 더 만들기"가 아니라
  "이미 만든 법령엔진 결과를 사용자 체크 형태로 잇는" 단계.
```
