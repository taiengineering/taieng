# CURSOR TASK 2026-05-08: decompose_v1.py v1.9.1 (회귀 수정 + cleanup 강화)

> v1.9 sample 1000 dry-run 결과 — executor 채움률 **94.4%** 달성, 그러나 **회귀 1건 + cleanup 결함** 발견.
>
> 본 적용 전 마무리 보강 (10분 작업).

---

## 변경 사유 (v1.9 dry-run에서 발견된 2개 결함)

### 결함 1: `select_best_subject_match` 회귀

```
원문: "행정안전부장관은 ... 위원이 ... 경우에는 ..."

v1.8: "행정안전부장관" ✓
v1.9: "호에 따른 위원" ✗  ← 조건절 안의 거짓 주어 선택
```

**원인**: 두 후보 모두 `condition_end` 앞에 있어 `outside`가 비어 있음 → 알고리즘이 `candidates` 전체에서 가장 뒤쪽 선택 → 조건절 안의 거짓 주어("위원이").

### 결함 2: `SUBJECT_PREFIX_CLEANUP` 부분 매칭

```
원문: "제5항에 따라 지정된 교육실시기관은 ..."

v1.9: "항에 따라 지정된 교육실시기관" ✗  ← cleanup이 "제5"만 제거
정답: "교육실시기관" 또는 "지정된 교육실시기관"
```

**원인**: lazy `.*?`가 "제5"만 매치하고 끊음 → "항에 따라" 잔존.

---

## 패치 1. select_best_subject_match — "은/는" 우선 규칙

### 핵심 통찰

한국어 법령 문장에서:
- **"은/는"** = 의무 주어 (행위자) — 거의 항상
- **"이/가"** = 조건절 주어가 흔함 (`X이/가 ... 경우/때`)

→ "은/는" 후보를 무조건 우선시키면 회귀 케이스 정확히 처리됨.

### 코드 (v1.9 → v1.9.1 교체)

```python
def select_best_subject_match(candidates, text):
    """
    v1.9.1 — "은/는" 우선 규칙.
    
    Returns: (noun, marker, position) 또는 None
    
    candidates는 re.finditer 결과라 위치 순서로 정렬됨 → [0]이 가장 앞쪽.
    """
    if not candidates:
        return None
    
    condition_end = find_condition_end(text)
    
    # "은/는" 후보와 "이/가" 후보 분리
    eun_neun = [c for c in candidates if c[1] in ('은', '는')]
    i_ga = [c for c in candidates if c[1] in ('이', '가')]
    
    # 1. 조건절 밖의 "은/는" 최우선 (= 의무 주어)
    if condition_end >= 0 and eun_neun:
        outside_en = [c for c in eun_neun if c[2] >= condition_end]
        if outside_en:
            return outside_en[0]  # 가장 앞쪽
    
    # 2. 모든 "은/는" 중 시작 부분 (조건절 안에 있어도 의무 주어 가능성 높음)
    if eun_neun:
        return eun_neun[0]  # 가장 앞쪽 — 보통 진짜 의무 주어
    
    # 3. "이/가"만 있다면 조건절 밖 우선
    if condition_end >= 0:
        outside_ig = [c for c in i_ga if c[2] >= condition_end]
        if outside_ig:
            return outside_ig[0]
    
    if i_ga:
        return i_ga[0]
    
    return candidates[0]
```

**중요 변경**: 기존 v1.9의 `outside.sort(key=lambda x: x[2], reverse=True)` (가장 뒤) 로직 **제거**. "은/는" 우선 + 시작 부분 우선으로 대체.

### 검증

| Sample | 후보 | v1.9 결과 | v1.9.1 예상 |
|---|---|---|---|
| 회귀 [1] | "행정안전부장관/은(0)", "위원/이(30)" | "위원" ✗ | **"행정안전부장관"** ✓ |
| 이전 still_null #3 | "양성기관/이(15)", "장관/은(50)" 조건절 밖 | "장관" ✓ | "장관" ✓ (유지) |
| 이전 still_null #4 | "공단/은" | "공단" ✓ | "공단" ✓ (유지) |
| 이전 still_null #5 | "원인자부담금/은" | review ✓ | review ✓ (유지) |
| sample [2] 200 | "기후에너지환경부장관/은", ... | (위임) | (DELEGATION 재분류 유지) |

---

## 패치 2. SUBJECT_PREFIX_CLEANUP 정규식 강화

### 변경

article ref + "에 따라/따른" + 동사 prefix를 **명시적으로** 매칭:

```python
# v1.9 (기존, lazy .*?로 너무 짧게 끊김)
SUBJECT_PREFIX_CLEANUP = re.compile(
    r'^.*?(?:에\s*따라|에\s*따른|에\s*의한|에\s*의해)\s*'
)

# v1.9.1 (명시적 매칭)
SUBJECT_PREFIX_CLEANUP = re.compile(
    r'^(?:법\s*)?'                                           # "법" 시작 (선택)
    r'(?:제\s*\d+\s*(?:조|항|호)(?:의\s*\d+)?'                # 첫 article ref (제5조의2)
    r'(?:\s*제\s*\d+\s*(?:조|항|호))*\s*)?'                  # 추가 ref (제2항제3호)
    r'(?:[가-힣]+\s+){0,2}'                                   # 부사구 (단서/본문 등 1~2 토큰)
    r'(?:에\s*따라|에\s*따른|에\s*의한|에\s*의해|단서에\s*따라|부터\s*제\s*\d+\s*항까지의\s*규정에\s*따라)\s*'
    r'(?:[가-힣]+(?:된|받은|한|승인된|지정된|위탁받은)\s+)?'    # 동사 prefix
)
```

### 검증

| 입력 | v1.9 결과 | v1.9.1 결과 |
|---|---|---|
| "제5항에 따라 지정된 교육실시기관" | "항에 따라 지정된 교육실시기관" ✗ | **"교육실시기관"** ✓ |
| "법 제48조의6제8항 단서에 따라 산재보험 노무제공자" | (부분 cleanup) | **"산재보험 노무제공자"** ✓ |
| "제2항에 따라 지정된 전문인력 양성기관" | (부분 cleanup) | **"전문인력 양성기관"** ✓ |
| "제18조제2항부터 제4항까지의 규정에 따라 신고를 한 자" | (cleanup 부족) | **"한 자"** ✓ (또는 alias로 후속 처리) |
| "행정안전부장관" (cleanup 대상 아님) | "행정안전부장관" ✓ | "행정안전부장관" ✓ (유지) |

가드는 v1.9 그대로:

```python
def cleanup_subject_candidate(noun):
    if not noun:
        return noun
    cleaned = SUBJECT_PREFIX_CLEANUP.sub('', noun)
    if not cleaned or len(cleaned.strip()) < 2:
        return noun.strip()
    return cleaned.strip()
```

---

## 패치 3. version

```python
print("[의미절 분해 v1.9.1 — dry-run]")
"decomposition_version": "v1.9.1",
```

---

## 테스트 흐름

```bash
# 1. Cursor 로컬 v1.9.1 적용 (10분)
# 2. dry-run sample 1000:
railway run python3 decompose_v1.py --dry-run --sample-size 1000 --sampling stratified --seed 42
# 3. 결과 채팅에 보고 → 본 적용 결정
```

---

## 회귀 검증 sample (dry-run 출력에서 확인)

dry-run sample 1000은 seed=42로 고정되어 있어 같은 paragraph가 sample에 들어옴. 다음 두 케이스가 정상 처리되는지 확인:

```
[CASE A — 회귀 수정 검증]  (sample [1] = 0008051)
원문: "행정안전부장관은 제8조의4제2항제2호에 따른 위원이 제1항 각 호의 어느 하나에 해당하는 경우에는 해당 위원을 해촉(解囑)할 수 있다."
기대 executor: "행정안전부장관"

[CASE B — cleanup 강화 검증]  (sample [4] = 0006021)
원문: "제5항에 따라 지정된 교육실시기관은 교육을 실시한 경우 교육 수료증을 발급하고 ..."
기대 executor: "교육실시기관" 또는 "지정된 교육실시기관"
```

---

## 판정 기준 (v1.9.1 sample 1000)

| executor 채움률 | 회귀 케이스 | 판정 |
|---|---|---|
| ≥94% | A=정답, B=정답 | **본 적용 진행** ✅ |
| ≥94% | A 또는 B 회귀 | 추가 보강 |
| <94% | — | 알고리즘 부작용 점검 |

v1.9.1은 v1.9 대비 채움률이 **떨어지면 안 됨** (94.4% → 동등 이상 유지). "은/는" 우선 규칙이 일부 케이스에서 채움률에 영향 줄 수 있으니 모니터링.

---

## 본 적용 절차 (v1.9.1 통과 후)

```bash
# 1. 본 적용 (iter1 truncate + 재추출):
railway run python3 decompose_v1.py --apply --truncate-first

# 2. 검증 SQL 7개 (CURSOR_TASK_2026-05-08_decompose_v19.md 참조)

# 3. iter1 → 본 동기화 (별도 SQL)

# 4. 무결성 재검증 (사용자 지시) — 새 회귀 발견 시 v2.0
```

---

## 작업 원칙 (불변)

1. AI/LLM 호출 0%
2. 검증 없는 완료 선언 금지
3. 패턴 발견 → 룰 보강 → 재반복
4. 의미절 출처 추적 가능
5. 200줄+ 파일은 GitHub MCP 직접 수정 금지 → Cursor 로컬

---

## 관련 문서

- `CURSOR_TASK_2026-05-08_decompose_v19.md` — v1.9 작업지시서 (적용됨)
- `PATTERN_MINING_2026-05-08_v2.md` — v1.9 사전 채굴
- `decompose_v1.py` — v1.9 적용 상태 (v1.9.1 수정 대상)
- `HANDOFF_FINAL_2026-05-07.md` — 통합 핸드오프
