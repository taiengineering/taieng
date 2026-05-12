# Track E — Phase 2.2 v3 단일 법령 격리 분석 · 정정 반복

**작성일**: 2026-05-10  
**명세**: `Cursor_Phase_2_2_v3_Single_Law_Isolation_Spec.md` (tai-admin main; 진입 수치 정정 b4adf52a…)  
**코드**: `taiengineering/tai-api` `dev`

---

## 1. 요약

- **DB**: `stage_2_elements`에 `is_isolated`, `isolation_reason`, `isolated_at` + CHECK(8종 사유) + 부분 인덱스.
- **엔진**: `StageContext`에 `isolation_mode`, `exclude_isolated`; `Pipeline.run` kwarg 호환 보강.
- **Stage 2**: `isolation_mode=True`일 때 격리 clause만 재처리 (`fetch_isolated_clauses_by_law_id`).
- **sample_accuracy**: `exclude_isolated` — 정확도 샘플에서 격리 행 제외.
- **Phase22V3Iterator**: 법령당 최대 N회 반복 → FP만 `_verify_row` 기준 격리 마킹 → 재시도; 회귀(10법령 단위).
- **CLI**: `--phase22-v3`, `--only checks|migration|iterate|all`, `--max-iterations-per-law`, `--regression-window`(미지정 시 v3 iterate에서 기본 10).

---

## 1.1 진입 점검 수치 (PM ground truth, 명세 §2.1 정정)

| 항목 | 값 | 비고 |
|------|-----|------|
| `stage_2_elements` | 151,751 | 기존 Phase 2.2 점검과 동일 |
| UC | 68,130 | 동일 |
| 활성 sub_type 룰 | 34 | 동일 |
| **law_master** (`law` 행 수) | **768** | 구 명세 “1,322”는 별표(law_attachment) 오인용 |
| **laws_with_clauses** | **704** | `stage_1_clauses` 경유 DISTINCT `law_id` |
| Iterator 순회 집합 | `stage_2_elements` 조인 DISTINCT `law_id` | 통상 704과 일치; 불일치 시 스크립트가 WARNING 로그 |

---

## 2. 검증 원칙 (변경 없음)

| 항목 | 내용 |
|------|------|
| `validator.py` | 본문 0 byte 변경 |
| TP / Phase 1 5종 | 자동 업데이트 금지 — 격리는 FP만 |
| 룰 INSERT/UPDATE | 본 명세 범위 밖 — 격리 마킹만 자동 |

---

## 3. 마이그레이션

파일: `tai-api/supabase/migrations/20260510_phase_2_2_v3_isolation_columns.sql`

백업 테이블 (스크립트):  
`stage_2_elements_backup_20260510_pre_phase2_2_v3`,  
`rule_classify_subtype_backup_20260510_pre_phase2_2_v3`

---

## 4. 운영 명령

```bash
railway run python3 scripts/track_e_phase2_run.py --phase22-v3 --only checks

railway run python3 scripts/track_e_phase2_run.py --phase22-v3 --only migration

railway run python3 scripts/track_e_phase2_run.py --phase22-v3 --iterate \
  --order ascending_size --max-iterations-per-law 5 --regression-window 10
```

`--iterate` 플래그를 주면 `--only`가 `all`일 때도 순회 단계가 포함됩니다. `--only iterate`로 순회만 실행 가능합니다.

---

## 5. 단위 테스트

- `tests/test_iterator.py`: Phase22V3Iterator PASS / FAIL_HALT / 회귀 트리거, 격리 사유 맵.
- 기존 Pipeline·sample_accuracy 회귀 유지.

---

## 6. 알려진 제약

- `_isolate_fp_rows`: `DATABASE_URL`이 있으면 psycopg2 일괄 UPDATE; 없으면 Supabase 클라이언트 경로.
- 진입 점검: `EXPECTED_PHASE22_V3_LAW_MASTER = 768`, `EXPECTED_PHASE22_V3_LAWS_WITH_CLAUSES = 704` (배포 스냅샷 기준; 불일치 시 상수 조정).

---

**END**
