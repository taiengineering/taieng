# PATTERN MINING 2026-05-08 v2 — v1.9 작업지시서 사전 채굴

> v1.8 dry-run 결과 분석 후, v1.9 역순 추출 알고리즘 사전 검증.
>
> 핵심 발견: v1.8 still_null의 78%+가 **추출 본체의 결함** (article ref / 부사구 시작으로 매칭 실패).
> 역순 추출 알고리즘이 모집단의 84.8%를 잠재 해결.

---

## v1.8 dry-run 결과 (1000 sample) 회상

| 항목 | 결과 | 판정 |
|---|---|---|
| executor 채움률 | 77.3% (760/983) | ❌ baseline 76.4%와 거의 동일 |
| 가짜 7 패턴 잔존 | 0 | ✅ |
| recipient 채움률 | 58.2% | ✅ |
| inherit 적용 (paragraph+article) | 40건 / 예상 ~242건 | ❌ 16.5% |
| still_null | 223건 (22.7%) | ❌ |

still_null 223건 중 sample 5건이 모두 **텍스트 안에 진짜 주어가 명시**되어 있는데 분해기가 시작 prefix(article ref/부사구)에서 막혀 추출 실패.

→ v1.8의 FAKE 필터 / inherit으로는 못 잡음. **`extract_executor_text` 본체 재설계 필요**.

---

## 채굴 1. NULL executor 의미절의 주어 표지 보유율

```sql
SELECT 
  COUNT(*) AS total_null,
  COUNT(*) FILTER (WHERE source_text ~ '[가-힣ㆍ]{2,30}\s*(은|는|이|가)\s') AS has_subject_marker
FROM semantic_clause
WHERE executor_text IS NULL
  AND content_type IN ('OBLIGATION','PROHIBITION','AUTHORITY')
  AND sectors IS NOT NULL;
```

| 표지 | 건수 | 비율 |
|---|---|---|
| **주어 표지 보유 (역순 추출 대상)** | **9,264** | **84.8%** |
| 은/는 | 9,011 | 82.5% |
| 이/가 | 2,241 | 20.5% |
| 둘 다 | 2,013 | 18.4% |
| 표지 없음 | 1,656 | 15.2% |

→ NULL executor 10,920건 중 **9,264건이 역순 알고리즘 적용 가능**.

---

## 채굴 2. 텍스트 시작 패턴 (v1.8이 못 잡은 이유)

| 시작 패턴 | 건수 | 비율 |
|---|---|---|
| `법 제X조` | 769 | 7.0% |
| `제X조` | 735 | 6.7% |
| `제X항/호` | 5,509 | 50.4% |
| 대명사 (`이 법`, `이 규정`, `위`, `해당`, `당해`) | 1,404 | 12.9% |
| **PREFIX_SKIP 대상 합계** | **7,288** | **66.7%** |

→ NULL executor의 **66.7%가 article reference / 대명사로 시작** → v1.8 시작 매칭 실패.

---

## 채굴 3. 다중 주어 (조건절 + 의무 주어)

NULL executor + 표지 보유 9,264건 중:

| 항목 | 건수 | 비율 |
|---|---|---|
| `경우(에는\|에)` 보유 | 1,101 | 11.9% |
| `때(에는\|에)` 보유 | 361 | 3.9% |
| **조건절 보유** | **1,433** | **15.5%** |
| **다중 주어 추정** (조건절 + 표지 2+) | **1,389** | **15.0%** |

→ 약 **15%가 sample 3 같은 다중 주어 케이스** — `select_best_subject` 우선순위 알고리즘 필요. 나머지 85%는 단일 주어라 단순.

---

## 채굴 4. AUTHORITY 의 DELEGATION 누수

v1.8에서 OBLIGATION → DELEGATION은 잡았지만 AUTHORITY → DELEGATION 누수 발견:

| 패턴 | AUTHORITY 빈도 |
|---|---|
| `위임할 수 있다` | 112 |
| `위탁할 수 있다` | 314 |
| `~의 권한 ~ 위임` | 106 |
| **AUTHORITY 누수 합계** | **459 (4.2%)** |

→ v1.9 DELEGATION_PATTERNS 보강으로 잡음.

---

## 채굴 5. 사물 주어 (행위자 아님)

NULL executor + "은/는" 표지 9,011건 중 사물성 접미사로 끝나는 후보:

| 카테고리 | 접미사 | 건수 |
|---|---|---|
| 금액성 | 부담금, 수수료, 수당, 여비, 보험료, 비용, 기준, 범위, 예산, 기간, 금액, 요금, 단가, 상금 | 314 |
| 행정성 | 허가, 신고, 등록, 승인, 인가, 면허, 자격, 증명서 | 24 |
| 시설성 | 시설, 설비, 장비, 건축물, 공작물, 차량, 장치, 기기 | 34 |
| 기능성 | 권한, 업무, 직무, 책임, 의무 | 107 |
| **사물 주어 합계** | — | **445 (4.9%)** |

→ v1.9에서 **사물 주어는 executor NULL + needs_review** 마크.

---

## v1.9 효과 추정 (모집단)

| 단계 | 분자 (채움) | 분모 | 채움률 |
|---|---|---|---|
| baseline v1.7.1 | 35,253 | 46,173 | 76.4% |
| v1.8 (FAKE 정정 + DELEGATION 1차) | 31,138 | 42,199 | 73.8% |
| **+ v1.9 역순 추출 (NULL 9,264 중 ~85% = 7,874건)** | **39,012** | 41,740 | **93.5%** |
| 사물 주어 needs_review (-445) | 38,567 채움 + 445 review | 41,740 | 92.4% |
| AUTHORITY DELEGATION 재분류 (-459) | 동일 | 41,281 | **93.4%** |

→ **v1.9 후 약 93% 채움률** (목표 90% 초과). 사물 주어는 needs_review로 정확도 우선.

---

## v1.9 알고리즘 핵심 (개념)

```
[입력] source_text + content_type

1. content_type이 DELEGATION/DEFINITION/STATEMENT → executor NULL (early return)

2. 괄호 제거 (alias / 보충 설명)

3. 모든 위치에서 "(명사구)(은|는|이|가) " 매칭 후보 수집
   - 가짜 필터 적용
   - article ref prefix 제거 (cleanup)

4. select_best_subject:
   - condition(경우에는/때에는) 위치 식별
   - condition 뒤의 후보 우선
   - 모두 condition 안이면 마지막 후보
   - 서술어 근접 (= 가장 뒤쪽) 우선

5. 사물 주어 검사 (접미사 lexicon)
   - 사물 주어면 → executor NULL + needs_review='object_subject'
   - 아니면 → executor 채움
```

---

## 5 sample 시뮬레이션 검증 (v1.8 still_null 1000-sample)

| # | 텍스트 | v1.8 결과 | v1.9 예상 |
|---|---|---|---|
| 1 | "법 제48조의6제8항 단서에 따라 산재보험 노무제공자가 ... 제출해야 한다." | NULL | **"노무제공자"** ✅ |
| 2 | "이 법에 따른 권한은 ... 위임할 수 있다." | NULL | DELEGATION 재분류 → NULL ✅ |
| 3 | "...전문인력 양성기관이 ... 경우에는 보건복지부장관과 식품의약품안전처장은 ... 취소할 수 있다." | NULL | **"보건복지부장관과 식품의약품안전처장"** ✅ |
| 4 | "...업무를 위탁받은 공단(이하 '위탁사업자'라 한다)은 ... 한다." | NULL | **"공단"** ✅ |
| 5 | "...징수한 원인자부담금은 ... 사용할 수 있다." | NULL | NULL + needs_review='object_subject' ⚠️ |

→ 5건 중 4건 자동 해결, 1건 정확히 needs_review.

---

## 다음 액션

→ `CURSOR_TASK_2026-05-08_decompose_v19.md` 작업지시서 작성 (본 채굴 결과 반영).

---

## 관련 문서

- `PATTERN_MINING_2026-05-08.md` — v1.8 사전 채굴
- `CURSOR_TASK_2026-05-08_decompose_v18_v2.md` — v1.8 작업지시서 (적용됨)
- `CURSOR_TASK_2026-05-08_decompose_v19.md` — **v1.9 작업지시서** (다음 작성)
- `HANDOFF_FINAL_2026-05-07.md` — 통합 핸드오프
