# OUTPUT CONTRACT COMPARISON REPORT V1
# WO-OUTPUT-CONTRACT-COMPARISON-001

**작성일**: 2026-06-18
**성격**: 계약 비교만. 새 추적/구현/제안 없음.

---

## 비교 대상 (2개)

```
A. V4 출력 계약
   routers/applicability_api.py
   GET /applicability/evaluate/{factory_id} 응답

B. 정제레이어 입력 계약
   routers/diagnosis_transform.py
   _build_transform(row) — row.result_data(JSONB) 읽기
```

---

## 결정적 사실 1: 입력 소스가 다르다

```
정제레이어가 읽는 것:
  factory_diagnosis_results 테이블의 result_data(JSONB) 컬럼
  (_fetch_row_by_id / _fetch_latest_row)

V4가 쓰는 것:
  아무 테이블에도 안 씀. JSON을 직접 HTTP 응답으로 반환
  (save=True여도 factory_diagnosis_results에 안 씀)

→ 정제레이어는 factory_diagnosis_results.result_data를 기대
→ V4는 그 테이블을 채우지 않음
→ 애초에 만나는 지점이 없음
```

---

## 결정적 사실 2: 필드 구조가 다르다

정제레이어가 result_data에서 기대하는 의무 필드 (_obligation_from_item):
```
obligation_summary / title / name / item   (제목)
law_name                                    (법령명)
law_article                                 (조문)
rule_type                                   (규칙유형)
risk_level / severity                       (위험도)
description / remarks / detail              (설명)
evidence / legal_basis                      (근거 배열)
rule_id / id                                (식별자)
category / type                             (분류)
```

V4 evaluation_details가 실제 반환하는 필드:
```
condition_id
metric
input_state / input_value
evaluation_result
evaluation_reason
industry_name
threshold_value
operator
required_count
scope_result / scope_reason
```

---

## 필드 매핑표

| 정제레이어 요구 | V4 응답 존재? | V4 원천 데이터 존재? | 매핑 가능? |
|---|---|---|---|
| obligations (배열) | ❌ 없음 | — | 구조 재구성 필요 |
| title/obligation_summary | ❌ 없음 | ✅ action_text (조건 레코드) | 조인 시 가능 |
| law_name | ❌ 응답에 없음 | ✅ applicability_conditions.law_name | 조인 시 가능 |
| law_article | ❌ 응답에 없음 | ✅ appendix_no | 조인 시 가능 |
| category | ❌ 없음 | ✅ action_type 매핑 | 변환 필요 |
| risk_level | ❌ 없음 | ❌ 없음 | 신규 필요 |
| description | ❌ 없음 | △ industry_name 일부 | 부분 |
| evidence/legal_basis | ❌ 없음 | ✅ law_name+appendix_no | 조립 가능 |
| rule_id/id | △ condition_id 있음 | ✅ condition_id | 매핑 가능 |
| verdict (MATCH 여부) | ✅ evaluation_result | ✅ | 필터 기준 |
| headline | ❌ 없음 | ❌ 없음 | 신규 필요 |
| warnings | ❌ 없음 | ❌ 없음 | 해당 없음 |
| roi | ❌ 없음 | ❌ 없음 | 별도 |
| inspection_schedule | ❌ 없음 | ❌ 없음 | 별도 |

---

## 판정: CASE B + 일부 C

```
CASE B (필드 구조가 다름 → 어댑터 필요): 주 판정
  - V4는 condition 단위 평가 결과(verdict 중심)
  - 정제레이어는 obligation 단위 표현 구조(title/category/evidence)
  - 두 구조가 다름 → 변환 어댑터 필요

CASE C 요소 (핵심 필드 일부가 V4 응답에 없음):
  - law_name/action_text는 DB(조건 레코드)엔 있으나
    V4 evaluate() 응답 JSON에는 미포함
  - risk_level/headline은 V4에 아예 없음 (정제레이어가 자체 폴백 생성)
```

---

## 정확히 안 맞는 것 (요약)

```
1. 입력 소스 불일치:
   정제레이어 ← factory_diagnosis_results.result_data
   V4 → 직접 JSON 반환 (테이블 미기록)

2. 단위 불일치:
   V4 = condition 평가 단위
   정제레이어 = obligation 표현 단위

3. 필드 노출 불일치:
   law_name/action_text가 DB엔 있으나 V4 응답엔 없음

4. 결손 필드:
   risk_level, headline은 양쪽 다 없음
   (정제레이어가 폴백으로 자체 생성)
```

---

## 결론

```
연결이 안 되는 이유는 "배선 누락"보다 한 겹 더 깊다:

(1) V4와 정제레이어는 서로 다른 입력 소스를 본다
    (V4 직접반환 vs result_data JSONB)
(2) 데이터 단위가 다르다 (condition vs obligation)
(3) V4 응답이 정제레이어 필드를 노출하지 않는다

따라서 단순 배선(CASE A)이 아니라
어댑터가 필요한 상태(CASE B)다.

어댑터의 역할 (관찰 결과, 구현 아님):
  V4 evaluate() MATCH 결과
    → 조건 레코드의 law_name/action_text 조인
    → 정제레이어 obligation 스키마로 변환
    → factory_diagnosis_results.result_data 형식으로 정렬
```

---

## 다음 판단 (PROJECT_POLICY §6, 사장님/GPT)

```
이 비교로 확정된 것:
  연결 작업 = "어댑터 1개" 규모 (CASE B)
  데이터는 있음, 구조 변환이 핵심

판단 필요:
  어댑터를 어디에 둘지 (V4 응답 확장 vs 별도 변환 레이어)
  → 이번 WO 범위 아님. 계약 비교까지가 이 WO.
```
