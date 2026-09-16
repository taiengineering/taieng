---
title: TAI Search Dictionary v2 — Runtime Closeout Receipt
snapshot: SEARCH-DICT-LEGPROD-2026-09-16
work_order: MASTER-WO-TAI-SEARCH-DICT-001
generated: 2026-09-16
status: CONDITIONAL_READY
---

# TAI 검색어 사전 v2 — 런타임 완결 리시트 (T1–T7)

**Object**: OBJ-SEARCH-DICT · **Snapshot**: SEARCH-DICT-LEGPROD-2026-09-16
**Branch**: `feature/search-dictionary-v2-legprod` (tai-api PR #368 / taieng PR #31)
**Executor**: Claude Code (런타임) · **Owner**: 심태왕
**Status proposal**: **CONDITIONAL_READY** — 게이트 8건 중 7 PASS, T4(MORPH/COMPOUND/TYPO/TRIGRAM) 4행 FAIL (실측치가 오너 확정 임계 미달). T1(a) 라이브 verify + T3 14,942행 extract는 leg-runtime `DATABASE_URL` 주입으로 **CLOSED**. READY 승격은 T4 FAIL 봉합(별도 후속 WO) 후.

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
| T4 MORPH/COMPOUND/TYPO/TRIGRAM 벤치마크 | ❌ **FAIL** | 확정 게이트(MORPH/COMPOUND ≥0.95, TYPO/TRIGRAM ≥0.85) 대입 → 4/4 FAIL. 실측 0.8388/0.3333/0.6500/0.7500. 튜닝은 별도 후속 WO. |
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
| **MORPHOLOGY** | 242 | top3 | 0.8388 | ≥0.95 | ❌ **FAIL** (-0.1112) |
| **COMPOUND_NOUN** | 12 | top3 | 0.3333 | ≥0.95 | ❌ **FAIL** (-0.6167) |
| **TYPO** | 220 | top3 | 0.6500 | ≥0.85 | ❌ **FAIL** (-0.2000) |
| **TRIGRAM** | 88 | top3 | 0.7500 | ≥0.85 | ❌ **FAIL** (-0.1000) |

**지표는 하나도 조작되지 않음.** 확정 게이트에 4/4 미달 — 봉합/튜닝은 이 리시트 범위 밖(별도 후속 WO).

**COMPOUND_NOUN 낮은 이유 (진단, 미봉합)**: seed_v2 의 SEARCH_PHRASE 원어(예: `국소배기장치`)는 status=PROPOSED 로 프로덕션 인덱스에서 제외되며, 대응하는 APPROVED surface (`국소 배기 장치`)는 Kiwi 분석 시 3토큰으로 쪼개져 TokenTier 사전에서 사용자사전 매칭이 성립하지 않는다. 「compound 자체 쿼리」는 NORMALIZED_EXACT 로 통과하지만 「compound + suffix」 형태는 TOKEN tier로도 매칭되지 못한 4/12 fail. 튜닝 축(예: PROPOSED SEARCH_PHRASE 프로덕션 편입 정책, Kiwi user dict 확장, pg_trgm min_sim 하향)은 후속 WO 대상.

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
| HTTP + normalize + T1-T3 (12 mixed queries, warm) | 500 | 0.911 ms | 0.874 ms | 1.091 ms | 1.384 ms | 6.290 ms |
| Tier 4 (Kiwi TOKEN) standalone | 600 | 0.124 ms | 0.093 ms | 0.236 ms | 0.289 ms | 0.346 ms |
| Tier 6 (pg_trgm scratch) standalone | 500 | 9.626 ms | 8.975 ms | 13.990 ms | 17.409 ms | 43.052 ms |

**주의(정직 기록)**: 현행 `services/search_query_svc.lookup` 은 T1-T3만 호출한다 (T4/T6 는 tools/search_dict/search_runtime_ext.py 로 분리되어 있고 HTTP 서비스에 아직 wire-in 되지 않음). 위 표의 HTTP p95=1.091ms는 T1-T3 기준. T4/T6 를 라우터에 결합하는 것은 오너 게이트 확정 후 후속.

---

## 코드 델타 요약 (tai-api PR #368 위 추가 커밋 예정 파일)

```
tools/search_dict/search_runtime_ext.py     [+] Tier 4 (Kiwi TOKEN) + Tier 6 (pg_trgm) 클래스
tools/search_dict/benchmark_runtime_ext.py  [+] T4 벤치마크 하네스 (확정 게이트 기준 PASS/FAIL 판정)
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

**CONDITIONAL_READY** — 승격 진척 및 잔여 조건:

1. **T1(a) live verify + T3 14,942행 extract** — ✅ **CLOSED** (`railway run --service leg-runtime`으로 leg-prod 라이브 대조 PASS, 카운트 정확 매치)
2. **T4 확정 게이트 (MORPH/COMPOUND ≥0.95, TYPO/TRIGRAM ≥0.85)** — ❌ **4/4 FAIL** (실측 0.8388 / 0.3333 / 0.6500 / 0.7500). 튜닝은 이 리시트 범위 밖; **별도 후속 WO** (예: PROPOSED SEARCH_PHRASE의 프로덕션 표면 편입 정책, Kiwi user dict 확장, pg_trgm min_sim 하향, TokenTier subject 토큰화 시 SEARCH_PHRASE 원어 포함 등)에서 처리.

READY_FOR_OWNER_APPROVAL 승격은 T4 FAIL 4행이 해소되기 전까지 유보.

**병합은 오너 전용.** 이 리시트는 상태 제안만 하며 자동 승격/병합 트리거 없음.
