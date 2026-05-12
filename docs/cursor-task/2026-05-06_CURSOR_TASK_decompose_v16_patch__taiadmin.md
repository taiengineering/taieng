# Cursor 작업지시서 PATCH — 의미절 분해 v1.6 (정확함 검증 Round 1 결과 반영)

> 이전 doc: `docs/extraction/CURSOR_TASK_2026-05-06_decompose_v141_patch.md` (v1.5는 doc 없이 직접 명령으로 적용됨)
> 적용 대상: `docs/extraction/scripts/decompose_v1.py`
> 트리거: 500건 적재 후 sample 20건 정확도 검증에서 60% 정확도 (목표 80% 미달)

---

## 1. Round 1 정확함 검증 결과

500건 적재 후 OBL_fallback 10건 + INHERIT 10건 검증:

| 평가 | 건수 | 비율 |
|---|---|---|
| ✓ 정확 | 12/20 | **60%** |
| ❌ 명백 오분류 | 3/20 | 15% |
| 의심/검증 어려움 | 5/20 | 25% |

명백 오분류 3건 + 룰 순서 문제 3건 + inherit 의심 2건 → 4가지 보강 필요.

### 발견된 문제

**문제 1. `위임한다` 종결 — rule_11 DELEGATION 누락**
- 케이스: `…산림청장의 권한은 지방산림청장에게 위임한다.`
- 현재 분류: OBLIGATION fallback (틀림)
- 정답: DELEGATION (권한 위임)

**문제 2. inherit 정책 너무 광범**
- 케이스 1: `…자치구의 구청장을 말하며` → last_ct=OBLIGATION inherit. "말하며"는 정의 일부라 OBL 어색
- 케이스 2: `…임대료 등을 받지 못하거나` → last_ct=AUTHORITY inherit. 부정 행위 + AUTH 어색
- 케이스 3: `…피상속인의 지위를 승계하며` → last_ct=DEFINITION inherit. 명백히 오분류

**문제 3. rule_6 strong 정규식 너무 strict**
- 현재: `(?:하여야|해야|두어야)\s*한다` 만 매칭
- 빠지는 케이스: `내줘야 한다`, `받아야 한다`, `내보여야 한다`, `갖추어야 한다`, `지켜야 한다` 등
- 결과적으로 OBLIGATION 분류는 fallback으로 맞게 되지만 룰 통계 부정확

**문제 4 (보류). `~할 수 있다`가 fallback으로 떨어지는 case**
- 케이스: 긴 paragraph가 분해 후 끝부분이 다른 어미로 끝나는 듯. 분해 알고리즘 디버그 필요.
- 이번 v1.6에서는 보류 (별도 케이스 디버그 필요)

---

## 2. 변경 사항 (3개)

### 2-1. rule_11 (DELEGATION) — `위임한다` 추가

`classify_content_type()` 함수의 DELEGATION 매칭 줄:

```python
# 변경 전 (v1.4)
if re.search(r'(?:준용한다|에\s*따른다|에\s*의한다|을\s*적용한다|에\s*의하여\s*한다|을\s*따른다|(?:과|와)\s*같다|또한\s*같다)\.?$', text):
    return 'DELEGATION', 'rule_11_delegation'

# 변경 후 (v1.6) — 위임한다 추가
if re.search(r'(?:준용한다|에\s*따른다|에\s*의한다|을\s*적용한다|에\s*의하여\s*한다|을\s*따른다|(?:과|와)\s*같다|또한\s*같다|위임한다)\.?$', text):
    return 'DELEGATION', 'rule_11_delegation'
```

추가로 매칭되는 케이스:
- `…에게 위임한다.` ✓
- `…권한을 위임한다.` ✓

### 2-2. rule_6 obligation_strong — 한글 어미 일반화

`classify_content_type()` 함수의 OBLIGATION strong 매칭 줄:

```python
# 변경 전 (v1.5)
if re.search(r'(?:하여야\s*한다|해야\s*한다|두어야\s*한다)\.?$', text):
    return 'OBLIGATION', 'rule_6_obligation_strong'

# 변경 후 (v1.6) — 한글 1글자 + (어야|아야|여야|야) + 한다
if re.search(r'[가-힣](?:어야|아야|여야|야)\s*한다\.?$', text):
    return 'OBLIGATION', 'rule_6_obligation_strong'
```

추가로 매칭되는 케이스:
- `하여야 한다` ✓ (기존)
- `해야 한다` ✓ (기존)
- `두어야 한다` ✓ (기존)
- `내줘야 한다` ✓ (신규)
- `받아야 한다` ✓ (신규)
- `내보여야 한다` ✓ (신규)
- `갖추어야 한다`, `지켜야 한다`, `마쳐야 한다` 등 ✓ (신규)

**충돌 검증**:
- 단독 `한다`(앞에 한글 글자 + 어미 없음)는 매칭 안 됨 → fallback 그대로 작동
- `정한다`, `결정한다` 같은 verb는 strong이 매칭하지 않음 → rule_6_obligation_verb 정상 작동
- 우선순위 위치는 그대로 (verb 다음, fallback 전)

### 2-3. inherit 정책 보수화 — 비-OBLIGATION inherit는 review 마크

`classify_segments()` 함수의 inherit 처리 부분:

```python
# 변경 전 (v1.3 — 무조건 inherit)
if ct is None and last_ct is not None and not is_last:
    inherited_rules = rules + [f'inherit_from_last_segment(={last_ct})']
    final_results.append((last_ct, inherited_rules))

# 변경 후 (v1.6 — last가 OBLIGATION 외면 review 마크)
if ct is None and last_ct is not None and not is_last:
    inherited_rules = rules + [f'inherit_from_last_segment(={last_ct})']
    if last_ct != 'OBLIGATION':
        # 비-OBLIGATION inherit는 의미적 일관성 의심
        inherited_rules.append('inherit_review_required')
    final_results.append((last_ct, inherited_rules))
```

그리고 **needs_review 결정 부분**(보통 `decompose_paragraph` 또는 메인 루프 내)에서 `inherit_review_required` 처리:

```python
# 기존 needs_review 로직에 추가
if 'inherit_review_required' in applied_rules:
    needs_review = True
    review_reasons.append(f"비-OBLIGATION inherit 의심 (last segment의 content_type이 의미적으로 일치하지 않을 수 있음)")
```

**효과**: 
- OBLIGATION inherit는 그대로 (가장 흔하고 안전한 패턴)
- DEFINITION/AUTHORITY/PROHIBITION/STATEMENT/DELEGATION inherit는 needs_review=true 마크 → 사람 검증 가능
- inherit 정확함 정책상 일관성 확보

---

## 3. 적용 절차

### Step A — Cursor에 patch 적용

```
docs/extraction/CURSOR_TASK_2026-05-06_decompose_v16_patch.md를 읽고
§2의 3개 변경(2-1 위임한다 추가, 2-2 strong 정규식 일반화,
2-3 비-OBLIGATION inherit review 마크)을
docs/extraction/scripts/decompose_v1.py에 정확히 적용해줘.

규칙:
- 2-1: rule_11 정규식 한 줄만 변경
- 2-2: rule_6 strong 정규식 한 줄만 변경 (우선순위 순서 절대 변경 금지)
- 2-3: classify_segments 함수의 inherit 처리 + needs_review 결정 부분 둘 다 수정
- 다른 부분 절대 변경 금지
- 끝나면 git diff --numstat 결과만 보고
```

### Step B — 재apply (같은 seed 42, 500건)

```bash
cd ~/Desktop/tai-engineering/tai-admin
git pull origin main

railway run python3 docs/extraction/scripts/decompose_v1.py \
  --sample-size 500 --sampling random --apply --seed 42 \
  --truncate-first 2>&1 | tee /tmp/decompose_iter1_v16_apply.log

cat /tmp/decompose_iter1_v16_apply.log
```

### Step C — 정확함 재검증 (제가 SQL)

같은 sample 카테고리로 다시 추출 + 분류 결과 비교. 기대:
- 위임한다 케이스 → DELEGATION으로 정확 분류
- inherit 의심 케이스 → needs_review=true로 마크
- strong 매칭 카운트 ↑ (fallback 카운트 ↓)

목표: 정확도 60% → **>= 80%**

---

## 4. v1.6 통과 기준

| 지표 | v1.5 (500건) | v1.6 목표 |
|---|---|---|
| 미분류 비율 | 0.35% (2/568) | < 1% 유지 |
| Round 1 sample 20건 정확도 | 60% | **>= 80%** |
| `위임한다` DELEGATION 매칭 | 0 | **>= 1건** |
| 비-OBLIGATION inherit (review 마크) | 0 | **>= 5건** (의심 정책 작동 확인) |
| rule_6 strong 카운트 | 177 | **약 200~210** (`내줘야`/`받아야` 등 캐치) |

**통과** → Round 2 (PROHIBITION/STATEMENT/multi-clause split 검증) 후 본 적용
**미달** → 추가 분석

---

## 5. 메모

- 문제 4 (`할 수 있다` fallback 떨어짐)는 별도 디버그 필요. v1.6에선 보류, sample 200건의 #A7 case의 source_text 전체를 SQL로 raw 형태로 보고 분해 알고리즘 점검 후 v1.7에서 처리.
- v1.6 patch 후엔 정확도 이외 새 검증 지표(inherit 의심 마크 작동, 위임한다 DELEGATION 분류) 추가됨.
- inherit 정책 변경은 needs_review 비율 일시적 ↑ 가능 (45% → 50%대). 이건 정확함 검증 위해 의도된 trade-off.
