# 법령엔진 근본원인 규명 — 의미절 파이프라인 교체 사고 (2026-06-13)

> 이 문서는 "현상"이 아니라 **확인된 원인과 자산 상태**의 기록이다.
> 다음 세션(GPT/Claude/Cursor 누구든)은 이 문서를 먼저 읽고 시작한다.
> 모든 수치는 운영 DB(`vwlahtguyggrhvslabax`, Supabase 서울)를 직접 SELECT해 확인한 사실이다(추측 아님).

---

## 0. 한 줄 결론

**검증까지 끝났던 "의미절(semantic_clause)" 파이프라인이 비워지고, 그보다 더 잘게 부수는
"constraint/evidence/draft" 파이프라인으로 교체됐다가 미완성(31%)으로 멈췄다.
이것이 제조업 진단에 안전관리자·보건관리자 선임이 안 나오는 근본 원인이다.
의미절이 옳았고, 다시 모으는 재조립 구조가 오판이었다. 원재료와 분해기는 살아있어 의미절은 복원 가능하다.**
**(2026-06-13 진행: 의미절 58,495건 복원·본테이블 동기화·원본↔파생 전수검증 완료. 9장 참조.)**

---

## 1. 어떻게 여기까지 왔나 (관찰 경로)

1. 현상 확정(결과 글읽기): 대한정밀화학(제조 80명·8000㎡) 진단 결과 118건에
   산안법 15~19조 선임 의무가 **0건**. 선임은 소방안전관리자만. (토큰 b17ba6ef)
2. Cursor 조사: 엔진이 읽는 `executable_draft`에 산안법 15~19조가 0건 → RULE GAP으로 보고.
3. 교차검증(직접 DB): 산안법 본법 203조 중 원문(article_text)은 203조 전부 존재하나
   executable_draft는 40조만. 전체 법령으로는 35,412조 중 draft 보유 6,313조 = **17.8%**.
4. 크기로 전체 훑기(대표 지시 — 연결점 추적이 아니라 큰 테이블 직접 확인):
   분해 중간산출물은 거대(constraint_node 284,579 / evidence_* 28만대 / rule_candidate 34,456)한데
   엔진이 읽는 executable_draft는 10,725건뿐. rule_candidate→executable_draft 변환이 **31%만** 진행.
5. 재료 품질 글읽기: 산안법 17·18조 rule_candidate의 slot을 읽으니 선임 의무 ①항이 아니라
   ④항(위탁 재량)·⑤항(장관 교체명령)만 잡힘. 대부분 slot이 UNRESOLVED.
   → 변환을 100% 돌려도 선임은 안 나옴. 재료 자체가 ①항을 안 담음.
6. 과거 문서 대조(LEGAL_RULE_PIPELINE 5/8): 원설계는
   `law_article_part → semantic_clause(의미절) → master_rule_v2`. constraint/evidence/draft는
   문서 어디에도 없음 → **5/8 이후 파이프라인이 통째로 교체됨**을 발견.
7. 옛 파이프라인 생존 확인(직접 count): semantic_clause 0 / semantic_clause_iter1 0 /
   master_rule_v2 0 / master_rule_scope 0 / master_rule_v2_relation 0.
   **의미절 데이터는 본 테이블·백업 모두 비워졌다.**
8. 분해기 생존 확인(tai-admin `docs/extraction/scripts/`): decompose_v1.py(66KB) 등 전 단계 보존.
   원재료 law_article_part 143,544건도 살아있음 → **의미절 복원 가능**.

---

## 2. 현재 DB 자산 상태표 (사실)

| 층 | 테이블 | 상태 |
|---|---|---|
| 원문 | law_master / law_article(33,862) / law_article_part(143,544) | ✅ 온전 (아무도 안 건드림) |
| 의미절(복원완료 2026-06-13) | semantic_clause(58,495) / semantic_clause_iter1(58,495) | ✅ **복원됨(9장)** |
| 룰(옛 설계) | master_rule_v2 / master_rule_scope / master_rule_v2_relation | ❌ **0 (D단계에서 변환 결정)** |
| 분해 중간(새, 폭주산물) | constraint_node(284,579) / constraint_edge(53,528) | ⚠️ 격리 대상(삭제금지·보존) |
| 〃 | evidence_normalized(283,175)/evidence_candidate(266,274)/evidence_token(230,383) | ⚠️ |
| 〃 | family_candidate(263,326) / residuals(111,142, 분해실패 잔여) | ⚠️ |
| 룰후보(새) | rule_candidate(34,456, 전부 status=CANDIDATE) | ⚠️ 격리 대상 |
| 엔진입력(새, 실사용) | executable_draft(10,725) / draft_slot(50,133) | ⚠️ **현 엔진이 읽음. D단계에서 의미절로 전환** |
| 런타임 객체화 | 15차 레이어·계약(InputContract→…→StoredDiagnosisResult) | ✅ 완성 |

분해기/스크립트(tai-admin `docs/extraction/scripts/`): decompose_v1.py, parse_article_parts.py,
convert_clause_to_rule.py, extract_scope_from_clauses.py, 패턴사전 SET-003~005 — 전부 ✅ 보존.

---

## 3. 엔진이 실제로 읽는 경로 (코드 확인)

`run_step1_via_compiler`(diagnosis_integrated_svc) → `run_anonymous_diagnosis`
→ `evaluate_single_factory`(anonymous_factory_service):
  - `executable_draft` + `draft_slot`(IF_NUMERIC/IF_SCOPE, value=null이면 skip) 읽음
  - sector 필터: executable_draft→law_article→law_master←law_sector_mapping
  - 평가결과 facility_applicability INSERT → fetch_compiler_candidates → rules_table
※ 운영 엔진은 leg 별도 DB(wrfcedzgdrfupenzqhur)를 **참조하지 않음**. tai-api Supabase 한 곳만.
※ 즉 내가 본 DB가 엔진이 읽는 그 DB가 맞다(다른 DB 오인 아님 — 코드로 확인).

### 3.1 executable_draft를 읽는 코드 전수 (격리 대상 식별)
GitHub 코드검색 결과, executable_draft를 읽는 .py는 **전부 진단 엔진 한 덩어리 안**:
- services/anonymous_factory_service.py (진단 본체)
- services/facility_applicability_eval.py (평가 로직)
- services/runtime_evaluator_svc.py (런타임 평가)
- services/legal_runtime_fetch.py (런타임 fetch)
- scripts/run_executable_draft.py, scripts/run_facility_applicability.py (배치 생성)
→ 결제·문서생성·교육·알림·관리자 등 **다른 서비스가 직접 읽는 곳 없음.**
→ 격리해도 진단 엔진 밖은 영향 없음(다른 곳에서 빌려쓰지 않음).

---

## 4. 두 파이프라인 대조

### 옛 (5/8 완성·검증, 현재 비워짐) — 대표가 "해결점"이라 본 것
```
law_article_part → [decompose_v1.py] → semantic_clause(58,495, executor 99%, LLM 0%)
                 → [convert_clause_to_rule.py] → master_rule_v2(+sectors[])
소비자 입력 sector/조건 ──대조──> 해당 룰 SELECT
```
- 의미절 1건 = 룰 1건. 법을 "목적에 맞게 정리"해두고, 입력값과 비교해 꺼내는 구조.
- 이 구조에선 무거운 재조립 엔진이 필요 없다(대표 통찰).

### 새 (폭주 시점 교체, 현재 운영·미완성)
```
law_article_part → constraint_node(28만)/evidence(28만) → family_candidate(26만)
                 → rule_candidate(34,456) → executable_draft(10,725, 31%) → draft_slot
```
- 더 잘게 찢어 그래프로 엮고 다시 룰로 모음("다 찢고 다시 뭉친다" = 대표가 지적한 오판).
- rule_candidate 생성 단계에서 이미 핵심 의무문(예: 17조①항 선임)을 놓침 + 변환 31%에서 멈춤.

---

## 5. 근본원인 (분류)

- ENGINE BUG 아님: 엔진은 있는 draft를 정상 평가.
- INPUT GAP 아님: 입력(80명·C20·MANUFACTURING) 정상.
- EXPECTED 아님: 80명 화학제조에 안전·보건관리자 선임은 법적으로 당연.
- **근본원인 = 파이프라인 교체 사고.** 검증된 의미절 산출물이 비워지고, 미완성·과잉복잡
  파이프라인으로 대체됨. 선임 누락은 그 산물의 한 증상.
- **사고가 가능했던 이유 = 기존 자산(semantic_clause)을 격리하지 않았기 때문(대표 통찰).**
  새 작업이 같은 공간을 덮어쓸 수 있었다. → 7장 격리 원칙으로 재발 방지.

---

## 6. 방향 (대표 확정 2026-06-13)

**의미절 복원 + 15차 객체화 런타임으로 직접 대조·추출. 중간 재조립(constraint/evidence/draft)은 격리한다.**
(가)데이터 격리 + (나)코드 격리 둘 다 — **삭제 없이 참조만 끊고 보존**(7장 참조).

근거:
- 원재료(law_article_part)·분해기(decompose_v1.py) 생존 → 의미절 복원에 새로 만들 것 없음.
- 15차에 입력→대조→꺼내기 런타임이 객체화 완료 → 의미절만 있으면 엔진이 바로 동작.
- 대표 정책 원점("의미절이 해결점")과 일치. "다시 모으는 건 바보짓"이라는 판단과 일치.

확정 전 유의:
- 이는 엔진 근간 결정이므로 대표 승인 후에만 실행. (방향=확정, 실행 단계별 승인은 별도)
- 복원은 "분해기 재실행"이지 "분해 규칙 재발명"이 아니다(재발명=과거 폭주 원인).
  decompose_v1.py가 진실의 기준. 새 규칙을 상상하지 말 것.
- 검증은 카운트 금지, 결과 글읽기로만(예: 산안법 17조①항이 의미절에 선임 의무로 들어왔는지 원문 대조).

---

## 7. 격리 원칙 (재발 방지 — 대표 확정 2026-06-13)

폭주가 가능했던 근본 이유 = **기존 자산을 격리하지 않아 새 작업이 덮어쓸 수 있었음.**
따라서 파이프라인 전환 시 격리는 사후 정리가 아니라 **재발 방지 구조**다. 절대 규칙:

1. **삭제 금지.** 데이터도 코드도 지우지 않는다. "안 쓰니까 지우자"는 금지. 참조만 끊고 보존.
2. **(가) 데이터 격리** — constraint/evidence/rule_candidate/executable_draft/draft_slot 등
   중간 재조립 테이블은 그대로 둔다. 엔진이 안 읽도록 코드 경로만 의미절로 바꾼다.
   (테이블은 박물관처럼 보존. 나중에 필요하면 되살림.)
3. **(나) 코드 격리** — executable_draft를 읽던 .py(3.1 목록)는 옛 경로로 표시·보존한다.
   표준 양식(이미 services/legal_runtime_fetch.py 상단에 존재하는 패턴 그대로):
   ```
   # [ISOLATED] [CATALOG ONLY - NOT DIAGNOSIS SOURCE]
   # <테이블/경로> = <용도>. 진단은 <새 경로> 사용.
   # 삭제 금지. <보존 사유> 용도 보존.
   ```
4. **선례:** Phase 2 때 runtime_metadata_resolution → compiler_core 전환은 격리 주석을 달아
   살아남았다(legal_runtime_fetch.py가 그 증거). 의미절→constraint 전환 때는 격리를 안 해서
   semantic_clause가 비워졌다. **격리한 자산은 살고, 안 한 자산은 죽었다** — 이 차이가 교훈.
5. 새 파이프라인(의미절 복원본)도 별도 공간/명확한 경계로 만들어, 다음 전환 때 덮어쓰이지 않게 한다.

---

## 8. 실행 단계 로드맵

① decompose_v1.py 생존·실행환경 확인 ✅(완료)
② 분해기 dry-run 시험 — 산안법 17·18조 ①항 OBLIGATION 선임 확인 ✅(완료, 시험문서)
③ 의미절 전체 복원(--apply, iter1) ✅(완료, 9장 A)
④ 본 테이블 semantic_clause 동기화 ✅(완료, 9장 C)
⑤ 원본↔파생 전수 역검증(누락0·왜곡0·커버리지96.2%) ✅(완료, 9장 B)
⑥ executor 오추출 색출 강화(형태소 분석기 — 색출 전용) ⏳(다음, 10장)
⑦ D단계: 엔진이 executable_draft 대신 의미절을 읽도록 경로 전환(운영 영향 시작점)
⑧ 런타임 연결: engine-test로 제조 사업장에 안전관리자 선임이 뜨는지 글읽기
각 단계 삭제 없이, 기존 자산 격리 유지, 단계마다 대표 승인.

---

## 9. 의미절 복원·검증 결과 (2026-06-13 완료)

### A. 전체 복원 (decompose_v1.py --apply, iter1)
- iter1 58,495건 복원. 5/8 분포와 완전 일치:
  OBLIGATION 29,665 / AUTHORITY 10,470 / DELEGATION 9,055 / DEFINITION 6,471 /
  PROHIBITION 1,742 / NULL 702 / STATEMENT 390. 폐지조문 1,962 제외.
- 분해기 결정론적 재현 확인(같은 입력→같은 5/8 결과). 본 테이블 무영향(iter1만 쓰기).

### C. 본 테이블 동기화 (Claude 직접 INSERT)
- 본 테이블 semantic_clause = 28컬럼, iter1 = 23컬럼(부분집합). 본테이블 추가 5컬럼
  (exception_marker/how_text/inherited_from_clause_id/what_text/where_text)은 5/8후 확장·분해기 무관.
- iter1 23컬럼 명시 INSERT로 동기화: 본 테이블 58,495건, OBLIGATION 29,665,
  산안법 17조 "두어야 한다" OBLIGATION 존재 확인.

### B. 원본↔파생 충실성 전수 역검증 (범용 체크엔진 어댑터, LLM 아님)
- 검증1 누락: eligible part 49,997개 **100% 의미절 보유, 누락 0건**.
- 검증2 왜곡/환각: 58,495건 **전부 MATCH, MISMATCH 0건**(정규식 기반→환각 구조적 불가 입증).
- 검증3 재조합 커버리지: 평균 96.2%, ≥0.9가 87.3%, <0.7은 114건(0.23%, 조항참조·나열·병렬절=정상정제).
- **충실성("원문에서 왔나")은 전수 증명됨.** 5/8은 샘플추정이었으나 지금은 엔진 전수증명.

### 남은 결함 = 정확성(executor)
- 충실성(원문 글자 보존)은 증명됐으나, **정확성(부여된 의미가 맞나)은 별개.**
- executor 오추출: 의무류 41,877 중 동사어간이 주어로 잘못 잡힘.
  "~하$"만 글읽기 집계해도 6,787건(정하1,885/해당하1,601/관할하142…) = 전부 동사 활용형 어간.
  원인: 진짜 주어는 문장 맨 앞(사업주/장관)인데, v19_reverse_executor가 서술어 근처
  동사 어간을 주어로 오인. **단어 패턴의 한계 — 한국어는 문장을 봐야 주어-서술어가 이어짐.**
- A2가 868건만 잡은 것은 색출망(is_fake_executor/is_object_subject)이 동사어간 패턴을
  안 가져서임. **색출이 오류의 일부만 잡음 → "더 발견하는 방법"이 먼저(대표 지적).**

---

## 10. 엔진 히스토리와 도구 사용 원칙 (대표 정리 — 절대)

### 히스토리 (왜 지금 방식인가)
1. **LLM 파싱** → 원문 훼손(환각). 법은 원문이 생명.
2. **LLM + 규칙** → 규칙 비대·예외 폭발·통제 불능(폭주).
3. **LLM 제거, 순수 정규식** → 환각 0이나 "단어들만" 봄(문장 의미 못 읽음).
4. **의미절 도입** → 단어를 의미 단위로 묶어 많은 문제 해결. (현재, 환각0·누락0 증명됨)

### 도구 배치 원칙 (LLM이든 형태소 분석기든 동일)
- **핵심: "무엇이냐"가 아니라 "어디에 쓰느냐"가 본질.**
- 통제 안 되는 행동이 일어날 소지가 있는 곳(생성/파싱/분해) = **외부 판단 도구 배제.**
  여기 LLM이나 형태소 분석기를 넣으면 그 도구의 오류가 생성에 들어가 통제 불능 재발.
- 읽기/분석/색출/검증 = **LLM·형태소 분석기 활용 가능.** 단 체크엔진 코어
  (범용·무판단·무데이터)가 아니라 **어댑터/별도 단계에 격리.** 도구가 틀려도
  색출 후보만 잘못 표시될 뿐 의미절 자체는 안 망가짐.

### 형태소 분석기 결정 (대표 확정 2026-06-13) — (가) 색출 전용
- 의미절 분해는 지금 정규식 분해기 그대로(충실성·환각0 보존).
- 형태소 분석기는 **executor 색출/검증에만** 탑재: 추출된 executor가 명사 주어(NNG/NNP+주격)인지
  동사 어간(VV)인지 품사로 판정 → "정하/해당하" 같은 동사어간 오추출을 정확히 색출.
- 분해기에 탑재 금지(증명 무효·법조문 오태깅 위험·생성 오염). 색출 단계에 격리.
- 보정(정정)은 또 다른 트랙: 분해기 무수정, 의미절 테이블 위에서 별도 격리 단계로,
  결과는 체크엔진으로 재검증. (색출→패턴→규칙보강→재검증 루프. 5/8 작업원칙 3)
