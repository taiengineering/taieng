# WP-PERSISTENCE-02A STEP-2 — STD-INSPECT-001 특별 검증

- 작성일: 2026-08-25
- 성격: 지시서 §8. 이 판정 하나가 이후 324건 검토량을 좌우하므로 최우선 상세 직독.
- 방식: runtime_form_schema + 원천 document_form_master 직독. mutation 0.

---

## 0. 판정 (결론)

```
STD-INSPECT-001 = INSUFFICIENT_AS_GENERAL_RESULT_FORM
```
이름은 "안전점검 결과서"로 범용처럼 보이나, 실제 구조는 (1) 다중이용업소 특별법
전용 + BUILDING 섹터 종속, (2) multi_row/field_key contract 부재. 범용 결과서로
승인하지 않는다. 지시서 §4·§8 "이름만 보고 범용 승인 금지"가 정확히 작동한 사례.

---

## 1. 실측 구조

runtime_form_schema:
```
id              = ecfa9483-f078-4695-8f65-98d17b6fbf77
form_name       = 안전점검 결과서
form_type       = CUSTOM        (원천은 STANDARD — 표기 불일치, 관찰만)
document_family = DOCUMENT
status          = CANDIDATE
field_count     = 6
checklist_count = 0
evidence_count  = 2
source          = document_form_master / 49949506-...
```

실제 runtime_field 6개(직독): 점검일시(date) / 점검대상시설(text) / 점검항목(text) /
점검결과(text) / 조치필요사항(textarea) / 점검자서명(signature).
→ **multi_row 필드 없음, field_key 전건 NULL(required_status=CANDIDATE_ONLY).**
   (checklist_count=0 자체가 부적합 근거는 아님 — 부적합 근거는 아래 §2 참조.)

원천 document_form_master (STD-INSPECT-001):
```
form_type   = STANDARD
form_category / obligation_type = DOCUMENT
law_name    = 다중이용업소의 안전관리에 관한 특별법   ← 특정 법령 종속
sector      = BUILDING                              ← 특정 섹터
use_case    = 안전시설 정기점검 실시 후
required_fields = [ 점검 일시, 점검 대상 시설, 점검 항목,
                    점검 결과, 조치 필요사항, 점검자 서명 ]
template_fields = null
```

---

## 2. §8 6개 검증 항목

**1) 실제 field schema** — 평면 6필드(일시/대상시설/항목/결과/조치/서명). ✔ 존재하나 단순.

**2) 반복 점검 결과를 담을 수 있는가** — **현 AS-IS 로는 불가(구조 계약 부재).**
   저장 무결성 관점에서 runtime_data_json list/dict 나 multi_row 필드로 반복 표현은
   원리적으로 가능하다. 그러나 STD-INSPECT-001 의 실제 runtime_field 6개는 전부
   단일형(date/text/textarea/signature)이라 **multi_row 필드가 없고**, 나아가 field_key
   가 전건 NULL 이라 inspection_results 를 구조적으로 받을 승인된 계약이 없다.
   (대조: STD-FIRE-001 은 multi_row 필드를 가짐 — 원형 참고감. STD-INSPECT-001 은 아님.)
   → R3 의 실제 관문(승인된 field contract) 미충족.

**3) inspection metadata** — 일시/대상시설/점검자 정도는 표현 가능. △ 부분.

**4) evidence** — evidence_count=2 로 첨부 슬롯은 있음. △.

**5) 특정 법률 비종속(범용) 여부** — **실패.**
   law_name=다중이용업소 특별법, sector=BUILDING. 이 서식을 산업(INDUSTRIAL)·건설
   (CONSTRUCTION) 점검에 붙이면 잘못된 법적 근거가 부여된다. 범용 아님.

**6) runtime_data_json 결합 시 safety_inspection_results 무손실 표현** — **AS-IS 불가.**
   무손실 저장은 엔진상 가능하나, 이 schema 에 승인된 multi_row/field_key contract 가
   없어 구조적 매핑이 성립하지 않는다. 범용성 실패(5번)와 합쳐 범용 결과서 부적합.

---

## 3. 판정 근거 요약

| 항목 | 결과 |
|---|---|
| 반복 항목 구조 계약(R3) | AS-IS 불가 (multi_row 없음 + field_key NULL) |
| 범용성(R5) | 불가 (다중이용업소법·BUILDING 전용) |
| 무손실 구조 매핑 | AS-IS 불가 |
| → 종합 | **INSUFFICIENT_AS_GENERAL_RESULT_FORM** |

주: "저장 무결성 자체가 불가능"하다는 뜻이 아니다. 엔진은 list/dict/multi_row 를
보존한다. STD-INSPECT-001 이 부적합한 이유는 (a) 이 schema 에 그 계약이 없고
(b) 특정 법령·섹터 전용이라는 두 가지다.

## 4. 파급

- STD-INSPECT-001 을 **AS-IS 범용 결과서로 재활용**하는 손쉬운 경로는 없다(부적합).
- 대신 STEP-3 에서 반복 항목(multi_row line-item) 구조와 field_key contract 를 갖춘
  **GENERAL_INSPECTION_RESULT schema 1종을 신규 설계**한다. 이 GENERAL 1종은 여러
  inspection_set 이 명시적으로 공유할 수 있다(단 runtime fallback 아님, §14).
- STD-FIRE-001 의 multi_row 필드가 그 설계의 참고 원형이 된다.
- 이 판정으로 STEP-2 는 "기존 후보 AS-IS 승인"이 아니라 "GENERAL schema 설계 선행"으로
  방향이 확정된다(FINAL_DECISION 참조).
