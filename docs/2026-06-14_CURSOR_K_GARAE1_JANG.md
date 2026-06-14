# CURSOR 작업지시서 K — 갈래1 보정 3회차: "~의 장" 직책 주어 (첫 주격 주어만)

작성일: 2026-06-14
발행: Claude 기획창 / 수행: Cursor (로컬/railway, kiwipiepy + Supabase)
근거: docs/2026-06-14_EXECUTOR_FIX_STRATEGY.md (완벽 2조건 + BLOCKLIST B1/B2/B3)

---

## 이번 회차 — "~의 장" 직책 주어 (갈래1 미보정 중)

1·2회차: 주격직결 1,280 + 소유격 60 = 1,340 APPLIED. 대통령령 2 BLOCKED.
이번: 미보정 갈래1 중 원문에 "**~의 장 + 주격조사**"가 있는 856건.
"장"은 직책=사람이라 사물 위험 0(B3 안전). 사전 무관하게 보정 후보.

Claude 표본 글읽기(20건) 결과:
- 다수 정확: "재난관리책임기관의 장은…", "지방환경관서의 장은…", "주관연구기관의 장은…"
- 단 "의 장"이 **꼭 문장 맨 앞은 아님** — 조건절("제1항에 따라…", "필요한 경우")이 앞서면 중간에 옴.
- 함정: "의 장" 앞에 **이미 다른 주격 주어**가 있으면 모호.
  (예: "수당…은 …기관 또는 시설의 장이 지급한다" → 앞에 "수당은"이 먼저. 어느 게 의무주체인지 애매.)

## "완벽" 정의 (변함없음) + 이번 회차 규칙
- 조건1: 수정 후 Kiwi 재검증 작동. 조건2: 원문서 확정.
- 이번 추출 규칙:
```
"~의 장 + 주격조사(은/는/이/가)" 를 주어로 추출하되:
  ① 그 "의 장" 구절이 문장의 **첫 번째 주격 주어**일 때만.
     (그 앞에 다른 [명사+주격조사 은/는/이/가] 주어가 없어야 함.
      단 앞이 조건절 '제N항…/…에 따라/…경우' 같은 부사절이면 OK — 부사절은 주어 아님.)
  ② "의 장" 직후가 관형형(정하는/규정하는 등 ETM)이면 제외 (B2 수식절 함정).
  ③ 복합 주어(나열: "A장관, B 및 C의 장") → 이번엔 제외(미룸). 다음 회차.
     판별: "의 장" 앞 같은 주어구 안에 쉼표/및/또는/와/과 + 다른 명사가 있으면 나열로 보고 미룸.
주어 = "<...>의 장" (해당 기관명 포함 전체, 단 ③ 나열은 제외).
```

## 성격 / 안전 경계 (1·2회차 동일)
- 원본 semantic_clause 수정 금지. semantic_clause_fix(임시)에서만. executor_text는 STEP까지 보존.
- 분해기·Kiwi사전 무변경. 동사어간 사전등록 금지. Kiwi 사전 = 자가생산 1,348 NNP.

---

## STEP 1 — "~의 장" 첫주격 주어 추출 (Kiwi)
대상: fix_flag='GARAE1_VERB_STEM' AND fix_status NOT IN ('APPLIED','APPLIED_POSS','BLOCKED_NONSUBJECT')
      AND source_part_text에 '의 장(은|이|는|가)' 포함.
각 원문을 Kiwi 토큰화 → 위 규칙으로 "의 장" 주어 추출.
분류: PERFECT_JANG(첫주격·단순) / SKIP_PRIOR_SUBJECT(앞에 다른 주어) / SKIP_ENUM(나열) /
      SKIP_B2(직후 관형형).

## STEP 2 — executor_fixed 채움 (PERFECT_JANG만)
```sql
UPDATE semantic_clause_fix SET executor_fixed='<...의 장>', fix_status='FIXED_JANG' WHERE id=<id>;
-- executor_text 안 건드림
```

## STEP 3 — Kiwi 재색출 검증 (조건1) ★
executor_fixed를 Kiwi 색출 규칙으로 재판정 → 전부 OK(명사끝, "장"=NNG)인지.
REFIX_FAIL 나오면 그 건+형태소 보고. 0 기대.

## STEP 4 — 표본 글읽기 (Claude 판정)
FIXED_JANG 중 무작위 25건:
```
법령·조문 | 원문 source_part_text 앞 90자 | executor_text(기존) | executor_fixed(=…의 장) | content_type
```
+ "의 장" 앞에 다른 주어가 안 섞였는지, 나열이 안 들어왔는지 확인.

## 보고 형식
```
[선별]    의장 대상 총 / PERFECT_JANG / SKIP_PRIOR_SUBJECT / SKIP_ENUM / SKIP_B2 각 건수
[채움]    FIXED_JANG 건수
[재색출]  OK 수 / REFIX_FAIL(+샘플) — 0 기대
[표본]    25건 (위 형식)
[비고]    특이점 (수정 말고 기록만, executor_text 미변경 확인)
```
표본·재색출 통과 시 → executor_text 반영은 Claude가 이 창에서. 원본 복사는 보정 다 끝낸 뒤.
금지: 원본 수정 / executor_text 변경(추출·채움·표본만) / 나열·앞주어있음·수식절 보정 /
      분해기·사전 변경 / 동사어간 등록. 끝나면 정지.
