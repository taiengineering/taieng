# Cursor 작업지시서 — 의미절 분해 시스템 v1.1 첫 iteration

> 생성일: 2026-05-06
> 목적: 법령 paragraph part를 의미절 단위로 자동 분해하는 첫 iteration. 룰 기반(AI 0%), iterative refinement.
> 관련 결정: v3.1.1 NULL fix 보류 → 의미절 분해로 방향 전환

---

## 0. 배경 (왜 이 작업인가)

### 기존 방식의 한계
- `law_article_part.content_type` (115K parts에 단일 라벨) → part 단위가 너무 거칠어 룰 매칭 모호, NULL 40K 누락 발생
- `master_building_legal_rules` 2,002건은 production이지만 article과의 정규화된 FK 매핑 0건. 검증 매핑 0건. 학습 데이터로 직접 활용 불가

### 새 방향
의미절 단위 분해 + 라벨 → 한국어 어미/접속어 패턴이 명시적 분해점이 되어 룰 정확도 향상. SaaS의 작업 할당 단위(1 의미절 = 1 task)와도 일치.

### 파이프라인 (확정)
```
[1] 법령원문 (보유) → [2] 객체화 (거의 보유) →
[3] 의미절 분해 (이번 작업) → [4] 파싱저장 (이번 작업) →
[5] master_rule_v2 (다음) → [6] 문서매핑 (다음)
```

### 원칙 (불변)
- AI/LLM 호출 0%, 정규식 룰 기반만
- iterative refinement: 자동 분해 → 그룹 검증 → 룰 보강 반복
- 사용자(기획자)는 정답 만들기 X, 그룹 단위 판정 O
- 적용된 75K content_type, master_building_legal_rules 2,002건 등 기존 자산 미터치
- 첫 iter는 임시 테이블 (`semantic_clause_iter1`) — 스키마 자유 변경

---

## 1. 분해 단위 결정

**`paragraph` part만 의미절 분해 대상**. clause(호 enumeration)는 parent paragraph의 조건/대상으로 inherit, 단독 의미절로는 추출하지 않음.

이유: 호("18세 미만인 사람", "선발 예정 인원" 같은 명사구)는 의미절로 단독 서기 어려움. paragraph가 행위/조건/주기를 담는 자연 단위.

---

## 2. 임시 테이블 DDL

`apply_migration` (Supabase MCP) 또는 Supabase Studio SQL editor에서 실행.

```sql
CREATE TABLE IF NOT EXISTS semantic_clause_iter1 (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

  -- 출처 (1급 시민)
  source_part_id uuid NOT NULL REFERENCES law_article_part(id),
  source_article_id uuid NOT NULL REFERENCES law_article(id),
  clause_seq integer NOT NULL,
  source_text text NOT NULL,        -- 분해된 의미절 원문
  source_part_text text NOT NULL,   -- 부모 paragraph 전체 (감사용)

  -- 의미절 5요소 (첫 iter는 텍스트 위주, code화는 v2 이후)
  condition_text text,
  executor_text text,
  action_text text,
  cycle_text text,
  exception_text text,
  form_token text,                  -- "별지 제13호서식" 등

  -- 분류
  content_type text,                -- OBLIGATION/AUTHORITY/PROHIBITION/RECOMMENDATION/DELEGATION

  -- 추출 메타
  applied_rules text[] NOT NULL DEFAULT '{}',
  decomposition_version text NOT NULL DEFAULT 'v1.1',
  needs_review boolean NOT NULL DEFAULT false,
  review_reason text,

  -- 비교용 (모호한 분해 검증)
  alternative_kept_text text,       -- 분리하지 않았을 때의 결과 (있으면)

  -- 적용 범위 (sector만 일단)
  sector text,                      -- BUILDING/INDUSTRIAL/CONSTRUCTION/COMMON

  -- 타임스탬프
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_sci1_part_id ON semantic_clause_iter1(source_part_id);
CREATE INDEX IF NOT EXISTS idx_sci1_article_id ON semantic_clause_iter1(source_article_id);
CREATE INDEX IF NOT EXISTS idx_sci1_content_type ON semantic_clause_iter1(content_type);
CREATE INDEX IF NOT EXISTS idx_sci1_needs_review ON semantic_clause_iter1(needs_review) WHERE needs_review = true;
CREATE INDEX IF NOT EXISTS idx_sci1_sector ON semantic_clause_iter1(sector);
```

---

## 3. 분해기 v1.1 스크립트

**파일**: `docs/extraction/scripts/decompose_v1.py` (신규)

### 3-1. CLI

```python
parser.add_argument('--sample-size', type=int, default=50,
    help='첫 iter sample 크기. 기본 50.')
parser.add_argument('--dry-run', action='store_true',
    help='DB 쓰기 없이 stdout 출력만.')
parser.add_argument('--apply', action='store_true',
    help='실제 DB 적용. dry-run과 상호 배타.')
parser.add_argument('--truncate-first', action='store_true',
    help='적용 전 semantic_clause_iter1 truncate. 재실행 시.')
parser.add_argument('--seed', type=int, default=42,
    help='sampling seed. 같은 결과 재현용.')
```

`--dry-run`과 `--apply`는 둘 중 하나 필수. 둘 다 없으면 dry-run으로 fallback + 경고.

### 3-2. Sample 추출 (계층화 무작위)

대상: `law_article_part.part_type = 'paragraph'` AND article_type = '조문' AND KEC 법령 제외 (기존 v3.0 방식과 동일)

계층:
- sector: BUILDING / INDUSTRIAL / CONSTRUCTION / COMMON 4개
  - 추정 룰: law_article.law_id 또는 law_name → sector 매핑. 일단 단순히 law_name 키워드 매칭으로 시작 ("산업안전보건" → INDUSTRIAL, "건설" → CONSTRUCTION, "건축" → BUILDING, 그 외 → COMMON). 정확하진 않지만 sample 다양성 확보 목적이라 이 정도면 충분.
- 길이: 짧은(<150자) / 중간(150~400) / 긴(>400) 3개

총 4 × 3 = 12 그룹. sample-size 50 → 그룹당 약 4~5개씩 무작위.

`seed` 인자로 재현 가능.

### 3-3. 분해 룰 11개 (정규식)

```python
RULES = {
    'rule_1_proviso': {
        'pattern': r'다만,?\s*([^.]+(?:한다|된다)[^.]*\.)',
        'role': 'exception',
        'desc': '단서절 = 별도 의미절(예외)',
    },
    'rule_2_condition': {
        'pattern': r'([^.,]*?(?:한 경우|할 때|인 때에는|인 경우|에 한정하여)[,\s])',
        'role': 'condition',
        'desc': '조건절 → 다음 행위에 조건 부여',
    },
    'rule_3_parallel': {
        # "하여야 하며" 우선 매칭, fallback "하고/하며"
        'pattern_strong': r'([^.]+?하여야\s*하며,?\s*)',
        'pattern_weak': r'([^.]+?(?:하고|하며),?\s+)',
        'role': 'split_parallel',
        'desc': '병렬 행위 분리 (하여야 하며 = 강제+연결, 하고/하며 = 일반)',
    },
    'rule_4_or': {
        'pattern': r'([^.]+?(?:하거나|또는)\s+)',
        'role': 'split_or',
        'desc': 'OR 행위/대상 분리 (모호성 → needs_review)',
    },
    'rule_5_and': {
        'pattern': r'([가-힣A-Za-z0-9]+)\s*및\s*([가-힣A-Za-z0-9]+)',
        'role': 'and_marker',
        'desc': 'AND 결합 (행위/대상/조건 병렬, 모호성 → needs_review)',
        'always_review': True,  # 첫 iter는 모두 needs_review
    },
    'rule_6_obligation': {
        'pattern': r'(?:하여야\s*한다|해야\s*한다|두어야\s*한다)\.?$',
        'role': 'content_type',
        'value': 'OBLIGATION',
    },
    'rule_7_authority': {
        'pattern': r'할\s*수\s*있다\.?$',
        'role': 'content_type',
        'value': 'AUTHORITY',
    },
    'rule_8_prohibition': {
        'pattern': r'(?:아니\s*된다|아니하여야\s*한다|금지한다)\.?$',
        'role': 'content_type',
        'value': 'PROHIBITION',
    },
    'rule_9_cycle': {
        # 우선순위: 명시적 숫자 > 명시적 단어 > 정기적으로(fallback)
        'pattern_explicit': r'(매년|매월|매일|매\s*반기|매\s*분기|\d+\s*(?:년|개월|월|일|시간)\s*(?:마다|이내에?|내에?)|즉시|지체\s*없이)',
        'pattern_fallback': r'(정기적으로)',
        'role': 'cycle',
        'desc': '주기 추출 (명시적 우선, 정기적으로는 fallback)',
    },
    'rule_10_form': {
        'pattern': r'(별지\s*제\s*\d+\s*호\s*서식|별표\s*제?\s*\d+\s*호?)',
        'role': 'form_token',
        'desc': 'form 토큰 추출',
    },
    'rule_11_delegation': {
        'pattern': r'(?:에\s*따른다|에\s*의한다|에\s*의하여\s*한다)\.?$',
        'role': 'content_type',
        'value': 'DELEGATION',
    },
}
```

### 3-4. 분해 알고리즘 (간략)

```
def decompose(part_text):
    clauses = []
    
    # Step 1: 단서절(다만) 분리 → exception
    main_text, proviso = split_proviso(part_text)
    if proviso:
        clauses.append(make_clause(proviso, role='exception'))
    
    # Step 2: 병렬 분리 (하여야 하며 우선)
    segments = split_parallel(main_text)  # ["...하여야 하며", "...해야 한다"] 같은 list
    
    # Step 3: 각 segment에서 OR 분리
    expanded = []
    for seg in segments:
        if has_or(seg):
            expanded.extend(split_or(seg))
        else:
            expanded.append(seg)
    
    # Step 4: 각 segment에서 5요소 추출
    for seg in expanded:
        clause = {
            'condition_text': extract_condition(seg),
            'executor_text': extract_executor(seg),  # "사업주는", "관리자는" 등
            'action_text': extract_action(seg),
            'cycle_text': extract_cycle(seg),
            'form_token': extract_form(seg),
            'content_type': classify_content_type(seg),
            'applied_rules': matched_rule_ids,
            'needs_review': has_ambiguity(seg),
            'review_reason': ambiguity_reason,
        }
        clauses.append(clause)
    
    return clauses
```

executor 추출: 첫 명사 + 조사 "는/은/이/가" 패턴. 여러 paragraph에서 inherit.

### 3-5. dry-run 출력 형식

```
======================================================================
[의미절 분해 v1.1 — dry-run]
======================================================================

[INFO] sample_size=50, seed=42
[INFO] 계층화: BUILDING=12 INDUSTRIAL=12 CONSTRUCTION=12 COMMON=14
[INFO] 길이 분포: short=18 medium=20 long=12

[DECOMPOSE] 50 parts → N clauses (확장률 N/50)

[PATTERN MATCHING]
  rule_1_proviso (다만)             :  X건
  rule_2_condition (경우/때)        :  X건
  rule_3_parallel_strong (하여야 하며): X건
  rule_3_parallel_weak (하고/하며)   :  X건
  rule_4_or (하거나/또는)           :  X건  → review M건
  rule_5_and (및)                   :  X건  → review X건 (전부 review)
  rule_6_obligation (하여야 한다)    :  X건
  rule_7_authority (할 수 있다)     :  X건
  rule_8_prohibition (아니 된다)    :  X건
  rule_9_cycle_explicit             :  X건
  rule_9_cycle_fallback (정기적으로) : X건
  rule_10_form (별지/별표)          :  X건
  rule_11_delegation                :  X건

[CONTENT_TYPE 분포]
  OBLIGATION   : N건
  AUTHORITY    : N건
  PROHIBITION  : N건
  DELEGATION   : N건
  None (룰 미매칭): N건

[NEEDS_REVIEW] N건 (X%)
  - "및" 모호성    : N건
  - "또는" 모호성  : N건
  - executor 추출 실패: N건
  - content_type 미분류: N건

[SAMPLE 출력 5건] (sector 골고루)
  ─────────────────────────────────────────────
  [BUILDING] 산업안전보건법 제16조제1항
  PART 원문 (전체):
    "사업주는 안전 및 보건에 관한 사무를 총괄하여 관리할 안전보건관리책임자를 
     두어야 하며, 이 경우 안전관리자와 보건관리자를 지휘ㆍ감독한다."

  분해 결과 (2 clauses):
    [1] executor: 사업주
        action  : 안전 및 보건에 관한 사무를 총괄하여 관리할 안전보건관리책임자를 두어야 한다
        content_type: OBLIGATION
        applied_rules: [rule_3_parallel_strong, rule_5_and, rule_6_obligation]
        needs_review: true
        review_reason: "안전 및 보건" AND 결합 모호성
    [2] condition: 이 경우
        executor: 사업주 (inherit from [1])
        action  : 안전관리자와 보건관리자를 지휘ㆍ감독한다
        content_type: OBLIGATION (...한다)
        applied_rules: [rule_2_condition, rule_5_and]
        needs_review: true
        review_reason: "안전관리자와 보건관리자" AND 결합 (행위자 vs 대상)
  ─────────────────────────────────────────────
  ... (4건 더, 패턴 다양하게)

[DRY-RUN 종료] 실제 DB 쓰기 없음. 적용은 --apply 사용.
```

### 3-6. apply 모드

- `--truncate-first` 있으면 `TRUNCATE semantic_clause_iter1` 먼저
- batch insert (100건씩)
- supabase reconnect 1000건마다
- assert: insert된 row 수 = 분해된 clause 수

---

## 4. 실행 순서

### Step A — 마이그레이션

Supabase Studio 또는 Cursor에서 §2 DDL 실행.

검증:
```sql
SELECT COUNT(*) FROM semantic_clause_iter1;  -- 0
SELECT column_name FROM information_schema.columns WHERE table_name='semantic_clause_iter1' ORDER BY ordinal_position;
```

### Step B — 스크립트 작성

Cursor 컴포저에 다음 그대로 붙여넣기:

```
docs/extraction/CURSOR_TASK_2026-05-06_decompose_v11_iter1.md를 읽고
§3 사양에 따라 docs/extraction/scripts/decompose_v1.py를 새로 만들어줘.

규칙:
- AI/LLM 호출 0%, 정규식 룰만 (§3-3 11개 룰)
- 분해 단위는 paragraph part만 (§1)
- 계층화 무작위 sampling (§3-2)
- dry-run 출력 형식은 §3-5 그대로
- 모호 케이스("및", "또는")는 needs_review=true + review_reason 마크
- 한 파일 400줄 이내 권장
- 끝나면 git diff 변경 라인 수만 보고
```

### Step C — dry-run

```bash
cd ~/Desktop/tai-engineering/tai-admin
git pull origin main

railway run python3 docs/extraction/scripts/decompose_v1.py \
  --sample-size 50 --dry-run --seed 42 2>&1 | tee /tmp/decompose_iter1_dry.log

cat /tmp/decompose_iter1_dry.log
```

결과 chat에 통째로 붙임 → 사용자 그룹 검증 → 룰 v1.2 보강 결정

### Step D — 적용 (검증 통과 시)

```bash
railway run python3 docs/extraction/scripts/decompose_v1.py \
  --sample-size 50 --apply --seed 42 --truncate-first 2>&1 | tee /tmp/decompose_iter1_apply.log
```

### Step E — DB 검증

```sql
-- Iter1 적재 결과
SELECT
  COUNT(*) AS total_clauses,
  COUNT(DISTINCT source_part_id) AS source_parts,
  AVG(CASE WHEN needs_review THEN 1.0 ELSE 0 END) AS review_rate,
  COUNT(*) FILTER (WHERE content_type = 'OBLIGATION') AS obl,
  COUNT(*) FILTER (WHERE content_type = 'AUTHORITY') AS auth,
  COUNT(*) FILTER (WHERE content_type = 'PROHIBITION') AS proh,
  COUNT(*) FILTER (WHERE content_type IS NULL) AS unclassified
FROM semantic_clause_iter1;

-- review 케이스 sample 10건
SELECT clause_seq, source_text, action_text, applied_rules, review_reason
FROM semantic_clause_iter1
WHERE needs_review = true
LIMIT 10;
```

---

## 5. 검증 사이클 (사용자 작업)

dry-run 결과 받은 후:

1. **그룹별 판정** (룰별로 묶인 결과):
   - "rule_5_and 14건 중 분리가 맞은 케이스 N건 / 묶었어야 했던 케이스 M건"
   - "rule_3_parallel 17건 중 시간 순서로 잘못 분리된 케이스 K건"
2. **에러 패턴 → 룰 v1.2 보강 사항 도출**
3. v1.2 코드 수정 → §3 갱신 → 재실행 (Step C 반복)

수렴 기준:
- needs_review 비율 < 20%
- 사용자 검증에서 "분해 맞다" 비율 > 85%
- 위 둘 만족 시 sample 200~500건으로 확장 후 같은 사이클 반복

---

## 6. 보고

dry-run 끝나면 chat에 다음 그대로:

```bash
cat /tmp/decompose_iter1_dry.log
```

분석 + v1.2 보강 사항 도출은 제(Claude)가 정리.

---

## 7. 메모

- 첫 iter는 임시 테이블 `semantic_clause_iter1`. 스키마 변경 자유.
- 안정화되면 본 테이블 `semantic_clause` (인덱스/제약 강화)로 마이그레이션.
- master_rule_v2와 form_master는 의미절 분해 안정화 후 다음 작업.
- 기존 master_building_legal_rules 2,002건은 비교 검증용으로 보존 (새 시스템 결과와 obligation_summary 비교).
