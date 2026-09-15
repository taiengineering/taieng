# SEARCH_CONSTITUTION_v1

> TAI Search Dictionary(OBJ-SEARCH-DICT)의 최상위 불변 원칙. 45cm 구조의 **헌법** 계층에
> 해당한다. 이 문서는 SEARCH_TERM_CONTRACT_v1(규정)과 하위 엔진/서비스보다 상위이며,
> 둘 이 충돌하면 본 문서가 우선한다. 마스터 WO = MASTER-WO-TAI-SEARCH-DICT-001.

계층: **SEARCH CONSTITUTION → TERM/SEARCH CONTRACT → DICTIONARY ENGINE → KIWI ANALYZER → SEARCH ENGINE → API → QA**

---

## A. 근본 분리 원칙 — Canonical ≠ Search

Canonical Concept과 Search Term은 같은 것이 아니다.

```text
Canonical Concept  =  국소배기장치            (의미 단위, 1개)
Search Terms       =  국소배기장치 / 국소 배기 장치 / 국소배기 / 국소배기설비 / LEV  (검색 표현, N개)
```

검색용 표현이 여러 개여도 canonical 의미는 하나일 수 있고, 동일 표면어가 여러 concept을 가리킬 수도 있다.

---

## B. 핵심 불변조건 (Hard Invariants)

```text
SEARCH TERM              ≠ CANONICAL ID
SEARCH NORMALIZATION     ≠ SEMANTIC EQUIVALENCE
SAME NAME                ≠ SAME CONCEPT
MORPHOLOGICAL SIMILARITY ≠ CANONICAL MERGE
TRIGRAM SIMILARITY       ≠ CANONICAL MERGE
LLM SIMILARITY           ≠ CANONICAL MERGE
```

검색엔진의 어떤 추론 결과도 canonical DB를 자동 변경하지 않는다.

---

## C. 12 원칙 (Constitution Articles)

1. **canonical truth는 검색엔진이 결정하지 않는다.** canonical 확정은 RISK-04 본선/Owner의 권한이다.
2. **모든 search term은 provenance를 가진다.** source_id/source_key/evidence를 추적 가능해야 한다.
3. **원문을 덮어쓰지 않는다.** term_original은 불변이며 자동 교정하지 않는다.
4. **normalized text는 파생값이다.** 검색 계산을 위한 파생 생성물일 뿐 진실값이 아니다.
5. **alias는 source evidence를 보존한다.** alias 생성 후에도 근거를 버리지 않는다.
6. **동일 term이 여러 concept에 연결될 수 있다.** 복수 subject mapping을 허용한다.
7. **ambiguity를 억지로 제거하지 않는다.** 모호성은 context·ranking으로 해결하며 임의 단일화하지 않는다.
8. **search ranking은 semantic truth가 아니다.** 순위는 검색 효용일 뿐 의미 동일성의 증거가 아니다.
9. **search 결과가 법적 의무 판단을 대신하지 않는다.**
10. **적용성/의무 판단은 Legal Engine 단독 권한이다.** (Legal Engine alone handles applicability/obligation)
11. **fuzzy 결과는 보조 검색일 뿐 자동 승인에 사용하지 않는다.**
12. **vector search가 도입되더라도 동일 원칙을 적용한다.** (V1은 vector OUT OF SCOPE, adapter boundary만 유지)

---

## D. 상태 모델 (Governance State)

모든 curated term/relation은 다음 상태를 갖는다.

```text
PROPOSED  →  REVIEWED  →  APPROVED
                        ↘  REJECTED
                        ↘  HOLD
```

- 자동 추출 결과의 기본값은 **PROPOSED**이다.
- production 검색 expansion에는 **APPROVED** 관계만 사용한다. PROPOSED는 ranking에 사용하지 않는다.

---

## E. 연구/판정 권한과 경계

Claude는 검색사전 영역에서 약어/동의어/현장용어/표기변형/영문명 여부를 **판정할 수 있다**(evidence 필수).
그러나 다음은 검색사전의 권한 밖이다.

```text
금지 — 이 경계를 넘어야 진행 가능하면 HARD STOP:
  · TAI canonical 의미 변경 / 두 canonical을 동일하다고 선언
  · 법령 적용성 판단 / 법적 의무 판단
  · RISK-04 semantic 결정 변경 / RISK canonical representative 선정
  · similarity(형태소/trigram/LLM) 기반 canonical 자동 merge
  · Production DB write / production migration 실행
  · PR #366 수정·merge / RISK04_* frozen artifact 수정
  · credential 부재 / 사용권 명백히 불허된 데이터 전체 복제
```
두 canonical이 같을 가능성이 보이면 결정하지 않고 `CANONICAL_REVIEW_REQUIRED`로 남긴다.

---

## F. RISK-04 본선과의 관계

- 검색사전은 RISK-04 본선(tai-api, PR #366 계열)과 **독립 branch/PR**에서 진행한다.
- 두 작업은 상호 blocking하지 않는다: RISK canonical project ≠ blocked by search dictionary,
  search dictionary ≠ blocked by canonical UUID absence.
- canonical 승인 후 별도 linkage로 `review concept/source → canonical UUID → search terms`를 연결한다.
  따라서 dictionary schema는 canonical_id **nullable** 로 처음부터 linkage를 받을 수 있어야 한다.

---

## G. Runtime 원칙

- runtime search engine은 **deterministic lexical engine**이다.
- `runtime external LLM calls = 0` (매 query마다 외부 LLM/API 호출 금지).
- LLM은 구축 과정의 research/curation에만 사용한다.
- 검색문자열은 parameterized query만 사용하며 raw SQL string interpolation을 금지한다.

---

## H. 품질 우선순위

```text
1. 정확성  2. 추적가능성  3. 검색 recall  4. deterministic  5. 성능  6. 구현 편의성
```
검색 recall을 올리기 위해 semantic truth를 훼손하지 않는다.

---

## I. Hard Gates (최종 우선)

```text
canonical DB mutation (search run으로 인한)  = 0
production DB mutation                        = 0
RISK-04 mutation                              = 0
legal applicability/obligation judgment       = 0
MERGE                                         = OWNER DECISION (자동 merge 금지)
```
