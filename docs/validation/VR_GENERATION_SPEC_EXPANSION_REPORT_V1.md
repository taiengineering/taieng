# VR GENERATION SPEC EXPANSION REPORT V1
# WO-VR-GENERATION-SPEC-EXPANSION-001-REBASE

**작성일**: 2026-06-20
**신규 파일**: services/vr_generation_spec.py (commit c78040b)
**목적**: 신규 VR generation_spec 생성기 생성 (수정 아님 — 기존 파일 부재).

---

## 배경 (수정→신규 전환 이유)

```
기존 VR 생성기 파일이 tai-api에 존재하지 않음:
  vr_generation_spec / virtual_factory_generator /
  synthetic_factory_builder / factory_generator → 전부 미존재.

지금까지 "VR"은 SQL(generate_series + CROSS JOIN)로 만든 임시 생성이었음.
  = generation_spec이 "3차원"이었던 건 코드 계약이 아니라
    내 SQL이 (ksic/workers/sector) 3개만 만들었기 때문.

FacilityProfile v2가 57차원을 받게 됨(WO-FACILITYPROFILE-EXPANSION-001).
→ 따라서 "수정"이 아니라 "신규 생성"으로 고정.
```

---

## 생성 결과

```
파일: services/vr_generation_spec.py (279줄)
주요 함수:
  build_virtual_facility_profile(spec) -> dict   ← 메인 생성기
  list_profile_types() -> [3개]
  list_all_input_keys() -> [57개 입력 키]

출력: factories row 형태 dict.
  facility_profile_service.build_facility_profile에 그대로 투입 가능.
  57개 입력 키 전부 존재 (미사용 = None=UNKNOWN).
```

---

## 생성 프로파일 3개

```
1. manufacturing_standard (제조업 표준)
   - 공정/설비/전기/가스/보일러 포함
   - 건설 필드 = UNKNOWN(None)
   - PRESENT 28개 / UNKNOWN 27개

2. construction_standard (건설업 표준)
   - construction_process / construction_work 포함
   - 일반 process = None (혼합 금지)
   - PRESENT 38개 / UNKNOWN 17개

3. low_risk_office (저위험 사무형)
   - 설비/위험속성 최소
   - PRESENT 17개 / UNKNOWN 38개
```

---

## 테스트 결과 (샘플 3개)

```
[C28 manufacturing_standard]
  입력키 누락: 0개
  FacilityProfile 차원: 57개 (57 기대) ✅
  PRESENT 28 / UNKNOWN 27

[F41 construction_standard]
  입력키 누락: 0개
  FacilityProfile 차원: 57개 ✅
  PRESENT 38 / UNKNOWN 17

[J58 low_risk_office]
  입력키 누락: 0개
  FacilityProfile 차원: 57개 ✅
  PRESENT 17 / UNKNOWN 38
```

---

## 분리 검증 (VR-05)

```
제조 manufacturing:
  process_lv1 = PRESENT / construction_process_code = UNKNOWN
건설 construction:
  process_lv1 = UNKNOWN / construction_process_code = PRESENT
              / construction_work_code = PRESENT

→ 일반 공정과 건설 공정/작업 분리 OK (혼합 없음).
```

---

## 값 원칙 검증

```
False 유지:  has_hazardous_material = state:PRESENT value:False ✅
0 유지:      equipment_count = state:PRESENT value:0 ✅ (UNKNOWN 변환 안 됨)
None→UNKNOWN: 미채운 키 = state:UNKNOWN value:None ✅

→ 실제 판정 추론 없음. 법령 조건 반영 없음. 현실적 값 범위만.
```

---

## 성공 기준 점검

```
VR-01 신규 파일 services/vr_generation_spec.py 생성 → ✅
VR-02 build_virtual_facility_profile() 구현 → ✅
VR-03 FacilityProfile v2 57차원 전체 키 생성 가능 → ✅ (3샘플 누락 0)
VR-04 3개 프로파일 생성 가능 → ✅ (manufacturing/construction/office)
VR-05 일반 공정과 건설 공정/작업 분리 → ✅
VR-06 V4/condition/FacilityProfile/UI 수정 0건 → ✅
```

---

## 금지 준수

```
법령 판정 실행 안 함 ✅
V4 수정 안 함 ✅
condition 수정 안 함 ✅
FacilityProfile 수정 안 함 ✅ (이번 WO에선 안 건드림)
Check Engine 수정 안 함 ✅
UI 수정 안 함 ✅
결과 변화 분석 안 함 ✅ (생성만)
```

---

## 완료 문장

```
VR generation_spec은 신규 services/vr_generation_spec.py로 생성되었고,
FacilityProfile v2 57차원 입력 dict를 생성할 수 있다.
판정 실행 및 결과 분석은 수행하지 않았다.
```

---

## 구현 메모 (사실 표기)

```
1. 생성기 출력은 factories row 형태 (build_facility_profile이 row.get으로 읽음).
   → vr.build_virtual_facility_profile(spec) → fps.build_facility_profile(row)
     체인으로 가상 사업장 → FacilityProfile v2 변환 가능.

2. profile_type 3개는 _PROFILE_BUILDERS에 등록. 추가 프로파일은
   빌더 함수 추가 + 등록만으로 확장 (판정 추론 금지 원칙 유지).

3. variant는 현재 baseline만. variant별 분기 훅 자리 마련(값 보정 없음).

4. 이번 WO는 "생성기 생성"까지.
   다음(별도 WO): 이 생성기로 N개 사업장 생성 → FacilityProfile v2 적재 →
   (판정 실행은 별도 결정). 결과 변화 분석은 본 WO 범위 밖.
```
