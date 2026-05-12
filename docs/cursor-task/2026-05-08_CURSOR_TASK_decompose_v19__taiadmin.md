# CURSOR TASK 2026-05-08: decompose_v1.py v1.9 (역순 추출 — extract_executor_text 본체 재설계)

> **v1.8 v2 dry-run 결과를 바탕으로 한 v1.9 보강 작업지시서**.
>
> 핵심 발견 (사용자 통찰 기반): 분해기가 텍스트 시작에서 매칭하는데, NULL executor 의미절의 **66.7%가 article ref / 대명사로 시작** → 시작 매칭 실패.
> 그러나 **84.8%는 텍스트 안에 "은/는/이/가" 주어 표지 보유** → 역순(텍스트 전체에서) 추출하면 잠재 해결.
>
> 채굴 결과: `PATTERN_MINING_2026-05-08_v2.md` 참조.

---

## 변경 요약 (vs v1.8)

| 패치 | 영향 범위 | 설명 |
|---|---|---|
| **패치 A (메인)** | `extract_executor_text` 본체 재설계 | 역순(`finditer`) 추출 + condition 영역 제외 + 사물 주어 needs_review |
| **패치 B** | DELEGATION_PATTERNS 보강 | `위임할 수 있다`, `위탁할 수 있다`, `~의 권한 ~ 위임` (AUTHORITY 누수 459건) |
| **패치 C** | FAKE_EXECUTOR_PATTERNS 좁히기 | v1.8의 `.+받은\s*자` 부작용 점검 (sample 4 "위탁받은 공단" 잘못 잡힘 가능성) |
| **패치 D** | `post_process_article_inherit` 호출 검토 | v1.8 review 메시지 0건 — 호출 자체 의심. 코드 확인. |
| **패치 E** | version | `decomposition_version`을 `v1.9`로 변경 + 헤더 print |

---

## 패치 A. extract_executor_text 본체 재설계 (메인)

### 핵심 변경

| | v1.8 | v1.9 |
|---|---|---|
| 매칭 방식 | `re.match()` — 텍스트 시작 1회 | `re.finditer()` — 모든 위치 |
| article ref 시작 처리 | ❌ 막힘 | ✅ 후보 cleanup으로 처리 |
| 다중 주어 처리 | ❌ 첫 매치 | ✅ condition 영역 제외 + 서술어 근접 |
| 사물 주어 처리 | ⚠️ 채워질 수 있음 | ✅ needs_review 마크 + NULL |

### 코드 추가/변경

#### A-1. 정규식 + 사물 lexicon (파일 상단에 추가)

```python
# v1.9 NEW — 역순 추출 알고리즘

# 모든 위치에서 주어 표지 매칭 (re.match가 아닌 re.finditer 사용)
SUBJECT_MARKER_PATTERN = re.compile(
    r'([가-힣ㆍ]{2,30}(?:\s+[가-힣ㆍ]{1,15}){0,4})\s*(은|는|이|가)\s'
)

# 후보에서 article ref / 부사구 prefix 제거 (cleanup)
# 예: "제2항에 따라 지정된 양성기관" → "지정된 양성기관"
SUBJECT_PREFIX_CLEANUP = re.compile(
    r'^.*?(?:에\s*따라|에\s*따른|에\s*의한|에\s*의해|에\s*따라\s*지정된|에\s*따라\s*승인된)\s*'
)

# 사물 주어 접미사 lexicon (행위자 아닌 사물/제도/금액)
OBJECT_SUBJECT_SUFFIXES = (
    # 금액성
    '부담금', '수수료', '수당', '여비', '보험료', '비용', '기준',
    '범위', '예산', '기간', '금액', '요금', '단가', '상금',
    # 행정성 (제도)
    '허가', '신고', '등록', '승인', '인가', '면허', '자격', '증명서',
    # 시설성
    '시설', '설비', '장비', '건축물', '공작물', '차량', '장치', '기기',
    # 기능성
    '권한', '업무', '직무', '책임', '의무',
)

OBJECT_SUBJECT_RX = re.compile(
    r'(?:' + '|'.join(re.escape(s) for s in OBJECT_SUBJECT_SUFFIXES) + r')$'
)


def is_object_subject(noun):
    """사물 주어 판별 (행위자 아님)"""
    if not noun:
        return False
    return bool(OBJECT_SUBJECT_RX.search(noun))


def cleanup_subject_candidate(noun):
    """후보에서 article ref / 부사구 prefix 제거"""
    if not noun:
        return noun
    cleaned = SUBJECT_PREFIX_CLEANUP.sub('', noun)
    if not cleaned or len(cleaned.strip()) < 2:
        return noun.strip()  # cleanup 실패 시 원본 (단 trim)
    return cleaned.strip()


def find_condition_end(text):
    """텍스트에서 조건절(경우/때) 끝 위치 식별. 없으면 -1."""
    if not text:
        return -1
    
    # 우선순위: 긴 표현 먼저
    candidates = [
        '경우에는', '때에는',
        '경우에', '때에',
    ]
    
    end = -1
    for c in candidates:
        idx = text.find(c)
        if idx >= 0:
            # 가장 마지막 조건절을 찾음 (조건이 여러 개면 마지막 이후 주어)
            last_idx = text.rfind(c)
            end = max(end, last_idx + len(c))
    
    return end
```

#### A-2. extract_executor_text_v19() 신규 함수

```python
def extract_executor_text_v19(source_text, content_type=None):
    """
    v1.9 역순 추출 알고리즘.
    
    Returns:
        (executor_text, review_flag)
        - executor_text: 추출된 행위자 또는 None
        - review_flag: 'object_subject' 또는 None
    """
    # 1. 행위자 없는 카테고리 early return
    if content_type in ('DELEGATION', 'DEFINITION', 'STATEMENT'):
        return None, None
    
    if not source_text:
        return None, None
    
    # 2. 괄호 제거 전처리 (alias / 보충 설명 제거)
    text_clean = re.sub(r'\([^)]*\)', '', source_text)
    
    # 3. 모든 위치에서 주어 표지 후보 수집
    candidates = []  # [(noun, marker, position)]
    for m in SUBJECT_MARKER_PATTERN.finditer(text_clean):
        raw_noun = m.group(1)
        marker = m.group(2)
        pos = m.start()
        
        # cleanup: article ref prefix 제거
        noun = cleanup_subject_candidate(raw_noun)
        
        if not noun or len(noun) < 2:
            continue
        
        # 가짜 필터 (v1.8 패치 1)
        if is_fake_executor(noun):
            continue
        
        candidates.append((noun, marker, pos))
    
    if not candidates:
        return None, None
    
    # 4. select_best_subject — condition 영역 제외 + 서술어 근접
    condition_end = find_condition_end(text_clean)
    
    if condition_end < 0:
        # 조건절 없음 → 모든 후보 활성
        outside = candidates
    else:
        outside = [c for c in candidates if c[2] >= condition_end]
        if not outside:
            # 모두 조건절 안 → 마지막 후보 (서술어 근접)
            outside = candidates
    
    # 가장 뒤쪽(서술어 근접) 후보
    outside.sort(key=lambda x: x[2], reverse=True)
    best_noun, best_marker, best_pos = outside[0]
    
    # 5. 사물 주어 검사
    if is_object_subject(best_noun):
        return None, 'object_subject'
    
    return best_noun, None
```

#### A-3. extract_executor_text() 통합

기존 `extract_executor_text()` 함수를 v1.9로 대체. 시그니처는 유지하되, 내부에서 v19 호출:

```python
def extract_executor_text(text, content_type=None):
    """
    v1.9 — 역순 추출.
    기존 시그니처 유지 (clauses 만들 때 review_flag도 별도 처리).
    """
    executor, _ = extract_executor_text_v19(text, content_type)
    return executor


def extract_executor_text_with_review(text, content_type=None):
    """
    v1.9 — review_flag도 함께 반환하는 새 함수.
    make_clause()에서 사용.
    """
    return extract_executor_text_v19(text, content_type)
```

#### A-4. make_clause() 변경

`make_clause()`에서 executor를 추출하는 위치에 v1.9 적용:

```python
def make_clause(...):
    # ... 기존 코드 ...
    
    # v1.9: extract_executor_text → extract_executor_text_with_review 사용
    # content_type이 결정된 후 호출 (DELEGATION이면 NULL early return)
    if content_type in ('DELEGATION', 'DEFINITION', 'STATEMENT'):
        clause_executor = None
        review_object = False
    else:
        clause_executor, review_flag = extract_executor_text_with_review(
            seg or source_part_text, 
            content_type
        )
        review_object = (review_flag == 'object_subject')
    
    clause = {
        # ... 기존 필드 ...
        'executor_text': clause_executor,
        # ...
    }
    
    # 사물 주어 needs_review 마크
    if review_object:
        clause['needs_review'] = True
        base_reason = clause.get('review_reason') or ''
        clause['review_reason'] = (
            base_reason + ('; ' if base_reason else '') + 
            '사물 주어 (행위자 부재)'
        ).strip()
    
    return clause
```

**주의**: paragraph/article inherit 적용 위치는 그대로 유지. 단 inherit 적용 시점에는 이미 추출된 executor가 NULL인 의미절에 대해서만 inherit 시도 (사물 주어 needs_review 케이스도 NULL이므로 inherit 시도되지만 가짜 필터 통과 안 함).

→ 사물 주어 케이스는 inherit으로 다시 채우는 것 방지 필요. `make_clause`에서 `review_object=True`면 `inherit_eligible=False` 플래그 추가:

```python
clause['_inherit_eligible'] = not review_object  # 내부 플래그

# post_process_article_inherit 등에서
if not c.get('_inherit_eligible', True):
    continue  # 사물 주어는 inherit 시도 안 함
```

---

## 패치 B. DELEGATION_PATTERNS 보강

v1.8 v2의 `DELEGATION_PATTERNS` 리스트에 다음 추가:

```python
DELEGATION_PATTERNS = [
    # ============ v1.8 v2 (유지) ============
    r'필요한\s*사항(?:은|을)\s*.{0,60}정한다(?:\s*$|\s*[.,;])',
    r'정하여\s*고시한다(?:\s*$|\s*[.,;])',
    r'(?:대통령령|행정안전부령|기획재정부령|[가-힣]+부령|[가-힣]+령)으?로\s*정한다(?:\s*$|\s*[.,;])',
    r'에\s*위임한다(?:\s*$|\s*[.,;])',
    r'으?로\s*정하여\s*[가-힣]+(?:한다|수\s*있다)(?:\s*$|\s*[.,;])',
    
    # ============ v1.9 NEW (AUTHORITY 누수 459건 잡기) ============
    
    # "위임할 수 있다" / "위탁할 수 있다" — AUTHORITY로 분류된 위임
    r'(?:위임|위탁)할\s*수\s*있다(?:\s*$|\s*[.,;])',
    
    # "권한 ~ 위임/위탁" 형태
    r'권한.{0,30}(?:위임|위탁)(?:할\s*수\s*있다|한다)(?:\s*$|\s*[.,;])',
    
    # "~로 위임/위탁한다" / "~로 위임할 수 있다"
    r'(?:으?로|에)\s*(?:위임|위탁)(?:할\s*수\s*있다|한다)(?:\s*$|\s*[.,;])',
]
```

`is_delegation_clause()` 함수는 변경 없음 (위 정규식만 보강).

`classify_content_type()`의 DELEGATION 우선 판정도 변경 없음.

---

## 패치 C. FAKE_EXECUTOR_PATTERNS — `.+받은\s*자` 좁히기

### 부작용 의심

v1.8의 `r'.+받은\s*자$'` 패턴이 문장 중간 "위탁받은 공단" 같은 표현을 가짜로 잡을 가능성.

### 검증 후 좁히기

```python
FAKE_EXECUTOR_PATTERNS = [
    # ... v1.8 v2 패턴 유지 ...
    
    # v1.8 NEW 5 (수범자 — 받은 자/사람) 좁히기
    # 변경 전: r'.+받은\s*자$'
    # 변경 후: 단어 경계에서 시작하거나 단순 형태만
    r'^[^\s]*받은\s*(?:자|사람)$',  # 단어 시작 받은 자
    r'^.{0,5}받은\s*(?:자|사람)$',  # prefix 매우 짧은 경우만 (가짜 추정)
    # 긴 prefix (위탁받은 공단 등)는 가짜로 보지 않음
]
```

또는 **단순화**: 그냥 `^받은\s*(?:자|사람)$` + `위반(?:한|된)\s*자`만 유지.

### 검증 SQL (적용 전후)

```sql
-- "위탁받은 X" 형태가 NULL executor가 되는지 확인
SELECT COUNT(*)
FROM semantic_clause
WHERE source_text ~ '위탁받은\s+[가-힣]'
  AND executor_text IS NULL
  AND content_type IN ('OBLIGATION','PROHIBITION','AUTHORITY');

-- 적용 후 위 결과가 줄어야 함
```

---

## 패치 D. post_process_article_inherit 호출 검토

### 의심

v1.8 dry-run 1000:
- `inherit_paragraph`: 29건
- `inherit_article`: 11건
- review_reason "article inherit 거절 (위임/수범)" : **0건**

→ `post_process_article_inherit` 함수가 거의 호출 안 됨 또는 candidate를 거의 못 찾는 상태.

### 점검 지점

```python
# main() 또는 분해기 진입점에서
def main():
    # ... 분해 처리 ...
    
    # post_process_article_inherit 호출이 있는지 확인
    inherit_n = post_process_article_inherit(clauses, articles, laws)
    print(f"[INHERIT] article 단위 inherit: {inherit_n}건")
    
    # ... DB write or dry-run output ...
```

### v1.9에서는 우선순위 낮춤

v1.9 역순 추출이 84.8%를 잡으면 article inherit 의존성이 줄어듦. 그러나 NULL executor + 표지 없음 1,656건(15.2%)은 여전히 inherit 필요.

**작업**: 
1. `post_process_article_inherit` 함수가 main() 끝에서 호출되는지 코드 확인
2. 호출 안 되고 있으면 추가
3. 호출되는데 candidate 못 찾는 거면 디버그 print 추가:
   ```python
   def post_process_article_inherit(clauses, articles, laws):
       inherit_count = 0
       articles_with_valid = 0
       for article_id, article_clauses in by_article.items():
           # ... 기존 로직 ...
           if article_executor:
               articles_with_valid += 1
           # ...
       
       print(f"[INHERIT DEBUG] articles_with_valid_executor: {articles_with_valid}")
       print(f"[INHERIT DEBUG] inherit applied: {inherit_count}")
       return inherit_count
   ```

---

## 패치 E. version 변경

```python
# 헤더 print
print("[의미절 분해 v1.9 — dry-run]")  # v1.8 → v1.9

# decomposition_version 필드
"decomposition_version": "v1.9",
```

---

## dry-run 검증 통계 블록 — v1.9 추가 지표

기존 v1.8 통계 블록에 다음 지표 추가:

```python
if dry_run:
    # ... v1.8 기존 지표 (executor 채움률, 가짜 잔존, recipient, inherit 분포) ...
    
    # ============ v1.9 NEW ============
    
    # 1. 사물 주어 needs_review 마크 건수
    object_review = sum(
        1 for c in rule_clauses 
        if c.get('needs_review') 
        and '사물 주어' in (c.get('review_reason') or '')
    )
    print(f"  - 사물 주어 needs_review: {object_review}건")
    
    # 2. extract 시도 → 성공/실패 분포
    extract_success = sum(
        1 for c in rule_clauses 
        if c.get('executor_text') 
        and 'inherit_paragraph' not in (c.get('applied_rules') or [])
        and 'inherit_article' not in (c.get('applied_rules') or [])
    )
    print(f"  - 직접 추출 성공: {extract_success}건")
    
    # 3. condition 영역 안에 잡힌 거짓 양성 검사
    # (executor가 텍스트 시작 부근이면 의심)
    suspicious_condition_subject = sum(
        1 for c in rule_clauses 
        if c.get('executor_text') 
        and c.get('condition_text')
        and c['executor_text'] in (c.get('condition_text') or '')
    )
    print(f"  - 의심: executor가 condition 안에 위치한 케이스: {suspicious_condition_subject}건")
```

---

## 테스트 흐름

```
1. Cursor 로컬에서 docs/extraction/scripts/decompose_v1.py 열기
2. 패치 A~E 적용 (~700줄 → ~1100줄 예상)
3. 로컬 dry-run sample 200 (작은 sample 우선 검증):
   railway run python3 decompose_v1.py --dry-run --sample-size 200 --sampling stratified --seed 42
4. 통계 + sample 5건 확인 → 알고리즘 정확도 1차 판정
5. 정확하면 sample 1000으로 재검증
   railway run python3 decompose_v1.py --dry-run --sample-size 1000 --sampling stratified --seed 42
6. 결과를 채팅에 가져와 보고 → 본 적용 결정
7. 본 적용 (iter1 truncate + 재추출):
   railway run python3 decompose_v1.py --apply --truncate-first
8. iter1 → 본 동기화 (별도 SQL)
9. 무결성 재검증 (검증 SQL 7개)
```

---

## 검증 SQL (v1.9 본 적용 후)

```sql
-- 1. executor 채움률 (전체)
SELECT 
  COUNT(*) AS total,
  COUNT(*) FILTER (WHERE executor_text IS NOT NULL) AS has_exec,
  ROUND(100.0 * COUNT(*) FILTER (WHERE executor_text IS NOT NULL) / COUNT(*), 1) AS pct
FROM semantic_clause_iter1
WHERE content_type IN ('OBLIGATION','PROHIBITION','AUTHORITY')
  AND sectors IS NOT NULL;
-- 기대: pct >= 90%


-- 2. 가짜 executor 잔존 (모두 0이어야 함)
SELECT 
  COUNT(*) FILTER (WHERE executor_text ~ '\s(또|또는|및|에)$') AS jal_chodaen,
  COUNT(*) FILTER (WHERE executor_text ~ '령으로\s*정하?$') AS wiim_jal,
  COUNT(*) FILTER (WHERE executor_text ~ '^다음\s*각\s*호') AS soobum,
  COUNT(*) FILTER (WHERE executor_text ~ '^필요한\s*사항(은|을)') AS pilyo,
  COUNT(*) FILTER (WHERE executor_text ~ '받은\s*(자|사람)$') AS badeun,
  COUNT(*) FILTER (WHERE LENGTH(executor_text) < 2) AS too_short
FROM semantic_clause_iter1
WHERE content_type IN ('OBLIGATION','PROHIBITION','AUTHORITY');


-- 3. 사물 주어 needs_review 마크 
SELECT COUNT(*) FROM semantic_clause_iter1 
WHERE review_reason ~ '사물 주어';
-- 기대: ~445건


-- 4. content_type 재분류 (DELEGATION 추가)
SELECT content_type, COUNT(*) AS cnt
FROM semantic_clause_iter1
WHERE sectors IS NOT NULL
GROUP BY content_type
ORDER BY cnt DESC;
-- 기대: DELEGATION ~9,000+ (v1.8 ~8,500 + v1.9 +459)


-- 5. recipient 채움률 (보고/신고/제출/통보/통지)
SELECT 
  COUNT(*) AS report_total,
  COUNT(*) FILTER (WHERE recipient_text IS NOT NULL) AS has_recipient,
  ROUND(100.0 * COUNT(*) FILTER (WHERE recipient_text IS NOT NULL) / 
        NULLIF(COUNT(*), 0), 1) AS pct
FROM semantic_clause_iter1
WHERE action_text ~ '신고|보고|제출|통보|통지'
  AND content_type IN ('OBLIGATION','PROHIBITION','AUTHORITY')
  AND sectors IS NOT NULL;
-- 기대: pct >= 50%


-- 6. inherit 분포 (v1.9에서는 의존도 낮아져야)
SELECT 
  CASE 
    WHEN 'inherit_paragraph' = ANY(applied_rules) THEN 'paragraph_inherit'
    WHEN 'inherit_article' = ANY(applied_rules) THEN 'article_inherit'
    WHEN executor_text IS NULL THEN 'still_null'
    ELSE 'direct'
  END AS source,
  COUNT(*) AS cnt
FROM semantic_clause_iter1
WHERE content_type IN ('OBLIGATION','PROHIBITION','AUTHORITY')
GROUP BY source
ORDER BY cnt DESC;
-- 기대: direct >> inherit, still_null < 10%


-- 7. v1.9 회귀 — 1000 dry-run still_null sample 5건이 채워졌는지
SELECT executor_text, source_text
FROM semantic_clause_iter1
WHERE source_text ~ '법 제48조의6제8항 단서에 따라 산재보험 노무제공자가'
   OR source_text ~ '제2항에 따라 지정된 전문인력 양성기관이.*경우에는 보건복지부장관과 식품의약품안전처장은'
   OR source_text ~ '업무를 위탁받은 공단.*위탁사업자.*다음 각 호의 업무를 한다'
   OR source_text ~ '징수한 원인자부담금은';
-- 기대: 4건 채움 ("노무제공자", "보건복지부장관과 식품의약품안전처장", "공단"), 1건 NULL+review (원인자부담금)
```

---

## 작업 원칙 (불변)

1. AI/LLM 호출 0%
2. 검증 없는 완료 선언 금지
3. 패턴 발견 → 룰 보강 → 재반복 (iterative refinement)
4. 의미절 출처 추적 가능 (FK), AI 임의판단 추적/차단
5. **200줄+ 파일은 GitHub MCP 직접 수정 금지** → Cursor 로컬
6. 사물 주어는 NULL + needs_review (정확함 우선)

---

## 예상 결과 (v1.9 후)

| 지표 | v1.7.1 | v1.8 v2 | **v1.9 (목표)** |
|---|---|---|---|
| executor 채움률 (rule candidates) | 76.4% | 77.3% | **>90%** |
| 가짜 7 패턴 잔존 | ~4,115 | 0 | 0 |
| recipient 채움률 (보고) | 0% | 58.2% | >50% |
| DELEGATION 재분류 | — | 3,974 (OBLIGATION) | + 459 (AUTHORITY) |
| 사물 주어 needs_review | — | — | ~445 |
| inherit 의존도 | 0건 | 40건 | 더 낮아짐 (역순이 잡음) |

---

## 관련 문서

- `PATTERN_MINING_2026-05-08_v2.md` — **v1.9 사전 채굴 (본 작업지시서의 근거)**
- `CURSOR_TASK_2026-05-08_decompose_v18_v2.md` — v1.8 v2 (이미 적용됨)
- `CURSOR_TASK_2026-05-07_decompose_v18.md` — v1.8 원본
- `decompose_v1.py` — v1.8 적용 상태 (수정 대상)
- `HANDOFF_FINAL_2026-05-07.md` — 통합 핸드오프
