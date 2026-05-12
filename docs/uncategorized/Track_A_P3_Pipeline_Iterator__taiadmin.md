# [Track A P3] Pipeline law 단위 처리 본질 도입

**작성일**: 2026-05-10  
**명세**: `Cursor_Track_A_P3_Pipeline_Iterator_Spec.md`  
**코드 브랜치**: `taiengineering/tai-api` `dev`

---

## 1. 변경 사항

### 1.1 `engine/pipeline.py`

- `Pipeline.run(..., law_id=, law_batch=)` kwarg 추가 (기존 호출 호환).
- 실행 중 `StageContext`에 주입 후 `finally`에서 이전 값 복원.

### 1.2 `engine/stages/base.py`

- `StageContext`: `law_id`, `law_batch` 필드 추가 (기본 `None`).

### 1.3 `engine/stages/stage_2.py`

- `ctx.law_id` / `ctx.law_batch` 시 `clause_fetch` 기반 조항 로드.
- `measure_accuracy`에 `compute_stage2_sample_accuracy(..., law_id=, law_batch=)` 전달.

### 1.4 `engine/sample_accuracy.py`

- `compute_stage2_sample_accuracy` / `_fetch_sample_rows`에 law 스코프 kwarg (호환 유지).

### 1.5 `engine/clause_fetch.py`

- 법령 단위 조항 조회 헬퍼 (`fetch_clauses_by_law_id`, `fetch_clauses_by_law_batch`).

### 1.6 `engine/iterator.py` (신규)

- `PipelineIterator`: 순회 순서 `ascending_size` | `descending_size` | `random` | `sequential`.
- `regression_window` > 0 이고 `i > 0`, `i % 10 == 0`일 때 이전 N개 법령 `_regression_check`.
- `halt_on_first_fail`: 첫 `PipelineHaltError` 시 중단 (기본 `True`).

### 1.7 `scripts/track_e_phase2_run.py`

- `--law-id`, `--law-batch` (쉼표 구분), `--iterate`, `--order`, `--regression-window`, `--continue-after-fail`.
- `run_phase22_iterate()` — `--phase22 --only pipeline|all` 시 `--iterate` 분기.

### 1.8 부수 수정 (앱 로드)

- `routers/inspection_schedule.py`: `_next_planned_from`을 `services.inspection_sets_helpers`에서 import (수집 단계 import 오류 해결).

---

## 2. 단위 테스트

| 항목 | 내용 |
|------|------|
| 신규 | `tests/test_iterator.py` — 순회 PASS/FAIL, 회귀 트리거, `_fetch_law_order` 정렬/SQL 실패, `law_id` 주입·복원 |
| 보강 | `tests/test_sample_accuracy.py` — mock `_fetch_sample_rows` 시그니처에 `law_id` / `law_batch` |
| 회귀 | 기존 `test_pipeline.py`, `test_phase_22_rules.py` 등 유지 |

로컬 검증: `pytest tests/` **320 passed**, 1 skipped (전체 스위트 약 5.5분).

---

## 3. `validator.py` 변경 없음

- 본문 수정 **0 byte** (강제 원칙).
- 참고 MD5 (로컬 스냅샷): `e70c6ab92de11525299b0b4765062ec4`

---

## 4. 운영 가이드 (PASS 후 Phase 2.2 점진 처리)

```bash
# 진입 점검
railway run python3 scripts/track_e_phase2_run.py --phase22 --only checks

# 단일 법령
railway run python3 scripts/track_e_phase2_run.py --phase22 --only pipeline --law-id <id>

# 배치
railway run python3 scripts/track_e_phase2_run.py --phase22 --only pipeline --law-batch id1,id2

# 자동 순회 + 회귀 (작은 법령부터)
railway run python3 scripts/track_e_phase2_run.py --phase22 --only pipeline --iterate --order ascending_size --regression-window 10
```

---

## 5. Coverage 참고

`pytest tests/ --cov=engine` 기준 엔진 패키지 전체는 기존 모듈 분포로 **약 68%** 수준. 신규 `iterator.py`는 단위 테스트로 주요 분기(순서·회귀·SQL 실패)를 커버.

---

**END** — Track A P3 완료 시 Phase 2.2 점진 처리 모드 운영 결정 가능.
