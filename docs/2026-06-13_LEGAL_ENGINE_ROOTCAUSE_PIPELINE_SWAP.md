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
| 의미절(옛, 검증완료) | semantic_clause / semantic_clause_iter1 | ❌ **0으로 비워짐** |
| 룰(옛 설계) | master_rule_v2 / master_rule_scope / master_rule_v2_relation | ❌ **0** |
| 분해 중간(새, 폭주산물) | constraint_node(284,579) / constraint_edge(53,528) | ⚠️ 거대하나 미완 연결 |
| 〃 | evidence_normalized(283,175)/evidence_candidate(266,274)/evidence_token(230,383) | ⚠️ |
| 〃 | family_candidate(263,326) / residuals(111,142, 분해실패 잔여) | ⚠️ |
| 룰후보(새) | rule_candidate(34,456, 전부 status=CANDIDATE) | ⚠️ |
| 엔진입력(새, 실사용) | executable_draft(10,725) / draft_slot(50,133) | ⚠️ **rule_candidate의 31%만** |
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

---

## 6. 방향 (제안 — 대표 확정 대기)

**의미절 복원 + 15차 객체화 런타임으로 직접 대조·추출. 중간 재조립(constraint/evidence/draft)은 걷어낸다.**

근거:
- 원재료(law_article_part)·분해기(decompose_v1.py) 생존 → 의미절 복원에 새로 만들 것 없음.
- 15차에 입력→대조→꺼내기 런타임이 객체화 완료 → 의미절만 있으면 엔진이 바로 동작.
- 대표 정책 원점("의미절이 해결점")과 일치. "다시 모으는 건 바보짓"이라는 판단과 일치.

확정 전 유의:
- 이는 엔진 근간 결정이므로 대표 승인 후에만 실행.
- 복원은 "분해기 재실행"이지 "분해 규칙 재발명"이 아니다(재발명=과거 폭주 원인).
  decompose_v1.py가 진실의 기준. 새 규칙을 상상하지 말 것.
- 검증은 카운트 금지, 결과 글읽기로만(예: 산안법 17조①항이 의미절에 선임 의무로 들어왔는지 원문 대조).

---

## 7. 다음 세션 시작점

이 문서 → 그다음 `docs/law-engine/LEGAL_RULE_PIPELINE__taiadmin.md`(옛 설계 전문) 순으로 읽는다.
방향(6장) 승인되면: ① decompose_v1.py 생존·실행환경 확인 → ② 파일럿 1개 법령(산안법) 의미절 복원
→ ③ 글읽기 검증(17·18조 선임 ①항 포함 확인) → ④ 통과 시 전체 → ⑤ 런타임 연결 확인(engine-test).
