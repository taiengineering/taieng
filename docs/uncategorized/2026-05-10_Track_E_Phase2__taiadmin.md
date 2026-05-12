# Track E — Stage 1/2 Phase 2 실행 보고

**실행일**: 2026-05-10  
**환경**: Railway `railway run`, Supabase `vwlahtguyggrhvslabax`  
**명세**: `docs/extraction/v3/log/Cursor_Stage_1_2_Phase_2_Spec.md` (동일 내용: `docs/extraction/Cursor_Stage_1_2_Phase_2_Spec.md`)

---

## 1. 요약

| 항목 | 결과 |
|---|---|
| Stage 1 메타 (Kiwi `tokenization_json`, `split_rule_id`, `char_start`/`char_end`) | 전 행 처리, 토큰화 NULL **0%** |
| Phase 1 분류 보전 | 백업 조인 검증 **덮어쓰기 0건** |
| Stage 2 UNCLASSIFIED 정밀 분류 | 추가 매칭 **322건** (143,542 → 143,220 UNCLASSIFIED) |
| 분류율 (`sub_type != UNCLASSIFIED`) | **약 5.62%** (8,531 / 151,751) |
| 명세 목표 분류율 **≥70%** / 중단 **<60%** | **목표 미달** (FAIL) |
| `verification_log` | **6행 INSERT 완료** (`--only log`, 분류 지표는 FAIL로 기록) |

---

## 2. 수행 작업

1. **백업 테이블**: `stage_1_clauses_backup_20260510_pre_phase2`, `stage_2_elements_backup_20260510_pre_phase2` (행 수 원본과 일치).
2. **Stage 1**: 배치 UPDATE로 형태소·오프셋·분할 규칙 메타 보강.
3. **Stage 2**: `rule_classify_subtype`만 사용, **UNCLASSIFIED**만 `priority` 오름차순 첫 매칭으로 갱신 (Phase 1 분류 행 미변경).
4. **6하원칙**: 분류된 행에 대해 휴리스틱으로 NULL 컬럼만 채움.
5. **검증 SQL**: §5.7 지표 산출.
6. **`verification_log`**: 자동 훅 6건 (분류율·6하·토큰화 등).

---

## 3. 스크립트·코드 위치 (`tai-api`)

- `scripts/track_e_phase2_run.py` — 백업, Stage 1/2, six_w, 검증, `verification_log`
- `engine/subtype_rule_match.py` — COMPOSITE / HEAD_TOKEN / TAIL_POS 매칭
- `engine/six_w_heuristic.py` — executor·recipient·what·when·where·how·condition 휴리스틱

실행 예:

```bash
cd tai-api && railway run python3 scripts/track_e_phase2_run.py [--only checks|backup|stage1|stage2|sixw|verify|log|all] [--limit N]
```

- `--only log`: 지표 산출 후 **`verification_log`만 삽입** (분류율이 60% 미만이어도 종료 코드 0).
- `--only verify` 또는 `--only all`: 명세 §8에 따라 분류율 **<60%** 등이면 **프로세스 중단** (`SystemExit`).

---

## 4. 목표 미달 원인 (분석)

DB의 **TAIL_POS** 등 패턴이 Kiwi 실제 출력과 자주 불일치함.

- 예: 룰은 `하/VV` + `ㄴ다/EF` 형태를 가정하나, Kiwi는 `하/XSV`, `처하/VV`, 어간 `ᆫ다/EF` 등으로 분석되어 **문자열·태그 정합이 깨짐**.
- 명세 **§9**: **`rule_classify_subtype`에 임의 신규 룰 추가 금지** → 패턴 정합은 **PM·DB에서 기존 룰 데이터 조정**(태그·형태 완화 또는 Kiwi 출력 기준 재설계)이 필요할 가능성이 큼.

---

## 5. PM 후속 권고

1. **분류율 목표 재합의**: 정밀 분류 전략을 Kiwi 출력과 정렬할지, 룰 매칭 로직을 태그·형태 변형 허용으로 확장할지(PM 승인 하에 코드 변경) 결정.
2. **`rule_classify_subtype` 데이터**: `TAIL_POS` / `HEAD_TOKEN` 패턴을 실제 Kiwi 샘플 분포에 맞게 조정하는 작업과 병행 검토.
3. Stage 3 등 후속 트랙은 본 Phase 2 분류율과 무관하게 진행할지 여부는 마스터 우선순위에 따름.

---

## 6. 수치 스냅샷 (실행 시점 DB)

| 지표 | 값 |
|---|---|
| `stage_1_clauses` / `stage_2_elements` 행 수 | 각 151,751 |
| `tokenization_json` NULL 비율 | 0% |
| `classified_pct` | 약 **5.62%** |
| UNCLASSIFIED 잔여 | **143,220** |
| Phase 2 추가 분류 | **322** 건 |

---

*본 보고는 LLM 분류 없이 Kiwi·정규식·DB 룰만 사용한 실행 결과이다.*
