# VR CHECK ENGINE BRIDGE REPORT V1
# WO-VR-CHECK-ENGINE-BRIDGE-001

**작성일**: 2026-06-19
**성격**: VR→Input→V4→Check Engine 생데이터 경로 존재 여부만 확인.
**범위 제외**: 정제레이어 / 결과페이지 / 권한모델 (탐색 안 함).

---

## 현재 위치 (실측)

```
VR
 ↓ (V4 입력계약 = ksic/workers/sector)   ✅ 존재 (VR_BRIDGE 검증됨)
Input
 ↓                                        ✅ 존재
V4 (applicability_api.evaluate)
 ↓                                        ❌ 끊김 (아래 설명)
Check Engine (check-adapter/run-track-a)
```

---

## 연결 상태: NOT_CONNECTED

```
판정: V4 → Check Engine = NOT_CONNECTED

이유 (코드 실측):
  Check Engine 진입점 = POST /check-adapter/run-track-a
    → load_track_a_results(facility_id)
    → facility_applicability 테이블을 읽음  ← Track A 결과

  V4 진입점 = GET /applicability/evaluate
    → applicability_conditions 평가  ← V4 결과 (별도)

  두 엔진은 서로 다른 테이블을 읽는다:
    Check Engine ← facility_applicability (Track A)
    V4           ← applicability_conditions (V4)

  V4 출력을 Check Engine 입력으로 넘기는 코드 경로 없음.
```

---

## 확인 항목 답변

### 1. Check Engine 실제 진입점
```
POST /check-adapter/run-track-a   (routers/check_adapter_api.py)
  → services/check_engine_adapter.load_track_a_results()
  입력: facility_id (factories.id)
  소스: facility_applicability 테이블 (읽기 전용)
```

### 2. V4 출력이 Check Engine 입력으로 연결되는지
```
NO. 연결 안 됨.
  Check Engine은 facility_applicability(Track A)를 읽는다.
  V4 결과(applicability_conditions 평가)를 입력으로 받지 않는다.
  → V4 → Check Engine 직접 경로 없음.
```

### 3. Check Engine 출력 구조 (CheckResult, 실측)
```
실제 필드 (schemas/check_input_schema.CheckResult):
  applicability_id / facility_id / draft_id
  applicability_status (MATCH_CANDIDATE / POSSIBLE_CANDIDATE)
  match_details (jsonb)
  article_id / article_no / article_title / law_name
  verdict (APPLICABLE/POSSIBLE/NOT_APPLICABLE/UNKNOWN)
  reason / check_method

WO가 언급한 필드 대조:
  proof                → ❌ 없음 (reason이 유사 역할)
  evidence             → ❌ 없음 (match_details가 유사)
  missing_data         → ❌ 없음
  additional_questions → ❌ 없음

→ 현재 Check Engine 출력은 "proof/evidence/missing_data/
   additional_questions" 구조가 아니라
   "verdict/reason/match_details" 구조다.
```

### 4. VR 입력이 Check Engine까지 도달 가능한지
```
NO (현재).
  VR 입력 → V4 입력계약 변환: 가능 (VR_BRIDGE_REPORT_V1 검증됨)
  V4 → Check Engine: 끊김 (위 2번)
  → 따라서 VR → Check Engine 생데이터 경로는 현재 없음.

  단 VR → Check Engine을 "Track A 경유"로 본다면:
    Check Engine은 facility_applicability를 읽으므로
    VR이 facility_applicability를 채우면 도달 가능.
    그러나 그건 V4 경유가 아니라 Track A 경유 = WO 목표 경로 아님.
```

### 5. 현재 상태 판정
```
NOT_CONNECTED

V4와 Check Engine은 다른 테이블을 읽는 분리된 엔진.
V4 → Check Engine 직접 경로 없음.
VR은 V4까지만 도달 (V4 입력계약 공유), Check Engine엔 미도달.
```

---

## 한 페이지 요약

```
현재 위치:
  VR → Input → V4    : CONNECTED (VR_BRIDGE 검증됨)
  V4 → Check Engine  : NOT_CONNECTED

연결 상태: NOT_CONNECTED
  Check Engine은 facility_applicability(Track A)를 읽고,
  V4는 applicability_conditions를 읽는다. 둘을 잇는 경로 없음.
  Check Engine 출력도 proof/evidence/missing_data 구조가 아니라
  verdict/reason/match_details 구조.

다음 작업 1개:
  V4 → Check Engine 사이의 "출력 계약 비교" WO.
  (V4 evaluation_details vs CheckResult 필드 매핑 가능성 점검)
  ※ 단 이건 설계 비교만. 구현 아님.
  ※ Check Engine이 Track A 전용으로 설계됐는지
    (V4를 받을 의도가 있는지) 먼저 확인 필요.
```

---

## 원칙 준수

```
구현/리팩토링 안 함 ✅
정제레이어/결과페이지/권한 탐색 안 함 ✅
condition_id 비교분석 / Impact / Coverage / 우선순위 분석 안 함 ✅
로드맵 변경 제안 안 함 ✅
생데이터(테이블/코드) 기준 확인 ✅
```

---

## 결론

```
VR → Check Engine 생데이터 경로: 현재 없음 (NOT_CONNECTED).

원인은 V4 → Check Engine 단절:
  Check Engine = facility_applicability(Track A) 읽기 전용 어댑터
  V4 = applicability_conditions 평가
  두 엔진은 다른 세계.

VR은 V4까지만 닿는다 (V4 입력계약 공유 확인됨).
Check Engine까지 가려면 V4↔Check 사이 계약 연결이 선행돼야 한다.

다음 1개: V4 출력 ↔ CheckResult 계약 비교 (설계만).
```
