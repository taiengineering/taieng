# TAI_SEARCH_DICT_FINAL_HANDOFF

WO: MASTER-WO-TAI-SEARCH-DICT-001 (OBJ-SEARCH-DICT)
Status: CONDITIONAL_READY — awaiting OWNER approval + runtime verification.

## What is delivered

### Docs (repo: taiengineering/taieng, branch feature/search-dictionary-v1, path docs/knowledge/search-dict/)
- 2026-09-16_MASTER-WO-TAI-SEARCH-DICT-001.md (planning doc)
- SEARCH_CONSTITUTION_v1.md
- SEARCH_TERM_CONTRACT_v1.md
- TERM_SOURCE_CENSUS_v1.tsv
- SEARCH_ENGINE_ARCHITECTURE_v1.md
- TERM_SEMANTIC_DECISIONS_v1.tsv
- SEARCH_BENCHMARK_v1.tsv
- SEARCH_FINAL_AUDIT_v1.md
- TAI_SEARCH_DICT_FINAL_HANDOFF.md (this file)

### Code (repo: taiengineering/tai-api, branch feature/search-dictionary-v1, from main db024b5)
- tools/search_dict/{normalize,seed_v1,build_dictionary,search_core,selftest}.py
- services/search_dictionary_svc.py, services/search_query_svc.py
- routers/search_dictionary.py (prefix /search-dict)
- router_registry/public.py wiring (append search_dictionary module)
- migrations/2026-09-16_search_dictionary_tables.sql (additive, idempotent, DB-APPLY=0)
- tests/test_search_dict_{normalize,build,search}_v1.py

## Runtime verification checklist (Cursor / Claude Code — has network)
1. cd tai-api && pip install -r requirements.txt   # kiwipiepy/psycopg2 already pinned
2. python3 tools/search_dict/selftest.py            # expect: SELFTEST PASS
3. python3 tools/search_dict/build_dictionary.py validate   # expect terms=60 relations=24
4. python3 tools/search_dict/build_dictionary.py build out && sha256sum out/*   # match the 5 SHAs in FINAL_AUDIT B
5. pytest tests/test_search_dict_*_v1.py            # regression
6. Load TAI_KIWI_USER_DICTIONARY_v1.txt into Kiwi; run benchmark -> fill SEARCH_BENCHMARK_v1.tsv
7. (OWNER approval) apply migration; run pg_trgm tier
8. Boot API; GET /search-dict/health and /search-dict/lookup?q=산안법; record latency

## Artifacts are reproducible build outputs (not committed as blobs)
The 5 artifacts (TAI_TERM_MASTER/RELATIONS/RUNTIME_PROJECTION/KIWI_*) are NOT
committed as blobs. They are regenerated deterministically from the committed
code (seed_v1.py + build_dictionary.py) and fingerprinted by the committed
BUILD_SHA256SUMS.txt. Deploy step (runtime, has network):
  `python3 tools/search_dict/build_dictionary.py build tools/search_dict/artifacts`
then `sha256sum -c` against BUILD_SHA256SUMS.txt before booting the API. The
service loads TAI_SEARCH_RUNTIME_PROJECTION_v1.json from that artifacts dir.

## Gates (unchanged)
- MERGE = OWNER. Claude opened PRs but does NOT merge.
- No DB apply without OWNER/GPT approval.
- PRE-MERGE GUARD 3-way SHA before any merge.

## Known v1 limitations (documented, not hidden)
- latin_lower not yet used as an index -> English queries case-sensitive in offline tiers.
- T4 (Kiwi) / T6 (pg_trgm) are runtime-injected hooks, unexecuted in build env.
- Benchmark runtime_result and latency = PENDING_RUNTIME.
