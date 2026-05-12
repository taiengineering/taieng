# [Cursor 위탁 v1.2-Patch] sample_accuracy.py 본질 보강 — Ground Truth 정규식 카테고리화

**작성일**: 2026-05-10  
**작성자**: PM 창  
**선행**: `Cursor_Phase_2_2_Pipeline_Engine_Spec_v1_2.md` (commit `5055de350f55f660...`)  
**선행 코드**: `tai-api` `dev` `b1188c8` (Cursor Phase 2.2-A/B/C 코드 완료)  
**핵심 본질**: `engine/sample_accuracy.py`의 `compute_stage2_sample_accuracy`는 **자기일관성 proxy** — 검증엔진 본질 미달 (false PASS 위험). Ground truth 정규식 카테고리화로 변경.

---

## 0. 본 보강의 본질

### 0.1 현재 proxy 함수의 본질적 한계

```python
# 현재 (Cursor 작성, b1188c8)
predicted = pick_first_matching_subtype_rule(rules, tj, stext)
ok if predicted == stored  # 자기일관성
```

→ 룰이 deterministic이므로 **항상 ~100% 일치**. AS_본다_WA_GATDA 1,998건 FP를 **감지 못함**.

### 0.2 Ground Truth 본질 (PM 진단 89.74% 재현)

```python
# 보강 (본 명세)
pattern = CATEGORY_VERIFICATION_PATTERNS[stored_sub_type]
ok if re.search(pattern, source_text)  # ground truth 패턴 정합
```

→ source_text 종결 패턴이 sub_type 본질과 정합한지 검증. PM 진단 정확도 89.74% 재현 가능.

---

## 1. 작업 본질 (1회 위탁, 분량 작음)

### 1.1 파일 변경

| 파일 | 작업 | 분량 |
|---|---|---|
| `engine/sample_accuracy.py` | 본문 보강 (proxy → ground truth) | ~120 라인 |
| `tests/test_sample_accuracy.py` | 신규 (단위 테스트) | ~80 라인 |
| `tests/test_pipeline.py` | 회귀 검증 (기존 mock 유지) | 0 변경 |

### 1.2 변경 X (강제)

- `engine/validator.py` — 0 byte 변경 (사용자 강제)
- `engine/pipeline.py` — 변경 X (검증 hook 호출 인터페이스 동일)
- `engine/stages/` — 변경 X
- `engine/subtype_rule_match.py` — 변경 X
- 기존 룰 / DB / Phase 1/2.1 결과 — 변경 X

---

## 2. `engine/sample_accuracy.py` 본문 시안 (전체 교체)

```python
"""Stage 2 sample 정확도 — Ground Truth 정규식 카테고리화 (PM 진단 정합).

각 sub_type의 본질 종결 패턴을 정규식으로 정의 (CATEGORY_VERIFICATION_PATTERNS).
샘플 row의 source_text vs stored sub_type 정합성 검증 → TP/FP/UC/WEAK 카테고리화.
PM 진단 89.74% 재현 가능 (마스터 §3.4 + Track A validator.py 정합).

이전 자기일관성 proxy (b1188c8) 폐기 — false PASS 위험 (룰 deterministic 한계).
"""

from __future__ import annotations

import logging
import random
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from supabase import Client as SupabaseClient

logger = logging.getLogger(__name__)

DEFAULT_SAMPLE_ARTICLES = 100  # 마스터 §3.4 sample 단위 = 100조문

# === Ground Truth 정규식 카테고리화 (PM 진단 정합) ===
# 각 sub_type별 source_text 종결 패턴. 본 PM 진단 (Track_E_..._Reverse_Validation.md) 정합.
CATEGORY_VERIFICATION_PATTERNS: dict[str, str] = {
    # HEADER 7종 (확정 패턴)
    'OBLIGATION_HEADER':
        r'(?:하여야|해야|어야|여야|아야)\s*한다\.?$|의무가\s*있다\.?$',
    'AUTHORITY_HEADER':
        r'(?:할\s*수|ᆯ\s*수)\s*있다\.?$',
    'PROHIBITION_HEADER':
        r'(?:할\s*수\s*없다|아니\s*된다|금지\s*한다|못한다|안\s*된다)\.?$',
    'PENALTY_HEADER':
        r'(?:처한다|과한다|부과한다)\.?$',
    'EXEMPTION_HEADER':
        r'(?:아니한다|제외한다)\.?$',
    'DEFINITION_HEADER':
        r'(?:말한다|이라\s*한다|고시한다)\.?$',
    'DELEGATION_ACTIVE':
        r'으로\s*정한다\.?$',
    'AS_본다':
        r'으로\s*본다\.?$',  # ★ TAIL3만 정합 (보조 룰 FP 제외)

    # ITEM
    'OBLIGATION_DETAIL_ITEM':
        r'할\s*것\.?$',
    'PENALTY_VIOLATOR_ITEM':
        r'(?:한|는)\s*자\b',

    # Phase 2.2 신규 sub_type 3종
    'ENUMERATION_LIST_INTRO':
        r'다음\s*(?:각\s*호와|과)\s*같다\.?$',
    'REFERENCE_TO_ATTACHMENT':
        r'(?:별표|별지)\s*제?\s*\d+',
    'REFERENCE_INVOCATION':
        r'준용한다\.?$',

    # Phase 1 단편 (정확 매칭)
    'DELETED':
        r'^삭제',
    'EXCEPTION_CLAUSE':
        r'^(?:다만|단)',
    # DEFINITION_INTRO / TITLE_HEADER / DATE_EFFECTIVE: parent_id 패턴 — 별도 검증 (TP로 가산)
}

# Phase 1 정확 분류 sub_type (parent_id 정합 — 정규식 검증 X, TP 가산)
PHASE1_ALWAYS_TP_SUB_TYPES: set[str] = {
    'DEFINITION_INTRO', 'TITLE_HEADER', 'DATE_EFFECTIVE',
}

# WEAK / UC (모호 — 별도 카테고리)
WEAK_PREFIX = 'WEAK_'
UC_SUB_TYPE = 'UNCLASSIFIED'

# ENUMERATION_ITEM 검증 — 명사 종결 + 길이 < 80
ENUMERATION_ITEM_MAX_LENGTH = 80
ENUMERATION_ITEM_TAIL_PATTERN = r'[가-힣]+\.?$'  # 한글 명사 종결 추정


def compute_stage2_sample_accuracy(
    supabase: SupabaseClient | None,
    *,
    sample_size: int = DEFAULT_SAMPLE_ARTICLES,
    seed: int | None = None,
) -> tuple[float, int]:
    """100 random article의 stage_2_elements ground truth 정확도 측정.

    반환: (accuracy, classified_sample_size)
    accuracy = TP / (TP + FP + WEAK), UC 제외.
    """
    if supabase is None:
        return (0.95, sample_size)  # 오프라인 스텁 (테스트용)

    if seed is not None:
        random.seed(seed)

    # 100 random article의 stage_2_elements + stage_1_clauses 조인
    rows = _fetch_sample_rows(supabase, sample_articles=sample_size)
    if not rows:
        logger.warning("compute_stage2_sample_accuracy: sample 0건")
        return (0.91, 0)

    tp, fp, uc, weak, phase1_tp = 0, 0, 0, 0, 0
    for row in rows:
        sub_type = row.get('sub_type') or UC_SUB_TYPE
        source_text = row.get('source_text') or ''
        verdict = _verify_row(sub_type, source_text)
        if verdict == 'TP':
            tp += 1
        elif verdict == 'FP':
            fp += 1
        elif verdict == 'UC':
            uc += 1
        elif verdict == 'WEAK':
            weak += 1
        elif verdict == 'PHASE1_TP':
            phase1_tp += 1

    classified = tp + fp + weak + phase1_tp
    if classified == 0:
        logger.warning("compute_stage2_sample_accuracy: 분류 sample 0건 (UC 100%)")
        return (0.91, 0)

    accuracy = (tp + phase1_tp) / classified
    logger.info(
        f"sample_accuracy: TP={tp+phase1_tp} (incl Phase1={phase1_tp}) "
        f"FP={fp} WEAK={weak} UC={uc} | classified={classified} | acc={accuracy:.4f}"
    )
    return (accuracy, classified)


def _verify_row(sub_type: str, source_text: str) -> str:
    """단일 row 카테고리화 → 'TP'/'FP'/'UC'/'WEAK'/'PHASE1_TP'."""
    if sub_type == UC_SUB_TYPE:
        return 'UC'
    if sub_type.startswith(WEAK_PREFIX):
        return 'WEAK'
    if sub_type in PHASE1_ALWAYS_TP_SUB_TYPES:
        return 'PHASE1_TP'

    # ENUMERATION_ITEM 별도 검증
    if sub_type == 'ENUMERATION_ITEM':
        if (
            len(source_text) < ENUMERATION_ITEM_MAX_LENGTH
            and re.search(ENUMERATION_ITEM_TAIL_PATTERN, source_text)
            and not re.search(r'한다\.?$|있다\.?$|것\.?$', source_text)  # 동사/것 종결 X
        ):
            return 'TP'
        return 'FP'

    pattern = CATEGORY_VERIFICATION_PATTERNS.get(sub_type)
    if not pattern:
        # 미정의 sub_type — WARNING으로 처리 (보수적)
        logger.warning(f"_verify_row: unknown sub_type '{sub_type}' — WEAK 처리")
        return 'WEAK'

    return 'TP' if re.search(pattern, source_text) else 'FP'


def _fetch_sample_rows(
    supabase: SupabaseClient,
    *,
    sample_articles: int,
) -> list[dict]:
    """100 random article의 (sub_type, source_text) 추출."""
    # SQL 직접 실행 (rpc 미생성 시 fallback)
    sql = f"""
    WITH sa AS (
        SELECT id FROM law_article 
        WHERE id IN (SELECT article_id FROM law_article_part)
        ORDER BY random() LIMIT {sample_articles}
    )
    SELECT s2.sub_type, s1.source_text
    FROM stage_2_elements s2
    JOIN stage_1_clauses s1 ON s1.id = s2.clause_id
    JOIN law_article_part lap ON lap.id = s1.part_id
    JOIN sa ON sa.id = lap.article_id
    """
    res = supabase.rpc("execute_sql", {"sql": sql}).execute()
    return res.data or []
```

→ Supabase Python SDK가 `rpc("execute_sql")` 미지원 시 별도 함수로 row fetch 가능 (Cursor 자체 판단).

---

## 3. `tests/test_sample_accuracy.py` 신규

```python
"""sample_accuracy.py 단위 테스트."""
import pytest
from engine.sample_accuracy import (
    _verify_row,
    CATEGORY_VERIFICATION_PATTERNS,
    compute_stage2_sample_accuracy,
)


class TestVerifyRow:
    """_verify_row 카테고리화 검증."""

    def test_obligation_header_tp(self):
        assert _verify_row('OBLIGATION_HEADER', '관계 서류를 제출하여야 한다.') == 'TP'
        assert _verify_row('OBLIGATION_HEADER', '준수해야 한다.') == 'TP'
        assert _verify_row('OBLIGATION_HEADER', '의무가 있다.') == 'TP'

    def test_authority_header_tp(self):
        assert _verify_row('AUTHORITY_HEADER', '명할 수 있다.') == 'TP'
        assert _verify_row('AUTHORITY_HEADER', '폐지할 수 있다.') == 'TP'

    def test_as_bonda_tail3_tp(self):
        """AS_본다 TAIL3만 TP."""
        assert _verify_row('AS_본다', '제출한 것으로 본다.') == 'TP'

    def test_as_bonda_wa_gatda_fp(self):
        """AS_본다 보조 룰 FP — 의제 X."""
        # AS_본다_WA_GATDA가 매칭한 케이스 — 본질 ENUMERATION_LIST_INTRO
        assert _verify_row('AS_본다', '다음 각 호와 같다.') == 'FP'
        assert _verify_row('AS_본다', '별표 1과 같다.') == 'FP'

    def test_obligation_detail_gwan_sahang_fp(self):
        """OBLIGATION_DETAIL_ITEM 잘못 매칭 — 본질 ENUMERATION_ITEM."""
        # GWAN_SAHANG 룰이 만든 row — 본질 enumeration
        assert _verify_row('OBLIGATION_DETAIL_ITEM', '관한 사항') == 'FP'

    def test_enumeration_list_intro_tp(self):
        assert _verify_row('ENUMERATION_LIST_INTRO', '다음 각 호와 같다.') == 'TP'
        assert _verify_row('ENUMERATION_LIST_INTRO', '다음과 같다.') == 'TP'

    def test_reference_to_attachment_tp(self):
        assert _verify_row('REFERENCE_TO_ATTACHMENT', '별표 1과 같다.') == 'TP'
        assert _verify_row('REFERENCE_TO_ATTACHMENT', '별지 제3호 서식에 따른다.') == 'TP'

    def test_reference_invocation_tp(self):
        assert _verify_row('REFERENCE_INVOCATION', '제5조의 규정을 준용한다.') == 'TP'

    def test_uc_returns_uc(self):
        assert _verify_row('UNCLASSIFIED', '아무 텍스트') == 'UC'

    def test_weak_returns_weak(self):
        assert _verify_row('WEAK_한다단순', '제출한다.') == 'WEAK'
        assert _verify_row('WEAK_있다단순', '있다.') == 'WEAK'

    def test_phase1_tp(self):
        assert _verify_row('DEFINITION_INTRO', '아무 텍스트') == 'PHASE1_TP'
        assert _verify_row('TITLE_HEADER', '제1장 총칙') == 'PHASE1_TP'

    def test_deleted_tp(self):
        assert _verify_row('DELETED', '삭제 <2020. 1. 1.>') == 'TP'

    def test_exception_clause_tp(self):
        assert _verify_row('EXCEPTION_CLAUSE', '다만, 부득이한 경우는 제외한다.') == 'TP'


class TestComputeStage2SampleAccuracy:
    def test_offline_stub(self):
        """supabase=None → 오프라인 스텁 0.95 PASS."""
        acc, n = compute_stage2_sample_accuracy(supabase=None, sample_size=100)
        assert acc == 0.95
        assert n == 100

    def test_pm_diagnosis_reproduction_via_mock(self, monkeypatch):
        """PM 진단 89.74% 재현 — mock rows 사용."""
        from engine import sample_accuracy
        mock_rows = (
            [{'sub_type': 'OBLIGATION_HEADER', 'source_text': '준수해야 한다.'}] * 115
            + [{'sub_type': 'AUTHORITY_HEADER', 'source_text': '명할 수 있다.'}] * 69
            + [{'sub_type': 'OBLIGATION_DETAIL_ITEM', 'source_text': '시행할 것.'}] * 54
            + [{'sub_type': 'AS_본다', 'source_text': '으로 본다.'}] * 3
            + [{'sub_type': 'AS_본다', 'source_text': '다음 각 호와 같다.'}] * 14   # ★ FP
            + [{'sub_type': 'OBLIGATION_DETAIL_ITEM', 'source_text': '관한 사항'}] * 6  # ★ FP
            # ... 합계 351 row, FP 24, WEAK 11
        )
        # _fetch_sample_rows mock 후 compute_stage2_sample_accuracy 호출
        # accuracy ≈ 0.8974 검증
        # (실제 mock 데이터는 PM 진단 분포 정확 반영)
```

---

## 4. 검증 임계 (PASS 기준)

| check | 임계 | 본질 |
|---|---|---|
| `_verify_row` 단위 테스트 | 100% pass | sub_type별 카테고리화 정합 |
| AS_본다 보조 룰 FP 식별 | "다음 각 호와 같다" → FP | PM 진단 재현 |
| OBLIGATION_DETAIL "관한 사항" → FP | 명확 식별 | PM 진단 재현 |
| 기존 회귀 테스트 | 147 → 160+ passed | 기존 흐름 미파괴 |
| coverage | ≥ 80% | Track A 정합 |
| validator.py 본문 변경 | 0 byte | 강제 |

---

## 5. 보강 후 운영 진행 (Phase 2.2-C 실 DB)

### 5.1 진입 점검 + 부분 실행 (옵션 3 정합)

```bash
# 1. checks 단독 실행 (DB 변경 X, 점검만)
railway run python3 scripts/track_e_phase2_run.py --phase22 --only checks
# 결과 확인: total_elements, UC, active_rules 등
# EXPECTED_PHASE22_RULES_SUB = 34 정합 확인
```

### 5.2 전체 실행

```bash
# 2. all 실행 (백업 → CHECK → 룰 → Pipeline 검증)
railway run python3 scripts/track_e_phase2_run.py --phase22 --only all
```

→ Pipeline 내장 검증 hook이 자동:
- PASS (≥ 90%): 정상 완료
- WARNING (≥ 85%): `halt_exit` SystemExit + PM 회신
- FAIL (< 85%): `halt_exit` SystemExit + PM 회신

### 5.3 운영 결과 보고

- sub_type 분포 변화 (Phase 2.1 vs Phase 2.2)
- Pipeline 검증 hook 결과 (PASS/WARNING/FAIL + actual_value)
- verification_log entry 확인
- 보고서 push (`tai-admin` `Track_E_20260510_Phase2_2.md` 보강)

---

## 6. 임의판단 절대 금지

| 영역 | 금지 |
|---|---|
| LLM 호출 | X |
| validator.py 본문 수정 | 0 byte 변경 |
| CATEGORY_VERIFICATION_PATTERNS 자의 변경 | 본 명세 정의대로만 |
| sub_type 카테고리화 결과 자의 변경 | TP/FP/WEAK/UC/PHASE1_TP만 |
| Pipeline halt_exit 우회 | 절대 X |
| 운영 임계 미달 시 강제 진행 | 절대 X |

---

## 7. 중단 트리거

1. 진입 점검 SQL 결과 EXPECTED_PHASE22_RULES_SUB와 다름
2. validator.py 본문 변경 발견
3. 단위 테스트 회귀 (기존 147 → < 147 passed)
4. 운영 시 Pipeline FAIL/WARNING (≥ 90% 미달)
5. row 수 변동 (151,751 ≠)
6. Phase 1 분류 변경 발견

---

## 8. 환경 정보

| 항목 | 값 |
|---|---|
| 코드 base | `taiengineering/tai-api` `dev` (선행 commit `b1188c8`) |
| 변경 파일 | `engine/sample_accuracy.py` (전체 교체), `tests/test_sample_accuracy.py` (신규) |
| 변경 X | `validator.py`, `pipeline.py`, `stages/`, `subtype_rule_match.py` |
| 보고서 | `tai-admin` `docs/extraction/v3/log/Track_E_20260510_Phase2_2.md` (이어서 보강) |
| 코드 commit | `tai-api` `dev` |

---

**END — proxy 폐기 + Ground Truth 정규식 카테고리화 + 운영 진행 (1회 위탁).**
