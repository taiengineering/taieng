# RISK EXPANSION LOOP #001 — 4종 확대 시도
# WO-RISK-EXPANSION-LOOP-001

**목적**: 타워크레인/석면/발파/밀폐 4종을 결과에 등장. 변경→실행→읽기.
**결과**: 4종 전부 미출현. IF_CONDITION binding 무효 확인 → 롤백.

---

## STEP-1+2 4종 사업주 의무 draft 평가가능 slot
```
산안기준규칙 4종 의무의 IF_* slot 전수:
  석면해체 작업 시 조치     → IF_CONDITION 1개
  타워크레인의 지지         → IF_CONDITION 1개
  (열차운행감시인)         → IF_CONDITION 1개
  발파 / 밀폐공간          → 평가가능 slot 0 (IF_NUMERIC/SCOPE/CONDITION 없음)
= 4종 중 석면·타워크레인만 IF_CONDITION 보유. 발파·밀폐는 조건 slot 자체가 없음.
```

## STEP-3+4 변경 (묶음)
```
석면·타워크레인 IF_CONDITION slot 2개 → employee_count >= 0 일괄.
(잠수가 IF_NUMERIC으로 출현했으니 IF_CONDITION도 시도)
롤백: binding_field NULL.
```

## STEP-5+6 실행 → 읽기
```
factory-test-run(7b9bf18d) 재실행 → 결과 7건 (변경 전과 동일).
```

## STEP-7 4종 출현 여부 (문장 읽기)
```
타워크레인: 미출현
석면:      미출현
발파:      미출현
밀폐:      미출현
잠수:      출현 (유지)
```

## STEP-8 판정
```
GOOD/BETTER/BEST: 미달 (4종 0개 등장)
ROLLBACK 조건(C/D/E 증가): 해당 없음 (오염 0).
실제 판정: 변화 없음 → IF_CONDITION binding 무효 → 롤백(불필요 변경 제거).
```

---

## ★ 읽은 결과가 확정한 사실 (실측)

```
IF_CONDITION에 employee_count binding을 걸어도 결과에 안 나옴.
  = 잠수(IF_NUMERIC)는 출현, 석면·타워크레인(IF_CONDITION)은 미출현.
  = 평가 루프(_load_draft_slot_groups)가 IF_NUMERIC/IF_SCOPE만 적재하고
    IF_CONDITION은 적재 안 함이 결과로 확인됨(이론 아닌 실측).

발파·밀폐: 조건 slot(IF_*) 자체가 0 → binding 걸 자리도 없음.

= 4종(타워크레인/석면/발파/밀폐)은 현재 binding 방식(IF_NUMERIC+employee_count)
  으로는 결과에 못 나옴. 구조적으로 막힘.
  → Boolean trigger를 평가하는 메커니즘(IF_CONDITION 적재 + boolean binding)이
    필요. 이는 compiler_core 평가경로 확장 + binding 설계 = GPT 영역.
```

---

## 현재 유지 상태 (롤백 후)
```
A(사업장 의무): 3건 (건설기술진흥법)
B(위험요소 의무): 1건 (잠수)
C(기술기준): 소수 / D·E: 0 / WRONG: 0
= 직전 GOOD 상태 유지. 4종 확대는 GPT Boolean 메커니즘 전제.
```

---

## 완료 문장

```
타워크레인/석면/발파/밀폐 4종 확대를 시도하여 석면·타워크레인의
IF_CONDITION slot에 binding을 적용하고 재실행했으나 4종 모두 미출현하였다.
결과 읽기로 IF_CONDITION binding이 평가 루프에 진입하지 못함(잠수 IF_NUMERIC만
출현)을 확인하고, 효과 없는 변경을 롤백하였다.
발파·밀폐는 조건 slot 자체가 없어 binding 대상도 아니다.
4종 확대는 현 수치형 binding 방식으로는 구조적으로 막혀 있으며,
IF_CONDITION 평가 + Boolean binding(compiler_core 확장, GPT 영역)이 전제임을
결과로 확정하였다. 현재 A 3종 + B 잠수 1종 / WRONG 0 상태를 유지한다.
```
