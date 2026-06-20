# REAL INPUT CONNECTION TRACE V1
# WO-REAL-INPUT-CONNECTION-TRACE-001

**작성일**: 2026-06-20
**목적**: 실제 사용자 입력이 Compiler Core(facility_applicability → task_candidate)까지 도달하는 경로 추적.
**범위**: 실제 SaaS / 유료진단 경로만. VR 경로 제외.
**금지 준수**: 원인분석/버그판정/엔진·VR·FacilityProfile·조건 수정 없음. 도달 여부 표기만(YES/NO/UNKNOWN).

---

## 추적한 실제 경로 (코드 실측)

```
[배치] scripts/run_facility_applicability.py
  [1단계] SELECT id, employee_count, electrical_capacity_kw,
          transformer_capacity_kva, building_area, gas_capacity_m3,
          gas_capacity_kg, construction_amount, site_type, ksic_code, name
          FROM factories WHERE is_active=true
          → factories에서 11개 컬럼만 읽음.
  [2단계] executable_draft + draft_slot (IF_NUMERIC / IF_SCOPE) 로드
  [평가]  evaluate_draft_for_facility(fac, ...) 호출

[평가 로직] services/facility_applicability_eval.py
  FIELD_MAP = {  # binding_field → factories column
    employee_count   → employee_count   (DIRECT)
    area_size        → building_area    (DIRECT)
    power_capacity   → electrical_capacity_kw (DIRECT)
    voltage_level    → transformer_capacity_kva (AMBIGUOUS)
    storage_capacity → gas_capacity_m3  (AMBIGUOUS)
    equipment_type   → None (EQUIPMENT_JOIN)
    facility_type    → site_type        (AMBIGUOUS)
    process_type     → ksic_code        (AMBIGUOUS)
    monetary_value   → construction_amount (AMBIGUOUS)
    concentration_level → None (MISSING)
    distance_value   → None (MISSING)
  }
  → 평가가 보는 입력 필드 = 위 11개 binding_field 뿐.
  → facility.get(fac_col)으로 읽음. fac_col 없거나 None이면 MISSING_DATA.

[Compiler Core] services/compiler_core_svc.py
  facility_applicability / task_candidate (factory_id 기준) 읽어 진단 출력.
```

---

## 입력항목 → 저장 테이블/컬럼 매핑표 (factories 기준)

```
※ 시설관리 입력(회사/시설목록/공정/설비)은 전부 factories 단일 테이블 저장.
   (WO-INPUT-PATH-TRACE-001에서 확인: sector 라벨로만 구분, 단일 경로)
```

| INPUT_FIELD | factories COLUMN | 배치 SELECT | FIELD_MAP binding |
|---|---|---|---|
| 근로자수 | employee_count | YES | employee_count |
| 연면적 | building_area | YES | area_size |
| 전기용량 | electrical_capacity_kw | YES | power_capacity |
| 변압기 | transformer_capacity_kva | YES | voltage_level |
| 가스용량 | gas_capacity_m3 / kg | YES | storage_capacity |
| 공사금액 | construction_amount | YES | monetary_value |
| 시설유형 | site_type | YES | facility_type |
| 업종 | ksic_code | YES | process_type |
| 설비 | (equipment_type) | (조인) | equipment_type→None |

---

## ★ 건설 전용 입력 도달 여부 표 (YES/NO/UNKNOWN)

| 항목 | factories 저장 | 배치 SELECT 조회 | FIELD_MAP 존재 | facility_applicability 도달 | task_candidate 도달 |
|---|---|---|---|---|---|
| construction_process | NO | NO | NO | NO | NO |
| construction_work | NO | NO | NO | NO | NO |
| tower_crane (has_tower_crane) | YES | NO | NO | NO | NO |
| excavation (has_excavation_work) | NO | NO | NO | NO | NO |
| scaffold (has_scaffold_work) | NO | NO | NO | NO | NO |
| formwork (has_formwork_work) | NO | NO | NO | NO | NO |
| asbestos (has_asbestos) | NO | NO | NO | NO | NO |
| blasting (has_blasting) | YES | NO | NO | NO | NO |
| diving (has_diving_work) | NO | NO | NO | NO | NO |

```
참고 (건설이 아닌 일반 입력, 대조용):
  construction_amount  | 저장 YES | 배치 YES | FIELD_MAP YES(monetary_value) | 도달 YES
  employee_count       | 저장 YES | 배치 YES | FIELD_MAP YES                 | 도달 YES
  ksic_code            | 저장 YES | 배치 YES | FIELD_MAP YES(process_type)   | 도달 YES
```

---

## 도달 여부 요약 (사실, 판정 아님)

```
건설 전용 입력 9개:
  - factories 저장:  tower_crane, blasting 2개만 YES. 나머지 7개 NO(컬럼 부재).
  - 배치 SELECT:     9개 전부 NO (배치가 읽는 11개 컬럼에 건설 항목 없음).
  - FIELD_MAP:       9개 전부 NO (binding_field에 건설 항목 없음).
  - facility_applicability 도달: 9개 전부 NO.
  - task_candidate 도달:         9개 전부 NO.

= 건설 전용 입력 9개 중 어느 것도 Compiler Core(candidate)에 도달하지 않는다.
  tower_crane/blasting은 factories에 컬럼은 있으나,
  배치가 SELECT하지 않고 FIELD_MAP에도 없어 평가에 사용되지 않는다.

  실제 진단이 건설 사업장에 candidate를 만드는 입력은
  construction_amount / employee_count / ksic_code 등
  비건설-전용(일반) 필드뿐이다.
```

---

## 끊기는 지점 (위치 기록, 원인분석 아님)

```
건설 입력의 흐름은 다음 지점에서 끊긴다:

  construction_process / work / excavation / scaffold /
  formwork / asbestos / diving:
    → [끊김 위치 1] factories 컬럼 자체가 없음 (저장 단계).

  tower_crane / blasting:
    → factories 컬럼은 있음 (저장 YES).
    → [끊김 위치 2] 배치 SELECT 목록에 없음 + FIELD_MAP에 없음 (조회/평가 단계).

  공통:
    → 건설 binding_field가 FIELD_MAP에 0개.
      평가가 건설 항목을 볼 통로 자체가 없음.
```

---

## 성공 기준 점검

```
건설 입력 100% 추적 → ✅ (9개 항목 전부)
입력 → runtime candidate 도달 여부 표 작성 → ✅
원인분석/버그판정/엔진·VR·FacilityProfile·조건 수정 → 안 함 ✅
```

---

## 완료 문장

```
실제 사용자 입력의 Compiler Core 도달 경로를 추적하였다.
```

---

## IF/THEN 판정

```
규칙:
  IF 건설 입력이 candidate까지 도달 THEN 결과 표현 계층 문제
  ELSE 입력 연결 문제 (최우선 수정)

추적 결과:
  건설 전용 입력 9개 전부 candidate(facility_applicability/task_candidate)에
  도달하지 않음 (도달 여부 전부 NO).

  → IF 조건 FALSE → ELSE 분기

  ∴ 입력 연결 문제 (최우선 수정 대상)

  끊김 위치 2종 확정:
    (1) 저장 단계: 7개 항목은 factories 컬럼 자체가 없음.
    (2) 조회/평가 단계: tower_crane/blasting은 저장되나
        배치 SELECT·FIELD_MAP에 없어 평가가 못 읽음.

  ※ 이 WO는 도달 여부·끊김 위치 확인까지.
    "어떻게 연결할지"(구현)는 별도 WO + GPT 아키텍처 결정 영역.
    FIELD_MAP/조건/엔진은 GPT 전담이므로 Claude 임의 수정 금지.
```
