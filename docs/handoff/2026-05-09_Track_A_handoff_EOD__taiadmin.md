# Track A 핸드오프 — 2026-05-09 EOD (P0 해결 + 안정화 announce)

**작성**: Track A 작업창 (P0 패치 + 정지점 1 통과)
**대상**: 차기 Track A 인스턴스 또는 트랙 통합 마스터 갱신 작업창
**선행**: `docs/extraction/v3/log/Track_A_handoff_20260509.md` (사전 인계)

---

## 1. 한 문단 요약

Track A 산출물 명세 100% 유지 + P0 (자동 로드 1,000건 미스터리) 해결. `engine/morpheme.py` `load_verified_dict_from_db`를 PostgREST max-rows=1000 회피용 페이지네이션(`.range()` page_size=1000 / max_pages=50)으로 교체 (commit `91c12da6`). 정지점 1 (pytest 회귀 + 두 트리 diff) 통과 — 126 passed, 커버리지 85% (morpheme.py 96%). P1 (다단어 3건 토큰화)·P2 (실 환경 비용 측정)·P4 (housekeeping)는 별도 trackpoint로 분리. **Track A 안정화 announce 가능 상태**.

---

## 2. 본 트랙 정체성 (재확인)

- **Track ID**: A — 엔진 인프라 + Kiwi + Stage 모듈 + validator
- **마스터 §7.1 산출물 명세**: 100% 도달 유지 (이전 commit `0459dce5` announce)
- **본 창 추가 산출물**:
  - `engine/morpheme.py` P0 페이지네이션 패치
  - `tests/v3/conftest.py` `_Builder.range()` 추가 (mock 환경 통합 재현)
  - `tests/v3/test_morpheme_pagination.py` 신규 12 case (TestPagination 8 + TestAutoLoadIntegration 2 + TestDeprecatedLimit 2)

---

## 3. 절대원칙 점검 (마스터 §2)

| 원칙 | 본 창 작업 적용 |
|---|---|
| ① LLM X | ✅ 정규식 + Python 표준 라이브러리만 |
| ② 법령 보전 | ✅ morpheme/Kiwi 인터페이스 변경 없음, dict_legal_terms 어휘 변형 0 |
| ③ 누락 0건 | ✅ deprecated `limit` 인자도 호환 shim으로 보존 (warning 후 무시) |
| ④ 100% 매핑 | ✅ 페이지네이션이 모든 verified=true row 정합 로드 (test_load_exact_1725) |
| ⑤ 오염 = 폐기 | ✅ mock fixture에서 1,725 정확 로드 검증 후 push |
| §2.6 사용자 검증 부담 0 | ⚠️ 정지점 1 (pytest) + diff는 Cursor 위탁 — Track A 본 창 환경 제약상 |
| §2.7 ground truth 우선 | ✅ Track C v1.2 (1,725건) ground truth 그대로 활용 |

---

## 4. P0 해결 사실 (정지점 1 통과)

### 4.1 패치 본질

- 위치: `taiengineering/tai-api`, branch `dev`, commit `91c12da6`
- 변경: `engine/morpheme.py` `load_verified_dict_from_db` (구 `.limit(5000)` → 신 `.range(start, end)` 페이지네이션)
- 호환: 기존 `limit` 인자는 keyword-only deprecated, warning 후 무시
- 동반 변경: `tests/v3/conftest.py` `_Builder.range()` 추가, `tests/v3/test_morpheme_pagination.py` 신규

### 4.2 검증 결과 (Cursor 회신 사실)

```
git rev-parse upstream/dev → 91c12da6bd32cd8ee500a58863feab956435894a
git merge-base HEAD upstream/dev → 91c12da6 (모노레포 루트 mirror 동기화 완료)
diff /engine/morpheme.py /tai-api/engine/morpheme.py → exit 0 (동일)
pytest tests/v3/ -v --cov=engine → 126 passed, 약 20.65s
  - 직전 baseline: 114 passed
  - 신규 12 case 모두 통과 (TestPagination + TestAutoLoadIntegration + TestDeprecatedLimit)
커버리지: 합계 85% (이전 83%), morpheme.py 96% (이전 90%)
```

### 4.3 가설 검증 (`extract_generic_candidates.py` 비교)

`scripts/v3/extract_generic_candidates.py`의 `fetch_existing_terms`는 동일한 페이지네이션 패턴(`.range(page * PAGE, (page+1) * PAGE - 1)`)을 이미 사용 중이며, v1.2 GENERIC 추출 (14,474건)을 정상 수행했음. 본 창 P0 패치가 이 검증된 패턴을 `morpheme.py`에 동일 적용한 형태이므로 정합성 입증.

---

## 5. P1 잔여 — 다단어 토큰화 3건 (별도 trackpoint)

### 5.1 사실

- 핸드오프 §4 명시 case (변동 없음):
  - `'하수도법 시행규칙'` → `'하/IC + 수도법 시행규칙/NNP'` (2토큰)
  - `'하수도법 시행령'` → `'하/IC + 수도법 시행령/NNP'` (2토큰)
  - `'체외진단의료기기법 시행령'` → 3토큰 분해
- 가설 A~E 모두 실패 (직전 핸드오프 §4 표 그대로)
- 새 가설 F~I 미시도 (`add_user_word(공백)`, ZWJ 전처리, `user_dict_path`, `blocklist`)

### 5.2 본 창에서 분리한 사유

- 마스터 §7 Track A 산출물 명세 8개 모두 100% 유지 (P1은 명세 외 정밀도 이슈)
- §10 학습 #2 (검증 전 단언 X) 준수 — 가설 F~I 검증 없이 "안정화 100%" announce 위배
- P0 해결로 마스터 §7.1 핵심 게이트는 통과 — P1은 안정화 announce 호환 trackpoint

### 5.3 차기 인스턴스 진입 시 자료

`scripts/v3/verify_dict_loading.py` `step_4_multiword_bulk` (sha `c3ad1c25`)가 다단어 LAW_NAME 344건 일괄 토큰화 + 실패 case 자동 list out. 별도 갱신 없이 그대로 실행 시 P1 3건 + 회귀 case 식별 가능. 단, 기대값 `EXPECTED_TOTAL=464`는 v1.1 시점이라 step_1에서 fail. P1 작업 시 step_1·step_2 기대값을 1,725로 갱신하거나 step_4만 단독 실행하는 형태로 활용.

---

## 6. P2 펜딩 — Track C 자동 로드 비용 회신

### 6.1 사실

- Track C가 `Track_C_20260509.md` 마지막 섹션 + `Track_C_handoff_20260509_EOD.md` §7.1에서 본 창의 비용 측정 회신 명시 대기
- 본 창은 정지점 1 (mock 통합 환경)에서 1,725건 자동 로드 정합 확인했으나, **실 supabase 환경의 wall time은 측정하지 않음**
- 사유: 본 창 환경 python3 직접 실행 X. mock 측정값은 supabase HTTP 비용을 반영하지 않음. 잘못된 측정값 회신 시 §10 학습 #2 위배

### 6.2 차기 인스턴스 측정 방법

`verify_dict_loading.py` step_2·step_5를 1,725건 기대값으로 갱신 후 Cursor `railway run` 실행. 측정 항목:
- 인스턴스 생성 + 자동 로드 wall time (1,725건, 다단어 344 add_re_word 포함)
- warmup vs warm 토큰화 (정규식 컴파일 EAGER/LAZY 추정)
- 100회 평균 토큰화

### 6.3 Track C 회신 양식 (측정 후 사용)

`docs/extraction/v3/log/Track_C_20260509.md` 마지막 섹션 양식 그대로:

```
Track A → Track C 회신 — P0 해결 + 자동 로드 비용 측정

dict_legal_terms 페이지네이션 자동 로드: ✅ 통과
  engine = MorphemeEngine(supabase=get_supabase())
  engine.user_dict_size = 1725

성능 측정 (verify_dict_loading.py step_5):
  인스턴스 생성 + 자동 로드: __.___s
  첫 토큰화 (warmup):       __.__ms
  warm 토큰화:              __.__ms
  100회 평균:                __.__ms
  컴파일 모드:                EAGER / LAZY

샘플 토큰화 (Track_C 통보 양식 그대로): "안전관리자는 다음 사항을 검사한다."

P1 (다단어 3건) 잔여는 안정화 announce에서 별도 trackpoint로 분리. 본 회신 무관.
Track C v1.3 시안 적용 결정은 Track E 시작 시점에 재검토 권고.
```

---

## 7. P4 housekeeping — 정정·정리 항목 (다음 기회에)

### 7.1 핸드오프 §6 환경 가이드 정정

`Track_A_handoff_20260509.md` §6 "rebase: `git fetch upstream dev && git rebase ...`" + "`origin`(fork) + `upstream`(canonical) 패턴" 부정확.

실제 환경:
- `tai-engineering/` (모노레포 루트): origin = tai-engineering.git, **upstream = tai-api.git**
- `tai-engineering/tai-api/` (sub-repo): **origin only** (tai-api.git)

따라서 rebase 명령은 모노레포 루트에서 실행해야 의미. 차기 핸드오프 작성 시 §6 명령에 `cd /Users/taiwangsim/Desktop/tai-engineering` (루트) 명시 필요.

### 7.2 보고서 파일명 정정

`Track_A_20260512.md` → `Track_A_20260509.md` (작업일 정합). 본 창 환경에서 GitHub MCP 단독 rename 미지원, Cursor 위탁 필요.

### 7.3 마스터 핸드오프 v1.4 갱신 권고

마스터 §13 변경 이력에 추가:
- **v1.4** (2026-05-09): Track A P0 해결 (페이지네이션) + 안정화 announce + 환경 가이드 §6 정정. P1 (다단어 3건) trackpoint 분리.

본 창은 마스터 직접 갱신 권한 모호 — 사용자 결정 위임.

### 7.4 `tokenize_sample_100.py` 재설계

직전 보고서 `Track_A_20260512.md` 결정사항 그대로 보류 (Day 4+ 처리). 본 창 무관.

---

## 8. Track A 안정화 announce

마스터 §7.1 산출물 명세 100% 유지 + P0 자동 로드 게이트 통과 + 정지점 1 (126 passed / 85% coverage / 두 트리 diff 0) 통과로 **Track A 안정화 단계 도달**.

남은 미해결: P1 (다단어 3건) — 명세 외 정밀도 trackpoint, 안정화 호환. P2 (실 환경 비용 측정) — Track C 회신 양식 제공, 측정 자체는 차기 인스턴스 위탁.

---

## 9. 차기 인스턴스 진입 시 권고 행동

### 즉시 (모든 트리거 공통)
1. 본 문서 정독
2. 마스터 핸드오프 (v1.3, 또는 v1.4 갱신 후) §2 절대원칙 재확인
3. `taiengineering/tai-api` dev HEAD = `91c12da6` 확인 (또는 그 위 커밋)
4. 모노레포 루트에서 `git fetch upstream dev && git rebase -X ours --empty=drop upstream/dev` (필요 시)

### 트리거별 분기

**Track C 비용 측정 회신 요청**:
- `verify_dict_loading.py` step_1·step_2 기대값을 1,725 (LAW_NAME 423 / AGENCY_NAME 26 / TECH_TERM 15 / GENERIC 1,261)로 갱신
- Cursor `railway run` 실행 → 측정값 회신 → §6.3 양식으로 Track C 작업창에 전달

**P1 다단어 3건 처리**:
- 가설 F (add_user_word with whitespace) → G (ZWJ) → H (user_dict_path) → I (blocklist) 순서로 시도
- `tests/v3/test_morpheme_collision.py` (sha `a9c59fef`) 통합 환경 재현 강화

**Track E 시작 통보**:
- 본 트랙 인프라 (morpheme + stage_1/2/3 + validator + 12 DB 테이블) 그대로 활용 가능
- dict_legal_terms 자동 로드 1,725건 (P0 해결 후 정합)

---

## 10. 핵심 commit 인덱스 (본 창 추가)

| commit | 내용 | repo |
|---|---|---|
| `91c12da6` | morpheme.py 페이지네이션 + conftest.range() + test_morpheme_pagination 신규 | tai-api dev |

(이전 커밋 인덱스는 `Track_A_handoff_20260509.md` §9 그대로)

---

## 11. 본 창 학습 (다음 창 전달)

1. **모노레포 + sub-repo 구조 인지** — 두 트리 (`tai-engineering/engine/` vs `tai-engineering/tai-api/engine/`)가 git remote 다름. push는 `tai-api` 단일 source-of-truth, 모노레포 루트는 `git fetch upstream dev` 후 rebase로 mirror 받음.
2. **mock fixture는 PostgREST 정책 시뮬레이션 필요** — `_Builder.range()` 슬라이싱이 1,725건 통합 환경 재현. mock에 `.limit()` 만 있고 `.range()` 부재 시 페이지네이션 패치 검증 0 효과 (직전 §10 학습 #1 재확인).
3. **검증 단계 자체에 함정** — pytest cwd / PYTHONPATH가 어느 트리를 import하는지 사전 분석 필수. 본 창은 정지점 1 첫 시도에서 트리 이중화로 신규 12 case가 0건 실행됨 (사용자 회신으로 발견).
4. **권고만 한 것 vs 실 push 구분** — 직전 핸드오프 §3 권고 패치는 코드 제시였고 push는 본 창 작업. 핸드오프 인용 시 "권고됨" vs "적용됨" 구분.

---

**END OF HANDOFF — Track A 안정화 announce. 차기 트리거 대기 모드.**
