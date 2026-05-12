# CURSOR TASK 2026-05-09: decompose_v2.0 — Pipeline 8단계 신규 구축

> **목표**: 분해기 v1.9.1 (`decompose_v1.py` 66KB 단일 파일) 폐기 → 8단계 pipeline 신규 구축. 4종 part_type 100% 처리, 6하원칙 분해, 의미절 간 관계 매핑.
> **룰 카탈로그**: `docs/extraction/RULE_CATALOG_v20.md` 참조 (R-01~R-20)
> **백업**: `semantic_clause_backup_pre_redecompose_20260509` (58,495 row) 유지

---

## § 0. 절대 금지 (전 stage 공통)

1. AI/LLM 호출 0% (정규식 + 키워드 사전만)
2. 검증 없는 완료 선언 금지 ("X% 완료", "사실상 PASS")
3. 의미해석 회피 (정규식 매칭 안 되면 NULL + needs_review)
4. 200줄+ 파일 GitHub MCP 직접 수정 금지 → Cursor 로컬
5. 정직 보고 5개 강제 (모집단·분모, 성공·실패 함께)

## § 1. 디렉토리 구조

```
docs/extraction/scripts/decompose_v2/
├── 00_runner.py             # orchestrator (--stage N, --apply, --sample N)
├── 01_fetch_parts.py
├── 02_preprocess.py
├── 03_split_clauses.py
├── 04_classify_content_type.py
├── 05_extract_executor.py
├── 06_extract_6w.py
├── 07_build_relations.py
├── 08_load_to_db.py
├── lib/
│   ├── __init__.py
│   ├── content_type_dict.py
│   ├── executor_patterns.py
│   ├── six_w_patterns.py
│   └── relation_markers.py
├── data/                    # gitignored
└── tests/
```

## § 2. 데이터 흐름

```
DB law_article_part (143,549)
  → [01] fetch        → data/01_parts.jsonl (143,549)
  → [02] preprocess   → data/02_preprocessed.jsonl (143,549)
  → [03] split        → data/03_clauses.jsonl (예상 ~150,000~200,000)
  → [04] classify     → data/04_classified.jsonl (8종 content_type)
  → [05] executor     → data/05_executor.jsonl
  → [06] 6w           → data/06_6w.jsonl
  → [07] relations    → data/07_clauses.jsonl + data/07_relations.jsonl
  → [08] load         → DB semantic_clause + semantic_clause_relation
```

## § 3. 정직 보고 (전 stage 공통)

매 stage 종료 시 stderr에 다음 형식 출력 (모집단·분모·실패 모두 포함):

```
[stage 0X] in=N, out=M, needs_review=K, by_type={paragraph: A, clause: B, ...}
[stage 0X] elapsed=Ts, throughput=N/s
```

`X% 완료`, `사실상 PASS` 같은 가공 표현 금지.

---

## § 4. Stage 01: fetch_parts.py

### 목적
4종 part_type 모두 fetch. **필터 없음** (R-14 fetch 필터 결함 수정).

### 입력
- DB: `law_article_part` (143,549 row)
- args: `--limit N` (테스트), `--part-type all|paragraph|clause|subclause|proviso`

### 출력
`data/01_parts.jsonl`. 1줄 = 1 part:
```json
{
  "id": "uuid", "article_id": "uuid", "part_type": "paragraph",
  "depth": 1, "paragraph_no": 2, "clause_no": null, "subclause_code": null,
  "parent_id": "uuid", "sort_order": 12, "part_text": "...",
  "has_proviso": false, "proviso_text": null,
  "primary_content_type": "OBLIGATION", "content_types": ["OBLIGATION"],
  "part_code": "..."
}
```

### 핵심 로직
```python
PAGE_SIZE = 1000

def fetch_all_parts(part_type='all', limit=None):
    parts, offset = [], 0
    while True:
        q = supabase.table("law_article_part").select("*")
        if part_type != 'all':
            q = q.eq("part_type", part_type)
        batch = q.range(offset, offset + PAGE_SIZE - 1).execute().data
        parts.extend(batch)
        if len(batch) < PAGE_SIZE: break
        offset += PAGE_SIZE
        if limit and len(parts) >= limit: return parts[:limit]
    return parts
```

### 검증
- 출력 row = 143,549 (전체) 또는 --part-type별 (paragraph 61,223 / clause 65,819 / subclause 10,438 / proviso 6,069)
- 정직 보고: `[stage 01] fetched=143549, paragraph=61223, clause=65819, subclause=10438, proviso=6069`

---

## § 5. Stage 02: preprocess.py

### 목적
HTML/줄바꿈/숫자코드 prefix 정리 (R-15, R-18).

### 입력
`data/01_parts.jsonl`

### 출력
`data/02_preprocessed.jsonl`. 추가 필드:
```json
{
  ...(01 모든 필드),
  "raw_text": "<원본 part_text>",
  "preprocessed_text": "<전처리 후>",
  "preprocess_marks": ["html_removed","newline_collapsed","code_prefix_removed","table_or_figure_detected"],
  "preprocess_needs_review": false,
  "preprocess_review_reason": null
}
```

### 핵심 로직 (lib/preprocess_patterns.py)
```python
import re

CODE_PREFIX = re.compile(r'^\s*\d+(?:\.\d+)*\s+')                       # R-15
TABLE_FIGURE = re.compile(r'<(?:표|그림|table|figure)[^>]*>', re.IGNORECASE)  # R-18
GENERIC_HTML = re.compile(r'<[^>]+>')
NEWLINE_COLLAPSE = re.compile(r'\s*\n+\s*')

def preprocess(text):
    marks, review, reason = [], False, None
    new_text, n = CODE_PREFIX.subn('', text)
    if n > 0: marks.append("code_prefix_removed")
    if TABLE_FIGURE.search(new_text):
        marks.append("table_or_figure_detected"); review = True; reason = "table_or_figure"
    new_text, n = GENERIC_HTML.subn('', new_text)
    if n > 0: marks.append("html_removed")
    new_text, n = NEWLINE_COLLAPSE.subn(' ', new_text)
    if n > 0: marks.append("newline_collapsed")
    return new_text.strip(), marks, review, reason
```

### 검증
- 출력 = 입력 (143,549)
- 정직 보고: `[stage 02] in=143549, out=143549, code_removed=N, html=N, newline=N, table=N, review=N`

---

## § 6. Stage 03: split_clauses.py

### 목적
preprocessed_text를 의미절로 분리. 다중 마커 적용 (R-06, R-07, R-08, R-11, R-17).

### 입력
`data/02_preprocessed.jsonl`

### 출력
`data/03_clauses.jsonl`. 1줄 = 1 의미절:
```json
{
  "temp_id": "<part_id>_<seq>",
  "source_part_id": "uuid",
  "clause_seq": 1,
  "split_marker": "다만",
  "split_position": 87,
  "source_text": "...",
  "split_needs_review": false,
  "split_review_reason": null
}
```

### 핵심 로직 (lib/split_patterns.py)

**분리 마커 우선순위** (앞→뒤로 적용, 종결 동사 다음만):
```python
import re

# 종결 동사 패턴 (분리 마커가 이 직후에 와야 함, R-08)
TERMINAL_VERB = r'(?:한다|된다|있다|없다|하여야\s*한다|아니\s*된다|이다|같다)'

# R-07: 마침표 분리 (한국어 종결 + 마침표 + 한국어 시작)
PERIOD_SPLIT = re.compile(rf'(?<={TERMINAL_VERB})\.\s+(?=[가-힣])')

# R-17: "이 경우" 분리
THIS_CASE_SPLIT = re.compile(rf'(?<={TERMINAL_VERB})\.\s*이\s*경우[,\.]?\s*')

# R-06: "...하며" 분리 (v1.9.1 유지)
HAMYEO_SPLIT = re.compile(r'(?:하|되|이)며,?\s+(?=[가-힣])')

# R-03: paragraph 인라인 "다만," 분리
DAMAN_SPLIT = re.compile(r'(?:한다|된다|있다|없다)\.?\s*다만,?\s*')

# R-11: "또는·및" 분리 안 함 (정규식 사용 안 함)
```

**알고리즘**:
```python
def split_clauses(preprocessed_text):
    """우선순위 순 분리. 한 텍스트가 여러 marker 가지면 모두 분리."""
    clauses = [(0, preprocessed_text, None)]  # (position, text, marker)
    
    # 1. 마침표 분리 (R-07)
    clauses = apply_split(clauses, PERIOD_SPLIT, 'period')
    
    # 2. "이 경우" 분리 (R-17, R-07 보다 우선 적용 가능 — 마침표 포함)
    clauses = apply_split(clauses, THIS_CASE_SPLIT, 'this_case')
    
    # 3. "다만" 분리 (R-03)
    clauses = apply_split(clauses, DAMAN_SPLIT, 'daman')
    
    # 4. "...하며" 분리 (R-06)
    clauses = apply_split(clauses, HAMYEO_SPLIT, 'hamyeo')
    
    return [(seq, text, marker) for seq, (pos, text, marker) in enumerate(clauses)]
```

### 검증
- 출력 의미절 수 ≥ 입력 part 수
- split_marker 분포 (period N / this_case N / daman N / hamyeo N / null=단일 의미절 N)
- 정직 보고: `[stage 03] in_parts=143549, out_clauses=N, period=N, daman=N, hamyeo=N, this_case=N, single=N`

---

## § 7. Stage 04: classify_content_type.py

### 목적
의미절별 8종 content_type 분류. 종결어미 사전 100+ 패턴 (R-10, R-16).

### 입력
`data/03_clauses.jsonl`

### 출력
`data/04_classified.jsonl`. 추가 필드:
```json
{ ..., "content_type": "OBLIGATION", "classified_by_pattern": "보관해야 한다", "classified_needs_review": false }
```

### 핵심 사전 (lib/content_type_dict.py)
```python
# 우선순위 순 (앞 패턴부터 매칭)
PATTERNS = [
    # PROHIBITION (R-10)
    ('PROHIBITION', re.compile(r'(?:아니\s*된다|아니하여야\s*한다|금지한다|할\s*수\s*없다|받을\s*수\s*없다|있을\s*수\s*없다)\.?\s*$')),
    # PENALTY
    ('PENALTY', re.compile(r'(?:과태료를\s*부과한다|벌금에\s*처한다|형에\s*처한다|처벌한다)\.?\s*$')),
    # DELEGATION
    ('DELEGATION', re.compile(r'(?:로\s*정한다|에\s*따른다|과\s*같다|로\s*정하여\s*고시한다|령으로\s*정한다)\.?\s*$')),
    # DEFINITION
    ('DEFINITION', re.compile(r'(?:이라\s*한다|로\s*한다|으로\s*본다|을\s*말한다|를\s*말한다|이다)\.?\s*$')),
    # OBLIGATION (강한 의무)
    ('OBLIGATION', re.compile(r'(?:하여야\s*한다|해야\s*한다|받아야\s*한다|보관해야\s*한다|결정하여야\s*한다)\.?\s*$')),
    # AUTHORITY (권한)
    ('AUTHORITY', re.compile(r'(?:할\s*수\s*있다|받을\s*수\s*있다|명할\s*수\s*있다|요청할\s*수\s*있다)\.?\s*$')),
    # STATEMENT (효과·상태)
    ('STATEMENT', re.compile(r'(?:된다|진다|소멸된다|잃는다|발생한다|종료된다|거친다|뺀다)\.?\s*$')),
    # OBLIGATION (약한 의무, fallback)
    ('OBLIGATION', re.compile(r'(?:한다|에\s*등록한다|에\s*신고한다)\.?\s*$')),
]

def classify(text):
    for ct, pattern in PATTERNS:
        m = pattern.search(text)
        if m: return ct, m.group(0)
    return None, None  # NULL → needs_review
```

### 검증
- 출력 = 입력
- content_type별 분포 (NULL 0% 목표)
- 정직 보고: `[stage 04] in=N, out=N, OBLIGATION=A, PROHIBITION=B, ..., NULL=K (review=K)`

---

## § 8. Stage 05: extract_executor.py

### 목적
의미절별 executor + recipient 추출. 동사 어간 오추출 방지 (R-12), content_type별 차별화 (R-13).

### 입력
`data/04_classified.jsonl`

### 출력
`data/05_executor.jsonl`. 추가 필드:
```json
{ ..., "executor_text": "도시가스사업자", "recipient_text": "한국가스안전공사", "executor_needs_review": false }
```

### 핵심 로직 (lib/executor_patterns.py)

분해기 v1.9.1의 알고리즘 유지 + R-12 + R-13 보강:
```python
import re

# v1.9.1 핵심: "은/는" 우선, condition_end 다음
SUBJECT_MARKER = re.compile(r'([가-힣A-Za-z]+?)(은|는|이|가)\s')

# R-12: 동사 어간 오추출 방지
VERB_STEM_SUFFIXES = ('하', '받', '되', '치', '시키', '되어', '하여', '받아', '되는')
def is_verb_stem(noun):
    return any(noun.endswith(s) for s in VERB_STEM_SUFFIXES)

# 사물 명사 사전 (R-13)
OBJECT_NOUNS = {'기준', '계산방법', '범위', '대상', '시기', '절차', '방법', '심사기준', '자료', '기간', '연면적', '권고기준', '세부기술기준', '심사기준'}

def extract_executor(text, content_type):
    candidates = list(SUBJECT_MARKER.finditer(text))
    
    # ... v1.9.1 select_best_subject_match 로직
    best = select_best_subject_match(candidates, text)
    if not best:
        return None, "no_candidate"
    
    noun = best.group(1)
    
    # R-12: 동사 어간 제거
    if is_verb_stem(noun):
        return None, "verb_stem_rejected"
    
    # R-13: DEFINITION/DELEGATION 사물 주어 NULL
    if content_type in ('DEFINITION', 'DELEGATION') and noun in OBJECT_NOUNS:
        return None, "object_subject_in_definition"
    
    return cleanup_subject_candidate(noun), None
```

### 검증
- executor 채움률 by content_type
- needs_review 사유 분포 (no_candidate / verb_stem_rejected / object_subject)
- 정직 보고: `[stage 05] in=N, executor_filled=A (B%), null=C (review=C), verb_stem_rejected=D, object_subject=E`

---

## § 9. Stage 06: extract_6w.py

### 목적
6하원칙 컬럼 채우기. where_text + what_text + how_text + cycle_text + condition_text + exception 보강 (R-NEW-01~03).

### 입력
`data/05_executor.jsonl`

### 출력
`data/06_6w.jsonl`. 추가 필드:
```json
{ ..., "where_text": "사업장에서", "what_text": "신청서를", "how_text": "산업통상부령으로 정하는 바에 따라", "cycle_text": "매년", "condition_text": "...경우", "exception_text": "...", "exception_marker": "다만" }
```

### 핵심 로직 (lib/six_w_patterns.py)
```python
import re

# R-NEW-01: where_text
WHERE_PATTERNS = [
    re.compile(r'([가-힣]+(?:에서|에\s*한정하여|\s*내에서|\s*안에))'),
]

# R-NEW-02: what_text
WHAT_PATTERN = re.compile(r'([가-힣]{2,15})(을|를)\s+(?=[가-힣]+(?:한다|되다|하여야|받아야))')

# R-NEW-03: how_text
HOW_PATTERNS = [
    re.compile(r'([가-힣]+(?:으로|로))\s+(?=[가-힣]+(?:한다|정한다))'),
    re.compile(r'([가-힣]+의\s*방법(?:으)?로)'),
    re.compile(r'([가-힣\s]+에\s*따라)'),
]

# cycle (기존)
CYCLE_PATTERNS = [
    re.compile(r'(매년|매월|매일|즉시|지체\s*없이|\d+년마다|\d+개월마다|\d+일\s*이내)'),
]

# condition (기존 + 보강)
CONDITION_PATTERN = re.compile(r'([가-힣\s]+(?:경우|때|하면|하려면))(?:에는|에)?')

# exception (R-09)
EXCEPTION_MARKERS = ['다만', '제외하고는', '그러하지\s*아니하다', '경우는\s*제외']
```

### 검증
- 6컬럼별 채움률 (where N% / what N% / how N% / cycle N% / condition N% / exception N%)
- 정직 보고: `[stage 06] in=N, where_filled=A%, what=B%, how=C%, cycle=D%, condition=E%, exception=F%`

---

## § 10. Stage 07: build_relations.py

### 목적
의미절 간 관계 도출. 매핑 테이블 INSERT 준비 (R-01~R-05, R-09).

### 입력
`data/06_6w.jsonl`

### 출력
- `data/07_clauses.jsonl` (의미절 최종, id uuid 부여)
- `data/07_relations.jsonl` (관계, semantic_clause_relation INSERT용):
```json
{ "source_clause_id": "uuid", "target_clause_id": "uuid", "relation_type": "proviso", "relation_marker": "다만", "is_inferred": true, "needs_review": false }
```

### 관계 유형별 룰

#### proviso (R-03, R-09)
- proviso part_type 의미절 → parent_id로 paragraph 찾기 → paragraph의 첫 의미절 = target
- relation_type='proviso', marker='다만'

#### enumeration (R-01, R-02, R-04)
- clause part_type 의미절 → parent_id로 paragraph 찾기 → paragraph 첫 의미절 = target
- subclause part_type 의미절 → parent_id로 clause 찾기 → clause 첫 의미절 = target
- relation_type='enumeration'

#### parallel_seq (R-06)
- split_marker='hamyeo'인 의미절들이 같은 part_id 공유 → 같은 part 안의 이전 clause_seq 의미절 = target
- relation_type='parallel_seq', marker='하며'

#### sentence_seq (R-07, R-17)
- split_marker='period' 또는 'this_case' → 같은 part 안의 이전 의미절 = target
- relation_type='sentence_seq'

### 검증
- relation_type별 분포 (proviso 6,069 / enumeration N / parallel_seq N / sentence_seq N)
- 정직 보고: `[stage 07] clauses=N, relations=M, proviso=A, enumeration=B, parallel_seq=C, sentence_seq=D`

---

## § 11. Stage 08: load_to_db.py

### 목적
`semantic_clause` + `semantic_clause_relation`에 bulk INSERT.

### 입력
- `data/07_clauses.jsonl`
- `data/07_relations.jsonl`

### 출력
- DB INSERT
- 검증 SQL 결과

### 핵심 로직
```python
# 안전망: 본 적용 전 백업 검증
assert table_exists("semantic_clause_backup_pre_redecompose_20260509")

# --truncate-first 옵션 시
if args.truncate_first:
    supabase.rpc("truncate_semantic_clause_v2").execute()  # 별도 RPC 등록 필요

# Bulk INSERT (chunk 100)
def bulk_insert_clauses(clauses, chunk_size=100):
    for chunk in chunks(clauses, chunk_size):
        supabase.table("semantic_clause").insert(chunk).execute()
        print(f"[stage 08] inserted clauses: {progress}/{total}")

def bulk_insert_relations(relations, chunk_size=100):
    for chunk in chunks(relations, chunk_size):
        supabase.table("semantic_clause_relation").insert(chunk).execute()
        print(f"[stage 08] inserted relations: {progress}/{total}")
```

### 검증 SQL
```sql
-- (a) row count
SELECT COUNT(*) FROM semantic_clause;
SELECT COUNT(*) FROM semantic_clause_relation;

-- (b) part_type별 의미절 수 (Y 정책: 4종 모두 의미절)
SELECT p.part_type, COUNT(DISTINCT sc.id) AS clause_count
FROM law_article_part p
LEFT JOIN semantic_clause sc ON sc.source_part_id = p.id
GROUP BY p.part_type;
-- 기대: paragraph N, clause 65,819+, subclause 10,438+, proviso 6,069+

-- (c) relation_type 분포
SELECT relation_type, COUNT(*) FROM semantic_clause_relation GROUP BY 1;
-- 기대: proviso ~6,069, enumeration ~76,257, parallel_seq N, sentence_seq N

-- (d) 4 FK 무결성
SELECT COUNT(*) FROM semantic_clause sc
LEFT JOIN law_article_part p ON sc.source_part_id = p.id
WHERE p.id IS NULL;
-- 기대: 0

-- (e) needs_review 분포
SELECT review_reason, COUNT(*) FROM semantic_clause WHERE needs_review GROUP BY 1 ORDER BY 2 DESC;
```

### 정직 보고
```
[stage 08] inserted clauses: N
[stage 08] inserted relations: M
[stage 08] by part_type: paragraph=A, clause=B, subclause=C, proviso=D
[stage 08] by relation_type: proviso=A, enumeration=B, parallel_seq=C, sentence_seq=D
[stage 08] needs_review: K (사유별 분포)
```

---

## § 12. Stage 00: runner.py (orchestrator)

```python
import argparse, subprocess

STAGES = [
    "01_fetch_parts.py",
    "02_preprocess.py",
    "03_split_clauses.py",
    "04_classify_content_type.py",
    "05_extract_executor.py",
    "06_extract_6w.py",
    "07_build_relations.py",
    "08_load_to_db.py",
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', type=int, help='특정 stage만 실행 (1~8)')
    parser.add_argument('--from-stage', type=int, default=1, help='시작 stage')
    parser.add_argument('--to-stage', type=int, default=8, help='종료 stage')
    parser.add_argument('--apply', action='store_true', help='Stage 08 본 적용')
    parser.add_argument('--truncate-first', action='store_true', help='Stage 08 truncate first')
    parser.add_argument('--sample', type=int, help='Stage 01에서 sample 수 제한')
    args = parser.parse_args()
    
    if args.stage:
        run_stage(args.stage, args)
    else:
        for i in range(args.from_stage, args.to_stage + 1):
            run_stage(i, args)
            print(f"[runner] Stage {i:02d} 완료")
```

### 사용 예
```bash
# 전체 (sample 100건 dry-run)
railway run python3 00_runner.py --sample 100

# 단일 stage
railway run python3 00_runner.py --stage 3

# Stage 03부터 끝까지
railway run python3 00_runner.py --from-stage 3

# 본 적용
railway run python3 00_runner.py --apply --truncate-first
```

---

## § 13. 단계별 검증 절차 (Cursor 구현 후)

각 stage 구현 후 다음 순서로 검증:

1. **단일 stage dry-run**: `--sample 100`으로 100건 처리. jsonl 출력 → 사용자 검토 가능
2. **다음 stage로 진입 전**: 정직 보고 통계 확인 (모집단·분모·needs_review)
3. **누락된 sample 식별**: needs_review=true 행 sample 5건 검토 → 룰 추가 필요 여부 결정
4. **다음 stage 진행** 또는 **현 stage 룰 보강**

전체 dry-run (143,549 paragraph)은 **Stage 04 완성 후 처음 시도**. Stage 04까지 안정되면 Stage 05~08도 비교적 안전.

---

## § 14. 본 적용 절차 (사용자 GO 신호 후)

```bash
# 1. 백업 확인
railway run python3 -c "..."  # backup row count

# 2. 전체 dry-run (jsonl만 생성, DB INSERT 안 함)
railway run python3 00_runner.py --from-stage 1 --to-stage 7

# 3. dry-run 결과 검증 SQL 비교 (07_clauses.jsonl + 07_relations.jsonl 통계)

# 4. 본 적용 (Stage 08만)
railway run python3 00_runner.py --stage 8 --apply --truncate-first

# 5. 검증 SQL 5종 (§ 11 (a)~(e))
```

---

## § 15. 사고 시 백업 복원

```sql
BEGIN;
TRUNCATE semantic_clause CASCADE;  -- semantic_clause_relation도 ON DELETE CASCADE로 삭제
INSERT INTO semantic_clause SELECT * FROM semantic_clause_backup_pre_redecompose_20260509;
COMMIT;
```

복원 후 분해기 v1.9.1 시점으로 복귀.

---

## § 16. 작업 순서 권장

Cursor 작업 시:
1. **Stage 01·02** 먼저 구현 (fetch + 전처리, 가장 안전)
2. dry-run 100건 → 검증 통과 → Stage 03 시작
3. **Stage 03·04** (분리 + 분류, 가장 핵심)
4. dry-run 1000건 → 검증 통과 → Stage 05·06 시작
5. **Stage 05·06** (executor + 6하원칙)
6. dry-run 1000건 → 검증 통과 → Stage 07·08 시작
7. **Stage 07·08** (관계 + 본 적용)
8. 사용자 GO 신호 후 본 적용

---

## 관련 문서

- `RULE_CATALOG_v20.md` — 룰 카탈로그 (R-01~R-20)
- `HANDOFF_2026-05-08_night.md` — 이전 핸드오프 (참고용)
- `decompose_v1.py` — v1.9.1 (폐기 대상, 비교용 보존)
