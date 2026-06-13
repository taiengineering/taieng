# CURSOR 작업지시서 B — 의미절 전체 원본↔파생 역검증 (범용 체크엔진 활용)

작성일: 2026-06-13
발행: Claude 기획창 / 수행: Cursor (railway run)
근거: docs/2026-06-13_LEGAL_ENGINE_ROOTCAUSE_PIPELINE_SWAP.md,
      docs/2026-06-13_CURSOR_A_RESTORE_AND_VERIFY.md (A단계 완료: iter1·본테이블 58,495 복원)
대표 확정: LLM은 58,495건 전수검증 불가. 범용 체크엔진으로 결과값을 역추적해 증명한다.

---

## 목적 — 원본에서 파생된 의미절이 손상/누락/왜곡 없는지 엔진으로 증명

지금까지 검증한 것: 의미절의 content_type 분류·executor 타당성(A2).
**아직 검증 안 한 것: 원본(law_article_part) → 의미절 파생의 충실성.**
분해기가 긴 문장을 쪼개고 5요소를 추출하는 과정에서 원문을 빠뜨리거나 변형했을 수 있다.
이것을 범용 체크엔진(services/check_engine.py)으로 전수 역검증한다.

---

## 안전 경계 (절대)

- **check_engine.py · decompose_v1.py 를 한 글자도 수정하지 않는다.** 검증 어댑터만 새로 만든다.
- **DB에 아무것도 쓰지 않는다.** 전수 SELECT + 메모리 대조 + 카운트/샘플 보고만.
- executor·의미절 보정 금지(별도 트랙). 분해규칙 변경 금지. 자가패치 금지.
- 검증 대상: 본 테이블 semantic_clause (58,495건, A단계에서 복원됨). iter1과 동일.

---

## 체크엔진 계약 (services/check_engine.py — 읽기만)

```
CheckItem(id, values) 를 expected 와 대조 → CheckResult(verdict)
  MATCH    : expected 가 values 안에 있음 (정합)
  MISMATCH : values 는 있는데 expected 가 그 안에 없음 (모순)
  NO_RULE  : values 가 비어있음 (대조할 근거 없음 → 보류)
tally(results) → verdict별 개수
```
어댑터가 "원본↔파생"을 이 계약으로 변환해 넣고, verdict를 충실성으로 해석한다.
**check_engine.py가 로컬에 없으면**(A2 비고 참조) services/ 에서 찾아 import.
경로 문제 시 동일 계약(MATCH/MISMATCH/NO_RULE 3분류 + tally)을 어댑터 안에 그대로 재현해도 됨
(단 "범용·무판단·무데이터" 원칙 유지 — 도메인 상수 하드코딩 금지).

---

## 검증 1 — 누락 (NO_RULE 색출): 원본 part가 의미절을 가졌는가

원본 paragraph part 중, 의미절이 하나도 파생되지 않은 것을 색출.

- 대상 모집단 = 분해 대상이던 part (eligible: article_type='조문', KEC 제외, 폐지 제외).
  decompose_v1 의 eligible_population / filter_deleted 기준과 동일하게 추린다.
- CheckItem.id = part_id, values = 그 part_id로 생성된 semantic_clause 개수>0 이면 ["has_clause"] 아니면 []
- expected = "has_clause"
- NO_RULE = 그 원본 part에서 의미절이 0개 생성됨 → **누락 후보**

보고: 모집단 part 수 / 의미절 보유 part 수 / NO_RULE(의미절 0개) part 수 + 샘플 10
(샘플은 part_text 앞 80자 — 어떤 원문이 통째로 빠졌는지 글로 볼 수 있게)

## 검증 2 — 왜곡 (MISMATCH 색출): 의미절 텍스트가 원문에 실재하는가

각 의미절의 source_text 가 그 원본 part_text 안에 실제로 존재하는 내용인가
(분해기가 원문에 없는 말을 만들어내지 않았는가 = 환각/왜곡 색출).

- CheckItem.id = clause_id
- values = 원본 part_text 를 정규화(공백·구두점 제거)한 문자열 1개를 담은 목록
- expected = 의미절 source_text 를 같은 방식으로 정규화한 문자열
- 대조 규칙: expected(정규화 의미절)가 values(정규화 원문)의 **부분문자열**이면 MATCH.
  ※ check_engine 은 정확일치(in)만 하므로, 부분문자열 판정은 어댑터에서 수행하여
    "포함되면 values=[expected] 로 세팅"하는 방식으로 계약에 태운다(엔진 계약 위반 아님).
  ※ 단서절(rule_1_proviso)·병렬분리(split_parallel)·OR분리(split_or)로 생긴 의미절은
    원문 연속 부분문자열이 아닐 수 있다(어미 변형·재조합). 이 경우는 "토큰 포함율"로 보조 판정:
    의미절의 어절(공백분리 토큰) 중 원문에 존재하는 비율이 0.8 이상이면 MATCH로 본다.
    (0.8 미만 = 왜곡 후보 MISMATCH)
- MISMATCH = 의미절 내용이 원문에 충분히 없음 → **왜곡/환각 후보**

보고: 의미절 총 / MATCH / MISMATCH(왜곡후보) 수 + MISMATCH 샘플 10
(샘플은 의미절 source_text 앞 60자 + 원본 part_text 앞 60자 나란히)

## 검증 3 — 재조합 충실성 (보조): 한 part의 의미절을 합치면 원문 핵심이 복원되나

part 단위로, 그 part에서 나온 모든 의미절의 source_text 어절 합집합이
원본 part_text 어절을 얼마나 덮는가(커버리지).

- part별 coverage = (의미절들이 덮은 원문 어절 수) / (원문 어절 수)
- 보고: coverage 분포(>=0.9 / 0.7~0.9 / <0.7 각 part 수) + coverage<0.7 part 샘플 10
  (커버리지 낮음 = 원문 상당 부분이 의미절로 안 넘어옴 = 누락 후보)

---

## 어댑터 스크립트 골격 (읽기 전용, _probe_ 접두, 끝나면 보존/삭제)

```python
# scripts/_probe_verify_origin_to_clause.py — 원본↔의미절 역검증 (수정 없음)
import os, re
from supabase import create_client
# check_engine 가 있으면 import, 없으면 동일 계약 함수를 아래에 재현
try:
    import check_engine as CE
    MATCH, MISMATCH, NO_RULE = CE.VERDICT_MATCH, CE.VERDICT_MISMATCH, CE.VERDICT_NO_RULE
except Exception:
    MATCH, MISMATCH, NO_RULE = "MATCH","MISMATCH","NO_RULE"

sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])

def norm(s): return re.sub(r"[\s\W]+","", s or "")
def tokens(s): return [t for t in re.split(r"\s+", (s or "").strip()) if t]

# 1) 의미절 전수 (source_part_id, source_text)
clauses, off = [], 0
while True:
    r = sb.table("semantic_clause").select("id,source_part_id,source_text,source_part_text").range(off,off+999).execute().data
    if not r: break
    clauses += r; off += 1000
    if len(r) < 1000: break

# part_text 는 source_part_text 에 동봉돼 있음(분해기가 함께 저장). 없으면 part 조회로 보강.
from collections import defaultdict
by_part = defaultdict(list)
for c in clauses: by_part[c["source_part_id"]].append(c)

# 검증2: 왜곡 (부분문자열 / 토큰포함율 0.8)
mm = []
for c in clauses:
    pt = norm(c.get("source_part_text"))
    st = norm(c.get("source_text"))
    if st and st in pt:
        continue
    toks = tokens(c.get("source_text"))
    if toks:
        hit = sum(1 for t in toks if t in (c.get("source_part_text") or ""))
        if hit/len(toks) >= 0.8: continue
    mm.append(c)
print("검증2 왜곡: 의미절", len(clauses), " MISMATCH(왜곡후보)", len(mm))
for c in mm[:10]:
    print("  절:", (c.get("source_text") or "")[:60])
    print("  원:", (c.get("source_part_text") or "")[:60])

# 검증3: 재조합 커버리지 (part 단위)
import statistics
cov_hi=cov_mid=cov_lo=0; lo_samples=[]
for pid, cs in by_part.items():
    ptt = cs[0].get("source_part_text") or ""
    ptoks = set(tokens(ptt))
    if not ptoks: continue
    covered = set()
    for c in cs:
        for t in tokens(c.get("source_text")):
            if t in ptoks: covered.add(t)
    cov = len(covered)/len(ptoks)
    if cov>=0.9: cov_hi+=1
    elif cov>=0.7: cov_mid+=1
    else:
        cov_lo+=1
        if len(lo_samples)<10: lo_samples.append((cov, ptt[:80]))
print("검증3 커버리지: >=0.9", cov_hi, " 0.7~0.9", cov_mid, " <0.7", cov_lo)
for cov, s in lo_samples: print(f"  cov={cov:.2f} :: {s}")
```
검증 1(누락)은 위 골격에 eligible part 모집단을 추가해 part_id 기준 의미절 0개를 센다
(decompose_v1.eligible_population 기준 재현 또는 law_article_part paragraph 전수 대비).

```bash
railway run python3 scripts/_probe_verify_origin_to_clause.py 2>&1 | tee /tmp/verify_origin.log
```

---

## 합격 기준 (카운트로 규모 파악 + 샘플 글읽기로 성격 판정)

- 검증2 MISMATCH(왜곡) 비율이 낮고(수%), 샘플이 "어미변형·재조합" 수준이면 정상.
  원문에 전혀 없는 내용이 생겼으면(진짜 환각) 보고에 강조.
- 검증3 coverage<0.7 part가 소수면 정상. 다수면 누락 구조 문제.
- 어느 수치도 "합격/불합격" 단정은 Claude·대표가 글로 보고 판정. Cursor는 색출·보고만.

## 보고 형식

```
[검증1 누락]   eligible part 수 / 의미절 보유 part / 의미절 0개 part(NO_RULE) + 샘플10
[검증2 왜곡]   의미절 총 / MATCH / MISMATCH(왜곡후보) + 샘플10(절·원 나란히)
[검증3 재조합] coverage >=0.9 / 0.7~0.9 / <0.7 part 수 + <0.7 샘플10
[비고]        에러·예상과 다른 점(수정 말고 기록만)
```

금지: check_engine·decompose 수정 / DB 쓰기 / 보정 / 분해규칙 변경. 검증·보고만. 끝나면 정지.
