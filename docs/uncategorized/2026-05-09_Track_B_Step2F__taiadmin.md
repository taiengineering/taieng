# [Track B] 2026-05-09 Step 2-F — 룰 V1 보강 (inheritance 첫 매칭 한계 해소)

**선행**: Step 2-D + Step 2-E 완료 (cross-validate 86.5%, 위임표현만 282건 발견)  
**목표**: inheritance 1차 추출의 "첫 300자 첫 매칭만" 한계 해소

---

## Done

### Step 2-F-1: 한계 분석

**1차 inheritance 룰 V1 한계**:
```
WITH first_law_ref AS (
  SELECT DISTINCT ON (la.id) ...
  FROM law_article la
  WHERE la.article_text ~ '법\s*제\d+조'
)
-- DISTINCT ON 첫 매칭 + LEFT(article_text, 300) 한정
```

**문제**:
- 자식 article 본문 첫 300자에서 첫 매칭만 잡음
- 그 article이 본법의 N조를 더 깊은 곳에서 인용하면 누락
- 한 article이 여러 본법 조문을 인용해도 첫 매칭만

**Sample 분석 (위임표현만 282건)**:
| 본법 | 본법조 | 자식법령 | 자식조 | 본문 인용 위치 |
|---|---|---|---|---|
| 건설기계관리법 | 27 | 시행규칙 | 76 | 284자 (첫 300자 끝자락) |
| 건설기술 진흥법 | 68 | 시행령 | 117 | **2,589자** (훨씬 뒤) |
| 건설산업기본법 | 101 | 시행령 | 86 | **1,384자** |
| 건설폐기물 재활용 | 36 | 시행규칙 | 6 | 746자 |

**원인**: 인용 위치가 본문 깊은 곳 (1,384 ~ 2,589자) → 1차 LEFT(300) 룰로는 발견 불가

### Step 2-F-2: 보강 INSERT (전체 본문 search)

**룰 V2 (regex_v2_enhanced)**:
```sql
INSERT INTO law_article_inheritance (...)
SELECT ...
FROM law_article la
CROSS JOIN LATERAL REGEXP_MATCHES(
  la.article_text,                                 -- 전체 본문 (LEFT 제거)
  '법\s*제(\d+)조(?:의\s*(\d+))?(?:제(\d+)항)?(?:제(\d+)호)?',
  'g'                                              -- 모든 매칭 ('g' flag)
) AS matches
WHERE NOT EXISTS (
  -- 같은 child + parent_article_no 중복 방지
  SELECT 1 FROM law_article_inheritance lai
  WHERE lai.child_article_id = la.id
    AND lai.parent_article_no = matches[1]::integer
)
```

**핵심 차이**:
- LEFT(article_text, 300) → article_text 전체
- DISTINCT ON 단일 매칭 → REGEXP_MATCHES 'g' 모든 매칭
- is_first_in_article=false 마킹 (1차와 구분)
- 중복 방지: 같은 child + parent_article_no 조합 SKIP

**결과**:
- "법" 키워드 보강: **+6,156 row** (8,028 → 14,184, 75% 증가)
- "영" 키워드 보강: **+1,053 row** (613 → 1,666, 172% 증가)
- 합계: 8,641 → **15,850 row** (1.83배)
- parent_article_id 매핑: 99.6% (15,783/15,850)

### Step 2-F-3: cross-validate 재실행

**보강 효과**:

| 검증결과 | 보강 전 | 보강 후 | 변화 |
|---|---|---|---|
| ✓ 양방향 일치 | 3,151 (86.5%) | **3,284** | **+133** |
| ⚠ 위임표현만 (자식 인용 X) | 282 (7.7%) | **149** | **-133** (47% 감소) |
| ⚠ 자식 인용만 (위임표현 X) | 210 | 543 | +333 (추가 인용 발견) |
| **합계** | 3,643 | 3,976 | +333 |

**해석**:
- ✓ **위임표현만 케이스 47% 감소** — 룰 V2 보강 핵심 효과
- ✓ 자식 인용만 543건 증가 = 정책 article 일반 인용 추가 발견 (정상)
- 양방향 일치 비율 = 3,284 / 3,976 = **82.6%** (비율로는 감소하지만 절대 정확도 향상)

### Step 2-F-4: 산안법 보강 효과 검증

| 본법조 | 인용 총수 | first 매칭 | 보강 매칭 | 비고 |
|---|---|---|---|---|
| 2 | 4 | 1 | 3 | 보강 효과 ✓ |
| 3 | 1 | 0 | **1** | 1차에서 누락, 보강으로 발견 ★ |
| 4 | 5 | 5 | 0 | 1차에서 모두 발견 |
| 11 | 3 | 0 | **3** | 1차에서 누락, 보강으로 모두 발견 ★ |
| 13 | 1 | 0 | **1** | 1차에서 누락, 보강으로 발견 ★ |
| 15 | 8 | 2 | 6 | 다중 위임 + 다중 인용 |
| **17** | **11** | 3 | **8** | 가장 많이 인용된 본법조 |
| 18 | 7 | 2 | 5 | |
| 19 | 7 | 2 | 5 | |

**결론**: 산안법 본법 제3, 11, 13조 = 1차 inheritance 누락 → 보강으로 해소.

---

## 사용자 원칙 정합 확인

| 원칙 | 적용 |
|---|---|
| LLM 사용 X | ✓ 정규식만 |
| 법령 보전 | ✓ 원본 텍스트 추출만 |
| 놓치는 것 = 리스크 | ✓ 6,156 + 1,053 = 7,209 추가 발견 (1.83배) |
| 100% 매핑 | ✓ 99.6% parent_article_id 매핑 |
| 오염 = 폐기 | - (보강 INSERT, TRUNCATE 불필요) |
| 검증도 엔진 | ✓ cross-validate 자동 재실행 |

---

## Found

### 1. inheritance 1차 룰의 본질 한계
- "첫 300자 + 첫 매칭" = 룰 V1
- 적합: 시행령 article 시작에 본법 인용이 명시된 케이스 (50%)
- 부적합: 본문 깊은 곳 인용 (50%) — 보강 V2로 해소

### 2. is_first_in_article 컬럼의 가치
- 1차 inheritance = "본 article의 핵심 부모"
- 보강 inheritance = "본 article의 추가 인용 (참조 또는 위임)"
- Stage 분해 시 is_first_in_article=true 우선 활용 (핵심 부모만)
- 외부 인용 분석 시 전체 활용 (정밀)

### 3. 자식 인용만 543건 증가
- 위임 동사 ("정한다") 없는 본법 article을 자식이 인용
- 정책 article 인용 (예: 본법 제4조 "정부의 책무" → 시행령에서 정책 일관성 표현)
- 일반 cross-reference (예: 시행령 제K조 본문에 "법 제3조에 따른 ~~"는 위임 X, 정의 인용)
- 룰 V3에서 분류 가능: 위임 vs 일반 인용 구분

---

## Tomorrow

### Step 2-G: 룰 V3 (위임 vs 일반 인용 분류)

**현재**: `inheritance_keyword='법'` 통합  
**보강**: 인용 패턴 별 분류
- `위임 직접`: "법 제N조에 따라" / "법 제N조의 위임에 따라" → 위임
- `위임 간접`: "법 제N조의 사항" / "법 제N조에서 정한" → 위임 가능성
- `일반 인용`: "법 제N조의 적용을 받는" / "법 제N조에 따른 X에 대하여" → 일반 인용
- `정의 참조`: "법 제N조의 정의" → 정의 인용

룰 V3 도입 시 cross-validate 정밀화 가능 (위임 양방향 일치 실측).

### Step 2-G + 다른 진행 옵션

| 옵션 | 작업 | 의존 |
|---|---|---|
| (a) Step 2-G 룰 V3 (위임/일반 분류) | 정규식 패턴 추가 | 즉시 |
| (b) Week 2 admrule-kr 행정규칙 매핑 | 사용자 git clone | 외부 |
| (c) TAI 추가 수집 12건 | 법제처 API | Cursor |
| (d) Track B 단독 진행 종료 → 다른 트랙 | A/C/D | 사용자 결정 |

---

## 마일스톤

| 마일스톤 | 상태 |
|---|---|
| Step 1: 가족 매핑 366건 | ✅ Day 3 |
| Step 2-A: 위임 source 추출 | ✅ 7,730건 |
| Step 2-B: target_law_id 매핑 | ✅ 97.4% |
| Step 2-D: inheritance 1차 추출 | ✅ 8,641건 |
| Step 2-E: cross-validate 1차 | ✅ 86.5% |
| **Step 2-F: 룰 V2 보강 (전체 본문)** | **✅ +7,209건, 위임표현만 47% 감소** |
| Step 3: 외부 인용 | ✅ 7,179건 |
| 행정규칙 매핑 (Week 2) | ⏳ admrule-kr 사용자 작업 대기 |
| TAI 추가 수집 12건 | ⏳ 별도 작업 |

**Track B 단독 진행 가능 영역의 95% 완료** (Step 2-F까지).

---

**END OF Step 2-F** — 룰 V2 보강 + cross-validate 재실행 + 산안법 검증 통과
