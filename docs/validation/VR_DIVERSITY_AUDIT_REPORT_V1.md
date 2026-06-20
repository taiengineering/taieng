# VR DIVERSITY AUDIT REPORT V1
# WO-VR-DIVERSITY-AUDIT-001

**작성일**: 2026-06-20
**목적**: VR 생성기 입력 다양성 측정만. 엔진 실행/결과 분석 없음.
**대상**: vr_generation_spec.py / build_virtual_facility_profile()
**샘플**: 1,000개 (제조400/건설400/사무200, ksic 변주)

---

## 측정 방법

```
1,000개 생성 → 57개 입력 필드별 distinct value 집계.
등급:
  D0 = distinct 1     (고정값)
  D1 = distinct 2~5   (낮은 다양성)
  D2 = distinct 6~20  (중간 다양성)
  D3 = distinct >20   (높은 다양성)
```

---

## 필드별 다양성 표 (전수)

| 필드 | distinct | 등급 |
|---|---|---|
| sector | 2 | D1 |
| ksic_code | 14 | D2 |
| employee_count | 3 | D1 |
| subcontractor_worker_count | 3 | D1 |
| total_worker_count_calc | 3 | D1 |
| building_use_code | 3 | D1 |
| building_area | 3 | D1 |
| floor_count | 3 | D1 |
| building_grade | 2 | D1 |
| electrical_capacity_kw | 3 | D1 |
| gas_capacity_m3 | 2 | D1 |
| gas_capacity_kg | 1 | D0 |
| annual_energy_toe | 3 | D1 |
| transformer_kva | 2 | D1 |
| boiler_capacity | 2 | D1 |
| elevator_count | 3 | D1 |
| has_hazardous_material | 3 | D1 |
| has_chemical_material | 3 | D1 |
| has_high_pressure_gas | 2 | D1 |
| has_safety_manager | 2 | D1 |
| is_factory_registered | 2 | D1 |
| is_public_facility | 1 | D0 |
| construction_amount | 2 | D1 |
| construction_type | 2 | D1 |
| subcontractor_company_count | 2 | D1 |
| has_tower_crane | 2 | D1 |
| has_confined_space | 2 | D1 |
| has_asbestos | 2 | D1 |
| has_blasting | 2 | D1 |
| has_diving_work | 2 | D1 |
| process_lv1 | 2 | D1 |
| process_lv2 | 2 | D1 |
| process_lv3 | 2 | D1 |
| process_lv4 | 1 | D0 |
| equipment_count | 3 | D1 |
| equipment_names | 3 | D1 |
| equipment_install_years | 3 | D1 |
| equipment_locations | 3 | D1 |
| equipment_legal_targets | 3 | D1 |
| equipment_operation_status | 3 | D1 |
| construction_process_code | 2 | D1 |
| construction_process_name | 2 | D1 |
| construction_process_standard_version | 2 | D1 |
| construction_work_code | 2 | D1 |
| construction_work_name | 2 | D1 |
| construction_work_standard_version | 2 | D1 |
| construction_work_amount | 2 | D1 |
| construction_work_duration_days | 2 | D1 |
| construction_work_worker_count | 2 | D1 |
| has_excavation_work | 2 | D1 |
| has_high_place_work | 2 | D1 |
| has_lifting_work | 2 | D1 |
| has_demolition_work | 2 | D1 |
| has_scaffold_work | 2 | D1 |
| has_formwork_work | 2 | D1 |
| has_welding_work | 2 | D1 |
| has_electrical_work | 2 | D1 |
| has_hot_work | 2 | D1 |

```
※ 행 수 58 = 입력 원본 키 기준 (gas_capacity가 m3/kg 두 키로 분리,
  FacilityProfile에선 gas_capacity 1차원으로 병합). 측정은 원본 키 전수.
```

---

## 등급 분포

```
D0 (고정값, distinct 1):       3개
   gas_capacity_kg, is_public_facility, process_lv4
D1 (낮은 다양성, distinct 2~5): 54개
D2 (중간 다양성, distinct 6~20): 1개
   ksic_code (14)
D3 (높은 다양성, distinct >20):  0개
```

---

## 측정값 핵심 (수치 사실)

```
- D3(높은 다양성) = 0개. 다양성 높은 필드가 하나도 없다.
- ksic_code(D2, 14) 외 모든 필드가 distinct ≤ 5.
- 수치 필드(employee_count/electrical_kw/construction_amount 등)
  대부분 distinct 2~3 (None 포함).
  예: employee_count = {280, 150, 30} (프로파일당 1값)
      electrical_capacity_kw = {None, 50, 1500}
      construction_amount = {None, 50000000000}
- boolean 필드 = distinct 2 (값 1개 + None) 또는 3.
- 배열 필드(equipment_*) = distinct 3 (프로파일당 고정 배열 + None).

→ 각 필드가 "프로파일 3종의 고정값 + None"만 가진다.
  ksic_code만 라벨이 14종으로 다양.
```

---

## 성공 기준 점검

```
DA-01 1,000개 생성 완료      → ✅
DA-02 57개 필드 전수 조사     → ✅ (원본 키 58행 전수)
DA-03 필드별 distinct 집계    → ✅
DA-04 엔진 실행 0건           → ✅
DA-05 판정 결과 분석 0건      → ✅
```

---

## 금지 준수

```
법령 분석 안 함 ✅
결과 분석 안 함 ✅
버그 판정 안 함 ✅
엔진 개선안 안 함 ✅
FacilityProfile 수정 안 함 ✅
입력 다양성 측정만 ✅
```

---

## 완료 문장

```
VR 생성기의 입력 다양성을 측정하였다.
엔진 판정 및 결과 분석은 수행하지 않았다.
```

---

## 처음으로 답할 수 있는 질문 (측정 사실)

```
"57차원 VR인가? 아니면 57차원 템플릿 3종인가?"

측정 답:
  현재는 "57차원 템플릿 3종"이다.
  - 57개 필드 전부 존재하나(차원은 57),
    각 필드의 값은 프로파일 3종의 고정값(+None)뿐.
  - D3(높은 다양성) 0개, ksic_code(14)만 D2.
  - 나머지 56개 필드가 distinct ≤ 5 (대부분 2~3).

= 차원은 57이지만, 조합 다양성은 사실상 3(프로파일 수).
  ksic 라벨만 14종으로 갈릴 뿐 속성 조합은 3종.

※ 이것은 측정값이다. "고쳐야 한다/생성기를 바꿔야 한다"는
  판단·제안이 아니다 (금지 준수). 다음 방향은 별도 결정.
```
