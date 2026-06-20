# INPUT PATH TRACE V1
# WO-INPUT-PATH-TRACE-001

**작성일**: 2026-06-20
**목적**: 실제 사용자 입력 경로와 VR 생성 경로가 동일한지 확인. (가설 검증)
**금지 준수**: 판정/원인분석/수정 없음. 경로 비교표만.

---

## 가설 (검증 대상)

```
실제 사용자 입력:
  산업 → 산업 입력부 / 건설 → 건설 입력부 / 건물 → 건물 입력부 (서로 다른 경로?)
VR:
  57개 필드를 한 객체에 생성
→ 실제 흐름과 다르면 건설 의무 미출력
```

---

## 경로 추적 1: FacilityProfile 생성 경로 (코드 실측)

```
routers/facility_profile_api.py:
  POST /facility-profiles/{factory_id}
    → factories 테이블에서 row 1건 로드 (select * where id)
    → build_facility_profile(row)  ← sector 분기 없음. 단일 함수.
    → facility_profiles 저장.

= FacilityProfile 생성은 산업/건설/건물 구분 없이 단일 경로.
  factories 한 row → build_facility_profile 하나.
```

## 경로 추적 2: 실제 factories 저장 구조 (DB 실측)

```
factories 테이블 sector 분포:
  BUILDING        278건
  INDUSTRIAL      225건
  CONSTRUCTION    195건
  SPECIAL_FACILITY  1건

= 산업/건설/건물이 전부 동일한 factories 테이블, 동일 컬럼 사용.
  sector 컬럼으로만 구분. 별도 입력부 테이블 없음.
  (모든 sector가 ksic/emp/construction_amount/electrical 같은 컬럼 공유)
```

---

## 경로 비교표: 항목별 산업/건설/건물

| 항목 | 산업 | 건설 | 건물 |
|---|---|---|---|
| 저장 테이블 | factories | factories | factories |
| 구분 방식 | sector=INDUSTRIAL | sector=CONSTRUCTION | sector=BUILDING |
| FacilityProfile 생성 | build_facility_profile | build_facility_profile | build_facility_profile |
| 경로 분기 | 없음(단일) | 없음(단일) | 없음(단일) |
| ksic 보유 | 138/225 | 102/195 | 102/278 |
| employee_count 보유 | 224/225 | 195/195 | 278/278 |
| construction_amount 보유 | 90/225 | 93/195 | 164/278 |
| electrical 보유 | 215/225 | 184/195 | 273/278 |

```
→ 산업/건설/건물 입력 경로는 서로 다르지 않다.
  전부 factories 단일 테이블 → build_facility_profile 단일 경로.
  sector 라벨만 다르고 경로/컬럼은 공통.
```

---

## INPUT_PRESENT vs FACILITYPROFILE_PRESENT (필드 존재 추적)

```
VR이 생성하는 건설 필드가 실제 factories 테이블에 컬럼으로 존재하는가?

[factories에 컬럼 존재 — 17개]
  construction_type, subcontractor_worker_count, total_worker_count_calc,
  has_tower_crane, has_confined_space, has_blasting,
  has_high_pressure_gas, has_safety_manager, is_factory_registered,
  building_use_code, building_area, building_grade, floor_count,
  gas_capacity_m3, gas_capacity_kg, elevator_count, annual_energy_toe

[factories에 컬럼 부재 — VR은 만드나 실제 테이블엔 없음]
  construction_process_code / name / standard_version
  construction_work_code / name / standard_version
  construction_work_amount / duration_days / worker_count
  has_excavation_work / high_place / lifting / demolition / scaffold /
    formwork / welding / electrical / hot_work
  has_asbestos / has_diving_work
  subcontractor_company_count
  process_lv1~4
  equipment_count / equipment_names
  is_public_facility
  has_hazardous_material / has_chemical_material
```

---

## 비교표: VR 생성 vs factories 컬럼 vs FacilityProfile

| 건설 입력 항목 | VR 생성 | factories 컬럼 | FacilityProfile 수용 |
|---|---|---|---|
| construction_type | O | O | O |
| has_tower_crane | O | O | O |
| has_confined_space | O | O | O |
| has_blasting | O | O | O |
| has_asbestos | O | **부재** | O(키만, 값 None) |
| has_diving_work | O | **부재** | O(키만, 값 None) |
| construction_process_code | O | **부재** | O(키만, 값 None) |
| construction_work_code | O | **부재** | O(키만, 값 None) |
| has_excavation_work | O | **부재** | O(키만, 값 None) |
| (굴착/고소/양중/해체/비계/거푸집/용접/전기/화기) | O | **부재** | O(키만, 값 None) |
| subcontractor_company_count | O | **부재** | O(키만, 값 None) |

```
※ VR은 이 필드들을 값으로 만든다(타워크레인=True 등).
  그러나 실제 factories 테이블엔 해당 컬럼이 없다.
  build_facility_profile은 row.get("컬럼")으로 읽으므로,
  실제 사업장에선 그 컬럼이 없어 None(UNKNOWN)이 된다.
  = VR 가상사업장은 값이 있고, 실제 사업장은 컬럼 자체가 없다.
```

---

## 성공 기준 점검

```
실제 입력 경로 3종 비교표 작성 → ✅ (산업/건설/건물)
판정/원인분석/수정 안 함 → ✅
```

---

## 완료 문장

```
실제 사용자 입력 경로와 FacilityProfile 생성 경로를 정리하였다.
```

---

## IF/THEN 판정

```
규칙:
  IF 산업/건설/건물 입력 경로가 서로 다르다
     THEN WO-VR-PATH-ALIGNMENT-001 (VR을 실제 경로 구조로 재작성)
  ELSE WO-ROOT-CAUSE-002 (건설 의무 미출력 원인 분석)

추적 결과:
  산업/건설/건물 입력 경로 = 서로 다르지 않다.
    전부 factories 단일 테이블 → build_facility_profile 단일 경로.
    sector 라벨로만 구분.

  → IF 조건 FALSE (경로가 다르지 않음) → ELSE 분기

  ∴ 다음 WO = WO-ROOT-CAUSE-002
    (건설 의무 미출력 원인 분석)

  단 추적 중 별도 사실 1건 관찰됨 (판정 아님, 사실 기록):
    VR이 만드는 건설 세부 필드(건설공정/작업/굴착 등)의 다수가
    실제 factories 테이블에 컬럼으로 존재하지 않는다.
    = 가설("경로가 다르다")은 FALSE이지만,
      "VR 필드와 실제 컬럼의 존재 범위가 다르다"는 별개 사실이 보임.
    이 사실은 WO-ROOT-CAUSE-002의 입력으로 넘긴다.
```
