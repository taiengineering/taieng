# CHECK REAL INPUT READ REPORT V1
# WO-CHECK-REAL-INPUT-READ-001

**작성일**: 2026-06-19
**목적**: facility_id가 "입력"인가 "조회 키"인가 — Check Engine 진짜 입력 계약 확인.
**금지 준수**: V4/Track A 판정로직/결과해석/권한 분석 안 함. 입력 계약 구조만 봄.

---

## 결론 먼저

```
내가 지금까지 "Check Engine"이라 부른 것은
실제로는 실행 엔진이 아니라 "결과 조회·역추적 어댑터"였다.

facility_id는 그 어댑터의 조회 키다 (입력 데이터 아님).
그러나 그 어댑터가 읽는 facility_applicability에는
사업장 속성(workers/ksic/sector)이 없고 이미 계산된 판정 결과만 있다.

→ 진짜 실행 엔진(facility_applicability를 채우는 것)은
  내가 본 코드 범위에서 아직 확인 안 됨.
  판정을 단정하지 않고 정확히 보고한다.
```

---

## 확인된 사실 (코드 실측)

### 사실 1: 내가 본 "Check" 경로는 전부 조회 어댑터
```
POST /check-adapter/run-track-a   → load_track_a_results(facility_id)
POST /reverse-check/trace-track-a → load_track_a_results(facility_id)
POST /reverse-check/trace-single  → load_track_a_results(facility_id)

load_track_a_results(facility_id):
  facility_id로 facility_applicability 조회 (읽기 전용)
  → executable_draft/law_article/law_master 조인
  → CheckResult 포장

  코드 명시: "이 함수는 읽기 전용.
    evaluate_single_factory / evaluate_draft_for_facility 호출 없음."

→ 이건 "입력→증명 실행"이 아니라 "기존 결과 조회·포장".
```

### 사실 2: facility_applicability에는 사업장 속성이 없다
```
facility_applicability 컬럼 (실측):
  id / factory_id / draft_id / part_id
  applicability_status (text) / match_details (jsonb) / created_at

  → workers / ksic / sector 없음.
  → 이미 계산된 "판정 결과"만 저장 (status + details).
  → 즉 이 테이블은 "엔진 입력"이 아니라 "엔진 출력 저장소".
```

### 사실 3: 진짜 실행 엔진은 아직 코드로 못 봤다
```
코드 주석이 반복 언급하는 실제 실행 함수:
  evaluate_single_factory
  evaluate_draft_for_facility

  이 둘이 facility_applicability를 "채우는" 실행 엔진으로 추정.
  그러나 이 함수의 입력 시그니처는 내가 본 파일들에 없음.
  (check_adapter / reverse_check / runtime_evaluator / runtime_candidate
   전부 조회·CRUD·별도엔진이었음)

→ "실행 엔진이 facility_id를 받는가, 사업장 데이터를 받는가"는
  evaluate_single_factory 코드를 봐야 확정.
  아직 위치 미확인.
```

---

## 판정: 보류 (B 또는 C, 확정 불가)

```
WO 판정 후보:
  A. 실제 입력 = 사업장 데이터 → VR 직접 연결
  B. 실제 입력 = facility_id   → VR 적재 필요
  C. 혼합                      → 최소 어댑터

현재 확정 가능한 것:
  내가 본 "Check 경로"(조회 어댑터)는 facility_id로 기존 결과를 읽는다.
  = 조회 계약은 facility_id (사장님 지적이 맞음 — 조회 키).

현재 확정 불가한 것:
  facility_applicability를 "채우는" 실행 엔진
  (evaluate_single_factory)이 무엇을 입력으로 받는지.
  → 이게 A/B/C를 가른다.
  → 그 코드를 아직 못 봤으므로 단정하지 않는다.

잠정 판정: 보류.
  단 한 가지는 분명 — facility_id는 "조회 어댑터의 키"이지
  "증명 엔진의 입력"이 아니다. 사장님 지적 방향이 맞다.
```

---

## 다음 작업 1개 (정확히 좁힘)

```
WO-EVALUATE-ENGINE-INPUT-READ-001:
  evaluate_single_factory / evaluate_draft_for_facility
  단 2개 함수의 입력 시그니처만 읽는다.

  확인:
    이 함수가 받는 것이
      (a) factory_id (str)      → B (조회 키, VR 적재 필요)
      (b) 사업장 데이터 객체     → A (VR 직접 연결)
      (c) 혼합                  → C

  이 함수의 위치만 찾으면 (services/ 어딘가) 1파일로 판정 끝.
  ※ V4(applicability_api) 아님. facility_applicability 채우는 엔진.
  ※ 판정 로직 내용은 안 봄 — 입력 시그니처만.
```

---

## 원칙 준수

```
V4 분석 안 함 ✅ (applicability_api 안 봄)
Track A 판정 로직 분석 안 함 ✅ (match_details 내용 안 해석)
결과 해석 안 함 ✅
권한 분석 안 함 ✅
입력 계약 구조(컬럼/시그니처)만 확인 ✅
추적 루프 회피: 4파일 보고 멈춤, 단정 안 하고 보고 ✅
```

---

## 결론

```
사장님 지적이 맞다:
  facility_id는 "조회 키"다. 내가 본 Check 경로는 전부
  facility_id로 기존 결과(facility_applicability)를 읽는 조회 어댑터다.

그러나 "진짜 실행 엔진의 입력"은 아직 확정 못 했다:
  facility_applicability를 채우는 evaluate_single_factory가
  사업장 데이터를 받는지(A) facility_id를 받는지(B)
  그 코드를 아직 못 봤다.

→ VR이 Check Engine을 "factories 적재 없이 바로 태울 수 있는가"는
  evaluate_single_factory 입력 시그니처 1개로 판정된다.
  다음 WO에서 그 함수만 읽으면 A/B/C 확정.

단정하지 않고 보류로 정직하게 보고한다.
```
