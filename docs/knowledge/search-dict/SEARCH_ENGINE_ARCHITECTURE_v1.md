# SEARCH_ENGINE_ARCHITECTURE_v1

WO: MASTER-WO-TAI-SEARCH-DICT-001 (OBJ-SEARCH-DICT)
Status: DESIGN — code authored, HTTP/DB/Kiwi execution = PENDING_RUNTIME
Anchors: tai-api main `db024b57d9b81802f5dd18b18c69872735e3c3da` (CODE), taieng main `5d3be9b52232395c39ea0538e6b459733846096f` (DOC)

## 1. Repo census facts (verified via guri get_file_contents on tai-api main)

- FastAPI app; APP_VERSION 6.0.2. Thin routers delegate to `services.<name>`.
- Routers registered in `router_registry/<group>.py` ROUTERS lists, loaded per-group in `main.py`.
- To register a new router: append `{"module": "routers.search_dictionary"}` to `router_registry/public.py` (natural fit alongside public_safety_search / public_knowledge_graph).
- Response convention: `{"status":"success","data":...}`. Typed service errors -> HTTPException.
- **Kiwi already integrated**: requirements.txt pins `kiwipiepy>=0.22.0,<0.24.0` + `kiwipiepy-model>=0.22.0` (added 2026-05-09, 법령엔진 v3.0 Track A). REUSE — do not duplicate.
- psycopg2-binary present; direct SQL via `db/direct_sql.py`.
- Migration convention `migrations/{YYYY-MM-DD}_{snake_case}.sql`: additive, idempotent `IF NOT EXISTS`, `public.` schema, header tags WO/STEP, `ARTIFACT ONLY — DB APPLY = 0`.
- Test convention `tests/test_*_v1.py`, `conftest.py`, `tests/fixtures/`. 269 test files. No existing term-dict tests -> no collision.

## 2. Non-collision endpoint

Existing search endpoints that MUST NOT be touched or shadowed:
- `/search` (routers/global_search.py -> services.global_search_svc)
- `/public/safety-search/kosha` (routers/public_safety_search.py -> services.kosha_smart_search)
- routers/public_knowledge_graph.py

New surface uses prefix **`/search-dict`** (no collision):
- `GET /search-dict/lookup?q=...` — lexical lookup over APPROVED terms only.
- `GET /search-dict/health` — projection load status + term/relation counts.

## 3. Layered design

```
routers/search_dictionary.py         (thin: parse q, call service, wrap {status,data})
  -> services/search_query_svc.py    (SearchEngine over runtime projection; tier orchestration)
       -> tools/search_dict/search_core.py   (pure-stdlib tiers T1-T3; offline-verified)
  -> services/search_dictionary_svc.py  (projection load / census / build invocation)
       -> tools/search_dict/build_dictionary.py (deterministic compiler/validator)
            -> tools/search_dict/seed_v1.py     (provenance-bound seed snapshot)
            -> tools/search_dict/normalize.py   (NFC/compact/latin/term_id §23)
```

## 4. Search tiers (WO §52: production indexes APPROVED terms only)

- **T1 EXACT** — normalized exact match.
- **T2 NORMALIZED_EXACT** — compact (spacing-insensitive) match.
- **T3 EXPANSION** — approved alias/synonym expansion (ABBREVIATION_OF, SPACING_VARIANT_OF, SYNONYM_OF, ENGLISH_OF).
- **T4 KIWI_TOKEN** — runtime-injected hook using the already-integrated Kiwi + `TAI_KIWI_USER_DICTIONARY_v1.txt`. PENDING_RUNTIME.
- **T6 PG_TRGM** — runtime-injected hook (fuzzy) via pg_trgm on leg-prod. PENDING_RUNTIME.

Ranking: score desc, then subject_key. Every result carries `match_type` + `matched_term`. REVIEWED/PROPOSED terms are excluded from the production index (proven by the LEV case in selftest).

## 5. Runtime projection

`TAI_SEARCH_RUNTIME_PROJECTION_v1.json` — only APPROVED terms feed production tiers; PROPOSED/REVIEWED carried in a `non_production` block for audit, never indexed. This is the single artifact the service loads at boot.

## 6. Determinism (WO §94/§121)

Same seed snapshot -> byte-identical artifacts. Verified offline over two clean builds:
- TAI_TERM_MASTER_v1.tsv `44bb8b6c3f9245dad230443ecd9c7f25e25fbede124b352e80fe020d1d6afc12`
- TAI_TERM_RELATIONS_v1.tsv `7c8356b491b0b9b9e6fce215ea374ed82ceeef21c507c73f2686488331c7793c`
- TAI_SEARCH_RUNTIME_PROJECTION_v1.json `5d6359f7afd3011e79e9069fc4d15fec4b4ec95253014f07b6c0a8687db794db`
- TAI_KIWI_TERMS_v1.tsv `96654eed6ba9cf93a8efe973a60d052f7021b4f1115ca25775a5d7a4eec8e987`
- TAI_KIWI_USER_DICTIONARY_v1.txt `953d67104e912980ae06afaa752d215bda81dbd22df08306044a79e044ed9a01`

## 7. Security finding (surfaced, not acted on — out of WO scope)

leg-prod advisory flags 42 tables with RLS disabled (anon key can read/modify). No production mutation performed. Recommend owner review before exposing any anon-key path.
