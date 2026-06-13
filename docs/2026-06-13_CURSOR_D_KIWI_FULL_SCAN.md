# CURSOR 작업지시서 D — Kiwi 전체 executor 색출 (반복 루프 1회차)

작성일: 2026-06-13
발행: Claude 기획창 / 수행: Cursor (로컬/railway, kiwipiepy)
근거: docs/2026-06-13_CURSOR_C_KIWI_PARTIAL_TEST.md (부분테스트 결과),
      docs/2026-06-13_LEGAL_ENGINE_ROOTCAUSE_PIPELINE_SWAP.md 10장

---

## 부분테스트 결과 (확정된 색출 규칙의 근거)

Kiwi 부분테스트(C)에서 드러난 것:
- A그룹(정상주어) 9/9 = 전부 마지막 형태소가 명사(NNG/NNP/XSN).
- B그룹(오추출) = 전부 마지막 형태소가 XSV(하/되) 또는 VV/EC.
  · 설치하→설치/NNG+하/XSV, 인정하→인정/NNG+하/XSV, 지도ㆍ조언하→…+하/XSV
  · 정하→정하/VV(단일), 받으려→받/VV+으려/EC
- **핵심 교훈: "첫 형태소"가 아니라 "마지막 형태소"가 명사인지로 판정해야 한다.**
  한국어 주어(명사)는 명사로 끝남. XSV(하/되)·VV·EC로 끝나면 동사 활용이 잘린 오추출.

## 확정 색출 규칙 (이번 회차)
```
executor를 Kiwi로 토큰화 → 마지막 형태소 품사 검사:
  마지막이 NN* / XSN / NP / NNB (명사류)  → 정상 주어 후보 (OK)
  마지막이 XSV / VV / VA / VX / EC / EF / EP (동사·활용·어미) → 오추출 (FLAG)
  그 외(SW만 등) → 보류(REVIEW)
```

---

## 목적 — 전체 58,495 의미절의 executor를 색출해 "진짜 오추출 N건" 확정

이것은 반복 루프의 1회차다:
1. (이번) 전체 Kiwi 색출 → 오추출 N건 + 패턴별 분류
2. (다음, Claude 분석) N건 패턴 분석 → 색출 규칙 보강점 도출
3. 보강 규칙으로 재색출 (1 반복)
4. 분석 (2 반복) … 색출 안정될 때까지
5. 안정 후에만 의미절 수정(보정 트랙)

## 성격 / 안전 경계
- **분해기·의미절·DB 일절 수정 안 함.** Kiwi 색출은 읽기 전용. 몇 번 돌려도 안전.
- Kiwi는 색출 도구로 격리(생성/분해에 안 넣음 — 10장).
- 이번은 색출(어느 게 오추출인가)만. 보정(올바른 주어로 교체)은 나중 별도 트랙.
- 기본 설정 Kiwi(사용자 사전·튜닝 없이) — 회차마다 무엇을 바꿨는지 추적 위해.

---

## 스크립트 (읽기 전용, _probe_ 접두)
```python
# scripts/_probe_kiwi_executor_full.py — 전체 executor Kiwi 색출 (DB 안 씀, 읽기만)
import os
from collections import Counter, defaultdict
from supabase import create_client
from kiwipiepy import Kiwi

kiwi = Kiwi()
sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])

NOUN = ("NNG","NNP","NNB","NP","XSN")          # 명사류 = 주어 OK
VERBISH = ("XSV","VV","VA","VX","EC","EF","EP","VV-R","VV-I")  # 동사·활용·어미 = 오추출

# 의무류 의미절의 executor 전수 (페이지네이션)
rows, off = [], 0
while True:
    r = sb.table("semantic_clause").select("id,executor_text,content_type")\
        .in_("content_type", ["OBLIGATION","PROHIBITION","AUTHORITY"])\
        .range(off, off+999).execute().data
    if not r: break
    rows += r; off += 1000
    if len(r) < 1000: break

def last_tag(text):
    toks = kiwi.tokenize(text)
    return (toks[-1].tag if toks else None), toks

ok = flag = review = nullc = 0
flag_by_lasttag = Counter()
flag_samples = defaultdict(list)   # 마지막품사별 샘플
for c in rows:
    ex = c.get("executor_text")
    if not ex:
        nullc += 1; continue
    lt, toks = last_tag(ex)
    if lt is None:
        review += 1; continue
    base = lt.split("-")[0]
    if base in NOUN:
        ok += 1
    elif base in VERBISH or lt in VERBISH:
        flag += 1
        flag_by_lasttag[lt] += 1
        if len(flag_samples[lt]) < 5:
            flag_samples[lt].append((ex, [(t.form,t.tag) for t in toks]))
    else:
        review += 1
        flag_by_lasttag[f"REVIEW:{lt}"] += 1
        if len(flag_samples[f"REVIEW:{lt}"]) < 5:
            flag_samples[f"REVIEW:{lt}"].append((ex, [(t.form,t.tag) for t in toks]))

print(f"의무류 executor 총: {len(rows)}")
print(f"  정상주어(OK, 명사끝): {ok}")
print(f"  오추출(FLAG, 동사/어미끝): {flag}")
print(f"  보류(REVIEW): {review}")
print(f"  executor NULL: {nullc}")
print("=== 오추출 마지막품사 분포 ===")
for tag, cnt in flag_by_lasttag.most_common(20):
    print(f"  {tag}: {cnt}")
print("=== 마지막품사별 샘플(각5) ===")
for tag, samples in list(flag_samples.items())[:15]:
    print(f"--- {tag} ---")
    for ex, parts in samples:
        print(f"    {ex!r} :: {parts}")

# 오추출 executor 값 빈도(보정 트랙 준비용)
exec_freq = Counter(c["executor_text"] for c in rows
                    if c.get("executor_text") and
                    (lambda lt: lt and lt.split("-")[0] in VERBISH or lt in VERBISH)(last_tag(c["executor_text"])[0]))
print("=== 오추출 executor 값 상위 30 ===")
for v, cnt in exec_freq.most_common(30):
    print(f"  {v!r}: {cnt}")
```
```bash
python3 scripts/_probe_kiwi_executor_full.py 2>&1 | tee /tmp/kiwi_full.log
```

## 보고 형식
```
[규모]   의무류 executor 총 / OK(명사끝) / FLAG(오추출) / REVIEW / NULL
[분포]   오추출 마지막품사 분포 (XSV n, VV n, EC n, REVIEW:xx n …)
[샘플]   마지막품사별 샘플 5개씩 (executor + 형태소 전체나열)
[빈도]   오추출 executor 값 상위 30 (정하 n, 해당하 n …)
[비고]   특이점·예상과 다른 점 (수정 말고 기록만)
```

이 결과로 Claude가 2회차(패턴 분석 → 규칙 보강)를 설계한다.
금지: 분해기·의미절·DB 수정 / 보정 / Kiwi 튜닝·사전등록 / 의미절 변경. 색출·보고만. 끝나면 정지.
