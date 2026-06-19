# CHECK CONTRACT READ REPORT V1
# WO-CHECK-CONTRACT-READ-001

**작성일**: 2026-06-19
**성격**: 입출력 계약 비교만. Track A/facility_applicability/proof철학/재설계/권한/UI 분석 없음.
**관점**: 엔진은 범용. "A엔진 출력 = B엔진 입력"이면 연결.

---

## 1. Check Engine Input Contract

Check Engine 진입점(run_track_a)이 실제로 받는 입력:

```
필수 필드:
  facility_id (str, UUID)   ← 평가 대상 식별자

선택 필드:
  status (str)              ← 결과 필터 (MATCH_CANDIDATE/POSSIBLE_CANDIDATE)

데이터 타입:
  facility_id: 문자열 UUID
  status: 문자열 (옵션)

핵심: Check Engine 입력은 "식별자 1개(facility_id)"다.
  verdict 데이터를 통째로 받는 게 아니라,
  facility_id로 자기 소스를 조회하는 pull 방식.
```

---

## 2. Check Engine Output Contract

Check Engine이 반환하는 구조 (CheckResult):

```
반환 구조: CheckResultListResponse { items[], total, facility_id }

CheckResult 필드:
  applicability_id (str)
  facility_id (str)
  draft_id (str)
  applicability_status (str)
  match_details (dict, 선택)
  article_id / article_no / article_title / law_name (선택)
  verdict (enum: APPLICABLE / POSSIBLE / NOT_APPLICABLE / UNKNOWN)
  reason (str)
  check_method (str)
```

---

## 3. V4 Output Contract (직전 확인분)

```
verdict (str): REQUIRED / NOT_REQUIRED / UNKNOWN
evaluation_details[]:
  condition_id
  evaluation_result (MATCH/NOT_MATCH/NOT_APPLICABLE/UNKNOWN)
  evaluation_reason
  industry_name / threshold_value / operator / required_count
  scope_result / scope_reason
factory_id
```

---

## 4. 계약 비교 (한 페이지 표)

| 항목 | V4 Output | Check Input | 연결 |
|---|---|---|---|
| 식별자 | factory_id | facility_id (필수) | ✅ 동일 (이름만 다름) |
| 전달 방식 | verdict+details 통째 반환 | facility_id로 pull 조회 | ⚠️ 방식 다름 |
| verdict 데이터 | evaluation_details[] 포함 | 입력으로 안 받음 | ❌ 미사용 |

```
핵심 발견:
  Check Engine 입력 = facility_id 1개 (pull 방식)
  V4 출력 = verdict + evaluation_details[] (push 데이터)

  Check Engine은 "facility_id를 받아 자기 소스를 조회"한다.
  V4 출력(verdict 묶음)을 직접 입력으로 받는 구조가 아니다.
```

---

## 판정: C (일부) + B (일부)

```
식별자 레벨 (facility_id):
  → B (필드명만 다름: factory_id ↔ facility_id) → ADAPTER 불필요할 정도로 사소

전달 방식 레벨:
  → C (의미 자체가 다름)
  V4 = "결과를 밀어준다(push)"
  Check = "식별자로 직접 조회한다(pull)"
  → V4 출력을 Check 입력으로 "그대로" 넘길 수 없음.
    Check는 verdict 데이터를 입력으로 받지 않기 때문.

종합 판정: CONTRACT MISMATCH (전달 방식 불일치)
  단, 식별자는 호환되므로 "완전 불일치"는 아님.
  Check Engine이 facility_id만 받는 pull 엔진이라
  V4의 verdict 출력을 소비하는 입력 슬롯이 없음.
```

---

## 한 페이지 요약

```
Check Input Contract:
  facility_id (필수) + status (선택)
  = 식별자 pull 방식

V4 Output Contract:
  verdict + evaluation_details[] (push 데이터)

차이점:
  1. 식별자: factory_id ↔ facility_id (이름만 다름, 호환)
  2. 전달 방식: V4=push(데이터), Check=pull(식별자) ← 핵심 불일치
  3. Check은 verdict 데이터를 받는 입력 슬롯이 없음

연결 가능 여부:
  현재 계약으로는 직접 연결 불가 (CONTRACT MISMATCH).
  Check Engine이 "facility_id로 자기 소스 조회"만 하므로,
  V4 verdict를 Check에 먹이려면
  Check에 "verdict 데이터 입력 슬롯"이 있어야 한다 (현재 없음).
```

---

## 다음 작업 1개 (판단용, 구현 아님)

```
질문: Check Engine을 어느 방식으로 V4와 잇는가?

  경로 1 (Check이 pull 유지):
    V4 결과를 Check이 읽는 소스에 먼저 적재
    → 그 후 Check이 facility_id로 조회
    → 단 "Check이 읽는 소스"가 무엇인지는 이번 범위 밖
      (Track A 분석 금지 지시 준수)

  경로 2 (Check에 push 입력 추가):
    Check Engine에 "verdict 데이터 직접 입력" 슬롯 추가
    → Check Engine 입력 계약 변경 = GPT 아키텍처 영역

→ 어느 쪽이든 "Check Engine 입력 계약을 어떻게 둘지"는
  GPT(엔진 아키텍처)의 판단 영역.
  Claude 범위(구현·연결)를 넘는 결정.
```

---

## 원칙 준수

```
Track A 분석 안 함 ✅ (입력=facility_id, 출력=CheckResult 계약만 봄)
facility_applicability 분석 안 함 ✅
proof/evidence 철학 분석 안 함 ✅
Check Engine 재설계 안 함 ✅
권한/UI 분석 안 함 ✅
입력 계약 / 출력 계약만 비교 ✅
```

---

## 결론

```
V4 출력 → Check 입력 직접 연결: 불가 (CONTRACT MISMATCH).

이유 (계약만 본 결과):
  Check Engine 입력 = facility_id 1개 (pull).
  V4 출력 = verdict 데이터 (push).
  Check은 verdict를 받는 입력 슬롯이 없다.
  식별자(factory_id↔facility_id)는 호환되나, 그것만으로는
  V4의 verdict가 Check으로 흐르지 않는다.

다음 1개: Check Engine 입력 계약을 pull 유지 vs push 추가 중
  어디로 둘지 = GPT 아키텍처 판단.
  (Claude 범위 밖. 계약 비교까지가 이 WO.)
```
