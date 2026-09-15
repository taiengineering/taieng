# SEARCH_TERM_CONTRACT_v1

> TAI Search Dictionary의 **규정** 계층. SEARCH_CONSTITUTION_v1(헌법) 하위이며, 데이터 타입·관계·
> 상태·증거·식별자·normalization·산출물 스키마를 정의한다. 모든 tests는 이 Contract를 기준으로 검증한다.

---

## 1. Term Type

```text
CANONICAL_NAME      승인된 canonical의 공식 표시명 (canonical 미확정 대상에 남발 금지)
SOURCE_NAME         원천데이터에 실제 존재하는 명칭
ALIAS               같은 대상의 다른 일반적 표현
SYNONYM             의미적 동일/검색상 동등으로 취급할 승인된 표현
ABBREVIATION        약어 (MSDS, SDS, LEV, SCP, GCP 등)
FIELD_TERM          현장에서 흔히 사용하는 표현
ENGLISH_TERM        영문 기술명
SPELLING_VARIANT    철자/표기 변형
SPACING_VARIANT     띄어쓰기 변형
PUNCTUATION_VARIANT 기호 차이
SEARCH_PHRASE       공백 포함 검색구 (phrase layer)
KIWI_USER_WORD      Kiwi 사용자사전 단어
```
확장 가능하나 사용 전 본 Contract에 먼저 추가 기록한다.

---

## 2. Relation Type

```text
EXACT_ALIAS  SYNONYM_OF  ABBREVIATION_OF  ENGLISH_OF  FIELD_TERM_OF
SPELLING_VARIANT_OF  SPACING_VARIANT_OF  PUNCTUATION_VARIANT_OF
RELATED_TERM  BROADER_SEARCH_TERM  NARROWER_SEARCH_TERM  AMBIGUOUS_WITH
```

- `RELATED_TERM`을 synonym처럼 사용하지 않는다.
- 예: 환기설비 / 국소배기장치 는 보통 BROADER_SEARCH_TERM 관계이지 SYNONYM이 아니다.

---

## 3. 상태 모델

```text
PROPOSED  REVIEWED  APPROVED  REJECTED  HOLD
```
자동 추출 기본값 = PROPOSED. production expansion은 APPROVED만 사용.

---

## 4. Evidence Model

각 term/relation은 가능한 경우 다음을 저장한다.

```text
source_id  source_key  source_text  evidence_ref  evidence_type  confidence  curation_method
```

curation_method 예: `SOURCE_EXACT`, `RULE_DERIVED`, `MANUAL_SEMANTIC`, `OFFICIAL_GLOSSARY`, `DOMAIN_RESEARCH`
confidence: `HIGH` / `MEDIUM` / `LOW` (LOW는 자동 APPROVED 금지)

---

## 5. Deterministic Term ID

```text
payload = source_id + "\n" + source_key + "\n" + term_type + "\n" + original_term
term_id = SHA256_UTF8(payload)
```

이 term_id는 **canonical ID가 아니다.** 동일 snapshot → 동일 term_id 를 보장하기 위한 내부 식별자이다.

---

## 6. 원문 보존과 Normalization

원문은 불변(`term_original`). 파생 검색필드만 별도 생성한다.

```text
term_normalized     Unicode normalization + whitespace 정리
term_compact        공백 제거 검색 copy
term_latin_lower    Latin lowercase search copy
term_no_punctuation 명백한 punctuation 제거 copy
```

기본 normalization(보수적, 원본 미적용): Unicode normalization, leading/trailing whitespace 제거,
연속 whitespace 축약, Latin lowercase search copy, 명백한 punctuation search copy.

**자동 오탈자 교정 금지**: 잘린 원문/오탈자 의심/`N=`/`(`/깨진 분류 문자열은 수정하지 않고
`quality_flag`로 관리한다. 띄어쓰기 경우의 수를 무한 생성하지 않고 검색에 의미 있는 variant만 생성한다.

---

## 7. Subject Link Contract

```text
subject_type  subject_key  canonical_id (nullable)  relation_type  status  evidence
```

허용 subject_type: `RISK_REVIEW_CONCEPT`, `RISK_SOURCE`, `LEGAL_TERM`, `KOSHA_TERM`, `KALIS_TERM`,
`CHEM_TERM`, `ACCIDENT_TERM`, `EQUIPMENT_TERM`, `GENERAL_TERM` (확장 시 Contract 먼저 기록).

`canonical_id`는 nullable — canonical 미존재 term도 사전에 존재 가능. 동일 term이 복수 subject에 연결 가능.

---

## 8. Snapshot Identity

가능한 모든 입력은 `source_id / snapshot_date / source_checksum / source_row_key`를 가진다.

---

## 9. Artifact Schema

### TAI_TERM_MASTER_v1.tsv
```text
term_id  term_original  term_normalized  term_type  language  pos_hint
subject_type  subject_key  canonical_id  status
source_id  source_key  evidence_ref  quality_flag  curation_method  created_from_snapshot
```

### TAI_TERM_RELATIONS_v1.tsv
```text
relation_id  source_term_id  target_term_id  relation_type  status  evidence_ref  confidence  curation_method
```

### TERM_SEMANTIC_DECISIONS_v1.tsv
```text
decision_id  term  decision_type  decision  reason  evidence  confidence
```

### TAI_KIWI_TERMS_v1.tsv
```text
term  pos  score  source_term_id  reason  before_analysis  after_analysis  status
```

---

## 10. 승인 정책 (Approval Policy)

명백하고 위험이 낮은 유형은 evidence 기반으로 Claude가 **APPROVED** 가능:
```text
SOURCE_NAME, SPACING_VARIANT, PUNCTUATION_VARIANT, 명백한 공식 약어(ABBREVIATION)
```
의미적 위험이 큰 유형은 evidence가 약하면 **REVIEWED 또는 HOLD**:
```text
SYNONYM, BROADER/NARROWER, 복수 canonical 연결
```

---

## 11. 도메인 특별 정책

- **Legal**: 법령용어는 `LEGAL_TERM` metadata로 구분. 검색 expansion은 가능하나 법적 의미 동일성을
  자동 선언하지 않는다.
- **Chemical**: 국문명/영문명/CAS/관용명을 검색용으로 연결 가능. **CAS는 형태소 분석하지 않는다.**
- **Equipment**: 공식명/현장명/약칭/제조업·건설업 표현/영문명 변형 고려.

---

## 12. Validation 규칙 (compiler/tests가 검사)

```text
duplicate term_id / invalid relation / missing subject / invalid status / self relation
cycle where forbidden / unknown relation_type / empty term / untraceable source
```
