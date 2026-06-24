# WO-EXISTS-INPUT-TRACE-001
# EXISTS 입력(has_*) 저장 위치 추적

**작성일:** 2026-06-24 | **상태:** 완료 (읽기 전용 추적)
**선행:** WO-INPUT-BINDING-IMPLEMENTATION-001
**금지 (전부 준수):** 새 매핑/Trigger/Harvest/Review/엔진작업 없음. 저장 위치 추적만.
**목적:** has_welding/has_crane 등 EXISTS 입력이 실제 어디 저장되는지 끝낸다.

> 0건은 엔진 문제가 아니라 "입력 신호가 generator까지 도달했는가"의 문제.

---

## 최종 판정: CASE-B + 부분 CASE-C 혼합

```
has_*는 저장된다. 단, generator가 읽는 곳이 아니다.

저장 위치: public_diagnosis_requests.facility_data (jsonb)
  예: {"has_elevator": true, "worker_count": 50, ...}

generator가 읽는 곳: facility_profiles.profile_snapshot
  → 여기엔 has_* 없음 (SCOPE+THRESHOLD만)

→ 신호는 존재하나 다른 저장소에 있다 (CASE-B: 저장소 분리).
→ 일부 필드명도 다름 (has_gas vs has_high_pressure_gas — CASE-B 변환).
→ 주 진단 경로(anonymous 171건)엔 has_* 아예 없음 (CASE-C 부분).
```

---

## TASK-001: EXISTS 후보 목록 (diagnosis_input_fields)

```
diagnosis_input_fields: 총 128 필드, boolean 59개.

boolean(EXISTS) field_group:
  공정: has_welding, has_excavation, has_demolition, has_pile_work,
        has_casting, has_painting, has_plating, has_high_place_work,
        has_concrete_work, has_steel_frame, has_heat_treatment
  설비: has_crane, has_forklift, has_conveyor, has_press, has_grinding,
        has_injection, has_pressure_vessel, has_rolling, has_elevator
  석면: has_asbestos
  다중이용: is_multi_use
  기본정보: has_safety_manager, has_subcontractor

auto_source: 전부 NULL → 사용자 직접 입력 필드.
→ 입력표준(정의)은 확실히 존재. 59개 boolean.
```

---

## TASK-002~004: 저장 경로 추적 (실측)

### 진단 입력 저장 후보 테이블 데이터량

| 테이블 | 건수 | has_* 포함 |
|---|---|---|
| anonymous_diagnosis_results.input_data | 171 | **0** |
| factory_diagnosis_results.input_data | 4 | 0 |
| public_diagnosis_requests.facility_data | 14 | **4** ★ |
| diagnosis_session.input_snapshot | 1 | 0 |
| facility_profiles.profile_snapshot | (다수) | 0 |

### has_*가 실제 저장된 유일한 곳: public_diagnosis_requests

```json
// public_diagnosis_requests.facility_data (jsonb)
{
  "floor_count": 5,
  "building_use": "업무시설",
  "has_elevator": true,        ← has_* 값으로 저장됨
  "worker_count": 50,
  "total_floor_area": 3000,
  "electric_capacity": 75
}

// 다른 건
{
  "has_gas": false,            ← generator는 has_high_pressure_gas
  "has_hazardous": false,      ← generator는 has_hazardous_material
  "floor_area": 500,
  "worker_count": 50
}
```

### 주 진단 경로(anonymous 171건)는 has_* 없음

```json
// anonymous_diagnosis_results.input_data — 가장 많은 경로
{
  "sector": "CONSTRUCTION",
  "tier_code": "CONSTRUCTION_FREE",
  "factory_id": "...",
  "floor_area": 8000,
  "worker_count": 50,
  "company_name": "..."
}
// → has_* 전혀 없음. sector+floor_area+worker_count만.
```

---

## TASK-005: 최종 판정

```
CASE-A (실제 저장됨, 같은 이름):
  부분 해당. has_elevator는 public_diagnosis_requests에 정확히 저장.

CASE-B (저장되나 다른 저장소/이름):
  ★ 주 해당.
  - 저장소: public_diagnosis_requests (generator는 facility_profiles 읽음)
  - 이름변환: has_gas→has_high_pressure_gas, has_hazardous→has_hazardous_material

CASE-C (UI 존재하나 저장 안 됨):
  부분 해당. 주 진단 경로(anonymous 171)는 has_* 미저장.

CASE-D (UI 미사용):
  비해당. UI는 쓰임 (public_diagnosis_requests 4건이 증거).

종합 판정: CASE-B 주도 + CASE-C 부분.
  → has_* 신호는 존재하나
    (1) generator가 읽는 facility_profiles엔 없고
    (2) public_diagnosis_requests에만 있으며
    (3) 주 경로(anonymous)는 아예 수집 안 함.
```

---

## 0건의 진짜 원인 (증명 완료)

```
0건 = 엔진 문제 아님. 저장소 단절 문제.

흐름 단절 지점:
  진단 UI (has_elevator 등 입력)
    ↓
  public_diagnosis_requests.facility_data  ← has_* 여기 저장
    ↓
    ✗ 단절 (facility_profiles로 안 넘어감)
    ↓
  facility_profiles.profile_snapshot  ← has_* 없음
    ↓
  generator (facility_profiles 읽음)
    ↓
  obligation_instance 0건

→ has_* 신호가 generator까지 도달하지 못함.
→ 두 저장소(public_diagnosis_requests vs facility_profiles)가
  연결 안 됨.
```

---

## 핵심 발견

### 발견 1: has_*는 public_diagnosis_requests에 산다

```
generator가 보는 facility_profiles가 아니라
public_diagnosis_requests.facility_data(jsonb)에 저장.
→ 저장은 됨. 위치가 다름.
→ 98개(실제 59 boolean) 입력표준이 헛것이 아니었음.
→ 단 generator와 다른 테이블.
```

### 발견 2: 주 경로와 부 경로가 다른 데이터를 수집

```
anonymous_diagnosis_results (171건, 주 경로):
  sector+floor_area+worker_count만. has_* 없음.
public_diagnosis_requests (14건, 부 경로):
  facility_data에 has_* 포함.

→ 두 진단 경로가 입력 깊이가 다름.
→ 주 경로(무료/익명)는 간이 입력.
→ 부 경로(공개 요청)는 상세 입력(has_* 포함).
```

### 발견 3: 필드명도 일부 변환 필요

```
public_diagnosis_requests: has_gas, has_hazardous
generator(cmc):            has_high_pressure_gas, has_hazardous_material

→ CASE-B 이름 변환 존재.
→ 바인딩 시 동의어 매핑 필요:
   has_gas → has_high_pressure_gas
   has_hazardous → has_hazardous_material
```

### 발견 4: 숫자(THRESHOLD)는 양쪽 다 있다

```
public_diagnosis_requests: worker_count, total_floor_area, electric_capacity
facility_profiles: total_workers_value, floor_area_value, electrical_kw_value
anonymous: worker_count, floor_area

→ THRESHOLD 재료는 모든 경로에 존재.
→ has_*(EXISTS)만 facility_profiles에서 누락.
```

---

## 성공 기준 답변

```
has_welding=true가 최종적으로 어떤 테이블 어떤 컬럼에
저장되는지 1개 경로로 설명 가능한가?

✅ 가능.

경로:
  진단 UI (상세 입력)
    → public_diagnosis_requests.facility_data (jsonb)
       {"has_welding": true}  형태로 저장

단, 이 경로는:
  - generator가 읽는 facility_profiles와 분리됨
  - 주 진단 경로(anonymous)에서는 수집 안 됨
  - 일부 필드명 변환 필요 (has_gas 등)
```

---

## 다음 단계 (실측 기반)

```
이제 0건 원인이 증명됨: 저장소 단절.

선택지 1: public_diagnosis_requests → generator 직접 연결
  - facility_profiles 대신 public_diagnosis_requests.facility_data 읽기
  - has_* 신호가 즉시 generator 도달
  - 단 4건만 존재 (데이터 적음)

선택지 2: 입력 파이프 통합
  - 진단 UI가 has_*를 facility_profiles에도 쓰게
  - 두 저장소 정합 (코드 수정 필요 — GPT/Cursor 영역 가능)

선택지 3: generator 입력 소스를 다중화
  - facility_profiles(THRESHOLD/SCOPE)
    + public_diagnosis_requests(EXISTS) 둘 다 읽기
  - Binding Layer에서 병합

권고: 선택지 1로 즉시 검증 (public_diagnosis_requests 4건으로
      has_* generator 도달 실증) → 그 후 파이프 통합 결정.
```

---

*WO-EXISTS-INPUT-TRACE-001 완료. 읽기 전용 추적.*
*판정: CASE-B 주도 — has_*는 public_diagnosis_requests.facility_data에 저장.*
*generator가 읽는 facility_profiles와 분리됨 = 0건의 진짜 원인.*
*주 경로(anonymous 171)는 has_* 미수집. 필드명 일부 변환 필요.*
