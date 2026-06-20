# FACILITYPROFILE EXPANSION REPORT V1
# WO-FACILITYPROFILE-EXPANSION-001 (보강 포함)

**작성일**: 2026-06-20
**수정 파일**: services/facility_profile_service.py (commit 09d13b4)
**목적**: 사용자 입력 계약 전체를 FacilityProfile 계약으로 정합. 수집→전달만.

---

## 변경 요약

```
profile_version: 1 → 2
입력 차원: 11개 → 57개 (기존 11 유지 + 신규 46)
기존 11차원: 100% 유지 (regular/subcontract/total_workers, use_code,
            floor_area, floor_count, construction_amount, electrical_kw,
            gas_capacity, sector, ksic_code)
신규 그룹: 7개 (아래)
```

---

## 추가 필드 목록 + 매핑 소스 (누락 0건)

### facility_physical (시설 물리속성, 5)
| 필드 | 매핑 소스 (row.get) |
|---|---|
| boiler_capacity | boiler_capacity |
| elevator_count | elevator_count |
| annual_energy_toe | annual_energy_toe |
| building_grade | building_grade |
| transformer_kva | transformer_kva |

### facility_hazard (시설 위험속성, 6)
| 필드 | 매핑 소스 |
|---|---|
| has_hazardous_material | has_hazardous_material |
| has_chemical_material | has_chemical_material |
| has_high_pressure_gas | has_high_pressure_gas |
| has_safety_manager | has_safety_manager |
| is_factory_registered | is_factory_registered |
| is_public_facility | is_public_facility |

### construction (건설 속성, 7)
| 필드 | 매핑 소스 |
|---|---|
| construction_type | construction_type |
| subcontractor_company_count | subcontractor_company_count |
| has_tower_crane | has_tower_crane |
| has_confined_space | has_confined_space |
| has_asbestos | has_asbestos |
| has_blasting | has_blasting |
| has_diving_work | has_diving_work |

### process (일반 공정, 4)
| 필드 | 매핑 소스 |
|---|---|
| process_lv1~4 | process_lv1 / lv2 / lv3 / lv4 |

### equipment (설비, 6)
| 필드 | 매핑 소스 |
|---|---|
| equipment_count | equipment_count |
| equipment_names | equipment_names |
| equipment_install_years | equipment_install_years |
| equipment_locations | equipment_locations |
| equipment_legal_targets | equipment_legal_targets |
| equipment_operation_status | equipment_operation_status |

### construction_process (건설 공정, 3) — 일반 process와 분리
| 필드 | 매핑 소스 |
|---|---|
| construction_process_code | construction_process_code |
| construction_process_name | construction_process_name |
| construction_process_standard_version | construction_process_standard_version |

### construction_work (건설 작업, 15) — 일반 task와 분리
| 필드 | 매핑 소스 |
|---|---|
| construction_work_code | construction_work_code |
| construction_work_name | construction_work_name |
| construction_work_standard_version | construction_work_standard_version |
| construction_work_amount | construction_work_amount |
| construction_work_duration_days | construction_work_duration_days |
| construction_work_worker_count | construction_work_worker_count |
| has_excavation_work | has_excavation_work |
| has_high_place_work | has_high_place_work |
| has_lifting_work | has_lifting_work |
| has_demolition_work | has_demolition_work |
| has_scaffold_work | has_scaffold_work |
| has_formwork_work | has_formwork_work |
| has_welding_work | has_welding_work |
| has_electrical_work | has_electrical_work |
| has_hot_work | has_hot_work |

```
신규 필드 합계: 5+6+7+4+6+3+15 = 46개. 지시서 대조 누락 0건 (검증 완료).
```

---

## 검증 결과

```
SYNTAX OK (ast.parse 통과)
지시서 신규 46필드 → 코드 매핑 100% (누락 0)
기존 11차원 → 전부 유지 확인
동작 테스트 (샘플 row → build_facility_profile):
  - 입력값 PRESENT 확인 (boiler_capacity=10, has_tower_crane=True,
    process_lv1='토공사', construction_process_code='CP-001',
    construction_work_code='CW-100', has_excavation_work=True ...)
  - 미입력 → UNKNOWN/value None 확인 (elevator_count, has_diving_work)
  - 값 변환 금지 확인: False → value:False/state:PRESENT (0/UNKNOWN 변환 안 됨)
  - profile_to_db_row: profile_snapshot에 신규 필드 전체 보존 확인
분리 검증: process / construction_process / construction_work 별도 키 (혼합 안 됨)
```

---

## 성공 기준 점검

```
FP-01 사용자 입력 → FacilityProfile 매핑 100% → ✅ (46/46)
FP-02 기존 11개 필드 유지 → ✅
FP-03 신규 필드 dump에서 입력값 확인 가능 → ✅ (동작 테스트)
FP-04 판정 결과 변화 검증 안 함 → ✅ (범위 외)
FP-05 건설 공정 표준코드 포함 → ✅ (construction_process_*)
FP-06 건설 작업 표준코드 포함 → ✅ (construction_work_*)
FP-07 일반 공정/작업 vs 건설 공정/작업 분리 → ✅ (별도 그룹키)
```

---

## 금지 준수

```
평가조건 수정 안 함 ✅
V4 로직 수정 안 함 ✅
condition / threshold 수정 안 함 ✅
VR 수정 안 함 ✅
Check Engine / Projection 수정 안 함 ✅
factories 데이터 수정 안 함 ✅
값 변환 / 판정 로직 / 조건 추가 안 함 ✅ (수집→전달만)
```

---

## 구현 메모 (사실 표기)

```
1. 신규 필드는 build_facility_profile 반환 dict + profile_snapshot(JSON)에
   담긴다. facility_profiles 테이블의 평탄화 컬럼은 기존 11차원만 유지
   (DB 스키마 변경 회피). 신규 46필드는 profile_snapshot JSON에 전량 보존.
   → 평탄화 컬럼이 필요하면 별도 WO에서 DB 컬럼 추가.

2. 매핑 소스는 factories row의 동일 키명을 가정 (row.get("필드명")).
   해당 컬럼이 factories에 없으면 None → UNKNOWN으로 안전 처리됨
   (에러 없음, 값 변환 없음).
   → 실제 factories에 어떤 컬럼이 존재하는지는 이 WO 범위 밖
     (FP-03은 "입력값이 있으면 담긴다"를 검증; 실 컬럼 존재 여부는 별도).

3. profile_version 1→2로 올림. 기존 v1 소비자는 기존 키 그대로 접근 가능
   (하위호환 — 신규 키는 추가만 됨).
```

---

## 결론

```
FacilityProfile을 사용자 입력 계약 전체(57차원)로 확장 완료.
  기존 11차원 유지 + 신규 46필드(7그룹) 추가.
  건설 공정/작업을 일반 process/task와 분리.
  수집→전달만 (값 변환/판정/조건 추가 없음).

이번 WO는 입력 계약 정합까지. 
판정 결과 변화 / 평가조건 사용 여부는 별도 WO.
```
