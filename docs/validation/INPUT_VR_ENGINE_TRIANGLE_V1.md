# INPUT VR ENGINE TRIANGLE V1
# WO-INPUT-VR-ENGINE-TRIANGLE-001

**작성일**: 2026-06-20
**성격**: 3자(사용자입력/VR입력/엔진사용)를 한 표에 정렬. 판단/탐색/결론 없음.
**자료 출처 (기확보)**:
  - 사용자 입력 = UI_FIELD_INVENTORY_V1 (회사/시설/공정/설비 화면 실측)
  - VR 입력 = VR_BRIDGE generation_spec (근로자수/KSIC/sector)
  - 엔진 사용 = FACILITYPROFILE_FIELD_INVENTORY_V1 (FacilityProfile 11차원)
              + ENGINE_INPUT_CONTRACT_TRACE_V1 (평가 조건 threshold/metric)

---

## 3자 비교표

표기:
- 사용자 입력 = 화면에서 입력 가능한가
- VR 입력 = VR generation_spec이 생성하는가
- 엔진 사용 = FacilityProfile에 담기는가 / 평가 조건이 비교하는가
  (FacilityProfile 담김 = "PROFILE", 평가조건 비교 = "조건" 표기)

| 항목 | 사용자 입력 | VR 입력 | 엔진 사용 |
|---|---|---|---|
| 근로자수(상시) | Y | Y | Y (PROFILE + 조건비교) |
| 업종(KSIC) | Y | Y | Y (PROFILE + scope) |
| sector | Y(계약) | Y | Y (PROFILE) |
| 하도급/외주 근로자수 | Y | N | Y (PROFILE) / N (조건비교) |
| 총근로자수(계산) | 자동 | N | Y (PROFILE) / N (조건비교) |
| 건물 용도(use_code) | Y(시설유형 연계) | N | Y (PROFILE) / N (조건비교) |
| 연면적(floor_area) | Y | N | Y (PROFILE) / N (조건비교) |
| 층수(floor_count) | Y | N | Y (PROFILE) / N (조건비교) |
| 공사금액 | Y(건설) | N | Y (PROFILE) / N (조건비교) |
| 전기수전용량(kW) | Y | N | Y (PROFILE) / N (조건비교) |
| 가스용량(m3/kg) | Y | N | Y (PROFILE) / N (조건비교) |
| 보일러용량 | Y | N | N |
| 승강기수 | Y | N | N |
| 연간에너지(TOE) | Y | N | N |
| 건물등급 | Y | N | N |
| 변압기(kVA) | Y | N | N |
| 위험물시설 | Y | N | N |
| 화학물질취급 | Y | N | N |
| 고압가스취급 | Y | N | N |
| 안전관리자선임(체크) | Y | N | N |
| 공장등록/다중이용 | Y | N | N |
| 타워크레인 | Y(건설) | N | N |
| 밀폐공간 | Y(건설) | N | N |
| 석면해체 | Y(건설) | N | N |
| 발파 | Y(건설) | N | N |
| 잠수 | Y(건설) | N | N |
| 하도급업체수 | Y(건설) | N | N |
| 건설공사유형 | Y(건설) | N | N |
| 공정(lv1~4) | Y | N | N |
| 설비명 | Y | N | N |
| 설비수량 | Y | N | N |
| 설비 설치연도 | Y | N | N |
| 설비 위치 | Y | N | N |
| 설비 법정점검대상 | Y | N | N |
| 설비 운영상태 | Y | N | N |

---

## 엔진 사용 열의 2단계 구분 (표 보조 설명, 판단 아님)

```
"엔진 사용"은 두 단계로 나뉘어 표기됨 (사실 구분):

  PROFILE = FacilityProfile 객체에 필드로 담김
            (sector/ksic_code + workforce 3 + building 3 + metrics 3 = 11차원)

  조건비교 = 평가 조건(appendix_condition/applicability_conditions)이
            threshold/metric으로 실제 비교
            (현재 = employee_count + KSIC scope)

→ 같은 "엔진 사용"이라도:
  근로자수 = PROFILE에도 담기고 조건도 비교 (Y/Y)
  연면적/전기/가스 등 = PROFILE엔 담기나 조건비교는 안 함 (Y/N)
  보일러/위험물/설비 등 = PROFILE에도 없음 (N)

※ 이 구분은 표의 정확성을 위한 사실 표기이며 판단이 아님.
```

---

## 성공 기준 점검

```
사용자 입력 / VR 입력 / 엔진 사용 3개가 동일 표에 정리됨 → ✅
이미 확보된 자료만 사용 → ✅ (4개 기존 문서 인용)
새 탐색 없음 → ✅
```

---

## 원칙 준수

```
병목 판단 안 함 ✅
엔진 좁다/VR 좁다 판단 안 함 ✅
개선안/확장안 안 함 ✅
새 탐색/Federation/Check Engine/패턴분석 안 함 ✅
표 1개, 결론 0줄 ✅
```

---

(결론 없음. 표만 제출.)
