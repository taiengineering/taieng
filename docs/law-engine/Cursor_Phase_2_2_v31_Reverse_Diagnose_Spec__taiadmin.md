# [Cursor 위탁 v3.1] Phase 2.2 v3.1 — 역순 검증 본질 (sub_type별 + 룰별 group sample)

**작성일**: 2026-05-10
**작성자**: PM 창
**위탁 대상**: Cursor (TAI Backend / Railway)
**선행 base**:
- `Cursor_Phase_2_2_v3_Single_Law_Isolation_Spec.md` (v3.0, commit `b4adf52a3dc8f692e...`)
- `tai-api` `dev` `90c994c` (PASS_STABLE 본질 보강 — 운영 PASS 정합)

**본질**: 사용자 본질 17번째 학습 — METHODOLOGY (5월 4일 9단계 방법론)의 **역순 검증 본질**을 본 운영에 보강. v3.0 운영 결과 (FP_OTHER 3,341건) 세분화.

---

## 0. 본 명세의 본질

### 0.1 사용자 본질 17번째 정합

> "역순 검증을 넣으면 더 완벽해지겠네요."

METHODOLOGY (5월 4일):
- 정순 (article → drafts) + **역순 (drafts → article, 환각 방지)**
- 본 운영 (v3.0)은 **부분 역순 동작** (sample_accuracy._verify_row, row 단위)
- 더 본질적 역순 = **sub_type별 / 룰별 group sample**

### 0.2 v3.0 운영 결과 + v3.1 보강 영역

**v3.0 운영 종합 결과** (`a1b2c3d...` 시점, 본 PM DB 직접 점검):
- 704/704 법령 PASS/PASS_STABLE
- 격리 10,214 row (FP만)
- TP 변동 0 row
- Phase 1 5종 100% 보전
- 회귀 검증 FAIL 0건

**격리 isolation_reason 분포**:
| reason | count | % |
|---|---|---|
| FP_OTHER | 3,341 | 32.71% ★ 세분화 영역 |
| FP_AS_본다_보조_룰 | 3,183 | 31.16% |
| FP_OBLIGATION_DETAIL_GWAN_SAHANG | 2,313 | 22.65% |
| FP_DELEGATION_ETRAHADA_별표 | 1,115 | 10.92% |
| FP_PROHIBITION_NOT_DOEN | 262 | 2.57% |

→ **FP_OTHER 3,341건** = `isolation_reason_for_fp_subtype` 매칭 X = 추가 세분화 본질.

### 0.3 v3.1 본질 보강

| 보강 | 본질 | 용도 |
|---|---|---|
| `compute_subtype_group_accuracy(sub_type)` | sub_type별 random 100건 → 정확도 | 어느 sub_type이 본질적 FP? |
| `compute_rule_accuracy(rule_name)` | 룰별 매칭 row 100건 → 정확도 | FP 룰 식별 → 룰 폐기 결정 |
| FP_OTHER 세분화 | isolation_reason_for_fp_subtype 보강 | 카테고리 정합성 |
| 진단 모드 CLI | `--phase22-v3 --diagnose ...` | 별도 진단 (운영 흐름 X) |

→ 본 운영 (Iterator) 영향 X. **별도 진단 도구**.

---

## 1. 절대 원칙

| 원칙 | 본 명세 적용 |
|---|---|
| ① LLM X | 정규식 + DB 빈도만 |
| ② 법령 보전 | source_text 변경 X |
| ③ 누락 0건 | row 변동 X (진단 read-only) |
| ④ 100% 매핑 | 진단 도구만 (UPDATE X 또는 isolation_reason 재할당만) |
| ⑤ 오염 = 부분 폐기 | 진단 결과로 룰 폐기 결정 (PM 회신) |
| ⑥ 검증 부담 0 | 자동 진단 + 표 출력 |
| ⑦ Ground Truth 우선 | _verify_row 기준 |
| ⑧ DB가 ground truth | DB 직접 조회 |

### 1.1 변경 X (강제)

| 영역 | 강제 |
|---|---|
| `engine/validator.py` 본문 | **0 byte (MD5 동일)** |
| `engine/iterator.py` 본문 | 변동 X (90c994c 보전) |
| `engine/pipeline.py` 본문 | 변동 X |
| `engine/stages/stage_2.py` | 변동 X (lazy init 보전) |
| 본 운영 흐름 (`--iterate`) | 변동 X |
| 본 운영 격리 결과 (`is_isolated`) | 변동 X (또는 isolation_reason 재할당만) |

---

## 2. 작업 환경

| 항목 | 값 |
|---|---|
| Supabase | `vwlahtguyggrhvslabax` |
| 코드 base | `tai-api` `dev` `90c994c` |
| 보강 파일 | `engine/sample_accuracy.py` (함수 추가), `scripts/track_e_phase2_run.py` (CLI 옵션) |
| 신규 파일 | `tests/test_diagnose.py` |
| 변경 X | `validator.py`, `iterator.py`, `pipeline.py`, `stages/`, `subtype_rule_match.py`, `morpheme.py` |
| 보고서 | `tai-admin/docs/extraction/v3/log/Track_E_20260510_Phase2_2_v31_Diagnose.md` (Cursor 작성) |

---

## 3. v3.1 본질 — 함수 신규

### 3.1 `engine/sample_accuracy.py` 함수 추가

```python
# 기존 함수 보전 (_verify_row, compute_stage2_sample_accuracy, ...)

def compute_subtype_group_accuracy(
    supabase,
    sub_type: str,
    *,
    sample_size: int = 100,
    seed: int | None = None,
    exclude_isolated: bool = False,
) -> dict[str, Any]:
    """sub_type 그룹 random sample 정확도 (역순 검증).

    예: compute_subtype_group_accuracy(sb, 'AS_본다', sample_size=100)
        → AS_본다 분류된 N건 (격리 포함/제외) 중 100건 random
        → _verify_row로 ground truth 카테고리화
        → {'sub_type': 'AS_본다', 'n': 100, 'tp': 5, 'fp': 95, 'weak': 0,
           'phase1_tp': 0, 'accuracy': 0.05, 'population_size': 3500}

    Returns:
        - sub_type: 입력 sub_type
        - n: random sample 크기 (요청 sample_size 또는 population_size 중 작은 값)
        - tp / fp / weak / phase1_tp: _verify_row verdict 분포
        - accuracy: (tp + phase1_tp) / n
        - population_size: 전체 sub_type=X row 수
    """
    # 1. population fetch (SELECT id, source_text WHERE sub_type=X [AND COALESCE(is_isolated,false)=false])
    # 2. random sample (seed=seed)
    # 3. _verify_row 카테고리화
    # 4. 집계 + 반환


def compute_rule_accuracy(
    supabase,
    rule_name: str,
    *,
    sample_size: int = 100,
    seed: int | None = None,
    exclude_isolated: bool = False,
) -> dict[str, Any]:
    """rule_name 그룹 random sample 정확도.

    예: compute_rule_accuracy(sb, 'AS_본다_WA_GATDA', sample_size=100)
        → 해당 룰 매칭 row N건 중 100건 random
        → ground truth verdict 분포 → 0% TP 식별 (룰 폐기 결정)

    Returns:
        - rule_name / n / tp / fp / weak / phase1_tp / accuracy / population_size
    """
    # applied_rules->>'sub_type_rule_name' = rule_name 조회


def diagnose_all_subtypes(
    supabase,
    *,
    sample_size: int = 100,
    seed: int | None = None,
) -> list[dict[str, Any]]:
    """모든 sub_type 진단 (가나다순) → 정확도 표."""
    # SELECT DISTINCT sub_type FROM stage_2_elements WHERE sub_type != 'UNCLASSIFIED'
    # 각 sub_type별 compute_subtype_group_accuracy 호출
    # accuracy 오름차순 정렬 (FP 다수 sub_type 식별 우선)


def diagnose_all_rules(
    supabase,
    *,
    sample_size: int = 100,
    seed: int | None = None,
) -> list[dict[str, Any]]:
    """모든 룰 진단 → 정확도 표.

    rule_classify_subtype.rule_name 기준 또는
    applied_rules->>'sub_type_rule_name' DISTINCT.
    """
```

### 3.2 `engine/iterator.py` `isolation_reason_for_fp_subtype` 보강

기존 (90c994c):
```python
def isolation_reason_for_fp_subtype(sub_type: str | None) -> str:
    s = sub_type or ""
    if s == "AS_본다":
        return "FP_AS_본다_보조_룰"
    if "OBLIGATION_DETAIL" in s or "GWAN" in s or "SAHANG" in s:
        return "FP_OBLIGATION_DETAIL_GWAN_SAHANG"
    # ...
    return "FP_OTHER"   # ← v3.0에서 3,341건 (32.71%) 미세분화
```

**v3.1 보강 본질**:
- 본 운영 결과 (PM DB 직접 점검) — FP_OTHER 3,341건 sub_type 분포 점검
- sub_type별 본질 카테고리 추가 → CHECK 제약 새 enum 추가 (apply_migration)
- 또는 기존 5 카테고리 매칭 패턴 확장

**작업 본질** (Cursor 위탁):
1. SQL: `SELECT sub_type, COUNT(*) FROM stage_2_elements WHERE is_isolated=true AND isolation_reason='FP_OTHER' GROUP BY sub_type` 직접 점검
2. Top sub_type별 본질 카테고리 결정 (PM 회신 또는 자체 결정)
3. CHECK 제약 enum 추가 (필요 시)
4. UPDATE: 기존 FP_OTHER row 재할당 (sub_type 기반)

### 3.3 CLI 옵션 추가 (`scripts/track_e_phase2_run.py`)

```python
# argparse 추가
parser.add_argument("--diagnose", action="store_true",
                    help="진단 모드 (sub_type별/룰별 정확도)")
parser.add_argument("--all-subtypes", action="store_true",
                    help="모든 sub_type 진단")
parser.add_argument("--all-rules", action="store_true",
                    help="모든 룰 진단")
parser.add_argument("--sub-type", type=str, default=None,
                    help="특정 sub_type 진단")
parser.add_argument("--rule-name", type=str, default=None,
                    help="특정 룰 진단")
parser.add_argument("--diagnose-sample-size", type=int, default=100,
                    help="진단 sample size (기본 100)")
parser.add_argument("--diagnose-seed", type=int, default=None,
                    help="random seed (재현 가능)")

# main() 분기
if args.diagnose:
    if args.all_subtypes:
        run_diagnose_all_subtypes(sb, sample_size=args.diagnose_sample_size, seed=args.diagnose_seed)
    elif args.all_rules:
        run_diagnose_all_rules(sb, sample_size=args.diagnose_sample_size, seed=args.diagnose_seed)
    elif args.sub_type:
        run_diagnose_subtype(sb, args.sub_type, sample_size=args.diagnose_sample_size, seed=args.diagnose_seed)
    elif args.rule_name:
        run_diagnose_rule(sb, args.rule_name, sample_size=args.diagnose_sample_size, seed=args.diagnose_seed)
    else:
        sys.exit("--diagnose 사용 시 --all-subtypes/--all-rules/--sub-type/--rule-name 중 하나 필요")
    return 0
```

### 3.4 출력 본질 (`run_diagnose_*` 함수)

표 형식 출력 (logger + stdout):

```
=== sub_type별 정확도 진단 (sample_size=100, seed=42) ===

sub_type                              n    TP   FP   WEAK  Phase1   acc      population
─────────────────────────────────────────────────────────────────────────────────────
AS_본다                                100   3    97    0     0     0.0300   3500
WEAK_한다단순                          100   12   45    43    0     0.1200   2100
OBLIGATION_HEADER                      100   95   3     2     0     0.9500   45000
DELETED                                100   0    0     0     100   1.0000   1768
EXCEPTION_CLAUSE                       100   0    0     0     100   1.0000   6174
...

★ 정확도 < 0.5: AS_본다 (0.03), WEAK_한다단순 (0.12), ... → 룰 폐기 검토
★ 정확도 ≥ 0.95: OBLIGATION_HEADER (0.95), DELETED (1.0), ... → TP 확정
```

verification_log entry 추가 (선택):
```python
# 각 진단 결과를 verification_log에 INSERT (check_name='phase22_v31_diagnose_subtype' 등)
```

---

## 4. 단위 테스트 (`tests/test_diagnose.py` 신규)

```python
def test_compute_subtype_group_accuracy_returns_dict():
    """기본 동작 — sub_type 입력 시 dict 반환."""

def test_compute_subtype_group_accuracy_seed_reproducible():
    """seed 동일 시 재현 가능 random."""

def test_compute_subtype_group_accuracy_sample_size_under_population():
    """population < sample_size 시 population 만큼 sample."""

def test_compute_subtype_group_accuracy_exclude_isolated():
    """exclude_isolated=True 시 격리 row 제외."""

def test_compute_rule_accuracy_returns_dict():
    """rule_name 입력 시 dict 반환."""

def test_diagnose_all_subtypes_returns_list():
    """모든 sub_type 진단 → list[dict]."""

def test_diagnose_all_rules_returns_list():
    """모든 룰 진단 → list[dict]."""

def test_isolation_reason_for_fp_subtype_v31_categories():
    """v3.1 신규 카테고리 매칭."""
    # 본 PM이 v3.1에서 추가 결정한 카테고리 검증
```

---

## 5. 검증 임계

| 항목 | 임계 |
|---|---|
| 단위 테스트 | 334 → 342+ passed (8 신규) |
| `validator.py` MD5 | **8,100 bytes 동일** (강제) |
| `iterator.py` 본문 변경 | `isolation_reason_for_fp_subtype` 외 X |
| 본 운영 회귀 | 격리 row 변동 X (DB read-only 또는 reason 재할당만) |
| TP 변동 | 0 row (절대 보전) |

---

## 6. 운영 흐름

### 6.1 Cursor 정정 후 사용자 진행

```bash
# 1. 코드 갱신
cd tai-api && git pull origin dev

# 2. sub_type별 진단 (모든 sub_type)
railway run python3 scripts/track_e_phase2_run.py --phase22-v3 --diagnose --all-subtypes \
  --diagnose-sample-size 100 --diagnose-seed 42

# 3. 룰별 진단 (모든 룰)
railway run python3 scripts/track_e_phase2_run.py --phase22-v3 --diagnose --all-rules \
  --diagnose-sample-size 100 --diagnose-seed 42

# 4. 특정 sub_type 진단 (예: AS_본다)
railway run python3 scripts/track_e_phase2_run.py --phase22-v3 --diagnose --sub-type AS_본다

# 5. 특정 룰 진단 (예: AS_본다_WA_GATDA)
railway run python3 scripts/track_e_phase2_run.py --phase22-v3 --diagnose --rule-name AS_본다_WA_GATDA
```

### 6.2 PM 후속 점검

진단 결과 기반:
1. **정확도 < 0.5 sub_type** → 룰 폐기 결정 (`UPDATE rule_classify_subtype SET enabled=false WHERE ...`)
2. **정확도 ≥ 0.95 sub_type** → TP 확정 보고서
3. **FP_OTHER 3,341건 세분화** → CHECK 제약 enum 추가 + isolation_reason 재할당
4. v3.2 (룰 정정) 또는 Stage 3 진입 결정

---

## 7. 본 명세 외 작업 X

다음 작업은 **별도 명세**로 분리:
- Stage 3 진입 (객체화) — 별도 명세
- METHODOLOGY 6하원칙 역순 검증 — Stage 3 시 별도 명세
- Track B Tier 2-4 본법 수집 — 별도
- Track C v1.3 dict 보강 — 별도
- 6하원칙 보강 (executor/recipient/what) — 별도
- tai-api dev → main merge — Phase 2.2 v3.1 PASS 후 별도

---

## 8. PASS 임계

본 v3.1 정정 PASS 조건:
1. ✅ 단위 테스트 342+ passed
2. ✅ validator.py 0 byte 변경
3. ✅ iterator.py 본문 변경 X (`isolation_reason_for_fp_subtype` 보강만)
4. ✅ 진단 모드 CLI 동작 (4 옵션 모두)
5. ✅ 본 운영 격리 결과 변동 X 또는 reason 재할당 정합
6. ✅ TP 변동 0 row 절대 보전
7. ✅ 사용자 진단 결과 회신 (sub_type/룰별 정확도 표)

PASS 후 PM 결정:
- 룰 폐기 (rule_classify_subtype.enabled=false)
- isolation_reason 재할당 (FP_OTHER → 신규 카테고리)
- v3.2 또는 Stage 3 진입

---

## 9. push 정책

| 영역 | 대상 | 본질 |
|---|---|---|
| 코드 | `tai-api` `dev` (Cursor 자체) | v3.1 보강 push |
| 테스트 | `tai-api` `dev` (Cursor 자체) | 8 신규 |
| 보고서 | `tai-admin` `main` (Cursor 작성) | `Track_E_20260510_Phase2_2_v31_Diagnose.md` |
| 명세 정정 | `tai-admin` `main` (PM 자체) | 본 명세 commit |

---

## 10. 본 명세 본질 vs Stage 3 본질 (구분)

| 영역 | 본 명세 (v3.1) | Stage 3 (별도) |
|---|---|---|
| 본질 | sub_type/룰별 정확도 진단 (역순 검증 부분) | 의무 객체화 (6하원칙 본질) |
| 영향 | DB read-only 또는 reason 재할당 | 신규 stage_3_objectifier row |
| 검증 | _verify_row (정규식) | 6하원칙 정순+역순 (METHODOLOGY 정합) |
| 단위 | sub_type / 룰 group | 의무 객체 단위 |

→ **본 v3.1 = Stage 2 정밀 보강** (역순 진단). **Stage 3 진입 = 별도 명세** (METHODOLOGY 6하원칙 역순 검증 통합).

---

## 11. Cursor 위탁 메시지 (그대로 복붙)

```
[Phase 2.2 v3.1 정정 위탁 — 역순 검증 본질 보강]

선행 base: tai-api dev 90c994c (PASS_STABLE 정합)
본 명세: tai-admin main `Cursor_Phase_2_2_v31_Reverse_Diagnose_Spec.md`

본 PM 본질:
1. v3.0 운영 PASS 정합 (704/704, 격리 10,214, TP 변동 0, Phase 1 보전, 회귀 FAIL 0)
2. FP_OTHER 3,341건 (32.71%) 세분화 본질
3. METHODOLOGY 정합 — sub_type별/룰별 group sample 역순 검증 본질
4. 별도 진단 도구 (본 운영 흐름 영향 X)

작업 영역:
1. engine/sample_accuracy.py:
   - compute_subtype_group_accuracy(supabase, sub_type, *, sample_size=100, seed=None, exclude_isolated=False)
   - compute_rule_accuracy(supabase, rule_name, *, sample_size=100, seed=None, exclude_isolated=False)
   - diagnose_all_subtypes(supabase, *, sample_size=100, seed=None)
   - diagnose_all_rules(supabase, *, sample_size=100, seed=None)
2. engine/iterator.py isolation_reason_for_fp_subtype 보강:
   - SQL 직접 점검 (FP_OTHER sub_type 분포)
   - 신규 카테고리 추가 또는 기존 5 카테고리 패턴 확장
   - CHECK 제약 apply_migration 필요 시 PM 위탁
3. scripts/track_e_phase2_run.py:
   - --diagnose, --all-subtypes, --all-rules, --sub-type, --rule-name, --diagnose-sample-size, --diagnose-seed
   - run_diagnose_* 함수
4. tests/test_diagnose.py (신규):
   - 8 신규 테스트 (위 명세 §4)

검증 임계:
- 단위 테스트 334 → 342+ passed
- validator.py 0 byte 변경 (MD5 8,100)
- iterator.py 본문 변경 X (`isolation_reason_for_fp_subtype` 외)
- pipeline.py / stages/ / subtype_rule_match.py / morpheme.py 변동 X
- 본 운영 격리 결과 변동 X 또는 reason 재할당만

본 명세 외 작업 X:
- Stage 3 진입 / METHODOLOGY 6하원칙 역순 / Track B/C / 6하원칙 보강 / dev→main merge

push 정책:
- tai-api dev에 v3.1 보강 push
- tai-admin main에 보고서 작성 (Track_E_20260510_Phase2_2_v31_Diagnose.md)

운영 흐름:
1. 사용자 git pull origin dev
2. railway run --diagnose --all-subtypes --diagnose-sample-size 100 --diagnose-seed 42
3. railway run --diagnose --all-rules --diagnose-sample-size 100 --diagnose-seed 42
4. PM DB 직접 점검 + 진단 결과 회신
5. PM 후속 결정 (룰 폐기 / reason 재할당 / v3.2 / Stage 3)

진행 부탁드립니다.
```

---

## 12. 본 명세 외 PM 추가 결정 영역

본 v3.1 PASS 후 PM 결정 본질:
- **isolation_reason 신규 enum** (FP_OTHER 세분화 결과)
- **rule_classify_subtype.enabled UPDATE** (정확도 < 0.5 룰)
- **Stage 3 진입** (별도 명세, METHODOLOGY 6하원칙 역순 통합)
- **dev → main merge** (v3.0 + v3.1 안정성 검증 후)

본 PM 9번째 학습 정합 — 즉시 결정 X, 진단 결과 받고 결정.

---

**END OF SPEC v3.1**
