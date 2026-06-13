# CURSOR 작업지시서 C — Kiwi 형태소 분석기 부분 테스트 (executor 색출 적합성)

작성일: 2026-06-13
발행: Claude 기획창 / 수행: Cursor (로컬, pip install kiwipiepy)
근거: docs/2026-06-13_LEGAL_ENGINE_ROOTCAUSE_PIPELINE_SWAP.md 10장
      (형태소 분석기 = 색출 전용, 분해기 무수정, 색출/분석에만 격리 활용)

---

## 목적 — 전체 적용 전에 Kiwi가 우리 executor를 제대로 가르는지 시험

executor 오추출(동사어간이 주어로 잘못 잡힘)을 Kiwi 품사 태깅으로 색출할 수 있는지
**작은 정답지로 먼저 검증**한다. 통과하면 전체(58,495) 색출로 확대, 불통과면 보고만.

## 성격 / 안전 경계
- **분해기(decompose_v1.py)·의미절 테이블 일절 건드리지 않는다.** Kiwi는 색출 시험용.
- **DB에 쓰지 않는다.** Kiwi에 문자열만 넣어 품사 결과를 stdout으로 본다.
- Kiwi는 색출/분석 도구로만 격리(생성/분해에 넣지 않음 — 10장 원칙).
- 이 단계는 "Kiwi가 쓸만한가" 시험이지 보정·적용이 아니다.

## 설치
```bash
pip install kiwipiepy
```
(C++ 기반, JDK 불필요. Railway/로컬 어디서든 pip만으로 설치)

---

## 정답지 (Claude가 의미절 테이블에서 직접 추출 — 이게 채점 기준)

**A그룹 = 정상 주어 (Kiwi가 '명사'로 판정해야 통과):**
사업주, 고용노동부장관, 국토교통부장관, 시ㆍ도지사, 위원회, 사용자, 제조업자, 관리감독자, 대통령

**B그룹 = 오추출 의심 (Kiwi가 '동사/형용사 어간' 등 비명사로 판정해야 통과):**
정하, 해당하, 받으려, 설치하, 인정하, 실시하, 취급하, 관련되, 구입하, 지도ㆍ조언하

핵심 기대:
- A그룹 → 마지막 형태소가 명사(NNG/NNP/XSN 등) → "주어 자격 있음"
- B그룹 → 동사어간(VV)/형용사(VA)/연결어미 잔여 등 → "주어 자격 없음(오추출)"
- 특히 "정하/해당하/설치하/실시하/취급하/인정하/구입하" = 동사 'X하다'의 어간이 잘린 것 →
  Kiwi가 'X하'를 어떻게 보는지가 관건(명사+'하' 동사파생 또는 동사어간으로).

---

## 테스트 스크립트 (읽기 전용, _probe_ 접두)
```python
# scripts/_probe_kiwi_executor_test.py — Kiwi executor 색출 시험 (DB 안 씀)
from kiwipiepy import Kiwi
kiwi = Kiwi()

A = ["사업주","고용노동부장관","국토교통부장관","시ㆍ도지사","위원회","사용자","제조업자","관리감독자","대통령"]
B = ["정하","해당하","받으려","설치하","인정하","실시하","취급하","관련되","구입하","지도ㆍ조언하"]

def analyze(word):
    toks = kiwi.tokenize(word)
    # 각 형태소의 (형태, 품사) 나열 + 마지막 형태소 품사
    parts = [(t.form, t.tag) for t in toks]
    last_tag = toks[-1].tag if toks else None
    return parts, last_tag

def is_noun_subject(word):
    # 색출 규칙(시험용): 마지막 형태소가 명사류면 주어 자격, 동사/형용사면 오추출
    _, last = analyze(word)
    if not last: return None
    return last.startswith("NN") or last in ("XSN","NP","NNB")  # 명사·명사파생·의존명사

print("=== A그룹 (정상 주어 — 명사 기대) ===")
for w in A:
    parts, last = analyze(w)
    verdict = "주어OK" if is_noun_subject(w) else "오추출판정"
    print(f"  {w:20} last={last:6} {verdict}  :: {parts}")

print("=== B그룹 (오추출 의심 — 비명사 기대) ===")
for w in B:
    parts, last = analyze(w)
    verdict = "주어OK" if is_noun_subject(w) else "오추출판정"
    print(f"  {w:20} last={last:6} {verdict}  :: {parts}")
```
```bash
python3 scripts/_probe_kiwi_executor_test.py 2>&1 | tee /tmp/kiwi_test.log
```

---

## 합격 기준 (글로 읽어 판정 — Claude·대표)

- **A그룹 9개 전부 "주어OK"(명사 판정)** 이고
- **B그룹 10개 전부 "오추출판정"(비명사)** 이면 → Kiwi 색출 적합, 전체 확대.
- 일부 어긋나면(예: "정하"를 명사로 봄, "위원회"를 동사로 봄) → 어긋난 항목과 그 품사 결과를
  **그대로 보고**. 수정·튜닝하지 말 것. Claude가 보고 색출 규칙(is_noun_subject)을 조정할지,
  사용자 사전을 쓸지 판정.
- 'X하'(정하/설치하 등)가 Kiwi에서 어떻게 분석되는지 **형태소 나열 전체**를 꼭 보고에 포함
  (예: 정하 → [('정하','VV')] 인지 [('정','NNG'),('하','XSV')] 인지가 색출 규칙 설계에 결정적).

## 보고 형식
```
[설치]   kiwipiepy 버전
[A그룹]  9개 각각: 단어 / last_tag / 판정 / 형태소 전체나열
[B그룹]  10개 각각: 단어 / last_tag / 판정 / 형태소 전체나열
[요약]   A 명사판정 n/9, B 비명사판정 n/10
[비고]   어긋난 항목·특이점 (수정 말고 기록만)
```

금지: 분해기·의미절 수정 / DB 쓰기 / Kiwi 튜닝·사전등록(이번 시험은 기본설정 그대로) /
      전체 적용. 시험·보고만. 끝나면 정지.
