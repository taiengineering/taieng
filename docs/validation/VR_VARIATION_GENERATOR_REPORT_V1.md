# VR VARIATION GENERATOR REPORT V1
# WO-VR-VARIATION-GENERATOR-001

**작성일**: 2026-06-20
**수정 파일**: services/vr_generation_spec.py (commit 06307244, sha 7a5848a)
**목적**: 57차원 템플릿 3종 → 57차원 조합 생성기 전환.

---

## 변경 요약

```
프로파일 구조(제조/건설/사무)는 유지.
프로파일 내부 값 = 고정값 → 변주(조합 기반)로 전환.

변주 방식:
  수치 필드  → 범위 랜덤 (_rint, 예: employee_count 1~3000)
  boolean   → 코인 (_coin, True/False 랜덤)
  배열/공정/작업 → 부분집합 조합 (_subset)
  seed 지정 시 재현 가능.
```

---

## 변주 규칙 적용 (지시서 대비)

```
수치 필드:
  employee_count:        고정 280 → 범위 1~3000 랜덤
  electrical_kw:         고정 1500 → 범위 20~5000 랜덤
  gas_capacity_m3:       고정 200 → 범위 10~5000 랜덤
  construction_amount:   고정 500억 → 범위 1억~1조 랜덤
  building_area/floor_count/transformer/boiler/elevator 등 전부 범위 변주

boolean (위험속성/건설/건설작업 20개):
  고정값 → True/False 코인 랜덤

배열:
  equipment_names:       고정 → 풀에서 부분집합 조합
  equipment_install_years/locations/legal_targets/operation_status → 항목별 변주

공정:
  process_lv1~3:         고정 → 풀에서 선택 조합 (제조)
건설 공정/작업:
  construction_process:  고정 CP-100 → 5종 풀에서 선택
  construction_work:     고정 CW-210 → 6종 풀에서 선택
```

---

## 측정 결과 (1,000개 생성)

```
VG-02 중복률:     0.00% (고유 1000/1000) ✅ (1% 이하 목표 충족)
VG-03 ksic 외 다양성: ✅ (수치/배열/공정 다수 필드 다양성 확보)
VG-04 엔진 수정:   0건 ✅
VG-05 FacilityProfile 수정: 0건 ✅

다양성 등급 (distinct):
  D3 (>20):   20개
  D2 (6~20):  10개
  D1 (2~5):   26개
  D0 (1):     2개 (gas_capacity_kg, process_lv4)
  distinct>10 필드: 22개
```

---

## VG-01 정직 보고 (구조적 미달)

```
VG-01 목표: "57개 필드 중 50개 이상 distinct > 10"
실측: distinct>10 = 22개.  → 목표 50개 미달.

미달 원인 (추정 아님, 구조적 산술):
  - 57개 입력 필드 중 boolean 필드가 20개.
    (has_* 17개 + is_* 3개)
  - boolean은 값이 {True, False}(+None) 뿐이라
    distinct가 영구히 ≤ 3. distinct>10 절대 불가능.
  - 따라서 distinct>10이 가능한 필드의 상한 = 비-boolean 37개.
    (57 - boolean 20 = 37)

  비-boolean 37개 중 distinct>10 달성: 22개.
  나머지 15개는 카테고리/코드 필드(building_grade 4종,
  construction_type 6종, process_lv 풀 5~7종, 코드 5~6종 등)라
  후보 풀 크기 자체가 작아 >10 미달.

결론:
  "distinct>10 필드 50개 이상"은 boolean 20개 구조상 달성 불가능한 수치.
  현실적 상한은 비-boolean 37개이며, 그 중 22개가 >10.
  나머지는 카테고리 풀 한계.

  → VG-01은 목표 수치 자체가 입력 구조(boolean 20개)와
    맞지 않았다. 억지로 50개를 맞추려면 boolean을 가짜 다값으로
    만들어야 하는데, 그건 "False는 False 유지" 원칙 위반이라 안 함.
```

---

## 변주 전후 비교

```
                  변주 전(템플릿)   변주 후(조합)
distinct>10 필드      1개(ksic만)      22개
D3(>20)              0개              20개
중복률               해당없음(3종)     0%
employee_count       3종 고정          distinct 16+ (범위)
equipment_names      3종 고정          distinct 639 (조합)
construction_amount  1종 고정          distinct 100+ (범위)

= 템플릿 3종 반복 → 조합 기반 생성으로 전환됨.
```

---

## 분리 / 값 원칙 (유지 확인)

```
분리: 제조=일반공정 PRESENT/건설공정 UNKNOWN,
      건설=일반공정 UNKNOWN/건설공정·작업 PRESENT → 혼합 0건 ✅
False 보존: boolean False가 False로 유지 (0 변환 없음) ✅
0 보존: equipment_count 0 유지 ✅
None→UNKNOWN: 미설정 필드 UNKNOWN ✅
57차원 적재: 3프로파일 전부 FacilityProfile v2 57차원 ✅
```

---

## 성공 기준 점검

```
VG-01 distinct>10 50개 이상 → ✗ 미달 (22개)
       사유: boolean 20개 구조상 상한 37개. 정직 보고.
VG-02 중복률 1% 이하        → ✅ (0%)
VG-03 ksic 외 다양성        → ✅
VG-04 엔진 수정 0건         → ✅
VG-05 FacilityProfile 수정 0건 → ✅
```

---

## 완료 문장

```
VR 생성기는 템플릿 반복이 아닌 조합 기반 생성기로 변경되었다.

단 VG-01(distinct>10 필드 50개)은 입력 구조상 미달이다:
  57개 중 boolean이 20개라 distinct>10 가능 필드의 상한이 37개이며,
  그 중 22개가 달성됐다. 50개는 boolean 비중을 고려하지 않은 목표 수치였다.
```

---

## 측정 사실 정리 (판단 아님)

```
변주 전: 57차원 템플릿 3종 (조합 다양성 사실상 3)
변주 후: 57차원 조합 생성기 (1000개 전부 고유, distinct>10 필드 22개)

이제 "전기용량/가스용량/위험물/공정/설비를 바꾼" 사업장이
실제로 서로 다르게 생성된다.
  = 처음으로 "57개 입력을 흔드는" 것이 가능해졌다.

남은 구조적 사실: boolean 20개는 본질적으로 2~3값이므로,
  다양성 지표를 distinct로만 보면 영구히 낮게 나온다.
  (이건 한계 보고이지 개선 제안이 아님)
```
