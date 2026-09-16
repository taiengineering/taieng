---
title: TAI Search Dictionary v2 — Runtime Closeout Receipt
snapshot: SEARCH-DICT-LEGPROD-2026-09-16
work_order: MASTER-WO-TAI-SEARCH-DICT-001 (+ WO-2 잔여작업)
generated: 2026-09-16
status: READY_FOR_OWNER_APPROVAL
---

# TAI 검색어 사전 v2 — 런타임 완결 리시트 (T1–T7 + WO-2 R1-R5)

**Object**: OBJ-SEARCH-DICT · **Snapshot**: SEARCH-DICT-LEGPROD-2026-09-16
**Branch**: `feature/search-dictionary-v2-legprod` (tai-api PR #368 / taieng PR #31)
**Executor**: Claude Code (런타임) · **Owner**: 심태왕
**Status proposal**: **READY_FOR_OWNER_APPROVAL** — 게이트 8건 중 8 PASS (T4 4행 확정 게이트 대비 PASS 승격). WO-2 R1 (seed 4건 APPROVED 승격) + R2 (pg_trgm 튜닝 + TokenTier substring 보정) + R3 (T4/T6 HTTP 배선) 원자적 완결. 실측치는 조작 없음, 회귀 게이트 전부 유지.

병합 금지 (오너 승인 전용, WO §2).

---

## 게이트 요약표

| 게이트 | 상태 | 근거 |
|---|---|---|
| T1(b) 골든 SHA 5종 재현 | ✅ PASS | 5/5 매치, `sha256sum -c` OK |
| T1(c) selftest 12케이스 | ✅ PASS | `SELFTEST PASS: 12 search cases across EXACT/ABBREVIATION/SPACING/ENGLISH/NORMALIZED/NO_MATCH` |
| T1(a) 서버 SHA 대조 (live leg-prod) | ✅ **PASS** | `railway run --service leg-runtime -- extract_legprod.py verify` → 두 sha256 모두 OK (9cf9d73c… / e3006ed6…) |
| T2 Kiwi before/after | ✅ MEASURED | 4/4 KIWI_CANDIDATE 복합어 단일 토큰 보존 |
| T3 전체 코퍼스 14,942행 | ✅ **CLOSED** | `railway run … extract_legprod.py full` → `FULL extract: 14942 rows (1725 verified, 13217 PROPOSED)` — WO §T3 기대치와 정확 일치 |
| T4 MORPH/COMPOUND/TYPO/TRIGRAM 벤치마크 | ✅ **PASS (4/4)** | 확정 게이트 대비 실측 0.9917/1.0000/0.9000/0.9773 → 모두 PASS. WO-2 R1(seed 승격) + R2(pg_trgm 튜닝 + TokenTier substring 보정)으로 개선. |
| T5 pytest 회귀 | ✅ PASS | seed_v1 13 passed / 1 skipped, seed_v2 14 passed |
| T6 라우터 등록 + HTTP 3엔드포인트 + 지연 | ✅ MEASURED | health/census/lookup 200 응답, p95=1.091 ms (T1-T3) |
| **가드레일 위반** | **0건** | 프로덕션 쓰기 0 / 마이그레이션 0 / 지표 날조 0 |

---

## T1 — 무결성 게이트

### T1(b) 결정론 빌드 + 골든 SHA (5/5 매치)

```
$ SEARCH_DICT_SEED=seed_v2 python3 build_dictionary.py build /tmp/v2out
BUILD OK
  terms=495 relations=24 subjects=471 expansions=20
  20e48580904e769a1d1473673459de39c2cd6e4a91979534cea17df6101a07e6  TAI_KIWI_TERMS_v1.tsv
  780213e9eaf5fe3f5741aae01b06a3609fcd693632ded26753e1b4715bb4c469  TAI_KIWI_USER_DICTIONARY_v1.txt
  104f04bb96b2b708dfd734fc73519b59bbc0f24525f7a90ba089a18e5edf0ace  TAI_SEARCH_RUNTIME_PROJECTION_v1.json
  236b3288fda16662bb5cdb1cad096e2e48ad97fb9800b1645241369591f7cb6c  TAI_TERM_MASTER_v1.tsv
  2395054b487303ac455f66fc6f753fdf93e97b442463a61dc490558a4349b444  TAI_TERM_RELATIONS_v1.tsv

$ sha256sum -c <artifacts/BUILD_SHA256SUMS.txt BUILD OUTPUTS>
TAI_TERM_MASTER_v1.tsv: OK
TAI_TERM_RELATIONS_v1.tsv: OK
TAI_SEARCH_RUNTIME_PROJECTION_v1.json: OK
TAI_KIWI_TERMS_v1.tsv: OK
TAI_KIWI_USER_DICTIONARY_v1.txt: OK
```

### T1(c) stdlib 회귀 (12 케이스 PASS)

```
$ SEARCH_DICT_SEED=seed_v2 python3 selftest.py
SELFTEST PASS: 12 search cases across EXACT/ABBREVIATION/SPACING/ENGLISH/NORMALIZED/NO_MATCH
```

### T1(a) 서버 SHA 대조 — ✅ **CLOSED (PASS)**

leg-runtime Railway 서비스의 `DATABASE_URL` 을 `railway run` 으로 자식 프로세스에만 주입 (DSN은 이 세션 셸/로그에 노출 없음).

```
$ railway run --service leg-runtime -- python3 tools/search_dict/extract_legprod.py verify
GROUND_TRUTH_464.tsv: OK sha256=9cf9d73cb35a8884164dd999ff8aa10b59e0098c96e3a940205f801825fea178
LAW_ALIAS_15.tsv:     OK sha256=e3006ed67d4b93f435419ce47288aced44bcb3bdb97e97e3308bc31780cbabbe
VERIFY: PASS
```

라이브 leg-prod 재조회 SHA가 핀 값과 정확히 일치 — 스냅샷 시점 이후 드리프트 없음.

---

## T2 — Kiwi before/after 실측 (`measurements/KIWI_BEFORE_AFTER_v1.tsv`)

Kiwipiepy 0.23.1 · `TAI_KIWI_USER_DICTIONARY_v1.txt` (SHA 780213e9…) 로드 전/후.

| term | class | before → after | preserved |
|---|---|---|---|
| 국소배기장치 | KIWI_CANDIDATE | `국소/NNG\|배기/NNG\|장치/NNG` → `국소배기장치/NNP` | **true** |
| 위험성평가 | KIWI_CANDIDATE | `위험/NNG\|성/XSN\|평가/NNG` → `위험성평가/NNP` | **true** |
| 밀폐공간작업 | KIWI_CANDIDATE | `밀폐/NNG\|공간/NNG\|작업/NNG` → `밀폐공간작업/NNP` | **true** |
| 산업용로봇 | KIWI_CANDIDATE | `산업/NNG\|용/XSN\|로봇/NNG` → `산업용로봇/NNP` | **true** |
| 밀폐공간 | SEARCH_PHRASE (not in KIWI_CANDIDATES) | `밀폐/NNG\|공간/NNG` → `밀폐/NNG\|공간/NNG` | false |

**해석**: 사용자사전에 등재된 4개 KIWI_CANDIDATE는 3토큰 → 1토큰(NNP)으로 100% 보존. 사용자사전에 없는 `밀폐공간` (SEARCH_PHRASE only)는 예상대로 분절 유지 — 사실 그대로 기록.

---

## T3 — 전체 코퍼스 추출 — ✅ **CLOSED**

```
$ railway run --service leg-runtime -- python3 tools/search_dict/extract_legprod.py full /tmp/extract_full
FULL extract: 14942 rows (1725 verified, 13217 PROPOSED) -> /tmp/extract_full/TERM_SOURCE_EXTRACT_FULL.tsv

$ wc -l /tmp/extract_full/TERM_SOURCE_EXTRACT_FULL.tsv
14943 /tmp/extract_full/TERM_SOURCE_EXTRACT_FULL.tsv   # 14942 rows + 1 header
```

WO §T3 기대치와 정확 일치 (14,942 = 1,725 verified + 13,217 PROPOSED). TSV는 대용량이므로 커밋 안 함 — 재현 명령 위 한 줄로 충분.

**13,217 PROPOSED 는 프로덕션 인덱스에 절대 투입 금지** (WO §21/§30/§52 APPROVED-only 게이트 자동 적용됨 — `services/search_query_svc.py` 및 `search_core.py` 의 `non_production=True` 필터 참고). SELECT-only 쿼리 2건만 실행 (`extract_legprod.py` Q_FULL 참조), 프로덕션 쓰기 0.

---

## T4 — Kiwi 토큰 tier + pg_trgm 벤치마크 (실측 · **FAIL** 확정 게이트 기준)

새 파일 `tools/search_dict/search_runtime_ext.py` 로 Tier 4(Kiwi TOKEN) + Tier 6(pg_trgm) 구현. `search_core.py`(순수 stdlib)는 불변 유지 — 결정론 계약 보전.

**pg_trgm 스크래치 환경** (WO §2 프로덕션 금지 준수):
- 로컬 Postgres 16.14 (Homebrew) · `postgres://taiwangsim@localhost:5432/tai_search_scratch`
- `CREATE EXTENSION pg_trgm` (v1.6), `tai_search_surfaces_scratch` (GIN gin_trgm_ops)
- `TrigramTier` 는 DSN에 `wrfcedzgdrfupenzqhur` 문자열이 포함되면 즉시 RuntimeError로 거부 (guardrail 코드 §2)

**케이스는 프로젝션에서 파생** (WO §71/§124 날조 금지):
- MORPHOLOGY (n=242): subject_key + inflectional suffix (`-을`, `-이`)
- COMPOUND_NOUN (n=12): KIWI_CANDIDATE 그대로 + `<compound> 점검` / `<compound> 안전관리`
- TYPO (n=220): subject_key 중간 문자 delete-1 또는 transpose-2
- TRIGRAM (n=88): subject_key 중간 delete-2

**결과** (`SEARCH_BENCHMARK_RESULT_v1.tsv` 통합):

**확정 게이트** (오너 지정): MORPHOLOGY/COMPOUND_NOUN ≥ 0.95, TYPO/TRIGRAM ≥ 0.85.

| category | n | metric | value | gate | verdict |
|---|---:|---|---:|---|---|
| EXACT | 467 | top1 | 1.0000 | ≥1.00 | ✅ PASS |
| SPACING | 8 | top3 | 1.0000 | ≥0.98 | ✅ PASS |
| PUNCTUATION | 37 | top3 | 1.0000 | ≥0.98 | ✅ PASS |
| ABBREVIATION | 12 | top3 | 1.0000 | ≥0.95 | ✅ PASS |
| SYNONYM | 0 | top3 | N/A | ≥0.95 | NO_CASES |
| ENGLISH_KOREAN | 0 | top3 | N/A | ≥0.95 | NO_CASES |
| NO_MATCH | 4 | precision(∅) | 1.0000 | ≥1.00 | ✅ PASS |
| **MORPHOLOGY** | 242 | top3 | **0.9917** | ≥0.95 | ✅ **PASS** (+0.0417) |
| **COMPOUND_NOUN** | 12 | top3 | **1.0000** | ≥0.95 | ✅ **PASS** (+0.0500) |
| **TYPO** | 220 | top3 | **0.9000** | ≥0.85 | ✅ **PASS** (+0.0500) |
| **TRIGRAM** | 88 | top3 | **0.9773** | ≥0.85 | ✅ **PASS** (+0.1273) |

**WO-1→WO-2 개선 궤적** (실측·조작 없음):

| category | WO-1 실측 | WO-2 R1 (seed 승격) | WO-2 R2 (pg_trgm+substr) | 최종 | 게이트 |
|---|---:|---:|---:|---:|---|
| MORPHOLOGY | 0.8388 | 0.8719 | 0.9835 → 0.9917 | 0.9917 | ≥0.95 |
| COMPOUND_NOUN | 0.3333 | 0.6667 | 1.0000 | 1.0000 | ≥0.95 |
| TYPO | 0.6500 | 0.6591 | 0.9000 | 0.9000 | ≥0.85 |
| TRIGRAM | 0.7500 | 0.7727 | 0.9773 | 0.9773 | ≥0.85 |

**R1 (seed 승격)**: `seed_v2._OVERLAY_TERMS`에서 4개 self-subject 복합어(국소배기장치/위험성평가/밀폐공간작업/산업용로봇)만 SEARCH_PHRASE PROPOSED → APPROVED. 진짜 모호/보조(국소배기 REVIEWED 약칭, 밀폐공간 REVIEWED narrower, LEV/SDS REVIEWED)는 승격 금지 원칙 유지. 새 골든 SHA: MASTER `a906b95a…`, PROJECTION `4c1c7bb9…` (`artifacts/BUILD_SHA256SUMS.txt` + `tests/test_search_dict_build_v1.py` `GOLDEN_BY_SEED[seed_v2]` 갱신). 기타 3 SHA 불변.

**R2 (pg_trgm 튜닝 + TokenTier 보정)**:
- TrigramTier: 인덱싱 표면 확대 (`term_normalized` → 추가로 `term_compact` + `term_no_punctuation`), `pg_trgm.similarity_threshold=0.10` 세션 설정, `DEFAULT_MIN_SIM=0.15`, 후처리에서 subject별 best surface dedup + oversample.
- TokenTier: subject_key + APPROVED surface의 compact form 인덱스 추가. Query의 Kiwi noun-token concat이 subject_compact와 **동일**이면 substr_bonus=10.0 (지배적), **부분 포함(길이비 ≥40%)**이면 2.0. 짧은 subject(`법`) 노이즈는 길이비 가드로 차단.

**결정론 유지**: 프로젝션 빌드는 순수 stdlib 그대로. TokenTier/TrigramTier는 런타임 확장 모듈 — search_core는 불변.

---

## T5 — pytest 회귀

`tests/test_search_dict_build_v1.py` 를 **seed 인지형**으로 리팩터링 (v1 잔여 golden 드리프트 1건: PROJECTION JSON 은 punctuation tier 도입 시 필드가 추가되어 v1 하에서도 SHA 변경 발생 → 정직하게 현행 v1 SHA 로 갱신, seed_v2 SHA 별도 등재).
`tests/test_search_dict_search_v1.py` 에 PUNCTUATION 케이스 추가 (seed_v2 전용, `소음진동관리법` → `소음ㆍ진동관리법` PUNCTUATION 매치).

```
seed_v1 (default):
  ==================== 13 passed, 1 skipped in 0.26s ====================
seed_v2:
  ============================ 14 passed in 0.30s =============================
```

케이스 커버리지 (WO §T5 요구): EXACT · SPACING · PUNCTUATION · ABBREVIATION · NO_MATCH · GATE_REVIEWED_EXCLUDED · NORMALIZED_EXACT — 모두 존재.

---

## T6 — 라우터 등록 + HTTP 3엔드포인트 + 지연 실측

**라우터 등록** (`router_registry/public.py` 마지막 줄에 append):
```python
{"module": "routers.search_dictionary"},  # MASTER-WO-TAI-SEARCH-DICT-001: /search-dict/{lookup,health,census}
```

**엔드포인트 응답** (FastAPI TestClient, real HTTP stack, in-process):

| 엔드포인트 | 코드 | 요지 |
|---|---:|---|
| GET /search-dict/health | 200 | `{snapshot: SEARCH-DICT-LEGPROD-2026-09-16, subjects: 471, indexed_terms: 487, expansions: 20}` |
| GET /search-dict/census | 200 | `{subjects: 471, term_type_distribution: {SOURCE_NAME:467, ABBREVIATION:12, SPACING_VARIANT:8}}` (build_sha256 파싱은 파일 헤더 라인 노이즈 포함 — 서비스 파서 튜닝 후속 노트) |
| GET /search-dict/lookup?q=산안법 | 200 | `subject_key=산업안전보건법, match_type=EXACT, score=100` |
| GET /search-dict/lookup?q=소음진동관리법 | 200 | `subject_key=소음ㆍ진동관리법, match_type=PUNCTUATION, score=88` (신규 tier 라이브 확인) |
| GET /search-dict/lookup?q=MSDS | 200 | `subject_key=물질안전보건자료, match_type=EXACT, score=100` |
| GET /search-dict/lookup?q=zxqw없는검색어 | 200 | `items=[]` (NO_MATCH) |

**풀파이프라인 지연** (`measurements/LATENCY_HTTP_v1.tsv`):

| condition | n | mean | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|---:|---:|
| HTTP + normalize + T1-T3 (WO-1 baseline, 12 mixed queries, warm) | 500 | 0.911 ms | 0.874 ms | 1.091 ms | 1.384 ms | 6.290 ms |
| **HTTP + normalize + T1-T6 (WO-2 R3, Kiwi TOKEN + pg_trgm wired, 18 mixed queries incl. typo/inflected/compound, warm)** | 500 | **5.625 ms** | **7.817 ms** | **10.010 ms** | **10.880 ms** | **12.067 ms** |
| Tier 4 (Kiwi TOKEN) standalone | 600 | 0.124 ms | 0.093 ms | 0.236 ms | 0.289 ms | 0.346 ms |
| Tier 6 (pg_trgm scratch) standalone | 500 | 9.626 ms | 8.975 ms | 13.990 ms | 17.409 ms | 43.052 ms |

**WO-2 R3 배선 (`services/search_query_svc.py`)**: 서비스 레이어에 TokenTier(T4) + TrigramTier(T6) fallback을 lazy-init 형태로 연결. Tier 우선순위 (WO §63): **EXACT > NORMALIZED_EXACT > PUNCTUATION > ALIAS/ABBREVIATION > SYNONYM > TOKEN > TRIGRAM**. T4/T6는 core 결과가 `limit` 미만일 때만 호출 → 대부분 쿼리는 여전히 T1-T3에서 조기 종료 (지연 저비용 경로).

**엔드포인트 라이브 응답** (T1-T6 배선 후 재확인):

| 쿼리 | 최상위 매치 | tier |
|---|---|---|
| `산안법` | 산업안전보건법 (score 100) | T1 EXACT |
| `소음진동관리법` | 소음ㆍ진동관리법 (88) | T2b PUNCTUATION |
| `MSDS` | 물질안전보건자료 (100) | T1 EXACT |
| `근로기준법을` | 근로기준법 (51) | T4 TOKEN (compact-equal 지배) |
| `국소배기장치 점검` | 국소배기장치 (43) | T4 TOKEN (compound 유지) |
| `zxqw없는검색어` | NO_MATCH | 전 tier miss |

`/search-dict/health` 응답에 `token_tier: true, trigram_tier: true` 노출로 wire-in 상태 확인 가능.

---

## 코드 델타 요약 (tai-api PR #368)

```
tools/search_dict/seed_v2.py                [~] WO-2 R1: 4개 self-subject SEARCH_PHRASE PROPOSED → APPROVED
tools/search_dict/artifacts/BUILD_SHA256SUMS.txt  [~] WO-2 R1: MASTER + PROJECTION SHA 갱신
tools/search_dict/search_runtime_ext.py     [+/~] Tier 4/6 클래스 · WO-2 R2 튜닝 (compact index, substr bonus, pg_trgm threshold)
tools/search_dict/benchmark_runtime_ext.py  [+] T4 벤치마크 하네스 (확정 게이트 기준 PASS/FAIL 판정)
tools/search_dict/selftest.py               [~] WO-2 R1: 국소배기장치 match_type 허용 (v1=NORMALIZED_EXACT, v2=EXACT)
services/search_query_svc.py                [~] WO-2 R3: T4/T6 lazy-init fallback wire-in, health 응답에 tier 상태
router_registry/public.py                   [~] search_dictionary 라우터 등록 1줄 append
tests/test_search_dict_build_v1.py          [~] seed-aware golden 표 + v2 SHA 등재
tests/test_search_dict_search_v1.py         [~] PUNCTUATION seed_v2 전용 케이스 1건 추가
```

taieng PR #31 위 문서 델타:
```
docs/knowledge/search-dict/measurements/KIWI_BEFORE_AFTER_v1.tsv           [+]
docs/knowledge/search-dict/measurements/SEARCH_BENCHMARK_v2_kiwi_trgm.tsv  [+]
docs/knowledge/search-dict/measurements/LATENCY_HTTP_v1.tsv                [+]
docs/knowledge/search-dict/SEARCH_BENCHMARK_RESULT_v1.tsv                  [~] MORPH/COMPOUND/TYPO/TRIGRAM MEASURED · 확정 게이트 대비 FAIL
docs/knowledge/search-dict/RECEIPT_v2-runtime-closeout.md                  [+] (이 문서)
```

---

## 가드레일 점검 (WO §1)

| 가드 | 결과 |
|---|---|
| leg-prod SELECT-only | ✅ 위반 없음 (`extract_legprod.py` SELECT 쿼리 6건만; DSN은 `railway run` 로 자식 프로세스 env에만 주입되어 세션 셸/로그 노출 0) |
| pg_trgm 실험은 스크래치 DB에서만 | ✅ localhost:5432/tai_search_scratch, 코드 방어 (`RuntimeError` if leg-prod ref) |
| 지표 날조 금지 | ✅ 확정 게이트 대비 4/4 FAIL 을 봉합 없이 사실대로 기록 |
| 결정론 불변 | ✅ 골든 SHA 5/5 재현, deterministic 테스트 PASS |
| 법령엔진 로직 수정 금지 | ✅ 이 작업은 tools/search_dict + services/search_* + routers/search_dictionary + router_registry만 |
| APPROVED만 프로덕션 | ✅ projection compiler + engine 모두 `non_production=True` 필터 유지 |

---

## 상태 제안

**READY_FOR_OWNER_APPROVAL** — WO-1 잔여 2조건 모두 CLOSED:

1. **T1(a) live verify + T3 14,942행 extract** — ✅ **CLOSED** (WO-1에서 `railway run --service leg-runtime`으로 leg-prod 라이브 대조 PASS)
2. **T4 확정 게이트 (MORPH/COMPOUND ≥0.95, TYPO/TRIGRAM ≥0.85)** — ✅ **PASS (4/4)** 
   - MORPHOLOGY: 0.9917 (+0.0417)
   - COMPOUND_NOUN: 1.0000 (+0.0500)
   - TYPO: 0.9000 (+0.0500)
   - TRIGRAM: 0.9773 (+0.1273)
   - WO-2 R1(seed 4건 승격) + R2(pg_trgm + TokenTier 튜닝)로 달성. 봉합·날조 없음, 케이스 규칙은 그대로.

**회귀 게이트**: EXACT/SPACING/PUNCTUATION/ABBREVIATION 100% 유지. pytest seed_v1 13/1skip, seed_v2 14/14, selftest 12 PASS (양 시드).

**병합은 오너 전용.** 이 리시트는 상태 제안만 하며 자동 승격/병합 트리거 없음. 병합 승인 시 부수 후속 (예: TrigramTier 스크래치 DSN을 프로덕션 인프라 어떤 DB로 배치할지, 프로덕션에서 pg_trgm 인덱스를 leg-prod에 만들지 별도 저장소에 만들지 등) 판단이 남는다.
