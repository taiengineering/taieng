# APPENDIX3 CONSTRUCTION LOCATE REPORT V1
# WO-APPENDIX3-CONSTRUCTION-LOCATE-001

**작성일**: 2026-06-18  
**성격**: 저장 위치 추적. 구현/구조화/수집 없음.

---

## 완료 조건 답변

```
Q1: 별표3 건설업란 "본문"이 현재 DB에 존재하는가?
A1: NO — 본문(전체 구간표)은 없음. 요약·메타데이터만 존재, 그조차 값이 충돌.

Q2: 왜 INDUSTRIAL은 구조화되고 CONSTRUCTION은 안 됐는가?
A2: INDUSTRIAL은 수동 구조화(MANUAL)로 appendix_condition 7건 생성.
    CONSTRUCTION은 그 수동 작업에서 제외됨.
```

---

## 판정: CASE B (본문 없음) — 단, 조건부

```
별표3 건설업란 "전체 구간표 본문"은 DB에 없다.
그러나 완전한 CASE B는 아니다:
  - 일반 조문(제16/17/73/75조)은 governance DB에 있음
  - 별표3 "구간표" 자체만 없다
```

---

## 검색한 테이블과 결과

| 테이블 | 건설업 안전관리자 별표3 본문 | 결과 |
|---|---|---|
| law_appendix | 제목만 (appendix_text=NULL) | ❌ 본문 없음 |
| law_attachment | 안전관리자 별표 첨부 없음 | ❌ 없음 |
| law_article_part | 제16/17조 조문 (120억 전담 경계) | ⚠️ 조문만, 별표본문 아님 |
| semantic_clause | "별표3과 같다" 참조 | ⚠️ 참조만 |
| appendix_runtime_metadata | 요약 2건 (값 충돌) | ⚠️ 요약·충돌 |

---

## 핵심 발견 1: INDUSTRIAL의 source도 NULL이었다

```
appendix_condition 7건의 source appendix_id:
  = law_appendix 제0be28b96 (별표 3)
  = appendix_text가 NULL

즉 INDUSTRIAL 7건은 appendix_text에서 파싱된 게 아니다.
  → 수동 구조화(MANUAL)로 입력된 것
  → raw_condition에 직접 "50명 이상 1명" 등을 써넣음
```

## 핵심 발견 2: appendix_runtime_metadata 값 충돌

```
레코드 1 (extraction_method=STRUCTURAL):
  source_trace: "시행령 제17조 → 별표3"
  건설업 공사금액 50억 (5,000,000,000) >=

레코드 2 (extraction_method=MANUAL_STRUCTURAL):
  source_trace: "시행령 별표3 제1호~2호"
  건설업 공사금액 120억 (12,000,000,000) >=
  건설_토목 150억 (15,000,000,000) >=

→ 두 메타데이터가 50억 vs 120억로 충돌
→ 둘 다 요약이지 별표3 본문 전체 구간표가 아님
→ 신뢰 불가 (추정 금지 원칙)
```

## 핵심 발견 3: 120억의 의미 (재확인)

```
제17조제3항 120억 = "전담 안전관리자를 두어야 하는" 경계
  ≠ "안전관리자 선임 의무 발생" 최소 기준

즉 metadata의 120억은 "전담 경계"를
"선임 기준"으로 잘못 요약했을 가능성

50억은 근거 불명 (어느 조항에서 온 것인지 trace 불명확)
```

---

## 다음 WO 판정

```
Phase 5 = CASE B (별표3 건설업란 본문 재확보 필요)

이유:
  - 현재 DB의 건설업 구간 값이 충돌 (50억 vs 120억)
  - 둘 다 요약이지 별표3 본문 구간표가 아니고
  - 120억은 전담 경계와 혼동 가능성
  - 추정 금지 원칙상 이 값들로 ApplicabilityCondition 설계 불가

단, "새 수집"의 의미:
  - 국가법령정보센터 별표3 원문(구간표)을 확보하는 것
  - 이미 수집된 일반 조문과는 별개로, 별표3 본문은 미확보 상태
```

---

## INDUSTRIAL은 왜 가능했는가 (결론)

```
INDUSTRIAL appendix_condition 7건:
  appendix_text(NULL)에서 파싱한 게 아니라
  사람이 수동으로 raw_condition을 입력한 것
  (예: "제1호~제27호 외 사업 50명 이상 999명 미만 1명")

즉 INDUSTRIAL은 "이미 사람이 아는 기준"을 입력한 것.
CONSTRUCTION은 그 수동 입력이 안 되었을 뿐.

따라서 두 가지 경로 가능:
  A. 국가법령정보센터 별표3 원문 확보 → 정확한 구간 입력 (권장)
  B. 사장님이 별표3 건설업란 공식 구간 제공
```

---

## 사장님 판단 요청

```
별표3 건설업 안전관리자 구간표 본문이 DB에 없습니다.
DB의 요약 메타데이터는 50억/120억이 충돌하고 신뢰 불가입니다.

확보 방법 선택:
  A. 국가법령정보센터에서 별표3 원문 확보
     (기존 일반조문과 별개로 별표 구간표만)
  B. 사장님이 별표3 건설업란 공식 구간 직접 제공
  C. INDUSTRIAL처럼 안전관리자 선임 기준 수동 입력
     (단 건설업 구간을 정확히 아는 경우에만)
```

---

## 교훈

```
INDUSTRIAL이 "구조화됨"의 의미:
  자동 파싱이 아니라 수동 입력이었다.

appendix_runtime_metadata의 수치를 그대로 믿으면 안 된다:
  50억 vs 120억 충돌 = 요약 과정의 오류
  원문(구간표)만이 Source of Truth
```
