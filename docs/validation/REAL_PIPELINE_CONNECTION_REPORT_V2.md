# REAL PIPELINE CONNECTION REPORT V2
# WO-REAL-PIPELINE-CONNECTION-002

**작성일**: 2026-06-20
**목적**: 실제 소비자 입력 1건이 입력→저장→FacilityProfile→거름망→Compiler Core→결과까지 도달하는지 확인.
**규칙 적용 (16회차)**: 목업 수량·factory 개수·도달률·결과 건수로 판단하지 않음. 입력 1건의 관통 여부만.
**금지 준수**: 수량분석/원인분석/해결책 없음. 법령·엔진·VR·Compiler 수정 없음. YES/NO/UNKNOWN만.

---

## STEP-1: 섹터별 입력 기준선 (SECTOR_INPUT_BASELINE_V1)

```
diagnosis_input_fields 기준 (is_active, 중복 제외):

| sector       | 입력필드 | 필수 | 선택 | 자동(auto_source) |
|--------------|---------|------|------|-------------------|
| BUILDING     | 34      | 11   | 23   | 7 (building_register) |
| INDUSTRIAL   | 18      |  9   |  9   | 0                 |
| CONSTRUCTION | 15      |  8   |  7   | 0                 |

거름망 입력 통로 (draft_slot.binding_field, 11종):
  employee_count, area_size, power_capacity, voltage_level,
  storage_capacity, facility_type, process_type, monetary_value,
  equipment_type, concentration_level, distance_value
  → 이 11종에 해당하는 입력만 거름망이 읽을 수 있다.
```

---

## STEP-2: 대표 소비자 입력 1건 (목업 factory 미사용)

```
실제 소비자가 diagnosis_input_fields에 입력 가능한 값만 사용:

BUILDING:    근로자120, 연면적8500, 층수12, 용도=업무시설,
             전기450kW, 변압기300kVA, 승강기4, 에너지1800toe, 가스50kg
INDUSTRIAL:  업종C28, 근로자85, 연면적3200, 전기900kW, 가스120kg,
             승강기1, 에너지2400toe
CONSTRUCTION: 업종F41, 근로자45, 공사금액58억, 공사유형=건축,
             타워크레인=Y, 밀폐공간=Y, 석면=N, 발파=N, 잠수=N, 하도급12
```

---

## STEP-3~4: 저장 / FacilityProfile 도달 (실측)

```
build_facility_profile(입력) 실행 결과 — 입력값이 프로파일에 들어가는가:

BUILDING:
  sector→profile         YES (BUILDING)
  근로자→workforce        YES (PRESENT/120)
  연면적→building.floor_area YES (PRESENT/8500)
  용도→building.use_code  YES (PRESENT/업무시설)
INDUSTRIAL:
  sector→profile         YES (INDUSTRIAL)
  근로자→workforce        YES (PRESENT/85)
  업종→ksic_code          YES (C28)
  전기→metrics.electrical YES (PRESENT/900)
CONSTRUCTION:
  sector→profile         YES (CONSTRUCTION)
  근로자→workforce        YES (PRESENT/45)
  타워크레인→construction  YES (PRESENT/True)
  공사금액→metrics         YES (PRESENT/5800000000)

→ 저장/FacilityProfile 계층은 세 섹터 모두 관통 (YES).
  건설 고유 입력(타워크레인)도 프로파일까지는 도달.
```

---

## STEP-5: 거름망 입력 도달 (대표입력 필드 × binding_field 통로)

```
거름망이 읽을 수 있는 입력 = binding_field 11종으로 매핑되는 것만.

BUILDING 대표입력:
  근로자 → employee_count    YES (거름망 통로 존재)
  연면적 → area_size         YES
  전기   → power_capacity    YES
  변압기 → voltage_level     YES
  가스   → storage_capacity  YES
  용도(building_use)         NO (binding_field 없음)
  승강기(elevator)           NO
  에너지(energy_toe)         NO
INDUSTRIAL 대표입력:
  업종   → process_type      YES
  근로자 → employee_count    YES
  연면적 → area_size         YES
  전기   → power_capacity    YES
  가스   → storage_capacity  YES
  설비(equipment)            UNKNOWN (equipment_type=EQUIPMENT_JOIN, 조인 의존)
CONSTRUCTION 대표입력:
  업종   → process_type      YES
  근로자 → employee_count    YES
  공사금액 → monetary_value  YES
  타워크레인                 NO (binding_field 없음)
  밀폐공간                   NO
  석면/발파/잠수             NO
  공사유형/하도급            NO

→ 공통·일반 입력(근로자/연면적/전기/가스/업종/공사금액)은 거름망 도달 YES.
  건설 고유 입력(타워크레인/밀폐/석면/발파/잠수)은 거름망 도달 NO.
```

---

## STEP-6: Compiler Core 도달 (거름망 통과 입력만)

```
거름망 통과 입력 → facility_applicability → task_candidate:

BUILDING:    근로자/연면적/전기/변압기/가스 → YES (일반 의무 도달)
             용도/승강기/에너지            → NO
INDUSTRIAL:  업종/근로자/연면적/전기/가스   → YES
             설비                         → UNKNOWN
CONSTRUCTION: 업종/근로자/공사금액          → YES (일반 의무 도달)
             타워크레인/밀폐/석면/발파/잠수 → NO (건설 고유 의무 미도달)
```

---

## STEP-7: 연결지도 (대표입력 1건 기준)

```
                  입력 → 저장 → FacilityProfile → 거름망 → Compiler Core → 결과

[BUILDING]
  근로자수        YES   YES     YES              YES      YES            YES
  연면적          YES   YES     YES              YES      YES            YES
  전기/변압기/가스 YES   YES     YES              YES      YES            YES
  용도/승강기/에너지 YES  YES     YES              NO       NO             NO

[INDUSTRIAL]
  업종            YES   YES     YES              YES      YES            YES
  근로자/연면적/전기/가스 YES YES YES            YES      YES            YES
  설비            YES   YES     YES              UNKNOWN  UNKNOWN        UNKNOWN

[CONSTRUCTION]
  업종            YES   YES     YES              YES      YES            YES
  근로자/공사금액  YES   YES     YES              YES      YES            YES
  타워크레인      YES   YES     YES              NO       NO             NO
  밀폐/석면/발파/잠수 YES YES   YES              NO       NO             NO
```

---

## 관통 여부 요약 (입력 1건, 수량 무관)

```
공통·일반 입력 (근로자/연면적/전기/가스/업종/공사금액):
  → 입력부터 Compiler Core 결과까지 관통 YES (3섹터 공통).

건설 고유 입력 (타워크레인/밀폐공간/석면/발파/잠수):
  → 저장·FacilityProfile까지 YES, 거름망에서 NO (관통 실패).
  끊기는 지점: FacilityProfile → 거름망 (binding_field 없음).

산업 설비 입력 (equipment):
  → 거름망 도달 UNKNOWN (EQUIPMENT_JOIN 경로, 별도 확인 필요).

건물 부속 입력 (용도/승강기/에너지/소방 등):
  → 거름망에서 NO (binding_field 없음).
```

---

## 성공 기준 점검

```
RPC-01 섹터별 입력 기준선 작성        → ✅ (STEP-1)
RPC-02 BUILDING 입력 1건 추적         → ✅
RPC-03 INDUSTRIAL 입력 1건 추적       → ✅
RPC-04 CONSTRUCTION 입력 1건 추적     → ✅
RPC-05 입력→결과 연결지도 작성        → ✅ (STEP-7)
RPC-06 수량 기반 판단 0건             → ✅ (factory수/applicability건수 미사용)
RPC-07 원인분석 0건                   → ✅ (끊김 지점 위치만 표기, 원인 분석 안 함)
```

---

## 완료 문장

```
실제 소비자 입력 기준으로 입력→결과 파이프라인 도달 여부를 확인하였다.
목업 데이터 수량과 기존 결과 테이블 건수는 판단 기준으로 사용하지 않았다.

공통·일반 입력은 입력→결과까지 관통(YES).
건설 고유 입력은 FacilityProfile까지 도달하나 거름망에서 끊김(NO).
산업 설비 입력은 거름망 도달 UNKNOWN.
```
