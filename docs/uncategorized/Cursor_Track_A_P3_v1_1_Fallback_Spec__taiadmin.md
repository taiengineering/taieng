# [Cursor 위탁] Track A P3 v1.1 — Pipeline 단위 fallback 본질 보강

**작성일**: 2026-05-10  
**작성자**: PM 창  
**위탁 대상**: Cursor (TAI Backend / Railway)  
**선행**:
- `Cursor_Track_A_P3_Pipeline_Iterator_Spec.md` v1.0 (commit `098d29a4dfb1b1094...`) — 법령 단위만 정의

**v1.0 → v1.1 본질 변경**: 단위 fallback 메커니즘 추가 (사용자 본질 지적 정합)

---

## 0. 본 보강의 본질

### 0.1 사용자 본질 지적 (v1.0 P3 한계)

> "이 방식으로 안되면 더 작은 단위로 법령 > 보다 작은 단위로 진행하는 방식."

### 0.2 v1.0 P3의 한계

| 영역 | v1.0 (법령 단위만) | 한계 |
|---|---|---|
| 단위 | law_id만 | 법령 단위 평균 115 row → FAIL 시 어느 룰이 어디서 X 식별 어려움 |
| FAIL 처리 | halt_on_first_fail → SystemExit | 정정 단위 큼 (룰 본질 정밀 분석 어려움) |
| fallback X | - | 법령 내부 다양 패턴 분석 X |

### 0.3 v1.1 본질 (단위 fallback 자동)

```
법령 단위 FAIL → 조 단위 fallback → 항 단위 fallback → 의미절 단위 (가장 작은)
```

→ **가장 작은 단위 (의미절 = 1 row) 도달 시 직접 분석 + 룰 본질 정정 + 단위 ↑ 회귀**.

### 0.4 v1.0 보전 + v1.1 추가

v1.0 명세 그대로 보전. **추가만** (호환):
- Pipeline.run() 인자에 article_id / part_id / clause_id 추가
- StageContext에 article_id / part_id / clause_id 추가
- compute_stage2_sample_accuracy(article_id / part_id / clause_id) kwarg 추가
- Iterator.iterate_with_fallback() 메서드 추가

---

## 1. 절대 원칙 (v1.0 동일)

| 영역 | 변경 X (강제) |
|---|---|
| validator.py 본문 | 0 byte (MD5 동일) |
| Pipeline 시그니처 호환 | 기존 미파괴 (kwarg만 추가) |
| Stage 추상 시그니처 | 호환 |
| Phase 1 / 2.1 / 2.2 결과 | 변경 X |

---

## 2. v1.1 추가 본질

### 2.1 engine/stages/base.py 보강 (v1.0 위에서)

```python
@dataclass
class StageContext:
    supabase: Any | None = None
    config: dict[str, Any] | None = None
    # v1.0 (보전)
    law_id: int | None = None
    law_batch: list[int] | None = None
    # v1.1 (신규)
    article_id: int | None = None      # ★ 조 단위
    part_id: int | None = None         # ★ 항/호 단위
    clause_id: int | None = None       # ★ 의미절 단위 (가장 작은)
```

### 2.2 engine/pipeline.py 보강 (v1.0 위에서)

```python
class TAIExtractionPipeline:
    def run(
        self,
        input_data: Any,
        *,
        only_stages: list[int] | None = None,
        # v1.0 (보전)
        law_id: int | None = None,
        law_batch: list[int] | None = None,
        # v1.1 (신규)
        article_id: int | None = None,
        part_id: int | None = None,
        clause_id: int | None = None,
    ) -> PipelineRun:
        # ctx에 단위 정보 주입 (가장 작은 단위 우선)
        if clause_id is not None:
            self.ctx.clause_id = clause_id
        elif part_id is not None:
            self.ctx.part_id = part_id
        elif article_id is not None:
            self.ctx.article_id = article_id
        elif law_id is not None:
            self.ctx.law_id = law_id
        elif law_batch is not None:
            self.ctx.law_batch = law_batch
        
        # 기존 단계+단계 흐름 그대로
        ...
```

### 2.3 engine/sample_accuracy.py 보강

```python
def compute_stage2_sample_accuracy(
    supabase,
    *,
    sample_size: int = DEFAULT_SAMPLE_ARTICLES,
    seed: int | None = None,
    # v1.0
    law_id: int | None = None,
    law_batch: list[int] | None = None,
    # v1.1
    article_id: int | None = None,
    part_id: int | None = None,
    clause_id: int | None = None,
) -> tuple[float, int]:
    """단위별 정확도 측정. 가장 작은 단위 우선."""
    rows = _fetch_sample_rows(
        supabase,
        sample_articles=sample_size,
        clause_id=clause_id,    # ★ 가장 작은
        part_id=part_id,
        article_id=article_id,
        law_id=law_id,
        law_batch=law_batch,
    )
    # 이하 _verify_row 카테고리화 동일
```

### 2.4 _fetch_sample_rows 보강 (단위별 SQL)

```python
def _fetch_sample_rows(
    supabase,
    *,
    sample_articles: int,
    clause_id: int | None = None,
    part_id: int | None = None,
    article_id: int | None = None,
    law_id: int | None = None,
    law_batch: list[int] | None = None,
) -> list[dict]:
    """단위별 SQL — 가장 작은 단위 우선."""
    if clause_id is not None:
        # 의미절 단위 — 1 row만
        sql = """
        SELECT s2.sub_type, s1.source_text
        FROM stage_2_elements s2
        JOIN stage_1_clauses s1 ON s1.id = s2.clause_id
        WHERE s2.clause_id = %s
        """
        params = (clause_id,)
    elif part_id is not None:
        # 항/호 단위
        sql = """
        SELECT s2.sub_type, s1.source_text
        FROM stage_2_elements s2
        JOIN stage_1_clauses s1 ON s1.id = s2.clause_id
        WHERE s1.part_id = %s
        """
        params = (part_id,)
    elif article_id is not None:
        # 조 단위
        sql = """
        SELECT s2.sub_type, s1.source_text
        FROM stage_2_elements s2
        JOIN stage_1_clauses s1 ON s1.id = s2.clause_id
        JOIN law_article_part lap ON lap.id = s1.part_id
        WHERE lap.article_id = %s
        """
        params = (article_id,)
    elif law_id is not None:
        # 법령 단위 (v1.0 동일)
        ...
    else:
        # 전체 random (v1.0 동일)
        ...
```

### 2.5 Stage2Decomposer 보강

```python
class Stage2Decomposer(Stage):
    def run(self, input_data, ctx):
        # 단위별 fetch (가장 작은 단위 우선)
        if ctx.clause_id is not None:
            clauses = fetch_clause_by_id(ctx.supabase, ctx.clause_id)
        elif ctx.part_id is not None:
            clauses = fetch_clauses_by_part_id(ctx.supabase, ctx.part_id)
        elif ctx.article_id is not None:
            clauses = fetch_clauses_by_article_id(ctx.supabase, ctx.article_id)
        elif ctx.law_id is not None:
            clauses = fetch_clauses_by_law_id(ctx.supabase, ctx.law_id)
        elif ctx.law_batch:
            clauses = fetch_clauses_by_law_batch(ctx.supabase, ctx.law_batch)
        else:
            clauses = input_data.clauses or fetch_all_clauses(ctx.supabase)
        
        elements = decompose_clauses(clauses, ctx.supabase)
        return StageOutput(data=Stage2Output(elements=elements), metrics={...})
    
    def measure_accuracy(self, output, ctx):
        from engine.sample_accuracy import compute_stage2_sample_accuracy
        return compute_stage2_sample_accuracy(
            ctx.supabase,
            clause_id=ctx.clause_id,
            part_id=ctx.part_id,
            article_id=ctx.article_id,
            law_id=ctx.law_id,
            law_batch=ctx.law_batch,
        )
```

---

## 3. PipelineIterator 보강 (자동 fallback)

### 3.1 engine/iterator.py 보강 (v1.0 위에서)

```python
@dataclass
class FallbackResult:
    """단위 fallback 추적."""
    unit: str  # 'law' / 'article' / 'part' / 'clause'
    unit_id: int
    status: str  # 'PASS' / 'FAIL'
    accuracy: float | None = None
    error: str | None = None


@dataclass
class FallbackRun:
    """Iterator with fallback 결과."""
    fallback_traces: list[FallbackResult] = field(default_factory=list)
    final_failed_clauses: list[int] = field(default_factory=list)
    laws_processed: list[int] = field(default_factory=list)
    halted: bool = False


class PipelineIterator:
    # v1.0 메서드 보전 (iterate)
    
    def iterate_with_fallback(
        self,
        *,
        only_stages: list[int] | None = None,
        max_fallback_depth: int = 3,  # law → article → part → clause
        halt_on_clause_fail: bool = True,  # 의미절 단위 FAIL 시 정지
    ) -> FallbackRun:
        """단위 자동 fallback (법령 → 조 → 항 → 의미절).
        
        FAIL 시 자동으로 더 작은 단위로 fallback.
        의미절 단위 (1 row) FAIL 시 정지 + 룰 정정 트리거.
        """
        run = FallbackRun()
        law_ids = self._fetch_law_order()
        
        for law_id in law_ids:
            result = self._try_unit(
                pipeline_kwargs={'law_id': law_id, 'only_stages': only_stages},
                unit='law', unit_id=law_id,
            )
            run.fallback_traces.append(result)
            
            if result.status == 'PASS':
                run.laws_processed.append(law_id)
                continue
            
            # fallback 1: 조 단위
            if max_fallback_depth >= 1:
                article_ids = self._fetch_articles_by_law(law_id)
                for article_id in article_ids:
                    a_result = self._try_unit(
                        pipeline_kwargs={'article_id': article_id, 'only_stages': only_stages},
                        unit='article', unit_id=article_id,
                    )
                    run.fallback_traces.append(a_result)
                    
                    if a_result.status == 'PASS':
                        continue
                    
                    # fallback 2: 항 단위
                    if max_fallback_depth >= 2:
                        part_ids = self._fetch_parts_by_article(article_id)
                        for part_id in part_ids:
                            p_result = self._try_unit(
                                pipeline_kwargs={'part_id': part_id, 'only_stages': only_stages},
                                unit='part', unit_id=part_id,
                            )
                            run.fallback_traces.append(p_result)
                            
                            if p_result.status == 'PASS':
                                continue
                            
                            # fallback 3: 의미절 단위 (가장 작은, 1 row)
                            if max_fallback_depth >= 3:
                                clause_ids = self._fetch_clauses_by_part(part_id)
                                for clause_id in clause_ids:
                                    c_result = self._try_unit(
                                        pipeline_kwargs={'clause_id': clause_id, 'only_stages': only_stages},
                                        unit='clause', unit_id=clause_id,
                                    )
                                    run.fallback_traces.append(c_result)
                                    
                                    if c_result.status == 'FAIL':
                                        run.final_failed_clauses.append(clause_id)
                                        if halt_on_clause_fail:
                                            run.halted = True
                                            return run
        return run
    
    def _try_unit(self, *, pipeline_kwargs: dict, unit: str, unit_id: int) -> FallbackResult:
        """단위별 Pipeline 실행 시도 → PASS/FAIL 결과."""
        try:
            pipeline_run = self.pipeline.run(input_data=None, **pipeline_kwargs)
            check = pipeline_run.check_results[-1] if pipeline_run.check_results else None
            return FallbackResult(
                unit=unit, unit_id=unit_id,
                status='PASS',
                accuracy=check.actual_value if check else None,
            )
        except PipelineHaltError as e:
            return FallbackResult(
                unit=unit, unit_id=unit_id,
                status='FAIL',
                accuracy=e.check.actual_value,
                error=str(e),
            )
    
    def _fetch_articles_by_law(self, law_id: int) -> list[int]:
        """법령 내 조 ID 목록."""
        ...
    
    def _fetch_parts_by_article(self, article_id: int) -> list[int]:
        """조 내 항/호 ID 목록."""
        ...
    
    def _fetch_clauses_by_part(self, part_id: int) -> list[int]:
        """항/호 내 의미절 ID 목록."""
        ...
```

---

## 4. CLI 옵션 보강 (scripts/track_e_phase2_run.py)

```bash
# v1.0 (보전)
--law-id <id>
--law-batch <ids>
--iterate
--regression-window <N>

# v1.1 신규
--article-id <id>            # 조 단위 직접
--part-id <id>               # 항/호 단위 직접
--clause-id <id>             # 의미절 단위 직접 (1 row)
--iterate-with-fallback      # 자동 fallback 모드
--max-fallback-depth <N>     # 1 (article) / 2 (part) / 3 (clause, 기본)
--halt-on-clause-fail        # 의미절 FAIL 시 정지 (기본 True)
```

---

## 5. 단위 테스트 보강 (`tests/test_iterator.py`)

```python
def test_iterate_with_fallback_law_pass():
    """법령 단위 PASS → fallback 안 함."""
    iterator = PipelineIterator(mock_pass_pipeline, mock_supabase)
    run = iterator.iterate_with_fallback(only_stages=[2])
    assert all(t.unit == 'law' for t in run.fallback_traces)
    assert all(t.status == 'PASS' for t in run.fallback_traces)

def test_iterate_with_fallback_law_fail_article_pass():
    """법령 FAIL → 조 단위 fallback → 모두 PASS."""
    # mock: 법령 1 FAIL, 조 1/2/3 PASS
    iterator = PipelineIterator(mock_law_fail_pipeline, mock_supabase)
    run = iterator.iterate_with_fallback(only_stages=[2])
    assert run.fallback_traces[0].unit == 'law'
    assert run.fallback_traces[0].status == 'FAIL'
    assert all(t.unit == 'article' and t.status == 'PASS' for t in run.fallback_traces[1:])

def test_iterate_with_fallback_clause_fail_halt():
    """의미절 단위 FAIL → 정지."""
    iterator = PipelineIterator(mock_all_fail_pipeline, mock_supabase, halt_on_clause_fail=True)
    run = iterator.iterate_with_fallback(only_stages=[2])
    assert run.halted is True
    assert len(run.final_failed_clauses) > 0

def test_pipeline_clause_id_filter():
    """Pipeline.run(clause_id=N)이 단일 row 처리."""
    pipeline = TAIExtractionPipeline(...)
    pipeline.run(input_data=None, clause_id=12345)
    assert pipeline.ctx.clause_id == 12345

def test_compute_accuracy_clause_id():
    """sample_accuracy(clause_id=N) → 1 row만."""
    accuracy, n = compute_stage2_sample_accuracy(mock_sb, clause_id=12345)
    assert n == 1
```

---

## 6. 검증 임계 (v1.1 PASS 기준)

| check | 임계 |
|---|---|
| 단위 테스트 (v1.0 + v1.1 보강) | 100% pass (170 → 180+) |
| Pipeline 인터페이스 호환 | 기존 시그니처 미파괴 |
| Stage 추상 시그니처 | 호환 |
| validator.py 0 byte | 강제 |
| coverage | ≥ 80% |
| fallback 단위 테스트 | law/article/part/clause 분기 정합 |

---

## 7. 운영 흐름 (Track A P3 v1.1 PASS 후)

### 7.1 자동 fallback 모드 (사용자 본질 지적 정합)

```bash
railway run python3 scripts/track_e_phase2_run.py --phase22 \
  --iterate-with-fallback \
  --max-fallback-depth 3 \
  --halt-on-clause-fail \
  --regression-window 10

# 자동 진행:
# 1. 법령 단위 시도 → PASS / FAIL
# 2. FAIL 법령 → 조 단위 fallback → PASS / FAIL
# 3. FAIL 조 → 항 단위 fallback
# 4. FAIL 항 → 의미절 단위 fallback (1 row)
# 5. 의미절 FAIL → 정지 + PM 회신 (어느 룰이 어느 row에서 X 정확 식별)
# 6. 룰 정정 후 재진행
```

### 7.2 결과 분석

```python
# FallbackRun 결과
print(f"PASS 법령: {len(run.laws_processed)}/{total_laws}")
print(f"FAIL trace 단위 분포:")
for trace in run.fallback_traces:
    if trace.status == 'FAIL':
        print(f"  {trace.unit}={trace.unit_id} accuracy={trace.accuracy:.4f}")
print(f"최종 FAIL 의미절: {len(run.final_failed_clauses)}")
# → PM이 의미절 1개씩 source_text + sub_type 직접 분석 → 룰 본질 정정
```

---

## 8. 임의판단 절대 금지 (v1.0 동일)

| 영역 | 금지 |
|---|---|
| LLM 호출 | X |
| validator.py 본문 변경 | 0 byte |
| Pipeline 시그니처 호환 깨짐 | 절대 X |
| Stage 추상 시그니처 변경 | 절대 X |
| max_fallback_depth 자의 변경 | 명세 정의대로만 (1/2/3) |
| halt_on_clause_fail 우회 | 절대 X |

---

## 9. 본 명세 외 작업 X (v1.0 동일)

- ❌ Stage 3 / v3.0 마스터 / Tier 2-4 / Track C v1.3
- ❌ Phase 1/2.1/2.2 결과 변경
- ❌ validator.py 본문 수정
- ❌ Pipeline 시그니처 변경 (호환 깨짐)

---

## 10. 보고서 양식 (`Track_A_P3_v1_1_Pipeline_Iterator_Fallback.md`)

```markdown
# [Track A P3 v1.1] Pipeline 단위 fallback 본질 보강

## 1. v1.0 → v1.1 변경
### 1.1 StageContext에 article_id / part_id / clause_id 추가
### 1.2 Pipeline.run() 인자 보강
### 1.3 sample_accuracy 단위별 측정
### 1.4 PipelineIterator.iterate_with_fallback 신규
### 1.5 CLI 옵션 추가

## 2. 단위 테스트 (180+ tests passed)

## 3. validator.py 0 byte 변경 확인 (MD5)

## 4. 운영 가이드 (자동 fallback 모드)
```

---

## 11. 환경 정보

| 항목 | 값 |
|---|---|
| 코드 base | `tai-api` `dev` (Track A P3 v1.0 PASS 후) |
| 보강 파일 | `engine/pipeline.py`, `engine/stages/base.py`, `engine/stages/stage_2.py`, `engine/sample_accuracy.py`, `engine/iterator.py`, `scripts/track_e_phase2_run.py`, `tests/test_iterator.py` |
| 변경 X | `validator.py`, `subtype_rule_match.py`, `morpheme.py` |
| 보고서 | `tai-admin` `docs/extraction/v3/log/Track_A_P3_v1_1_Pipeline_Iterator_Fallback.md` |

---

**END — 단위 자동 fallback 본질 (법령 → 조 → 항 → 의미절) — 사용자 본질 지적 정합. 가장 작은 단위 (의미절 1 row)에서 룰 본질 정정 가능.**
