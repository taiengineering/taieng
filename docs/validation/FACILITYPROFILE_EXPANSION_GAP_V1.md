# FACILITYPROFILE EXPANSION GAP V1
# WO-FACILITYPROFILE-EXPANSION-GAP-001

**작성일**: 2026-06-20
**성격**: 사용자 입력 ↔ FacilityProfile 매핑. GAP-A/GAP-B 2목록. 구현/수정 없음.
**자료 출처 (기확보)**:
  - 사용자 입력 = UI_FIELD_INVENTORY_V1 (회사/시설/공정/설비 실측)
  - FacilityProfile = FACILITYPROFILE_FIELD_INVENTORY_V1 (build_facility_profile 11차원)

---

## 매핑표 (사용자 입력 → FacilityProfile)

| 사용자 입력 | FacilityProfile 존재 | 매핑필드 |
|---|---|---|
| 근로자수(상시) | Y | workforce.regular_workers ← employee_count |
| 외주/하도급 근로자수 | Y | workforce.subcontract_workers ← subcontractor_worker_count |
| 총근로자수(자동) | Y | workforce.total_workers ← total_worker_count_calc |
| 업종(KSIC) | Y | ksic_code |
| sector | Y | sector |
| 연면적 | Y | building.floor_area ← building_area |
| 층수 | Y | building.floor_count ← floor_count |
| 건물용도(시설유형 연계) | Y | building.use_code ← building_use_code |
| 공사금액 | Y | metrics.construction_amount ← construction_amount |
| 전기수전용량(kW) | Y | metrics.electrical_kw ← electrical_capacity_kw |
| 가스용량(m3/kg) | Y | metrics.gas_capacity ← gas_capacity_m3/kg |
| 보일러용량 | N | - |
| 승강기수 | N | - |
| 연간에너지(TOE) | N | - |
| 건물등급 | N | - |
| 변압기(kVA) | N | - |
| 위험물시설 | N | - |
| 화학물질취급 | N | - |
| 고압가스취급 | N | - |
| 안전관리자선임(체크) | N | - |
| 공장등록 | N | - |
| 다중이용시설 | N | - |
| 타워크레인(건설) | N | - |
| 밀폐공간(건설) | N | - |
| 석면해체(건설) | N | - |
| 발파(건설) | N | - |
| 잠수(건설) | N | - |
| 하도급업체수(건설) | N | - |
| 건설공사유형(건설) | N | - |
| 공정(lv1~4) | N | - |
| 설비명 | N | - |
| 설비수량 | N | - |
| 설비 설치연도 | N | - |
| 설비 위치 | N | - |
| 설비 법정점검대상 | N | - |
| 설비 운영상태 | N | - |

---

## GAP-A: 사용자 입력 → FacilityProfile 존재 (현재 수용 범위)

```
11개 (= FacilityProfile 전체 차원과 일치):

  근로자수(regular_workers)
  외주/하도급 근로자수(subcontract_workers)
  총근로자수(total_workers)
  업종(ksic_code)
  sector
  연면적(floor_area)
  층수(floor_count)
  건물용도(use_code)
  공사금액(construction_amount)
  전기수전용량(electrical_kw)
  가스용량(gas_capacity)

→ 사용자가 입력하는 이 11개는 FacilityProfile이 이미 받는다.
```

---

## GAP-B: 사용자 입력 → FacilityProfile 미존재 (미수용 범위)

```
약 25개 (FacilityProfile에 담을 필드 없음):

  [시설 물리속성]
    보일러용량, 승강기수, 연간에너지(TOE), 건물등급, 변압기(kVA)

  [시설 위험속성 — 체크박스]
    위험물시설, 화학물질취급, 고압가스취급,
    안전관리자선임, 공장등록, 다중이용시설

  [건설 속성]
    타워크레인, 밀폐공간, 석면해체, 발파, 잠수,
    하도급업체수, 건설공사유형

  [공정]
    공정(lv1~4)

  [설비]
    설비명, 설비수량, 설비 설치연도, 설비 위치,
    설비 법정점검대상, 설비 운영상태

→ 사용자가 입력하지만 FacilityProfile이 받는 필드가 없다.
  (다음 확장 WO의 후보 목록)
```

---

## 완료 기준 점검

```
FacilityProfile 현재 수용 범위 (GAP-A) → ✅ 11개 목록
FacilityProfile 미수용 범위 (GAP-B)  → ✅ 약 25개 목록
2개 목록 작성 완료 → ✅
```

---

## 원칙 준수

```
필드 추가 안 함 ✅
FacilityProfile 수정 안 함 ✅
DTO 생성 안 함 ✅
엔진/VR 수정 안 함 ✅
구현/리팩토링 안 함 ✅
표 + 2목록만 ✅
```

---

## 참고 (사장님 우려 직접 대응, 판단 아닌 사실 표기)

```
사장님 우려: "34개 추가 → 실제 사용 0개 → 코드만 복잡"

이 표가 제공하는 사실 (아직 미해결로 남는 것):
  - GAP-A(11개) = FacilityProfile이 "받는" 필드.
  - 단 "받는다" ≠ "평가 조건이 비교한다".
    (ENGINE_INPUT_CONTRACT_TRACE: 조건 비교는 employee_count+KSIC 2개뿐)

  → 즉 GAP-A 11개 중에서도
    "FacilityProfile에 담기지만 조건이 안 쓰는" 필드가 있다
    (연면적/전기/가스/공사금액/층수/건물용도/하도급/총근로자 = 담기나 미비교).

  ※ "어떤 필드가 실제 평가에서 참조되는가"의 정밀 목록은
    이 WO 범위 밖 (다음: WO-EVALUATION-FIELD-USAGE-INVENTORY).
    이번엔 "FacilityProfile 수용 여부"까지만 표기.
```

---

(결론 없음. 2개 목록 + 표만 제출.)
