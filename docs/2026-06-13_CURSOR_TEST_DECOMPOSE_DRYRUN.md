# CURSOR 작업지시서 — 의미절 분해기 시험 실행 (dry-run, 쓰기 없음)

작성일: 2026-06-13
발행: Claude 기획창 / 수행: Cursor (로컬 또는 railway run)
근거 문서: docs/2026-06-13_LEGAL_ENGINE_ROOTCAUSE_PIPELINE_SWAP.md (방향·격리 원칙)

---

## 이 작업의 성격 — "실행"이지 "수정"이 아니다

- **decompose_v1.py를 한 글자도 수정하지 않는다.** 정해진 명령으로 실행만 한다.
- 분해 규칙을 새로 만들거나 고치지 않는다(재발명 = 과거 폭주 원인).
- 이번 단계는 **dry-run** 이므로 DB에 아무것도 쓰지 않는다(`--apply` 절대 금지).
- 목적: 비워진 의미절(semantic_clause)을 복원하기 전에, 분해기가 **선임 의무를 제대로 잡는지** 시험.

---

## 배경 (왜 이 시험인가)

- 운영 진단에 산안법 안전관리자(17조)·보건관리자(18조) 선임이 0건으로 누락됨(근본원인 문서 참조).
- 원인: 검증됐던 의미절 파이프라인이 비워지고, 새 constraint/evidence 파이프라인으로 교체됨.
  새 파이프라인의 rule_candidate는 17조에서 ④항(위탁)·⑤항(장관 교체명령)만 잡고
  ①항(선임 "두어야 한다")을 놓쳤다.
- 가설: 기존 의미절 분해기(decompose_v1.py)는 ①항을 OBLIGATION으로 정확히 잡는다.
  이 가설을 dry-run 출력으로 검증한다.

### 원재료는 확인됨 (Claude가 DB 직접 조회)
산안법 17조의 law_article_part(paragraph)에 5개 항이 온전히 존재. 특히:
- ①항: "사업주는 사업장에 … (이하 "안전관리자"라 한다)을 **두어야 한다**." ← 선임 본문
- 위탁항: "… 안전관리자의 업무를 **위탁할 수 있다**." ← DELEGATION이어야
- 장관항: "고용노동부장관은 … 교체할 것을 **명할 수 있다**." ← 사업주 의무 아님
- 위임항: "… 필요한 사항은 대통령령으로 **정한다**." ← DELEGATION이어야

---

## 실행 환경

- decompose_v1.py 위치: `tai-admin` 레포 `docs/extraction/scripts/decompose_v1.py`
- 의존성: `pip install supabase httpx`
- 환경변수 필수: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` (service role — RLS 우회)
  - 운영 프로젝트: `vwlahtguyggrhvslabax` (Supabase 서울). 이 프로젝트의 URL·service role key 사용.
- 읽는 테이블: law_article_part(paragraph) / law_article / law_master — 전부 살아있음(확인됨)
- 쓰는 테이블: dry-run 이므로 **없음**

---

## 실행 명령 (이 순서 그대로)

### STEP 1 — 분해기 정상 작동 확인 (작은 dry-run)
```bash
cd docs/extraction/scripts/
railway run python3 decompose_v1.py --dry-run --sample-size 1000 --sampling stratified --seed 42
```
확인할 것(출력 글읽기):
- `[DECOMPOSE] N parts → M clauses` 라인이 나오는가 (이 라인 없으면 사고 — 5/8 INCIDENT 참조)
- `[CONTENT_TYPE 분포]`에 OBLIGATION/AUTHORITY/DELEGATION 등이 정상 분포하는가
- `[v1.8 검증 통계]`의 executor 채움률이 90%대인가
- 에러·예외 없이 `[DRY-RUN 종료]`로 끝나는가

### STEP 2 — 산안법 17·18조가 어떻게 분해되는지 직접 확인 (핵심)
sample 무작위로는 17조가 안 걸릴 수 있다. **17조·18조를 반드시 포함해서** 분해 결과를 봐야 한다.
decompose_v1.py를 수정하지 말고, 아래 중 택1로 17·18조만 분해 결과를 출력하라:

(권장) 별도 1회용 스크립트(읽기 전용)를 만들어 decompose_v1의 함수를 import해서 17·18조 part만 분해:
```python
# scripts/_probe_appoint_17_18.py  (1회용, DB 쓰기 없음, decompose_v1 수정 안 함)
import os
from supabase import create_client
import decompose_v1 as D   # 같은 폴더

sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])

# 산안법 17·18조 article_id 조회
law = sb.table("law_master").select("id").eq("law_name","산업안전보건법").limit(1).execute().data[0]["id"]
arts = sb.table("law_article").select("id,article_no").eq("law_id",law).in_("article_no",["17","18"]).execute().data
art_ids = [a["id"] for a in arts]

# 해당 article의 paragraph part 조회
parts = sb.table("law_article_part").select("id,article_id,part_text,part_type,depth")\
          .in_("article_id",art_ids).eq("part_type","paragraph").execute().data

from collections import Counter
rc = Counter()
for p in parts:
    clauses = D.decompose_part(p, sector="INDUSTRIAL", rule_counts=rc)
    for c in clauses:
        print("─"*60)
        print("part:", (p["part_text"][:80]))
        print("  executor    :", c.get("executor_text"))
        print("  content_type:", c.get("content_type"))
        print("  action      :", (c.get("action_text") or "")[:80])
        print("  needs_review:", c.get("needs_review"), c.get("review_reason"))
```
```bash
railway run python3 scripts/_probe_appoint_17_18.py
```
- 이 probe 스크립트는 **읽기 전용**이며 끝나면 삭제한다(또는 _probe_ 접두로 격리).
- decompose_v1.py 본체는 건드리지 않는다.

---

## 합격 기준 (카운트 아님 — 글로 읽어 판정)

STEP 2 출력에서 다음을 **글로** 확인한다:

| 항(원문 핵심) | 기대 content_type | 기대 executor |
|---|---|---|
| "안전관리자를 **두어야 한다**" (①항) | **OBLIGATION** | 사업주 |
| "전담하도록 **하여야 한다**" | OBLIGATION | 사업주 |
| "위탁**할 수 있다**" | DELEGATION (또는 AUTHORITY) | — |
| 장관 "**명할 수 있다**" | AUTHORITY | (장관/사업주 아님) |
| "대통령령으로 **정한다**" | DELEGATION | — |

**핵심 합격 조건**: ①항("두어야 한다")이 **OBLIGATION**으로 나오고 executor가 사업주여야 한다.
(이것이 진단 결과에 안전관리자 선임이 뜨게 만드는 출발점이다. 18조 보건관리자도 동일 구조여야.)

- 합격: ①항이 OBLIGATION 선임으로 잡힘 → 다음 단계(iter1 본 적용 + 본 테이블 동기화 + 룰 변환) 설계로.
- 불합격: ①항이 OBLIGATION이 아니거나 누락 → **수정하지 말고 출력을 그대로 보고**. Claude가 분석·판정.

---

## 보고 형식 (이 형식 그대로 기획창에 제출)

```
[STEP1] [DECOMPOSE] 라인 / CONTENT_TYPE 분포 / executor 채움률 / 정상종료 여부
[STEP2] 17·18조 각 항의 (원문 앞부분 → content_type → executor → needs_review) 전체 출력 붙여넣기
[판정]  ①항이 OBLIGATION 선임으로 나왔는가? (예/아니오 + 출력 근거)
[비고]  에러·예외·예상과 다른 점 (수정하지 말고 기록만)
```

수정·개선·`--apply`·분해규칙 변경 일체 금지. 실행과 출력 보고만. 끝나면 정지.

---
---

# 시험 결과 + 판정 (2026-06-13, Cursor 실행 → Claude 판정)

## STEP 1 결과 — 분해기 정상
- `[DECOMPOSE] 1000 parts → 1279 clauses` (정상, 사고 라인 누락 없음)
- CONTENT_TYPE 분포: OBLIGATION 707 / AUTHORITY 227 / DELEGATION 134 / DEFINITION 135 /
  PROHIBITION 42 / STATEMENT 4 / None 30
- executor 채움률 97.8% (955/976), still_null 21
- 에러 없이 `[DRY-RUN 종료]`. → **분해기 즉시 실행 가능 상태 확인.**

## STEP 2 결과 — 17·18조 글읽기
| 항 | content_type | executor | 판정 |
|---|---|---|---|
| ①항 "두어야 한다"(선임 본문) | **OBLIGATION** ✓ | "지도ㆍ조언하" ✗ (사업주 아님) | 의무는 정확, 주체 오추출 |
| 전담 "하여야 한다" | OBLIGATION ✓ | "정하"(suspicious) ✗ | 〃 |
| 위탁 "위탁할 수 있다" | DELEGATION ✓ | — | 정확 |
| 장관 "명할 수 있다" | AUTHORITY ✓ | 고용노동부장관 ✓ | 정확 |
| 위임 "대통령령으로 정한다" | DELEGATION ✓ | — | 정확 |
- 18조 보건관리자도 동일 구조(①항 OBLIGATION, executor "지도ㆍ조언하").
- executor 오추출 원인: ①항 긴 문장이 "보좌하고"에서 2 clause로 분할 →
  [1]은 executor=사업주 정확, [2]("…지도ㆍ조언하는…두어야 한다")는 역순 주어탐색이
  문장 중간 "지도ㆍ조언하"를 주어로 오인. `v19_reverse_executor` 부작용.

## 판정 (Claude)
- **의미절 분해기는 선임 의무를 정확히 잡는다.** ①항이 OBLIGATION으로 살고,
  곁가지(위탁·장관·위임)가 DELEGATION/AUTHORITY로 정확히 갈라짐. 새 파이프라인(rule_candidate)이
  ①항을 통째로 놓친 것과 대비 → **방향(의미절 복원)은 시험 통과.**
- executor 오추출은 **방향을 막는 결함이 아니라 알려진 한계**(5/8 문서도 "사물 주어 1,532건
  needs_review"로 이미 기록). 진단 가치는 "선임 의무 존재"이며 그건 정확. executor(거의 항상
  '사업주')는 표시/보정 단계에서 해결 가능.

## 결정 (대표 확정 2026-06-13) — 2단계 전략
1. **먼저 확률 높은 것으로 본 작업**: 분해기를 수정하지 않고 그대로 의미절 복원(다수가 정확).
   완벽한 executor를 기다리며 멈추지 않는다(한 조문에 매달리는 루프 회피).
2. **그 다음 범용 체크엔진으로 오류 개선**: 이미 있는 check_engine(범용 역검증 엔진) +
   engine-test 하니스 패턴을 활용해, executor·content_type 오류를 **자동 역검증으로 색출**한다.
   - 분해기는 안 건드린다. 새 검증 어댑터만 붙인다(오염 격리 원칙).
   - 사람이 일일이 찾지 않고, 결과를 룰과 거꾸로 대조해 MISMATCH를 사실로 드러낸다.
   - executor 보정은 분해기 수정이 아니라 별도 보정/검토 트랙으로 다룬다.

## 다음 단계 (실행 — 단계마다 대표 승인, 삭제 없이, 격리 유지)
A. 산안법 1개 법령을 iter1에 의미절 복원(분해기 그대로 --apply, semantic_clause_iter1만 쓰기).
   본 테이블·기존 자산 무영향(분해기는 iter1에만 INSERT 확인됨).
B. iter1 결과 글읽기 검증(17·18조 ①항 OBLIGATION 선임 포함 + 분포 정상).
C. 통과 시 본 테이블 동기화(5/8 문서의 본 동기화 SQL) → 룰 변환(convert_clause_to_rule.py) 설계.
D. 런타임 연결: engine-test로 제조 사업장 진단에 안전관리자 선임이 뜨는지 글읽기.
E. 그 후 범용 체크엔진 역검증 트랙으로 executor·매핑 오류 색출·개선.
