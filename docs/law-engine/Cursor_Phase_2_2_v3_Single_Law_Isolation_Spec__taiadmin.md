# [Cursor 위탁 v3.0] Phase 2.2 v3.0 — 단일 법령 + 격리 분석 정정 반복 본질

**작성일**: 2026-05-10  
**작성자**: PM 창  
**위탁 대상**: Cursor (TAI Backend / Railway)  
**v3.0 정정**: 2026-05-10 — DB ground truth 직접 점검 결과 law_master = **768** (이전 잘못 표기 "1,322" → 별표 수). 처리 대상 = **704 법령** (stage_1_clauses 있는 법령).

**선행 base**:
- `PM_Validation_Report_20260510_User_11Step_Workflow.md` (검증 보고서, commit `2c9c7e02d12357c8...`)
- `tai-api` `dev` `b699218` (Pipeline + sample_accuracy Ground Truth)

**선행 폐기**:
- v1.0 / v1.1 / v1.2 / v1.2-Patch / Track A P3 v1.0 / v1.1 명세 모두 폐기 (검증 보고서 §4.3)

---

## 0. 본 명세의 본질

### 0.1 사용자 본질 11단계 (검증 보고서 §1)

본 명세는 **사용자 본질 11단계 누적의 작업 흐름 정합**:

```
[1] 단일 법령 선택
[2] Track 1부터 진행
[3] 파싱
[4] 문제 발견 (검증엔진)
[5] 격리 (콩과 팥 골라내기)
[6] 격리 부분 분석
[7] 파싱 개선 (룰 정정 / 신규 룰)
[8] 재파싱 (격리 row만)
[9] 검증엔진 PASS 도달
[10] 회귀 검증
[다음 법령] 같은 흐름 반복
```

### 0.2 본 PM v1.x 명세 본질 한계 (검증 보고서 §4.3)

| 명세 | 본질 한계 |
|---|---|
| v1.0 | 작업 순서 누락 |
| v1.1 | 엔진 구조 누락 |
| v1.2 | **전체 폐기 본질 (콩과 팥 모두 버림)** |
| v1.2-Patch | sample_accuracy Ground Truth ✅ + 폐기 본질 ⚠️ |
| Track A P3 v1.0 | 법령 단위 ✅ + 격리 본질 X |
| Track A P3 v1.1 | fallback 통계 한계 |

### 0.3 v3.0 본질 (사용자 본질 정합)

**핵심**: 콩과 팥 골라내기 = FP만 격리, TP 보전.

```
Phase 2.1 분류 결과:
  ├ TP ~68,685 row (검증된 데이터) → 보전 ★
  ├ FP ~6,633 row (격리 대상) → is_isolated=true
  └ UC 68,130 row → 분류 시도 (신규 룰 적용)

→ 격리 row만 재파싱 + 검증된 row 변동 X
```

### 0.4 v3.0 정정 본질 (DB ground truth 재검증, 2026-05-10)

본 PM 14번째 본질 학습 — DB ground truth 직접 점검 + 명세 정정:

| 항목 | 이전 명세 (잘못) | 정정 (DB 실측) |
|---|---|---|
| law 수 | "1,322" (별표 수 잘못 인용) | **law_master = 768** |
| 처리 대상 | 1,322 모두 | **704** (stage_1_clauses 있는 법령) |

→ 본 PM의 v1.1 강제 ("진입 필터 패스, 1,322 모두 처리") 정정: **704 법령 모두 처리**.

---

## 1. 절대 원칙

| 원칙 | 본 명세 적용 |
|---|---|
| ① LLM X | Kiwi + 정규식 + DB 빈도만 |
| ② 법령 보전 | source_text 변경 X |
| ③ 누락 0건 | 151,751 row 변동 X |
| ④ 100% 매핑 | UPDATE만 (격리 row + 신규 룰 INSERT) |
| ⑤ **오염 = 부분 폐기** (사용자 본질 10) | **격리 row만 UC + TP 보전** |
| ⑥ 검증 부담 0 | Pipeline 자동 + 검증엔진 자동 |
| ⑦ Ground Truth 우선 | DB 직접 점검 |
| ⑧ DB가 ground truth | 진입 점검 SQL |

### 1.1 변경 X (강제)

| 영역 | 강제 |
|---|---|
| `engine/validator.py` 본문 | 0 byte (MD5 동일) |
| `engine/pipeline.py` 시그니처 | 호환 (kwarg 추가만) |
| `engine/sample_accuracy.py` Ground Truth | 보전 (b699218) |
| Phase 1 분류 결과 (5종) | 절대 변동 X |
| **TP row** (검증된 데이터) | 절대 변동 X |
| 진입 필터 (필요 법령 파악) | **패스** (사용자 결정 Q1, **704 법령** 모두 처리) |

---

## 2. 작업 환경

| 항목 | 값 |
|---|---|
| Supabase | `vwlahtguyggrhvslabax` |
| 코드 base | `tai-api` `dev` `b699218` (현재 Cursor 작업 commit으로 갱신) |
| 보강 파일 | `engine/pipeline.py`, `engine/stages/`, `engine/sample_accuracy.py`, `engine/iterator.py` (신규), `scripts/track_e_phase2_run.py` |
| 변경 X | `validator.py`, `subtype_rule_match.py`, `morpheme.py` |
| 보고서 | `tai-admin` main `docs/extraction/v3/log/Track_E_20260510_Phase2_2_v3.md` |

### 2.1 진입 점검 SQL (정정)

```sql
SELECT 
  (SELECT COUNT(*) FROM stage_2_elements) AS total,         -- 151,751
  (SELECT COUNT(*) FROM stage_2_elements WHERE sub_type='UNCLASSIFIED') AS uc,  -- 68,130
  (SELECT COUNT(*) FROM rule_classify_subtype WHERE enabled=true) AS rules,    -- 34
  (SELECT COUNT(*) FROM law_master) AS laws,                -- 768 (정정)
  (SELECT COUNT(DISTINCT la.law_id) FROM law_article la 
   JOIN law_article_part lap ON lap.article_id=la.id 
   JOIN stage_1_clauses s1 ON s1.part_id=lap.id) AS laws_with_clauses;  -- 704 (Phase 2 처리 대상)
```

→ 결과 다르면 정지 + PM 회신.

---

## 3. v3.0 본질 — DB 스키마 보강 (격리 본질)

### 3.1 stage_2_elements 컬럼 추가

```sql
-- 마이그레이션: phase_2_2_v3_isolation_columns
ALTER TABLE stage_2_elements 
  ADD COLUMN IF NOT EXISTS is_isolated boolean NOT NULL DEFAULT false,
  ADD COLUMN IF NOT EXISTS isolation_reason text NULL,
  ADD COLUMN IF NOT EXISTS isolated_at timestamptz NULL;

CREATE INDEX IF NOT EXISTS idx_stage_2_elements_isolated 
  ON stage_2_elements(is_isolated) WHERE is_isolated = true;

-- isolation_reason CHECK (열거형 확장 가능)
ALTER TABLE stage_2_elements 
  ADD CONSTRAINT stage_2_elements_isolation_reason_check
  CHECK (
    isolation_reason IS NULL OR 
    isolation_reason IN (
      'FP_AS_본다_보조_룰',           -- AS_본다_WA/GWA/TTOHAN_GATDA
      'FP_OBLIGATION_DETAIL_GWAN_SAHANG',  -- 관한 사항
      'FP_DELEGATION_ETRAHADA_별표',  -- 별표/별지 인용
      'FP_PROHIBITION_NOT_DOEN',     -- 적용하지 아니한다 (EXEMPTION 본질)
      'FP_WEAK_JUNYONG_HADA',        -- 준용한다 (REFERENCE_INVOCATION 본질)
      'FP_OTHER',                    -- 기타 PM 진단
      'WARNING_LOW_ACCURACY',        -- 법령 단위 정확도 미달
      'MANUAL_REVIEW'                -- 수동 검토 요청
    )
  );
```

### 3.2 백업

```sql
CREATE TABLE stage_2_elements_backup_20260510_pre_phase2_2_v3 AS 
  SELECT * FROM stage_2_elements;
CREATE TABLE rule_classify_subtype_backup_20260510_pre_phase2_2_v3 AS 
  SELECT * FROM rule_classify_subtype;
```

---

## 4. v3.0 본질 — engine 보강

(이전 §4 동일 — Cursor 작업 commit `b699218` 기반 보강 + iterator.py 신규)

---

## 5. 운영 흐름

### 5.1 진입 점검 + 백업 (정정)

```bash
railway run python3 scripts/track_e_phase2_run.py --phase22-v3 --only checks
# 결과 점검 (정정): 151,751 / UC 68,130 / 34 active rules / 768 laws / 704 laws_with_clauses
```

### 5.2 마이그레이션

```bash
railway run python3 scripts/track_e_phase2_run.py --phase22-v3 --only migration
# is_isolated boolean + isolation_reason text 추가 + 백업
```

### 5.3 단일 법령 순회 (사용자 본질 정합)

```bash
railway run python3 scripts/track_e_phase2_run.py --phase22-v3 --iterate \
  --order ascending_size \
  --max-iterations-per-law 5 \
  --regression-window 10

# 자동 진행:
# 1. 작은 법령부터 (704 법령 처리 대상)
# 2. 각 법령 Pipeline.run(law_id=N)
# 3. PASS → 다음 법령
# 4. WARNING/FAIL → FP 격리 (is_isolated=true) → 재시도
# 5. max_iterations 초과 → 정지 + PM 회신 (룰 정정 트리거)
# 6. 회귀 검증 (10개 법령마다)
```

### 5.4 PM 회신 트리거 (FAIL 시)

```python
# 콘솔 출력 예시
[Iterator HALT] law_id=12345 iterations=5 final_status=FAIL_HALT
  Final accuracy: 0.7823 (< 0.90)
  Isolated rows: 47
  Isolation reasons:
    FP_AS_본다_보조_룰: 12
    FP_OBLIGATION_DETAIL_GWAN_SAHANG: 8
    WARNING_LOW_ACCURACY: 27
  
  Next action (PM 결정):
    1. 격리 row 분석 → 신규 룰 INSERT → 재실행
    2. 룰 정정 (UPDATE) → 재실행
    3. 사용자 회신 → v3.1 명세
```

---

## 6. 검증 임계 (PASS 기준)

| check | 임계 |
|---|---|
| 단위 테스트 | 100% pass (Cursor 보고: 329 passed) |
| Pipeline 인터페이스 호환 | 기존 시그니처 미파괴 |
| validator.py 0 byte | 강제 |
| `is_isolated` 컬럼 마이그레이션 | PASS |
| 단일 법령 정확도 (validator.py) | ≥ 90% |
| 회귀 검증 | 이전 PASS 법령 변동 X |
| TP row 보전 | is_isolated=false인 row의 sub_type 변동 X |
| Phase 1 보전 (5종) | 절대 X |

---

## 7. 임의판단 절대 금지

| 영역 | 금지 |
|---|---|
| LLM 호출 | X |
| validator.py 본문 변경 | 0 byte |
| Pipeline 시그니처 호환 깨짐 | X |
| TP row 변동 | 절대 X (검증된 데이터 보전) |
| Phase 1 결과 변동 | 절대 X |
| 자동 룰 정정 | X (PM 회신 트리거만) |
| max_iterations 우회 | X |
| 회귀 미실시 강제 진행 | X |

---

## 8. 중단 트리거

1. 진입 점검 SQL 결과 명세와 다름 (laws ≠ 768 또는 laws_with_clauses ≠ 704)
2. validator.py 본문 변경 발견
3. 마이그레이션 실패
4. row 수 변동 (151,751 ≠)
5. TP row 변동 발견
6. Phase 1 분류 변경 발견
7. 단일 법령 max_iterations 초과 (5)
8. 회귀 검증 FAIL

---

## 9. 본 명세 외 작업 X

- Stage 3 진입
- v3.0 마스터 객체 결정
- Tier 2-4 본법 수집
- Track C v1.3 dict 보강
- Kiwi 사전 보강
- 6하원칙 보강
- 자동 룰 정정 (PM 회신만)
- validator.py 본문 수정

---

## 10. 보고서 양식 (`Track_E_20260510_Phase2_2_v3.md`)

(이전 §10 동일)

---

## 11. 환경 정보

| 항목 | 값 |
|---|---|
| 코드 base | `tai-api` `dev` (Cursor v3.0 작업 commit, 329 passed) |
| 신규 파일 | `engine/iterator.py`, `tests/test_iterator.py` |
| 보강 파일 | `engine/pipeline.py`, `engine/stages/base.py`, `engine/stages/stage_2.py`, `engine/sample_accuracy.py`, `scripts/track_e_phase2_run.py` |
| 변경 X | `validator.py`, `subtype_rule_match.py`, `morpheme.py` |
| 마이그레이션 | `apply_migration` (name: `phase_2_2_v3_isolation_columns`) |
| 보고서 | `tai-admin` main `docs/extraction/v3/log/Track_E_20260510_Phase2_2_v3.md` |
| 코드 commit | `tai-api` `dev` |

---

**END — 사용자 본질 11단계 정합: 단일 법령 (768 / Phase 2 처리 대상 704) + 트랙 1부터 + 격리 분석 정정 반복 + TP 보전 (콩과 팥 골라내기) + 검증엔진 자동.**
