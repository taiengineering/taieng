# CURSOR 작업지시서 L — 갈래2 보정 1회차: 수식절 뒤 주어명사 (유형 A)

작성일: 2026-06-14
발행: Claude 기획창 / 수행: Cursor (로컬/railway, kiwipiepy + Supabase)
근거: docs/2026-06-14_EXECUTOR_FIX_STRATEGY.md, _LEGAL_PIPELINE_3LAYER.md

---

## 갈래2란 / 유형 분류 (Claude 표본 글읽기 결과)

갈래2 = executor가 동사구(받은/받으려는/요청받은/제출받은/위탁받 등)로 잡힌 4,464건.
가설("수범자")보다 복잡, 표본 결과 3유형:
- **유형 A (다수)**: "동사구(받은/받으려는…) + 주어명사 + 주격조사" → 그 명사가 진짜 주어.
  예: "요청받은 **도급인은**…제출해야 한다" → 도급인 / "받으려는 **시행자는**" → 시행자 /
      "제출받은 **식품의약품안전처장은**" → 식품의약품안전처장 / "요구받은 **비치의무자는**" → 비치의무자
  (executor "요청받/받으려/제출받"은 주어를 꾸미는 수식절 동사. 진짜 주어는 그 뒤 명사.)
- 유형 B (485): "~해서는/하여서는 아니 된다" 금지문. 주어는 source_part 앞에 있음. (이번 제외)
- 유형 C (261): executor가 "위해서/관하여/대해서" 부사구 꼬리. 주어 아님. (이번 제외, needs_review)

**이번 회차 = 유형 A만.** 갈래1 "의 장"·"A의 B"에서 검증된 "수식 뒤 명사+주격조사" 방법의 재적용.
차이: 갈래2는 동사구가 주어 **앞**(받으려는 자) → "동사구 다음 명사+주격조사"를 주어로.

## "완벽" 정의 (변함없음) + 이번 규칙
- 조건1 재검증 작동 ∧ 조건2 원문서 확정.
- 추출 규칙:
```
executor가 동사구(받은/받으려는/요청받은/제출받은/위탁받은/신청받은/지원받은/적용받은/지급받은 등
  '받' 계열, 또는 하려는/되려는)일 때:
1. 원문 source_part_text에서 executor에 해당하는 동사구를 찾고, 그 직후의
   [명사덩어리 + 주격조사(은/는/이/가)]를 주어로 추출.
   ("요청받은 도급인은" → 도급인 / "받으려는 시행자는" → 시행자)
2. 추출 주어가:
   - 첫 주격 주어이고 (앞에 다른 주격주어 없음, 조건절 '제N항/…경우/…따라'는 OK)
   - 사물 아님 (B3: 배관/사고/시설/금액 등 사물접미 제외)
   - 직후 관형형(B2 수식절) 아님
   → executor_fixed 채움
3. 못 찾거나 사물/모호 → SKIP (needs_review)
주어는 수식 포함 가능("받으려는 자") 또는 명사만("도급인"). 구체명사면 명사만, 일반명사(자)면 수식포함 권장.
```

## 성격 / 안전 경계 (갈래1 회차와 동일)
- 원본 semantic_clause 수정 금지. semantic_clause_fix(임시)에서만. executor_text는 STEP까지 보존.
- 분해기·Kiwi사전 무변경. 동사어간 사전등록 금지. Kiwi 사전 = 자가생산 1,348 NNP.
- 대상: fix_flag='GARAE2_SUBJECT_VERB' AND fix_status='TAGGED'(미보정).

## STEP 1 — 유형 A 주어 추출 (Kiwi)
각 갈래2 의미절의 source_part_text를 Kiwi 토큰화 → 위 규칙으로 "동사구 뒤 주어명사" 추출.
분류: PERFECT_A(추출 성공·첫주격·비사물) / SKIP_PRIOR / SKIP_SAMUL / SKIP_B2 /
      SKIP_NO_MATCH(B 금지문·C 부사구 등 A 아님).

## STEP 2 — executor_fixed 채움 (PERFECT_A만)
```sql
UPDATE semantic_clause_fix SET executor_fixed='<주어>', fix_status='FIXED_G2A' WHERE id=<id>;
-- executor_text 안 건드림
```

## STEP 3 — Kiwi 재색출 검증 (조건1) ★
executor_fixed 재판정 → 전부 OK(명사끝)인지. REFIX_FAIL(+샘플) 보고, 0 기대.

## STEP 4 — 표본 글읽기 (Claude 판정)
FIXED_G2A 무작위 25건:
```
법령·조문 | 원문 source_part_text 앞 95자 | executor_text(기존 동사구) | executor_fixed(주어) | content_type
```
특히 동사구 뒤 주어가 정확히 잡혔는지, 사물·앞주어 함정 없는지.

## 보고 형식
```
[분류]   갈래2 대상 총 / PERFECT_A / SKIP_PRIOR / SKIP_SAMUL / SKIP_B2 / SKIP_NO_MATCH 각 건수
[채움]   FIXED_G2A 건수
[재색출] OK 수 / REFIX_FAIL(+샘플) — 0 기대
[표본]   25건 (위 형식)
[비고]   특이점 (수정 말고 기록만, executor_text 미변경 확인)
```
표본·재색출 통과 시 → executor_text 반영은 Claude가 이 창에서. 원본 복사는 보정 다 끝낸 뒤.
금지: 원본 수정 / executor_text 변경(추출·채움·표본만) / 금지문B·부사구C 보정(이번 제외) /
      분해기·사전 변경 / 동사어간 등록. 끝나면 정지.
