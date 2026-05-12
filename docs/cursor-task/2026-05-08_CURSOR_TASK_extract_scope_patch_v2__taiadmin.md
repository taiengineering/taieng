# CURSOR_TASK 2026-05-08 — extract_scope patch v2 (4월 후반 자산 통합)

> 기존 `extract_scope_from_clauses.py`에 4월 후반 (5/4 ~ 5/5) 작업 자산 통합.
> 목적: 후수정 회피, 정확한 추출 방식 안정화 (사용자 원칙: "진짜 산출물은 안정화된 추출 방식").

---

## 0. 핵심 원칙 (4월 후반에서 가져옴)

### PRINCIPLE_RECALL_FIRST
> "불완전한 1건이 누락된 1건보다 낫다"
- 불완전한 추출 = 검토·정정 가능 (needs_review=true)
- 누락된 의무 = 영원한 사각지대
- 의심스러우면 추출 + needs_review (skip 회피)

### PRINCIPLE_NO_SELF_REINFORCEMENT
> "추출기와 검증기는 다른 메커니즘"
- 추출기 = 정규식 + 키워드 사전
- 검증기 = 추출 후 SQL/사전 매칭 (별도 단계)
- 같은 룰셋 사용 시 자기 충족 사이클 = 약점 영원히 안 보임

### 작업 원칙 (오늘 추가)
- 의미해석 0%: 매핑 안 되면 NULL + needs_review
- AI/LLM 호출 0%: 정규식 + 키워드 사전만

---

## 1. 변경 사항 — `extract_scope_from_clauses.py`

### 1-1. 가운뎃점 normalize 추가 (verification B-1)

`extract_thresholds()` 함수 시작에 normalize 적용:

```python
def normalize_text(text):
    """가운뎃점 normalize: ㆍ (한글, U+318D) ↔ · (라틴, U+00B7)
    
    discovered_in: verification_patterns.yaml v0.3 B-1 (16/16 drafts 100% 재현)
    rationale: 추출 단계에서 자동 변형됨. substring 비교 시 false fail 방지.
    """
    if not text:
        return text
    return text.replace('ㆍ', '·').replace('・', '·')

def extract_thresholds(text):
    """4값 분해. 매핑 안 되면 NULL 반환 (추정 금지)."""
    if not text:
        return []
    
    text = normalize_text(text)  # ⭐ 추가
    
    thresholds = []
    # ... 기존 코드 그대로
```

### 1-2. THRESHOLD_PATTERNS 보강 (rule_patterns.yaml v1.2 COND_001~004 통합)

#### 면적 패턴 — `평방미터` 단위 추가

```python
# 패턴 2 (area)
{
    'name': 'area',
    'pattern': r'(?P<criterion>연면적|대지면적|건축면적|면적)(?:\s*(?:이|가|은|는|의))?\s*(?P<value>\d+(?:,\d{3})*(?:\.\d+)?)\s*(?P<unit>㎡|제곱미터|평방미터|m²|m2|평)\s*(?P<op>이상|이하|초과|미만)',
    #                                                                                                                                                  ↑ 평방미터 추가
    'criterion_code': 'area_floor',
},
```

#### 공사금액 패턴 — "억\s*원" / "만\s*원" 띄어쓰기 허용

```python
# 패턴 3 (construction_amount) — rule_patterns COND_003 통합
{
    'name': 'construction_amount',
    'pattern': r'(?P<criterion>공사금액|총공사금액|도급금액|계약금액)(?:\s*(?:이|가|은|는|의))?\s*(?P<value>\d+(?:,\d{3})*(?:\.\d+)?)\s*(?P<unit>억\s*원|만\s*원|억원|만원|천만원|백만원|원)\s*(?P<op>이상|이하|초과|미만)',
    #                                                                                                                                                                                                                       ↑ 띄어쓰기 허용 (억\s*원, 만\s*원)
    'criterion_code': 'construction_amount',
},
```

### 1-3. OPERATOR_MAP — 4개 그대로 유지

⚠️ rule_patterns.yaml COND_004의 "이내/이전"은 scope_threshold가 아니라 master_rule_v2_value (DUE) 영역. 
scope_threshold OPERATOR_MAP은 4개 (이상/이하/초과/미만)만 유지.

```python
OPERATOR_MAP = {
    '이상': 'GTE',
    '이하': 'LTE',
    '초과': 'GT',
    '미만': 'LT',
}
# '이내', '이전'은 추가하지 않음 (scope ≠ duration)
```

### 1-4. 분류형 추출 — 가운뎃점 normalize 적용

`extract_building_use`, `extract_facility`, `extract_equipment`, `extract_industry` 등 모든 분류형 추출 함수에 normalize 적용:

```python
def extract_building_use(text):
    if not text:
        return []
    text = normalize_text(text)  # ⭐ 추가
    found = set()
    for kw, code in BUILDING_USE_DICT.items():
        if kw in text:
            found.add(code)
    return sorted(list(found))

# extract_facility, extract_equipment, extract_industry, extract_construction_type, extract_process 동일하게 적용
```

---

## 2. 작업지시서 § 0 (절대 금지) — 그대로 유지

기존 작업지시서의 5개 절대 금지 사항 + 자가 검증 5개 그대로.

추가 금지 사항:
- ❌ "이전/이내" operator를 scope_threshold에 추가하지 말 것 (rule_value 영역)
- ❌ verification_patterns.yaml의 검증 룰을 추출 단계에 적용하지 말 것 (검증은 별도 단계)

---

## 3. dry-run 검증

```bash
# 1. 일반 sample 100 — 보강 후 INSERT 대상 줄어든 효과 확인
railway run python3 extract_scope_from_clauses.py --dry-run --sample-size 100

# 2. 임계값 sample 100 — 정규식 보강 효과 확인 (가장 중요)
railway run python3 extract_scope_from_clauses.py --dry-run --sample-size 100 --sample-with-threshold
```

### 기대 결과 (보강 효과)

| 지표 | 이전 (조사 보강만) | 이번 (가운뎃점 + 면적/금액 보강) |
|---|---|---|
| 임계값 sample 100, thresholds | 12 | 14~18 추정 |
| 임계값 sample 100, scopes | 26 | 28~32 추정 |
| needs_review 비율 | 76.9% | 70~75% 추정 |

매칭률 1.5~2배 추가 향상 예상.

---

## 4. 자가 검증 (작성 후 commit 전)

```
□ normalize_text() 함수 추가됨
□ THRESHOLD_PATTERNS area에 "평방미터" 추가됨
□ THRESHOLD_PATTERNS construction_amount에 "억\s*원|만\s*원" 추가됨
□ extract_* 함수 6개 모두에 normalize_text() 호출 추가됨
□ OPERATOR_MAP는 4개 그대로 유지됨 ("이내/이전" 추가 안 됨)
□ verification_patterns.yaml의 추출 외 패턴 (B-3 어순, C-2 조사 등) 적용 안 됨
□ obligation_type_dictionary.yaml 적용 안 됨 (검증 단계용)
□ dry-run 출력 강화 (matched 4건 + unmatched 10건) 그대로 유지됨
```

---

## 5. 진행 흐름

```
1. 본 작업지시서대로 patch 적용
2. dry-run 1번 (일반)
3. dry-run 2번 (임계값 sample) — 매칭 14건+ 기대
4. 매칭 향상 확인 후 사용자 보고
5. 전체 적용 진행 (--apply)
```

---

## 6. 200줄+ 파일 처리

기존 `extract_scope_from_clauses.py`가 600줄+로 추정. **GitHub MCP 직접 수정 금지**, Cursor 로컬 + git push.

```bash
cd ~/Cursor/tai-admin/docs/extraction/scripts/
# Cursor에 본 작업지시서 첨부 + 패치 요청

# 자가 검증 8개 통과 확인 후
git add extract_scope_from_clauses.py
git commit -m "feat(extraction): 4월 후반 자산 통합 — 가운뎃점 normalize + 면적/금액 패턴 보강"
git push origin main
```

---

## 7. 통합 출처 명시

| 변경 | 출처 | 효과 |
|---|---|---|
| 가운뎃점 normalize | verification_patterns.yaml v0.3 B-1 | substring 비교 false fail 방지 |
| 평방미터 단위 | rule_patterns.yaml v1.2 COND_001 | 면적 매칭률↑ |
| 억원/만원 띄어쓰기 | rule_patterns.yaml v1.2 COND_003 | 공사금액 매칭률↑ |
| PRINCIPLE_RECALL_FIRST | rule_patterns.yaml v1.2 core_principles | needs_review 정책 강화 |
| PRINCIPLE_NO_SELF_REINFORCEMENT | rule_patterns.yaml v1.2 core_principles | 검증 분리 |

→ 이 통합으로 후수정 작업 회피 + 처음부터 안정된 추출 방식.
