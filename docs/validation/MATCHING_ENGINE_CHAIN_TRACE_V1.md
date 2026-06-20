# 거름망(법령매칭) 코드화 체인 확인 — MATCHING ENGINE CHAIN TRACE V1

**작성일**: 2026-06-20
**목적**: 이미 코드화된 거름망(법령매칭) 전체 체인을 확인. 이게 "매칭 고도화" 작업의 기준선.
**성격**: 확인 + 구조 확정. 수정 없음.
**전환점**: 직전 "draft_slot 건설 0건이라 무의미" 차단 보고는 잘못된 멈춤이었음.
  → 그 0건이 곧 고도화 대상이고, 연결해서 VR을 흘려야 문제가 잡힌다.

---

## 거름망 전체 체인 (코드 실측, 이미 코드화돼 있음)

```
[입력]  factories (사용자 입력 저장)
          │
          │  ① run_facility_applicability.py (거름망 1차 = 적용성 평가)
          │     - factories 11컬럼 SELECT
          │     - draft_slot(IF_NUMERIC, IF_SCOPE) 로드
          │     - FIELD_MAP(binding_field 11종)으로 매칭
          │       · IF_NUMERIC: compare_numeric (>=, <=, > , <)
          │       · IF_SCOPE: 필드 존재 여부
          │     - 결과 status: MATCH_CANDIDATE / POSSIBLE_CANDIDATE /
          │                    NOT_MATCHED / AMBIGUOUS / MISSING_DATA
          ▼
[거름망1] facility_applicability (적용성 판정 결과 기재) — 29,096건
          │
          │  ② run_task_candidate.py (거름망 2차 = 의무 후보 생성)
          │     - facility_applicability에서 MATCH/POSSIBLE만 로드
          │     - draft_slot(THEN_ACTION) 로드
          │     - ACTION_TO_TASK(23종 family→task_type) 매핑
          │       · INSPECT_FAMILY → INSPECTION_TASK_CANDIDATE
          │       · REPORT_FAMILY → REPORT_TASK_CANDIDATE
          │       · INSTALL/APPOINT/MANAGE/NOTIFY/... 23종
          │     - relation 연결: SCOPE/NUMERIC/FREQUENCY/TRIGGER/
          │       DEADLINE/EVIDENCE/EXCEPTION/REFERENCE/ACTOR
          ▼
[거름망2] task_candidate (의무 후보 기재) — 3,388건
          │  applicability_id / draft_id / part_id 로 법령 연결
          ▼
[출력]  Compiler Core (fetch_compiler_candidates) → 유료진단 결과
```

---

## 거름망의 입력 통로 (binding_field) = 매칭의 핵심

```
거름망이 입력을 받는 유일한 통로 = draft_slot.binding_field.
실측된 binding_field (11종):
  distance_value 415, equipment_type 260, facility_type 220,
  voltage_level 142, concentration_level 110, process_type 33,
  storage_capacity 23, power_capacity 15, area_size 12,
  monetary_value 6, employee_count 3

FIELD_MAP (binding_field → factories 컬럼, 11종):
  employee_count→employee_count, area_size→building_area,
  power_capacity→electrical_capacity_kw, voltage_level→transformer_kva,
  storage_capacity→gas_capacity_m3, facility_type→site_type,
  process_type→ksic_code, monetary_value→construction_amount,
  equipment_type→(EQUIPMENT_JOIN), concentration_level→(MISSING),
  distance_value→(MISSING)

★ 건설 전용 binding_field (tower_crane/excavation/scaffold/
  formwork/asbestos/blasting/diving/construction_process/work) = 0종.
```

---

## "연결하면 당연히 문제가 발생" — 그 문제의 정체 (확인)

```
연결(입력→거름망)을 하고 VR 건설 데이터를 흘리면:

  건설 입력(타워크레인=True, 굴착=True, 건설공정=CP-100…)이
  거름망 1차(run_facility_applicability)에 들어와도:
    → 매칭할 draft_slot의 binding_field가 건설용 0종
    → IF_NUMERIC/IF_SCOPE 어디에도 안 걸림
    → 건설 입력은 평가에 미반영, 일반 조건(ksic/emp/면적 등)만 통과
    → facility_applicability에 건설 고유 적용성 0건
    → task_candidate에 건설 고유 의무 0건

= 이것이 "연결하면 당연히 발생하는 문제".
  결과가 틀린 게 아니라, 건설 입력을 받을 매칭 규칙(거름망의 눈)이
  아직 좁다(11종, 건설 0종).
```

---

## 매칭 고도화의 대상 (확인된 지점, 작업은 별도)

```
거름망(코드)은 작동한다. 고도화 대상은 "거름망의 눈"을 넓히는 것:

[A] draft_slot에 건설 binding_field를 가진 조건 생성
    = 법령(건설 안전법조문)을 컴파일해 IF_SCOPE/IF_NUMERIC에
      tower_crane/excavation/asbestos… binding_field를 가진 slot 생성.
    → 법령 컴파일 = GPT 전담.

[B] FIELD_MAP에 건설 binding_field → factories 컬럼 매핑 추가
    = 평가 로직이 건설 binding_field를 factories 컬럼으로 읽도록.
    → 엔진 입력계약 = GPT 결정. (Claude 단독 금지)

[C] factories에 누락 건설 컬럼 + batch SELECT 추가
    = construction_process/work/excavation… 저장·조회.
    → DDL/스크립트 = Claude 가능 (단 [A][B] 매핑 확정 후).

순서: [A] 법령 컴파일(건설 조건) → [B] FIELD_MAP 매핑 → [C] 저장/조회 →
      연결 → VR 흘림 → 문제 수집 → 매칭 미세조정(고도화 반복).
```

---

## 이미 도입된 효율 장치 (사장님 언급 확인)

```
- VR 생성기: 섹터별 입력 생성 (이번 세션 c78040b/06307244).
  → 거름망에 흘릴 입력을 대량 생성하는 장치. 준비됨.
- 읽기(Reading): 결과 글 독해로 이상 수집 (PHASE 5).
  → 거름망 통과 결과의 문제를 사람이 잡는 장치. 준비됨.
- 거름망 코드화: run_facility_applicability + run_task_candidate.
  → 법령매칭을 배치 코드로 구현. 작동 중(29096/3388건).

= 장치는 다 있다. 남은 것은 거름망의 눈(binding_field)을
  섹터별로 넓혀 VR을 흘리며 매칭을 고도화하는 것.
```

---

## 완료 (확인)

```
거름망(법령매칭)의 코드화 체인을 확인하였다:
  factories → [run_facility_applicability] → facility_applicability
            → [run_task_candidate] → task_candidate → Compiler Core.

거름망은 작동하나 입력 통로(binding_field)가 11종으로 좁고
건설 전용은 0종이다. 따라서 연결 후 VR을 흘리면 건설 의무가
미출력되는 것은 예정된 문제이며, 이를 잡아 매칭을 고도화하는 것이
다음 작업이다. (법령 컴파일·FIELD_MAP은 GPT 전담, 저장/조회는 Claude)
```
