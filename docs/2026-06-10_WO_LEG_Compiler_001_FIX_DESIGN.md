# WO-LEG-Compiler-001 산출물 (Claude) — 오매핑 추출기 위치 + 수정 설계안

작성일: 2026-06-10
작성: Claude (위치 식별·수정 설계) — **엔진 직접 수정 안 함(역할분리)**
수정 실행: GPT (분해기/Compiler 전담)
근거: public_token `86ff8075-412a-43c4-b9d3-dfed65c5e080` (제조업 80명 화학공장)

> 이 문서는 "조문 사례집"이 아니라 **오매핑을 만든 추출기의 코드 위치와
> 패턴 단위 수정 설계**다. 개별 조문 수정·예외처리·블랙리스트 금지.

---

## 핵심 결론 (한 줄)

`numeric_constraint`를 만들 때 **"N명/N인" 패턴이면 주어(subject)와 무관하게
`constraint_type = EMPLOYEE_THRESHOLD_CANDIDATE`로 분류**되고, 이후 단계가 이를
**그대로 `employee_count` binding으로 확정**한다. 그 숫자의 주어가 유족·위원·
발기인·부상자·정원이어도 전부 "사업장 근로자 수"로 둔갑한다.

---

## 파이프라인상 오류 3개 층 (코드 확정)

```text
Law Article
   ↓
Parser → numeric_constraint(constraint_type, subject)   ← ① 1차 분류기 (주어 무시)
   ↓
run_numeric_family.py → numeric_family_candidate(family) ← ② Subject 게이트 부재
   ↓
run_executable_draft.py → draft_slot(binding_field)      ← ③ Binding 무조건 employee_count
   ↓
Compiler / Applicability (정상 — 주어진 조건을 정확히 평가)
   ↓
Output (오매핑 노출)
```

---

## A. Subject Extractor (1차 분류기) — 위치·오류·수정안

**파일/위치**: `numeric_constraint` 테이블을 생성하는 Parser 단계.
  (`constraint_type`, `subject` 컬럼을 채우는 코드. scripts/ 내 numeric_constraint
   생성 스크립트 또는 그 상위 Parser. GPT가 정확한 함수 위치 특정 필요 —
   `run_numeric_family.py`는 이미 만들어진 `numeric_constraint`를 읽기만 함.)

**오류 패턴 (데이터로 확인)**:
`constraint_type='EMPLOYEE_THRESHOLD_CANDIDATE'`의 subject 분포 —
  - 진짜 근로자: "상시근로자"(8), "상시근로자수가"(9), "상시"(22) → 정상
  - **오분류**: "위원"(7), "전문가"(12), "이사"(4) = 위원회 정원 /
    "부상자가"(8), "사망자가"(5), "실종자가"(3), "특수교육대상자가"(3) = 재해자 수 /
    "보행자수가"(5), "정원이"(5), "수용인원"(3), "보육정원이"(3) = 무관 대상
  - **추출 실패**: "포함한"(107), "포함하여"(91), "각각"(22), "이상"(17),
    "경우에는"(7), "따라"(8) = 조사/부사를 주어로 오인 / "UNKNOWN_SUBJECT"(86)

즉 **"N명/N인"이라는 숫자 패턴만 보고 EMPLOYEE로 분류**하며, 주어 추출 자체가
부정확하다(조사·연결어가 subject로 들어옴).

**수정안 (패턴 단위)**:
1. `EMPLOYEE_THRESHOLD_CANDIDATE` 분류 조건에 **주어 화이트리스트**를 건다.
   주어가 {상시근로자, 근로자, 종업원, 노동자} 계열일 때만 EMPLOYEE로 분류.
2. 주어가 {위원, 위원장, 전문가, 이사, 발기인, 유족, 수급권자, 부상자, 사망자,
   실종자, 정원, 수용인원, 보행자, 용접사, 잠수작업자 …}면 EMPLOYEE 아님 →
   `PERSON_COUNT_OTHER_CANDIDATE`(신규) 또는 `UNKNOWN_THRESHOLD_CANDIDATE`로.
3. 주어 추출이 조사/부사("포함한","각각","이상","따라")로 잡히면 추출 실패로
   간주 → `UNKNOWN_SUBJECT` 처리(주어 토큰 정제 규칙 보강).

---

## B. Scope Extractor — 위치·오류·수정안

**파일/위치**: `run_executable_draft.py` (draft_slot 생성) + Parser의 scope 추출.
  draft_slot section 중 `IF_SCOPE`를 채우는 경로, `UNRESOLVED_SCOPE` family.

**오류 패턴 (글로 확인)**:
- "표면공급식 잠수작업을 하는 경우" → scope=잠수작업이어야 하는데 IF_SCOPE 없이
  `employee_count>=1`만 생성.
- "압력용기에 용접사가…작업할 때" → scope=압력용기 용접 작업인데 누락.
- NFPC 설치기준(간이스프링클러·도로터널·고층건축물) → 해당 설비/시설 보유 scope
  없이 `NO_CONDITION`(IF_SCOPE/IF_NUMERIC 둘 다 없음) → 무조건 적용.

**수정안 (패턴 단위)**:
1. 본문에 "**~을 하는 경우 / ~작업 시 / ~를 설치한 경우**" 패턴이 있으면
   IF_SCOPE 슬롯을 생성하고 해당 작업/설비 scope_family를 부여.
   (잠수작업/발파작업/밀폐공간작업/압력용기/특정 소방설비 …)
2. `UNRESOLVED_SCOPE`가 있는 draft는 employee_count fallback으로 통과시키지 말 것
   (C 항목과 연동).
3. `NO_CONDITION`(슬롯 없음) draft는 "무조건 적용" 대신 보류 상태로 둘 것.

---

## C. Binding Generator — 위치·오류·수정안

**파일/위치**: `scripts/run_executable_draft.py`
  - `SCOPE_BINDING` 딕셔너리 (라인 상단):
    ```python
    SCOPE_BINDING = {
        "EMPLOYEE_SCOPE_FAMILY":     "employee_count",
        "EMPLOYEE_THRESHOLD_FAMILY": "employee_count",   # ← 무조건 박음
        ...
    }
    ```
  - 적용 루프:
    ```python
    for family, field in SCOPE_BINDING.items():
        cur.execute("UPDATE draft_slot SET binding_field=%s "
                    "WHERE family_name=%s AND binding_field IS NULL", (field, family))
    ```

**오류 패턴**:
`family_name='EMPLOYEE_THRESHOLD_FAMILY'`이기만 하면 **주어 검증 없이**
`binding_field='employee_count'`를 박는다. A의 오분류가 그대로 통과된다.
또 `run_numeric_family.py`의 `SUBJECT_HINTS`는 subject를 **family 강화(restriction)
에만** 쓰고 **family 차단에는 안 쓴다** → 주어가 근로자가 아니어도 안 막힌다.

**수정안 (패턴 단위)**:
1. A에서 subject 게이트가 적용되어 family가 올바르면, 이 binding은 자동 정상화됨
   (EMPLOYEE_THRESHOLD_FAMILY가 진짜 근로자에만 붙으므로).
2. 보강: binding 직전에도 subject가 근로자 계열이 아닌데 EMPLOYEE family면
   binding_field를 NULL로 두고 `UNRESOLVED`로 표시(이중 안전장치).
3. `run_numeric_family.py`의 SUBJECT_HINTS를 **양방향**으로:
   근로자 계열 → EMPLOYEE 확정 / 비(非)근로자 주어 → EMPLOYEE 차단.

---

## D. 수정 후 예상 영향 범위 (추정)

- A의 주어 게이트가 핵심. `EMPLOYEE_THRESHOLD_CANDIDATE`로 분류된 것 중
  주어가 근로자가 아닌 건이 **과반**(위 분포상 진짜 근로자는 소수).
  → 동일 패턴 조문이 **법령 수십 개·draft 수백 건** 단위로 동시 교정됨.
- 특히 "포함한/포함하여"(198건) 같은 추출실패가 정제되면 광범위 정상화.
- 개별 조문(유족·위원회·잠수작업)은 손대지 않아도, A·B·C 추출기를 고치면
  같은 유형이 일괄로 빠진다.

---

## 성공 기준 (재검증, 카운트 아님)

같은 80명 화학공장 재진단 시 **글을 읽어** 확인:
- 제거: 유족 대표자 선임 / 판정·재심사·심의위원회 운영 / 각종 기관 지정요건 /
  협회 설립인가 / 잠수작업·압력용기 용접사 지정
- 잔존: 관리감독자 / 안전보건관리책임자 / 위험물 / 화학물질 / 소방 / 전기 등
  실제 사업장 의무

---

## GPT에게 (핵심)

> **개별 조문 수정·예외처리·블랙리스트 금지.**
> 수정 지점은 단 세 곳: ① numeric_constraint를 만드는 Parser의 주어 분류
> (EMPLOYEE 화이트리스트 게이트), ② run_numeric_family.py의 SUBJECT_HINTS를
> 양방향 게이트로, ③ run_executable_draft.py SCOPE_BINDING 직전 subject 재검증.
> A를 고치면 B·C는 대부분 자동 정상화된다. 동일 유형 수백 건이 한 번에 교정되어야 한다.

(주의: 위 세 파일은 법령엔진 분해/Compiler 계층 = GPT 전담. Claude는 위치·설계만
제출했고 코드를 수정하지 않았다.)
