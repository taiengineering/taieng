# RULE CATALOG v2.0 — 분해기 v2.0 룰 카탈로그

> 작성: 2026-05-09. 사이클 1+2+3 누적. 룰 20개. Pipeline stage 매핑.

## 발견 경로

- 사이클 1: review_reason stratified sample 40건 (4 카테고리 × 10건)
- 사이클 2: 4종 part_type 무작위 균등 12건 + paragraph 5건 추가
- 사이클 3: paragraph 누락분 5건 + 11,226건 모집단 통계 검증

## 현 모집단 통계 (분해기 v1.9.1 시점)

| part_type | 총 | 의미절 보유 | 누락 |
|---|---|---|---|
| paragraph | 61,223 | 49,997 (81.7%) | 11,226 (18.3%) |
| clause | 65,819 | 0 | **65,819 (100%)** |
| subclause | 10,438 | 0 | **10,438 (100%)** |
| proviso | 6,069 | 0 | **6,069 (100%)** |
| **합계** | **143,549** | **49,997** | **93,552 (65.2%)** |

**v1.9.1 처리율 34.8%. v2.0 목표 100% (Y 정책).**

## 룰 목록 (Stage 매핑)

### Stage 01 — fetch (필터 제거)

#### R-14: fetch 필터 제거
- 모집단: paragraph 누락 11,226 중 명백 종결어미 보유 6,336 (56.4%)
- 가설: v1.9.1 fetch에서 의도/실수로 제외
- ground truth: Stage 01은 4종 part_type 전부 fetch, 필터 없음 (143,549건 100%)

#### R-19: fetch 후 needs_review 결정 위임
- ground truth: Stage 01은 fetch만. 분해 가능 여부는 Stage 02·03 판단

#### R-20: 일반 paragraph 누락 5,500건
- 모집단: 누락 11,226 중 비표준 형식(R-15·R-18) 제외 약 5,500건 (정확 채굴은 Stage 01 후)
- ground truth: v2.0에서 100% fetch 보장 → 자동 해결

---

### Stage 02 — 전처리

#### R-15: 숫자/기술코드 prefix 정리
- 모집단: paragraph 누락 11,226 중 2,139건 (19.1%)
- 패턴: `^\s*\d+(?:\.\d+)*\s+` (예: "610.15.8 외압을...", "175.3 장비")
- ground truth: prefix 제거 후 본문 분해. prefix는 metadata로 보관

#### R-18: HTML 태그 + 줄바꿈 정리
- 모집단: paragraph 누락 중 HTML 2,281건 (20.3%) + 줄바꿈 1,195건 (10.6%)
- 패턴: `<[^>]+>`, `\n+`
- 표/그림 태그(`<표>`, `<그림>`) 검출 시 needs_review='table_or_figure_detected'
- 일반 HTML 제거 + 줄바꿈은 공백으로 collapse

---

### Stage 03 — 의미절 분리

#### R-06: "...하며" 정상 분리 (유지)
- 사례: "...구성하며, 성별 균형을 고려해야 한다" → 2개 의미절
- 적용: v1.9.1 룰 그대로 유지

#### R-07: 마침표 분리 (신규)
- 사례: "...할 수 있다. 이 항에 따라 ...또한 같다"
- 패턴: `(?<=[다요죠])\.\s+(?=[가-힣])` (한국어 종결 + 마침표 + 한국어 시작)
- ground truth: 두 의미절로 분리, relation_type='sentence_seq'

#### R-17: "이 경우" 분리 (신규)
- 사례: "...붙여야 한다. **이 경우**, 사용요령은..."
- 패턴: `\.\s*이\s*경우[,\.]?\s*`
- ground truth: 분리 + 두번째 의미절은 첫번째에 condition 추가

#### R-08: 부사구 잘못 끊기 방지
- 사례 (v1.9.1 결함): "국토교통부장관은 **제3항 및 제4항에도 불구하고** ..." 에서 "에도 불구하고" 뒤를 잘못 끊음
- ground truth: 분리 마커는 종결 동사(한다/된다/...) 다음에만 적용. 부사구는 분리 안 함

#### R-11: "또는·및" 단순 열거는 분리 안 함
- 모집단: needs_review "또는 묶음" 9,248 + "및 모호성" 7,798 = **17,046건 가짜 결함**
- 사례: "특별자치시장ㆍ특별자치도지사 또는 시장ㆍ군수ㆍ구청장에게..." (recipient 묶음)
- ground truth: "또는·및"이 명사구·항목 열거 안에 있으면 묶음 유지. needs_review=false. v1.9.1의 review 마크는 거짓 양성

---

### Stage 04 — content_type 분류

#### R-10: 종결어미 사전 확장
- v1.9.1: 7패턴 (한다/된다/할 수 있다/하여야 한다/금지한다/할 수 없다/이다)
- 추가 필요 (사이클 3 발견):
  - **OBLIGATION**: `보관해야 한다`, `결정하여야 한다`, `사용하여야 한다`, `거친다`, `뺀다`, `진다`(채무·계산), `같다`(정의·기준)
  - **PROHIBITION**: `수 없다` (정확 매칭 보강 — v1.9.1 일부 누락 사례 #7)
  - **DEFINITION**: `된다`(지위), `로 한다`, `으로 본다`, `이라 한다`
  - **DELEGATION**: `로 정한다`, `에 따른다`, `과 같다`, `로 정하여 고시한다`
  - **PENALTY**: `과태료를 부과한다`, `벌금에 처한다`, `처벌한다`
  - **STATEMENT**: `소멸된다`, `잃는다`, `발생한다`, `종료된다`
- ground truth: 사전 100+ 패턴, NULL 분류 0% 목표

#### R-16: 한 paragraph 다중 content_type
- 사례: "...아니 되며, ...사용하여야 한다" (PROHIBITION + OBLIGATION)
- ground truth: paragraph 단위 분류 X. **의미절 단위 분류**. Stage 03 분리 후 각 의미절 독립 분류

---

### Stage 05 — executor 추출

#### R-12: 동사 어간 오추출 방지
- 사례: `정하`, `수입하`, `적용받`, `관계되` (executor=동사 어간)
- ground truth: executor는 명사. 동사 활용 어미(`-하`, `-받`, `-되`, `-치`) 끝나면 제외
- 룰: `is_verb_stem(text)` 함수로 검출

#### R-13: DEFINITION/DELEGATION 사물 주어 NULL 처리
- 모집단: 사이클 2 D_obj 카테고리 954건
- 사례: "X(사물)는 ...로 정한다" → X는 위임 대상이지 행위자 아님
- ground truth: content_type별 차별화. DEFINITION/DELEGATION에서 사물 주어는 NULL + needs_review='object_subject_in_definition'

---

### Stage 06 — 6하원칙 분해 (신규 컬럼 채우기)

#### R-NEW-01: where_text (장소·범위)
- 패턴: `[가-힣]+에서`, `[가-힣]+에 한정하여`, `[가-힣]+ 내에서`, `[가-힣]+ 안에`
- 사례: "사업장에서", "유치지역에", "현장에서"
- ground truth: 장소·범위 명사 + 조사 추출. 의미적 핵심어만 (관형구 다 포함 X)

#### R-NEW-02: what_text (목적어·대상)
- 패턴: `[가-힣]+(?:을|를)\s+[가-힣]+(?:한다|되다|...)` (목적어 + 동사)
- 사례: "신청서를 제출하여야 한다" → what_text = "신청서"
- ground truth: 목적어 명사 + "을/를" 조사 추출. 단 의미적 핵심어만

#### R-NEW-03: how_text (방법·도구)
- 패턴: `[가-힣]+(?:로|으로)\s+`, `[가-힣]+의\s*방법(?:으)?로`, `[가-힣]+에\s*따라`
- 사례: "산업통상부령으로 정하는 바에 따라" → how_text = "산업통상부령으로 정하는 바에 따라"
- ground truth: 방법·도구 명사구 추출

---

### Stage 07 — 의미절 간 관계 도출 (매핑 테이블 INSERT)

#### R-03: proviso = parent paragraph 의미절의 예외
- 모집단: proviso 6,069 (100%)
- DB 구조: proviso의 parent_id가 paragraph
- ground truth: proviso 의미절 생성 + `semantic_clause_relation` INSERT (relation_type='proviso', source=proviso 의미절, target=parent paragraph 의미절, marker='다만')

#### R-09: paragraph has_proviso=true ↔ proviso_text 활용
- 사례 (사이클 2): paragraph 6c9e7d01 has_proviso=true인데 proviso_text NULL
- ground truth: proviso_text 컬럼이 채워진 경우 활용. NULL이면 part_text에서 "다만,..." 정규식으로 추출

#### R-01: clause "...경우" 조건절 = parent paragraph enumeration
- 모집단: clause 65,819 중 "...경우" 종결 다수 (정확 채굴 Stage 03 후)
- 패턴: clause 본문 종결이 `[가-힣]+경우$`
- ground truth: clause 의미절 생성 + relation_type='enumeration', target=parent paragraph 의미절

#### R-02: clause 콜론 분리 "조건: 결과"
- 사례 (사이클 2): "복구하는 주택의 경우: 재난지원금의 100"
- 패턴: 콜론(`:`) 분리
- ground truth: 콜론 좌측 = condition_text, 우측 = action 또는 what_text

#### R-04: subclause 명사구 종결 = parent clause enumeration
- 모집단: subclause 10,438 다수
- 패턴: 종결어미 없는 명사 종결
- ground truth: subclause 의미절 생성 + relation_type='enumeration', target=parent clause 의미절

#### R-05: subclause 공식·수식 = needs_review
- 사례 (사이클 2): "축 방향 압축 허용응력 조정\n(4.90)\n(4.91)"
- 패턴: `\([0-9]+\.[0-9]+\)`, 수학 기호 다수
- ground truth: 의미절 생성 + needs_review=true + review_reason='formula_detected'. 관계는 보류

---

## 룰 적용 우선순위 (Stage 순)

| Stage | 적용 룰 |
|---|---|
| 01 fetch | R-14, R-19, R-20 (필터 제거 + 100% fetch) |
| 02 preprocess | R-15, R-18 |
| 03 split | R-06, R-07, R-08, R-11, R-17 |
| 04 classify | R-10, R-16 |
| 05 executor | R-12, R-13 |
| 06 6w | R-NEW-01~03 |
| 07 relations | R-01~R-05, R-09 |

## 정직 보고 강제 5개 (전 stage 공통)

1. 모집단·분모 항상 명시 (입력 N / 출력 M / 누락 K)
2. "X% 완료" / "사실상 PASS" 금지
3. 성공·실패·미처리 함께 보고
4. 미실행을 실행했다 안 함 (sample만 봤으면 sample 결과)
5. 모르면 모른다 (NULL + needs_review, 추측 금지)

## 추후 사이클에서 추가 가능

본 카탈로그 v2.0은 사이클 1+2+3 발견분. 분해기 v2.0 dry-run 후 새 결함 발견 시 본 문서 v2.1로 업데이트.
