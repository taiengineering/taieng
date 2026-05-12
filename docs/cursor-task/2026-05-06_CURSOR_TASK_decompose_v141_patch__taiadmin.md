# Cursor 작업지시서 PATCH — 의미절 분해 v1.4.1 (디버그 결과 반영, 정규식 2개 fix)

> 이전 doc: `docs/extraction/CURSOR_TASK_2026-05-06_decompose_v14_patch.md`
> 적용 대상: `docs/extraction/scripts/decompose_v1.py`
> 트리거: v1.4 디버그 결과로 미매칭 원인 명확히 식별

---

## 1. v1.4 디버그 결과

`--debug-classify` dry-run에서 미분류 with `있다` 3건 repr:

```
1. ' 따른 인증기관은 제4항에 따라 녹색건축의 인증을 신청한 자로부터 수수료를 받을 수 있다.'
2. '이 경우 보완 또는 보정에 걸린 기간은 제10조제1항의 처리기간에 산입(算入)하지 않는다.'
3. '그 자격을 취소하거나 6개월 이상 2년 이하의 기간을 정하여 그 자격을 정지시킬 수 있다.'
```

### 진단

| 케이스 | 종결 어미 | 미매칭 원인 |
|---|---|---|
| 1 | `받을 수 있다` | rule_7 정규식이 `할\s*수\s*있다`로 **`할` 한정** → `받을`은 미매칭 |
| 2 | `하지 않는다` | rule_13(`아니한다`)도 미커버. 어떤 룰에도 없는 종결 어미 |
| 3 | `정지시킬 수 있다` | 케이스 1과 동일 (`할` 한정 문제) |

### 결론

`할 수 있다` 외의 동사 어간(`받을`, `정지시킬`, `될`, `볼`, `있을` 등) + `하지 않는다`(단순 부정) 패턴이 룰에 빠져 있었음. 정규식 2개 보강으로 해결.

---

## 2. 변경 사항 (2개)

### 2-1. rule_7 (AUTHORITY) — 동사 어간 광범 매칭

`classify_content_type()` 함수의 AUTHORITY 매칭 줄 (우선순위 5위):

```python
# 변경 전 (v1.4)
if re.search(r'할\s*수\s*있다\.?$', text):
    return 'AUTHORITY', 'rule_7_authority'

# 변경 후 (v1.4.1) — `할` 한정 제거, 한글 1글자 이상 + 수 있다
if re.search(r'[가-힣]\s*수\s*있다\.?$', text):
    return 'AUTHORITY', 'rule_7_authority'
```

**보강 후 매칭 케이스**:
- `할 수 있다` ✓ (기존)
- `받을 수 있다` ✓ (신규 — case 1)
- `정지시킬 수 있다` ✓ (신규 — case 3)
- `될 수 있다`, `볼 수 있다`, `있을 수 있다`, `만들 수 있다` 등 모두 매칭

**가짜 매칭 방지**: `[가-힣]` 한글 1글자 강제 + `수\s*있다` 종결로 한정. 일상 표현 "관계 수 있다" 같은 부적절 매칭 가능성 낮음 (법령 텍스트에선 사실상 0).

### 2-2. rule_13 (STATEMENT) — `하지 않는다`, `되지 않는다` 추가

`classify_content_type()` 함수의 STATEMENT 매칭 줄 (우선순위 4위):

```python
# 변경 전 (v1.4)
if re.search(r'아니한다\.?$', text):
    return 'STATEMENT', 'rule_13_statement'

# 변경 후 (v1.4.1) — 단순 부정 어미 추가
if re.search(r'(?:아니한다|하지\s*않는다|되지\s*않는다)\.?$', text):
    return 'STATEMENT', 'rule_13_statement'
```

**보강 후 매칭 케이스**:
- `진행하지 아니한다` ✓ (기존)
- `산입하지 않는다` ✓ (신규 — case 2)
- `포함되지 않는다` ✓ (신규)

**우선순위 체크**: STATEMENT는 PROHIBITION(rule_8) 다음. PROHIBITION의 `아니 된다`, `금지한다`가 먼저 매칭되어 충돌 없음.

---

## 3. 적용 절차

### Step A — Cursor에 patch 적용

```
docs/extraction/CURSOR_TASK_2026-05-06_decompose_v141_patch.md를 읽고
§2의 2개 변경(2-1 rule_7 동사 어간 광범, 2-2 rule_13 부정 어미 추가)을
docs/extraction/scripts/decompose_v1.py의 classify_content_type() 함수에
정확히 적용해줘.

규칙:
- 2-1: rule_7 정규식 한 줄만 변경. 우선순위/순서 절대 변경 금지
- 2-2: rule_13 정규식 한 줄만 변경. 다른 룰 영향 없음
- 끝나면 git diff --numstat 결과만 보고
```

### Step B — dry-run 재검증

```bash
cd ~/Desktop/tai-engineering/tai-admin
git pull origin main

railway run python3 docs/extraction/scripts/decompose_v1.py \
  --sample-size 200 --sampling random --dry-run --seed 42 \
  --debug-classify 2>&1 | tee /tmp/decompose_v141_debug.log

# 핵심 부분만 확인
grep -E "DEBUG-CLASSIFY|미분류|content_type|NEEDS_REVIEW" /tmp/decompose_v141_debug.log
```

기대:
- `[DEBUG-CLASSIFY] 미분류 with 있다:` 라인 **0건 또는 거의 없어야**
- 미분류 비율 **< 3%**

### Step C — apply (truncate-first 작동 확인 포함)

```bash
railway run python3 docs/extraction/scripts/decompose_v1.py \
  --sample-size 200 --sampling random --apply --seed 42 \
  --truncate-first 2>&1 | tee /tmp/decompose_iter1_v141_apply.log

cat /tmp/decompose_iter1_v141_apply.log
```

확인:
- `[TRUNCATE]` 또는 그에 상응하는 메시지 (RPC 의존 제거 확인)
- `[INFO] 폐지 조문 제외: N건`
- `[DONE] inserted N clauses`

### Step D — 적재 검증

apply 결과 chat에 붙여주세요. 제가 SQL로 적재 검증 + 미분류 잔여 패턴 분석.

---

## 4. v1.4.1 통과 기준

| 지표 | v1.4 (200건) | v1.4.1 목표 |
|---|---|---|
| content_type 미분류 비율 | 4.4% | **< 3%** (이상적: < 1%) |
| `[DEBUG-CLASSIFY]` 미분류 with 있다 | 3건 | **0건** |
| sample 5/5 분해 품질 | 5/5 | 5/5 유지 |
| `하지 않는다` 매칭 (rule_13) | 0 | **>= 1건** |

**셋 다 통과** → sample 500건 확장 또는 본 적용 (51,959건 - 1,962 폐지 = 49,997건) 진입 결정
**미달** → v1.5 보강 (남은 미분류 패턴 추가 분석)

---

## 5. 메모

- v1.4.1는 매우 작은 patch (정규식 2줄 변경) — Cursor 작업 5분 이내
- v1.4의 폐지 조문 제외(1,962건) + 둔다/또한 같다 추가가 가장 큰 효과였고, v1.4.1은 마무리 정밀화
- 통과 시 본 적용 직전 단계. sample 500~1000건 한 번 더 검증한 후 49,997건 전체 적용 권고
- 본 적용은 임시 테이블 → 본 테이블 `semantic_clause` 마이그레이션 동시 진행
