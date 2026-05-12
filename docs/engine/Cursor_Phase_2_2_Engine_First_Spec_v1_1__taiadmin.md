# [Cursor 위탁 v1.1] Phase 2.2 — 엔진 우선 수정 + 검증엔진 통합 + 데이터셋 처리

**작성일**: 2026-05-10  
**작성자**: PM 창 (Claude 기획창)  
**위탁 대상**: Cursor (TAI Backend / Railway)  
**선행 폐기**: `Cursor_Phase_2_2_Accuracy_Spec.md` v1.0 (commit `6f39d25540e5c8...`) — **순서 본질 오류 폐기**  
**선행 보전**:
- `Track_E_20260510_Phase2_1_Reverse_Validation.md` — PM 정확도 진단 (commit `eac06285de25e7f...`)
- `Track_ABCDE_Verification_Matrix_20260510.md` — 전수 검증 매트릭스 (commit `dc0617556b9070...`)

---

## 0. 본 명세의 본질 (v1.0 폐기 사유 + v1.1 정합)

### 0.1 v1.0 본질 오류

v1.0 명세는 **룰 변경 + 데이터 처리 한 패키지**로 작성:
```
[v1.0 잘못] DB 백업 → CHECK 확장 → 룰 UPDATE/INSERT → Phase 2 재실행 → 검증
              (룰 정확성 사전 검증 없이 데이터 처리, 결과로만 측정)
```

문제:
- 룰의 정확성이 사전 검증되지 않은 상태에서 데이터 처리
- 결과 PASS/FAIL이 데이터 처리 후에만 결정 → 다시 폐기 + 재실행 반복 위험
- **엔진 형태 작업이 아니라 "수정의 수정" 패턴** (사용자 본질 지적: "오염 양산 프로그램")
- validator.py 통합 누락 (임계 ≥ 50% 자의 사용)

### 0.2 v1.1 본질 (사용자 본질 지적 정합)

> "파싱과 검증엔진을 수정한 후 데이터셋 폐기 진행"

**올바른 순서**:
```
[v1.1 정합]
  Phase 2.2-A: 파싱엔진 수정 + 단위 검증 (DB 무관)
       ↓ PASS 확정 (룰별 ≥ 95%)
  Phase 2.2-B: 검증엔진 통합 (validator.py 그대로 활용)
       ↓ PASS 확정 (통합 단위 테스트)
  Phase 2.2-C: 데이터셋 처리 (수정·검증된 엔진으로)
       ↓ PASS 확정 (Stage 2 sample 정확도 ≥ 90%)
```

→ **엔진 우선 수정 → 검증엔진 통합 → 그 후 데이터 처리**. 각 단계 PASS 미달 시 다음 단계 진입 금지.

---

## 1. 절대 원칙 (마스터 §2 + validator.py 본질)

### 1.1 마스터 §2 절대 원칙

| 원칙 | 본 명세 적용 |
|---|---|
| ① LLM X | Kiwi + 정규식 + DB 빈도만 |
| ② 법령 보전 | source_text / tokenization_json 변경 X |
| ③ 누락 0건 | 151,751 row 변동 X |
| ④ 100% 매핑 | UPDATE만 (INSERT는 신규 룰만) |
| **⑤ 오염 = 데이터셋 단위 폐기** | **Phase 2.2-C에서 Phase 2.1 분류 폐기 (Phase 1 보전)** |
| ⑥ 검증 부담 0 | 사용자 sample 검증 요청 X |
| ⑦ Ground Truth 우선 | DB 직접 점검 |
| ⑧ DB가 ground truth | 진입 점검 SQL 필수 |

### 1.2 validator.py 본질 (Track A `engine/validator.py`, dev 브랜치, 변경 X)

```python
# 절대 변경 X — 그대로 활용
SAMPLE_ACCURACY_THRESHOLDS = {1: 0.95, 2: 0.90, 3: 0.90}
# Stage 2 ≥ 90% (마스터 §3.4 정합)
# PASS / WARNING [-5%p] / FAIL 3-단계
# docstring: "통과 기준 미달 = 데이터셋 truncate + 룰 수정 + 재실행 (마스터 §9.2)"
```

### 1.3 본 명세의 추가 강제 규칙

| 규칙 | 본질 |
|---|---|
| 단계별 PASS 미달 → 다음 단계 진입 금지 | 마스터 §2.5 정합 |
| validator.py **본문 수정 X** | 그대로 활용 (사용자 본질 지적 정합) |
| 임계 자의 변경 X | ≥ 90% 강제 (Stage 2) |
| 명세 외 작업 X | 임의판단 절대 금지 |
| FAIL 시 즉시 정지 + PM 회신 | `raise SystemExit` 강제 |

---

## 2. 작업 환경

| 항목 | 값 |
|---|---|
| Supabase Project ID | `vwlahtguyggrhvslabax` |
| 환경 | `railway run python3 ...` |
| 코드 base | `taiengineering/tai-api` (브랜치 `dev`) |
| 검증엔진 | `engine/validator.py` (8,100 bytes, **변경 절대 X**) |
| 파싱엔진 | `engine/subtype_rule_match.py` (3,305 bytes, **본 작업에서 보강**) |
| 룰 DB | `rule_classify_subtype` (활성 34 / 비활성 1) |
| 보고서 commit | `taiengineering/tai-admin` main |
| 코드 commit | `taiengineering/tai-api` dev |

### 2.1 진입 점검 SQL (필수, 마스터 §2.7)

```sql
SELECT 
  (SELECT COUNT(*) FROM stage_2_elements) AS total,                              -- 151,751
  (SELECT COUNT(*) FROM stage_2_elements WHERE sub_type='UNCLASSIFIED') AS uc,   -- 68,130
  (SELECT COUNT(*) FROM rule_classify_subtype WHERE enabled=true) AS active_rules; -- 34
-- 결과가 다르면 즉시 정지 + PM 회신
```

---

## 3. Phase 2.2-A — 파싱엔진 수정 + 단위 검증 (DB 무관)

### 3.1 본 단계의 본질

**DB는 절대 건드리지 않음**. 코드 파일 (`engine/subtype_rule_match.py` 등) 보강 + 단위 테스트만.

### 3.2 subtype_rule_match.py 보강 항목

#### 3.2.1 TAIL_REGEX 패턴 위치 지원 (신규)

현재 `pattern_position` ∈ {TAIL_1, TAIL_2, TAIL_3, TAIL_4, HEAD_1, ...}. 신규: **TAIL_REGEX** (정규식 기반 종결 매칭).

```python
# engine/subtype_rule_match.py 보강 (시안)
def match_tail_regex(text: str, pattern_regex: str) -> bool:
    """source_text 종결부에 정규식 매칭. COMPOSITE strategy 보강."""
    import re
    return bool(re.search(pattern_regex + r'$', text))

# match_strategy='COMPOSITE' + pattern_position='TAIL_REGEX' 시 활용
```

#### 3.2.2 NNG/NNB/NNP 통합 매칭 (신규)

신규 `ENUMERATION_ITEM_NOMINAL_TAIL` 룰의 명사 종결 패턴. 3개 룰로 분리하거나, `tag` 필드의 `|` OR 구분자 처리.

**권고: 3개 룰 분리** (단순화):
- ENUMERATION_ITEM_TAIL_NNG
- ENUMERATION_ITEM_TAIL_NNB
- ENUMERATION_ITEM_TAIL_NNP

`form: "*"` wildcard 처리는 코드에서 form match 생략 옵션 추가:

```python
# engine/subtype_rule_match.py
def _match_token(token: dict, target: dict) -> bool:
    if target.get('form') == '*':  # wildcard
        return token['tag'] == target['tag']
    return token['form'] == target['form'] and token['tag'] == target['tag']
```

### 3.3 신규 룰 시안 (코드 단위 테스트용, DB INSERT는 Phase 2.2-C에서)

| rule_name | sub_type | match_strategy | pattern | priority | 본질 |
|---|---|---|---|---|---|
| ENUMERATION_LIST_INTRO_DAUM_GACHO | ENUMERATION_LIST_INTRO | COMPOSITE | `다음\s*각\s*호와\s*같다\.?$` | 85 | 다음 각 호와 같다 |
| ENUMERATION_LIST_INTRO_DAUMGWA | ENUMERATION_LIST_INTRO | COMPOSITE | `다음과\s*같다\.?$` | 86 | 다음과 같다 |
| REFERENCE_TO_ATTACHMENT_BYPYO_GATDA | REFERENCE_TO_ATTACHMENT | COMPOSITE | `별표\s*\d+(?:의\d+)?와?\s*같다\.?$` | 72 | 별표 N과 같다 |
| REFERENCE_TO_ATTACHMENT_BYPYO_TTAREUNDA | REFERENCE_TO_ATTACHMENT | COMPOSITE | `별표\s*\d+(?:의\d+)?에\s*따른다\.?$` | 73 | 별표 N에 따른다 |
| REFERENCE_TO_ATTACHMENT_BYJI | REFERENCE_TO_ATTACHMENT | COMPOSITE | `별지\s*제\d+호\s*서식(?:과?\s*같다\|에\s*따른다)\.?$` | 74 | 별지 제N호 서식 |
| REFERENCE_INVOCATION_JUNYONG | REFERENCE_INVOCATION | TAIL_POS | `[준용/NNG, 하/XSV, ᆫ다/EF]` | 198 | 준용한다 |
| OBLIGATION_HEADER_YA_TAIL3 | OBLIGATION_HEADER | TAIL_POS | `[야/EC, 하/VX, ᆫ다/EF]` | 11 | 어야 축약 변형 |
| OBLIGATION_HAS_DUTY | OBLIGATION_HEADER | TAIL_POS | `[의무/NNG, 가/JKS, 있/VV, 다/EF]` | 12 | 의무가 있다 |
| PROHIBITION_HEADER_AN_DOEN | PROHIBITION_HEADER | TAIL_POS | `[안/MAG, 되/VV, ᆫ다/EF]` | 18 | 안 된다 |
| PROHIBITION_HEADER_MOTHANDA | PROHIBITION_HEADER | TAIL_POS | `[못하/VX, ᆫ다/EF]` | 23 | 못한다 |
| ENUMERATION_ITEM_TAIL_NNG | ENUMERATION_ITEM | TAIL_POS | `[*/NNG]` (wildcard form) | 251 | 명사 종결 |
| ENUMERATION_ITEM_TAIL_NNB | ENUMERATION_ITEM | TAIL_POS | `[*/NNB]` | 252 | 의존명사 종결 |
| ENUMERATION_ITEM_TAIL_NNP | ENUMERATION_ITEM | TAIL_POS | `[*/NNP]` | 253 | 고유명사 종결 |

### 3.4 단위 테스트 작성 (`tests/test_phase_22_rules.py` 신규)

각 신규 룰별 sample 100건 정확도 측정:

```python
# tests/test_phase_22_rules.py
from engine.subtype_rule_match import match_rule
import json

def test_enumeration_list_intro_daum_gacho():
    """ENUMERATION_LIST_INTRO_DAUM_GACHO sample 100건 정확도 ≥ 95%."""
    samples = load_samples('phase_22_samples/enumeration_list_intro.json')
    rule = load_rule('ENUMERATION_LIST_INTRO_DAUM_GACHO')
    
    correct = sum(1 for s in samples if match_rule(s['tokenization'], rule) == s['expected'])
    accuracy = correct / len(samples)
    
    assert accuracy >= 0.95, f"룰 정확도 {accuracy:.4f} < 0.95"

# 12+개 신규 룰 각각 동일 패턴
```

**sample 데이터 준비**:
- DB에서 각 패턴 매칭 row 100건 추출 → JSON 저장
- `expected=True` (TP) / `expected=False` (FP, 의도된 비매칭)
- Cursor가 추출 + 검증

### 3.5 검증 임계

| check | 임계 | status |
|---|---|---|
| 신규 룰 12개 단위 테스트 정확도 | 룰별 ≥ 95% | PASS 필수 |
| subtype_rule_match.py 보강 단위 테스트 | wildcard / TAIL_REGEX 통과 | PASS 필수 |
| 기존 단위 테스트 회귀 | 0 fail | PASS 필수 |
| coverage | ≥ 80% (Track A 정합) | PASS 필수 |

### 3.6 Phase 2.2-A PASS 미달 시

→ **즉시 정지 + PM 회신**. Phase 2.2-B 진입 금지. 룰 패턴 / 코드 보강 정정 후 재진행.

---

## 4. Phase 2.2-B — 검증엔진 통합 (validator.py 그대로 활용)

### 4.1 본 단계의 본질

**validator.py 본문 절대 변경 X**. 활용 패턴 작성 + 통합 단위 테스트.

### 4.2 통합 패턴 (`scripts/track_e_phase2_run.py` 보강)

```python
# scripts/track_e_phase2_run.py
from engine.validator import Validator
from db.supabase_client import get_supabase

def run_phase_22(...):
    sb = get_supabase()
    validator = Validator(supabase=sb)
    
    # ... Phase 2.2-C 데이터 처리 후 ...
    
    # Stage 2 sample 정확도 측정 (100조문)
    accuracy, sample_size = compute_sample_accuracy(
        sb=sb,
        sample_articles=100,
        check_categories=[
            'AS_본다', 'OBLIGATION_DETAIL_ITEM', 'ENUMERATION_ITEM',
            'ENUMERATION_LIST_INTRO', 'REFERENCE_TO_ATTACHMENT', 'REFERENCE_INVOCATION',
            # ... 모든 분류 sub_type
        ],
    )
    
    # validator.py 그대로 활용
    result = Validator.evaluate_sample_accuracy(
        stage=2,
        accuracy=accuracy,
        sample_size=sample_size,
    )
    result.verified_by = 'phase_22_run_2026-05-XX'
    validator.log(result)  # verification_log INSERT
    
    # 마스터 §2.5 정합 — FAIL/WARNING 시 즉시 정지
    if result.result_status in ('FAIL', 'WARNING'):
        raise SystemExit(
            f"Stage 2 정확도 {accuracy:.4f} {result.result_status} "
            f"(임계 ≥ 0.90, 마스터 §3.4) — "
            f"마스터 §2.5: 데이터셋 truncate + 룰 수정 + 재실행 필요"
        )
    
    # PASS만 통과
    return result
```

### 4.3 sample 정확도 측정 함수 (`engine/sample_accuracy.py` 신규)

```python
# engine/sample_accuracy.py
def compute_sample_accuracy(sb, sample_articles=100, check_categories=None):
    """100 random article의 stage_2_elements sub_type 정확도 측정.
    
    각 sub_type 별로 룰 패턴 정합성 검증 (PM 진단 정합 정규식 활용).
    """
    # 1. random sample 추출
    # 2. 각 row의 sub_type vs source_text 종결 패턴 검증
    # 3. TP / FP / WEAK / UC 카테고리화
    # 4. 정확도 = TP / (TP + FP + WEAK)
    # 반환: (accuracy: float, sample_size: int)
```

**카테고리 검증 룰** (PM 진단 정합):

```python
CATEGORY_VERIFICATION_PATTERNS = {
    'OBLIGATION_HEADER': r'(?:하여야|해야|어야|여야)\s*한다\.?$|의무가\s*있다\.?$',
    'AUTHORITY_HEADER': r'(?:할\s*수|ᆯ\s*수)\s*있다\.?$',
    'PROHIBITION_HEADER': r'(?:할\s*수\s*없다|아니\s*된다|금지\s*한다|못한다|안\s*된다)\.?$',
    'PENALTY_HEADER': r'(?:처한다|과한다|부과한다)\.?$',
    'EXEMPTION_HEADER': r'(?:아니한다|제외한다)\.?$',
    'DEFINITION_HEADER': r'(?:말한다|이라\s*한다|고시한다)\.?$',
    'DELEGATION_ACTIVE': r'으로\s*정한다\.?$',
    'AS_본다': r'으로\s*본다\.?$',  # ★ TAIL3만 정합 (보조 룰 폐기)
    'OBLIGATION_DETAIL_ITEM': r'할\s*것\.?$',
    'PENALTY_VIOLATOR_ITEM': r'(?:한|는)\s*자',
    'ENUMERATION_LIST_INTRO': r'다음\s*(?:각\s*호와|과)\s*같다\.?$',
    'REFERENCE_TO_ATTACHMENT': r'(?:별표|별지)\s*제?\s*\d+',
    'REFERENCE_INVOCATION': r'준용한다\.?$',
    'ENUMERATION_ITEM': r'',  # 명사 종결 (별도 검증 — 길이 + parent context)
    # Phase 1 단편: source_text 패턴 검증
    'DELETED': r'^삭제',
    'EXCEPTION_CLAUSE': r'^다만',
    # ...
}
```

### 4.4 단위 테스트 (`tests/test_validator_integration.py` 신규)

```python
def test_validator_pass_path():
    """Stage 2 정확도 0.95 → PASS."""
    result = Validator.evaluate_sample_accuracy(stage=2, accuracy=0.95, sample_size=100)
    assert result.result_status == 'PASS'

def test_validator_warning_path():
    """Stage 2 정확도 0.87 → WARNING."""
    result = Validator.evaluate_sample_accuracy(stage=2, accuracy=0.87, sample_size=100)
    assert result.result_status == 'WARNING'

def test_validator_fail_path():
    """Stage 2 정확도 0.80 → FAIL."""
    result = Validator.evaluate_sample_accuracy(stage=2, accuracy=0.80, sample_size=100)
    assert result.result_status == 'FAIL'

def test_phase_22_run_systemexit_on_fail():
    """run_phase_22가 FAIL 시 SystemExit raise."""
    # mock 정확도 0.80 → SystemExit 검증
    with pytest.raises(SystemExit):
        run_phase_22(mock_accuracy=0.80)
```

### 4.5 검증 임계

| check | 임계 | status |
|---|---|---|
| compute_sample_accuracy 단위 테스트 | sample 카테고리화 정확 | PASS 필수 |
| validator.py 통합 패턴 단위 테스트 | PASS/WARNING/FAIL 3단계 정합 | PASS 필수 |
| run_phase_22 FAIL 시 SystemExit | raise 검증 | PASS 필수 |
| coverage | ≥ 80% | PASS 필수 |

### 4.6 Phase 2.2-B PASS 미달 시

→ **즉시 정지 + PM 회신**. Phase 2.2-C 진입 금지.

---

## 5. Phase 2.2-C — 데이터셋 처리 (수정·검증된 엔진으로)

### 5.1 본 단계의 본질

**Phase 2.2-A + 2.2-B PASS 확정 후에만 진입**. 본 PM 결정 옵션 A (데이터셋 폐기) 정합.

### 5.2 작업 흐름

```
[1] 백업 (rule_classify_subtype + stage_2_elements)
   ↓
[2] DB CHECK enum 확장 (28 enum)
   ↓
[3] 룰 DB 적용
   3a. UPDATE: AS_본다 보조 룰 3종 비활성
   3b. UPDATE: OBLIGATION_DETAIL_GWAN_SAHANG sub_type → ENUMERATION_ITEM
   3c. UPDATE: WEAK_JUNYONG_HADA → REFERENCE_INVOCATION (또는 비활성 + 신규 룰로 대체)
   3d. INSERT: 신규 룰 12+개 (Phase 2.2-A에서 단위 검증 완료)
   ↓
[4] Phase 2.1 분류 폐기 (Phase 1 보전, ~75,318 row → UC)
   ↓
[5] Phase 2 재실행 (수정 엔진으로, --phase22)
   ↓
[6] 검증엔진 통합 실행 (validator.py)
   - Stage 2 sample 정확도 ≥ 90% → PASS
   - PASS 미달 → SystemExit + 사용자 회신
   ↓
[7] 보고서 + commit + push
```

### 5.3 SQL 시안 (Phase 2.2-A에서 단위 검증 완료한 룰만 INSERT)

#### 5.3.1 백업

```sql
CREATE TABLE rule_classify_subtype_backup_20260510_pre_phase2_2 AS 
  SELECT * FROM rule_classify_subtype;
CREATE TABLE stage_2_elements_backup_20260510_pre_phase2_2 AS 
  SELECT * FROM stage_2_elements;
```

#### 5.3.2 DB CHECK enum 확장

```sql
ALTER TABLE stage_2_elements DROP CONSTRAINT stage_2_elements_sub_type_check;
ALTER TABLE rule_classify_subtype DROP CONSTRAINT rule_classify_subtype_sub_type_check;

-- 28 enum (기존 25 + 신규 3)
ALTER TABLE stage_2_elements ADD CONSTRAINT stage_2_elements_sub_type_check
CHECK (sub_type = ANY (ARRAY[
  'OBLIGATION_HEADER', 'PROHIBITION_HEADER', 'PENALTY_HEADER', 'AUTHORITY_HEADER',
  'EXEMPTION_HEADER', 'DEFINITION_HEADER', 'DELEGATION_ACTIVE', 'AS_본다',
  'OBLIGATION_DETAIL_ITEM', 'PENALTY_VIOLATOR_ITEM', 'AUTHORITY_TARGET_ITEM',
  'EXEMPTION_TARGET_ITEM', 'DEFINITION_TARGET_ITEM', 'PROHIBITION_TARGET_ITEM',
  'DELETED', 'DEFINITION_INTRO', 'TITLE_HEADER', 'DATE_EFFECTIVE',
  'PARSE_FRAGMENT', 'DELEGATED_WAIVER', 'ENUMERATION_ITEM', 'EXCEPTION_CLAUSE',
  'WEAK_한다단순', 'WEAK_있다단순', 'UNCLASSIFIED',
  'ENUMERATION_LIST_INTRO', 'REFERENCE_TO_ATTACHMENT', 'REFERENCE_INVOCATION'
]));
-- rule_classify_subtype도 동일
```

#### 5.3.3 룰 DB 적용 (UPDATE + INSERT)

```sql
-- AS_본다 보조 룰 3종 비활성
UPDATE rule_classify_subtype 
SET enabled = false, 
    description = description || ' [DEPRECATED Phase 2.2 — FP 100%, ENUMERATION/REFERENCE 본질]',
    updated_at = NOW()
WHERE rule_name IN ('AS_본다_WA_GATDA', 'AS_본다_GWA_GATDA', 'AS_본다_TTOHAN_GATDA');

-- OBLIGATION_DETAIL_GWAN_SAHANG sub_type 변경
UPDATE rule_classify_subtype
SET sub_type = 'ENUMERATION_ITEM',
    description = '관한 사항 종결 — enumeration 항목',
    updated_at = NOW()
WHERE rule_name = 'OBLIGATION_DETAIL_GWAN_SAHANG';

-- WEAK_JUNYONG_HADA sub_type 변경
UPDATE rule_classify_subtype
SET sub_type = 'REFERENCE_INVOCATION',
    description = '준용한다 — REFERENCE_INVOCATION 본질 매핑',
    updated_at = NOW()
WHERE rule_name = 'WEAK_JUNYONG_HADA';

-- 신규 룰 12+개 INSERT (Phase 2.2-A 단위 검증 완료 후)
INSERT INTO rule_classify_subtype (...) VALUES (...);
```

#### 5.3.4 Phase 2.1 분류 폐기 (Phase 1 보전)

```sql
UPDATE stage_2_elements
SET sub_type = 'UNCLASSIFIED',
    confidence_score = 0,
    applied_rules = jsonb_build_object(
      'phase', 'phase_2_2_reset',
      'reason', '마스터 §2.5 — Phase 2.1 분류 데이터셋 단위 폐기',
      'previous_subtype', sub_type
    ),
    updated_at = NOW()
WHERE sub_type NOT IN ('DELETED', 'EXCEPTION_CLAUSE', 'DEFINITION_INTRO', 'TITLE_HEADER', 'DATE_EFFECTIVE')
  AND sub_type != 'UNCLASSIFIED';
-- 영향: ~75,318 row → UC (143,448 UC + 8,303 Phase 1 보전 = 151,751)
```

### 5.4 Phase 2 재실행 (수정 엔진으로)

```bash
railway run python3 scripts/track_e_phase2_run.py --phase22
# 내부:
# 1. UC 143,448 대상 룰 매칭
# 2. Phase 2 룰 적용 (수정 + 신규)
# 3. validator.py 통합 실행 (raise SystemExit on FAIL/WARNING)
# 4. verification_log INSERT
```

### 5.5 검증엔진 PASS 임계 (마스터 §3.4 + validator.py 정합)

| check | 임계 | 미달 시 |
|---|---|---|
| **Stage 2 sample 정확도 (100조문)** | **≥ 90%** (validator.py) | **SystemExit + Phase 2.2-A 회귀** |
| 분류율 | ≥ 70% (1차) | INFO |
| AS_본다 (TAIL3만) | ≤ 1,000 | WARNING |
| ENUMERATION_ITEM | ≥ 50,000 | WARNING |
| Phase 1 보전 (5종 row 수) | 동일 | FAIL |
| 0건 매칭 룰 | ≤ 2 | INFO |

### 5.6 Phase 2.2-C PASS 미달 시

→ **마스터 §2.5 정합 — Phase 2.2-A로 회귀** (Phase 2.2-C 데이터 폐기 + Phase 2.2-A 룰 정정 + 재진행).

---

## 6. 임의판단 절대 금지

| 영역 | 금지 | 허용 |
|---|---|---|
| LLM 호출 | 어떤 형태든 X | Kiwi + 정규식 + DB 빈도 |
| 본 명세 외 신규 sub_type | 본 명세 3개 외 추가 X | ENUMERATION_LIST_INTRO + REFERENCE_TO_ATTACHMENT + REFERENCE_INVOCATION만 |
| validator.py 본문 수정 | **절대 X** | 활용 패턴만 작성 |
| 임계 자의 변경 | ≥ 90% 위반 | 마스터 §3.4 정합만 |
| Phase 1 결과 변경 | 절대 X | 100% 보전 |
| 단계별 PASS 미달 시 다음 단계 | **절대 X** | PM 회신 후 정정 |
| 룰 단위 검증 미실행 | 절대 X | 신규 룰 12+개 모두 sample 100건 검증 |
| 검증엔진 미통합 | 절대 X | validator.py 통합 강제 |

---

## 7. 중단 트리거 (즉시 정지 + PM 회신)

1. 진입 점검 SQL 결과 명세와 다름
2. validator.py 본문 변경 발견
3. Phase 2.2-A 단위 테스트 룰별 < 95% (룰 정정 필요)
4. Phase 2.2-B 통합 단위 테스트 FAIL
5. Phase 2.2-C 백업 row 수 ≠ 본체
6. CHECK enum 마이그레이션 실패
7. row 수 변동 (151,751 ≠)
8. Phase 1 분류 row 변경 발견
9. Phase 2.2-C 검증엔진 FAIL/WARNING (≥ 90% 미달)

---

## 8. 본 명세 외 작업 절대 X

- ❌ Stage 3 진입 (별도 작업, v3.0 마스터 결정 후)
- ❌ v3.0 마스터 객체 테이블 마이그레이션
- ❌ Tier 2-4 본법 수집 (Track B 별도)
- ❌ Track C v1.3 dict 보강 (별도)
- ❌ Kiwi 사전 보강
- ❌ 6하원칙 보강 (별도 명세)
- ❌ 신규 sub_type 추가 (본 명세 3개 외)
- ❌ Phase 1 결과 변경
- ❌ validator.py 본문 수정

---

## 9. 보고서 양식 (`Track_E_20260510_Phase2_2.md`)

```markdown
# [Track E] Phase 2.2 — 엔진 우선 수정 + 검증엔진 통합 + 데이터셋 처리

## 1. Phase 2.2-A 결과
### 1.1 subtype_rule_match.py 보강
### 1.2 신규 룰 12개 단위 테스트 정확도 (룰별 ≥ 95% 검증)
### 1.3 PASS 확정 / 미달 시 회귀

## 2. Phase 2.2-B 결과
### 2.1 validator.py 통합 패턴
### 2.2 통합 단위 테스트
### 2.3 PASS 확정

## 3. Phase 2.2-C 결과
### 3.1 백업
### 3.2 CHECK enum 확장 (28 enum)
### 3.3 룰 DB 적용 (UPDATE + INSERT)
### 3.4 Phase 2.1 분류 폐기 (75,318 row → UC)
### 3.5 Phase 2 재실행 결과 — sub_type 분포

| sub_type | Phase 2.1 | Phase 2.2 | 변화 |
|---|---|---|---|
| AS_본다 | 4,188 | ___ | -___ |
| OBLIGATION_DETAIL_ITEM | 6,748 | ___ | -___ |
| ENUMERATION_ITEM | 0 | ___ | +___ |
| ENUMERATION_LIST_INTRO | 0 | ___ | +___ |
| REFERENCE_TO_ATTACHMENT | 0 | ___ | +___ |
| REFERENCE_INVOCATION | 0 | ___ | +___ |
| UNCLASSIFIED | 68,130 | ___ | -___ |

### 3.6 검증엔진 결과
- `Validator.evaluate_sample_accuracy(stage=2, accuracy=___, sample_size=___)`
- result_status = `PASS / WARNING / FAIL`
- verification_log INSERT 1 row

## 4. 절대 원칙 점검 (마스터 §2)
## 5. 다음 단계 권고
```

---

## 10. 환경 정보

| 항목 | 값 |
|---|---|
| 코드 base | `taiengineering/tai-api` 브랜치 `dev` |
| 보강 파일 | `engine/subtype_rule_match.py`, `scripts/track_e_phase2_run.py` |
| 신규 파일 | `engine/sample_accuracy.py`, `tests/test_phase_22_rules.py`, `tests/test_validator_integration.py` |
| 변경 절대 X | `engine/validator.py` |
| 마이그레이션 | `apply_migration` (name: `phase_2_2_subtype_enum_extension`) |
| 보고서 commit | `taiengineering/tai-admin` main, `docs/extraction/v3/log/Track_E_20260510_Phase2_2.md` |
| 코드 commit | `taiengineering/tai-api` dev |

---

**END — 엔진 우선 수정 → 검증엔진 통합 → 데이터셋 처리 (사용자 본질 지적 정합).**
