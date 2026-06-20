# VR 57D SMOKE TEST REPORT V1
# WO-VR-57D-SMOKE-TEST-001

**작성일**: 2026-06-20
**목적**: VR 57차원 생성기 → FacilityProfile v2 적재 확인만 (스모크 테스트).
**대상**: vr_generation_spec.py (c78040b) × facility_profile_service.py (09d13b4)
**금지 준수**: 판정 실행/결과 분석/패턴 분석/evaluation 호출/condition 분석 없음.

---

## 실행 체인

```
각 샘플:
  build_virtual_facility_profile(spec) → row (factories 형태)
  → build_facility_profile(row) → profile (FacilityProfile v2)
  → 57차원 키 / 분리 / 값 보존 확인
```

---

## 샘플별 결과

```
[C28 manufacturing_standard]
  생성: OK / 적재: OK
  차원: 57개 (57 기대) ✅
  PRESENT 28 / UNKNOWN 27
  키 누락: 0개
  분리: 일반공정=O 건설공정=X 건설작업=X → OK

[F41 construction_standard]
  생성: OK / 적재: OK
  차원: 57개 ✅
  PRESENT 38 / UNKNOWN 17
  키 누락: 0개
  분리: 일반공정=X 건설공정=O 건설작업=O → OK

[J58 low_risk_office]
  생성: OK / 적재: OK
  차원: 57개 ✅
  PRESENT 17 / UNKNOWN 38
  키 누락: 0개
  분리: 일반공정=X 건설공정=X (사무형, 둘다 최소)
```

---

## 값 보존 검증

```
False 보존:  has_high_pressure_gas = state:PRESENT value:False → OK
0 보존:      equipment_count = state:PRESENT value:0 → OK (UNKNOWN 변환 안 됨)
None→UNKNOWN: boiler_capacity = state:UNKNOWN value:None → OK
```

---

## 성공 기준 점검

```
SMK-01 3개 샘플 생성 성공          → ✅
SMK-02 3개 샘플 FacilityProfile v2 적재 성공 → ✅
SMK-03 57차원 키 누락 0건          → ✅ (3샘플 전부 누락 0)
SMK-04 일반공정/건설공정/건설작업 혼합 0건 → ✅
SMK-05 판정 실행 0건               → ✅ (build_facility_profile만, evaluate 호출 없음)
SMK-06 조건/엔진/VR 추가 수정 0건  → ✅ (읽기·실행만, 수정 없음)
```

---

## 금지 준수

```
법령 판정 실행 안 함 ✅
결과 분석 안 함 ✅ (PRESENT/UNKNOWN 카운트는 적재 확인용, 판정 아님)
패턴 분석 안 함 ✅
evaluation 호출 안 함 ✅
condition 분석 안 함 ✅
Check Engine / Federation 논의 안 함 ✅
추가 필드 제안 안 함 ✅
```

---

## 완료 문장

```
VR 57차원 생성기는 FacilityProfile v2에 정상 적재된다.
법령 판정 및 결과 분석은 수행하지 않았다.
```

---

## 요약

```
생성기(vr_generation_spec) ↔ 입력계약(FacilityProfile v2) 맞물림 확인 완료.
  3개 프로파일 전부 57차원 무손실 적재.
  일반/건설 공정·작업 분리 유지.
  False/0/None 값 보존.

= "읽기 검증"으로 넘어가기 전 안전핀 통과.
  생성기와 입력계약이 실제로 맞물린다.
```
