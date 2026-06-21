# INPUT TYPE COVERAGE MAP — 엔진 입력 처리 능력 구조 분석
# WO-INPUT-TYPE-COVERAGE-MAP-001

**작성일**: 2026-06-21
**목적**: 엔진이 처리 가능/불가능한 입력 유형을 구조적으로 분류. 개별 위험요소 아님.
**방법**: draft_slot section/binding_field 전수 + 본문 Reading. 수정 0.
**핵심**: "타워크레인 의무 추가"(땜질)가 아니라 "어떤 입력 TYPE을 처리 못하나"(구조).

---

## ★★★ 구조적 결론

```
엔진은 "조건을 추출"은 하지만 "조건을 입력값과 연결(binding)"하는 것은
수치형(IF_NUMERIC)과 분류형(IF_SCOPE)에만 한다.
Boolean/이벤트 조건(IF_CONDITION)은 추출되었으나 binding_field가 0건 →
입력값과 영영 만나지 못함.

= 타워크레인이 안 나오는 건 "타워크레인 binding이 없어서"가 아니라
  "Boolean 조건을 입력에 잇는 binding 메커니즘 자체가 없어서".
```

---

## 수행 1-2: binding_field 전수 × section 분류

```
[IF_NUMERIC — 수치 비교, operator(<,<=,>,>=,RANGE) 있음]
  distance_value 415 / voltage_level 142 / concentration_level 110 /
  storage_capacity 23 / power_capacity 15 / area_size 12 /
  monetary_value 6 / employee_count 3
  = 8종 726건. binding_field 보유.

[IF_SCOPE — 분류 매칭, operator 없음]
  equipment_type 260 / facility_type 220 / process_type 33
  = 3종 513건. binding_field 보유.

[IF_CONDITION — 조건 표현, binding_field = 0건(none) ★]
  2525건 전부 binding_field 없음.
  family: IF_AFTER_INSTALL(설치하는 경우) / IF_OPERATIONAL(사용하는 경우) /
          IF_ON_CHANGE(변경한 경우) / IF_OVER_THRESHOLD(초과/이상) /
          UNRESOLVED_CONDITION(해당하는/법인인 경우)

[IF_ACTOR 7513 — 주체] / [EXCEPTION 535 — 예외]
[THEN_FREQUENCY 504 — 주기: ANNUAL332/PERIODIC36/QUARTERLY13/SEMI_ANNUAL4]
[THEN_DEADLINE 2022 — 기한] / [THEN_EVIDENCE 2284 — 증빙]
```

---

## 수행 3-4: TYPE별 의무 생성 + 작동 판정

```
TYPE-A 수치형 (근로자수/면적/거리/용량/전압/농도)
  binding: IF_NUMERIC 8종 726건, operator 정상.
  결과: distance/voltage/concentration 등이 실제 평가됨.
  판정: PASS

TYPE-B 분류형 (시설종류/업종/설비종류)
  binding: IF_SCOPE 3종 513건 (equipment/facility/process_type).
  결과: facility_type 등 scope 매칭 작동.
  판정: PASS

TYPE-C Boolean 위험요소 (타워크레인/발파/석면/밀폐공간/잠수)
  binding: 0건. IF_OPERATIONAL("사용하는 경우")은 IF_CONDITION에 있으나
    binding_field 없음 → 입력(has_tower_crane 등)과 연결 안 됨.
  결과: 위험요소 입력해도 의무 0.
  판정: FAIL ★

TYPE-D 복합조건 (근로자50 AND 타워크레인)
  binding: IF_CONDITION에 조건 표현은 있으나 binding 0 +
    AND 결합 메커니즘 미확인. numeric 단독평가만 존재.
  판정: FAIL ★

TYPE-E 기간/주기 (6개월/1년/3년)
  binding: THEN_FREQUENCY family 분류됨(ANNUAL/QUARTERLY...).
    inspection_schedule_ready에 일부 반영(on_demand_count).
    단 UNRESOLVED_FREQUENCY 101건, 주기→실제 일정 산출은 부분.
  판정: PARTIAL

TYPE-F 행위 이벤트 (신규설치/해체/증설/변경)
  binding: IF_AFTER_INSTALL("설치하는 경우") / IF_ON_CHANGE("변경한 경우")가
    IF_CONDITION에 추출됨. 단 binding_field 0 + 이벤트 입력 자체 없음.
  판정: FAIL ★
```

---

## 수행 5: TYPE별 GAP

```
TYPE   유형         판정      GAP
A      수치형       PASS      없음 (VALID_LOCK 후보)
B      분류형       PASS      없음 (VALID_LOCK 후보)
C      Boolean      FAIL      IF_CONDITION→binding_field 미연결.
                              Boolean trigger binding 메커니즘 부재.
D      복합조건     FAIL      AND/OR 결합 평가 메커니즘 부재.
E      주기형       PARTIAL   주기 family는 있으나 일정 산출 부분 +
                              UNRESOLVED 101.
F      이벤트형     FAIL      이벤트 입력 부재 + IF_CONDITION 미연결.
```

★ 사장님 예상과 일치:
```
TYPE-A 수치형   PASS    ✓
TYPE-B 분류형   PASS    ✓
TYPE-C Boolean  FAIL    ✓
TYPE-D 복합조건 FAIL    ✓
TYPE-E 주기형   PARTIAL ✓
TYPE-F 이벤트형 FAIL    ✓
```

---

## ★ 근본 원인 (구조)

```
엔진 평가 경로(evaluate_single_factory):
  _load_draft_slot_groups가 section IN ('IF_NUMERIC','IF_SCOPE')만 적재.
  → IF_CONDITION(Boolean/이벤트)은 평가 루프에 아예 안 들어감.

= IF_CONDITION 2525건은 "추출은 됐으나 평가되지 않는 죽은 조건".
  타워크레인 "사용하는 경우"가 여기 묻혀 있음.

→ 해결의 레벨:
  (하) 타워크레인 의무 추가 = 땜질 (TYPE-C 한 건)
  (상) Boolean Trigger Binding 설계 = IF_CONDITION을 입력에 잇는
       binding 메커니즘 신설 (TYPE-C/D/F 동시 해결)
```

---

## GPT 인계 (상위 레벨 과제)

```
[기존 인계(WO-INPUT-OBLIGATION-BINDING-HANDOFF) 상향 조정]
  "타워크레인/석면 의무 binding 추가" →
  "Boolean Trigger Binding 메커니즘 설계"로 격상.

[필요한 GPT 설계]
  1. IF_CONDITION family(IF_OPERATIONAL/IF_AFTER_INSTALL/IF_ON_CHANGE)를
     입력값에 잇는 binding_field 유형 신설 (boolean/event).
  2. _load_draft_slot_groups가 IF_CONDITION도 적재하도록 평가 경로 확장
     (단 이건 compiler_core 영역 = 엔진 수정, GPT/사장님 승인).
  3. TYPE-D 복합조건: 여러 IF_* 를 AND/OR 결합하는 평가 규칙.
  4. FIELD_MAP: has_tower_crane/has_blasting/... → boolean binding.

[효과]
  한 번의 메커니즘 설계로 TYPE-C(Boolean)+TYPE-F(이벤트) 동시 해결.
  타워크레인/석면/발파/밀폐공간/잠수가 일괄 연결됨.
```

---

## 성공 기준

```
- binding_field 전수 분류        → ✅ (NUMERIC 8 / SCOPE 3 / CONDITION 0연결)
- TYPE 분류                      → ✅ (A~F)
- TYPE별 의무 생성 집계          → ✅
- TYPE별 작동 판정               → ✅ (A/B PASS, C/D/F FAIL, E PARTIAL)
- TYPE별 GAP                     → ✅
- 엔진 능력 구조적 설명          → ✅ (IF_CONDITION 미평가가 근본)
- 수정 0건                       → ✅
```

---

## 완료 문장

```
엔진의 입력 처리 능력을 6유형으로 분류한 결과,
수치형(A)·분류형(B)은 PASS, Boolean(C)·복합(D)·이벤트(F)는 FAIL,
주기(E)는 PARTIAL이다. 근본 원인은 IF_CONDITION(2525건, Boolean/이벤트 조건)이
추출되었으나 binding_field가 0건이고 평가 루프(IF_NUMERIC/IF_SCOPE만 적재)에
포함되지 않는 구조다. 따라서 다음 과제는 "타워크레인 의무 추가"가 아니라
"Boolean Trigger Binding 메커니즘 설계"로 격상되며, 이는 TYPE-C/D/F를
동시에 해결한다. 수정은 수행하지 않았다.
```
