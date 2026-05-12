# [Cursor 위탁 v4.0] Phase 2.2 v4.0 — 정순 + 역순 본질 통합 (METHODOLOGY 정합)

**작성일**: 2026-05-10
**작성자**: PM 창
**위탁 대상**: Cursor (TAI Backend / Railway)
**선행 base**: `tai-api` `dev` `90c994c` (PASS_STABLE 정합)
**본 명세 정정 (v4.0 본질 격상)**: 사용자 본질 지적 — "역순 검증은??" → 회귀 hook 수준 X, **본 운영의 핵심 본질로 격상**.

---

## 0. 본 v4.0의 본질

### 0.1 v3.0 운영 결과 본질 결함

본 PM 자체 진단 (DB 직접 점검):
- 격리 10,214 row 중 **FP_OTHER 3,341건 (32.71%)** sub_type 분포:
  - **OBLIGATION_HEADER 2,027** (60.67%) — **본질적 TP 의무 헤더**
  - DEFINITION_HEADER 490 / AUTHORITY_HEADER 453 / EXEMPTION_HEADER 371

OBLIGATION_HEADER 10개 random sample 본 PM 검증 — **10/10 모두 본질적 TP**:
- "...따라야 한다" / "...내줘야 한다" / "...커야한다" / "...지켜야 한다" / "...내야 한다"

→ **`_verify_row` CATEGORY_VERIFICATION_PATTERNS 좁아 본질적 TP를 FP로 잘못 분류**.

### 0.2 사용자 본질 결정 (2건)

> **결정 1**: "몰입 중지. 역순 검증을 탑재하여, 처음부터 다시 가동. 그리고 지금 발생한 것도 함께 적용."
>
> **결정 2 (본 정정)**: "역순 검증은??" → 본 PM 명세에 역순 검증이 회귀 hook 수준 격하 = 본질 미달.

→ 본 v4.0 정정:
1. `_verify_row` 본질 보강 (CATEGORY_VERIFICATION_PATTERNS 다양성 정합)
2. **역순 검증 = 본 운영 핵심 본질로 격상** (정순 + 역순 둘 다 PASS만 진정 PASS)
3. DB 격리 복원 (PM 자체 진행 완료)
4. 처음부터 재가동

### 0.3 METHODOLOGY 본질 정합 (5월 4일 9단계)

```
[METHODOLOGY 본질]
정순 (article → drafts) + 역순 (drafts → article, 환각 방지)
둘 다 통과해야 PASS

[본 운영 적용 본질]
정순: source_text → sub_type 분류 정확 (sample_accuracy ≥ 0.9)
역순: sub_type → source_text 본질 정합 (sub_type별 정확도 ≥ 0.7)
둘 다 PASS만 진정한 PASS
```

### 0.4 PM 자체 진행 완료

- ✅ DB 격리 복원: `phase_2_2_v4_revert_isolation_for_reverse_verification` (10,214 → 0)
- ✅ stage_2_elements: 151,751 row 모두 not_isolated
- ✅ sub_type 분류 결과 보전 (Phase 2.1 결과 그대로)

---

## 1. 절대 원칙

| 원칙 | 본 명세 적용 |
|---|---|
| ① LLM X | 정규식 + DB 빈도만 |
| ② 법령 보전 | source_text 변경 X |
| ③ 누락 0건 | row 변동 X |
| ④ 100% 매핑 | 본질적 TP/FP 정확 분류 |
| ⑤ 오염 = 부분 폐기 | 본질적 FP만 격리 |
| ⑥ 검증 부담 0 | 자동 운영 |
| ⑦ Ground Truth 우선 | 보강된 `_verify_row` |
| ⑧ DB가 ground truth | DB 직접 조회 |

### 1.1 변경 X (강제)

| 영역 | 강제 |
|---|---|
| `engine/validator.py` 본문 | **0 byte (MD5 8,100 동일)** |
| `engine/pipeline.py` 본문 | 변동 X |
| `engine/stages/stage_2.py` | lazy init 보전 |
| `engine/morpheme.py` / `subtype_rule_match.py` | 변동 X |

### 1.2 변경 영역

| 영역 | 본질 |
|---|---|
| `engine/sample_accuracy.py` `_verify_row` | CATEGORY_VERIFICATION_PATTERNS 본질 확장 |
| `engine/sample_accuracy.py` 신규 | `compute_subtype_group_accuracy` (역순 검증 핵심) |
| `engine/iterator.py` `_process_single_law` | **역순 검증 본 운영 통합** (정순 + 역순 둘 다) |
| `engine/iterator.py` `_regression_check` | sub_type별 group sample 통합 |

---

## 2. v4.0 본질 — `_verify_row` CATEGORY_VERIFICATION_PATTERNS 보강

### 2.1 본질 결함 분석

```python
# 현재 (v3.0, 본질 미달)
'OBLIGATION_HEADER': r"하여야\s*한다\.?$"
# → "따라야 한다" / "내야 한다" / "커야한다" / "지켜야 한다" 등 매칭 X
```

### 2.2 v4.0 본질 보강

```python
# v4.0 — 의무 종결 본질 다양성 정합
CATEGORY_VERIFICATION_PATTERNS = {
    'OBLIGATION_HEADER': r"[가-힣]{1,5}(어|아|여|야)\s*한다\.?$|[가-힣]+해야\s*한다\.?$",
    # 매칭: 하여야/해야/따라야/내야/지켜야/보내야/커야/되어야/있어야/갖춰야 한다 등

    'PROHIBITION_HEADER': r"(?:[가-힣]+지|[가-힣]+해서는|[가-힣]+할\s*수\s*없)\s*아니된다\.?$|할\s*수\s*없다\.?$|되지\s*아니한다\.?$|금지한다\.?$",

    'AUTHORITY_HEADER': r"[가-힣]{1,5}(할|을)\s*수\s*있다\.?$|권한이\s*있다\.?$|결정한다\.?$",

    'EXEMPTION_HEADER': r"[가-힣]+에서\s*제외(된다|한다)\.?$|적용(을\s*받지\s*아니한다|되지\s*아니한다)\.?$|면제(된다|한다)\.?$",

    'DEFINITION_HEADER': r"[가-힣]+(이|란)\s*[가-힣]+를?\s*말한다\.?$|[가-힣]+(이|란)\s*다음[과]?\s*같다\.?$|정의는\s*다음과\s*같다\.?$",

    'AS_본다': r"으로\s*본다\.?$|(이|로)\s*간주한다\.?$",
    # WA_GATDA / GWA_GATDA 등 보조 룰은 본 패턴 외 → FP 정합

    'REFERENCE_TO_ATTACHMENT': r"별표\s*\d*[과와]?\s*같다\.?$|별첨[과와]?\s*같다\.?$|별지[과와]?\s*같다\.?$",

    'DELEGATION_HEADER': r"위임한다\.?$|[가-힣]+령으로\s*정한다\.?$|[가-힣]+령에\s*따른다\.?$",

    'WEAK_한다단순': r"^(?!.*하여야|해야|따라야|내야|지켜야).*한다\.?$",
    'WEAK_있다단순': r"^(?!.*할\s*수).*있다\.?$",

    # Phase 1 5종 (보전, 변동 X)
    'DELETED': r".*",
    'EXCEPTION_CLAUSE': r".*",
    'DEFINITION_INTRO': r".*",
    'TITLE_HEADER': r".*",
    'DATE_EFFECTIVE': r".*",
}
```

### 2.3 Cursor 자체 검증 본질

```sql
-- v4.0 _verify_row 보강 후 본질 정합 검증
-- 각 sub_type별 random 50건 → source_text 직접 검토 → 본질적 TP가 새 패턴 매칭
SELECT sub_type, source_text 
FROM stage_2_elements s2 
JOIN stage_1_clauses s1 ON s1.id = s2.clause_id
WHERE sub_type IN ('OBLIGATION_HEADER', 'PROHIBITION_HEADER', 'AUTHORITY_HEADER', 
                   'EXEMPTION_HEADER', 'DEFINITION_HEADER', 'REFERENCE_TO_ATTACHMENT')
ORDER BY RANDOM() LIMIT 50;
```

→ Cursor가 50건 본문 직접 검토 + v4.0 패턴 매칭 정합 보장.

---

## 3. v4.0 본질 — 역순 검증 본 운영 핵심 통합 ★

### 3.1 본 정정의 핵심 본질

**v4.0 (이전 명세) 본질 미달**:
- 역순 검증 = `_regression_check`의 hook (10법령마다 1회)
- acc < 0.7 시 logger.warning만 (halt X)
- 매 법령 본질 X

**v4.0 (본 정정) 본질**:
- **역순 검증 = `_process_single_law`의 본 운영 핵심**
- 매 법령 PASS 후 = **반드시 역순 검증 수행**
- acc < 임계 → halt + 격리 + 다음 iteration
- **정순 + 역순 둘 다 PASS만 진정한 PASS**

### 3.2 신규 함수 (`engine/sample_accuracy.py`)

```python
def compute_subtype_group_accuracy(
    supabase,
    sub_type: str,
    *,
    law_id: Any | None = None,
    sample_size: int = 100,
    seed: int | None = None,
    exclude_isolated: bool = True,
) -> dict[str, Any]:
    """sub_type 그룹 random sample 정확도 (역순 검증 본질).

    예: compute_subtype_group_accuracy(sb, 'OBLIGATION_HEADER', law_id=X, sample_size=100)
        → 해당 법령의 OBLIGATION_HEADER N건 (또는 전체) 중 100건 random
        → _verify_row로 ground truth 카테고리화
        → {'sub_type': X, 'n': 100, 'tp': 95, 'fp': 5, 'accuracy': 0.95, 'population': N}

    law_id=None 시 전체 sub_type 정확도 (회귀 검증 hook).
    law_id 지정 시 해당 법령 내 sub_type 정확도 (매 법령 역순 검증 본질).
    """


def compute_law_reverse_verification(
    supabase,
    law_id: Any,
    *,
    threshold: float = 0.7,
    min_sample: int = 5,
) -> dict[str, Any]:
    """법령 단위 역순 검증 본질.

    해당 법령의 모든 sub_type별 정확도 측정.
    각 sub_type acc < threshold 시 FAIL.
    sub_type 내 row < min_sample 시 통계 건너뜀.

    Returns:
        {
            'law_id': X,
            'overall_pass': True/False,
            'subtype_results': [
                {'sub_type': 'OBLIGATION_HEADER', 'n': 50, 'accuracy': 0.95, 'pass': True},
                {'sub_type': 'AS_본다', 'n': 5, 'accuracy': 0.0, 'pass': False, 'failed_rows': [id1, id2, ...]},
                ...
            ],
            'failed_subtypes': ['AS_본다'],  # acc < threshold
        }
    """
    # SELECT DISTINCT sub_type FROM stage_2_elements WHERE law_id=X
    # 각 sub_type별 compute_subtype_group_accuracy 호출
    # 결과 집계 + 반환
```

### 3.3 Iterator `_process_single_law` 정정 본질 ★

```python
def _process_single_law(self, law_id, *, only_stages):
    """단일 법령 처리 — 정순 + 역순 본질 통합 (METHODOLOGY 정합)."""
    total_marked = 0
    prev_marked = -1
    
    for it in range(1, self.max_iterations_per_law + 1):
        iso_mode = it > 1
        excl = iso_mode
        try:
            # 1. 정순 검증 (Pipeline.run — 90c994c 보전)
            self.pipeline.run(
                input_data=None, only_stages=only_stages,
                law_id=law_id, isolation_mode=iso_mode, exclude_isolated=excl,
            )
            
            # ★ 2. 역순 검증 본질 (v4.0 신규)
            reverse_result = compute_law_reverse_verification(
                self.supabase, law_id, threshold=0.7, min_sample=5,
            )
            if not reverse_result['overall_pass']:
                # 역순 검증 FAIL — 격리 + 다음 iteration
                marked = self._isolate_failed_subtypes(law_id, reverse_result['failed_subtypes'])
                total_marked += marked
                logger.info(
                    "law_id=%s iteration=%s 역순 검증 FAIL — sub_types=%s 격리 %s건",
                    law_id, it, reverse_result['failed_subtypes'], marked,
                )
                # 안정 상태 본질 (90c994c 보전)
                if marked == 0 and total_marked == prev_marked:
                    return LawProcessRun(law_id, it, "PASS_STABLE", total_marked)
                prev_marked = total_marked
                continue
            
            # 정순 + 역순 둘 다 PASS → 진정한 PASS
            return LawProcessRun(law_id, it, "PASS", total_marked)
        
        except PipelineHaltError as e:
            # 정순 검증 FAIL — 90c994c 본질 보전
            chk = e.check
            marked = self._isolate_fp_rows(law_id, chk)
            total_marked += marked
            logger.info(
                "law_id=%s iteration=%s 정순 검증 %s — FP 격리 %s건",
                law_id, it, chk.result_status, marked,
            )
            if marked == 0 and total_marked == prev_marked:
                return LawProcessRun(law_id, it, "PASS_STABLE", total_marked)
            prev_marked = total_marked
    
    return LawProcessRun(law_id, self.max_iterations_per_law, "FAIL_HALT", total_marked)


def _isolate_failed_subtypes(self, law_id, failed_subtypes: list[str]) -> int:
    """역순 검증 FAIL sub_type의 본질적 FP row만 격리.
    
    각 failed sub_type의 row 중 _verify_row가 FP인 row만 마킹.
    isolation_reason은 sub_type 기반 (isolation_reason_for_fp_subtype 활용).
    """
    n = 0
    # SELECT id, sub_type, source_text WHERE law_id=X AND sub_type IN failed_subtypes
    # _verify_row가 FP인 row만 UPDATE is_isolated=true
    return n
```

### 3.4 회귀 검증 통합 (`_regression_check`)

```python
def _regression_check(self, recent_law_ids, *, only_stages):
    """회귀 검증 — 90c994c 본질 보전 + 전역 sub_type 진단."""
    
    # 1. 기존 회귀 (90c994c 보전 — TP variance + sample n≥30)
    for law_id in recent_law_ids:
        ...
    
    # 2. 전역 sub_type 정확도 진단 (10법령마다 1회)
    target_subtypes = ['OBLIGATION_HEADER', 'PROHIBITION_HEADER', 'AUTHORITY_HEADER', 
                       'EXEMPTION_HEADER', 'DEFINITION_HEADER', 'AS_본다',
                       'REFERENCE_TO_ATTACHMENT', 'DELEGATION_HEADER']
    for st in target_subtypes:
        result = compute_subtype_group_accuracy(self.supabase, st, sample_size=100, seed=42)
        n = result.get('n', 0); acc = result.get('accuracy', 0)
        if n >= 30 and acc < 0.7:
            logger.warning(
                "v4.0 전역 역순 검증 sub_type=%s acc=%.4f n=%s → 본질 점검",
                st, acc, n,
            )
        else:
            logger.info(
                "v4.0 전역 역순 검증 sub_type=%s acc=%.4f n=%s ✅",
                st, acc, n,
            )
```

→ **매 법령 = `_process_single_law`에서 역순 검증 본 운영**. **회귀 = 전역 sub_type 진단** (보조).

---

## 4. 단위 테스트

```python
def test_verify_row_obligation_header_diverse_endings():
    """v4.0 OBLIGATION_HEADER 다양성 — 10개 종결 모두 TP."""
    for text in ["...따라야 한다.", "...내줘야 한다.", "...커야한다.", "...지켜야 한다.",
                 "...내야 한다.", "...보내야 한다.", "...되어야 한다.", "...있어야 한다.",
                 "...갖춰야 한다.", "...준수하여야 한다."]:
        assert _verify_row('OBLIGATION_HEADER', text) == 'TP', text

def test_verify_row_reference_to_attachment():
    """v4.0 REFERENCE_TO_ATTACHMENT — 별표/별첨/별지."""
    for text in ["...별표와 같다.", "...별첨과 같다.", "...별지와 같다."]:
        assert _verify_row('REFERENCE_TO_ATTACHMENT', text) == 'TP'

def test_compute_subtype_group_accuracy():
    """sub_type별 group sample (mock supabase)."""

def test_compute_law_reverse_verification_pass():
    """법령 역순 검증 — 모든 sub_type acc ≥ 0.7 → overall_pass=True."""

def test_compute_law_reverse_verification_fail_specific_subtype():
    """법령 역순 검증 — AS_본다 acc < 0.7 → overall_pass=False, failed_subtypes=['AS_본다']."""

def test_process_single_law_reverse_verify_fail_halts_iteration():
    """매 법령 — 역순 검증 FAIL 시 격리 + 다음 iteration."""

def test_process_single_law_pass_when_both_forward_and_reverse_pass():
    """매 법령 — 정순 + 역순 둘 다 PASS만 진정 PASS."""

def test_isolate_failed_subtypes():
    """failed sub_type의 FP row만 격리 (TP 보전)."""
```

---

## 5. 검증 임계

| 항목 | 임계 |
|---|---|
| 단위 테스트 | 334 → 343+ passed (8+ 신규) |
| `validator.py` MD5 | **8,100 bytes 동일** (강제) |
| `iterator.py` 본문 | `_process_single_law` 정정 (역순 통합) + `_regression_check` 보강 |
| `pipeline.py` / `stages/` / `morpheme.py` | 변동 X |
| `_verify_row` 본질 | 단위 테스트 PASS + Cursor 50건 sample 직접 검증 |
| **매 법령 정순 + 역순** | **둘 다 PASS만 진정 PASS** (METHODOLOGY 정합) |

---

## 6. 운영 흐름

```bash
# 1. 코드 갱신
cd tai-api && git pull origin dev

# 2. 처음부터 재가동 (격리 0 상태)
railway run python3 scripts/track_e_phase2_run.py --phase22-v3 --iterate \
  --order ascending_size \
  --max-iterations-per-law 5 \
  --regression-window 10 \
  2>&1 | tee phase22_v4_run_$(date +%Y%m%d_%H%M%S).log
```

### 6.1 기대 본질

| 영역 | 기대 |
|---|---|
| 처리 법령 | 704/704 PASS/PASS_STABLE |
| **격리 row** | **본질적 FP만 (대폭 감소, ~3,000 추정)** |
| TP 변동 | 0 row |
| Phase 1 보전 | 8,303 row |
| **매 법령 역순 검증** | **각 sub_type acc ≥ 0.7 + n ≥ 5** |
| **OBLIGATION_HEADER 격리** | **0 (본질적 TP 보전)** |

### 6.2 PM 후속 점검

```sql
-- 1. 격리 분포 (FP 본질만)
SELECT isolation_reason, COUNT(*) FROM stage_2_elements 
WHERE is_isolated=true GROUP BY isolation_reason;

-- 2. OBLIGATION_HEADER 격리 0 본질 검증
SELECT COUNT(*) FROM stage_2_elements 
WHERE sub_type='OBLIGATION_HEADER' AND is_isolated=true;
-- 기대: 0 또는 매우 낮은 수치

-- 3. sub_type별 역순 검증 결과 (logger 또는 verification_log)
SELECT * FROM verification_log 
WHERE check_name LIKE '%v4_reverse%' OR check_name LIKE '%subtype_group%' 
ORDER BY verified_at DESC LIMIT 50;
```

---

## 7. 본 명세 외 작업 X

- Stage 3 / METHODOLOGY 6하원칙 / Track B/C / 6하원칙 보강 / dev→main merge

---

## 8. push 정책

| 영역 | 대상 | 본질 |
|---|---|---|
| 코드 | `tai-api` `dev` (Cursor) | v4.0 보강 push |
| 테스트 | `tai-api` `dev` (Cursor) | 8+ 신규 |
| 명세 | `tai-admin` `main` (PM 자체) | 본 정정 commit |

---

## 9. Cursor 위탁 메시지 (그대로 복붙)

```
[Phase 2.2 v4.0 정정 위탁 — 정순 + 역순 본질 통합 (METHODOLOGY 정합)]

선행 base: tai-api dev 90c994c
본 명세 (정정): tai-admin main `Cursor_Phase_2_2_v4_Reverse_Verification_Spec.md`

본 PM 본질 (사용자 본질 정정 정합):
1. v3.0 운영 결과 본질 결함 — _verify_row CATEGORY_VERIFICATION_PATTERNS 좁음
2. OBLIGATION_HEADER 2,027건 본질적 TP 잘못 격리 (10/10 sample 검증)
3. 사용자 본질 결정 — 역순 검증 탑재 + 처음부터 재가동
4. ★ 사용자 본질 정정 — "역순 검증은??" → 회귀 hook X, 본 운영 핵심 본질로 격상
5. PM 자체 DB 격리 복원 완료 (10,214 → 0)

작업 영역:
1. engine/sample_accuracy.py:
   - CATEGORY_VERIFICATION_PATTERNS 본질 보강 (위 명세 §2.2)
   - compute_subtype_group_accuracy 신규 (law_id 옵션 추가)
   - compute_law_reverse_verification 신규 (법령 단위 역순 검증)

2. engine/iterator.py:
   - _process_single_law 본질 정정 (정순 + 역순 둘 다)
     - try 블록에서 Pipeline.run 후 compute_law_reverse_verification 호출
     - 역순 FAIL 시 _isolate_failed_subtypes 격리 + 다음 iteration
     - 정순 + 역순 둘 다 PASS만 진정 PASS
   - _isolate_failed_subtypes 신규
   - _regression_check 보강 (전역 sub_type 진단 추가)
   - 90c994c 본질 보전 (PASS_STABLE / TP variance)

3. tests/ — 8+ 신규:
   - test_verify_row_obligation_header_diverse_endings (10 종결)
   - test_verify_row_reference_to_attachment
   - test_compute_subtype_group_accuracy
   - test_compute_law_reverse_verification_pass
   - test_compute_law_reverse_verification_fail_specific_subtype
   - test_process_single_law_reverse_verify_fail_halts_iteration
   - test_process_single_law_pass_when_both_forward_and_reverse_pass
   - test_isolate_failed_subtypes

검증 임계:
- 단위 테스트 334 → 343+ passed
- validator.py 0 byte (MD5 8,100)
- pipeline.py / stages/ / morpheme.py / subtype_rule_match.py 변동 X
- 매 법령 정순 + 역순 둘 다 PASS만 진정 PASS

본 명세 외 작업 X.

push: tai-api dev에 v4.0 보강.

운영 흐름 (사용자):
1. cd tai-api && git pull origin dev
2. railway run python3 scripts/track_e_phase2_run.py --phase22-v3 --iterate \
     --order ascending_size --max-iterations-per-law 5 --regression-window 10
3. 운영 종료 후 PM DB 직접 점검

진행 부탁드립니다.
```

---

## 10. 본 PM 본질 학습 누적 (20단계)

| # | 사용자 본질 | PM 학습 |
|---|---|---|
| 19 | `_verify_row` 본질 자체 검증 누락 | v3.0 명세 결함 인정 |
| 20 | **역순 검증 = 본 운영 핵심 본질** (회귀 hook X) | 본 PM v4.0 (이전) 명세 본질 미달 인정. v4.0 (본 정정) 정순 + 역순 통합 본질로 격상. METHODOLOGY 정합. |

본 PM 자체 결정적 결함 인정:
- 역순 검증을 회귀 검증의 부속물 수준으로 격하 = 본질 미달
- 본 v4.0 정정 — 정순 + 역순 둘 다 본 운영 핵심 본질
- 사용자 본질 정합

---

**END OF SPEC v4.0 (정정)**
