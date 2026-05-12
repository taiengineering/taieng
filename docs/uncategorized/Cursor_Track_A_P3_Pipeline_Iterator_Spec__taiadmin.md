# [Cursor 위탁] Track A P3 — Pipeline law 단위 처리 본질 도입 (구조적 보강)

**작성일**: 2026-05-10  
**작성자**: PM 창  
**위탁 대상**: Cursor (TAI Backend / Railway)  
**선행**:
- `Cursor_Phase_2_2_Pipeline_Engine_Spec_v1_2.md` — Pipeline 본질 (단계+단계 흐름)
- `tai-api` `dev` `b699218` — Pipeline + sample_accuracy 보강 완료
- `Track_E_20260510_Phase2_2.md` — Cursor Phase 2.2 보고서

**위치**: Track A P3 (엔진 인프라 보강), Phase 2.2 작업 영역 X.

---

## 0. 본 명세의 본질

### 0.1 사용자 본질 지적

> "계속 전체를 파싱을 해서 나온 문제인데. 한 개의 법령씩 돌리면서 엔진 보강을 하는 방법은 어떤가요?"

### 0.2 현재 엔진 본질의 한계

```python
# 현재 (b699218)
Pipeline.run(input_data, only_stages=[2])  # 전체 데이터 처리
compute_stage2_sample_accuracy(supabase, sample_size=100)  # 전체 random sample
```

→ 1,322 법령 한 번에 처리 + 정확도는 전체 평균. 법령별 패턴 다양성 묻힘.

### 0.3 본 명세 본질

엔진 본질 (단계+단계 흐름)을 보전하면서 **법령 단위 처리** 인터페이스 추가:

```python
# v1.3 (본 명세)
Pipeline.run(input_data, only_stages=[2], law_id=N)        # 단일 법령
Pipeline.run(input_data, only_stages=[2], law_batch=[ids]) # batch 법령
compute_stage2_sample_accuracy(supabase, law_id=N)         # 법령별 정확도

# 자동 순회 (Track A 엔진 인프라)
PipelineIterator(pipeline, supabase).iterate(
    order='ascending_size',  # 작은 법령부터
    regression_window=10,    # 이전 10개 법령 회귀
)
```

→ 엔진의 단계+단계 흐름 보전 + 법령 단위 본질 + 자동 순회 + 회귀 테스트.

---

## 1. 절대 원칙

### 1.1 마스터 §2

| 원칙 | 본 명세 적용 |
|---|---|
| ① LLM X | 정규식 + 빈도만 |
| ② 법령 보전 | source_text 변경 X |
| ③ 누락 0건 | 151,751 row 보전 |
| ④ 100% 매핑 | Pipeline 인터페이스만 보강 |
| ⑤ 오염 = 폐기 | **법령 단위 폐기 가능** (사용자 본질 지적 정합) |
| ⑥ 검증 부담 0 | Pipeline 자동 순회 |
| ⑦ Ground Truth 우선 | DB 직접 점검 |
| ⑧ DB가 ground truth | 진입 점검 SQL 필수 |

### 1.2 변경 X (강제)

| 영역 | 변경 X | 본질 |
|---|---|---|
| `engine/validator.py` | 0 byte | 사용자 강제 |
| `engine/pipeline.py` | **인터페이스 보강만** (law_id/law_batch 인자 추가) | 단계+단계 흐름 보전 |
| `engine/stages/base.py` | StageContext에 law_id 추가 | 호환 |
| `engine/sample_accuracy.py` | `law_id` 인자 추가 (kwarg) | 호환 |
| Phase 1 결과 | 절대 X | 보전 |
| Phase 2.1 결과 | 절대 X (본 명세 X) | Phase 2.2 분리 |

### 1.3 본 명세의 본질 강제

| 규칙 | 본질 |
|---|---|
| Pipeline 인터페이스 호환 | 기존 Pipeline.run() 시그니처 보전 (kwarg 추가) |
| Stage 추상 클래스 호환 | run() 시그니처 보전 |
| 자동 순회는 별도 클래스 | `PipelineIterator` (Pipeline 본문 변경 X) |
| 회귀 테스트는 Iterator 본질 | 이전 N개 법령 자동 재검증 |

---

## 2. 작업 환경

| 항목 | 값 |
|---|---|
| Supabase | `vwlahtguyggrhvslabax` |
| 코드 base | `taiengineering/tai-api` `dev` `b699218` |
| 신규 파일 | `engine/iterator.py`, `tests/test_iterator.py` |
| 보강 파일 | `engine/pipeline.py`, `engine/stages/base.py`, `engine/sample_accuracy.py` |
| 변경 X | `validator.py`, `subtype_rule_match.py`, `morpheme.py` |
| 보고서 | `tai-admin` `docs/extraction/v3/log/Track_A_P3_Pipeline_Iterator.md` |

### 2.1 진입 점검 SQL

```sql
SELECT 
  (SELECT COUNT(*) FROM stage_2_elements) AS total,           -- 151,751
  (SELECT COUNT(*) FROM law) AS laws,                         -- ~1,322
  (SELECT COUNT(DISTINCT lap.article_id) FROM law_article_part lap) AS articles,
  (SELECT COUNT(*) FROM rule_classify_subtype WHERE enabled=true) AS rules; -- 34
```

→ 결과 다르면 정지 + PM 회신.

---

## 3. Track A P3-1 — Pipeline 인터페이스 보강

### 3.1 engine/stages/base.py 보강 (StageContext에 law_id 추가)

```python
# engine/stages/base.py
@dataclass
class StageContext:
    """Stage 실행 시 공유 컨텍스트."""
    supabase: Any | None = None
    config: dict[str, Any] | None = None
    law_id: int | None = None              # ★ 신규: 단일 법령 처리
    law_batch: list[int] | None = None     # ★ 신규: batch 법령 처리
```

→ 기존 인터페이스 호환 (None 기본값).

### 3.2 engine/pipeline.py 보강

```python
# engine/pipeline.py — Pipeline.run() 시그니처 호환 보강
class TAIExtractionPipeline:
    def run(
        self,
        input_data: Any,
        *,
        only_stages: list[int] | None = None,
        law_id: int | None = None,        # ★ 신규
        law_batch: list[int] | None = None,  # ★ 신규
    ) -> PipelineRun:
        """엔진 실행. law_id / law_batch 시 해당 법령만 처리."""
        # ctx에 law 정보 주입
        if law_id is not None:
            self.ctx.law_id = law_id
        if law_batch is not None:
            self.ctx.law_batch = law_batch
        
        # 기존 흐름 (단계+단계, 검증 hook 내장) 그대로
        run = PipelineRun()
        current = input_data
        for stage in self.stages:
            if only_stages is not None and stage.stage_number not in only_stages:
                continue
            
            output = stage.run(current, self.ctx)  # Stage가 ctx의 law_id 활용
            run.stage_outputs.append(output)
            
            # 검증 hook (기존 동일)
            accuracy, sample_size = stage.measure_accuracy(output, self.ctx)
            check = Validator.evaluate_sample_accuracy(...)
            self.validator.log(check)
            run.check_results.append(check)
            
            if check.result_status in ('FAIL', 'WARNING') if self.halt_on_warning else ('FAIL',):
                run.halted_at = stage
                raise PipelineHaltError(stage, check)
            
            current = output.data
        return run
```

### 3.3 engine/stages/stage_2.py 보강 (law_id 필터)

```python
# engine/stages/stage_2.py
class Stage2Decomposer(Stage):
    def run(self, input_data: Stage2Input, ctx: StageContext) -> StageOutput:
        # ctx.law_id / ctx.law_batch 활용
        if ctx.law_id is not None:
            # 해당 법령의 stage_1_clauses만 처리
            clauses = fetch_clauses_by_law_id(ctx.supabase, ctx.law_id)
        elif ctx.law_batch:
            clauses = fetch_clauses_by_law_batch(ctx.supabase, ctx.law_batch)
        else:
            clauses = input_data.clauses or fetch_all_clauses(ctx.supabase)
        
        elements = decompose_clauses(clauses, ctx.supabase)
        return StageOutput(data=Stage2Output(elements=elements), metrics={...})
    
    def measure_accuracy(self, output: StageOutput, ctx: StageContext) -> tuple[float, int]:
        from engine.sample_accuracy import compute_stage2_sample_accuracy
        return compute_stage2_sample_accuracy(
            ctx.supabase,
            law_id=ctx.law_id,           # ★ 법령별 측정
            law_batch=ctx.law_batch,     # ★ batch 측정
        )
```

### 3.4 engine/sample_accuracy.py 보강

```python
# engine/sample_accuracy.py — kwarg 추가 (기존 호환)
def compute_stage2_sample_accuracy(
    supabase,
    *,
    sample_size: int = DEFAULT_SAMPLE_ARTICLES,
    seed: int | None = None,
    law_id: int | None = None,           # ★ 신규
    law_batch: list[int] | None = None,  # ★ 신규
) -> tuple[float, int]:
    """sample 정확도 측정. law_id 시 해당 법령만, 미지정 시 전체 random."""
    rows = _fetch_sample_rows(
        supabase,
        sample_articles=sample_size,
        law_id=law_id,
        law_batch=law_batch,
    )
    # 이하 기존 _verify_row 카테고리화 그대로
    ...
```

### 3.5 _fetch_sample_rows 보강 (law 필터)

```python
def _fetch_sample_rows(
    supabase,
    *,
    sample_articles: int,
    law_id: int | None = None,
    law_batch: list[int] | None = None,
) -> list[dict]:
    """psycopg2 SQL with law 필터."""
    if law_id is not None:
        sql = """
        SELECT s2.sub_type, s1.source_text
        FROM stage_2_elements s2
        JOIN stage_1_clauses s1 ON s1.id = s2.clause_id
        JOIN law_article_part lap ON lap.id = s1.part_id
        JOIN law_article la ON la.id = lap.article_id
        WHERE la.law_id = %s
        """
        params = (law_id,)
    elif law_batch:
        sql = """
        SELECT s2.sub_type, s1.source_text
        FROM stage_2_elements s2
        JOIN stage_1_clauses s1 ON s1.id = s2.clause_id
        JOIN law_article_part lap ON lap.id = s1.part_id
        JOIN law_article la ON la.id = lap.article_id
        WHERE la.law_id = ANY(%s)
        """
        params = (law_batch,)
    else:
        # 기존 random 100조문
        sql = """ ... """
        params = (sample_articles,)
    
    # psycopg2 실행 + fallback
```

---

## 4. Track A P3-2 — PipelineIterator (자동 순회 + 회귀 테스트)

### 4.1 engine/iterator.py 신규

```python
"""Pipeline Iterator — 법령 단위 자동 순회 + 회귀 테스트.

엔진의 단계+단계 흐름 위에서 법령 단위 점진 처리 본질 구현.
"""
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Iterator, Literal

from engine.pipeline import TAIExtractionPipeline, PipelineHaltError, PipelineRun

logger = logging.getLogger(__name__)


@dataclass
class IteratorRun:
    """Iterator 실행 결과."""
    laws_processed: list[int] = field(default_factory=list)  # PASS 법령
    laws_failed: list[tuple[int, PipelineRun]] = field(default_factory=list)  # FAIL 법령
    total_laws: int = 0
    halted: bool = False


class PipelineIterator:
    """법령 단위 자동 순회 + 회귀 테스트 본질."""
    
    def __init__(
        self,
        pipeline: TAIExtractionPipeline,
        supabase,
        *,
        order: Literal['ascending_size', 'descending_size', 'random', 'sequential'] = 'ascending_size',
        regression_window: int = 0,    # 이전 N개 법령 회귀 (0 = X)
        halt_on_first_fail: bool = True,  # 첫 FAIL에서 정지
    ):
        self.pipeline = pipeline
        self.supabase = supabase
        self.order = order
        self.regression_window = regression_window
        self.halt_on_first_fail = halt_on_first_fail
    
    def iterate(self, *, only_stages: list[int] | None = None) -> IteratorRun:
        """모든 법령 순회 + 자동 검증."""
        run = IteratorRun()
        law_ids = self._fetch_law_order()
        run.total_laws = len(law_ids)
        
        for i, law_id in enumerate(law_ids):
            try:
                # 단일 법령 Pipeline 실행 (검증 hook 내장)
                pipeline_run = self.pipeline.run(
                    input_data=None,
                    only_stages=only_stages,
                    law_id=law_id,
                )
                run.laws_processed.append(law_id)
                logger.info(f"[Iterator {i+1}/{run.total_laws}] law_id={law_id} PASS")
                
                # 회귀 테스트 (이전 N개 법령 재검증)
                if self.regression_window > 0 and i % 10 == 0 and i > 0:
                    self._regression_check(run.laws_processed[-self.regression_window:])
            except PipelineHaltError as e:
                run.laws_failed.append((law_id, e.check))
                logger.error(f"[Iterator {i+1}/{run.total_laws}] law_id={law_id} {e.check.result_status}")
                if self.halt_on_first_fail:
                    run.halted = True
                    return run
        
        return run
    
    def _fetch_law_order(self) -> list[int]:
        """법령 순회 순서 결정 (작은 법령부터 / random / sequential)."""
        # SELECT id FROM law ORDER BY <order> 
        ...
    
    def _regression_check(self, recent_law_ids: list[int]) -> None:
        """이전 N개 법령 재검증 (룰 정정 후 회귀)."""
        for law_id in recent_law_ids:
            pipeline_run = self.pipeline.run(
                input_data=None,
                only_stages=[2],
                law_id=law_id,
            )
            # 이전 PASS이었지만 룰 정정 후 FAIL 시 즉시 정지
```

### 4.2 사용 패턴 (scripts/track_e_phase2_run.py)

```python
# scripts/track_e_phase2_run.py 보강 (점진 처리 모드)
def run_phase22_iterate(supabase):
    """점진 처리 모드 — 법령 단위 자동 순회."""
    pipeline = TAIExtractionPipeline(
        stages=[Stage2Decomposer()],
        validator=Validator(supabase=supabase),
        ctx=StageContext(supabase=supabase),
        halt_on_warning=True,
    )
    iterator = PipelineIterator(
        pipeline=pipeline,
        supabase=supabase,
        order='ascending_size',  # 작은 법령부터 (룰 발견 빠름)
        regression_window=10,
        halt_on_first_fail=True,
    )
    run = iterator.iterate(only_stages=[2])
    
    if run.halted:
        # 첫 FAIL 법령에서 정지 — PM 회신
        first_fail_law = run.laws_failed[0]
        raise SystemExit(
            f"법령 {first_fail_law[0]} {first_fail_law[1].result_status} "
            f"(actual={first_fail_law[1].actual_value:.4f}). "
            f"PASS 법령: {len(run.laws_processed)}/{run.total_laws}"
        )
    
    return run
```

### 4.3 CLI 옵션 (scripts/track_e_phase2_run.py)

```bash
# 단일 법령 처리
railway run python3 scripts/track_e_phase2_run.py --phase22 --law-id 12345

# batch 법령 처리
railway run python3 scripts/track_e_phase2_run.py --phase22 --law-batch 12345,67890,...

# 자동 순회 (점진 처리)
railway run python3 scripts/track_e_phase2_run.py --phase22 --iterate --order ascending_size --regression-window 10
```

---

## 5. 단위 테스트 (`tests/test_iterator.py` 신규)

```python
"""PipelineIterator 단위 테스트."""
import pytest
from engine.iterator import PipelineIterator, IteratorRun
from engine.pipeline import TAIExtractionPipeline, PipelineHaltError
# ... mock import

def test_iterator_all_pass():
    """모든 법령 PASS → laws_processed 모두 채움."""
    iterator = PipelineIterator(
        pipeline=mock_pass_pipeline,
        supabase=mock_supabase,
        order='ascending_size',
        regression_window=0,
        halt_on_first_fail=True,
    )
    run = iterator.iterate(only_stages=[2])
    assert run.total_laws == 10
    assert len(run.laws_processed) == 10
    assert len(run.laws_failed) == 0
    assert run.halted is False

def test_iterator_halt_on_first_fail():
    """첫 FAIL 법령에서 정지."""
    iterator = PipelineIterator(
        pipeline=mock_fail_at_5_pipeline,  # 5번째 법령에서 FAIL
        supabase=mock_supabase,
        halt_on_first_fail=True,
    )
    run = iterator.iterate(only_stages=[2])
    assert run.halted is True
    assert len(run.laws_processed) == 4
    assert len(run.laws_failed) == 1

def test_iterator_regression_window():
    """회귀 테스트 — 이전 N개 법령 재검증."""
    # 10개 법령 PASS 후 룰 정정 → 11번째 법령부터 회귀 테스트
    # 이전 PASS 중 1개 FAIL → 정지

def test_pipeline_law_id_filter():
    """Pipeline.run(law_id=N)이 Stage 2에 ctx.law_id 주입."""
    pipeline = TAIExtractionPipeline(...)
    pipeline.run(input_data=None, law_id=12345)
    assert pipeline.ctx.law_id == 12345

def test_compute_stage2_sample_accuracy_law_id():
    """sample_accuracy(law_id=N)이 해당 법령만 측정."""
    # mock supabase with law-filtered rows
    accuracy, n = compute_stage2_sample_accuracy(mock_sb, law_id=12345)
    assert n > 0
    assert 0.0 <= accuracy <= 1.0
```

---

## 6. 검증 임계 (Track A P3 PASS 기준)

| check | 임계 | 본질 |
|---|---|---|
| 단위 테스트 (`test_iterator.py` + 보강) | 100% pass | 인터페이스 정합 |
| 회귀 테스트 (`test_pipeline.py` 등 기존) | 0 fail (163 → 170+) | 호환 |
| Pipeline 인터페이스 호환 | 기존 시그니처 미파괴 | 정합 |
| validator.py 본문 변경 | 0 byte | 강제 |
| coverage | ≥ 80% | Track A 정합 |
| iterator 단위 테스트 PASS/FAIL/회귀 | 분기 정합 | 본질 |

---

## 7. Track A P3 PASS 후 운영 (Phase 2.2 점진 처리)

### 7.1 진입 점검

```bash
railway run python3 scripts/track_e_phase2_run.py --phase22 --only checks
# row 수 + 룰 수 + 법령 수 점검
```

### 7.2 Phase 2.2-C 점진 처리 모드

```bash
railway run python3 scripts/track_e_phase2_run.py --phase22 --iterate --order ascending_size --regression-window 10

# 자동 진행:
# 1. 작은 법령부터 순회
# 2. 각 법령 Pipeline.run(law_id=N) 실행
# 3. PASS (≥ 90%) → 다음 법령
# 4. FAIL → 첫 FAIL에서 정지 + PM 회신
# 5. 룰 정정 후 재진행 (--iterate 다시)
# 6. 모든 법령 PASS → 종합 sample_accuracy 측정
```

### 7.3 결과 분기

| 결과 | 처리 |
|---|---|
| 모든 법령 PASS | 종합 sample_accuracy 자동 ≥ 90% |
| 일부 FAIL | 정지 + PM 회신 → 룰 정정 → 재진행 |
| 회귀 FAIL | 룰 정정으로 이전 PASS 법령 영향 → 정지 + PM 회신 |

---

## 8. 임의판단 절대 금지

| 영역 | 금지 |
|---|---|
| LLM 호출 | X |
| validator.py 본문 변경 | 0 byte |
| Pipeline 본문 시그니처 변경 (호환 X) | 절대 X |
| Stage 추상 클래스 시그니처 변경 | 절대 X |
| 회귀 미실시 강제 진행 | 절대 X |
| FAIL 시 강제 진행 | halt_on_first_fail=True 우회 X |

---

## 9. 중단 트리거

1. 진입 점검 SQL 결과 명세와 다름
2. validator.py 본문 변경 발견
3. 단위 테스트 회귀 (163 → < 163)
4. Pipeline 인터페이스 호환 깨짐 (기존 Pipeline.run() 시그니처)
5. Stage 추상 클래스 시그니처 변경
6. 운영 시 회귀 FAIL (이전 PASS 법령에서 FAIL)

---

## 10. 본 명세 외 작업 절대 X

- ❌ Stage 3 진입
- ❌ v3.0 마스터 객체 결정
- ❌ Tier 2-4 본법 수집
- ❌ Track C v1.3
- ❌ Phase 2.1 결과 변경 (Phase 2.2 영역)
- ❌ Phase 1 결과 변경
- ❌ validator.py 본문 수정
- ❌ Pipeline 시그니처 변경 (호환 깨짐)
- ❌ 신규 sub_type 추가 (본 명세 X)
- ❌ 신규 룰 INSERT/UPDATE (Phase 2.2 영역)

---

## 11. 보고서 양식 (`Track_A_P3_Pipeline_Iterator.md`)

```markdown
# [Track A P3] Pipeline law 단위 처리 본질 도입

## 1. 변경 사항
### 1.1 engine/pipeline.py — law_id / law_batch 인자 추가
### 1.2 engine/stages/base.py — StageContext에 law_id 추가
### 1.3 engine/stages/stage_2.py — ctx.law_id 활용
### 1.4 engine/sample_accuracy.py — law_id kwarg 추가
### 1.5 engine/iterator.py 신규 — PipelineIterator
### 1.6 scripts/track_e_phase2_run.py — CLI 옵션 추가

## 2. 단위 테스트
### 2.1 test_iterator.py 신규
### 2.2 회귀 검증 (163 → 170+ passed)

## 3. validator.py 0 byte 변경 확인 (MD5)

## 4. 운영 가이드 (Track A P3 PASS 후 Phase 2.2 점진 처리)
```

---

## 12. 환경 정보

| 항목 | 값 |
|---|---|
| 코드 base | `tai-api` `dev` `b699218` |
| 신규 파일 | `engine/iterator.py`, `tests/test_iterator.py` |
| 보강 파일 | `engine/pipeline.py`, `engine/stages/base.py`, `engine/stages/stage_2.py`, `engine/sample_accuracy.py`, `scripts/track_e_phase2_run.py` |
| 변경 X | `validator.py`, `subtype_rule_match.py`, `morpheme.py`, `phase_22_apply.py` |
| 보고서 commit | `tai-admin` main `docs/extraction/v3/log/Track_A_P3_Pipeline_Iterator.md` |
| 코드 commit | `tai-api` `dev` |

---

**END — Pipeline law 단위 처리 본질 도입 (사용자 본질 지적 정합) → Phase 2.2 점진 처리 모드 가능.**
