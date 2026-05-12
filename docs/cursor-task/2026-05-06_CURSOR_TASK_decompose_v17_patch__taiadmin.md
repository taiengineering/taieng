# Cursor 작업지시서 PATCH — 의미절 분해 v1.7 (5요소 객체화 강화)

> 이전 doc: `docs/extraction/CURSOR_TASK_2026-05-06_decompose_v16_patch.md`
> 적용 대상: `docs/extraction/scripts/decompose_v1.py`
> 트리거: 본 적용 58,495건 검증 — 5요소 객체화 절반만 작동

---

## 1. v1.6 본 적용 진단

| 5요소 | 현재 채움률 | 평가 |
|---|---|---|
| action_text | 100% | △ 단순 분해 결과 텍스트 그대로 |
| executor_text | **33.5%** | ❌ 주어 추출 미구현 |
| condition_text | 7.4% | △ 키워드 매칭만, 텍스트 분리 없음 |
| **exception_text** | **0.0%** | ❌ proviso(다만) 매칭은 됐으나 분리 안 함 |
| cycle_text | 7.8% | △ 키워드만 |
| form_token | 7.1% | △ 키워드만 |

**if 케이스 객체화율**: condition 있는 4,334건 중 (조건/주어/행위) 셋 다 채움 1,731건 = **40%만**

**근본 원인**: 분해 알고리즘이 텍스트 분리 + 분류만 하고, **5요소를 별도 컬럼에 분리 추출하는 로직이 없음**.

핸드오프 doc 스펙은 5요소 객체화. 현재는 기능 미구현 상태.

---

## 2. 변경 사항 (4개 추출 알고리즘)

### 2-1. executor_text 추출 — 한국어 주어 매칭

paragraph 또는 분해된 segment의 시작 부분에서 행위자(주어) 추출.

```python
# 우선순위 1: 핵심 행위자 사전 (가장 자주 등장)
EXECUTOR_LEXICON_PATTERN = re.compile(
    r'^(?:.*?)('
    r'사업주|사용자|소유자|점유자|임차인|관리자|관계인|관할관청|'
    r'이사장|회장|위원장|청장|구청장|시ㆍ도지사|시장|군수|'
    r'중앙행정기관의\s*장|행정기관의\s*장|지방행정기관의\s*장|'
    r'(?:[가-힣ㆍ]+\s*){0,3}장관|'
    r'(?:[가-힣ㆍ]+\s*){0,4}(?:위원회|이사회)|'
    r'다음\s*각\s*호의?\s*어느\s*하나에\s*해당하는\s*자|'
    r'누구든지|신청인|등록자|대리인|대표자|소속\s*공무원'
    r')\s*(?:은|는|이|가)\s'
)

def extract_executor(text):
    """
    한국어 법령 텍스트에서 행위자(주어) 추출.
    paragraph/segment 시작 부분에서 첫 번째 매칭.
    매칭 안 되면 None.
    """
    if not text:
        return None
    m = EXECUTOR_LEXICON_PATTERN.match(text)
    if m:
        return m.group(1).strip()
    # fallback: paragraph 시작 부분의 첫 명사구 + 조사 (가장 광범)
    fallback = re.match(
        r'^([가-힣ㆍ]{2,20}(?:\s+[가-힣ㆍ]{1,15}){0,3})\s*(?:은|는|이|가)\s',
        text
    )
    if fallback:
        return fallback.group(1).strip()
    return None
```

**기대 효과**: executor 채움률 33% → 80% 이상

### 2-2. condition_text 추출 — 조건절 텍스트 분리

현재는 rule_2 매칭 시 condition_text에 키워드만 들어감(또는 안 들어감). 실제 조건절 전체를 추출해서 condition_text에 저장.

```python
CONDITION_PATTERNS = [
    # 패턴 A: "다음 각 호의 어느 하나에 해당하는 경우에는"
    re.compile(r'(다음\s*각\s*호의?\s*어느\s*하나에\s*해당(?:하는|되는)\s*(?:경우|때))(?:에는?)?'),
    # 패턴 B: "...할 때에는" / "...한 경우에는" / "...려면"
    re.compile(r'([^,.]{5,80}(?:할\s*때|한\s*경우|는\s*경우|려면|하려면))(?:에는?)?'),
    # 패턴 C: "이 경우" (단독)
    re.compile(r'(이\s*경우)(?:에는?)?'),
    # 패턴 D: "...에는" 종결 조건절
    re.compile(r'([^,.]{5,80})에는\s'),
]

def extract_condition(text):
    """
    조건절 텍스트 추출. 우선순위 순으로 첫 매칭.
    """
    if not text:
        return None
    for pattern in CONDITION_PATTERNS:
        m = pattern.search(text)
        if m:
            return m.group(1).strip()
    return None
```

**기대 효과**: condition 채움률 7% → 30% 이상 (rule_2 키워드만 → 실제 텍스트 분리)

### 2-3. exception_text 추출 — proviso(다만) 뒤 텍스트 분리

rule_1 (proviso `다만`)이 매칭됐을 때 exception_text가 0%. 분리 로직 추가.

```python
EXCEPTION_PATTERN = re.compile(
    r'(?:^|[\s,.])다만,?\s*(.+?)(?:\.\s*$|\.$|$)',
    re.DOTALL
)

def extract_exception(text):
    """
    "다만, X" 패턴에서 X 부분 추출.
    """
    if not text or '다만' not in text:
        return None
    m = EXCEPTION_PATTERN.search(text)
    if m:
        return m.group(1).strip()
    return None
```

**기대 효과**: exception 채움률 0% → rule_1 매칭 비율(약 2~5%) 만큼 채워짐

### 2-4. cycle_text 강화 — 정확한 주기 표현 분리

현재 cycle 매칭 키워드만 들어감(또는 안 들어감). 실제 주기 표현 추출.

```python
CYCLE_PATTERNS = [
    # 정기 주기
    re.compile(r'매\s*(?:년|월|주|일|반기|분기|반년)\s*\d*회?(?:\s*이상)?'),
    # X년/월/일 마다
    re.compile(r'\d+(?:년|개월|월|일|시간|주)\s*마다'),
    # X일 이내
    re.compile(r'\d+(?:년|개월|월|일|시간|영업일)\s*이내'),
    # X 이상
    re.compile(r'\d+(?:년|개월|월|일|시간)\s*이상'),
    # 매년 X월 Y일까지
    re.compile(r'(?:매년|매월)?\s*\d+월\s*\d+일(?:까지)?'),
    # X월 Y일까지
    re.compile(r'\d+월\s*\d+일까지'),
    # fallback
    re.compile(r'(?:정기적으로|상시|즉시|지체\s*없이|수시로|연\s*\d+회)'),
]

def extract_cycle(text):
    """
    주기 표현 추출. 첫 매칭만.
    """
    if not text:
        return None
    for pattern in CYCLE_PATTERNS:
        m = pattern.search(text)
        if m:
            return m.group(0).strip()
    return None
```

**기대 효과**: cycle 채움률 8% → 15~20% (정확한 주기 표현 추출)

---

## 3. 통합 — decompose_paragraph 또는 메인 분해 함수에 5요소 추출 단계 추가

각 의미절(clause) 생성 시 5요소를 별도로 추출:

```python
# 기존 분해 결과를 dict로 만들 때
clause = {
    'source_text': segment_text,
    'source_part_text': original_part_text,
    'content_type': ct,
    'applied_rules': rules,
    'needs_review': review,
    
    # NEW: 5요소 추출
    'executor_text': extract_executor(segment_text) or extract_executor(original_part_text),
    'condition_text': extract_condition(segment_text) or extract_condition(original_part_text),
    'exception_text': extract_exception(original_part_text),  # exception은 paragraph 전체에서
    'cycle_text': extract_cycle(segment_text) or extract_cycle(original_part_text),
    
    # 기존 form_token, action_text는 그대로
    'action_text': segment_text,  # 분해된 segment 텍스트
    'form_token': extract_form_token(segment_text),  # 기존 로직
}
```

**중요**: 
- executor/condition/cycle은 segment에서 먼저 시도, 없으면 paragraph 전체에서 fallback
- exception은 paragraph 전체에서만 추출 (proviso는 paragraph 단위)
- action_text는 분해된 segment 텍스트 그대로 (지금과 동일)

---

## 4. 적용 절차

### Step A — Cursor에 patch 적용

```
docs/extraction/CURSOR_TASK_2026-05-06_decompose_v17_patch.md를 읽고
§2의 4개 추출 함수(extract_executor, extract_condition, extract_exception, extract_cycle)를
docs/extraction/scripts/decompose_v1.py에 정확히 추가해줘.

§3의 통합 단계도 적용 — 각 clause 생성 시 5요소 추출 호출.

규칙:
- 4개 함수 모두 doc 명세 정규식 정확히 사용
- 우선순위 segment → paragraph fallback 순서 유지
- 기존 분해/분류/inherit 로직 절대 변경 금지 (5요소 추출만 추가)
- 끝나면 git diff --numstat 결과만 보고
```

### Step B — sample 200건 dry-run + 5요소 채움 검증

```bash
cd ~/Desktop/tai-engineering/tai-admin
git pull origin main

railway run python3 docs/extraction/scripts/decompose_v1.py \
  --sample-size 200 --sampling random --dry-run --seed 42 \
  2>&1 | tee /tmp/decompose_v17_200.log

tail -50 /tmp/decompose_v17_200.log
```

dry-run 출력에 5요소 채움 비율 통계 추가하면 더 좋음 (Cursor에 추가 부탁 가능).

### Step C — apply (truncate-first)

```bash
railway run python3 docs/extraction/scripts/decompose_v1.py \
  --sample-size 200 --sampling random --apply --seed 42 \
  --truncate-first 2>&1 | tee /tmp/decompose_v17_apply.log

cat /tmp/decompose_v17_apply.log
```

### Step D — 5요소 채움 비율 검증 (제가 SQL)

200건 적재 후 5요소 채움 비율 + sample 검증.

---

## 5. v1.7 통과 기준

| 지표 | v1.6 (본 적용) | v1.7 목표 (200건 sample) |
|---|---|---|
| executor 채움률 | 33.5% | **>= 80%** |
| condition 채움률 | 7.4% | **>= 30%** |
| exception 채움률 | 0.0% | **>= 1건이라도** (rule_1 매칭 비율만큼) |
| cycle 채움률 | 7.8% | **>= 15%** |
| **if 케이스 (조건/주어/행위) 셋 다 채움** | 40% | **>= 80%** |
| 분해 정확함 | silent failure 0 | **유지** |

**셋 다 통과** → 본 적용 재실행 (49,997 paragraphs)
**미달** → v1.7.1 보강

---

## 6. 다음 단계 (v1.7 통과 후)

1. **본 적용 재실행** — 49,997 paragraphs → 약 58,495 clauses (분해는 그대로, 5요소만 추가 채움)
2. **mblr AI_GENERATED 1,601건 검증 사이클** — 별도 작업 (작업 B)
3. **master_rule_v2 설계** — A의 의미절 객체화 + B의 검증된 mblr 통합
