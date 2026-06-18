# CONTEXT RESTORE REPORT V1
# WO-CONTEXT-RESTORE-001

**작성일**: 2026-06-18  
**성격**: 컨텍스트 복구. 새 탐색/수집/설계 없음.

---

## 판정 철회

```
이전 판정: "별표3 원문 없음 → 멈춤"
→ 철회

이유: appendix_text(NULL)만 보고 판단했음
      실제 Source of Truth는 governance DB 전체
```

---

## 현재 프로젝트가 이미 보유한 데이터 (실측)

### 법령 원문 계층 (governance DB)

| 테이블 | 행수 | 의미 |
|---|---|---|
| law_master | 768 | 법령 마스터 |
| law_article | 35,412 | 조문 |
| law_article_part | 143,549 | 조문 항/호 단위 원문 |
| law_paragraph | 50,181 | 문단 |
| law_item | 65,426 | 호 단위 |
| law_attachment | 1,322 | 별표 첨부 |
| semantic_clause | 58,495 | 의미절 (핵심) |
| semantic_clause_actor_resolution | 29,986 | actor 분류 |
| constraint_node | 284,579 | 제약 노드 |
| constraint_edge | 54,122 | 제약 엣지 |
| rule_candidate | 34,456 | 규칙 후보 |
| draft_slot | 50,133 | 드래프트 슬롯 |
| numeric_constraint | 10,329 | 수치 제약 |

**결론: 법령은 조문·항·호·의미절 수준까지 완전 DB화됨.**

---

## 법령 Source of Truth (정정)

```
틀린 이해 (이전 판단):
  law_appendix.appendix_text = 유일한 원천
  → NULL이니 원문 없음

올바른 이해:
  Source of Truth = law_article_part + semantic_clause
  law_appendix는 별표 메타데이터일 뿐
  appendix_condition(7건)이 구조화된 결과물
```

---

## 건설업 안전관리자 관련 정보 존재 위치 (실측)

### 확인됨 — law_article_part에 원문 존재

```
제16조제2항 (안전관리자 공동선임):
  "건설업의 경우에는 공사금액의 합계가 120억원
   (토목공사업 150억원) 이내"

제16조제3항 (전담 안전관리자):
  "건설업의 경우에는 공사금액이 120억원
   (토목 150억원) 이상인 사업장"
```

### semantic_clause에 건설업 안전관리자 의미절 3건 존재

```
건설업 + 안전관리자 키워드 의미절: 3건
```

### 주의 — 혼동하면 안 되는 것

```
제59조 "공사금액 1억~120억":
  → 기술지도계약 기준 (안전관리자 아님)

제16조 120억원:
  → 안전관리자 전담/공동선임 경계 (300명 대응)

별표3 본문의 건설업 선임 인원 구간 (50억/800억 등):
  → law_attachment에 추출된 텍스트로는 미확인
  → 단, 조문(law_article_part)에 120억 기준은 존재
```

---

## 기억 손실 여부 판정

```
손실 있었음:
  "원문 없음" 판단은 잘못된 것
  governance DB에 law_article_part 143,549건,
  semantic_clause 58,495건이 존재함

복구됨:
  건설업 안전관리자 공사금액 120억 기준은
  law_article_part 제16조에 원문으로 존재
```

---

## "우리가 이미 가진 것" — 한 페이지 요약

```
1. 법령 원문: 조문·항·호 수준까지 완전 DB화 (143,549 part)
2. 의미절: 58,495건 (조건/주체/행위/주기 분리됨)
3. actor 분류: 29,986건
4. 제약 그래프: constraint_node 284,579
5. 건설업 안전관리자:
   - 공사금액 120억 기준 → law_article_part 제16조 ✅
   - 선임 인원 구간 세부 → semantic_clause 3건 + 별표3 추가 확인 필요
```

---

## 다음 단계 (수집 아님, 기존 DB 읽기)

```
Phase 5 설계 전:
  건설업 안전관리자 선임 인원 구간을
  semantic_clause + law_article_part에서 글읽기로 확인
  (API 재수집 아닌, 기존 DB 조회)

즉:
  "원문 수집"이 아니라
  "이미 수집된 것을 글읽기"
```

---

## 교훈

```
가장 위험한 것은 기술 문제가 아니라
이미 확보한 것을 없는 것으로 착각하는 것.

appendix_text 한 컬럼의 NULL을
"법령 원문 없음"으로 읽은 것이 바로 그 착각이었다.

Source of Truth = governance DB 전체
(law_article_part + semantic_clause), 단일 컬럼 아님.
```
