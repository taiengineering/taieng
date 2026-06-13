# CURSOR 작업지시서 E — Kiwi 재색출 2회차 (자가생산 사전 주입 + 규칙 보강)

작성일: 2026-06-13
발행: Claude 기획창 / 수행: Cursor (로컬/railway, kiwipiepy)
근거: docs/2026-06-13_CURSOR_D_KIWI_FULL_SCAN.md (1회차 결과),
      docs/2026-06-13_LEGAL_ENGINE_ROOTCAUSE_PIPELINE_SWAP.md 10장

---

## 1회차에서 드러난 것 (이번 보강의 근거)

1회차 전수 색출 결과: 의무류 41,877 중 FLAG(오추출) 11,678, REVIEW 443, NULL 421.
Claude가 결과를 글로 분석해 확인한 것:
- **가짜 양성 존재**: "수급인/도급인/하수급인/관계수급인"이 Kiwi에서 ETM(관형형)으로
  오태깅됨 → REVIEW로 빠짐. 그러나 원문 글읽기 결과 **이들은 정상 주어**
  ("하수급인은 …아니 된다", "도급인은 …요청할 수 있다"). 법률 미등록어 오태깅.
  → 법률주체를 Kiwi 사용자 사전에 명사로 등록하면 해소됨.
- **REVIEW 443 안에 진짜 오추출도 섞임**: 전문가에게(JKB 조사끝), 지체없(부사), 상당하(형용사),
  새로(부사), 콘크리트믹서트럭에(사물+조사) → 이들은 FLAG로 편입해야.
- **FLAG 안에 두 갈래**: 갈래1=동사어간 잘림(정하/설치하/해당하), 갈래2=수범자 동사구
  (되려/받으려/하려/제출받 = "~하려는/받는 자"가 주어인데 동사만 잡힘). 보정법이 달라 분리 필요.

## 성격 / 안전 경계
- **분해기·의미절·DB 일절 수정 안 함.** Kiwi 색출은 읽기 전용. 사전은 Kiwi 메모리에만 주입.
- DB는 SELECT만. 색출(어느 게 오추출인가)만. 보정은 나중 별도 트랙.
- 반복 루프 2회차. 1회차와 무엇이 달라졌는지(사전 주입·규칙 보강) 추적 가능하게.

---

## STEP 1 — 자가생산 사전 추출 (의미절 DB에서)

Claude 확인: 의미절의 정상 executor(명사 어미로 끝나는 고유값) = **1,348개**. 이것이 사전.
수급인/도급인/하수급인/관계수급인/허가권자/발주청/관계인 등이 여기 포함됨(확인됨).

```sql
-- 자가생산 사전: 의무류 executor 중 명사주체 고유값 (빈도 2+ 권장, 동사어미 제외)
SELECT executor_text, count(*) AS cnt
FROM semantic_clause
WHERE content_type IN ('OBLIGATION','PROHIBITION','AUTHORITY')
  AND executor_text IS NOT NULL
  AND executor_text ~ '(자|인|장|관|회|주|사|원|청|부|국|단|소|처|책임자|권자|업자|기관|공단|협회|정부|위원|공무원|근로자|대통령|도지사|군수|구청장|시장)$'
  AND executor_text !~ '(하|되|지|려|어|아|여)$'
  AND length(executor_text) BETWEEN 2 AND 40
GROUP BY executor_text
HAVING count(*) >= 2
ORDER BY cnt DESC;
```
이 목록을 Kiwi 사용자 사전으로 등록(고유명사 NNP, 높은 점수로 우선):
```python
for word in subject_dict:           # 위 쿼리 결과 executor_text들
    kiwi.add_user_word(word, "NNP", 5.0)   # 점수 높게 → 분해 우선
```
※ 주의: 사전은 "명사 어미로 끝나는 검증된 주체"만. 동사어간(정하 등)은 절대 사전에 넣지 말 것
  (넣으면 진짜 오추출이 명사로 둔갑 = 색출 무력화).

## STEP 2 — 보강된 색출 규칙

```
executor를 (사전 주입된) Kiwi로 토큰화 → 마지막 형태소 품사:
  명사류 NN*/XSN/NP/NNB                         → OK (정상 주어)
  동사·활용·어미 XSV/VV/VA/VX/EC/EF/EP          → FLAG (오추출)
  [보강] 조사 JK*/JX, 부사 MAG, 기호 SS*, 형용사파생 XSA → FLAG (비주어)
  그 외                                          → REVIEW (글읽기 필요, 자동판정 안 함)
```
FLAG를 두 갈래로 분리 태깅:
```
갈래2(수범자 동사구) 후보: 마지막이 EC/EF 이거나 값이 '~려/~받/~받으려/~하려'로 끝남
                          (되려·받으려·하려·제출받·요청받·지정받으려 등)
갈래1(동사어간 잘림) 후보: 그 외 FLAG (정하·설치하·해당하·관할하 등 XSV/VV)
```

## STEP 3 — 전체 재색출 + 1회차 대비

```python
# scripts/_probe_kiwi_rescan_v2.py — 사전주입 + 보강규칙 재색출 (읽기 전용)
import os
from collections import Counter, defaultdict
from supabase import create_client
from kiwipiepy import Kiwi

sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])
kiwi = Kiwi()

# STEP1: 자가생산 사전 주입
dict_rows = sb.rpc... # 위 SQL 실행(또는 .table().select 후 파이썬 필터). executor_text 목록 확보
subject_dict = [r["executor_text"] for r in dict_rows]
for w in subject_dict:
    try: kiwi.add_user_word(w, "NNP", 5.0)
    except: pass
print(f"사전 주입: {len(subject_dict)}개")

NOUN = ("NNG","NNP","NNB","NP","XSN")
VERBISH = ("XSV","VV","VA","VX","EC","EF","EP")
NONSUBJ = ("JKB","JKS","JKO","JKC","JX","MAG","SSC","SSO","SW","XSA")  # 보강: 조사·부사·기호·형용사파생

# 의무류 executor 전수
rows, off = [], 0
while True:
    r = sb.table("semantic_clause").select("id,executor_text,content_type")\
        .in_("content_type",["OBLIGATION","PROHIBITION","AUTHORITY"]).range(off,off+999).execute().data
    if not r: break
    rows += r; off += 1000
    if len(r) < 1000: break

def classify(ex):
    toks = kiwi.tokenize(ex)
    if not toks: return "REVIEW", None, toks
    lt = toks[-1].tag; base = lt.split("-")[0]
    if base in NOUN: return "OK", lt, toks
    if base in VERBISH or lt in VERBISH:
        # 갈래 분리
        garae = "갈래2_수범자" if (base in ("EC","EF") or ex.endswith(("려","받"))) else "갈래1_동사어간"
        return f"FLAG/{garae}", lt, toks
    if base in NONSUBJ or lt in NONSUBJ: return "FLAG/비주어", lt, toks
    return "REVIEW", lt, toks

cnt = Counter(); g1=g2=other_flag=0; samples=defaultdict(list)
for c in rows:
    ex = c.get("executor_text")
    if not ex: cnt["NULL"] += 1; continue
    verdict, lt, toks = classify(ex)
    cnt[verdict] += 1
    if verdict.startswith("FLAG") and len(samples[verdict])<8:
        samples[verdict].append((ex,[(t.form,t.tag) for t in toks]))

print("=== 2회차 분포 ===")
for k,v in cnt.most_common(): print(f"  {k}: {v}")
print("=== FLAG 샘플 ===")
for k,s in samples.items():
    print(f"--- {k} ---")
    for ex,parts in s: print(f"    {ex!r} :: {parts}")

# 1회차 가짜양성 해소 확인
print("=== 가짜양성 체크 (사전 주입 후 OK여야 정상) ===")
for w in ["수급인","도급인","하수급인","관계수급인","허가권자","발주청"]:
    v,lt,_ = classify(w); print(f"  {w}: {v} (last={lt})")
```
```bash
python3 scripts/_probe_kiwi_rescan_v2.py 2>&1 | tee /tmp/kiwi_rescan_v2.log
```

## 보고 형식
```
[사전]    주입 주체명사 개수
[분포]    OK / FLAG/갈래1 / FLAG/갈래2 / FLAG/비주어 / REVIEW / NULL  (각 건수)
[1회차대비] FLAG 총 11,678 → 2회차 FLAG 총 N' (증감)
[가짜양성] 수급인/도급인/하수급인/관계수급인/허가권자/발주청 → 사전주입 후 OK 됐는가
[샘플]    갈래1·갈래2·비주어 각 8건 (executor + 형태소 나열)
[비고]    여전히 이상한 것 (수정 말고 기록만)
```

이 결과로 Claude가 3회차(또 다른 가짜양성/누락 패턴) 필요 여부를 판정.
색출 안정되면 → 의미절 보정 트랙(갈래1/갈래2별 다른 보정법) 설계.
금지: 분해기·의미절·DB 수정 / 보정 / 동사어간 사전등록. 색출·보고만. 끝나면 정지.
