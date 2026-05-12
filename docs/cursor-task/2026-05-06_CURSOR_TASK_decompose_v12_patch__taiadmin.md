# Cursor 작업지시서 PATCH — 의미절 분해 v1.2 (iter1 첫 dry-run 결과 반영)

> 이전 doc: `docs/extraction/CURSOR_TASK_2026-05-06_decompose_v11_iter1.md`
> 적용 대상: `docs/extraction/scripts/decompose_v1.py`
> 트리거: v1.1 dry-run에서 needs_review 93%, content_type 미분류 79%

---

## 1. v1.1 dry-run 진단 (보강 근거)

| 지표 | v1.1 결과 | 목표 v1.2 | 원인 |
|---|---|---|---|
| needs_review 비율 | 93.1% | **< 50%** | executor 미추출을 review 사유로 잘못 마크 + content_type 미분류 누적 |
| content_type 미분류 | 79.3% (69/87) | **< 30%** | 종결 어미 룰이 한국 법령 흔한 패턴 누락 (`한다`, `말한다`, `준용한다`, `이다`) |
| executor 미추출 | 71% (62/87) | review 사유에서 제거 | 한국 법령 주어 생략은 정상 |
| "또는" 과민 매칭 | review 56건 | 보수화 | 분리보다 묶음+review가 안전 |

---

## 2. 변경 사항 (7개)

### 2-1. 종결 어미 분류 룰 전면 재설계 — 우선순위 매칭

기존 단순 패턴 매칭 → **순차 우선순위 매칭**으로 변경.

`classify_content_type(text)` 함수의 매칭 순서:

```python
def classify_content_type(text):
    """
    종결 어미 우선순위 매칭. 매칭되는 첫 룰의 결과를 반환.
    text: 의미절 텍스트 (구두점 포함)
    """
    # 1. DEFINITION (정의/간주/명명)
    if re.search(r'(?:으?로\s*한다|이?라\s*한다|라고\s*한다|말한다|본다|이다)\.?$', text):
        return 'DEFINITION', 'rule_12_definition'

    # 2. DELEGATION (위임/준용/적용)
    if re.search(r'(?:준용한다|에\s*따른다|에\s*의한다|을\s*적용한다|에\s*의하여\s*한다|을\s*따른다)\.?$', text):
        return 'DELEGATION', 'rule_11_delegation'

    # 3. PROHIBITION (명시적 금지)
    if re.search(r'(?:아니\s*된다|아니하여야\s*한다|금지한다|할\s*수\s*없다)\.?$', text):
        return 'PROHIBITION', 'rule_8_prohibition'

    # 4. STATEMENT (단순 부정 — fallback for `아니한다`)
    if re.search(r'아니한다\.?$', text):
        return 'STATEMENT', 'rule_13_statement'

    # 5. AUTHORITY (재량/허용)
    if re.search(r'할\s*수\s*있다\.?$', text):
        return 'AUTHORITY', 'rule_7_authority'

    # 6. OBLIGATION 강제 패턴
    if re.search(r'(?:하여야\s*한다|해야\s*한다|두어야\s*한다)\.?$', text):
        return 'OBLIGATION', 'rule_6_obligation_strong'

    # 7. OBLIGATION 일반 패턴 (`정한다`, `결정한다`, 단순 `한다` fallback)
    #    단, 위 1~6에서 다 빠져나온 경우만
    if re.search(r'(?:정한다|결정한다|실시한다|작성한다|보고한다|제출한다|관리한다|점검한다|확인한다)\.?$', text):
        return 'OBLIGATION', 'rule_6_obligation_verb'
    if re.search(r'한다\.?$', text):
        return 'OBLIGATION', 'rule_6_obligation_fallback'

    # 8. 미분류
    return None, None
```

**중요**: 우선순위 순서 절대 바꾸지 말 것. DEFINITION이 가장 먼저, OBLIGATION fallback이 가장 마지막. 그래야 "...로 한다"가 OBLIGATION으로 오분류되지 않음.

### 2-2. condition 룰 (rule_2) 확장

```python
# 기존
RULE_2_CONDITION = r'([^.,]*?(?:한 경우|할 때|인 때에는|인 경우|에 한정하여)[,\s])'

# 변경 — `이 경우` 등 단독 condition 마커 추가
RULE_2_CONDITION_PATTERNS = [
    r'([^.,]*?(?:한 경우|할 때|인 때에는|인 경우|에 한정하여)[,\s])',  # 기존
    r'(이\s*경우(?:에는|에)?[,\s])',                                      # 신규: 단독 "이 경우"
    r'(이때[,\s])',                                                        # 신규: "이때"
]
```

매칭 시 어떤 패턴이든 condition_text로 추출.

### 2-3. or 룰 (rule_4) 보수화

```python
# 기존: 모두 분리 시도
RULE_4_OR = r'([^.]+?(?:하거나|또는)\s+)'

# 변경 — "하거나"는 분리, "또는"은 묶고 review만
RULE_4_OR_SPLIT = r'([^.]+?하거나\s+)'           # 분리 대상
RULE_4_OR_KEEP = r'([^.]+?\s+또는\s+[^.]+)'      # 묶음 + needs_review=true
```

`or` 분리 규칙:
- `하거나`: 의미절 분리 시도. needs_review=true (모호성 마크)
- `또는`: 분리 X. 같은 의미절 안에 유지. needs_review=true, review_reason="또는 모호성 (묶음 처리)"

### 2-4. executor 정책 변경

**핵심**: executor 미추출은 정상 케이스. review 사유에서 제거.

```python
# 기존 (잘못)
if not executor_text:
    needs_review = True
    review_reasons.append("executor 추출 실패")

# 변경
# executor가 None이어도 review 사유 추가 X.
# 한국 법령은 주어 생략이 자연스러움 (수동태, 정의문, 절차문 등).
# 다만 통계용으로 별도 카운터 유지:
if not executor_text:
    stats['executor_implicit'] += 1
# review_reasons에는 추가하지 않음
```

### 2-5. 룰 카운트 stats 갱신

dry-run 출력 §3-5의 `[PATTERN MATCHING]` 블록을 다음과 같이 갱신:

```
[PATTERN MATCHING]
  rule_1_proviso (다만)             :  X건
  rule_2_condition (경우/때/이 경우): X건  ← "이 경우/이때" 포함
  rule_3_parallel_strong (하여야 하며): X건
  rule_3_parallel_weak (하고/하며)  :  X건
  rule_4_or_split (하거나)          :  X건  → review X건
  rule_4_or_keep (또는)             :  X건  → review X건 (전부 묶음+review)
  rule_5_and (및)                   :  X건  → review X건 (전부 review)
  rule_6_obligation_strong (하여야 한다): X건
  rule_6_obligation_verb (정한다/실시한다 등): X건
  rule_6_obligation_fallback (단순 한다): X건
  rule_7_authority (할 수 있다)     :  X건
  rule_8_prohibition (아니 된다/금지한다): X건
  rule_9_cycle_explicit             :  X건
  rule_9_cycle_fallback (정기적으로) : X건
  rule_10_form (별지/별표)          :  X건
  rule_11_delegation (따른다/준용한다): X건
  rule_12_definition (로 한다/말한다/이다): X건  ← 신규
  rule_13_statement (아니한다)      :  X건  ← 신규
```

### 2-6. NEEDS_REVIEW 사유 정리

```
[NEEDS_REVIEW] N건 (X%)
  - "및" 모호성    : N건
  - "또는" 묶음 처리: N건  ← 신규 사유 (분리 안 함)
  - "하거나" 분리 후: N건
  - content_type 미분류: N건
  ── (executor 미추출 사유는 제거됨)
```

### 2-7. CONTENT_TYPE 분포 출력 갱신

```
[CONTENT_TYPE 분포]
  OBLIGATION   : N건  (strong + verb + fallback 합산)
  AUTHORITY    : N건
  PROHIBITION  : N건
  STATEMENT    : N건  ← 신규 (아니한다)
  DEFINITION   : N건  ← 신규 (로 한다/말한다/이다)
  DELEGATION   : N건
  None (룰 미매칭): N건  ← 목표: < 30%
```

---

## 3. 적용 절차

### Step A — Cursor에 patch 적용

```
docs/extraction/CURSOR_TASK_2026-05-06_decompose_v12_patch.md를 읽고
§2의 7개 변경(2-1 ~ 2-7)을 docs/extraction/scripts/decompose_v1.py에
정확히 적용해줘.

규칙:
- 종결 어미 매칭은 §2-1의 우선순위 함수 그대로 (순서 절대 바꾸지 않음)
- executor 미추출은 review 사유에서 완전히 제거
- "또는"은 분리 X, 묶음+review만
- 새 룰 12, 13 추가
- 한 파일 500줄 이내 권장
- 끝나면 git diff --numstat 결과만 보고
```

### Step B — dry-run 3회 (seed 분산)

같은 sample-size + 다른 seed 3개. 분포가 sample 운인지 룰 자체 문제인지 구분.

```bash
cd ~/Desktop/tai-engineering/tai-admin
git pull origin main

# seed 42 (이전과 동일)
railway run python3 docs/extraction/scripts/decompose_v1.py \
  --sample-size 50 --dry-run --seed 42 2>&1 | tee /tmp/decompose_iter1_v12_seed42.log

# seed 100
railway run python3 docs/extraction/scripts/decompose_v1.py \
  --sample-size 50 --dry-run --seed 100 2>&1 | tee /tmp/decompose_iter1_v12_seed100.log

# seed 200
railway run python3 docs/extraction/scripts/decompose_v1.py \
  --sample-size 50 --dry-run --seed 200 2>&1 | tee /tmp/decompose_iter1_v12_seed200.log
```

### Step C — 보고

세 로그 모두 chat에 붙여주세요. 비교 분석 + v1.3 결정 또는 apply 진입 결정해드립니다.

```bash
echo "=== seed 42 ==="; cat /tmp/decompose_iter1_v12_seed42.log | tail -80
echo "=== seed 100 ==="; cat /tmp/decompose_iter1_v12_seed100.log | tail -80
echo "=== seed 200 ==="; cat /tmp/decompose_iter1_v12_seed200.log | tail -80
```

각 seed의 마지막 80줄(통계 + sample 5건)만 붙여도 충분.

---

## 4. v1.2 통과 기준 (apply 단계 진입 가능)

세 seed 평균:

| 지표 | v1.1 | v1.2 목표 |
|---|---|---|
| content_type 미분류 비율 | 79% | **< 30%** |
| needs_review 비율 | 93% | **< 50%** |
| 분해 확장률 (parts → clauses) | 2.1배 | 1.5~2.5배 유지 |
| OBLIGATION 분류 정확도 | 1/1 (sample) | sample 5건 중 ≥ 4건 정상 |

**셋 다 통과** → apply 단계 진입 (Step D, 다음 doc에서)
**하나라도 미달** → v1.3 보강 사항 추가 (예: `이라 한다` 미스, "또는" 묶음 너무 광범 등)

---

## 5. 메모

- 첫 iter는 임시 테이블 `semantic_clause_iter1`. 아직 미마이그레이션. apply 진입 시점에 §앞 doc §2 DDL 실행.
- v1.2가 통과해도 sample-size 50은 작음. 통과 후 200~500건으로 확장해서 같은 사이클 한 번 더.
- v1.1 dry-run의 41 parts → 50으로 채운 sample-size가 9건 적게 잡힌 이유는 dedup 또는 KEC 제외 등으로 추정. v1.2에선 50건 정확히 채워지는지 확인.
