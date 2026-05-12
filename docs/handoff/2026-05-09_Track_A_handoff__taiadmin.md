# [Track A] 핸드오프 — 2026-05-09 세션 종료 시점

> **인계 시점**: 2026-05-09 (토) 컨텍스트 길어져 차기 작업창 인계
> **작성**: Track A 작업창 → 차기 Track A (또는 통합 morpheme 패치 트랙)
> **본 보고서 범위**: Track A 산출물 명세 100% 달성 후 후속 패치 작업 + Track C v1.x 위탁 처리

---

## ⚡ 차기 작업창 즉시 우선순위

| P | 항목 | 상태 | 비용 |
|---|---|---|---|
| **P0** | 자동 로드 1,000건 미스터리 (1,725 기대) | 진단 필요 | ~10분 |
| **P1** | morpheme 다단어 토큰화 99.1% (3건) | A~E 가설 모두 실패 → 새 가설 필요 | ~30분 |
| **P2** | Track C 자동 로드 비용 회신 (1,725건 측정) | P0 해결 전 보류 | ~5분 |
| P3 | Track A 산출물 명세 100% **안정화** announce | morpheme 100% 도달 후 | 0 |
| P4 | housekeeping (보고서 파일명 5/12→5/9, tokenize_sample_100.py 재설계) | 우선순위 낮음 | — |

---

## §1 트랙 정체성 + 절대 원칙

**Track A**: 법령엔진 v3.0 인프라 + Kiwi 형태소 엔진 + Stage 1/2/3 모듈 골격 + validator
**마스터 핸드오프**: https://github.com/taiengineering/tai-admin/blob/main/docs/extraction/v3/MASTER_HANDOFF.md (sha `40bc57cc`)

**§2 절대 원칙 (위배 시 작업 정지)**:
1. LLM 사용 X — Kiwi/정규식/룰베이스만
2. 법령 보전 — 직접 인용만
3. 누락 0건 — 미달도 verified=false로 등록
4. 100% 매핑 — 단계 간 정보 손실 X
5. 오염 = 데이터셋 단위 폐기

---

## §2 Track A 산출물 명세 (마스터 §7.1) — 100% 달성

| 산출물 | 상태 | 커밋 |
|---|---|---|
| `requirements.txt` | ✅ | `831a9165` |
| DB migration 12 테이블 | ✅ | apply_migration 3회 |
| `engine/morpheme.py` | ✅ 90% | `76d14838` + `a9c131d8` + `6fac0e0f` |
| `engine/stage_1_splitter.py` | ✅ 75% | `d7a228d3` |
| `engine/stage_2_decomposer.py` | ✅ 74% | `8f65b9ee` |
| `engine/stage_3_objectifier.py` | ✅ 72% | `00a58e7b` |
| `engine/validator.py` | ✅ 99% | `91dad1a5` |
| 단위 테스트 ≥ 80% | ✅ **83%** (114 passed) | `6338ce85` + `6fac0e0f` |

**기존 보고서**: `docs/extraction/v3/log/Track_A_20260512.md` (commit `0459dce5`)

산출물 자체 100% 달성은 유지. 다만 **morpheme 99.1% (다단어 3건 실패)** 미해결로 "안정화 announce"는 보류 상태.

---

## §3 P0 — 자동 로드 1,000건 미스터리 (최우선)

### 사실
- `engine/morpheme.py` (sha `2c7da588`, dev) 의 `load_verified_dict_from_db`:
  ```python
  res = query.limit(limit).execute()  # limit=5000 default
  ```
- DB 사실: `dict_legal_terms.verified=true` = **1,725건**
- 직전 측정 (Cursor, Railway env): `MorphemeEngine(supabase=sb).user_dict_size = 1000` ❌

### 가설
- **유력**: supabase-py PostgREST 기본 limit 1000 (Range 헤더 default). `.limit(5000)` 인자가 PostgREST에 정확히 전달 안 됐을 가능성
- 차선: Range 헤더 명시 필요 (`headers={"Range": "0-4999"}`)
- 차선: 페이지네이션 강제 (1000개씩 page-by-page)

### 권고 패치
```python
def load_verified_dict_from_db(self, supabase, term_type=None, page_size=1000):
    """페이지네이션으로 전체 verified=true 어휘 로드."""
    out = []
    page = 0
    while True:
        q = (supabase.table("dict_legal_terms")
             .select("term, pos_tag, score, term_type")
             .eq("verified", True))
        if term_type:
            q = q.eq("term_type", term_type)
        res = q.range(page * page_size, (page + 1) * page_size - 1).execute()
        rows = res.data or []
        if not rows:
            break
        out.extend(rows)
        if len(rows) < page_size:
            break
        page += 1
    return self.load_dict_terms(out)
```
참고: `extract_generic_candidates.py`의 `fetch_existing_terms`가 이미 페이지네이션 구현 — 같은 패턴 적용.

### 회귀 검증
1. 단위 테스트 mock supabase에 1,500건 주입 → load_verified_dict_from_db 호출 → user_dict_size=1500 검증
2. 통합: `verify_dict_loading.py` 재실행 → user_dict_size=1,725 확인 + 토큰화 sample 재검증

---

## §4 P1 — morpheme 다단어 토큰화 99.1% (3건)

### 실패 케이스 (지속)
- `'하수도법 시행규칙'` → `하_IC` + `수도법 시행규칙_NNP` (2토큰)
- `'하수도법 시행령'` → `하_IC` + `수도법 시행령_NNP` (2토큰)
- `'체외진단의료기기법 시행령'` → 3토큰 분해

### 직전 진단 결과 (2026-05-09 Cursor)
| 옵션 | 가설 | 결과 |
|---|---|---|
| A | 정규식 2개만 등록 | 동일 실패 (`하_IC + ...`) |
| B | 단일어 어근 + 정규식 동시 등록 | 동일 실패 |
| C | score boost 100배 (10.0 → 100.0) | 동일 실패 |
| D | 단일어에도 score boost (0.0 → 10.0) | 동일 실패 |
| E | `add_pre_analyzed_word` | `ValueError: cannot find the original morpheme` (API 미지원) |

### **근본 원인 확정**
`Kiwi.add_re_word`는 **형태소 분석 단계 이후 매칭된 토큰 시퀀스에 태그 재할당**하는 수준의 API. 형태소 트리 탐색 자체에는 영향 X. 따라서:
- Kiwi가 입력 `'하수도법 시행규칙'`을 `'하'(IC) + '수도법'(NNP) + '시행규칙'(NNG)` 또는 유사 분해로 결정
- 그 후 정규식 `'수도법 시행규칙'`이 토큰 경계와 맞아 NNP 합쳐짐
- 정규식 `'하수도법 시행규칙'`은 토큰 경계 미일치 → 매칭 시도 자체 실패
- **score boost는 매칭 후 우선순위에만 작용 — 미매칭에는 무용**

### 다음 가설 권고 (P1 작업창에서)

| 가설 | 비용 | 회복 가능성 |
|---|---|---|
| **F**: `Kiwi.add_user_word(공백 포함, "NNP")` — 공백 포함 어휘를 `add_user_word`로 등록 가능한지 검증 (Kiwi 0.16+ 일부 지원) | 5분 | 중 |
| **G**: 입력 텍스트 전처리 — 다단어 어휘를 `\u200B` zero-width joiner 등으로 묶은 후 Kiwi 분석 | 30분 | 중-고 |
| **H**: Kiwi 사용자 사전 파일 (`.txt`) 빌드 + `Kiwi(user_dict_path=...)` — 모델 빌드 시점에 학습 | 1시간+ | 고 |
| **I**: `Kiwi.tokenize(text, blocklist=...)` — `'하'`(IC), `'수도법'` 등을 명시적으로 차단 후 Kiwi 재분석 | 15분 | 저-중 |

### 단위 테스트 회귀 인지
- `tests/v3/test_morpheme_collision.py` (commit `6fac0e0f`) — `TestObservedFailures` 3건 통과
- **하지만 통합 환경 (464 어휘 자동 로드 + 343 다단어 + 81 단일어) 재현 X**
- 차기 작업창은 fixture를 통합 환경에 가깝게 보강해야 회귀 방지 효과 보장

---

## §5 P2 — Track C 자동 로드 비용 회신 (보류)

### Track C 통보 (commit `3a998164`)
- v1.2 결과 유지 (재적재 X) — 14,474 INSERT 완료, Top 30 sanity 28/30 = 93%
- v1.3 시안 보존: `docs/extraction/v3/track_c/v1_3_design_proposal.md` (commit `3a998164`, 미열람)
- v1.3 적용 시점: Week 5+ Track E 시작 시 어휘 부족 발견 시
- Track C 결정 시점마다 Track A 동시 통보 절차 추가 예정 (양방향 합의)

### Track C 권고 작성 진입 조건
1. P0 (자동 로드 1,000건) 해결 → 1,725건 정확 로드 검증
2. 정규식 컴파일 비용 측정:
   - 인스턴스 생성 + 자동 로드 시간
   - 첫 토큰화 (warmup) vs 100회 평균 (warm)
3. 측정 결과 + morpheme 진단 옵션 명세를 Track C에 회신 → Track C 권고 작성

### 직전 측정 (1000건 기준, 신뢰도 낮음)
- 인스턴스 생성 + 자동 로드: **0.948s**
- warmup 토큰화: **576.89ms** (lazy 컴파일 추정)
- → 1,725건 정확 로드 후 재측정 필요

---

## §6 인프라 상태 (현재)

### Repo / 브랜치
- `taiengineering/tai-api` dev 브랜치 (canonical)
  - 마지막 본 창 push: `6fac0e0f` (morpheme score boost)
  - **fc5a791** (Track C extract_generic_candidates.py)도 dev에 존재
  - **3a998164**는 `tai-admin` repo의 v1.3 시안
- 로컬: `/Users/taiwangsim/Desktop/tai-engineering/tai-api`
- `origin`(fork) + `upstream`(canonical) 패턴

### DB 상태 (Supabase Seoul, project `vwlahtguyggrhvslabax`)
| 테이블 | 카운트 |
|---|---|
| `dict_legal_terms` 총 | **14,942** |
| ├ verified=true | **1,725** (LAW_NAME 423 + AGENCY_NAME 26 + TECH_TERM 15 + GENERIC 1,261) |
| └ verified=false | **13,217** (AGENCY_NAME 4 + GENERIC 13,213) |
| `law_article_part` | 143,549 (TOTAL_DOCS 하드코딩 일치) |
| Track A 12 테이블 | apply_migration 3회 적용 완료 |

### 단위 테스트
- `pytest tests/v3/ -v --cov=engine` — 114 passed in 15.72s
- 전체 커버리지 **83%**
- `engine/morpheme.py` 90%

### 환경 가이드 (Cursor 실행)
```bash
cd "/Users/taiwangsim/Desktop/tai-engineering/tai-api" && \
  railway run sh -lc 'cd "/Users/taiwangsim/Desktop/tai-engineering" && \
  PYTHONPATH="/Users/taiwangsim/Desktop/tai-engineering" python3 scripts/v3/<script>.py'
```
- 본 창 환경: python3 직접 실행 불가 → Cursor 위탁 패턴
- rebase: `git fetch upstream dev && git rebase -X ours --empty=drop upstream/dev`

---

## §7 협업 트랙 상태

| 트랙 | 상태 | 본 창 인터페이스 |
|---|---|---|
| **Track B** (가족 매핑) | 기존 `law_family_mapping` 그대로 — 영향 0 | — |
| **Track C** (도메인 사전) | v1.0 (186) → v1.1 (464) → v1.2 (1,725 verified=true / 13,217 verified=false) | `MorphemeEngine(supabase=sb)` 자동 로드 (P0 해결 후 정상화) |
| **Track D** (별표·서식 처리) | 별도 작업창 진입 (본 창 X) — 사용자 메시지 2026-05-09에 시작 트리거 받음 | 독립 |
| **Track E** (Stage 분해 사이클) | 본 창 인프라 위에서 시작 예정 — 진입 조건: A Week 4 ✅ + B Week 3 + C Week 4 | morpheme + stage_1/2/3 + validator |

---

## §8 차기 작업창 진입 시 행동 권고

### 첫 turn 체크리스트
1. **본 핸드오프 정독** — §3, §4 우선
2. `git fetch upstream dev` — dev 최신 확인
3. supabase MCP로 DB fact-check (verified=true 1,725 / 다단어 LAW_NAME 344 확인)
4. `pytest tests/v3/` 회귀 통과 확인
5. P0 진단 진입 (자동 로드 1,000건 미스터리)

### 절대 원칙 위배 회피
- **검증 전 100% 단언 X** (Day 1 함정 + 본 세션 morpheme 100% 단언 빗나감 학습)
- **사용자에게 옵션 제시 후 결정 받기** (`ask_user_input_v0` 금지 — 텍스트로)
- **단계별 정지점 명확히** — push → pytest 회귀 → 통합 검증 → 다음 단계
- **Track C 결과 받으면 임계값 영역 침범 X** — 사실만 회신

### 통보 채널 양방향 (Track C 합의)
- 결정 시점마다 Track A ↔ Track C 동시 통보
- 본 창은 Track C 회신 양식을 명시적으로 출력 (사용자가 Track C 작업창에 복사 붙여넣기 가능하게)

---

## §9 핵심 commit 인덱스

| commit | 내용 | repo |
|---|---|---|
| `831a9165` | requirements.txt (Kiwi 추가) | tai-api |
| `b825ca0e` | test_kiwi_hello.py | tai-api |
| `76d14838` | morpheme.py 초기 | tai-api |
| `d7a228d3` | stage_1_splitter | tai-api |
| `8f65b9ee` | stage_2_decomposer | tai-api |
| `00a58e7b` | stage_3_objectifier | tai-api |
| `91dad1a5` | validator | tai-api |
| `a9c131d8` | morpheme Track C v1.0 권고 (다단어 + 자동 로드) | tai-api |
| `6338ce85` | mock supabase + validator DB 케이스 | tai-api |
| `a0282cd9` | verify_dict_loading.py 초안 | tai-api |
| `6dd6e589` | verify_dict_loading.py v1.1 (성능 측정) | tai-api |
| **`6fac0e0f`** | **morpheme score boost (10.0) — 단위 통과 / 통합 미해결** | **tai-api** |
| `fc5a791` | extract_generic_candidates.py (Track C 작성) | tai-api |
| **`2c7da588`** | **morpheme.py 현재 sha (limit=5000 명시이지만 실제 1000 로드)** | **tai-api** |
| `0459dce5` | Track A 산출물 명세 100% 보고서 | tai-admin |
| `3a998164` | Track C v1.3 시안 (본 창 미열람) | tai-admin |

---

## §10 본 세션 학습 (다음 창에 전달)

1. **단위 테스트 fixture는 통합 환경 재현해야 회귀 방지** — 8개 어휘 fixture 통과 = 464개 통합 통과 보장 X
2. **Kiwi `add_re_word` 한계 인지** — 형태소 분석 단계 이후 매칭만, 트리 탐색에는 영향 X
3. **supabase-py PostgREST limit 동작 검증 필수** — `.limit(N)`이 실제 N건 가져오는지 페이지네이션 비교
4. **위탁받은 절차는 단계별 정지점 준수** — 1단계 → 2단계 → 3단계 사이 명시적 GO 신호
5. **통보 채널 양방향** — Track 간 결정은 양 트랙 작업창에 동시 통보

---

본 세션 종료. 차기 작업창은 §3 P0부터 진입.
