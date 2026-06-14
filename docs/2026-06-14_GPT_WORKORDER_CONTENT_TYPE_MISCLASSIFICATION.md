# [GPT 작업지시서] 법령엔진 content_type 오분류 — 벌칙·효력·준용·위임이 OBLIGATION으로 분류됨

- 작성: 2026-06-14 (Claude 기획창)
- 대상: **GPT (법령엔진/Compiler/판정로직/content_type 분류 전담)**
- 영역 구분: 본 문제는 **분해기·content_type 분류 로직**(1층, GPT 전담 영역). Claude는 executor 보정(2·3층)
  과정에서 증거를 수집했을 뿐, 분해기·content_type은 **미수정**. 수정 범위·방식은 GPT가 결정.
- 우선순위: **높음** — 사업장 진단 결과에 "의무"로 표시되는 항목에 벌칙·효력·준용 조항이 섞여 들어감.
  사용자가 "내 사업장이 이행해야 할 의무"로 오인할 수 있음.
- 함께 읽기: 2026-06-14_EXECUTOR_FIX_ALL_DONE.md(executor 보정 전체), 2026-06-09_GPT_WORKORDER_OBLIGATION_OUTPUT_BUG.md(형식 참조)

---

## 1. 증상 (executor 보정 중 발견)

executor(수범자) 보정 작업에서 의미절 12,358건의 주어를 교정하던 중,
**content_type=OBLIGATION으로 분류된 의미절 안에 "의무가 아닌 것"이 다수 섞여 있음**을 발견.
이들은 executor(주어)를 보정할 수 없음 — 애초에 의무 주체를 가질 문장이 아니기 때문(벌칙·효력·준용·위임).

executor 보정에서 이들을 EXCLUDE(제외) 처리한 건수: **741건**.

---

## 2. 근본 원인 (DB 실측 증거)

`semantic_clause` content_type별 분포 (executor 보정에서 EXCLUDE된 741건 기준):

| content_type (현재) | 실제 성격 | 건수 | 종결어 증거 |
|---|---|---|---|
| OBLIGATION | **벌칙(PENALTY)** | 677 | "처한다 / 과태료를 부과한다 / 벌금 / 징역" |
| OBLIGATION | **효력규정** | 21 | "소멸한다 / 효력을 상실한다 / 로 본다" |
| OBLIGATION | **위임규정** | 18 | "대통령령으로 정한다 / 조례로 정한다 / 법률로 정한다" |
| OBLIGATION | **준용규정** | 10 | "준용한다 / 준용할 수 있다" |
| AUTHORITY / PROHIBITION 등 | (혼재) | 15 | — |

### 실측 문장 표본 (content_type=OBLIGATION인데 벌칙·효력)
```
[OBLIGATION→벌칙] "다음 각 호의 어느 하나에 해당하는 자는 3년 이하의 징역 또는 3천만원 이하의 벌금에 처한다."
[OBLIGATION→벌칙] "다음 각 호의 어느 하나에 해당하는 자에게는 300만원 이하의 과태료를 부과한다."
[OBLIGATION→벌칙] "제16조제2항에 따른 생산 또는 판매 금지명령을 위반한 자는 2천만원 이하의 벌금에 처한다."
[OBLIGATION→양벌] "법인의 대표자나 …종업원이 …위반행위를 하면 그 행위자를 벌하는 외에 그 법인 또는 개인에게도 …벌금…"
```

→ 종결어가 "처한다/부과한다(벌칙)", "소멸한다/상실한다(효력)", "준용한다(준용)", "정한다(위임)"인 문장이
   OBLIGATION으로 분류됨. **이들은 사업장이 이행할 의무가 아님.**

---

## 3. 발생 경로 (Claude 추적, GPT 확인 필요)

- content_type은 분해기(decompose_v1.py) 또는 그 후처리에서 의미절마다 부여됨(GPT 전담).
- 벌칙 조항("…한 자는 …에 처한다")이 "…한 자는"이라는 수범자형 주어를 가져서 OBLIGATION으로
  오분류된 것으로 추정. 그러나 이 "자"는 의무 주체가 아니라 **처벌 대상**.
- 효력("저당권이 소멸한다")·준용("제10조를 준용한다")·위임("대통령령으로 정한다")도
  서술 종결이 의무형이 아닌데 OBLIGATION으로 떨어짐.

---

## 4. 요청 사항 (GPT 판단·실행)

> 아래는 Claude가 파악한 방향일 뿐, **수정 범위·방식은 분해기·content_type 전담인 GPT가 결정.**
> 글 읽기 기반 의미검증 원칙(카운트 아닌 의미, LLM은 어댑터/별도단계 격리) 유지.

1. **벌칙 재분류**: 종결이 "…에 처한다 / 과태료를 부과한다 / 벌금 / 징역"인 의미절을
   OBLIGATION → **PENALTY**(또는 분해기 표준 벌칙 content_type)로 재분류할지 GPT가 판단.
   - 주의: "위반한 자는 …처한다"의 "자"는 의무 주체가 아니라 처벌 대상 → executor 보정 대상 아님.
2. **효력/준용/위임 재분류**: "소멸한다/상실한다"(효력), "준용한다"(준용), "정한다"(위임)
   종결 의미절이 OBLIGATION이 맞는지 재검토. 이들은 사업장 이행 의무가 아니므로 진단 결과에서
   "의무"로 노출되면 안 됨.
3. content_type 분류 로직(분해기 또는 후처리)에 종결어·의미 기반 판정을 반영할지 GPT가 설계.
4. 재분류 후, 진단 결과(무료·유료·하니스)에서 벌칙·효력·준용이 "의무" 블록에서 빠지는지 검증.

---

## 5. Claude 영역(executor 보정)과의 경계

- executor 보정(2·3층)은 이 741건을 **EXCLUDE 처리**(executor 보정 대상에서 제외)했을 뿐,
  content_type은 **건드리지 않음**(GPT 영역). 임시테이블 semantic_clause_fix의 fix_status로만 표시:
  - EXCLUDE_PENALTY(411): 벌칙
  - EXCLUDE_NONOBLIG(약 328): 효력·준용·위임·기타 의무아님
  - BLOCKED_NONSUBJECT(2): 대통령령 등 법령형식어
- 원본 semantic_clause의 content_type은 **무변경**. 운영 미반영.
- GPT가 content_type을 고치면, executor 보정의 EXCLUDE 분류와 일치하는지 교차검증 가능.

---

## 6. 영향 범위

- 무료진단·유료진단·검증하니스 결과의 "의무" 목록에 벌칙·효력·준용 조항 혼입.
- SaaS 작업할당(의무→작업 생성): 벌칙이 의무로 분류되면 이행 작업이 잘못 생성될 수 있음.
- 진단 "법적 리스크" 표시: 벌칙은 의무 미이행의 "결과"로 연결돼야지 의무 자체로 나오면 안 됨.

---

## 7. 증거 재현 쿼리

```sql
-- content_type=OBLIGATION인데 종결이 벌칙/효력/준용/위임인 의미절
SELECT content_type, left(source_text, 100) AS source_text
FROM semantic_clause
WHERE content_type='OBLIGATION'
  AND source_text ~ '(처한다|과태료를 부과한다|벌금|징역|소멸한다|효력을 상실|준용한다|대통령령으로 정한다|조례로 정한다)'
LIMIT 20;

-- executor 보정이 EXCLUDE 처리한 741건 (임시테이블, 교차검증용)
SELECT f.fix_status, o.content_type, count(*)
FROM semantic_clause_fix f JOIN semantic_clause o ON o.id=f.id
WHERE f.fix_status IN ('EXCLUDE_PENALTY','EXCLUDE_NONOBLIG','BLOCKED_NONSUBJECT')
GROUP BY 1,2 ORDER BY 3 DESC;
```
