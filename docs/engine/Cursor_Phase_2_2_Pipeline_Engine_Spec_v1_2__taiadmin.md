# [Cursor 위탁 v1.2] Phase 2.2 — 엔진 Pipeline 구조 본질 설계 + 룰 보강 + 데이터셋 처리

**작성일**: 2026-05-10  
**작성자**: PM 창 (Claude 기획창)  
**위탁 대상**: Cursor (TAI Backend / Railway)  
**선행 폐기**:
- `Cursor_Phase_2_2_Accuracy_Spec.md` v1.0 (commit `6f39d25540e5c8...`) — 작업 순서 본질 오류
- `Cursor_Phase_2_2_Engine_First_Spec_v1_1.md` v1.1 (commit `962aa6101ef1ef6...`) — 엔진 구조 설계 누락

**선행 보전**:
- `Track_E_20260510_Phase2_1_Reverse_Validation.md` (PM 진단)
- `Track_ABCDE_Verification_Matrix_20260510.md` (전수 검증 매트릭스)

---

## 0. 본 명세의 본질

### 0.1 v1.0 + v1.1 본질 오류

| 버전 | 본질 오류 |
|---|---|
| v1.0 | 룰 변경 + 데이터 처리 한 패키지 (검증 없는 데이터 처리) |
| v1.1 | 작업 순서만 정의 (A→B→C 순차), **엔진 구조 설계 X** |

**공통 한계**: 엔진을 **"프로그램의 모음"**으로 다룸. 단계 간 흐름이 외부 script로 제어됨.

### 0.2 v1.2 본질 (사용자 본질 지적 정합)

> "엔진이란건 프로그램의 모음이 아니라 단계+단계로 이어져서 가는 방식"

**올바른 엔진 본질**:
```python
class TAIExtractionPipeline:
    """단계+단계로 이어지는 엔진."""
    stages = [Stage1, Stage2, Stage3]
    
    def run(self, input):
        current = input
        for stage in self.stages:
            output = stage.run(current)              # 단계 실행
            check = self.validator.evaluate(stage, output)  # 검증 hook 내장
            if check.result_status in ('FAIL', 'WARNING'):
                raise PipelineHaltError(check)       # 미통과 시 자동 정지
            current = output                          # 다음 단계 입력
        return current
```

→ **단계+단계 흐름이 엔진 내장 + 검증 hook 엔진 내장 + 미통과 시 자동 정지**.

### 0.3 v1.2 작업 본질

```
[Phase 2.2-A] 엔진 Pipeline 구조 신규 설계 (Track A P3 통합)
   ├ engine/pipeline.py 신규
   ├ engine/stages/base.py 신규 (Stage 추상)
   ├ engine/stages/stage_1.py / stage_2.py / stage_3.py (기존 wrapping)
   ├ engine/schemas/ 신규 (입출력 schema)
   ├ validator.py Pipeline 내장 호출
   └ 단위 테스트 (Pipeline 흐름 검증)
        ↓ PASS 확정 (단위 테스트 100% + state machine 검증)
[Phase 2.2-B] Stage 2 룰 보강 (Pipeline 위에서)
   ├ subtype_rule_match.py 보강
   ├ 신규 룰 12+개 (Stage 2의 일부)
   ├ 룰별 단위 테스트 (≥ 95%)
   └ Stage 2 통합 단위 테스트 (sample 100건)
        ↓ PASS 확정
[Phase 2.2-C] 데이터셋 처리 (Pipeline 실행)
   ├ 백업
   ├ DB CHECK enum 확장
   ├ 룰 DB 적용
   ├ Phase 2.1 분류 폐기 (Phase 1 보전)
   ├ Pipeline.run() 실행 (Stage 2 재처리)
   └ 검증 hook 자동 PASS 확정 (≥ 90%)
        ↓ PASS → 보고서 + commit + push
```

---

## 1. 절대 원칙

### 1.1 마스터 §2

| 원칙 | 본 명세 적용 |
|---|---|
| ① LLM X | Kiwi + 정규식 + DB 빈도만 |
| ② 법령 보전 | source_text 변경 X |
| ③ 누락 0건 | 151,751 row 변동 X |
| ④ 100% 매핑 | UPDATE만 (신규 룰 INSERT 허용) |
| ⑤ 오염 = 폐기 | Phase 2.1 분류 폐기 (Phase 1 보전) |
| ⑥ 검증 부담 0 | Pipeline 자동 검증 |
| ⑦ Ground Truth 우선 | DB 직접 점검 |
| ⑧ DB가 ground truth | 진입 점검 SQL 필수 |

### 1.2 validator.py 본질 (변경 X)

```python
# engine/validator.py — 본문 절대 수정 X
SAMPLE_ACCURACY_THRESHOLDS = {1: 0.95, 2: 0.90, 3: 0.90}
# 그대로 활용. Pipeline이 내장 호출.
```

### 1.3 v1.2 추가 강제

| 규칙 | 본질 |
|---|---|
| 엔진 = Pipeline + Stage + 검증 hook 내장 | 사용자 본질 지적 정합 |
| 단계 간 흐름 = Pipeline 내장 (script X) | 엔진의 본질 |
| 검증 hook = Stage 종료 시 자동 (외부 호출 X) | 엔진 내장 |
| FAIL/WARNING 시 PipelineHaltError 자동 raise | 마스터 §2.5 정합 |

---

## 2. 작업 환경

| 항목 | 값 |
|---|---|
| Supabase | `vwlahtguyggrhvslabax` |
| 환경 | `railway run python3 ...` |
| 코드 base | `taiengineering/tai-api` `dev` |
| 검증엔진 | `engine/validator.py` (변경 X) |
| 신규 파일 | `engine/pipeline.py`, `engine/stages/`, `engine/schemas/` |
| 보강 파일 | `engine/subtype_rule_match.py` |

### 2.1 진입 점검 SQL

```sql
SELECT 
  (SELECT COUNT(*) FROM stage_2_elements) AS total,           -- 151,751
  (SELECT COUNT(*) FROM stage_2_elements WHERE sub_type='UNCLASSIFIED') AS uc,  -- 68,130
  (SELECT COUNT(*) FROM rule_classify_subtype WHERE enabled=true) AS active;    -- 34
-- 결과 다르면 정지 + PM 회신
```

---

## 3. Phase 2.2-A — 엔진 Pipeline 구조 신규 설계 (Track A P3 통합)

### 3.1 본 단계의 본질

**DB는 절대 건드리지 않음**. 엔진의 단계+단계 흐름 본질을 코드 구조로 갖춤.

### 3.2 신규 파일 구조

```
engine/
├ pipeline.py                    ← 신규: Pipeline 클래스
├ validator.py                   ← 변경 X (그대로)
├ morpheme.py                    ← 변경 X (Kiwi 형태소)
├ subtype_rule_match.py          ← Phase 2.2-B에서 보강
├ stages/                        ← 신규 디렉토리
│   ├ __init__.py
│   ├ base.py                    ← 신규: Stage 추상 클래스
│   ├ stage_1.py                 ← 신규: stage_1_splitter.py wrapping
│   ├ stage_2.py                 ← 신규: stage_2_decomposer.py wrapping
│   └ stage_3.py                 ← 신규: stage_3_objectifier.py wrapping
├ schemas/                       ← 신규 디렉토리
│   ├ __init__.py
│   ├ stage_1.py                 ← Stage 1 입출력 schema
│   ├ stage_2.py                 ← Stage 2 입출력 schema
│   └ stage_3.py                 ← Stage 3 입출력 schema
├ stage_1_splitter.py            ← 변경 X (Stage 1 내부 활용)
├ stage_2_decomposer.py          ← 변경 X (Stage 2 내부 활용)
├ stage_3_objectifier.py         ← 변경 X (Stage 3 내부 활용)
└ ...
```

### 3.3 engine/stages/base.py — Stage 추상 클래스

```python
"""TAI 법령엔진 v3.0 — Stage 추상 base 클래스.

엔진의 단계+단계 흐름의 본질을 정의. 각 Stage는 입력 schema → 처리 → 출력 schema 형태.
검증 임계는 Stage가 정의 (마스터 §3.4 정합).
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class StageContext:
    """Stage 실행 시 공유 컨텍스트 (Pipeline 주입)."""
    supabase: Any | None = None
    config: dict[str, Any] | None = None


@dataclass
class StageOutput:
    """Stage 실행 결과. Pipeline이 다음 Stage 입력으로 전달."""
    data: Any                          # 출력 데이터 (schema 검증된)
    metrics: dict[str, Any]            # 검증 메트릭 (sample_accuracy, count, ...)
    sample_size: int = 0               # 검증 sample 크기
    notes: str | None = None


class Stage(ABC):
    """엔진의 단계 추상 클래스.
    
    각 Stage는:
    - stage_number: 1 / 2 / 3 (마스터 §3.4 임계 정합)
    - input_schema: 입력 데이터 schema (Pydantic)
    - output_schema: 출력 데이터 schema
    - validation_thresholds: Stage별 검증 임계
    - run(input, ctx) → StageOutput: 실제 처리
    """
    
    @property
    @abstractmethod
    def stage_number(self) -> int:
        """1 / 2 / 3 (validator.py SAMPLE_ACCURACY_THRESHOLDS key)."""
        ...
    
    @property
    @abstractmethod
    def stage_name(self) -> str:
        """'stage_1_splitter' / 'stage_2_decomposer' / 'stage_3_objectifier'."""
        ...
    
    @property
    def validation_thresholds(self) -> dict[str, float]:
        """Stage별 검증 임계 (validator.py 정합)."""
        from engine.validator import SAMPLE_ACCURACY_THRESHOLDS
        return {
            'sample_accuracy': SAMPLE_ACCURACY_THRESHOLDS[self.stage_number],
        }
    
    @abstractmethod
    def run(self, input_data: Any, ctx: StageContext) -> StageOutput:
        """단계 실행. 반환: StageOutput (data + metrics)."""
        ...
    
    @abstractmethod
    def measure_accuracy(self, output: StageOutput, ctx: StageContext) -> tuple[float, int]:
        """sample 정확도 측정. 반환: (accuracy, sample_size)."""
        ...
```

### 3.4 engine/pipeline.py — Pipeline 클래스 (단계+단계 흐름)

```python
"""TAI 법령엔진 v3.0 — Extraction Pipeline.

엔진의 본질: 단계+단계로 이어지는 흐름 + 검증 hook 내장.

각 Stage 종료 시:
  1. Stage가 출력 데이터 + 메트릭 생성
  2. Pipeline이 validator.py 자동 호출
  3. PASS → 다음 Stage 진입
  4. WARNING/FAIL → PipelineHaltError raise (마스터 §2.5 정합)

외부 script는 Pipeline.run()만 호출. 검증은 자동.
"""
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Any

from engine.stages.base import Stage, StageContext, StageOutput
from engine.validator import Validator, CheckResult

logger = logging.getLogger(__name__)


class PipelineHaltError(Exception):
    """Stage 검증 미통과 시 raise."""
    def __init__(self, stage: Stage, check: CheckResult):
        self.stage = stage
        self.check = check
        super().__init__(
            f"[{stage.stage_name}] 검증 {check.result_status} "
            f"(actual={check.actual_value}, threshold={check.threshold}). "
            f"마스터 §2.5: 데이터셋 truncate + 룰 수정 + 재실행 필요."
        )


@dataclass
class PipelineRun:
    """Pipeline 실행 결과 추적."""
    stage_outputs: list[StageOutput] = field(default_factory=list)
    check_results: list[CheckResult] = field(default_factory=list)
    halted_at: Stage | None = None


class TAIExtractionPipeline:
    """단계+단계 흐름 엔진."""
    
    def __init__(
        self,
        stages: list[Stage],
        validator: Validator,
        ctx: StageContext,
        halt_on_warning: bool = True,  # 마스터 §2.5 정합 (기본 엄격)
    ):
        self.stages = stages
        self.validator = validator
        self.ctx = ctx
        self.halt_on_warning = halt_on_warning
    
    def run(self, input_data: Any, *, only_stages: list[int] | None = None) -> PipelineRun:
        """엔진 실행. only_stages로 부분 실행 가능 (e.g., [2] = Stage 2만)."""
        run = PipelineRun()
        current = input_data
        
        for stage in self.stages:
            if only_stages is not None and stage.stage_number not in only_stages:
                continue
            
            logger.info(f"[Pipeline] Stage {stage.stage_number} ({stage.stage_name}) 진입")
            
            # 1. Stage 실행
            output = stage.run(current, self.ctx)
            run.stage_outputs.append(output)
            
            # 2. 검증 hook 자동 (엔진 내장)
            accuracy, sample_size = stage.measure_accuracy(output, self.ctx)
            check = Validator.evaluate_sample_accuracy(
                stage=stage.stage_number,
                accuracy=accuracy,
                sample_size=sample_size,
                check_name=f"{stage.stage_name}_sample_accuracy",
            )
            check.verified_by = f"pipeline_{stage.stage_name}"
            self.validator.log(check)  # verification_log INSERT
            run.check_results.append(check)
            
            # 3. 미통과 시 자동 정지
            halt_statuses = {'FAIL'}
            if self.halt_on_warning:
                halt_statuses.add('WARNING')
            
            if check.result_status in halt_statuses:
                run.halted_at = stage
                raise PipelineHaltError(stage, check)
            
            # 4. 다음 Stage 입력
            current = output.data
            logger.info(f"[Pipeline] Stage {stage.stage_number} PASS (accuracy={accuracy:.4f})")
        
        return run
```

### 3.5 engine/stages/stage_2.py — Stage 2 구현 (예시)

```python
"""Stage 2 — sub_type + if_pattern 분류 (151,751 row)."""
from __future__ import annotations
from typing import Any

from engine.stages.base import Stage, StageContext, StageOutput
from engine.schemas.stage_2 import Stage2Input, Stage2Output


class Stage2Decomposer(Stage):
    @property
    def stage_number(self) -> int:
        return 2
    
    @property
    def stage_name(self) -> str:
        return 'stage_2_decomposer'
    
    def run(self, input_data: Stage2Input, ctx: StageContext) -> StageOutput:
        """stage_1_clauses → stage_2_elements 분류."""
        # 기존 stage_2_decomposer.py 로직 활용
        from engine.stage_2_decomposer import decompose_clauses
        elements = decompose_clauses(input_data.clauses, ctx.supabase)
        
        return StageOutput(
            data=Stage2Output(elements=elements),
            metrics={
                'total_elements': len(elements),
                'classified_pct': sum(1 for e in elements if e.sub_type != 'UNCLASSIFIED') / len(elements),
            },
        )
    
    def measure_accuracy(self, output: StageOutput, ctx: StageContext) -> tuple[float, int]:
        """100조문 sample sub_type 정확도 측정 (PM 진단 정규식 카테고리화)."""
        from engine.sample_accuracy import compute_stage2_sample_accuracy
        return compute_stage2_sample_accuracy(ctx.supabase, sample_articles=100)
```

### 3.6 engine/schemas/stage_2.py — Stage 2 입출력 schema

```python
"""Stage 2 입출력 schema (Pydantic)."""
from pydantic import BaseModel
from typing import Any


class Stage2Input(BaseModel):
    """Stage 1 출력 = Stage 2 입력."""
    clauses: list[dict[str, Any]]  # stage_1_clauses row
    
    class Config:
        arbitrary_types_allowed = True


class Stage2Output(BaseModel):
    """Stage 2 출력."""
    elements: list[dict[str, Any]]  # stage_2_elements row
```

### 3.7 단위 테스트 (`tests/test_pipeline.py` 신규)

```python
"""Pipeline state machine 단위 테스트."""
import pytest
from engine.pipeline import TAIExtractionPipeline, PipelineHaltError
from engine.stages.base import Stage, StageContext, StageOutput
from engine.validator import Validator


class MockPassStage(Stage):
    """sample 정확도 0.95 mock."""
    @property
    def stage_number(self): return 2
    @property
    def stage_name(self): return 'mock_pass'
    def run(self, input_data, ctx):
        return StageOutput(data=input_data, metrics={})
    def measure_accuracy(self, output, ctx):
        return (0.95, 100)


class MockFailStage(Stage):
    """sample 정확도 0.80 mock."""
    @property
    def stage_number(self): return 2
    @property
    def stage_name(self): return 'mock_fail'
    def run(self, input_data, ctx):
        return StageOutput(data=input_data, metrics={})
    def measure_accuracy(self, output, ctx):
        return (0.80, 100)


def test_pipeline_pass():
    """모든 Stage PASS → 정상 완료."""
    pipeline = TAIExtractionPipeline(
        stages=[MockPassStage()],
        validator=Validator(supabase=None),
        ctx=StageContext(),
    )
    run = pipeline.run({})
    assert run.halted_at is None
    assert len(run.check_results) == 1
    assert run.check_results[0].result_status == 'PASS'


def test_pipeline_halt_on_fail():
    """Stage FAIL → PipelineHaltError raise + 다음 Stage 진입 X."""
    pipeline = TAIExtractionPipeline(
        stages=[MockFailStage(), MockPassStage()],
        validator=Validator(supabase=None),
        ctx=StageContext(),
    )
    with pytest.raises(PipelineHaltError) as exc_info:
        pipeline.run({})
    assert exc_info.value.stage.stage_name == 'mock_fail'
    assert exc_info.value.check.result_status == 'FAIL'
    # 다음 Stage 진입 확인 X (mock_pass 호출 안 됨)


def test_pipeline_halt_on_warning():
    """halt_on_warning=True 시 WARNING도 정지."""
    accuracy_warn = 0.87  # WARNING (≥ 0.85, < 0.90)
    # ... mock + 검증
```

### 3.8 검증 임계 (Phase 2.2-A)

| check | 임계 | status |
|---|---|---|
| Pipeline 단위 테스트 | 100% pass | PASS 필수 |
| Stage state machine | PASS/WARNING/FAIL 분기 정합 | PASS 필수 |
| validator.py 통합 | PipelineHaltError raise 검증 | PASS 필수 |
| 기존 테스트 회귀 | 0 fail (126 → 130+ passed) | PASS 필수 |
| coverage | ≥ 80% (Track A 정합) | PASS 필수 |
| validator.py 본문 변경 | 0 byte 변경 | PASS 필수 |

### 3.9 Phase 2.2-A PASS 미달 시

→ **즉시 정지 + PM 회신**. Phase 2.2-B 진입 금지.

---

## 4. Phase 2.2-B — Stage 2 룰 보강 (Pipeline 위에서)

### 4.1 본 단계의 본질

Pipeline 위에서 Stage 2의 룰 매칭 로직 보강. **DB 미반영, 코드 단위 검증만**.

### 4.2 subtype_rule_match.py 보강

| 보강 항목 | 본질 |
|---|---|
| TAIL_REGEX pattern_position 신규 | COMPOSITE strategy 정규식 매칭 |
| wildcard form (`*`) 처리 | NNG/NNB/NNP 통합 매칭 (또는 3룰 분리) |
| match_strategy 일관성 검증 | 룰 시안 정합 |

### 4.3 신규 룰 12+개 (코드 시안만)

(v1.1 §3.3 명세 동일 — ENUMERATION_LIST_INTRO 2 + REFERENCE_TO_ATTACHMENT 3 + REFERENCE_INVOCATION 1 + OBLIGATION 변형 2 + PROHIBITION 변형 2 + ENUMERATION_ITEM 3)

### 4.4 룰별 단위 테스트 (`tests/test_phase_22_rules.py`)

```python
def test_enumeration_list_intro_daum_gacho():
    """100건 sample, 정확도 ≥ 95%."""
    samples = load_samples('phase_22_samples/enumeration_list_intro.json')
    rule = load_rule_from_yaml('ENUMERATION_LIST_INTRO_DAUM_GACHO')
    
    correct = sum(1 for s in samples if match_rule(s['tokenization'], rule) == s['expected'])
    accuracy = correct / len(samples)
    
    assert accuracy >= 0.95, f"룰 정확도 {accuracy:.4f} < 0.95"
```

### 4.5 Stage 2 통합 단위 테스트

```python
def test_stage_2_with_new_rules():
    """Stage 2가 신규 룰을 정확히 적용."""
    stage = Stage2Decomposer()
    # mock 100조문 sample → Stage 2 처리 → 정확도 ≥ 90%
    pipeline = TAIExtractionPipeline(stages=[stage], validator=mock_validator, ctx=mock_ctx)
    run = pipeline.run(mock_input)
    assert run.check_results[0].result_status == 'PASS'
```

### 4.6 검증 임계

| check | 임계 |
|---|---|
| 신규 룰 12개 단위 테스트 | 룰별 ≥ 95% |
| Stage 2 통합 단위 테스트 | sample 정확도 ≥ 90% (Pipeline) |
| coverage | ≥ 80% |

### 4.7 Phase 2.2-B PASS 미달 시

→ **즉시 정지 + PM 회신**. Phase 2.2-C 진입 금지.

---

## 5. Phase 2.2-C — 데이터셋 처리 (Pipeline 실행)

### 5.1 본 단계의 본질

**Phase 2.2-A + 2.2-B PASS 확정 후에만 진입**. 데이터셋 폐기 + Pipeline 실행 (외부 script가 아닌 Pipeline.run() 호출).

### 5.2 작업 흐름

```
[1] 백업
[2] DB CHECK enum 확장 (28 enum)
[3] 룰 DB 적용 (UPDATE + INSERT)
[4] Phase 2.1 분류 폐기 (Phase 1 보전)
[5] Pipeline.run(only_stages=[2]) 실행 ★ 핵심
   - 내부: Stage 2 처리 → 검증 hook 자동 → PASS/FAIL 판정
[6] PASS 시 보고서 + commit + push
   FAIL 시 PipelineHaltError → Phase 2.2-A로 회귀
```

### 5.3 SQL 시안 (v1.1 §5.3 동일)

(생략 — v1.1 명세 §5.3 그대로 활용)

### 5.4 Pipeline 실행 (`scripts/track_e_phase2_run.py` 보강)

```python
# scripts/track_e_phase2_run.py
def run_phase_22(...):
    sb = get_supabase()
    
    # 백업, CHECK enum, 룰 적용, Phase 2.1 폐기 (위 1-4)
    # ...
    
    # Pipeline 실행 ★ (외부 script가 아닌 엔진 내장 흐름)
    from engine.pipeline import TAIExtractionPipeline, PipelineHaltError
    from engine.stages.stage_2 import Stage2Decomposer
    from engine.validator import Validator
    from engine.stages.base import StageContext
    
    pipeline = TAIExtractionPipeline(
        stages=[Stage2Decomposer()],
        validator=Validator(supabase=sb),
        ctx=StageContext(supabase=sb),
        halt_on_warning=True,  # 마스터 §2.5 엄격
    )
    
    try:
        run = pipeline.run(input_data=None, only_stages=[2])
        # PASS 도달 (Pipeline이 검증 hook 자동 통과 확정)
        return run
    except PipelineHaltError as e:
        # FAIL/WARNING 시 자동 raise
        logger.error(f"Pipeline halted: {e}")
        # PM 회신 + Phase 2.2-A 회귀
        raise SystemExit(str(e))
```

### 5.5 검증 임계 (Pipeline 자동)

| check | 임계 (Pipeline 자동) |
|---|---|
| Stage 2 sample 정확도 | ≥ 90% (validator.py) |
| WARNING 시 | PipelineHaltError raise |
| FAIL 시 | PipelineHaltError raise |

→ **검증 hook 엔진 내장**. 외부 script가 검증 X (Pipeline이 자동).

### 5.6 Phase 2.2-C PASS 미달 시

→ **PipelineHaltError + 마스터 §2.5 정합 — Phase 2.2-A로 회귀**.

---

## 6. 임의판단 절대 금지

| 영역 | 금지 |
|---|---|
| LLM 호출 | 어떤 형태든 X |
| validator.py 본문 수정 | 0 byte 변경 (그대로 활용) |
| Pipeline 외부 검증 | 항상 Pipeline 내장 |
| Stage 외 단계 추가 | 본 명세 3 Stage만 |
| 임계 자의 변경 | 마스터 §3.4 정합만 |
| Phase 1 결과 변경 | 절대 X |
| 단계별 PASS 미달 시 다음 단계 | 절대 X |

---

## 7. 중단 트리거

1. 진입 점검 SQL 결과 명세와 다름
2. validator.py 본문 변경 발견
3. Phase 2.2-A 단위 테스트 FAIL
4. Phase 2.2-A coverage < 80%
5. Phase 2.2-B 룰별 정확도 < 95%
6. Phase 2.2-C Pipeline.run() PipelineHaltError
7. row 수 변동 (151,751 ≠)
8. Phase 1 분류 변경 발견

---

## 8. 본 명세 외 작업 절대 X

- ❌ Stage 3 진입
- ❌ v3.0 마스터 객체 결정
- ❌ Tier 2-4 본법 수집
- ❌ Track C v1.3
- ❌ Kiwi 사전 보강
- ❌ 6하원칙 보강
- ❌ 신규 sub_type 추가 (3개 외)
- ❌ Phase 1 변경
- ❌ validator.py 본문 수정
- ❌ Pipeline 외부 검증

---

## 9. 보고서 양식 (`Track_E_20260510_Phase2_2.md`)

```markdown
# [Track E] Phase 2.2 — 엔진 Pipeline 구조 + 룰 보강 + 데이터셋 처리

## 1. Phase 2.2-A 결과
### 1.1 신규 파일 (engine/pipeline.py / stages/ / schemas/)
### 1.2 Pipeline state machine 단위 테스트
### 1.3 PASS 확정 (130+ tests passed, coverage ≥ 80%)

## 2. Phase 2.2-B 결과
### 2.1 subtype_rule_match.py 보강
### 2.2 신규 룰 12개 단위 정확도 (룰별 ≥ 95%)
### 2.3 Stage 2 통합 단위 테스트 (≥ 90%)
### 2.4 PASS 확정

## 3. Phase 2.2-C 결과
### 3.1 백업 / CHECK enum 확장 / 룰 DB 적용 / Phase 2.1 폐기
### 3.2 Pipeline.run(only_stages=[2]) 실행 결과
### 3.3 sub_type 분포 변화
### 3.4 검증 hook 자동 결과 (Pipeline 내장)

## 4. 절대 원칙 점검
## 5. 다음 단계 권고 (Stage 3 진입 조건)
```

---

## 10. 환경 정보

| 항목 | 값 |
|---|---|
| 코드 base | `taiengineering/tai-api` `dev` |
| 신규 파일 | `engine/pipeline.py`, `engine/stages/`, `engine/schemas/`, `tests/test_pipeline.py`, `tests/test_phase_22_rules.py` |
| 보강 파일 | `engine/subtype_rule_match.py`, `scripts/track_e_phase2_run.py` |
| 변경 X | `engine/validator.py`, `engine/morpheme.py`, `engine/stage_*.py` (기존 모듈) |
| 마이그레이션 | `apply_migration` (name: `phase_2_2_subtype_enum_extension`) |
| 보고서 commit | `taiengineering/tai-admin` main, `docs/extraction/v3/log/Track_E_20260510_Phase2_2.md` |
| 코드 commit | `taiengineering/tai-api` `dev` |

---

**END — 엔진 Pipeline 구조 본질 (단계+단계 흐름 + 검증 hook 내장) + 룰 보강 + 데이터셋 처리 (사용자 본질 지적 정합).**
