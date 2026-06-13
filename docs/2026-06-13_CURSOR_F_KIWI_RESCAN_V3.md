# CURSOR 작업지시서 F — Kiwi 재색출 3회차 (REVIEW 0 수렴 + 가짜음성 역검증)

작성일: 2026-06-13
발행: Claude 기획창 / 수행: Cursor (로컬/railway, kiwipiepy)
근거: docs/2026-06-13_CURSOR_E_KIWI_RESCAN_V2.md (2회차 결과)

---

## 왜 3회차인가 (대표 지시)

executor 하나가 룰로 잡히면 **수십만 명을 움직이는 지시**가 되고, 틀리면 **수십만 명이
패싱**하게 된다. 0.04%(16건)도 그냥 못 넘긴다. 한 건이 한 사업장의 안전관리자 선임
누락이 될 수 있다. 그래서:
1. 잔여 REVIEW 16건을 규칙에 흡수해 **REVIEW를 0으로 수렴**.
2. 지금까지 못 본 **반대 방향 = 가짜 음성**(OK로 통과했지만 실은 오추출)을 색출.
   놓친 오추출(패싱)이 잘못 잡은 것보다 위험하다.

## 성격 / 안전 경계
- 분해기·의미절·DB 수정 안 함. Kiwi 색출 읽기 전용. 사전은 Kiwi 메모리에만.
- 2회차 사전(자가생산 1,348개 NNP) 그대로 주입. 동사어간 사전 등록 절대 금지.
- 반복 루프 3회차. 색출·보고만.

---

## STEP 1 — REVIEW 16건 패턴 규칙 흡수 (Claude 원문 글읽기로 확정)

Claude가 잔여 16건 원문을 글로 확인한 결과 **전부 오추출**(정상 주어 0건):
- ETN(~기): 상환받기·끊기·꼬아넣기 — 동사 명사형. 진짜 주어는 문장 앞(기금관리기관의 장 등).
- JC(~와/과): 공사와·법과 — 접속조사 잘림.
- ETM: 어린(←어린이 잘림). XPN: 구조부재(사물). IC/잘림: 적합통보ㆍ허.
- Z_CODA: 근로능력있. SN: 90.

규칙 보강: 마지막 형태소가 다음이면 FLAG(비주어)로 편입:
```
기존 비주어: JKB JKS JKO JKC JK* JX MAG SSC SSO SW XSA
[3회차 추가]: ETN ETM JC XPN IC SN Z_CODA  (동사명사형·관형형·접속·접두·감탄·숫자·잔여)
```
→ REVIEW가 0 또는 극소수로 수렴해야. 남으면 그 품사·원문 보고.

## STEP 2 — 가짜 음성 역검증 (OK 통과분 중 숨은 오추출 색출) ★핵심

OK로 통과한 ~29,519건은 "마지막 형태소가 명사"라서 통과했다. 그러나 명사로 끝나도
주어가 아닌 것이 숨어 있을 수 있다(패싱 위험). 이를 역으로 색출:

OK 통과분 중 아래 의심 패턴을 **색출만**(고치지 말 것):
```
(가) 사물 명사 주어 의심: executor가 사물·대상으로 끝남
     (설비/장치/기계/시설/구조/부재/금액/기준/서류/자료/계획/물질/제품/차량/선박 등)으로 끝나는데
     의무류인 경우 → 사람이 아닌 사물이 주어 → 검토 대상
(나) 너무 짧음: 길이 2 이하 명사 (이/그/제/것 등 대명사·의존명사 잔여)
(다) 의존명사/대명사로 끝남: 것/바/때/곳/수 (NNB·NP)
(라) 추상 동작명사: ~화/~성/~도/~기 로 끝나는 명사형(안정도·주기 류)이 주어 자리
```
이것들은 "명사로 끝나서 OK였지만 진짜 주어가 아닐 수 있는" 후보다.
**색출만 하고, 각 유형 건수 + 샘플 10 + 원문 앞부분을 보고.** Claude가 글로 읽어
진짜 가짜음성인지 판정한다(자동 단정 금지 — 사물 주어가 정당한 경우도 있음: "구조부재는…").

## STEP 3 — 스크립트
```python
# scripts/_probe_kiwi_rescan_v3.py — 3회차: REVIEW수렴 + 가짜음성 색출 (읽기 전용)
import os, re
from collections import Counter, defaultdict
from supabase import create_client
from kiwipiepy import Kiwi

sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])
kiwi = Kiwi()
# 2회차 사전 그대로 주입
dict_rows = sb.table("semantic_clause").select("executor_text,content_type")\
    .in_("content_type",["OBLIGATION","PROHIBITION","AUTHORITY"]).execute().data
# (실제로는 페이지네이션으로 전수 → 명사어미 필터 → 고유값. 2회차 STEP1 SQL과 동일 집합)
# 여기선 2회차와 동일한 1,348개 목록을 재구성해 주입
# ... (2회차 STEP1 SQL 결과 사용) ...
# for w in subject_dict: kiwi.add_user_word(w, "NNP", 5.0)

NOUN=("NNG","NNP","NNB","NP","XSN"); VERBISH=("XSV","VV","VA","VX","EC","EF","EP")
NONSUBJ=("JKB","JKS","JKO","JKC","JX","MAG","SSC","SSO","SW","XSA",
         "ETN","ETM","JC","XPN","IC","SN","Z_CODA")   # 3회차 보강
SAMUL=("설비","장치","기계","시설","구조","부재","금액","기준","서류","자료","계획",
       "물질","제품","차량","선박","설계도","도면","장비","건축물","구조물")
ARTIFACT_TAIL=("화","성","도","기")  # 추상 동작/속성 명사형

rows, off = [], 0
while True:
    r = sb.table("semantic_clause").select("id,executor_text,content_type,source_text")\
        .in_("content_type",["OBLIGATION","PROHIBITION","AUTHORITY"]).range(off,off+999).execute().data
    if not r: break
    rows += r; off += 1000
    if len(r) < 1000: break

cnt=Counter(); review=[]; fn=defaultdict(list)
for c in rows:
    ex=c.get("executor_text")
    if not ex: cnt["NULL"]+=1; continue
    toks=kiwi.tokenize(ex); lt=toks[-1].tag if toks else None
    base=(lt or "").split("-")[0]
    if base in NOUN:
        cnt["OK"]+=1
        # 가짜음성 역검증
        if any(ex.endswith(s) for s in SAMUL): fn["사물주어"].append((ex,c.get("source_text","")[:70]))
        elif len(ex)<=2: fn["너무짧음"].append((ex,c.get("source_text","")[:70]))
        elif base in ("NNB","NP"): fn["의존명사/대명사"].append((ex,c.get("source_text","")[:70]))
        elif any(ex.endswith(t) for t in ARTIFACT_TAIL) and base=="NNG": fn["추상동작명사"].append((ex,c.get("source_text","")[:70]))
    elif base in VERBISH or lt in VERBISH: cnt["FLAG_동사류"]+=1
    elif base in NONSUBJ or lt in NONSUBJ: cnt["FLAG_비주어"]+=1
    else: cnt["REVIEW"]+=1; review.append((ex,lt,c.get("source_text","")[:70]))

print("=== 3회차 분포 ==="); 
for k,v in cnt.most_common(): print(f"  {k}: {v}")
print(f"=== REVIEW 잔여 {len(review)} ===")
for ex,lt,s in review[:30]: print(f"  {ex!r} [{lt}] :: {s}")
print("=== 가짜음성 색출(OK 중 의심) ===")
for typ, items in fn.items():
    print(f"--- {typ}: {len(items)}건 ---")
    for ex,s in items[:10]: print(f"    {ex!r} :: {s}")
```
```bash
python3 scripts/_probe_kiwi_rescan_v3.py 2>&1 | tee /tmp/kiwi_rescan_v3.log
```

## 보고 형식
```
[분포]   OK / FLAG_동사류 / FLAG_비주어 / REVIEW / NULL
[REVIEW] 잔여 건수 + 전체 목록(품사+원문) — 0 수렴 확인
[가짜음성] 사물주어 / 너무짧음 / 의존명사 / 추상동작명사 각 건수 + 샘플10(원문 포함)
[비고]   특이점 (수정 말고 기록만)
```

이 결과로 Claude가 가짜음성을 글로 판정 → 색출 최종 확정 또는 4회차 여부 결정.
금지: 분해기·의미절·DB 수정 / 보정 / 동사어간 사전등록. 색출·보고만. 끝나면 정지.
