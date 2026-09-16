# SEARCH_FINAL_AUDIT_v1

WO: MASTER-WO-TAI-SEARCH-DICT-001 (OBJ-SEARCH-DICT)
Date: 2026-09-16
**FINAL STATUS: CONDITIONAL_READY** (not READY_FOR_OWNER_APPROVAL)

This audit distinguishes what was genuinely executed and verified in the build
environment from what is honestly deferred to a runtime environment. No metric
in the deferred set is fabricated (WO §71/§73/§124).

## A. Execution environment boundary (hard fact)

- bash network: DISABLED.
- Present: Python 3.12.3 + stdlib (hashlib, unicodedata, json, csv, re).
- ABSENT and uninstallable here: kiwipiepy, pytest, psycopg2.
- Therefore VERIFIABLE offline: normalization, term_id (§23), deterministic
  compiler/validator, determinism-SHA, pure-python search tiers T1-T3, offline selftest.
- Therefore PENDING_RUNTIME: Kiwi baseline/after, pytest regression, DB/pg_trgm
  search, HTTP endpoint execution, latency p50/p95/p99.

## B. Verified offline (REAL)

| Item | Result |
|---|---|
| validate | PASS — terms=60, relations=24 |
| selftest.py | PASS — 12 cases (EXACT/ABBREVIATION/SPACING/ENGLISH/NORMALIZED/NO_MATCH) |
| determinism | PASS — 2 clean builds byte-identical, all 5 artifacts |
| APPROVED-only gate | PROVEN — LEV (REVIEWED) excluded from production index |

term_type distribution: SOURCE_NAME 32, ABBREVIATION 13, SPACING_VARIANT 8, SEARCH_PHRASE 5, ENGLISH_TERM 1, SYNONYM 1.
status distribution: APPROVED 52, PROPOSED 4, REVIEWED 4.
relation_type distribution: ABBREVIATION_OF 13, SPACING_VARIANT_OF 8, SYNONYM_OF 1, ENGLISH_OF 1, NARROWER_SEARCH_TERM 1.

Artifact SHA256 (byte-deterministic):
- TAI_TERM_MASTER_v1.tsv `44bb8b6c3f9245dad230443ecd9c7f25e25fbede124b352e80fe020d1d6afc12`
- TAI_TERM_RELATIONS_v1.tsv `7c8356b491b0b9b9e6fce215ea374ed82ceeef21c507c73f2686488331c7793c`
- TAI_SEARCH_RUNTIME_PROJECTION_v1.json `5d6359f7afd3011e79e9069fc4d15fec4b4ec95253014f07b6c0a8687db794db`
- TAI_KIWI_TERMS_v1.tsv `96654eed6ba9cf93a8efe973a60d052f7021b4f1115ca25775a5d7a4eec8e987`
- TAI_KIWI_USER_DICTIONARY_v1.txt `953d67104e912980ae06afaa752d215bda81dbd22df08306044a79e044ed9a01`

## C. Honesty finding (WO §71 — no fabricated targets)

Of 30 classic industrial-safety compound terms probed against dict_legal_terms,
only 14 exist as-is (근로자 2892, 사업주 2293, 화재 1966, 폭발 411, 감전 167,
보호구 159, 낙하 114, 비계 107, 추락 99, 거푸집 54, 방폭구조 22, 질식 12,
수변전설비 3, 안전보건교육 2). NOT present (existing Kiwi over-segments them):
국소배기장치, 위험성평가, 밀폐공간(작업), 산업용로봇, 산소결핍, 작업계획서,
관리감독자, 유해인자, 작업환경측정, 건강진단, etc.

These absences were NOT back-filled as canonical terms. They were entered only as
SEARCH_PHRASE / KIWI_USER_WORD candidates. Recall was not inflated to hit a target.

## D. Pending runtime verification (must run in Cursor / Claude Code)

1. `pip install kiwipiepy kiwipiepy-model pytest psycopg2-binary` (runtime env has network).
2. Load `TAI_KIWI_USER_DICTIONARY_v1.txt` into Kiwi; run baseline/after segmentation on the benchmark set -> fill SEARCH_BENCHMARK_v1.tsv `runtime_result`.
3. `pytest tests/test_search_dict_*_v1.py` -> regression PASS.
4. Apply migration (OWNER/GPT approval) and run T6 pg_trgm tier against leg-prod.
5. Boot FastAPI, hit `/search-dict/lookup` and `/search-dict/health`; record latency p50/p95/p99.
6. Re-run deterministic build in runtime env; confirm the 5 SHAs above are reproduced bit-for-bit.

## E. Security finding (surfaced only)

leg-prod: 42 tables with RLS disabled per advisory. Out of WO scope; no mutation done.
Owner review recommended before any anon-key exposure.

## F. Hard-stop compliance

No frozen-artifact edit, no canonical-meaning change, no similarity auto-merge, no
production DB write/migration apply, no legal-applicability judgment, no unlicensed
full-content copy. MERGE deferred to OWNER.
