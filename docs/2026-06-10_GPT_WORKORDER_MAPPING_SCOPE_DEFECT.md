# GPT 작업지시서 — 법령엔진 오매핑 원인: 부실 조건(scope 미추출) draft

작성일: 2026-06-10
작성: Claude(기획창) → GPT(법령엔진/분해기/Compiler 전담)
근거 진단: public_token `86ff8075-412a-43c4-b9d3-dfed65c5e080`
  (대한정밀화학 목업, 제조업/INDUSTRIAL, 80명, 8000㎡, 화학물질·고압가스·보일러)

---

## 0. 검증 방식 (대원칙)

이 진단을 **카운트가 아니라 글(법조문 제목·내용)을 읽어** 검증했다.
카운트로는 "선임 14건"이 정상으로 보였으나, 글을 읽으니 의미상 오매핑이
다수 섞여 있었다. 법은 텍스트이므로 의미로 판단해야 한다.

## 1. 증상 (글로 읽은 오매핑)

제조업 화학공장 진단인데, 아래 의무들이 "적용"으로 나왔다. 글을 읽으면
이 사업장의 의무가 **아니다**:

| 결과상 분류 | 법령·조문 | 글로 본 실제 의미 |
|---|---|---|
| APPOINT(선임) | 산재보험법 시행규칙 §9 판정위원회의 운영 | 근로복지공단 위원회 운영 — 사업장 의무 아님 |
| APPOINT(선임) | 산재보험법 시행령 §60 유족보상연금 청구 대표자 선임 | 유족이 정하는 대표자 — 사업장 의무 아님 |
| APPOINT(선임) | 산안법 시행령 §97 특수건강진단기관 지정 요건 | 진단"기관"이 갖출 요건 — 사업장 의무 아님 |
| APPOINT(선임) | 수도법 시행령 §38 위탁심의위원회 기능·운영 | 수도사업 위탁 심의위 — 무관 |
| APPOINT(선임) | 한국전기설비규정 §605 압력용기 용접사 지정 | 용접 검사 기술기준 — 선임 의무 아님 |
| APPOINT(선임) | 산안기준규칙 §547 표면공급식 잠수작업 시 조치 | 잠수작업 — 화학공장 무관 |
| ACTION | 각종 "○○기관 지정기준", "협회 설립인가", "평가위원회 구성" | 기관·협회·위원회 조항 — 사업장 의무 아님 |

## 2. 원인 (개발 개념으로 역추적)

위 조문들이 이 사업장에 매칭된 이유를 `draft_slot` 조건으로 역추적한 결과,
**적용조건이 부실**한 것이 근원이다. 결과 draft들의 조건 패턴 분포:

| 패턴 | 건수(중복포함) | 의미 |
|---|---|---|
| NO_CONDITION (조건 없음) | 193 | IF_NUMERIC·IF_SCOPE 둘 다 없음 → 무조건 통과 |
| HAS_SCOPE (실제 범위조건 있음) | 124 | 정상(scope로 적용대상 한정) |
| NUMERIC_ONLY (기타 수치만) | 45 | 수치 조건만 |
| EMPLOYEE_ONLY (근로자수만) | 41 | `employee_count >= 1/2`만 → 80명이면 다 통과 |
| UNRESOLVED_SCOPE (범위 미해결) | 9 | 적용범위를 못 풀고 통과 |

**핵심: NO_CONDITION + EMPLOYEE_ONLY + UNRESOLVED_SCOPE가 오매핑의 근원.**
- 조문의 진짜 적용조건(예: "잠수작업을 하는 경우", "지정받으려는 기관인 경우",
  "유족이 2명 이상인 경우")이 추출되지 않음.
- 대신 fallback으로 `employee_count >= 1/2`만 붙거나, 조건이 아예 없음.
- 80명 사업장은 이 fallback을 전부 만족 → 무관한 조문이 다 적용됨.

### 구체 사례 (binding 오류)
- "유족보상연금 청구 대표자 선임 등" → 조건 `employee_count >= 2`.
  하지만 이 §의 "2"는 **유족이 2명 이상**이라는 뜻. binding_field가
  `employee_count`로 잘못 바인딩됨(주체·대상 혼동).
- "특수건강진단기관 지정 요건" → `employee_count >= 1` + `UNRESOLVED_SCOPE`.
  적용대상(=지정받으려는 기관)을 못 풀고 근로자수로 fallback.

## 3. 어느 단계의 문제인가 (책임 구분)

- **sector 필터(입구) 문제 아님** — 위 조문 대부분 산안법·소방 계열이라 sector(INDUSTRIAL/BUILDING)는 맞음. sector로는 못 거른다.
- **facility_applicability 판정 로직 문제 아님** — 주어진 조건(`employee_count>=2`)을 정확히 평가했을 뿐. 80명이니 통과가 맞다.
- **draft_slot의 조건(분해 결과)이 문제** — 조문의 진짜 적용조건이 추출 안 되고 employee_count fallback/무조건으로 채워짐. **= 분해기/Compiler/scope 추출 단계 = GPT 전담 영역.**

## 4. GPT에게 요청 (분해·scope 영역)

다음은 법령엔진 분해/Compiler 구조에 관한 것이라 GPT가 판단·수정한다.
Claude는 손대지 않는다(역할분리).

1. **주체·대상 구분**: 조문이 "사업장이 지는 의무"인지, 아니면 "기관·협회·
   위원회·제품·유족 등 제3자 대상"인지 분해 단계에서 구분 가능한가?
   (예: "~기관의 지정 요건", "~위원회의 운영", "협회 설립인가"는 사업장 의무 아님)
2. **employee_count fallback 점검**: 적용조건을 못 풀었을 때 `employee_count >= 1/2`로
   채우는 fallback이 있는가? 있다면 그게 NO_CONDITION/UNRESOLVED와 함께
   오매핑을 만든다. fallback 대신 "조건 미해결"로 남겨 두는 게 맞지 않나?
3. **binding 정확성**: "유족 2명", "용접사 1명" 같은 조문 내 숫자가
   `employee_count`(사업장 근로자수)로 잘못 바인딩되는 경우의 분해 규칙 점검.
4. **NO_CONDITION 처리 방침**: 조건이 전혀 없는 draft를 "무조건 적용"으로
   둘지, "조건 미상=보류"로 둘지 분해 단계 방침 결정.

## 5. 검증 방법 (재확인용)

수정 후, 같은 목업(80명 화학공장)으로 재진단하여 **글을 읽어** 확인한다.
"잠수작업·유족연금·판정위원회·기관 지정요건"이 사라지면 개선된 것.
카운트(159건→몇 건) 비교는 보조 지표일 뿐, 판단은 글의 의미로 한다.

## 6. 참고 — 부실조건 draft 식별 쿼리

```sql
-- 결과 draft를 (법령명, 조문제목)으로 이어 조건 패턴 분류
WITH result_items AS (
  SELECT DISTINCT r->>'law_name' AS law_name, r->>'obligation_summary' AS title
  FROM anonymous_diagnosis_results a, jsonb_array_elements(a.full_result->'rules_table') AS r
  WHERE a.public_token='<TOKEN>'
), joined AS (
  SELECT ri.law_name, ri.title, ed.id AS draft_id
  FROM result_items ri
  JOIN law_master lm ON lm.law_name=ri.law_name AND lm.is_active
  JOIN law_article la ON la.law_id=lm.id AND la.article_title=ri.title
  JOIN executable_draft ed ON ed.article_id=la.id
)
SELECT j.*, ds.section, ds.binding_field, ds.value, ds.family_name
FROM joined j LEFT JOIN draft_slot ds ON ds.draft_id=j.draft_id;
```

`UNRESOLVED_SCOPE`, `EMPLOYEE_THRESHOLD_FAMILY` 단독, 슬롯 없음(NO_CONDITION)이
주 점검 대상.
