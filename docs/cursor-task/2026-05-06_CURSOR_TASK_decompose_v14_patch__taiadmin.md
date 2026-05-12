# Cursor 작업지시서 PATCH — 의미절 분해 v1.4 (200건 apply 결과 반영)

> 이전 doc: `docs/extraction/CURSOR_TASK_2026-05-06_decompose_v13_patch.md`
> 적용 대상: `docs/extraction/scripts/decompose_v1.py`
> 트리거: 200건 apply 후 미분류 20건(8.4%) 패턴 분석에서 4가지 발견

---

## 1. 200건 apply 결과 진단

| 지표 | 50건 (v1.3) | 200건 (v1.3) | 안정성 |
|---|---|---|---|
| 분해 확장률 | 1.18 | 1.185 | 매우 안정적 ✓ |
| content_type 미분류 | 6.8% | **8.4%** (20/237) | 약간 ↑ (새 패턴) |
| needs_review | 47.5% | 46.0% | 안정 ✓ |
| inherit 카운트 | 9 | 34 | 비례 ✓ |
| `과/와 같다` 매칭 | 1 | 13 | 풍부 ✓ |

**미분류 20건 패턴 분류** (실제 SQL 분석):

| 패턴 | 빈도 | 비율 | 처리 |
|---|---|---|---|
| `삭제 <YYYY.M.D>` (폐지 조문) | **8건** | 40% | 모집단 제외 |
| `~할 수 있다` 매칭 실패 | **5+건** | 25%+ | **정규식 디버그 필요** |
| `둔다` (조직 설치) | 3건 | 15% | rule_6에 추가 |
| `또한 같다` (반복 적용) | 1건 | 5% | rule_11에 추가 |
| `~하며` 비종결 + last도 미분류 | 2~3건 | 10~15% | inherit 대상 확장 |

---

## 2. 변경 사항 (4개)

### 2-1. 폐지 조문 제외 (가장 큰 효과 — 미분류 -8건)

**위치**: `decompose_v1.py`의 모집단 fetch 단계 (`fetch_population` 함수 또는 `random` 모드 fetch 직후)

```python
# 폐지 조문 패턴 (조문 번호 + "삭제" + 개정 일자)
DELETED_ARTICLE_PATTERN = re.compile(
    r'^(?:제\s*\d+(?:조|항)?(?:의\s*\d+)?\s*)?삭제\s*<\d{4}'
)

# 모집단 fetch 후 필터링
def filter_deleted(parts):
    """삭제된 조문은 의미절 분해 대상에서 제외."""
    filtered = []
    deleted_count = 0
    for p in parts:
        text = (p.get('part_text') or '').strip()
        if DELETED_ARTICLE_PATTERN.match(text):
            deleted_count += 1
            continue
        filtered.append(p)
    if deleted_count > 0:
        print(f"[INFO] 폐지 조문 제외: {deleted_count}건")
    return filtered
```

`random` 모드에서:
1. 페이지네이션으로 paragraph 모집단 전체 fetch
2. **`filter_deleted` 적용** (신규)
3. `random.sample(filtered_pool, sample_size)`

`stratified` 모드도 동일하게 fetch 후 filter_deleted 적용.

### 2-2. rule_6 (OBLIGATION) — `둔다` 추가, rule_11 (DELEGATION) — `또한 같다` 추가

`classify_content_type()` 함수에서:

```python
# 변경 전 (v1.3) — DELEGATION 줄
if re.search(r'(?:준용한다|에\s*따른다|에\s*의한다|을\s*적용한다|에\s*의하여\s*한다|을\s*따른다|(?:과|와)\s*같다)\.?$', text):
    return 'DELEGATION', 'rule_11_delegation'

# 변경 후 (v1.4) — `또한 같다` 추가
if re.search(r'(?:준용한다|에\s*따른다|에\s*의한다|을\s*적용한다|에\s*의하여\s*한다|을\s*따른다|(?:과|와)\s*같다|또한\s*같다)\.?$', text):
    return 'DELEGATION', 'rule_11_delegation'
```

```python
# 변경 전 (v1.3) — OBLIGATION verb 줄
if re.search(r'(?:정한다|결정한다|실시한다|작성한다|보고한다|제출한다|관리한다|점검한다|확인한다)\.?$', text):
    return 'OBLIGATION', 'rule_6_obligation_verb'

# 변경 후 (v1.4) — `둔다` 추가
if re.search(r'(?:정한다|결정한다|실시한다|작성한다|보고한다|제출한다|관리한다|점검한다|확인한다|둔다)\.?$', text):
    return 'OBLIGATION', 'rule_6_obligation_verb'
```

### 2-3. `할 수 있다` 매칭 실패 디버그 (가장 중요)

**문제**: 200건 apply에서 다음 케이스들이 미분류로 떨어짐. 모두 `할 수 있다` 종결인데 rule_7 정규식이 매칭되어야 정상:

```
"3년 이내의 범위에서 자격을 정지시킬 수 있다."
"...해임한 사실의 확인을 받을 수 있다."
"...전자정보처리프로그램과 연동시킬 수 있다."
"...분과위원회의 위원이 될 수 있다."
```

현재 정규식: `r'할\s*수\s*있다\.?$'`

이론적으론 매칭되어야 함. 매칭 안 되는 원인 추정:
- 분해 후 segment text의 trailing whitespace, newline, NBSP, 특수 dot
- 또는 `있다` 외의 어미 (`있다고 본다`, `있다는` 등) 케이스가 다른 룰에 우선 매칭되어 빠짐

**디버그 작업**:

`classify_content_type()` 함수 내부에서, **첫 호출 시 또는 디버그 모드일 때** repr 출력:

```python
# 디버그 옵션 (CLI 인자 추가)
parser.add_argument('--debug-classify', action='store_true',
    help='classify_content_type 매칭 실패 케이스의 text repr 출력')

# classify_content_type 함수 내부
def classify_content_type(text, debug=False):
    # ... 기존 우선순위 매칭 ...

    # 미분류로 떨어지기 직전, '있다' 포함 텍스트는 디버그 출력
    if debug and '있다' in text:
        last_50 = text[-50:] if len(text) > 50 else text
        print(f"[DEBUG-CLASSIFY] 미분류 with 있다: repr={last_50!r}")

    return None, None
```

dry-run에서 `--debug-classify`로 실행 → 미매칭 텍스트의 정확한 끝부분 (특수문자 포함) 확인 → 정규식 보강 또는 text normalize 추가.

**예상 fix 후보** (디버그 결과에 따라 택1):

```python
# 가설 A: trailing whitespace/newline 문제
text = re.sub(r'\s+$', '', text)  # 매칭 전에 trailing 정리

# 가설 B: 분해 후 마침표 누락 또는 특수 dot
text = text.rstrip('.\n\r\t ㆍ\u00a0')

# 가설 C: 정규식이 strict하게 끝(\)에 매칭 → 다른 토큰 뒤에 더 있을 수도
# 정규식 완화: `할\s*수\s*있다(?:\.|$|\n|\s)`
```

### 2-4. truncate-first RPC 의존 제거 (이전 보류 사항)

**위치**: `main()` 함수 내 `--truncate-first` 처리 부분

```python
# 변경 전 (안 되는 코드)
with_retry(lambda: supabase.rpc("execute_sql", {"query": "TRUNCATE semantic_clause_iter1;"}).execute())

# 변경 후 (PostgREST 표준 API)
ZERO_UUID = '00000000-0000-0000-0000-000000000000'
with_retry(lambda: supabase.from_('semantic_clause_iter1').delete().neq('id', ZERO_UUID).execute())
print("[TRUNCATE] semantic_clause_iter1 비움 완료")
```

---

## 3. 적용 절차

### Step A — Cursor에 patch 적용

```
docs/extraction/CURSOR_TASK_2026-05-06_decompose_v14_patch.md를 읽고
§2의 4개 변경(2-1 폐지 조문 제외, 2-2 둔다/또한 같다 추가,
2-3 "할 수 있다" 디버그 + fix, 2-4 truncate-first fix)을
docs/extraction/scripts/decompose_v1.py에 정확히 적용해줘.

규칙:
- 2-1: 폐지 조문 패턴은 정확히 doc 명시 정규식 사용
- 2-2: 정규식에 둔다/또한 같다만 추가. 우선순위 순서 절대 변경 금지
- 2-3: 먼저 --debug-classify 옵션으로 매칭 실패 케이스의 repr 출력 기능 추가.
  그 후 디버그 dry-run 1회 돌리는 것은 사용자가 함. dry-run 결과 따라
  가설 A/B/C 중 적절한 fix를 코드에 적용 (이건 사용자가 디버그 결과 보고 결정).
  지금은 일단 --debug-classify 옵션 + repr 출력만 추가.
- 2-4: RPC 호출을 delete().neq() 표준 API로 교체
- 한 파일 700줄 이내 권장
- 끝나면 git diff --numstat 결과만 보고
```

### Step B — 디버그 dry-run (`할 수 있다` 미매칭 원인 파악)

```bash
cd ~/Desktop/tai-engineering/tai-admin
git pull origin main

railway run python3 docs/extraction/scripts/decompose_v1.py \
  --sample-size 200 --sampling random --dry-run --seed 42 \
  --debug-classify 2>&1 | tee /tmp/decompose_v14_debug.log

# 디버그 라인만 추출
grep "DEBUG-CLASSIFY" /tmp/decompose_v14_debug.log
```

→ `[DEBUG-CLASSIFY] 미분류 with 있다: repr=...` 라인을 chat에 붙여주세요.
이 repr을 보고 가설 A/B/C 중 어떤 게 맞는지 결정 → 다음 patch v1.4.1로 fix 적용.

### Step C — patch v1.4.1 (`할 수 있다` fix 적용)

디버그 결과 받은 후 별도 patch doc에서 정확한 정규식/normalize 코드 적용. (이번 doc 범위 외)

### Step D — 200건 재실행 (v1.4 적용 후)

`할 수 있다` fix까지 끝난 후:

```bash
# 임시 테이블 정리 (이번엔 코드의 truncate-first 사용)
railway run python3 docs/extraction/scripts/decompose_v1.py \
  --sample-size 200 --sampling random --apply --seed 42 \
  --truncate-first 2>&1 | tee /tmp/decompose_iter1_v14_apply.log

cat /tmp/decompose_iter1_v14_apply.log
```

→ `[TRUNCATE]` 메시지 + `[DONE] inserted N clauses` 확인.

### Step E — 적재 검증 (제가 SQL 직접 실행)

다음 항목을 chat에 붙여주시면 제가 SQL 실행:
- apply 로그에 표시된 inserted clause 수
- 폐지 조문 제외 로그 (`[INFO] 폐지 조문 제외: N건`)

---

## 4. v1.4 통과 기준

| 지표 | v1.3 (200건) | v1.4 목표 |
|---|---|---|
| content_type 미분류 비율 | 8.4% | **< 3%** |
| needs_review 비율 | 46.0% | **< 45%** |
| 폐지 조문 제외 | 0 | **>= 5건 (200 sample 기준)** |
| `둔다` 매칭 | 0 | **>= 1건** |
| `또한 같다` 매칭 | 0 | **>= 1건** |
| inherit 카운트 | 34 | 비슷한 비율 유지 |

**셋 다 통과** → sample 500건 확장 또는 본 적용 진입 결정
**미달** → v1.5 보강

---

## 5. 메모

- 폐지 조문 8건 제외 = 미분류 -3.4%p
- `둔다`/`또한 같다` = -1.7%p
- `할 수 있다` fix = -2.1%p (5건 기준)
- 합계 약 -7.2%p → 8.4% - 7.2% = **1.2% 미분류 (예상)**, 통과 기준 < 3% 여유 있게 만족

- truncate-first 코드 fix 후엔 다음 iter부터 SQL 우회 불필요
- v1.4 통과 시 sample 500건 확장이 의미 있음 (200건은 안정성 확인 충분, 500건은 본 적용 직전 최종 검증)
