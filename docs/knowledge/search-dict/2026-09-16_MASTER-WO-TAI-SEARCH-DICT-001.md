# 기획문서 (Planning Record) — MASTER-WO-TAI-SEARCH-DICT-001

> Owner(심태왕) 제공 standalone Work Order 원문을 `feature/search-dictionary-v1` workstream의
> **기획 기록(planning record)** 으로 저장한 파일. 상단 "커밋 메모"는 Claude가 착수 시점에
> 남긴 provenance/anchor/경로 조정 근거이며, 그 아래 본문은 WO 원문 전문(verbatim)이다.

---

## 커밋 메모 (Claude, 착수 기록)

```text
MASTER WO      = MASTER-WO-TAI-SEARCH-DICT-001
OBJECT         = OBJ-SEARCH-DICT
SOURCE         = Owner(심태왕) 제공 standalone WO
REGISTERED_AT  = 2026-09-16
REGISTERED_BY  = Claude (기획창)

DOC REPO       = taiengineering/taieng   (문서 전용 저장소)
DOC BRANCH     = feature/search-dictionary-v1
DOC MAIN ANCHOR= 5d3be9b52232395c39ea0538e6b459733846096f  (taieng main HEAD, 2026-09-06)

CODE REPO      = taiengineering/tai-api  (검색 서비스/컴파일러/테스트, 향후 구현)
CODE MAIN ANCHOR = db024b57d9b81802f5dd18b18c69872735e3c3da  (tai-api main HEAD, 2026-09-14)
```

### 경로 조정 근거 (governance reconciliation)

WO §97은 산출물 폴더를 `docs/knowledge/search-dict/`로 권고하나, TAI 확정 거버넌스는
"모든 문서는 `taiengineering/taieng/docs/`에만 둔다 (tai-api/docs·tai-admin/docs 금지)"이다.
WO §97 후단("실제 repo 규칙이 다르면 동일 의미의 existing convention을 따른다")에 근거하여:

```text
문서(Constitution/Contract/Census/Master/Benchmark/Audit/Handoff 등)
  → taieng/docs/knowledge/search-dict/  에 배치 (governance + WO 폴더명 동시 충족)
검색 코드(search service / compiler / tests / migration)
  → tai-api  (WO §58, RISK-04 본선과 동일 저장소, 별도 branch/PR)
```

이 workstream은 문서 PR(taieng)과 코드 PR(tai-api)로 분리되며, 두 PR 모두 독립 branch에서
진행하고 PR #366(RISK-04) branch에서 분기하지 않는다. 구조화 산출물 파일명은 WO가 계약으로
참조하므로 WO 명시명(SEARCH_CONSTITUTION_v1.md 등)을 그대로 유지한다.

### 실행 환경 경계 (정직 고지)

현 대화 세션의 로컬 실행 환경은 네트워크가 비활성화되어 `kiwipiepy` 설치·형태소 분석 실행·
pytest·컴파일러 결정성 SHA 산출·벤치마크 latency 측정을 직접 검증 실행할 수 없다.

```text
이 세션 완결 가능 : Repo/Source Census, Constitution, Contract, 스키마·아키텍처 설계,
                 read-only DB 기반 term 후보 수집
실행 환경 필요 : Kiwi baseline/after, compiler 실행·결정성 SHA, 검색 서비스 코드,
                 pytest/regression, 벤치마크 recall·latency 실측  (Cursor/Claude Code)
```

검증되지 않은 수치를 임의로 채우지 않고("fabricating completion = integrity breach"),
최종 상태는 실측 phase 완료 전까지 READY_FOR_OWNER_APPROVAL로 선언하지 않는다.

---

## WO 원문 (verbatim)

# MASTER-WO-TAI-SEARCH-DICT-001

## TAI 산업안전 전문용어사전 · 한국어 형태소 검색 기반 구축

### Claude Standalone End-to-End Work Order

---

# 0. 당신의 역할

당신은 이 작업에서 **Claude 단독 수행자**다.

기존의 GPT=설계/판정/검증, Cursor=실행 분업 구조를 사용하지 않는다. 이번 프로젝트 안에서는
Claude가 조사·설계·데이터 수집·전문용어 판정·구현·테스트·QA·문서화·Git commit·PR·최종 Audit·인수인계를
전부 수행한다.

다만 아래 경계는 절대 넘지 않는다: TAI canonical 의미 변경 / 법령 적용성 판단 / 법적 의무 판단 /
RISK-04 semantic 결정 변경 / 기존 canonical 자동 병합 / Production DB 무단 write. 권한은
**검색용 언어자산(Search Language Asset) 구축**까지다.

---

# 1. 작업 방식

사용자에게 중간 단계마다 승인 요청하지 않는다. 정상 진행 가능한 것은 스스로 조사·판정·구현하여 계속
진행한다. 다음 경우에만 STOP 한다:
(1) credentials/secrets가 반드시 필요 (2) production destructive write 필요 (3) 기존 canonical 의미를
변경해야만 진행 가능 (4) source license 때문에 사용 여부를 사용자가 결정해야 함 (5) 저장소 접근 불가
(6) 서로 모순되는 Owner-approved governance 발견. 그 외에는 보수적 방향으로 판단하여 계속
진행하고 근거를 문서화한다.

---

# 2. 프로젝트 명

```text
OBJECT  = OBJ-SEARCH-DICT
MASTER WO = MASTER-WO-TAI-SEARCH-DICT-001
```

내부 명칭: TAI Search Dictionary / TAI Term Dictionary / TAI Domain Lexicon.
DB/API에서는 `search_dictionary` / `search_terms` / `search_term_relations` 계열을 사용한다.

---

# 3. 최종 목표

산업안전·산업설비·건설·제조·빌딩 분야에서 사용자가 어떤 표현으로 검색하더라도 TAI 내부의 적절한
자료와 개념을 찾을 수 있도록: 전문용어사전 + 원문명/표기변형 + 동의어 + 약어 + 현장용어 +
영문명 + Kiwi 사용자사전 + 한국어 형태소 분석 + 검색용 normalization + index + ranking + API +
benchmark/regression 을 구축한다.

파이프라인: 사용자 검색어 → normalization → exact term/alias → Kiwi 형태소 분석 → TAI 전문용어
expansion → candidate retrieval → ranking → TAI 내부 대상 반환.

---

# 4. 매우 중요한 철학 — Canonical과 Search 분리

Canonical Concept ≠ Search Term. 예: canonical "국소배기장치" 하나에 search terms는
국소배기장치/국소 배기 장치/국소배기/국소배기설비/LEV 등 여러 개. 검색표현이 여러개여도
canonical 의미는 하나일 수 있고, 동일 표면어가 여러 concept을 가리킬 수도 있다.

---

# 5. 핵심 불변조건

```text
SEARCH TERM ≠ CANONICAL ID
SEARCH NORMALIZATION ≠ SEMANTIC EQUIVALENCE
SAME NAME ≠ SAME CONCEPT
MORPHOLOGICAL SIMILARITY ≠ CANONICAL MERGE
TRIGRAM SIMILARITY ≠ CANONICAL MERGE
LLM SIMILARITY ≠ CANONICAL MERGE
```
검색엔진의 추론 결과가 canonical DB를 자동 변경해서는 안 된다.

---

# 6. 45cm 구조

헌법 → 규정 → 엔진. 적용: SEARCH CONSTITUTION → TERM/SEARCH CONTRACT → DICTIONARY ENGINE →
KIWI ANALYZER → SEARCH ENGINE → API → QA.

---

# 7. 반드시 먼저 만들 문서

구현 전에 `SEARCH_CONSTITUTION_v1.md` 와 `SEARCH_TERM_CONTRACT_v1.md` 를
`docs/knowledge/search-dict/` 에 먼저 만든다.

---

# 8. SEARCH CONSTITUTION 필수 원칙 (최소 12항)

1. canonical truth는 검색엔진이 결정하지 않는다. 2. 모든 search term은 provenance를 가진다.
3. 원문을 덮어쓰지 않는다. 4. normalized text는 파생값이다. 5. alias는 source evidence를 보존한다.
6. 동일 term이 여러 concept에 연결될 수 있다. 7. ambiguity를 억지로 제거하지 않는다.
8. search ranking은 semantic truth가 아니다. 9. search 결과가 법적 의무 판단을 대신하지 않는다.
10. Legal Engine alone handles applicability/obligation. 11. fuzzy 결과는 보조 검색일 뿐 자동
승인에 사용하지 않는다. 12. vector search 도입 시에도 동일 원칙을 적용한다.

---

# 9. RISK-04 본선과의 경계

현재 별도 본선에서 RISK-04 작업이 진행 중. 알려진 handoff 기준(참조사항): PR #366 OPEN/UNMERGED,
RISK-04 semantic review complete, REVIEW-009 PASS/CLOSED, pre-approval concept estimate 1111,
RISK-04-APPROVE-001 NOT OPENED, canonical UUID 0, approved mapping 0.

**절대 금지**: PR #366 수정/merge, RISK04_* frozen artifact 수정, RISK semantic decision 변경,
RISK canonical representative 선정. 검색사전 프로젝트는 독립 branch/PR에서 진행한다.

---

# 10. Branch 정책

반드시 현재 `origin/main`을 재확인하고 repository/main HEAD/checked_at 기록. 새 branch 권장
`feature/search-dictionary-v1`. PR #366 branch에서 분기하지 않는다.

---

# 11. Source와 Canonical 연결 방식

RISK canonical 미확정에도 진행 가능해야 하므로 search term 연결대상은 처음부터 UUID를 강제하지
않는다: subject_type / subject_key / canonical_id nullable. 허용 subject_type 예: RISK_REVIEW_CONCEPT,
RISK_SOURCE, LEGAL_TERM, KOSHA_TERM, KALIS_TERM, CHEM_TERM, ACCIDENT_TERM, EQUIPMENT_TERM,
GENERAL_TERM. canonical 확정 후 별도 linkage로 UUID 연결.

---

# 12. 목표 아키텍처

AUTHORITATIVE SOURCE → RAW TERM → NORMALIZATION LAYER(original/normalized/spacing/punctuation/Latin) →
TAI TERM DICTIONARY(synonym/alias/abbreviation/field/English/spelling variant) → KIWI DICTIONARY →
MORPHOLOGICAL ANALYZER → SEARCH INDEX → SEARCH SERVICE.

---

# 13. Source Census

먼저 repository를 조사하여 실제 source 위치를 찾는다(추측 경로 금지). 최소 source family:
CIC_W, KOSHA, KALIS, 법령, KOSHA Guide, 위험성평가, 산업재해/사고사례, MSDS/화학물질, 설비명,
공정명, 작업명, TAI Help/Knowledge, 기존 SaaS UI labels, 기존 검색 keyword.

---

# 14. 외부 조사 Source Priority

1. 대한민국 법령 공식 원문 2. 고용노동부 3. KOSHA 4. 국토교통부/국가건설기준 5. KALIS 등 공공기관
6. 공공데이터포털 7. 제조사 공식 기술자료 8. 산업 표준/공식 glossary 9. 기타 보조. 블로그/카페/SEO
페이지는 권위 근거로 사용하지 않고 현장용어 보조 evidence로만 허용.

---

# 15. Copyright/Source Policy

검색사전에는 용어/짧은 정의 요약/출처 식뱄자/source URL/source document/evidence location 정도만
저장. 저작권 있는 문서 본문 전체를 무단 복제하지 않는다.

---

# 16. Source Census Artifact

`docs/knowledge/search-dict/TERM_SOURCE_CENSUS_v1.tsv` 생성. 필수 필드: source_id, source_name,
source_type, authority_level, location, format, available, row_or_item_count, term_candidate_count,
license_or_usage_note, freshness, checksum_if_local, notes.

---

# 17. Source Snapshot 원칙

가능한 모든 입력은 snapshot identity(source_id/snapshot_date/source_checksum/source_row_key)를 가진다.
동일 입력 → 동일 dictionary output.

---

# 18. Term Type Contract

CANONICAL_NAME, SOURCE_NAME, ALIAS, SYNONYM, ABBREVIATION, FIELD_TERM, ENGLISH_TERM,
SPELLING_VARIANT, SPACING_VARIANT, PUNCTUATION_VARIANT, SEARCH_PHRASE, KIWI_USER_WORD.
확장 가능하나 Contract에 먼저 기록.

---

# 19. Term Type 의미

CANONICAL_NAME=승인된 canonical 공식 표시명(미확정에 남발 금지). SOURCE_NAME=원천데이터 실존 명칭.
ALIAS=같은 대상의 다른 일반 표현. SYNONYM=의미적 동일/검색상 동등 승인 표현. ABBREVIATION=약어(MSDS,
SDS, LEV, SCP, GCP). FIELD_TERM=현장용어. ENGLISH_TERM=영문 기술명. SPELLING/SPACING/PUNCTUATION
VARIANT=철자/띄어쓰기/기호 변형.

---

# 20. Relation Type Contract

EXACT_ALIAS, SYNONYM_OF, ABBREVIATION_OF, ENGLISH_OF, FIELD_TERM_OF, SPELLING_VARIANT_OF,
SPACING_VARIANT_OF, PUNCTUATION_VARIANT_OF, RELATED_TERM, BROADER_SEARCH_TERM,
NARROWER_SEARCH_TERM, AMBIGUOUS_WITH. RELATED_TERM을 synonym처럼 사용하지 않는다.

---

# 21. 상태 모델

PROPOSED, REVIEWED, APPROVED, REJECTED, HOLD. 자동 추출 결과 기본값 = PROPOSED.

---

# 22. Evidence Model

source_id, source_key, source_text, evidence_ref, evidence_type, confidence, curation_method.
curation_method 예: SOURCE_EXACT, RULE_DERIVED, MANUAL_SEMANTIC, OFFICIAL_GLOSSARY, DOMAIN_RESEARCH.

---

# 23. Deterministic Term ID

payload = source_id + "\n" + source_key + "\n" + term_type + "\n" + original_term;
term_id = SHA256_UTF8(payload). 단, 이는 canonical ID가 아니다.

---

# 24. 원문 보존

항상 term_original 보존. 예: 배관‧전로공사 / 배관및전로공사 를 원문 단계에서 하나로 덮어쓰지 않는다.

---

# 25. Search Normalization Layer

파생필드: term_normalized, term_compact, term_latin_lower, term_no_punctuation.

---

# 26. 기본 Normalization

보수적으로: Unicode normalization, leading/trailing whitespace 제거, 연속 whitespace 축약,
Latin lowercase search copy, 명백한 punctuation search copy. 원본에는 적용하지 않는다.

---

# 27. 자동 오탈자 교정 금지

잘린 원문/오탈자 의심/N=/(/깨진 분류 문자열은 자동 수정하지 않고 quality_flag로 관리.

---

# 28. Ambiguity 보존

예: 배전설비가 여러 context에 연결되면 하나만 강제 선택하지 않고 복수 mapping 허용. 검색 시 context와
ranking으로 해결.

---

# 29. 전문용어 자동 추출

각 source에서 명사성 기술용어 후보 추출: 공정, 작업, 설비, 기계, 장치, 부품, 위험요인, 유해인자,
안전조치, 점검항목, 법정용어, 화학물질, 측정항목, 보호구, 재해유형, 공법.

---

# 30. 자동 추출 ≠ 승인

추출 결과는 PROPOSED일 뿐. 자동으로 synonym/canonical 관계를 확정하지 않는다.

---

# 31. Kiwi 조사

구현 환경에서 사용 가능한 최신 안정 `kiwipiepy` 조사. 기록: kiwipiepy version, Python version, model
package version, platform. 공식 문서 기준으로 API signature 재확인.

---

# 32. Kiwi 역할

사용: 한국어 형태소 분석, 복합 기술용어 tokenization, 검색 query 분석, 미등록어 후보 탐색,
사용자사전 적용. 비사용: canonical merge, semantic truth 결정, legal applicability.

---

# 33. Kiwi Baseline Audit

user dictionary 투입 전 baseline analyzer 결과 측정. 예시 용어: 밀폐공간작업, 위험성평가,
국소배기장치, 수변전설비, 배전설비공사, 산소결필, 중량물취급, 산업용로봇, 방폭구조,
작업계획서. 각각 before_tokens 저장.

---

# 34. Kiwi User Word 선정 기준

(1) 산업 전문 복합어 오분절 (2) 약어 보존 필요 (3) 제품/설비/공법명 token boundary 중요 (4) 검색
recall 실제 개선. 모든 전문용어를 무조건 넣지 않는다.

---

# 35. Kiwi User Dictionary와 Phrase 분리

Kiwi user word는 기본적으로 공백 없는 기술복합어 중심(국소배기장치, 위험성평가, 밀폐공간작업,
산업용로봇). 공백 있는 구(국소 배기 장치 등)는 search alias/phrase layer에서 별도 관리.

---

# 36. Kiwi POS 정책

모든 단어를 NNP로 넣지 않는다. baseline과 용어성격을 보고 NNG/NNP/SL 등 실제 Kiwi 지원 tag
확인 후 적용. 근거 문서화.

---

# 37. Kiwi Artifact

`TAI_KIWI_USER_DICTIONARY_v1.txt` 및 machine-readable `TAI_KIWI_TERMS_v1.tsv`. 필수: term, pos, score,
source_term_id, reason, before_analysis, after_analysis, status.

---

# 38. Kiwi Quality Gate

user dictionary 적용 전/후 비교. 전문용어 token preservation이 악화되는 entry는 제외.

---

# 39. Master Term Artifact

`TAI_TERM_MASTER_v1.tsv`. 필수: term_id, term_original, term_normalized, term_type, language,
pos_hint, subject_type, subject_key, canonical_id, status, source_id, source_key, evidence_ref,
quality_flag, curation_method, created_from_snapshot.

---

# 40. Term Relations Artifact

`TAI_TERM_RELATIONS_v1.tsv`. 필수: relation_id, source_term_id, target_term_id, relation_type,
status, evidence_ref, confidence, curation_method.

---

# 41. Dictionary Semantic Curation

Claude는 검색사전 영역에서 약어/동의어/현장용어/표기변형/영문명 판정 가능. 단 "두 TAI canonical concept이
사실 같다"는 결정은 하지 않고 필요시 CANONICAL_REVIEW_REQUIRED로 남긴다.

---

# 42. Alias와 Synonym 구분

국소배기장치/국소배기설비는 evidence 충분시 SYNONYM 가능. 환기설비/국소배기장치는 보통
broader/related이므로 무조건 synonym으로 두지 않는다.

---

# 43. 검색 Index 데이터 모델

DB 구현 전 repository conventions 조사. 권장 논리구조: search_terms, search_term_subjects,
search_term_relations, search_term_tokens, search_dictionary_snapshots. 실제 관례에 맞춰 단순화 가능.

---

# 44. Production Migration 정책

migration SQL 작성 허용. production apply = FORBIDDEN. Owner 승인 전 production migration 실행 금지.

---

# 45. 권장 search_terms

id, term_original, term_normalized, term_type, language, pos_hint, status, priority, metadata,
created_at, updated_at.

---

# 46. 권장 Subject Link (search_term_subjects)

term_id, subject_type, subject_key, canonical_id nullable, relation_type, status, evidence.

---

# 47. Canonical ID nullable — 필수

canonical 미존재 term도 사전에 존재 가능해야 한다.

---

# 48. Search Document (projection)

subject_key, primary_display, aliases, approved_terms, tokens, normalized_text, source_context.

---

# 49–57. 검색 단계 / Tier

Tier1 Exact → Tier2 Normalized Exact → Tier3 Approved Alias/Synonym(APPROVED만) → Tier4 Kiwi Token →
Tier5 Domain Expansion(승인된 abbreviation/synonym만; SDS→MSDS, LEV→국소배기장치) → Tier6 pg_trgm
fallback(GiST/GIN benchmark 후 선택; TRIGRAM ≠ SYNONYM) → Tier7 Future Semantic(V1 OUT OF SCOPE,
adapter boundary만).

---

# 58–59. Search Service / API

기존 tai-api 구조·API conventions 조사 후 구현. 개념 예: search_dictionary_svc.py,
search_query_svc.py / GET /search, GET /search/terms. 실제 명칭은 repository convention 우선.

---

# 60–61. Search Request / Response

Request 최소: q, limit, subject_type?, sector?. Response 최소: query, normalized_query, tokens,
items[]{subject_type, subject_key, display_name, matched_term, match_type, score, evidence}.

---

# 62–65. Ranking Explainability / 우선순위 / Ambiguity / Context

각 result는 최소 match_type, matched_term 반환(EXACT/NORMALIZED_EXACT/ALIAS/SYNONYM/TOKEN/TRIGRAM).
LLM opaque score 금지. 기본 우선순위: EXACT > NORMALIZED EXACT > APPROVED ALIAS > APPROVED SYNONYM >
ABBREVIATION > TOKEN MATCH > TRIGRAM. 복수 subject 연결 시 강제 단일 반환 금지. context(sector/object_type/
page/factory/process/equipment) 활용하되 없는 context 추정 금지.

---

# 66–67. Dictionary Compiler / CLI

deterministic compiler(`tools/search_dict/build_dictionary.py` 또는 repo convention). 동일 snapshot →
동일 output SHA 필수. CLI 최소 명령: census, build, validate, export-kiwi, benchmark.

---

# 68. Validation

duplicate term_id, invalid relation, missing subject, invalid status, self relation, cycle where
forbidden, unknown relation_type, empty term, untraceable source.

---

# 69–73. Benchmark / Category / 품질 Gate

`SEARCH_BENCHMARK_v1.tsv` 직접 생성. Category 최소: EXACT, SPACING, PUNCTUATION, ABBREVIATION,
SYNONYM, FIELD_TERM, MORPHOLOGY, COMPOUND_NOUN, ENGLISH_KOREAN, TYPO, AMBIGUOUS, NO_MATCH.
허위 target 금지. 품질 Gate: exact Top-1=100%, approved alias Top-3>=98%, spacing/punctuation
Top-3>=98%, abbreviation/domain synonym Top-3>=95%, typo/trigram Top-5>=90%. 규모 부족 시 수치만 맞추려
데이터 왜곡 금지.

---

# 74–75. Zero False Canonical Mutation / Performance

search run으로 인한 canonical DB mutation = 0 (hard gate). test 환경에서 p50/p95/p99 기록.

---

# 76–77. Dictionary Statistics / 품질지표

unique source terms, unique normalized terms, approved aliases/synonyms/abbreviations, field terms,
English terms, Kiwi user words, ambiguous terms, HOLD terms, subjects linked, unlinked terms /
provenance coverage, subject linkage coverage, approved relation coverage, ambiguous rate, orphan
rate, duplicate rate, Kiwi improvement rate, benchmark recall.

---

# 78–80. 전문용어 판정 Audit / confidence / 승인 정책

`TERM_SEMANTIC_DECISIONS_v1.tsv`(decision_id, term, decision_type, decision, reason, evidence,
confidence). confidence HIGH/MEDIUM/LOW; LOW 자동 APPROVED 금지. Claude는 명백한 SOURCE_NAME/
SPACING_VARIANT/PUNCTUATION_VARIANT/명백한 공식 약어는 evidence 기반 APPROVED 가능. 의미적 위험 큰
SYNONYM/BROADER/NARROWER/복수 canonical 연결은 evidence 약하면 REVIEWED/HOLD.

---

# 81–83. Legal / Chemical / 설비 용어 특별 정책

법령용어는 LEGAL_TERM metadata로 구분, 법적 의미 동일성 자동 선언 금지. 화학물질은 국문명/영문명/CAS/
관용명 연결(CAS는 형태소 분석 안 함). 설비는 공식명/현장명/약칭/제조업·건설업 표현/영문명 고려.

---

# 84–88. 원칙 보강

Source Name 삭제 금지. 자동 생성 변형 제한(띄어쓰기 경우의 수 무한 생성 금지). Compound splitting 시
원형 term identity 유지(위험성/평가 → 위험성평가 유지). Query expansion upper bound. 검색문자열
parameterized query, raw SQL interpolation 금지.

---

# 89–90. Logging

개인정보 없이 normalized query/result count/latency/match type 정도만. 이번 프로젝트 production search
logging 기본 disabled 또는 익명 집계만.

---

# 91–92. DB Migration / Existing Tests 보호

migration idempotent. local/test 허용, staging 조건부 허용, production 금지. RISK/CHEM/GRAPH/LEGAL/
SaaS test에 regression 금지.

---

# 93–96. 테스트 / Determinism / No Network Runtime / LLM 역할

테스트: normalization, contract, relation validation, kiwi dictionary, query analysis, exact/alias/morph
search, trigram fallback, ambiguity, benchmark, determinism. TERM_MASTER/TERM_RELATIONS/KIWI_DICTIONARY/
BENCHMARK input/runtime projection 두 번 생성 시 동일 SHA. runtime external LLM calls = 0.
LLM은 구축 research/curation에만; runtime은 deterministic lexical engine.

---

# 97. Repository 문서 구조

docs/knowledge/search-dict/ : SEARCH_CONSTITUTION_v1.md, SEARCH_TERM_CONTRACT_v1.md,
TERM_SOURCE_CENSUS_v1.tsv, TAI_TERM_MASTER_v1.tsv, TAI_TERM_RELATIONS_v1.tsv,
TERM_SEMANTIC_DECISIONS_v1.tsv, TAI_KIWI_TERMS_v1.tsv, TAI_KIWI_USER_DICTIONARY_v1.txt,
SEARCH_BENCHMARK_v1.tsv, SEARCH_BENCHMARK_RESULT_v1.tsv, SEARCH_ENGINE_ARCHITECTURE_v1.md,
SEARCH_FINAL_AUDIT_v1.md, TAI_SEARCH_DICT_FINAL_HANDOFF.md. 실제 repo 규칙이 다르면 동일 의미의
existing convention을 따른다.

---

# 98–109. Phase 구조

P1 Repository Census → P2 Source Census → P3 Constitution/Contract → P4 Raw Term Extraction →
P5 Normalization → P6 Semantic Curation → P7 Kiwi Integration → P8 Storage/Compiler →
P9 Search Service → P10 Benchmark → P11 Regression → P12 Final Audit.

---

# 110–112. Final Exit Criteria / 판정

Governance/Source/Dictionary(invalid relation 0, untraceable approved 0, duplicate term_id 0)/Kiwi/
Search/Benchmark/Determinism/Regression/Canonical mutation 0/Production DB mutation 0. 최종 상태는
READY_FOR_OWNER_APPROVAL / CONDITIONAL_READY / BLOCKED 중 하나.

---

# 113–115. Git / PR / Merge

논리 단위 commit. 별도 PR 생성, 제목 권장 "feat(search): add TAI Korean domain dictionary and lexical
search". PR body에 Canonical mutation=0, Legal applicability judgment=0, Production DB write=0, RISK-04
mutation=0 명시. MERGE = OWNER DECISION (Claude 자동 merge 금지).

---

# 116–118. RISK-04 연결 / Export / 병렬성

RISK canonical 승인 후 별도 linkage로 review concept/source → canonical UUID → search terms 연결.
dictionary schema는 이 linkage를 받을 수 있어야 한다. Export: canonical/source key → approved search
aliases/abbreviations/Kiwi user words. RISK canonical project ≠ blocked by search dictionary,
Search dictionary ≠ blocked by canonical UUID absence.

---

# 119–120. 최종 인수인계서

`TAI_SEARCH_DICT_FINAL_HANDOFF.md` 생성. 필수: repository, branch, PR, main anchor, HEAD, architecture,
DB schema, API endpoints, source list, term/relation counts, Kiwi version/dictionary count, benchmark
results, latency, tests, CI, migration/production status, known HOLD/ambiguities/limitations,
canonical integration status, next recommended action.

---

# 121. 최종 반환 형식

작업 종료 시 MASTER WO / OBJECT / STATUS / REPOSITORY / BRANCH / PR / BASE MAIN SHA / HEAD SHA /
각 PASS-FAIL 항목 / count / KIWI / SEARCH / BENCHMARK / LATENCY / DETERMINISM / MIGRATION /
MUTATION 0 / TESTS / CI / FINAL AUDIT / FINAL HANDOFF / MERGE=NOT EXECUTED / NEXT=OWNER REVIEW /
STOP 형식으로 한 번에 반환.

---

# 122–124. Hard STOP / 절대 금지 / 품질 우선순위

Hard STOP: RISK-04 frozen artifact 수정, canonical 의미 변경, similarity 기반 canonical 자동 merge,
production DB write, production migration, 법령 applicability 판단, legal obligation 판단, credential 부재,
사용권 불허 데이터 전체 복제. 금지: 동일이름=동일개념 자동판정, Kiwi token=canonical identity,
fuzzy=synonym 자동승인, trigram=semantic equivalence, LLM score=production search truth, 검색어로 법률
적용성 판정, canonical DB 자동 수정, RISK-04 merge, production DB 자동 write, 사용자 승인 없이 PR
merge. 품질 우선순위: 1.정확성 2.추적가능성 3.검색 recall 4.deterministic 5.성능 6.구현편의성.

---

# 125–126. 최종 목표 상태 / 실행 시작

정상 종료 시 TAI는: TAI Canonical Concepts →(linkage)→ TAI Search Dictionary(Alias/Synonym/
Abbreviation) → Kiwi User Dictionary → Korean Morph Analysis → Lexical Search → pg_trgm fallback →
Ranked Results 구조를 갖는다. 장기 자산은 검색엔진 자체가 아니라 TAI가 소유하는 산업안전 전문용어사전
+ canonical 연결 가능한 검색 언어 그래프. Kiwi는 교체 가능한 분석엔진. 실행 시작: repository/main 조사 →
branch 생성 → census → Constitution/Contract → 이후 단계 연속 수행. START.
