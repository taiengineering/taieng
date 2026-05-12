# [Track B] 2026-05-09 Step 2-E + Step 3 — Cross-validate + 외부 인용

**선행**: Step 2-D 완료 (inheritance 8,641건 99.7% 매핑)

---

## Done

### Step 2-E: source × inheritance cross-validate 검증 엔진

**알고리즘**:
- delegation (본법 위임 표현 추출) ↔ inheritance (시행령/시행규칙 인용 추출)
- 본법 article 단위로 두 데이터셋 일치 확인
- 양방향 일치 = 위임 관계 confirmed

**전체 LAW (123건) 단위 결과**:

| 검증결과 | cnt | 비율 |
|---|---|---|
| 양방향 일치 | 3,151 | **86.5%** |
| 위임표현만 (자식 인용 X) | 282 | 7.7% |
| 자식 인용만 (위임표현 X) | 210 | 5.8% |

**해석**:
- ✓ 양방향 일치 = 위임 관계 cross-validate 통과
- ⚠ 위임표현만 = 룰 V1 첫 매칭 한계 (자식 article의 첫 매칭이 다른 조 인용일 때)
- ⚠ 자식 인용만 = 본법에 위임 동사 없는 정책 article 인용 (정상, 예: 본법 제4조 "정부의 책무")

**산안법 sample (20건)**:
- 양방향 일치: 17건 (85%)
- 본법 제3조: 위임표현만 (시행령에서 인용했지만 first 매칭 X)
- 본법 제4조 / 제5조: 자식 인용만 (정책 article 인용)
- 본법 제9조 / 제15조: 다중 위임 (DECREE + RULE) 양방향 정확히 매칭 ✓

### Step 3: 외부 법령 인용 관계 (cross-reference)

**테이블**: `law_article_citation`
```sql
CREATE TABLE law_article_citation (
  citing_article_id, citing_law_id, citing_article_no, citing_article_sub_no,  -- 인용하는 article
  cited_law_name,         -- 추출된 외부 법령명 (「~법」)
  cited_law_id,           -- TAI 매핑되면
  cited_article_no, cited_paragraph_no, cited_item_no,
  citation_pattern,       -- 추출 패턴 (예: "「근로기준법」 제2조제1항")
  citation_in_law_master  -- TAI 매핑 가능 여부
);
```

**룰 V1**:
- 정규식: `「([^」]+(?:법|규칙|영|규정))」\s*제(\d+)조(?:의\s*\d+)?(?:제(\d+)항)?(?:제(\d+)호)?`
- `REGEXP_MATCHES(text, ..., 'g')` — 모든 인용 추출 (한 article에 다중 인용)

**결과**:
- **7,179 row 추출** (TAI 366 법령 본문)
- 633 unique 인용 법령명
- TAI 매핑: 2,752 / 7,179 (**38.3%**)

**TAI 추가 수집 우선순위 (인용 빈도 top, TAI 미수집)**:

| 순위 | 법령명 | 인용수 | 비고 |
|---|---|---|---|
| 1 | **전자정부법** | 413 | 가장 많이 인용 |
| 6 | 형법 | 125 | 벌칙 관련 인용 |
| 8 | 고등교육법 | 106 | |
| 12 | 민법 | 92 | 계약/책임 관련 |
| 13 | 자동차관리법 | 91 | |
| 14 | 도시 및 주거환경정비법 | 76 | |

**ORPHAN 6건 + 인용 top 6건 = TAI 추가 수집 12건** (별도 작업 단위).

---

## Track B 단독 진행 종합 (Day 3 + Step 2 + Step 2-E + Step 3)

### 산출물 통합

| 테이블 | row | 의미 | 매핑률 |
|---|---|---|---|
| `law_family_mapping` | 366 | 가족 관계 (PRIMARY ↔ 시행령 ↔ 시행규칙) | 100% (97.8% verified) |
| `law_article_delegation` | 7,730 | 위임 source 추출 (본법 → 자식 type) | 97.4% target 매핑 |
| `law_article_inheritance` | 8,641 | 위임 target 추출 (자식 → 부모 article) | 99.7% parent 매핑 |
| `law_article_citation` | 7,179 | 외부 법령 인용 (cross-reference) | 38.3% TAI 매핑 |
| `legalize_kr_mapping_raw` | 5,667 | legalize-kr ground truth | (활용용) |
| `v_law_family` | view | 법령 가족 통합 조회 | - |
| `v_law_family_tree` | view | 본법 기준 가족 트리 | - |

### 검증 엔진 V1 — 4 룰

| 룰 | 입력 | 출력 |
|---|---|---|
| **V1-A: 자기 정의 패턴** | 시행령/규칙 본문 article 1, 2 | 부모 본법명 추출 → law_family_mapping verified |
| **V1-B: legalize-kr 디렉토리** | 5,667 row | TAI 가족 매핑 ground truth |
| **V1-C: source × inheritance cross-validate** | delegation × inheritance | 양방향 일치 86.5% |
| **V1-D: cited_law_name TAI 매칭** | citation 추출 | TAI 추가 수집 우선순위 도출 |

### 산안법 가족 완전 매핑 ✓

```
[가족 매핑]
산업안전보건법 (276853) — PRIMARY
├ 산업안전보건법 시행령 (284771)
├ 산업안전보건법 시행규칙 (271485)
└ 산업안전보건기준에 관한 규칙 (273603) ★ validator_v1_self_def

[조문 단위 위임 관계]
본법 제9조 → 시행령 (대통령령) + 시행규칙 (고용노동부령) ✓ 다중 위임
본법 제15조 → 시행령 + 시행규칙 ✓
본법 제4조 → 시행령 제3, 4, 5, 6, 7조 (5개 자식, inheritance)
본법 제8조의2 → 시행령 제8조의2 (정밀 매핑)

[외부 인용]
산안법 → 근로기준법, 화학물질관리법, 전기사업법, 형법 등 인용
```

---

## 사용자 원칙 정합 확인

| 원칙 | Day 3 | Step 2 | Step 3 |
|---|---|---|---|
| LLM 사용 X | ✓ | ✓ | ✓ |
| 법령 보전 (직접 인용) | ✓ | ✓ | ✓ |
| 놓치는 것 = 리스크 | ✓ 366/366 | ✓ 다중 위임 보강 | ✓ 모든 인용 추출 |
| 100% 매핑 | ✓ | ✓ 97.4% (행정규칙 의존 198건) | 38.3% (TAI 미수집 한계) |
| 오염 = 폐기 | ✓ Day 1+2 폐기 | ✓ 1차 INSERT 폐기 | - |
| **검증도 엔진** | ✓ legalize-kr | ✓ cross-validate 86.5% | ✓ 인용 빈도 분석 |
| **추정 매핑 금지** | ✓ ground truth | ✓ 정규식만 | ✓ 정규식만 |

**사용자 검증 작업: 0건** (모두 자동) ✓

---

## Tomorrow / 다음 단계

### (α) Week 2 행정규칙 매핑 — admrule-kr
- 사용자 git clone 대기
- 386건 (NOTICE 340 + STANDARD 42 + OTHER 4)
- 매핑 완료 시 Step 2-A의 STANDARD 155 + NOTICE 11건 자동 해소

### (β) ORPHAN 6건 + 인용 top 6건 = TAI 추가 수집 12건
- 통계법, 도서관법, 정부조직법, 방송통신발전 기본법, 비상대비, 도로교통법 (ORPHAN)
- 전자정부법, 형법, 민법, 자동차관리법, 고등교육법, 도시·주거환경정비법 (인용 top)
- 법제처 API 호출 (별도 작업, Cursor 또는 직접)
- 추가 수집 후 자동으로 inheritance 매핑 + ORPHAN 해소

### (γ) Step 2-F 룰 V1 보강
- inheritance 첫 매칭 한계 (282건 위임표현만 케이스)
- 정규식 보강 — "법 제N조에 따라" / "법 제N조의 ..." 직접 위임 패턴 우선 매칭
- 일반 인용 ("법 제N조에 따른 X") 후순위
- 룰 V2 도입 가능

### (δ) Master Handoff v1.2 update
- Step 2 + Step 3 결과 반영
- 검증 엔진 V1 4룰 명세
- 다른 트랙 (A/E)에 산출물 활용 가이드 공유

### Track B 한계 — 다음은 Track A/C/D/E 영역
- Stage 1 의미절 분리 (Track A 인프라 + Track C 사전 의존)
- 별표/서식 (Track D)
- 마스터 객체 합성 (Track E)

---

## 마일스톤

| 마일스톤 | 상태 |
|---|---|
| Step 1: 가족 매핑 366건 | ✅ Day 3 |
| Step 2-A: 위임 source 추출 | ✅ 7,730건 |
| Step 2-B: target_law_id 매핑 | ✅ 97.4% |
| Step 2-D: inheritance 추출 | ✅ 8,641건 99.7% |
| **Step 2-E: cross-validate 검증 엔진** | **✅ 86.5%** |
| **Step 3: 외부 인용 (cross-reference)** | **✅ 7,179건** |
| 행정규칙 매핑 (Week 2) | ⏳ admrule-kr 사용자 작업 대기 |
| TAI 추가 수집 12건 | ⏳ 별도 작업 |
| Master Handoff v1.2 | ⏳ 다음 |

**Track B 단독 진행 가능 영역의 90% 완료**.

---

**END OF Step 2-E + Step 3** — Track B 본질 작업 (가족 + 위임 + 인용) 완성
