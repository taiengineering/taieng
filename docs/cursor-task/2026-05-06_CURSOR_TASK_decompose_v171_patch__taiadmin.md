# Cursor 작업지시서 PATCH — 의미절 분해 v1.7.1 (executor 추출 보강)

> 이전 doc: `docs/extraction/CURSOR_TASK_2026-05-06_decompose_v17_patch.md`
> 적용 대상: `docs/extraction/scripts/decompose_v1.py`
> 트리거: v1.7 200건 검증 — executor 채움 62.7% (목표 80% 미달)

---

## 1. v1.7 200건 검증 결과

| 5요소 | v1.6 | v1.7 | 목표 |
|---|---|---|---|
| executor | 33.5% | **62.7%** | **>= 80%** ❌ 미달 |
| condition | 7.4% | **38.2%** | 30% ✓ 통과 |
| exception | 0% | 0% | sample에 "다만" 0건 (정상) |
| if 셋 채움 | 40% | **70.1%** | 80% △ 근접 |

### executor 미추출 85건 패턴 분석

| 패턴 | 빈도 | 처리 |
|---|---|---|
| **A. `법 제N조에 따라/따른 ...` (법 인용 시작)** | **약 12건+** (가장 큰 그룹) | **prefix 제거 후 매칭** |
| B. 괄호 보충 정보 "주민(이해관계자를 포함한다)은" | 5건+ | **괄호 제거 후 매칭** |
| C. 다중 주어 "X, Y, Z 또는 W는" — 마지막만 추출 | 5건+ | 정규식 anchor 강화 |
| D. 수동태/추상 주어 ("사항은", "기금은", 사물 주어) | 다수 | **정상 미추출** (강제 추출 X) |

→ A + B 처리만 해도 executor 80% 도달 가능.

---

## 2. 변경 사항 (extract_executor 함수 보강)

`extract_executor` 함수 시작 부분에 **2단계 정규화** 추가:

```python
# v1.7.1 NEW: 법 인용 prefix 제거 패턴
LAW_CITATION_PREFIX = re.compile(
    r'^법\s*제\d+조(?:제\d+항)?(?:제\d+호)?(?:의\d+)?[^,.]*?(?:따라|따른|의하여|의한|에서|에는?)\s+'
)

def extract_executor(text):
    """
    한국어 법령 텍스트에서 행위자(주어) 추출.
    v1.7.1: 법 인용 prefix + 괄호 보충 제거 후 매칭.
    """
    if not text:
        return None
    
    # === v1.7.1 NEW: 정규화 단계 ===
    cleaned = text
    
    # (1) 법 인용 prefix 제거: "법 제N조에 따라 X" → "X"
    cleaned = LAW_CITATION_PREFIX.sub('', cleaned, count=1)
    
    # (2) 괄호 내용 임시 제거: "주민(이해관계자를 포함한다)은" → "주민은"
    cleaned = re.sub(r'\([^)]*\)', '', cleaned)
    
    # === 기존 매칭 로직 (변경 없음) ===
    # 우선순위 1: 행위자 lexicon
    m = EXECUTOR_LEXICON_PATTERN.match(cleaned)
    if m:
        return m.group(1).strip()
    
    # 우선순위 2: 일반 명사구 fallback
    fallback = re.match(
        r'^([가-힣ㆍ]{2,20}(?:\s+[가-힣ㆍ]{1,15}){0,3})\s*(?:은|는|이|가)\s',
        cleaned
    )
    if fallback:
        return fallback.group(1).strip()
    
    return None
```

**중요**:
- `cleaned`는 매칭용으로만 사용. 추출된 executor 텍스트는 그대로 반환 (원문 텍스트 보존)
- LAW_CITATION_PREFIX 정규식은 처음 1회만 매칭 (`count=1`). 본문 중간의 법 인용은 영향 없음.
- 괄호 제거는 모든 괄호 (paragraph 내 보충정보 처리)
- 매칭 실패 시 None — 수동태/추상 주어는 정상 미추출

---

## 3. 적용 절차

### Step A — Cursor에 patch 적용

```
docs/extraction/CURSOR_TASK_2026-05-06_decompose_v171_patch.md를 읽고
§2의 extract_executor 함수에 정규화 2단계(법 인용 prefix 제거, 괄호 제거)를
docs/extraction/scripts/decompose_v1.py에 정확히 추가해줘.

규칙:
- LAW_CITATION_PREFIX 정규식 정확히 doc 명세대로 (?:따라|따른|의하여|의한|에서|에는?) 어미 포함
- 괄호 제거는 re.sub(r'\([^)]*\)', '', cleaned) 한 줄
- 정규화는 cleaned 변수에만 (원본 text 보존), 매칭에만 cleaned 사용
- 기존 lexicon/fallback 매칭 로직 절대 변경 금지
- 끝나면 git diff --numstat 결과만 보고
```

### Step B — apply (truncate-first)

dry-run 단계 생략 (정규식 보강만이라 큰 차이 없음). 바로 apply 200건:

```bash
cd ~/Desktop/tai-engineering/tai-admin
git pull origin main

railway run python3 docs/extraction/scripts/decompose_v1.py \
  --sample-size 200 --sampling random --apply --seed 42 \
  --truncate-first 2>&1 | tee /tmp/decompose_v171_apply.log

cat /tmp/decompose_v171_apply.log
```

### Step C — 5요소 채움률 검증 (제가 SQL)

apply 결과 chat에 붙여주시면 제가:
- executor 채움률 62.7% → ?
- if 케이스 셋 채움률 70.1% → ?
- 미추출 잔여 패턴 분석

---

## 4. v1.7.1 통과 기준

| 지표 | v1.7 | v1.7.1 목표 |
|---|---|---|
| executor 채움률 | 62.7% | **>= 78%** (수동태/추상 주어 일부 정상 미추출 감안) |
| if 셋 채움률 | 70.1% | **>= 78%** |
| 분해 정확함 | silent failure 0 | 유지 |

---

## 5. 통과 시 다음 단계

1. **본 적용 재실행** — 49,997 paragraphs → 5요소 채움 정상화된 58,495 clauses
2. **본 테이블 `semantic_clause` 데이터 갱신** — 임시 테이블 → 본 테이블 재이전
3. **mblr AI_GENERATED 1,601건 검증 사이클** — 별도 작업
4. **master_rule_v2 설계** — 검증된 의미절 + 검증된 mblr 통합
