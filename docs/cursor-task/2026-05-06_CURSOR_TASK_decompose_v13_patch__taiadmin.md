# Cursor 작업지시서 PATCH — 의미절 분해 v1.3 (v1.2 dry-run 3회 결과 반영)

> 이전 doc: `docs/extraction/CURSOR_TASK_2026-05-06_decompose_v12_patch.md`
> 적용 대상: `docs/extraction/scripts/decompose_v1.py`
> 트리거: v1.2 dry-run에서 sample 분해 품질 11/15 (73%), 통과 기준(80%) 미달 — 두 미스 패턴 식별

---

## 1. v1.2 진단 (보강 근거)

v1.2 dry-run 3회(seed 42/100/200) 평균:

| 지표 | v1.1 | v1.2 | 결과 |
|---|---|---|---|
| content_type 미분류 | 79% | **22.4%** | ✅ 큰 진전 |
| needs_review | 93% | 60.4% | △ 근접 |
| sample 분해 정확도 | 1/5 | 11/15 (73%) | ❌ 80% 미달 |

미스 패턴 2가지 (sample 15건 분석):

### 패턴 1. 분해된 비종결 segment 미분류 (4건)
```
"사업주는 ... 지정하고 / 다음 각 호의 사항을 게시하여야 한다"
   ↓ 분해
[1] "...지정하고"  → content_type: None ❌
[2] "...게시하여야 한다"  → OBLIGATION ✓
```
한국 법령의 병렬 행위 "A하고 + B하여야 한다"에서 A의 content_type은 B와 동일. **inherit 필요**.

### 패턴 2. `과 같다` / `와 같다` (별표 참조) 종결 미커버 (1건+)
```
"...석면비산방지계획서의 작성방법은 별표 1과 같다."
   → content_type: None ❌  (DELEGATION이어야)
```
별표/별지 참조의 매우 흔한 종결 어미. rule_11에 추가.

---

## 2. 변경 사항 (2개)

### 2-1. rule_11 (DELEGATION) 확장 — `과 같다` / `와 같다` 추가

`classify_content_type()` 함수의 DELEGATION 매칭 줄 (우선순위 2위):

```python
# 변경 전 (v1.2)
if re.search(r'(?:준용한다|에\s*따른다|에\s*의한다|을\s*적용한다|에\s*의하여\s*한다|을\s*따른다)\.?$', text):
    return 'DELEGATION', 'rule_11_delegation'

# 변경 후 (v1.3) — `과/와 같다` 추가
if re.search(r'(?:준용한다|에\s*따른다|에\s*의한다|을\s*적용한다|에\s*의하여\s*한다|을\s*따른다|(?:과|와)\s*같다)\.?$', text):
    return 'DELEGATION', 'rule_11_delegation'
```

매칭 케이스 예시:
- `별표 1과 같다.` ✓
- `별표 13과 같다.` ✓
- `별지 제5호서식과 같다.` ✓
- `다음과 같다.` ✓ (의도된 매칭)

### 2-2. 분해된 비종결 segment의 content_type inherit

분해 후 segment별 분류 함수에 inherit 로직 추가.

#### 알고리즘

```python
def classify_segments(segments):
    """
    분해된 segments를 분류. 비종결 segment는 last segment의 content_type inherit.

    segments: List[str]  # 분해된 의미절 텍스트 리스트 (앞→뒤 순서)
    returns: List[Tuple[Optional[str], List[str]]]  # (content_type, applied_rules) per segment
    """
    if not segments:
        return []

    # 1. 각 segment 직접 분류
    direct_results = []
    for seg in segments:
        ct, rule = classify_content_type(seg)
        direct_results.append((ct, [rule] if rule else []))

    # 2. last segment의 content_type 추출
    last_ct = direct_results[-1][0]

    # 3. 미분류 비종결 segment에 last 결과 inherit
    #    조건: 자신은 None + last는 분류됨 + 자신이 last가 아님
    final_results = []
    for i, (ct, rules) in enumerate(direct_results):
        is_last = (i == len(direct_results) - 1)
        if ct is None and last_ct is not None and not is_last:
            # 비종결 segment + last가 분류됨 → inherit
            inherited_rules = rules + [f'inherit_from_last_segment(={last_ct})']
            final_results.append((last_ct, inherited_rules))
        else:
            final_results.append((ct, rules))

    return final_results
```

#### 호출 변경

기존 코드에서 segment별로 개별 `classify_content_type()` 호출하던 부분을 `classify_segments(segments)` 한 번 호출로 변경. 호출 결과를 각 clause의 `content_type`과 `applied_rules`에 채움.

#### needs_review 정책

inherit된 segment는 **needs_review=true 마크 X**. inherit 자체는 정상 동작이라 review 불필요. 단 이미 다른 사유(`및`/`또는`/`하거나`)로 review 마크된 경우는 그대로.

review_reason에서 "content_type 미분류" 사유 카운트가 자연스럽게 줄어듦.

### 2-3. 출력 갱신

`[PATTERN MATCHING]` 블록 마지막에 inherit 카운터 추가:

```
[PATTERN MATCHING]
  ...
  rule_12_definition (로 한다/말한다/이다): X건
  rule_13_statement (아니한다)      :  X건
  inherit_from_last_segment        :  X건  ← 신규
```

---

## 3. 적용 절차

### Step A — Cursor에 patch 적용

```
docs/extraction/CURSOR_TASK_2026-05-06_decompose_v13_patch.md를 읽고
§2의 2개 변경(2-1 DELEGATION 확장, 2-2 inherit 로직, 2-3 출력)을
docs/extraction/scripts/decompose_v1.py에 정확히 적용해줘.

규칙:
- DELEGATION 정규식에 (?:과|와)\s*같다 만 추가. 다른 우선순위/매칭 순서 절대 변경 금지
- inherit는 last segment 기준만 (multi-step inherit 안 함, 단순화)
- inherit된 segment는 needs_review=true 마크 X (inherit 자체는 정상)
- review_reason 사유에서 "content_type 미분류"는 자동으로 줄어듦 (inherit 후 미분류 카운트만 됨)
- 한 파일 600줄 이내 권장
- 끝나면 git diff --numstat 결과만 보고
```

### Step B — dry-run (seed 1개로 빠른 검증)

```bash
cd ~/Desktop/tai-engineering/tai-admin
git pull origin main

railway run python3 docs/extraction/scripts/decompose_v1.py \
  --sample-size 50 --sampling random --dry-run --seed 42 2>&1 \
  | tee /tmp/decompose_v13_seed42.log

cat /tmp/decompose_v13_seed42.log
```

### Step C — 보고

전체 로그 chat에 붙여주세요. v1.3 통과 기준 평가 후 apply 진입 결정.

---

## 4. v1.3 통과 기준

| 지표 | v1.2 | v1.3 목표 |
|---|---|---|
| content_type 미분류 비율 | 22.4% | **< 15%** (inherit 효과로 자연 감소) |
| sample 5건 분해 정확도 | 3/5 (seed 42) | **≥ 4/5** |
| inherit 카운터 작동 | (없음) | **> 0건** (효과 검증) |
| `과/와 같다` 매칭 | 0건 | **>= 1건** (별표 참조 흔함) |

**셋 다 통과** → 임시 테이블 마이그레이션 + apply 진입
**미달** → v1.4 보강

---

## 5. apply 진입 시 (다음 단계)

v1.3 통과 후:

1. 임시 테이블 마이그레이션 (이전 doc `decompose_v11_iter1.md` §2 DDL 그대로)
2. apply 명령:
   ```bash
   railway run python3 docs/extraction/scripts/decompose_v1.py \
     --sample-size 50 --sampling random --apply --seed 42 \
     --truncate-first 2>&1 | tee /tmp/decompose_iter1_apply.log
   ```
3. DB 검증 SQL (이전 doc §4 Step E 그대로)
4. 그룹별 검증 → 다음 iter (sample 200~500건 확장)
