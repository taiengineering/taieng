# CHECK INPUT CONTRACT READ REPORT V1
# WO-CHECK-INPUT-CONTRACT-READ-001

**작성일**: 2026-06-19
**관점 교정**: Check Engine을 독립 엔진으로 본다.
  V4 연결 여부 안 봄. "VR 입력이 Check 입력 계약을 충족하는가"만 본다.
**금지 준수**: V4/Track A/facility_applicability/push·pull/권한 분석 없음.

---

## 관점 (사장님 교정 반영)

```
틀린 관점 (직전 WO):
  V4 Output → Check Input  (엔진 간 연결)

맞는 관점 (이번 WO):
  VR (입력 생성기)
    ↓ Input Contract
  Check Engine (입력 → 증명 엔진)
    ↓
  Output

→ Check Engine도 범용 엔진. 입력 계약만 충족하면 태울 수 있다.
  VR이 그 입력을 만들 수 있는가만 본다.
```

---

## 1. Check Engine Input Contract

Check Engine이 받는 입력 (독립 엔진으로 관찰):

```
필수 입력:
  facility_id (str, UUID)

선택 입력:
  status (str) — 결과 필터

데이터 타입:
  facility_id: 문자열 UUID
  status: 문자열 (옵션)

= Check Engine은 "식별자 1개"로 실행된다.
  복잡한 verdict 묶음이 아니라 facility_id만 있으면 태울 수 있다.
```

---

## 2. Check Engine Output Contract

```
반환: CheckResultListResponse { items[], total, facility_id }

CheckResult:
  verdict (APPLICABLE/POSSIBLE/NOT_APPLICABLE/UNKNOWN)
  reason (str)
  match_details (dict)
  + applicability_id / draft_id / article_no / law_name / check_method
```

---

## 3. VR Input Contract 비교

```
VR이 생성하는 것 (VR_BRIDGE_DESIGN/REPORT 확인분):
  가상 사업장 = FacilityProfile 인스턴스
  = ksic / regular_workers / sector
  + 생성된 사업장은 P4_ 접두사, is_active=false로 factories에 적재 가능

Check Engine이 요구하는 입력:
  facility_id (UUID) 1개

비교:
  VR 출력         : 가상 사업장 (속성: ksic/workers/sector)
  Check 입력 요구 : facility_id (식별자)

  → VR이 가상 사업장을 factories에 적재하면 facility_id가 생긴다.
    그 facility_id를 Check Engine에 넣으면 태울 수 있다.
    즉 VR은 Check 입력(facility_id)을 만들 수 있다.
```

---

## 판정: B (ADAPTER) — 1단계 변환 필요

```
A. DIRECT (VR 입력 = Check 입력)        → 아님
   VR은 "사업장 속성"을 만들지, "facility_id"를 직접 만들지 않음.

B. ADAPTER (필드/형태 차이만)            → 이것
   VR 가상 사업장 → factories 적재 → facility_id 획득 → Check 입력
   = "적재" 1단계가 어댑터.
   VR은 이미 P4_/is_active=false 규약으로 factories 적재 가능 (메모리).
   → facility_id 생성은 적재의 자연스러운 결과.

C. MISMATCH (의미 불일치)               → 아님
   VR이 만드는 것(사업장)과 Check이 받는 것(사업장 식별자)은
   같은 대상(사업장)이다. 의미 불일치 아님.
```

---

## 한 페이지 요약

```
Check Input Contract:
  facility_id (필수) + status (선택)

VR Input Contract:
  가상 사업장 (ksic/workers/sector) 생성
  → factories 적재 시 facility_id 획득

연결 가능 여부: 가능 (ADAPTER 1단계)
  VR 가상 사업장 → factories 적재(P4_, is_active=false) → facility_id
    → Check Engine(facility_id) 실행

  = VR은 Check Engine을 태울 입력(facility_id)을 만들 수 있다.
    중간에 "적재" 1단계만 있으면 된다.
```

---

## 다음 작업 1개

```
WO-VR-CHECK-RUN-001 (실행 검증, 승인 시):
  1. VR 가상 사업장 N개 → factories 적재 (P4_, is_active=false)
  2. 각 facility_id → Check Engine(run-track-a) 실행
  3. CheckResult 반환 확인 (verdict/reason)
  = "VR이 Check Engine을 실제로 태울 수 있다" 증명

  ※ 단 Check Engine이 facility_id로 조회하는 소스에
    데이터가 있어야 결과가 나옴 — 그 소스 분석은
    이번 금지(Track A/facility_applicability 분석)에 걸리므로
    실행 WO에서 "결과 0건이어도 엔진 실행 자체는 성공"을
    성공 기준으로 분리.
```

---

## 원칙 준수

```
V4 분석 안 함 ✅
Track A / facility_applicability 분석 안 함 ✅
push/pull 논쟁 안 함 ✅ (이번엔 "VR이 입력을 만들 수 있는가"만)
권한 분석 안 함 ✅
Check Input Contract / VR Input Contract만 비교 ✅
```

---

## 결론

```
VR → Check Engine: 연결 가능 (ADAPTER 1단계).

Check Engine은 facility_id로 실행되는 독립 엔진.
VR은 가상 사업장을 만들고 factories에 적재하면 facility_id가 생긴다.
그 facility_id로 Check Engine을 태울 수 있다.

직전 WO의 "CONTRACT MISMATCH"는 잘못된 관점(V4→Check)이었고,
올바른 관점(VR→Check)에서는 ADAPTER 1단계로 연결된다.

다음 1개: VR 가상사업장 적재 → facility_id → Check 실행 검증.
```
