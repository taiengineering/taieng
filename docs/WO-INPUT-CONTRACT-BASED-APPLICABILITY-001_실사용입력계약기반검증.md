# WO-INPUT-CONTRACT-BASED-APPLICABILITY-001 — 실사용 입력계약 기반 Applicability 검증

**작성일:** 2026-06-28 | **성격:** 읽기 전용 분석(코드 수정·DB 수정 0).
**핵심 판정:** mock factories 결측률은 **허상 기준**. 실서비스 Source of Truth = **입력계약(`diagnosis_input_fields`)**. 핵심 입력은 폼에서 대부분 확보 가능.

---

## TASK-001 — 실사용 입력 Contract (권위 소스: diagnosis_input_fields, 100필드)
```
BUILDING(FREE):   address, total_floor_area*, floor_count*, building_use_type*, worker_count*
BUILDING(PAID):   + has_safety_manager, electric_capacity*, has_gas, has_chemical, has_hazmat_storage,
                    has_sprinkler/fire_hydrant/smoke_control, is_multi_use, is_energy_intensive, main_structure …
INDUSTRIAL(FREE): ksic_major*, worker_count*, total_floor_area
INDUSTRIAL(PAID1):+ electric_capacity*, has_boiler, has_chemical_substance, has_high_pressure_gas, has_safety_manager
INDUSTRIAL(PAID2):+ process_list(공정·위험요인), INDUSTRIAL(PAID3): 설비 has_crane/press/forklift… (다수 is_active=false)
CONSTRUCTION(FREE): project_amount*, worker_count*, project_address*  (PAID: construction_type*, subcontractor_count, process_list, has_excavation…)
(* = 필수. 다수 has_*·설비 필드는 정의되어 있으나 is_active=false=현재 폼 미노출)
auto_source=building_register: total_floor_area/floor_count/building_use_type/built_year/main_structure (건축물대장 자동입력)
```

## TASK-002 — 입력값 ↔ Applicability 필드 매핑 (A/B/C)
Applicability FIELD_MAP(11) 대조:
```
binding_field      엔진 factories col        입력계약 대응                    분류
employee_count  →  employee_count         ←  worker_count(FREE 전섹터 필수)    A 직접
area_size       →  building_area          ←  total_floor_area(FREE, 건축물대장) A 직접
process_type    →  ksic_code              ←  ksic_major(INDUSTRIAL FREE 필수)   A 직접
monetary_value  →  construction_amount    ←  project_amount(CONSTRUCTION FREE)  A 직접
power_capacity  →  electrical_capacity_kw ←  electric_capacity(PAID 필수)       A 직접(PAID)
facility_type   →  site_type              ←  building_use_type/construction_type/sector(유추) B 보강
equipment_type  →  (컬럼 없음)             ←  has_crane/press/forklift…(폼 정의 有) B 입력가능·엔진미매핑
storage_capacity→  gas_capacity_m3        ←  has_gas/has_high_pressure_gas(유무만, 용량 X) B 부분
voltage_level   →  transformer_capacity_kva← (폼 없음. electric_capacity는 kW 수전용량≠kVA)  C 못받음
concentration_level→(컬럼 없음)            ←  has_chemical(유무만, 농도 X)        C 못받음
distance_value  →  (컬럼 없음)             ←  (이격거리 입력 없음)               C 못받음
```
**A(폼 직접): employee/area/ksic/construction_amount/electric = 5종(엔진 DIRECT·핵심 임계 전부 포함).**
**B(보강 가능): site_type, equipment has_*, gas 용량.  C(현재 불가): transformer_kVA, 농도, 이격거리 = 3종.**

## TASK-003 — 입력폼만으로 가능한 의무 범위
```
UNIVERSAL   가능 ✓  — sector 항상 수집(전 섹터 필수). 입력 의존 없음.
THRESHOLD   가능 ✓  — worker_count·total_floor_area·project_amount(FREE) + electric_capacity(PAID)
                      = 엔진 DIRECT 임계 입력 전부 폼에서 받음.
BUILDING    가능 ✓  — building_use_type·연면적·층수(건축물대장 auto) 수집.
EXISTS      부분 △  — has_*(크레인/화학/보일러/굴착 등) 폼에 정의되나, ① 다수 is_active=false,
                      ② 엔진 FIELD_MAP에 equipment_type→컬럼 없음 → 현재 엔진이 has_*를 의무로 미연결.
                      (입력은 받을 수 있음 = 입력 문제 아니라 엔진 매핑 문제)
APPENDIX    조건부  — 별표 임계(면적·인원·금액) 기반은 THRESHOLD와 동일하게 가능.
```

## TASK-004 — 입력 시 즉시 생성 가능한 의무 (입력계약 기준)
```
최소 입력(FREE): sector + worker_count + (area/ksic/project_amount)
  → UNIVERSAL 전량 + worker/area/금액 THRESHOLD. (엔진 평가가능 binding: employee 37 parts + area 7 + monetary 6 + ksic 16)
표준 입력(+PAID 기본): + electric_capacity + building_use + has_safety_manager 등
  → + power THRESHOLD(10 parts) + 건물용도 기반.
상세 입력(+PAID2/3 활성화 시): + process_list + 설비 has_*
  → EXISTS 다수 가능해지나 "엔진 FIELD_MAP에 has_* 매핑 추가" 선행 필요(현재 미연결).
※ 수치는 binding_field별 조항 수(WO-APPLICABILITY-INPUT-SOURCE-001). 입력계약은 A필드를 모두 공급하므로
  mock 결측으로 보였던 MISSING은 실사용에서 해소됨.
```

## TASK-005 — MISSING_DATA 재정의 (사용자에게 못 묻고 외부 API로도 못 받는 값)
```
진짜 MISSING (구조적·입력 불가):
  · voltage_level → transformer_capacity_kva  (폼 미수집, kW≠kVA)
  · concentration_level (화학물질 농도)        (유무만 받음, 농도 측정값 없음)
  · distance_value (이격거리)                  (입력·외부소스 없음)
가짜 MISSING (mock 결측 허상 — 실사용에선 받음):
  · building_area/area_size       ← total_floor_area(폼·건축물대장)
  · electrical_capacity_kw        ← electric_capacity(폼)
  · site_type/ksic/construction_amount/employee ← 폼 직접
```

## TASK-006 — 입력 보강 우선순위 (실제로 추가로 해야 할 것)
```
1. (엔진측) has_* → EXISTS 매핑 추가  ← 입력은 이미 받음. 최대 레버. equipment_type 컬럼/매핑 부재 해소.
2. (입력측) PAID2/3 has_* is_active=true 활성화 (크레인/프레스/굴착 등 폼 노출)
3. (입력측) 전기 상세: transformer_kVA / 가스 용량(유무→용량)
4. (제외/후순위) 화학물질 농도·이격거리 = 전문 측정 영역 → 현 단계 제외 또는 외부 데이터
```

## TASK-007 — 기존 factories 검증 결과 정정
```
정정: factories 데이터 결측률(building_area 88%·electrical 87.5% 등)은 "mock 데이터 기준 진단"일 뿐,
      실서비스 가능성 판단 기준이 아니다.
실서비스 Source of Truth = 입력계약(diagnosis_input_fields). 사용자/건축물대장이 핵심값을 공급한다.
→ 이전 WO들의 "MISSING_DATA 78~96%"는 mock 공백 반영이며, 실사용 진단 불가를 의미하지 않는다.
```

## TASK-008 — 최종 판정
```
1. 입력 가능한 값만으로 Applicability는: UNIVERSAL ✓ + THRESHOLD ✓ + BUILDING ✓ 동작 가능.
   (핵심 임계 입력 worker/area/금액/전기·업종을 폼·건축물대장이 공급)
2. EXISTS(설비·작업 has_*)는 입력은 받을 수 있으나 현재 엔진 FIELD_MAP 미매핑 → 엔진측 보강 필요(입력 문제 아님).
3. 진짜 못 받는 값(transformer_kVA·농도·이격거리)은 소수 → 추가 질문 또는 외부 API, 아니면 현 단계 제외.
부족분 처리: 대부분 "사용자에게 묻는다"(이미 폼에 있음/활성화) + "엔진 매핑 추가". DB 결측 보강은 불필요.
```

## 결론 — 개발 우선순위 전환
```
[폐기] mock factories 결측 보강 (실고객 데이터 아님 → 무의미)
[전환] ① 엔진 FIELD_MAP에 has_*/EXISTS 매핑 추가(GPT·엔진)  ② 입력계약 완성(PAID has_* 활성화, 전기·가스 상세)
→ Applicability의 Source of Truth를 factories(mock)가 아니라 입력계약으로 전환해야 함.
```

## Boundary 준수
```
읽기 전용. 코드/DB/INSERT/UPDATE/DELETE 0. 엔진 미수정. mock 기준 평가 폐기, 입력계약 기준 분석만.
```

*WO-INPUT-CONTRACT-BASED-APPLICABILITY-001 — 입력계약이 핵심 Applicability 입력(worker/area/ksic/금액/전기)을 이미 공급. UNIVERSAL+THRESHOLD+BUILDING 동작 가능. EXISTS는 입력 OK·엔진 매핑 부재. 진짜 결손은 transformer/농도/이격거리 3종. mock 결측 기준 폐기.*
