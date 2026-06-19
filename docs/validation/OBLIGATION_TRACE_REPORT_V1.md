# OBLIGATION TRACE REPORT V1
# WO-OBLIGATION-TRACE-001

**작성일**: 2026-06-18
**성격**: 추적(Trace)만. 구현/테이블생성/컬럼추가/Obligation 생성 없음.

---

## 최종 질문 답변

```
Q: 현재 ApplicabilityCondition 14건은 법령 그래프까지 역추적 가능한가?
A: YES — 추적 불필요. 이미 조건 레코드 자체에 법령 정보가 들어있다.
```

---

## 중대 정정: WO-OBLIGATION-LAYER-DESIGN-001의 오판

```
이전 판정 (틀림):
  "applicability_conditions에 legal_basis 없음, required_action 없음"
  → legal_basis / required_action 이라는 이름의 컬럼만 찾고
    "없다"고 결론냈음

실제 (정정):
  법령 정보는 이미 존재한다. 다른 컬럼명으로:
    law_name      = 근거 법령명
    appendix_no   = 조문/별표 번호
    action_type   = 의무 유형
    action_text   = 권장 조치 문구
    required_count = 필요 수량

또 "이미 가진 것을 없다고 착각"한 사례.
컬럼 이름이 다르다는 이유로 데이터 부재로 오판했음.
```

---

## Trace Coverage

```
조건 수: 14건 (INDUSTRIAL)
4요소 충족: 14건 (100%)
미도달: 0건
```

실측:
```
law_name 있음:     14/14
appendix_no 있음:  14/14
action_type 있음:  14/14
action_text 있음:  14/14
required_count 있음: 14/14
```

---

## Trace Matrix (대표 8건)

| 의무 | law_name | appendix_no | action_type | action_text |
|---|---|---|---|---|
| 안전관리자 선임 | 산업안전보건법 시행령 | 별표 3 | APPOINTMENT | "토사석 광업(071) 50명 이상 499명 미만 안전관리자 1명" |
| 관리감독자 지정 | 산업안전보건법 | 제16조 | DESIGNATION | "관리감독자 지정" |
| 정기 안전보건교육 | 산업안전보건법 | 제29조 | EDUCATION | "정기 안전보건교육 실시" |
| 신규채용자 교육 | 산업안전보건법 | 제29조 | EDUCATION | "채용 시 안전보건교육 실시" |
| 일반건강진단 | 산업안전보건법 | 제129조 | HEALTH_CHECK | "일반건강진단 실시" |
| 위험성평가 | 산업안전보건법 | 제36조 | RISK_ASSESSMENT | "위험성평가 실시" |
| 작업내용 변경 교육 | 산업안전보건법 | 제29조 | EDUCATION | "작업내용 변경 시 안전보건교육 실시" |
| 경보용 설비 설치 | 산업안전보건기준에 관한 규칙 | 제19조 | INSTALLATION | "경보용 설비 설치" |

---

## 미도달 조건 목록

```
없음. 14건 전부 도달.
```

---

## 출처 추적 구조 (참고)

```
안전관리자 7건:
  appendix_condition_id 연결됨 (예: 375f1daa..., d316d7c2...)
  → appendix_condition 테이블로 추적 가능
  → law_name=산업안전보건법 시행령, appendix_no=별표 3

일반의무 7건:
  appendix_condition_id = null
  → 조문 직접 참조 (law_name + appendix_no가 레코드에 직접 기재)
  → 예: 산업안전보건법 제129조, 제16조, 제29조 등
```

즉 두 경로 모두 법령 정보가 조건 레코드에 **이미 구체화**되어 있다.
semantic_clause/law_article_part까지 역추적할 필요 없이
조건 레코드만으로 Obligation 문장 생성 가능.

---

## 최종 판정: CASE A

```
CASE A: ApplicabilityCondition → 법령 추적 가능
→ Obligation Layer GO

근거:
  14건 전부 law_name + appendix_no + action_type + action_text + required_count 보유
  사용자 문장 4요소(의무명/근거/이유/조치) 전부 생성 가능
  - 의무명:   action_type / action_text
  - 근거:     law_name + appendix_no
  - 이유:     factory 입력(업종+인원) + threshold (런타임 생성)
  - 권장조치: action_text + required_count
```

---

## 사용자 화면 예시 (현재 데이터로 즉시 생성 가능)

```
[안전관리자 선임 필요]
  근거: 산업안전보건법 시행령 별표 3
  적용 이유: 제조업(C28), 상시근로자 280명
  권장 조치: 안전관리자 1명 선임

[일반건강진단 실시 필요]
  근거: 산업안전보건법 제129조
  적용 이유: 상시근로자 1명 이상
  권장 조치: 일반건강진단 실시
```

4줄 전부 현재 데이터로 생성 가능. 부족 요소 없음.

---

## 결론

```
Obligation Layer = GO (완전 GO, 조건부 아님)

이전 "조건부 GO"는 철회.
legal_basis/required_action을 새로 입력할 필요 없음.
이미 law_name/appendix_no/action_text로 존재함.

다음: WO-OBLIGATION-LAYER-IMPL-001 (사장님 승인 시)
  - V4 Evaluation Result(MATCH) → 조건 레코드 조인
  - law_name/appendix_no/action_text/required_count → 사용자 문장 조립
  - 새 테이블/새 데이터 입력 불필요, 표현 로직만
```

---

## 교훈 (Decision Chain 재분석 금지 항목에 추가 권장)

```
"컬럼 이름이 예상과 다르다" ≠ "데이터가 없다"
  legal_basis를 찾았으나 없음 → law_name이 그 역할
  required_action을 찾았으나 없음 → action_text가 그 역할

WO-OBLIGATION-LAYER-DESIGN-001의 "조건부 GO / 8건 입력 필요" 판정은
컬럼명만 보고 내린 오판이었다. 전수 데이터 확인으로 정정됨.
```
