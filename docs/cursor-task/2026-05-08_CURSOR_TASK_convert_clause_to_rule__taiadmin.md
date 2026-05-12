# CURSOR_TASK 2026-05-08 — semantic_clause → master_rule_v2 변환

> 의미절 v1.9.1 결과를 master_rule_v2 5 테이블로 자동 변환하는 스크립트 작성.
>
> **핵심 원칙: 모든 의미절 변환 (제외 없음). 사용 정책은 사용 단계 (View)에서 결정.**

---

## 1. 목적 & 원칙

### 목적
`semantic_clause` 58,495건 → `master_rule_v2` 58,495건 (1:1 매핑) + 부속 4 테이블 동시 INSERT.

### 원칙
1. **누락 0** — 모든 의미절을 변환. 분류 실패한 None 698건도 `rule_kind='UNCLASSIFIED'`로 보존.
2. **AI/LLM 호출 0%** — 정규식 + 키워드 사전만 사용.
3. **데이터 보존** — 의미절 종류(content_type)를 `rule_kind` 컬럼에 그대로 보존.
4. **사용 정책 분리** — 사업장 매칭에 어떤 룰을 쓸지는 **View**로 분리 (이 스크립트 밖 사안).
5. **검증 후 전체 적용** — sample 100건 dry-run → 사람 검토 → 전체 적용.
6. **재실행 가능** — `--truncate-first` 옵션으로 master_rule_v2 + 부속 4 테이블 비우고 재변환.

---

## 2. 입력 / 출력 명세

### 입력: `semantic_clause` (58,495 rows v1.9.1)

핵심 컬럼:
- `id` (uuid) → `master_rule_v2.source_clause_id`
- `source_article_id` → `master_rule_v2.source_article_id`
- `source_part_id` → 사용 안 함 (paragraph 추적은 article로 충분)
- `content_type` → `master_rule_v2.rule_kind`
- `executor_text` → `master_rule_executor` (role='EXECUTOR')
- `recipient_text` → `master_rule_executor` (role='RECIPIENT')
- `alternative_kept_text` → `master_rule_executor` (role='ALTERNATIVE')
- `action_text` → `master_rule_v2.what_action_text_raw` + 분류 → `what_action`
- `cycle_text` → `master_rule_v2.when_text_raw` + 파싱 → `when_*`
- `condition_text` → `master_rule_condition` (분리 INSERT)
- `exception_text` → `master_rule_exception` (5건만)
- `form_token` → `master_rule_v2.how_form`
- `sectors` (text[]) → `master_rule_v2.sectors`
- `source_text` → 분석 입력 (action_category 분류, scope 추출)
- `needs_review`, `review_reason` → `master_rule_v2.needs_review`, `review_reason`

### 출력 1: `master_rule_v2` (58,495 rows 예상)

| 컬럼 | 채움 정책 |
|---|---|
| `id` | uuid 자동 생성 |
| `rule_code` | 자동 생성 (아래 6번) |
| `source_clause_id` | clause.id |
| `source_article_id` | clause.source_article_id |
| `source_law_id` | law_article에서 SELECT (article_id → law_id) |
| `rule_kind` | clause.content_type or 'UNCLASSIFIED' (None인 경우) |
| `when_*` | cycle_text 파싱 (아래 7번) |
| `what_action` | action_text 분류 (정규식) |
| `what_target` | source_text에서 목적어 추출 (best-effort) |
| `what_action_text_raw` | action_text 그대로 |
| `how_method` | NULL (분해기에서 안 추출) |
| `how_form` | form_token |
| `sectors` | clause.sectors or {} (NULL이면 빈 배열) |
| `scope_*` | source_text에서 키워드 추출 (보유 10.2%만) |
| `why_obligation_summary` | source_text 원문 그대로 (또는 짧게 요약) |
| `why_law_citation` | law.law_name + article_no 조합 |
| `action_category_code` | action_text 분류 14 카테고리 (아래 8번) |
| `generation_method` | 'AUTO_REGEX' (default) |
| `generation_confidence` | 옵션 B 알고리즘 (아래 9번) |
| `status` | 'DRAFT' (default) |
| `needs_review` | clause.needs_review |
| `review_reason` | clause.review_reason |

### 출력 2: `master_rule_executor` (1~3 rows per rule)

```python
# 항상 INSERT
if clause.executor_text:
    INSERT (rule_id, role='EXECUTOR', role_label=clause.executor_text, 
            text_raw=clause.executor_text, sort_order=1)

# recipient 있으면
if clause.recipient_text:
    INSERT (rule_id, role='RECIPIENT', role_label=clause.recipient_text,
            text_raw=clause.recipient_text, sort_order=2)

# alternative 있으면
if clause.alternative_kept_text:
    INSERT (rule_id, role='ALTERNATIVE', role_label=clause.alternative_kept_text,
            text_raw=clause.alternative_kept_text, sort_order=3)
```

executor_text NULL인 의미절(421건 + 사물 주어 1,532건 + DELEGATION pure 4,866건)은 **master_rule_executor에 EXECUTOR row INSERT 안 함**. 룰 자체는 master_rule_v2에 들어가지만 실행자 미상.

### 출력 3: `master_rule_condition` (조건 보유 룰만)

`condition_text`가 있으면:
- "또는" / "및" / ";" 등으로 분리 가능하면 다중 row
- 분리 안 되면 단일 row
- `sort_order` 1부터 시작

조건 분리는 단순 split (정규식 `[,;]\s*|또는|또한`). 복잡한 구조는 단일 row로 처리.

### 출력 4: `master_rule_exception` (5건만)

`exception_text` 있으면 INSERT. 5건뿐이라 단순 처리.

### 출력 5: `master_rule_relation` 

이번 스크립트는 **건드리지 않음**. Phase B 후속 작업 (룰 그룹화)에서 채움.

---

## 3. 알고리즘 — 7단계

### Step 1. semantic_clause SELECT

```python
clauses = supabase.table('semantic_clause').select(
    'id, source_article_id, source_part_id, '
    'content_type, executor_text, recipient_text, alternative_kept_text, '
    'action_text, cycle_text, condition_text, exception_text, form_token, '
    'sectors, source_text, source_part_text, '
    'needs_review, review_reason'
).limit(sample_size).execute()
```

`--sample-size 100000` (모집단)로 전체 처리. 또는 `--sample-size 100` (sample 100건).

### Step 2. law_article에서 source_law_id + law_name 조회

```python
articles = supabase.table('law_article').select(
    'id, source_law_id, law_name, article_no'
).in_('id', [c.source_article_id for c in clauses]).execute()
```

article_id → (law_id, law_name, article_no) 매핑 dict 만들기.

### Step 3. 각 clause를 master_rule_v2 row로 변환

```python
def convert(clause, article_meta):
    # 3-1. rule_kind 결정
    rule_kind = clause.content_type or 'UNCLASSIFIED'
    
    # 3-2. when_* 파싱 (cycle_text → cycle_type/value/unit/due_days/base_event)
    when = parse_when(clause.cycle_text, clause.action_text)
    
    # 3-3. what_action 분류 (action_text → 동사 표제어)
    what_action = classify_what_action(clause.action_text)
    
    # 3-4. how_form
    how_form = clause.form_token  # 그대로
    
    # 3-5. sectors / scope_*
    sectors = clause.sectors or []
    scope = extract_scope(clause.source_text)  # 키워드 매칭 (10.2%만 채움)
    
    # 3-6. why
    why_summary = clause.source_text[:500]  # 길이 제한
    why_citation = f"{article_meta['law_name']} {article_meta['article_no']}"
    
    # 3-7. action_category_code (14 카테고리)
    action_cat = classify_action_category(clause.action_text)
    
    # 3-8. generation_confidence (옵션 B)
    confidence = calc_confidence_v19(clause)
    
    # 3-9. rule_code
    rule_code = generate_rule_code(article_meta, clause)
    
    return {
        'rule_code': rule_code,
        'source_clause_id': clause.id,
        'source_article_id': clause.source_article_id,
        'source_law_id': article_meta['source_law_id'],
        'rule_kind': rule_kind,
        **when,
        'what_action': what_action,
        'what_action_text_raw': clause.action_text,
        'how_form': how_form,
        'sectors': sectors,
        **scope,
        'why_obligation_summary': why_summary,
        'why_law_citation': why_citation,
        'action_category_code': action_cat,
        'generation_method': 'AUTO_REGEX',
        'generation_confidence': confidence,
        'status': 'DRAFT',
        'needs_review': clause.needs_review,
        'review_reason': clause.review_reason,
    }
```

### Step 4. master_rule_v2 batch INSERT (100건 단위)

```python
for chunk in chunks(rules, 100):
    supabase.table('master_rule_v2').insert(chunk).execute()
```

### Step 5. master_rule_executor batch INSERT

INSERT된 master_rule_v2 row의 id를 받아서 부속 테이블 채움:

```python
for clause in clauses:
    rule_id = clause_to_rule_id[clause.id]
    
    executors = []
    if clause.executor_text:
        executors.append({
            'rule_id': rule_id, 'role': 'EXECUTOR',
            'role_label': clause.executor_text, 'text_raw': clause.executor_text,
            'sort_order': 1,
        })
    if clause.recipient_text:
        executors.append({
            'rule_id': rule_id, 'role': 'RECIPIENT',
            'role_label': clause.recipient_text, 'text_raw': clause.recipient_text,
            'sort_order': 2,
        })
    if clause.alternative_kept_text:
        executors.append({
            'rule_id': rule_id, 'role': 'ALTERNATIVE',
            'role_label': clause.alternative_kept_text, 
            'text_raw': clause.alternative_kept_text,
            'sort_order': 3,
        })
    if executors:
        supabase.table('master_rule_executor').insert(executors).execute()
```

### Step 6. master_rule_condition / master_rule_exception batch INSERT

```python
# condition (분리 + INSERT)
for clause in clauses_with_condition:
    rule_id = clause_to_rule_id[clause.id]
    parts = split_conditions(clause.condition_text)  # 또는/및/; 으로 분리
    for i, p in enumerate(parts):
        supabase.table('master_rule_condition').insert({
            'rule_id': rule_id,
            'condition_text': p,
            'sort_order': i + 1,
        }).execute()

# exception (5건뿐)
for clause in clauses_with_exception:
    rule_id = clause_to_rule_id[clause.id]
    supabase.table('master_rule_exception').insert({
        'rule_id': rule_id,
        'exception_text': clause.exception_text,
        'sort_order': 1,
    }).execute()
```

### Step 7. 통계 출력 + 검증

```
[CONVERT] 58495 clauses → 58495 rules
[INSERT] master_rule_v2: 58495 rows
[INSERT] master_rule_executor: 53000 rows (executor 41349 + recipient 11284 + alt 367)
[INSERT] master_rule_condition: 18569 rows  
[INSERT] master_rule_exception: 5 rows
[STATS] rule_kind:
  OBLIGATION: 29665
  AUTHORITY: 10470
  DELEGATION: 9055
  DEFINITION: 6471
  PROHIBITION: 1742
  STATEMENT: 390
  UNCLASSIFIED: 702
[STATS] confidence avg: 0.84 (옵션 B)
[STATS] needs_review: 30753 / 58495 (52.6%)
[DONE]
```

---

## 4. rule_code 자동 생성 패턴

```python
def generate_rule_code(article_meta, clause):
    """
    형식: LAW_{law_id_short}_ART_{article_no}_CL_{clause_seq}
    예: LAW_a3f2_ART_제8조_CL_1
    
    UNIQUE 제약 보장: source_clause_id가 유일하므로 같은 의미절 = 같은 코드
    """
    law_short = str(article_meta['source_law_id'])[:4]
    article_no = article_meta['article_no'] or 'unknown'
    return f"LAW_{law_short}_ART_{article_no}_CL_{clause.clause_seq}"
```

⚠️ rule_code UNIQUE 제약 — 중복 시 INSERT 실패. clause_seq + article_no가 보장하면 UNIQUE.

대안: 단순 UUID 사용. `rule_code = str(clause.id)[:12]`도 OK.

---

## 5. action_category 14 카테고리 매칭 규칙

```python
def classify_action_category(action_text):
    if not action_text:
        return 'OTHER'
    
    # 우선순위 매칭 (먼저 매칭되는 카테고리 선택)
    rules = [
        (r'점검|진단|검사|확인',                    'INSPECTION'),
        (r'위험성\s*평가|위해\s*평가',              'RISK_ASSESSMENT'),
        (r'교육|훈련',                              'EDUCATION'),
        (r'측정|계측',                              'MEASUREMENT'),
        (r'보고|신고|통보|통지|제출',               'REPORT'),
        (r'설치|비치|구비',                         'INSTALL'),
        (r'기록|보존|작성|보관',                    'RECORD'),
        (r'알림|고지|공지|공표',                    'NOTIFY'),
        (r'조치|시정|개선|보호',                    'ACTION'),
        (r'작업\s*방법|작업\s*절차',                'WORK_METHOD'),
        (r'승인|허가|인가|면허',                    'APPROVAL'),
        (r'보호구|보호\s*장비|안전\s*장비',         'PROTECTION'),
        (r'체계|시스템|구축',                       'SYSTEM'),
    ]
    
    for pattern, code in rules:
        if re.search(pattern, action_text):
            return code
    
    return 'OTHER'  # 14번째 카테고리
```

미분류 21,039건 → 'OTHER' 카테고리.

⚠️ master_rule_v2.action_category_code는 NOT NULL — 'OTHER' default 처리해야.

---

## 6. when_* 파싱 (cycle_text + action_text)

```python
def parse_when(cycle_text, action_text):
    """
    cycle_text → when_cycle_type/value/unit/due_days/base_event/text_raw
    
    cycle_type 표준값:
      - 'RECURRING': 매년/매월/매주/매일 (반복)
      - 'INTERVAL': N년/N개월 마다 (간격)
      - 'DUE': N일 이내 (기한)
      - 'BASE_EVENT': 작업 전/후/즉시 (이벤트 기준)
      - NULL: 미명시
    """
    when = {
        'when_cycle_type': None,
        'when_cycle_value': None,
        'when_cycle_unit': None,
        'when_due_days': None,
        'when_base_event': None,
        'when_text_raw': cycle_text,
    }
    
    if not cycle_text:
        # action_text에서 base_event 추출 시도
        if action_text:
            m = re.search(r'(작업\s*전|착공\s*전|운전\s*전|발생\s*시|발생\s*후|완료\s*후|즉시|지체\s*없이)', action_text)
            if m:
                when['when_base_event'] = m.group(1)
                when['when_cycle_type'] = 'BASE_EVENT'
        return when
    
    # 1. RECURRING
    m = re.search(r'매(년|월|주|일|분기)', cycle_text)
    if m:
        when['when_cycle_type'] = 'RECURRING'
        when['when_cycle_unit'] = {'년':'YEAR','월':'MONTH','주':'WEEK','일':'DAY','분기':'QUARTER'}[m.group(1)]
        when['when_cycle_value'] = 1
        return when
    
    # 2. INTERVAL
    m = re.search(r'(\d+)\s*(년|개월|월|주|일)\s*마다', cycle_text)
    if m:
        when['when_cycle_type'] = 'INTERVAL'
        when['when_cycle_value'] = int(m.group(1))
        when['when_cycle_unit'] = {'년':'YEAR','개월':'MONTH','월':'MONTH','주':'WEEK','일':'DAY'}[m.group(2)]
        return when
    
    # 3. DUE
    m = re.search(r'(\d+)\s*일\s*이내', cycle_text)
    if m:
        when['when_cycle_type'] = 'DUE'
        when['when_due_days'] = int(m.group(1))
        return when
    
    m = re.search(r'(\d+)\s*개월\s*이내', cycle_text)
    if m:
        when['when_cycle_type'] = 'DUE'
        when['when_due_days'] = int(m.group(1)) * 30
        return when
    
    # 4. BASE_EVENT (cycle_text에 있는 경우)
    m = re.search(r'(작업\s*전|착공\s*전|발생\s*후|완료\s*후|즉시)', cycle_text)
    if m:
        when['when_base_event'] = m.group(1)
        when['when_cycle_type'] = 'BASE_EVENT'
    
    return when
```

---

## 7. 신뢰도 알고리즘 (옵션 B — 핵심 4 + 보조 보너스)

```python
def calc_confidence_v19(clause):
    """
    핵심 4요소 (WHO/WHAT/WHERE/WHY) 충족 = 0.7 (base)
    보조 추가 시 +0.075 each
      - WHEN (cycle 또는 base_event)
      - HOW (form)
      - recipient
      - condition
    
    최대 1.0
    """
    if clause.content_type in ('STATEMENT', 'DELEGATION', 'DEFINITION'):
        # 사업장 적용 룰 아님 — 별도 신뢰도
        return 0.5  # 정보 보존 가치는 있으나 룰 매칭 신뢰도 낮음
    
    # 핵심 4요소
    has_who = bool(clause.executor_text)
    has_what = bool(clause.action_text)  # 항상 True
    has_where = bool(clause.sectors)  # 사실상 항상 True (변환 후보 조건)
    has_why = bool(clause.source_text)  # 항상 True
    
    if not (has_who and has_what and has_where and has_why):
        # 핵심 결손 — 낮은 신뢰도
        return 0.5 - (4 - sum([has_who, has_what, has_where, has_why])) * 0.1
    
    confidence = 0.7  # base
    
    # 보조 보너스
    if clause.cycle_text or re.search(
        r'작업\s*전|착공\s*전|발생\s*후|완료\s*후|즉시|지체\s*없이|\d+일\s*이내',
        clause.action_text or ''):
        confidence += 0.075
    
    if clause.form_token:
        confidence += 0.075
    
    if clause.recipient_text:
        confidence += 0.075
    
    if clause.condition_text:
        confidence += 0.075
    
    return min(confidence, 1.0)
```

예상 분포:
- ~80% 의미절: 0.7~0.85 (핵심 4 + 보조 0~2개)
- ~15%: 0.85~1.0 (보조 3~4개 보유)
- ~5%: 0.5 미만 (사물 주어, 핵심 결손)

---

## 8. 명령

```bash
cd docs/extraction/scripts

# Step 8-1. dry-run sample 100건 — 출력만 (DB 변경 없음)
railway run python3 convert_clause_to_rule.py --dry-run --sample-size 100

# Step 8-2. 전체 변환 실행 (sample-size 명시 필수!)
railway run python3 convert_clause_to_rule.py --apply --truncate-first --sample-size 100000 2>&1 | tee /tmp/convert_apply.log

# 진행률 모니터링
tail -f /tmp/convert_apply.log
```

⚠️ **`--sample-size` 명시 필수** (default 50 사고 학습).

---

## 9. argparse 사양

```python
parser.add_argument('--dry-run', action='store_true')
parser.add_argument('--apply', action='store_true')
parser.add_argument('--truncate-first', action='store_true', 
                    help='적용 전 master_rule_v2 + 4 부속 테이블 비움')
parser.add_argument('--sample-size', type=int, default=100,
                    help='처리할 의미절 수. 전체 처리는 100000+ 명시.')
parser.add_argument('--start-from', type=int, default=0,
                    help='몇 번째 의미절부터 시작 (재개용)')
```

---

## 10. 검증 SQL (변환 후)

```sql
-- 1. master_rule_v2 row 수 확인
SELECT COUNT(*) FROM master_rule_v2;
-- 예상: 58495

-- 2. rule_kind 분포 — semantic_clause와 일치해야
SELECT rule_kind, COUNT(*) FROM master_rule_v2 GROUP BY rule_kind ORDER BY COUNT(*) DESC;
-- 예상: OBLIGATION 29665, AUTHORITY 10470, DELEGATION 9055, ...

-- 3. source_clause_id FK 무결성
SELECT COUNT(*) FROM master_rule_v2 mrv
LEFT JOIN semantic_clause sc ON mrv.source_clause_id = sc.id
WHERE sc.id IS NULL;
-- 예상: 0

-- 4. master_rule_executor row 수
SELECT role, COUNT(*) FROM master_rule_executor GROUP BY role;
-- 예상: EXECUTOR 41349, RECIPIENT 11284, ALTERNATIVE ?

-- 5. master_rule_condition row 수
SELECT COUNT(*) FROM master_rule_condition;
-- 예상: ~18500+ (분리 후 더 많음)

-- 6. action_category 분포
SELECT action_category_code, COUNT(*) FROM master_rule_v2 
GROUP BY action_category_code ORDER BY COUNT(*) DESC;
-- 예상: OTHER ~21000, REPORT ~9000, INSPECTION ~4900, ...

-- 7. confidence 분포
SELECT 
  CASE 
    WHEN generation_confidence >= 0.85 THEN 'high'
    WHEN generation_confidence >= 0.7 THEN 'medium'
    WHEN generation_confidence >= 0.5 THEN 'low'
    ELSE 'very_low'
  END AS bucket,
  COUNT(*)
FROM master_rule_v2
GROUP BY bucket;
-- 예상: medium ~80%, high ~15%, low/very_low ~5%

-- 8. sectors 보존 확인
SELECT COUNT(*) FROM master_rule_v2 WHERE sectors IS NULL OR sectors = '{}';
-- 예상: 161 (INACTIVE)
```

---

## 11. 사용 단계 — View 4개 (이번 작업 밖, 후속 작업)

별도 마이그레이션으로 추가:

```sql
-- 11-1. 사업장 매칭용 (가장 중요)
CREATE VIEW master_rule_v2_active AS
SELECT mrv.*
FROM master_rule_v2 mrv
WHERE mrv.rule_kind IN ('OBLIGATION', 'PROHIBITION', 'AUTHORITY')
  AND mrv.status = 'VALIDATED'
  AND array_length(mrv.sectors, 1) > 0;

-- 11-2. 정부 행위 분석용
CREATE VIEW master_rule_v2_government AS
SELECT * FROM master_rule_v2 WHERE rule_kind = 'DELEGATION';

-- 11-3. 정의 참고용
CREATE VIEW master_rule_v2_definitions AS
SELECT * FROM master_rule_v2 WHERE rule_kind = 'DEFINITION';

-- 11-4. 검토 대상
CREATE VIEW master_rule_v2_review_queue AS
SELECT * FROM master_rule_v2
WHERE rule_kind = 'UNCLASSIFIED' OR needs_review = true;
```

이번 작업에서는 View 만들지 않음. 변환 완료 후 별도 SQL로 추가.

---

## 12. 작업 흐름 (3단계)

### 단계 1. 스크립트 작성 (Cursor)

`docs/extraction/scripts/convert_clause_to_rule.py` 생성. 위 알고리즘 7단계 구현.

### 단계 2. dry-run sample 100 + 사람 검토

```bash
railway run python3 convert_clause_to_rule.py --dry-run --sample-size 100
```

출력 sample 5건 직접 확인:
- rule_kind 정확한가
- when_* 파싱 정확한가
- action_category 적절한가
- confidence 합리적인가
- executor / recipient / condition 분리 정확한가

문제 있으면 알고리즘 보강 → dry-run 재실행.

### 단계 3. 전체 변환

```bash
railway run python3 convert_clause_to_rule.py --apply --truncate-first --sample-size 100000
```

검증 SQL 8개 실행 → 모두 예상치와 일치 확인.

---

## 13. 주의사항

1. **`--sample-size 100000` 명시 필수** (default 100). v1.9.1 본 적용에서 sample-size 누락 사고 학습.

2. **rule_code UNIQUE 제약** — 의미절 1개 = 룰 1개라 rule_code 중복 없어야. clause.id가 unique이므로 `LAW_{law_short}_ART_{article_no}_CL_{clause_seq}` 패턴이 unique 보장.

3. **NOT NULL 컬럼** master_rule_v2:
   - `rule_code`, `source_clause_id`, `source_article_id`, `source_law_id`
   - `what_action`, `sectors`, `why_obligation_summary`, `action_category_code`
   - `generation_method`, `status`, `needs_review`, `rule_kind`
   - 모두 채워야 INSERT 성공

4. **sectors NOT NULL** — INACTIVE 161건은 `sectors=[]` (빈 배열) 처리.

5. **why_obligation_summary 길이 제한** — source_text 최대 500자로 잘림 (필요 시 1000자로).

6. **batch INSERT 100건 단위** — 큰 batch는 timeout 위험.

7. **트랜잭션 처리** — 한 의미절의 master_rule_v2 + 부속 INSERT는 한 트랜잭션이어야 무결성 보장. Supabase 클라이언트 트랜잭션 또는 RPC 함수로.

   대안: master_rule_v2 모두 먼저 INSERT → 부속 batch INSERT (단순). 실패 시 truncate + 재실행.

---

## 14. 200줄+ 파일 처리 — Cursor 로컬 작업

이 스크립트는 ~500~800줄 예상. **GitHub MCP 직접 수정 금지** (200줄+ 파일은 Cursor 로컬 + git push가 안전).

```bash
# 1. 로컬에서 작성/편집
cd ~/Cursor/tai-admin/docs/extraction/scripts/
# convert_clause_to_rule.py 작성 (Cursor agent 사용)

# 2. Railway env 확인
railway environment

# 3. dry-run
railway run python3 convert_clause_to_rule.py --dry-run --sample-size 100

# 4. git push
git add convert_clause_to_rule.py
git commit -m "feat(extraction): semantic_clause → master_rule_v2 변환 스크립트"
git push origin main
```

---

## 15. 완료 기준

- [ ] master_rule_v2 58,495 rows
- [ ] master_rule_executor ~53,000 rows (EXECUTOR + RECIPIENT + ALTERNATIVE)
- [ ] master_rule_condition ~18,500+ rows
- [ ] master_rule_exception 5 rows
- [ ] 검증 SQL 8개 모두 통과
- [ ] sample 5건 사람 검토 통과
- [ ] HANDOFF 갱신 (이 작업 완료 기록)

---

## 참고 문서

- `docs/extraction/DESIGN_master_rule_v2_2026-05-07.md` — master_rule_v2 5 테이블 스키마 + 7단계 알고리즘
- `docs/extraction/HANDOFF_2026-05-08.md` — 의미절 v1.9.1 본 적용 + 5개 점검 결과
- `docs/extraction/scripts/decompose_v1.py` — 분해기 (입력 데이터 생성)
