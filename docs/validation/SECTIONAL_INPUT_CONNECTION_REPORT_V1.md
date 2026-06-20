# SECTIONAL INPUT CONNECTION REPORT V1
# WO-SECTIONAL-INPUT-CONNECTION-001

**작성일**: 2026-06-20
**목적**: 섹션별(공통/산업/건설/건물) 입력을 Compiler Core까지 연결.
**결과**: ★ 구현 진입 전 차단 사실 발견 — 연결의 최종층(draft_slot)이 비어 있음.
**금지 준수**: 신규 법령조건 생성 안 함 / 법령해석 안 함 / 의무문구 안 함 / VR 수정 안 함 / 엔진(FIELD_MAP·평가) 임의 수정 안 함.

---

## 진입 전 실측: 연결의 4층 구조

```
실제 유료진단 입력 경로(직전 WO 확인)를 층으로 나누면:

[1층] 저장        factories 컬럼
[2층] 조회        batch SELECT (run_facility_applicability.py)
[3층] 평가매핑    FIELD_MAP (facility_applicability_eval.py)
[4층] 평가조건    draft_slot.binding_field (법령 컴파일 산출물)

평가는 [3층 FIELD_MAP]과 [4층 draft_slot]을 binding_field로 매칭한다.
  → draft_slot의 binding_field == FIELD_MAP의 키 일 때만 평가 발생.
```

---

## ★ 차단 사실: draft_slot에 건설 binding_field가 0건

```
draft_slot에 실제 존재하는 binding_field (전수):
  distance_value 415, equipment_type 260, facility_type 220,
  voltage_level 142, concentration_level 110, process_type 33,
  storage_capacity 23, power_capacity 15, area_size 12,
  monetary_value 6, employee_count 3

건설 전용 binding_field (construction_process / construction_work /
  tower_crane / excavation / scaffold / formwork / asbestos /
  blasting / diving):
  → draft_slot에 0건.
```

---

## 이것이 연결 작업에 의미하는 바 (사실, 판정 아님)

```
연결을 1~3층만 해도(저장 컬럼 추가 + batch SELECT 추가 + FIELD_MAP 추가),
  매칭될 draft_slot(4층)이 0건이라 candidate가 생성되지 않는다.

예:
  FIELD_MAP에 "construction_work → has_excavation_work" 추가해도
  → draft_slot에 binding_field='construction_work'인 행이 0건
  → 매칭 0 → facility_applicability 0 → task_candidate 0.

= 건설 입력 연결은 1~3층 작업만으로 완성되지 않는다.
  4층(법령 조건에 건설 binding_field가 존재)이 선행되어야 한다.
```

---

## 4층은 누가 만드는가 (역할 경계)

```
draft_slot의 binding_field = 법령엔진이 법조문을 컴파일해
  executable_draft / draft_slot으로 만든 산출물.

  = "어떤 법조문이 건설 작업(굴착/비계/타워크레인)을 조건으로 갖는가"를
    법령엔진이 해석·컴파일해야 생긴다.

  이것은 법령 해석 + 엔진 컴파일 영역 = GPT 전담.
  Claude는 신규 법령조건 생성·법령해석·의무문구 작성 금지(이 WO 명시).
  → 4층은 Claude가 만들 수 없다.
```

---

## 섹션별 연결 가능성 표 (각 층별)

| 섹션 | 1층 저장 | 2층 batch | 3층 FIELD_MAP | 4층 draft_slot | 종합 |
|---|---|---|---|---|---|
| 공통(ksic/emp/site_type) | 연결됨 | 연결됨 | 연결됨 | 존재(process_type/employee_count/facility_type) | 도달 가능 |
| 산업-전기/면적/가스 | 연결됨 | 연결됨 | 연결됨 | 존재(power/area/storage) | 도달 가능 |
| 산업-공정/설비/화학 | 일부 | 일부(equipment 조인) | equipment_type만 | equipment_type 260건 | 부분 |
| 건설-공정/작업/장비 | 컬럼 대부분 부재 | 미포함 | 미포함 | **0건** | 미도달 |
| 건물-연면적/승강기/에너지 | 일부(building_area 등) | 일부 | area_size만 | area_size 12건 | 부분 |

```
※ 건설 섹션은 4층(draft_slot)이 0건이라
  1~3층을 채워도 도달 불가. 4층 선행 필수.
```

---

## 검증 샘플 적용 (요청 3종, 도달 여부)

```
산업: C28 + 설비 + 화학물질
  - ksic(process_type) 4층 존재 → 도달 가능
  - 설비(equipment_type) 4층 존재 → 도달 가능
  - 화학물질(has_chemical_material): FIELD_MAP/draft_slot 없음 → 미도달

건설: F41 + 건설작업 + 타워크레인
  - ksic(process_type) → 도달 가능
  - 건설작업/타워크레인: draft_slot 0건 → 미도달

건물: J58 + 연면적 + 승강기
  - ksic(process_type) → 도달 가능
  - 연면적(area_size) 4층 존재 → 도달 가능
  - 승강기(elevator): FIELD_MAP/draft_slot 없음 → 미도달
```

---

## 성공 기준 점검 (정직)

```
SI-01 섹션별 입력 저장계층 연결 → 부분 (건설 7개 컬럼 부재)
SI-02 batch SELECT 포함        → 미수행 (4층 선행 필요로 보류)
SI-03 FIELD_MAP 포함           → 미수행 (GPT 영역 + 4층 선행 필요)
SI-04 Compiler Core 평가 전달  → 미수행 (4층 0건이라 무의미)
SI-05 산업/건설/건물 안 섞임   → (구현 미진입)
SI-06 신규 법령조건 0건        → ✅ (만들지 않음)

→ 이 WO는 구현 진입 전, 4층(draft_slot) 부재로 차단됨.
  1~3층만 구현하면 결과가 안 나오므로(추정 구현 금지 원칙),
  구현하지 않고 차단 사실을 보고함.
```

---

## 완료 문장 (조건부)

```
공통/산업/건물 섹션 일부는 Compiler Core 입력 경로에 이미 연결되어 있으나,
건설 섹션은 평가 조건(draft_slot.binding_field)이 0건이라
입력을 연결해도 도달하지 못함을 확인하였다.
건설 섹션 연결은 4층(법령 조건의 건설 binding_field) 선행이 필수이며,
이는 법령엔진 컴파일(GPT 전담) 영역이다.
```

---

## 역할 분리에 따른 다음 단계 (제안, 판정 아님)

```
[GPT 영역 — 선행 필수]
  건설 법조문(굴착/비계/타워크레인/석면 등)을 컴파일해
  draft_slot에 건설 binding_field를 가진 조건을 생성.
  + FIELD_MAP에 건설 binding_field → factories 컬럼 매핑 정의.
  (엔진 입력계약 변경 = GPT 결정)

[Claude 영역 — GPT 선행 후 가능]
  1층: factories에 누락 건설 컬럼 추가 (DDL, Supabase MCP).
  2층: batch SELECT에 건설 컬럼 추가 (스크립트).
  단 GPT가 정의한 binding_field ↔ 컬럼 매핑에 맞춰서만.

= 이 WO는 GPT 선행 작업 없이는 완수 불가.
  Claude 단독 구현 시 4층 0건이라 결과 없음 + 엔진영역 침범.
  따라서 구현 보류하고 차단 사실 + 역할 분리 보고로 마감.
```
