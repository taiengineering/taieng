# CONSTRUCTION FILTER CONNECTION REPORT V1
# WO-CONSTRUCTION-FILTER-CONNECTION-001

**작성일**: 2026-06-20
**목적**: 건설 입력을 FacilityProfile → 거름망 구간에 연결.
**규칙-004 적용**: "건설 입력→FacilityProfile YES" 확정됨. 재조사 안 함. 거름망 진입점만.
**금지 준수**: 법령/Compiler Core/섹터로직/VR/엔진 수정 없음. 결과 분석 없음.
**역할 경계**: 진입점 식별(STEP-1)은 Claude 수행. 실제 전달 연결(FIELD_MAP/draft_slot 채움)은 엔진 영역 = GPT.

---

## 확정된 전제 (재조사 안 함)

```
건설 입력 → 저장 → FacilityProfile = YES (WO-REAL-PIPELINE-CONNECTION-002 확정)
  FacilityProfile에 건설 입력 키 22종 존재:
    has_tower_crane / has_confined_space / has_asbestos / has_blasting /
    has_diving_work / has_excavation_work / has_scaffold_work /
    has_formwork_work / has_demolition_work / construction_type /
    construction_amount / subcontractor_company_count /
    construction_process_code·name·version /
    construction_work_code·name·version·amount·duration·worker_count

끊기는 구간 = FacilityProfile → 거름망 (단일 지점, 확정).
```

---

## STEP-1: 건설 입력별 거름망 진입점 식별 (매핑표)

```
거름망 입력 통로 구조 (facility_applicability_eval.py):
  - FIELD_MAP: binding_field → factories 컬럼
  - 매칭 종류:
      IF_NUMERIC (수치 비교: >=, <=, >, <) → compare_numeric
      IF_SCOPE   (필드 존재/해당 여부)      → 존재하면 POSSIBLE_CANDIDATE
```

### 건설 입력 → 거름망 진입점 매핑표

| 건설 입력 (FacilityProfile) | 입력 타입 | 거름망 진입 방식 | 제안 binding_field | 현재 상태 |
|---|---|---|---|---|
| has_tower_crane | boolean | IF_SCOPE (존재) | `equipment_type` 또는 신규 `construction_equipment` | 통로 없음 |
| has_confined_space | boolean | IF_SCOPE | 신규 `construction_hazard` | 통로 없음 |
| has_asbestos | boolean | IF_SCOPE | 신규 `construction_hazard` | 통로 없음 |
| has_blasting | boolean | IF_SCOPE | 신규 `construction_hazard` | 통로 없음 |
| has_diving_work | boolean | IF_SCOPE | 신규 `construction_work` | 통로 없음 |
| has_excavation_work | boolean | IF_SCOPE | 신규 `construction_work` | 통로 없음 |
| has_scaffold_work | boolean | IF_SCOPE | 신규 `construction_work` | 통로 없음 |
| has_formwork_work | boolean | IF_SCOPE | 신규 `construction_work` | 통로 없음 |
| has_demolition_work | boolean | IF_SCOPE | 신규 `construction_work` | 통로 없음 |
| construction_type | text | IF_SCOPE | 신규 `construction_type` | 통로 없음 |
| construction_process_code | text | IF_SCOPE | 신규 `construction_process` | 통로 없음 |
| construction_work_code | text | IF_SCOPE | 신규 `construction_work` | 통로 없음 |
| construction_amount | numeric | IF_NUMERIC (>=) | `monetary_value` (기존) | **통로 존재** |
| subcontractor_company_count | numeric | IF_NUMERIC | 신규 `subcontractor_count` | 통로 없음 |
| construction_work_worker_count | numeric | IF_NUMERIC | `employee_count` 또는 신규 | 부분(employee 유사) |

```
※ 진입 방식은 입력 타입으로 결정:
   boolean/text(유무·종류) → IF_SCOPE (존재 기반)
   numeric(금액·인원) → IF_NUMERIC (수치 비교)
※ binding_field 명칭은 제안(예시)이며, 확정은 GPT(엔진 입력계약).
```

---

## STEP-2: 거름망이 읽는 입력 집합 — 건설 추가 위치

```
현재 거름망 입력 집합 (FIELD_MAP, 11종):
  employee_count, area_size, power_capacity, voltage_level,
  storage_capacity, facility_type, process_type, monetary_value,
  equipment_type, concentration_level(미연결), distance_value(미연결)

건설 입력이 들어갈 위치 = FIELD_MAP에 건설 binding_field 행 추가:
  construction_equipment → has_tower_crane (또는 EQUIPMENT_JOIN 확장)
  construction_hazard    → has_confined_space/asbestos/blasting (다중)
  construction_work      → has_excavation/scaffold/formwork/demolition/diving
  construction_type      → construction_type
  construction_process   → construction_process_code
  subcontractor_count    → subcontractor_company_count

★ 단 FIELD_MAP은 평가 로직(엔진 입력계약)이다.
  여기에 행을 추가하는 것 = 엔진이 무엇을 입력으로 평가하는가의 변경.
  = GPT 결정 영역. Claude 단독 수정 금지(이 WO "엔진 수정 금지" 포함).
```

---

## STEP-3: 건설 입력 전달 연결 — 현재 확인

```
has_tower_crane → 거름망 입력 도달 여부: NO (현재)

연결되려면 두 가지가 모두 필요:
  [a] FIELD_MAP에 binding_field(construction_equipment 등) → factories 컬럼 추가
      = 엔진 입력계약 (GPT)
  [b] 그 binding_field를 가진 draft_slot 존재
      = 법령 컴파일 (GPT, 이 WO "법령 수정 금지")
  + [c] factories에 has_tower_crane 등 컬럼 저장 + batch SELECT 추가
      = DDL/스크립트 (Claude 가능)

현재 [a][b] 둘 다 없음 → has_tower_crane 거름망 도달 NO.
  [c]만 Claude가 해도 [a][b] 없으면 평가 안 됨.
```

---

## STEP-4: 대표 건설 입력 1건 재실행 — 현재 상태

```
건설 대표입력 (타워크레인=Y, 밀폐=Y, 공사금액58억, F41, 근로자45):

  입력 → 저장             YES
  저장 → FacilityProfile  YES (has_tower_crane PRESENT/True)
  FacilityProfile → 거름망:
    construction_amount → monetary_value  YES (기존 통로)
    has_tower_crane → (통로 없음)          NO
    has_confined_space → (통로 없음)       NO
    기타 건설 고유 입력 → (통로 없음)       NO

→ 현재 상태에서 건설 고유 입력의 거름망 도달은 여전히 NO.
  construction_amount만 기존 monetary_value 통로로 도달.
```

---

## 정직한 결론: 이 WO는 진입점 식별까지 (구현은 역할 분리)

```
STEP-1 (진입점 식별) = Claude 수행 완료.
  건설 입력 15종의 거름망 진입 방식(IF_SCOPE/IF_NUMERIC)과
  제안 binding_field를 매핑표로 확정.

STEP-2~3 (실제 전달 연결) = 엔진 영역, 이 WO 금지와 충돌:
  - FIELD_MAP에 건설 binding_field 추가 = 엔진 입력계약 변경
    → 이 WO "엔진 수정 금지" + 역할상 GPT 전담.
  - 매칭될 draft_slot의 건설 binding_field 생성 = 법령 컴파일
    → 이 WO "법령 수정 금지" + GPT 전담.

  Claude가 단독으로 할 수 있는 부분:
    [c] factories에 건설 컬럼 추가(DDL) + batch SELECT 확장.
    단 [a]FIELD_MAP·[b]draft_slot이 GPT에 의해 먼저 정의돼야
        [c]가 의미를 가짐(없으면 저장해도 평가 안 됨).
```

---

## 성공 기준 점검

```
CC-01 건설 입력별 진입점 식별        → ✅ (STEP-1 매핑표)
CC-02 FacilityProfile→거름망 연결    → 미완 (FIELD_MAP/draft_slot=GPT 선행 필요)
CC-03 대표 건설 입력 1건 도달 확인   → construction_amount만 YES, 건설고유 NO
CC-04 법령 수정 0건                  → ✅
CC-05 Compiler Core 수정 0건         → ✅
```

---

## GPT 인계 사항 (연결 완성을 위한 선행 작업)

```
[GPT-1] 건설 법조문 컴파일 → draft_slot에 건설 binding_field 조건 생성
  - IF_SCOPE 슬롯: construction_hazard(밀폐/석면/발파),
    construction_work(굴착/비계/거푸집/해체/잠수),
    construction_equipment(타워크레인), construction_type, construction_process
  - IF_NUMERIC 슬롯: subcontractor_count, construction_work_worker_count

[GPT-2] FIELD_MAP에 건설 binding_field → factories 컬럼 매핑 정의
  (Claude가 STEP-1에서 제안한 매핑표 참조)

[Claude-3] GPT-1/2 확정 후:
  factories에 건설 컬럼 추가(DDL) + run_facility_applicability batch SELECT 확장.
  → 그 후 대표 건설 입력 재실행 시 거름망 도달 YES 검증.
```

---

## 완료 문장

```
건설 입력의 거름망 진입점을 식별하였다(STEP-1 매핑표).
건설 입력 15종의 진입 방식(IF_SCOPE/IF_NUMERIC)과 제안 binding_field를 확정.
실제 전달 연결(FIELD_MAP·draft_slot)은 엔진/법령 영역으로
이 WO의 금지(엔진·법령 수정)와 역할 분리(GPT 전담)에 따라
진입점 식별까지 수행하고 GPT 선행 작업으로 인계한다.
construction_amount는 기존 monetary_value 통로로 이미 거름망 도달(YES).
```
