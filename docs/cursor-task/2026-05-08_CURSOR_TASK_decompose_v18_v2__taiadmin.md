# CURSOR TASK 2026-05-08: decompose_v1.py v1.8 보강 (v2)

> **원본 v1.8 작업지시서 (`CURSOR_TASK_2026-05-07_decompose_v18.md`) 보강본**.
>
> 패턴 채굴 결과(`PATTERN_MINING_2026-05-08.md`) 반영 — content_type 재분류 + 누락 FAKE 패턴 추가 + recipient 정리.
>
> 핵심 통찰 (사용자): "주어가 없는 경우 상단(article)에 존재할 확률이 높음" — 검증 결과 73.1% inherit 가능.

---

## 변경 요약 (vs 원본 v1.8)

| 변경 | 설명 |
|---|---|
| **패치 0 (NEW)** | content_type 재분류 (DELEGATION 우선 판정) — OBLIGATION 11.8% 오분류 정정 |
| **패치 1 보강** | FAKE_EXECUTOR_PATTERNS 4개 누락 추가 (`종조사 잘림`, `령으로 정하`, `^다음 각 호`, `받은 자`) |
| **패치 6 보강** | RECIPIENT_PATTERNS에서 `~한테` 제거 (실데이터 0건) |
| 패치 2~5, 7 | **원본 v1.8 그대로 유지** |

원본 v1.8 작업지시서를 base로 보고, 본 문서의 변경분만 추가/수정하면 됨.

---

## 패치 0 (NEW). content_type 재분류 (DELEGATION 우선)

### 배경

OBLIGATION 33,537건 중 **3,974건 (11.8%)이 위임조항(DELEGATION)** 으로 오분류됨.

검증 패턴:
- `필요한 사항(은|을) ... 정한다` (2,850건)
- `대통령령으로 정한다` (1,297건)
- `~령으로 정한다` (2,633건)
- `정하여 고시한다` (763건)

### 코드 변경

#### 0-1. 정규식 추가 (파일 상단)

```python
# v1.8 NEW — 위임조항 우선 판정 패턴
DELEGATION_PATTERNS = [
    # "~필요한 사항은 ~으로/~장관/~위원회 정한다" (가장 흔함)
    r'필요한\s*사항(?:은|을)\s*.{0,60}정한다(?:\s*$|\s*[.,;])',
    # "~정하여 고시한다"
    r'정하여\s*고시한다(?:\s*$|\s*[.,;])',
    # "~으로/~령으로 정한다"
    r'(?:대통령령|행정안전부령|기획재정부령|[가-힣]+부령|[가-힣]+령)으?로\s*정한다(?:\s*$|\s*[.,;])',
    # "~에 위임한다"
    r'에\s*위임한다(?:\s*$|\s*[.,;])',
    # "~으로 정하여 ~할 수 있다"
    r'으?로\s*정하여\s*[가-힣]+(?:한다|수\s*있다)(?:\s*$|\s*[.,;])',
]

DELEGATION_RX = [re.compile(p) for p in DELEGATION_PATTERNS]


def is_delegation_clause(text):
    """텍스트가 위임조항이면 True"""
    if not text:
        return False
    for rx in DELEGATION_RX:
        if rx.search(text):
            return True
    return False
```

#### 0-2. classify_content_type() 보강

기존 분류 함수 (또는 분류 로직)의 **가장 앞**에 DELEGATION 우선 판정 추가:

```python
def classify_content_type(source_text, segment_text):
    """v1.8 — DELEGATION 우선 판정 추가"""
    
    # v1.8 NEW: 위임조항 우선 판정
    # 본문(source_text) 또는 segment에 위임 패턴이 있으면 DELEGATION
    if is_delegation_clause(source_text) or is_delegation_clause(segment_text):
        return 'DELEGATION'
    
    # 기존 분류 로직 (OBLIGATION/PROHIBITION/AUTHORITY/...)
    # ... existing code ...
```

**주의**: 분해기 코드 구조 확인 후, content_type을 결정하는 함수가 어디인지 정확히 파악해서 그 앞에 삽입. 현재 추정으로는 `classify_segments_content_types` 함수 내부일 가능성 높음.

#### 0-3. DELEGATION 의미절은 executor NULL

DELEGATION으로 재분류된 의미절은 행위 의무가 아니므로 executor가 의미 없음:

```python
def make_clause(...):
    # ... 기존 코드 ...
    
    # v1.8 NEW: DELEGATION이면 executor를 NULL로 강제
    if content_type == 'DELEGATION':
        clause['executor_text'] = None
        clause['inherited_executor'] = None
        # needs_review는 그대로 (위임 자체가 needs_review 대상은 아님)
    
    return clause
```

---

## 패치 1 보강. FAKE_EXECUTOR_PATTERNS 누락 추가

### 변경 내용

원본 v1.8의 `FAKE_EXECUTOR_PATTERNS` 리스트를 다음으로 **교체**:

```python
FAKE_EXECUTOR_PATTERNS = [
    # ============ 원본 v1.8 (유지) ============
    
    # 부사구 (목적격) — 진짜 주어 아님
    r'^(?:기본|종합|중장기|마스터)?계획(?:은|이|을|에)$',  # 보강: "계획은/이/을/에" 추가
    r'경우에$',
    r'^이 경우$',
    r'^다만',
    
    # 종속어 시작 (subject 추출 실패 잔여)
    r'^따라|^대한|^위한|^관한|^의한|^또는|^및',
    
    # 시점/위치 부사구
    r'시점에$|때에$|기간에$',
    r'중간에서|중에|중간',
    
    # 간접 주어
    r'관한 사항은$|대한 사항은$',
    r'필요한 사항',  # 보강 아래 참조
    
    # 조건절 잔여
    r'(?:하려면|받으려면|하는 경우|되는 경우|있는 경우|하면|할 때|한 경우)$',
    
    # ============ v1.8 v2 NEW (PATTERN_MINING_2026-05-08.md 결과) ============
    
    # NEW 1. 종조사 잘림 (split_or 후 잔여) — 858건, 가장 큰 누락
    r'\s(?:또|또는|및|에)$',
    
    # NEW 2. 위임 잘림 (위임조항 잔여) — 458건
    r'(?:대통령령|행정안전부령|기획재정부령|[가-힣]+부령|[가-힣]+령)으?로\s*정하?$',
    r'으?로\s*정하?$',
    
    # NEW 3. 수범자 (다음 각 호 ~) — 420건
    r'^다음\s*각\s*호',
    r'다음\s*각\s*호의?\s*어느\s*하나에\s*해당하는\s*자$',
    
    # NEW 4. 위임조항 잔여 (필요한 사항은 + 장관) — 404건
    r'^필요한\s*사항(?:은|을)\s+',  # "필요한 사항은 ~장관" 전체 잡기
    
    # NEW 5. 수범자 (받은 자/사람) — 88건
    r'받은\s*(?:자|사람)$',
    r'.+받은\s*자$',
    
    # NEW 6. 위반자 — 1건이지만 명시
    r'^위반자$|위반(?:한|된)\s*자$',
    
    # NEW 7. 너무 짧음
    # length<2 검사는 별도 함수에서 처리 (정규식 비효율)
]

FAKE_EXECUTOR_RX = [re.compile(p) for p in FAKE_EXECUTOR_PATTERNS]


def is_fake_executor(executor_text):
    """executor_text가 부사구/조건절/종속어/잘림이면 True"""
    if not executor_text:
        return False
    
    # 너무 짧음
    if len(executor_text.strip()) < 2:
        return True
    
    # 정규식 매칭
    for rx in FAKE_EXECUTOR_RX:
        if rx.search(executor_text):
            return True
    
    return False
```

### 검증 SQL (적용 후)

```sql
-- 가짜 잔존 체크 (모두 0이어야 함)
SELECT 
  COUNT(*) FILTER (WHERE executor_text ~ '\s(또|또는|및|에)$') AS jal_chodaen,
  COUNT(*) FILTER (WHERE executor_text ~ '령으로\s*정하?$') AS wiim_jal,
  COUNT(*) FILTER (WHERE executor_text ~ '^다음\s*각\s*호') AS soobum,
  COUNT(*) FILTER (WHERE executor_text ~ '^필요한\s*사항(은|을)') AS pilyo,
  COUNT(*) FILTER (WHERE executor_text ~ '받은\s*(자|사람)$') AS badeun,
  COUNT(*) FILTER (WHERE LENGTH(executor_text) < 2) AS too_short
FROM semantic_clause_iter1
WHERE content_type IN ('OBLIGATION','PROHIBITION','AUTHORITY')
  AND sectors IS NOT NULL;
```

---

## 패치 2~5. 원본 v1.8 그대로 유지

원본 `CURSOR_TASK_2026-05-07_decompose_v18.md` 그대로 적용:

- 패치 2: `extract_executor_text()` 정정 (FAKE 검사 추가)
- 패치 3: NO_INHERIT_PATTERNS (위임/수범 inherit 금지)
- 패치 4: paragraph 단위 inherit (decompose_part 변경)
- 패치 5: article 단위 inherit (post-processing)

**단**, NO_INHERIT_PATTERNS도 `FAKE_EXECUTOR_PATTERNS`처럼 패턴 채굴 결과로 보강할 수 있음 — 일단 원본 유지하고 dry-run에서 부족하면 v1.9에서 보강.

---

## 패치 6 보강. recipient_text 추출

### 변경 내용

원본의 `RECIPIENT_PATTERNS`에서 `~한테` **제거** (실데이터 0건):

```python
# v1.8 v2 — RECIPIENT_PATTERNS (수정)
RECIPIENT_PATTERNS = [
    # 1. ~에게 + 동사 (가장 강한 패턴, 4,845건)
    re.compile(
        r'(?:^|\s)([가-힣ㆍ]{2,30}(?:\s+[가-힣ㆍ]{1,15}){0,3})에게\s+'
        r'(?:.{0,30}?\s+)?(?:신고|보고|제출|통보|통지|요청|회신)'
    ),
    
    # 2. ~에게 + 일반 (5,509건 중 대부분, 후순위)
    re.compile(r'(?:^|\s)([가-힣ㆍ]{2,30}(?:\s+[가-힣ㆍ]{1,15}){0,3})에게\s'),
    
    # 3. ~으로/~로 + 신고/제출 동사 앞 (1,095건)
    re.compile(
        r'(?:^|\s)([가-힣ㆍ]{2,30}(?:\s+[가-힣ㆍ]{1,15}){0,3})'
        r'(?:으?로)\s+(?:신고|보고|제출|통보|통지|요청|회신)'
    ),
    
    # ❌ 제거: ~한테 (실데이터 0건)
]


def extract_recipient_text(text):
    """수신자(~에게/~로) 추출. 가장 강한 패턴(~에게 + 동사) 우선."""
    if not text:
        return None
    for rx in RECIPIENT_PATTERNS:
        m = rx.search(text)
        if m:
            candidate = m.group(1).strip()
            # 가짜 검사 (executor와 동일 룰)
            if not is_fake_executor(candidate):
                return candidate
    return None
```

나머지 (DB ALTER `recipient_text` 컬럼, `make_clause()` 추가)는 **이미 완료** (DB ALTER 완료 + recipient_text 컬럼 존재 확인됨).

---

## 패치 7. version 변경

```python
# 기존
"decomposition_version": "v1.7.1",

# 변경
"decomposition_version": "v1.8",
```

(v1.8 v2 작업이지만 버전은 v1.8 그대로 — v2는 보강 차수일 뿐.)

---

## 테스트 흐름 (변경 없음)

원본 v1.8 작업지시서와 동일:

```
1. DB ALTER recipient_text 컬럼 (✅ 이미 완료)
2. decompose_v1.py 수정 (Cursor 로컬, ~700줄 → ~950줄)
   - 패치 0 (DELEGATION 재분류) 추가
   - 패치 1 (FAKE) 보강
   - 패치 2~5 원본 v1.8 그대로
   - 패치 6 (recipient) 보강 (~한테 제거)
   - 패치 7 (version)
3. 로컬 dry-run sample 200 (stratified) — 5분
4. 정확도 측정 + 패턴 잔존 검증 (아래 SQL) — 30분
5. 정확도 90% 미만이면 v1.9 보강
6. 통과 시 본 적용 (iter1 truncate + 재추출) — 30분
7. iter1 → 본 동기화 (별도 SQL)
8. 무결성 재검증 (SQL 6개) — 10분
9. 새 문제 발견 시 v1.9, v2.0 etc.
```

---

## 검증 SQL (v1.8 적용 후, 6개)

```sql
-- 1. content_type 재분류 효과
SELECT content_type, COUNT(*) AS cnt
FROM semantic_clause_iter1
WHERE sectors IS NOT NULL
GROUP BY content_type
ORDER BY cnt DESC;
-- 기대: OBLIGATION ~29,500 (33,537 - 3,974 + 신규 inherit 분),
--       DELEGATION ~8,500 (4,625 + 3,974)


-- 2. executor 채움률 (전체 + DELEGATION 제외)
SELECT 
  COUNT(*) AS rule_total,
  COUNT(*) FILTER (WHERE executor_text IS NOT NULL) AS has_exec,
  ROUND(100.0 * COUNT(*) FILTER (WHERE executor_text IS NOT NULL) / COUNT(*), 1) AS pct
FROM semantic_clause_iter1
WHERE content_type IN ('OBLIGATION','PROHIBITION','AUTHORITY')
  AND sectors IS NOT NULL;
-- 기대: pct >= 90%


-- 3. 가짜 executor 잔존 (모두 0이어야 함)
SELECT 
  COUNT(*) FILTER (WHERE executor_text ~ '\s(또|또는|및|에)$') AS jal_chodaen,
  COUNT(*) FILTER (WHERE executor_text ~ '령으로\s*정하?$') AS wiim_jal,
  COUNT(*) FILTER (WHERE executor_text ~ '^다음\s*각\s*호') AS soobum,
  COUNT(*) FILTER (WHERE executor_text ~ '^필요한\s*사항(은|을)') AS pilyo,
  COUNT(*) FILTER (WHERE executor_text ~ '받은\s*(자|사람)$') AS badeun,
  COUNT(*) FILTER (WHERE executor_text ~ '^(따라|대한|위한|관한|의한)') AS jongsoke
FROM semantic_clause_iter1
WHERE content_type IN ('OBLIGATION','PROHIBITION','AUTHORITY');
-- 기대: 모두 0


-- 4. recipient 채움률 (보고/신고/제출/통보/통지)
SELECT 
  COUNT(*) AS report_total,
  COUNT(*) FILTER (WHERE recipient_text IS NOT NULL) AS has_recipient,
  ROUND(100.0 * COUNT(*) FILTER (WHERE recipient_text IS NOT NULL) / 
        NULLIF(COUNT(*), 0), 1) AS pct
FROM semantic_clause_iter1
WHERE action_text ~ '신고|보고|제출|통보|통지'
  AND content_type IN ('OBLIGATION','PROHIBITION','AUTHORITY')
  AND sectors IS NOT NULL;
-- 기대: pct >= 50% (보수)


-- 5. inherit 적용 분포
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
-- 기대: still_null < 10%, article_inherit ~9,000+, direct ~31,000


-- 6. needs_review 분포 (article inherit 거절 등)
SELECT review_reason, COUNT(*) AS cnt
FROM semantic_clause_iter1
WHERE needs_review = true
GROUP BY review_reason
ORDER BY cnt DESC
LIMIT 20;
```

---

## 작업 원칙 (불변)

1. AI/LLM 호출 0%
2. 검증 없는 완료 선언 금지
3. 패턴 발견 → 룰 보강 → 재반복 (iterative refinement)
4. 의미절 출처 추적 가능 (FK), AI 임의판단 추적/차단
5. **200줄+ 파일은 GitHub MCP 직접 수정 금지** → Cursor 로컬
6. 비-OBLIGATION inherit는 needs_review로 마크 (silent failure 방지)

---

## 작업 순서 (실행)

```
1. Cursor 로컬에서 docs/extraction/scripts/decompose_v1.py 열기
2. 본 문서 + 원본 v1.8 작업지시서를 baseline으로 삼아 7가지 패치 적용
   (패치 0 NEW, 패치 1 보강, 패치 2~5 원본 그대로, 패치 6 보강, 패치 7)
3. 로컬 dry-run:
   python decompose_v1.py --dry-run --sample-size 200 --sampling stratified --seed 42
4. dry-run 결과를 사용자(또는 본 채팅)에게 보고
5. 정확도 검증 후 본 적용 결정
```

---

## 예상 결과 (v1.8 v2)

| 지표 | v1.7.1 | 원본 v1.8 (목표) | v1.8 v2 (목표) |
|---|---|---|---|
| OBLIGATION → DELEGATION 정정 | — | — | **3,974건** |
| executor 채움률 (rule candidates) | 76.4% | >90% | **>90%** (분모 감소로 더 쉬움) |
| 가짜 executor 잔존 | 4,115건 | 0건 | **0건** |
| recipient 채움률 | 0% | >70% | **>50%** (보수적으로 하향) |
| article inherit | 0건 | ~9,000건 | **~11,000건** |
| needs_review 비율 | 49% | 15~20% | **15~20%** |

---

## 관련 문서

- `PATTERN_MINING_2026-05-08.md` — **본 문서의 채굴 근거**
- `CURSOR_TASK_2026-05-07_decompose_v18.md` — **원본 v1.8 작업지시서 (base)**
- `HANDOFF_FINAL_2026-05-07.md` — 어제 통합 핸드오프
- `decompose_v1.py` — 분해기 v1.7.1 (수정 대상)
- `DESIGN_master_rule_v2_2026-05-07.md` — Phase B 의존 (v1.8 통과 후)
