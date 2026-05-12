# [Track E] Phase 2.2 — 엔진 Pipeline 구조 + 룰 보강 + 데이터셋 처리

**명세**: `Cursor_Phase_2_2_Pipeline_Engine_Spec_v1_2.md` (commit `5055de350f55f660b2bb2091a915797eac4f2db3`, tai-admin main)  
**Patch 명세**: `Cursor_Phase_2_2_Sample_Accuracy_Patch_v1_2.md` (commit `655b9d1d8018bee69939c789950a49e877b374f9`, tai-admin main)  
**코드 브랜치**: `taiengineering/tai-api` `dev`  
**작성일**: 2026-05-10 (Patch 보강 2026-05-10)  

---

## 1. Phase 2.2-A 결과

### 1.1 신규 파일

| 경로 | 설명 |
|------|------|
| `engine/pipeline.py` | `TAIExtractionPipeline`, `PipelineRun`, `PipelineHaltError`, `halt_exit` |
| `engine/sample_accuracy.py` | `compute_stage2_sample_accuracy` — **Ground Truth 정규식 카테고리화** (Patch v1.2, proxy 폐기) |
| `engine/stages/base.py` | `Stage` 추상, `StageContext`, `StageOutput` |
| `engine/stages/stage_1.py` | `Stage1Splitter` — `engine.stage_1_splitter` 래핑 |
| `engine/stages/stage_2.py` | `Stage2Decomposer` — `engine.stage_2_decomposer` 래핑 |
| `engine/stages/stage_3.py` | `Stage3Objectifier` — `engine.stage_3_objectifier` 래핑 |
| `engine/schemas/*.py` | Stage 1·2·3 Pydantic 입출력 |
| `tests/test_pipeline.py` | Pipeline state machine (PASS / WARNING / FAIL, `only_stages`) |
| `tests/test_phase_22_rules.py` | Phase 2.2 룰 시안 + 매처 보강 단위 테스트 |

### 1.2 Pipeline state machine

- **PASS**: 임계 이상 → 다음 단계 입력 전달  
- **WARNING / FAIL** (`halt_on_warning=True`): `PipelineHaltError` — 후속 Stage 미진입  
- **`only_stages=[n]`**: 지정 단계만 실행  

### 1.3 PASS 확정

- **테스트**: `tests/test_pipeline.py` + `tests/test_phase_22_rules.py` + `tests/test_sample_accuracy.py` + `tests/v3/*` 전체 통과 (Patch 후 **163** 이상)
- **`engine/validator.py`**: 본문 **변경 없음** (내장 `Validator.evaluate_sample_accuracy` / `log` 호출만)

---

## 2. Phase 2.2-B 결과

### 2.1 `subtype_rule_match.py` 보강

- **COMPOSITE**: `pattern_position` 이 `TAIL` / `TAIL_REGEX` 계열이면 원문 **끝 윈도**(200자)만 정규식 검색  
- **`TAIL_REGEX`**: 전략 추가 — 꼬리 구간 매칭  
- **TAIL_POS**: 패턴 요소 `*` / `**` → 해당 슬롯 형태소 **임의 형태** (태그는 유지)

### 2.2 신규 룰 단위 테스트

- `PHASE22_RULE_INSERTS` 기준 **8건** COMPOSITE/LAST_MEANINGFUL 긍정 샘플 + 꼬리 윈도·wildcard·`TAIL_REGEX` 테스트 (`tests/test_phase_22_rules.py`)

### 2.3 Stage 2 통합

- 파이프라인 없이도 룰 매칭 함수 단위로 검증. Stage 래퍼 연동 스모크는 `tests/test_pipeline.py::test_stage1_stage2_chain_smoke`

### 2.4 스키마

- `engine/phase_22_apply.apply_phase_22_schema`: `match_strategy` CHECK에 **`TAIL_REGEX`** 추가 (DB 마이그레이션 시 반영)

---

## 3. Phase 2.2-C 결과 (스크립트 연동)

### 3.1 `scripts/track_e_phase2_run.py`

- **`--phase22`** 분기 추가  
- **`--only`**: `checks` | `backup` | `rules` | `pipeline` | `all`  
  - `checks`: `run_entry_checks_phase22` (row 151,751 / UC 68,130 / 활성 룰 34 — 스냅샷 상수 `EXPECTED_PHASE22_RULES_SUB`)  
  - `backup`: `run_backup_phase22`  
  - `rules`: `apply_phase_22_schema` + `apply_phase_22_rule_changes`  
  - `pipeline`: `TAIExtractionPipeline` + `Stage2Decomposer` + 내장 검증 (`Stage2Input(clauses=[])` — 처리 생략, **샘플 정확도 hook만**)

### 3.2 운영 실행 예 (Patch 후 권장 순서)

```bash
# (a) 진입 점검만 — DB 변경 없음
cd tai-api && railway run python3 scripts/track_e_phase2_run.py --phase22 --only checks

# (b) 백업 → CHECK → 룰 → Pipeline 내장 검증
railway run python3 scripts/track_e_phase2_run.py --phase22 --only all
```

**실패 시**: `PipelineHaltError` → `halt_exit` → **SystemExit** (명세 §2.5). 본 저장소 Cursor 에이전트는 Railway 네트워크에 직접 접속하지 않음 — **운영 실행은 담당자가 Railway에서 수행** 후 로그·지표를 본 문서에 기재.

### 3.3 데이터셋·분포

- 본 보고서 시점 **원격 DB 미실행**. 배포 후 `checks` / `pipeline` 로그로 **sub_type 분포·검증 로그**를 채워 넣을 것.

---

## 4. 절대 원칙 점검

| 항목 | 상태 |
|------|------|
| `validator.py` 본문 변경 | 미변경 |
| Pipeline 외부 단독 검증 스크립트 | 금지 — Pipeline 내장 hook만 |
| Phase 1 분류 5종 | 코드 경로에서 변경 없음 |
| LLM | 미사용 |

---

## 5. Phase 2.2-Patch (sample_accuracy 본질 보강)

**명세**: `Cursor_Phase_2_2_Sample_Accuracy_Patch_v1_2.md`  

### 5.1 본질 변경

- **이전**: 룰 재적용 자기일관성 → deterministic 룰에서 **false PASS** 위험  
- **이후**: `CATEGORY_VERIFICATION_PATTERNS` 로 `source_text` 종결 패턴과 `stored sub_type` 정합 → **TP / FP / UC / WEAK / PHASE1_TP**  
- **보조 룰 FP 검출**: `AS_본다` + 「다음 각 호와 같다」→ **FP** (본질은 `ENUMERATION_LIST_INTRO` 등)  
- **`OBLIGATION_DETAIL_ITEM`** + 「관한 사항」→ **FP** (명세 단위 테스트)  
- **조회**: `DATABASE_URL` 있으면 `psycopg2`로 100 random `law_article` 기준 조인 샘플; 없거나 실패 시 Supabase embed fallback  

### 5.2 신규 테스트

- `tests/test_sample_accuracy.py`: `_verify_row`·`compute_stage2_sample_accuracy`·PM 진단 분포 **mock** (≈89.74% 재현)

### 5.3 변경 없음 (Patch 강제)

- `engine/validator.py`, `engine/pipeline.py`, `engine/stages/`, `engine/schemas/`, `engine/subtype_rule_match.py` — **미변경**

---

## 6. 다음 단계 권고

1. Railway에서 **§3.2 (a)(b)** 실행 후 Pipeline **PASS(≥90%)** 여부 확인  
2. **WARNING/FAIL** 시 PM 회신 → 룰·패턴 재설계 후 재실행  
3. **PASS** 확정 시 PM 창에서 DB ground truth 점검 → **Stage 3 진입** 결정  

---

**END**
