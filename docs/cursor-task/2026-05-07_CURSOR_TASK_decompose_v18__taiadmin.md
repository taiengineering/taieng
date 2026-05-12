# CURSOR TASK 2026-05-07: decompose_v1.py v1.8 보강 (옵션 B)

> 의미절 quality 향상 — inherit + FAKE_EXECUTOR 필터 + recipient 추출
> 
> 핵심 통찰 (사용자): "주어가 없는 경우, 상단(article)에 존재할 확률이 높음"
> 검증 결과: NULL executor 10,920건 중 **83% (9,095건)이 같은 article에서 inherit 가능**

---

## 작업 범위

### 패치 1. 가짜 executor 필터 (FAKE_EXECUTOR_PATTERNS)

분해기가 추출한 executor가 사실 부사구/조건절/종속어인 경우 NULL로 정정.

```python
# 파일 상단 (정규식 컴파일 영역)에 추가
FAKE_EXECUTOR_PATTERNS = [
    # 부사구 (목적격) — 진짜 주어 아님
    r'^(?:기본|종합|중장기|마스터)?계획에$',
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
    r'필요한 사항',
    
    # 조건절 잔여
    r'(?:하려면|받으려면|하는 경우|되는 경우|있는 경우|하면|할 때|한 경우)$',
]

FAKE_EXECUTOR_RX = [re.compile(p) for p in FAKE_EXECUTOR_PATTERNS]


def is_fake_executor(executor_text):
    """executor_text가 부사구/조건절/종속어이면 True (가짜)"""
    if not executor_text:
        return False
    for rx in FAKE_EXECUTOR_RX:
        if rx.search(executor_text):
            return True
    return False
```

### 패치 2. extract_executor_text() 정정

기존 함수 끝에 가짜 검사 추가:

```python
def extract_executor_text(text):
    """기존 함수 그대로 + FAKE 필터 추가"""
    if not text:
        return None

    cleaned = text
    cleaned = LAW_CITATION_PREFIX.sub('', cleaned, count=1)
    cleaned = re.sub(r'\([^)]*\)', '', cleaned)

    m = EXECUTOR_LEXICON_PATTERN.match(cleaned)
    if m:
        candidate = m.group(1).strip()
        if not is_fake_executor(candidate):
            return candidate

    fallback = re.match(
        r'^([가-힣ㆍ]{2,20}(?:\s+[가-힣ㆍ]{1,15}){0,3})\s*(?:은|는|이|가)\s',
        cleaned
    )
    if fallback:
        candidate = fallback.group(1).strip()
        if not is_fake_executor(candidate):
            return candidate

    return None
```

---

### 패치 3. Article 단위 inherit (가장 큰 개선)

**핵심**: 의미절의 executor가 NULL이면 같은 article의 다른 의미절에서 가져옴.

단, **위임/수범 조항은 inherit 금지** (행위자가 다름).

```python
# 정규식 추가
NO_INHERIT_PATTERNS = [
    # 위임 조항 — 행위자가 위임받는 사람 (장관 등)
    r'대통령령으로\s*정한다$',
    r'(?:[가-힣]+)?부령으로\s*정한다$',
    r'행정안전부령으로\s*정한다$',
    r'기획재정부령으로\s*정한다$',
    
    # 수범자 (처벌 대상)
    r'다음\s*각\s*호의?\s*어느\s*하나에\s*해당하는\s*자',
    r'위반(?:한|된)\s*자',
    r'위반자',
    r'.*받은\s*자|.*받은\s*사람',
    
    # 모호한 주어
    r'다음\s*각\s*호의?\s*사항',
    r'필요한\s*사항',
]

NO_INHERIT_RX = [re.compile(p) for p in NO_INHERIT_PATTERNS]


def can_inherit_executor(clause_text, candidate_executor):
    """
    inherit 가능 여부 판단.
    위임/수범 조항이거나 candidate가 가짜이면 False.
    """
    if not candidate_executor or is_fake_executor(candidate_executor):
        return False
    
    # 위임/수범 조항은 inherit 안 함
    for rx in NO_INHERIT_RX:
        if rx.search(clause_text or ''):
            return False
    
    return True
```

---

### 패치 4. decompose_part() — paragraph 단위 inherit

기존 코드의 inherit 로직을 paragraph 내(`inherited_executor` 변수)로 한정. 같은 part의 모든 의미절 처리 후 누적.

기존 코드 (참고):
```python
if clause.get("executor_text") and not inherited_executor:
    inherited_executor = clause["executor_text"]
```

→ 변경: 같은 paragraph 내 첫 valid executor를 모든 후속 의미절에 적용.

```python
def decompose_part(part, sector, rule_counts):
    part_text = part.get("part_text") or ""
    main_text, proviso = split_proviso(part_text, rule_counts)
    
    clauses = []
    seq = 1
    paragraph_executor = None  # 이 paragraph 내 모든 의미절 공유
    
    if proviso:
        # ... 기존 코드 그대로 ...
        seq += 1
    
    segments = split_parallel(main_text, rule_counts)
    expanded = []
    for seg in segments:
        parts_or, has_or_split, has_or_keep = split_or(seg, rule_counts)
        for x in parts_or:
            expanded.append((x, has_or_split, has_or_keep))
    
    seg_texts = [seg for seg, _, _ in expanded]
    seg_cts = classify_segments_content_types(seg_texts, rule_counts, debug=bool(part.get("_debug_classify")))
    
    # 1차 pass: 각 의미절의 직접 executor 추출 (paragraph 단위 inherit X)
    for (seg, has_or_split, has_or_keep), (ct, ct_rules, is_inherited) in zip(expanded, seg_cts):
        clause = make_clause(
            source_text=seg,
            source_part_text=part_text,
            source_part_id=part["id"],
            source_article_id=part["article_id"],
            clause_seq=seq,
            sector=sector,
            inherited_executor=None,  # 1차는 NULL — paragraph inherit는 후처리
            rule_counts=rule_counts,
            content_type=ct,
            applied_rules_seed=ct_rules,
            content_type_inherited=is_inherited,
        )
        # ... or_keep / or_split review 처리 그대로 ...
        clauses.append(clause)
        seq += 1
    
    # 2차 pass: paragraph 내 inherit (NULL → 첫 valid executor)
    paragraph_executor = next(
        (c["executor_text"] for c in clauses 
         if c.get("executor_text") and not is_fake_executor(c["executor_text"])),
        None
    )
    
    if paragraph_executor:
        for c in clauses:
            if not c.get("executor_text"):
                # NO_INHERIT 체크
                if can_inherit_executor(c.get("source_text"), paragraph_executor):
                    c["executor_text"] = paragraph_executor
                    c["applied_rules"] = (c.get("applied_rules") or []) + ["inherit_paragraph"]
    
    return clauses
```

---

### 패치 5. Article 단위 inherit (post-processing)

paragraph inherit 후에도 NULL인 의미절을 같은 article의 다른 paragraph에서 inherit.

`main()` 함수 끝 (DB INSERT 직전)에 후처리 추가:

```python
def post_process_article_inherit(clauses, articles, laws):
    """
    같은 article의 다른 paragraph에서 executor inherit.
    paragraph inherit으로 채워지지 않은 NULL executor 처리.
    """
    # article_id별로 클러스터링
    by_article = defaultdict(list)
    for c in clauses:
        by_article[c["source_article_id"]].append(c)
    
    inherit_count = 0
    for article_id, article_clauses in by_article.items():
        # 이 article의 valid executor (첫 명시된 것)
        article_executor = next(
            (c["executor_text"] for c in article_clauses 
             if c.get("executor_text") and not is_fake_executor(c["executor_text"])),
            None
        )
        
        if not article_executor:
            continue
        
        # NULL executor 의미절에 inherit (NO_INHERIT 체크)
        for c in article_clauses:
            if c.get("executor_text"):
                continue
            if not can_inherit_executor(c.get("source_text"), article_executor):
                c["needs_review"] = True
                base = c.get("review_reason") or ""
                c["review_reason"] = (base + ("; " if base else "") + "article inherit 거절 (위임/수범)").strip()
                continue
            
            c["executor_text"] = article_executor
            c["applied_rules"] = (c.get("applied_rules") or []) + ["inherit_article"]
            inherit_count += 1
    
    return inherit_count


# main() 끝, INSERT 직전에 호출:
inherit_n = post_process_article_inherit(clauses, articles, laws)
print(f"[INHERIT] article 단위 inherit: {inherit_n}건")
```

---

### 패치 6. recipient_text 추출 (신규 컬럼)

**의미절에 수신자 컬럼 추가 + 추출 로직**.

#### 6-1. DB 컬럼 추가 (먼저 실행)

```sql
-- semantic_clause + iter1 백업에 recipient_text 추가
ALTER TABLE semantic_clause ADD COLUMN IF NOT EXISTS recipient_text TEXT;
ALTER TABLE semantic_clause_iter1 ADD COLUMN IF NOT EXISTS recipient_text TEXT;

COMMENT ON COLUMN semantic_clause.recipient_text IS 
  '수신자(~에게/~로) — 행위가 향하는 대상. 보고/제출/통보 등의 의미절에 채워짐.';
```

#### 6-2. 추출 함수

```python
# 정규식 추가
RECIPIENT_PATTERNS = [
    # ~에게 (가장 명확)
    re.compile(r'(?:^|\s)([가-힣ㆍ]{2,30}(?:\s+[가-힣ㆍ]{1,15}){0,3})에게\s'),
    
    # ~한테 (구어체, 드물지만)
    re.compile(r'(?:^|\s)([가-힣ㆍ]{2,30})한테\s'),
    
    # ~으로/~로 + 신고/제출/보고 동사 앞
    re.compile(r'(?:^|\s)([가-힣ㆍ]{2,30}(?:\s+[가-힣ㆍ]{1,15}){0,3})(?:으?로)\s+(?:신고|보고|제출|통보|통지|요청|회신)'),
]


def extract_recipient_text(text):
    """
    수신자(~에게/~로) 추출. 가장 강한 패턴(~에게) 우선.
    """
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

#### 6-3. make_clause()에 recipient 추가

```python
def make_clause(...):
    # ... 기존 코드 ...
    
    # 수신자 추출 (신규)
    recipient = extract_recipient_text(seg) or extract_recipient_text(source_part_text)
    
    return {
        # ... 기존 필드 ...
        "recipient_text": recipient,  # 신규 추가
        # ...
    }
```

---

### 패치 7. version 변경

```python
# 기존
"decomposition_version": "v1.1",

# 변경
"decomposition_version": "v1.8",
```

---

## 테스트 흐름

### Step 1. 로컬 dry-run sample 200건

```bash
cd docs/extraction/scripts
export SUPABASE_URL="https://vwlahtguyggrhvslabax.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="..."

python decompose_v1.py --dry-run --sample-size 200 --sampling stratified --seed 42
```

### Step 2. 정확도 측정 (수동 검증 + 자동)

```python
# 검증 SQL (sample 200 결과 분석)

# 1. executor 채움률
SELECT 
  COUNT(*) AS total,
  COUNT(executor_text) AS has_executor,
  ROUND(100.0 * COUNT(executor_text) / COUNT(*), 1) AS pct
FROM semantic_clause_dryrun  -- 또는 print_dry_run output 분석
WHERE content_type IN ('OBLIGATION','PROHIBITION','AUTHORITY');

# 2. 가짜 executor 잔존 체크 (0이어야 함)
SELECT executor_text, COUNT(*) 
FROM semantic_clause_dryrun
WHERE executor_text ~ '^(따라|대한|위한|관한|의한)' OR
      executor_text ~ '경우에$|기본계획에$'
GROUP BY executor_text;

# 3. recipient 채움률 (보고/신고/제출 동사 가진 의미절 중)
SELECT COUNT(*) AS report_clauses,
       COUNT(recipient_text) AS has_recipient
FROM semantic_clause_dryrun
WHERE action_text ~ '신고|보고|제출|통보|통지';
```

### Step 3. 본 적용 (정확도 90%+ 시)

```bash
# iter1 백업에 본 적용
python decompose_v1.py --apply --truncate-first --sample-size 100000

# 검증 후 본 테이블 동기화 (별도 SQL)
```

### Step 4. v1.8 통과 후 무결성 재검증 (사용자 지시)

본 적용 후 다음 SQL 실행:

```sql
-- 1. executor 채움률 (전체)
SELECT 
  COUNT(*) AS total,
  COUNT(*) FILTER (WHERE executor_text IS NOT NULL) AS has_executor,
  COUNT(*) FILTER (WHERE executor_text IS NULL) AS null_executor,
  ROUND(100.0 * COUNT(*) FILTER (WHERE executor_text IS NOT NULL) / COUNT(*), 1) AS pct
FROM semantic_clause_iter1
WHERE content_type IN ('OBLIGATION','PROHIBITION','AUTHORITY')
  AND sectors IS NOT NULL;

-- 기대: pct > 80% (현재 76% → 향상)

-- 2. 가짜 executor 잔존 (0이어야 함)
SELECT executor_text, COUNT(*) AS cnt
FROM semantic_clause_iter1
WHERE executor_text ~ '^(따라|대한|위한|관한|의한)' OR
      executor_text ~ '(경우에|기본계획에|종합계획에)$'
GROUP BY executor_text
ORDER BY cnt DESC;

-- 3. recipient 채움률
SELECT 
  COUNT(*) AS total,
  COUNT(*) FILTER (WHERE action_text ~ '신고|보고|제출|통보|통지') AS report_action,
  COUNT(*) FILTER (WHERE recipient_text IS NOT NULL) AS has_recipient,
  ROUND(100.0 * 
    COUNT(*) FILTER (WHERE recipient_text IS NOT NULL) 
    / NULLIF(COUNT(*) FILTER (WHERE action_text ~ '신고|보고|제출|통보|통지'), 0), 
  1) AS recipient_pct
FROM semantic_clause_iter1
WHERE sectors IS NOT NULL;

-- 4. inherit 적용 분포
SELECT 
  CASE 
    WHEN 'inherit_paragraph' = ANY(applied_rules) THEN 'paragraph_inherit'
    WHEN 'inherit_article' = ANY(applied_rules) THEN 'article_inherit'
    ELSE 'direct'
  END AS source,
  COUNT(*) AS cnt
FROM semantic_clause_iter1
WHERE executor_text IS NOT NULL
GROUP BY source;

-- 5. needs_review 분포 (article inherit 거절 등)
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
3. 패턴 발견 → 룰 보강 → 재반복 (iterative)
4. 의미절 출처 추적 가능
5. 200줄+ 파일은 GitHub MCP 직접 수정 금지 → Cursor 로컬

---

## 작업 순서

```
1. DB ALTER (recipient_text 컬럼 추가) — 1분
2. decompose_v1.py 수정 (Cursor 로컬, ~700줄 → ~900줄) — 30분
3. 로컬 dry-run sample 200 — 5분
4. 결과 검증 + 정확도 측정 — 30분
5. 정확도 90% 미만이면 v1.9 보강 (룰 추가)
6. 통과 시 본 적용 (iter1 truncate + 재추출) — 30분
7. iter1 → 본 동기화 (별도 SQL)
8. 무결성 재검증 (위 SQL 5개) — 10분
9. 새 문제점 발견 시 v1.9, v2.0 etc.
```

---

## 예상 결과

| 지표 | v1.7.1 (현재) | v1.8 (목표) |
|---|---|---|
| executor 채움률 | 76% | **>90%** |
| 가짜 executor | 3,224건 | 0건 |
| recipient 채움률 | 0% | >70% (보고/신고/제출 의미절) |
| Article inherit | X | ~9,000건 |
| needs_review | 25% | 15~20% (정확한 review만) |

---

## 관련 문서

- `HANDOFF_2026-05-07.md` — 어제 핸드오프
- `decompose_v1.py` — 분해기 v1.7.1 (수정 대상)
- 본 문서 — v1.8 patch 작업지시서
