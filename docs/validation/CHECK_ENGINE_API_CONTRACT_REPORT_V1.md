# CHECK ENGINE API CONTRACT REPORT V1
# WO-CHECK-ENGINE-API-CONTRACT-001

**작성일**: 2026-06-19
**전제 수용**: Check Engine은 45cm에 존재하는 범용엔진. 존재 여부 탐색 안 함.
**목적**: 현재 파이프라인이 45cm Check Engine API 계약을 충족하는지 확인.

---

## 결론 먼저 (정직 보고)

```
판정 불가 — "45cm Check Engine API 계약 명세"의 위치를 모른다.

현재 파이프라인 출력 계약: 확정 가능 (아래 정리)
45cm Check Engine API 입력 계약: 명세 위치 미상 → 추정 안 함

추정으로 "DIRECT/ADAPTER/MISMATCH"를 단정하면
직전까지 반복한 오류 패턴과 같아진다. 단정하지 않는다.
```

---

## 내가 아는 것 / 모르는 것 (분리)

```
아는 것:
  현재 파이프라인(VR/V4) 출력 계약 — 코드로 확정됨
    V4 출력: verdict + evaluation_details[{condition_id, evaluation_result,
             evaluation_reason, scope_result, threshold_value, ...}]
    VR 출력: 동일 계약 (V4 입력계약 공유, condition_id 단위)
    Adapter 출력: obligations[{law_name, law_article, action_text, category}]

  tai-api 레포 안의 check 관련:
    check_engine_adapter = Track A 조회 어댑터 (45cm 엔진 아님, 확정)
    DB에 evidence/check 테이블 다수 (runtime_evidence_* 등)

모르는 것 (= 이 WO가 막히는 지점):
  "45cm Check Engine"이 무엇인가:
    - 별도 서버? 별도 레포? 특정 호스트/엔드포인트?
    - API base URL / 입력 스키마 / 인증 방식?
  → 이 API 계약 명세가 어디 있는지 내 컨텍스트에 없음.
  → tai-api 레포에서 본 것은 전부 내부 어댑터/DB이지
    "45cm 외부 범용 Check Engine API 호출 클라이언트"가 아니었음.
```

---

## 현재 파이프라인 출력 계약 (확정분 — 절반은 됨)

```
이 WO의 4개 확인 항목 중 "2. 현재 파이프라인 출력 계약"은 확정 가능:

V4/VR 출력 (condition 단위 판정):
  {
    verdict: REQUIRED/NOT_REQUIRED/UNKNOWN,
    evaluation_details: [{
      condition_id, evaluation_result(MATCH/NOT_MATCH/NOT_APPLICABLE/UNKNOWN),
      evaluation_reason, scope_result, threshold_value, operator,
      industry_name, required_count
    }]
  }

Adapter 출력 (의무 단위):
  obligations: [{
    id, category, title, law_name, law_article,
    rule_type, risk_level, description, evidence[], required_count
  }]

→ 이게 "45cm Check Engine"이 받아야 할 입력 후보.
  단 45cm가 무엇을 받는지를 모르므로 매핑은 못 함.
```

---

## 막힌 지점 (정확히)

```
확인 항목 1. Check Engine API 입력 계약  → ❌ 명세 위치 미상
확인 항목 2. 현재 파이프라인 출력 계약    → ✅ 확정 (위)
확인 항목 3. 입력 매핑 가능 여부          → ❌ 1번 없이는 불가
확인 항목 4. 직접 연결 가능 여부          → ❌ 1번 없이는 불가

판정(DIRECT/ADAPTER/MISMATCH): 보류
  2번만 알고 1번을 모르므로 비교 불가.
```

---

## 사장님께 필요한 것 (이 WO 완료를 막는 단 하나)

```
"45cm Check Engine API 계약"이 어디에 정의돼 있는가?

후보:
  (a) 별도 레포 (예: taiengineering/check-engine 등)
      → 레포명 주시면 API 스키마 읽음
  (b) API 문서 / OpenAPI 스펙 URL
      → URL 주시면 계약 확인
  (c) tai-api 안의 특정 파일 (내가 아직 안 본)
      → 파일 경로 주시면 즉시 읽음
  (d) 45cm = 특정 서버의 별칭/호스트
      → base URL + 입력 스키마 주시면 매핑

이 중 하나만 알면:
  현재 출력 계약(확정분) ↔ 45cm 입력 계약 매핑 →
  DIRECT/ADAPTER/MISMATCH 즉시 판정.
```

---

## 원칙 준수

```
Check Engine 탐색 안 함 ✅ (존재 전제 수용, 찾지 않음)
Check Engine 존재 여부 논쟁 안 함 ✅ (존재 확정으로 받음)
Track A 분석 안 함 ✅
권한/UI 분석 안 함 ✅
추정으로 API 계약 단정 안 함 ✅ (명세 위치 모르므로 보류)
```

---

## 결론

```
이 WO는 "API 계약 읽기"인데,
45cm Check Engine API 계약 명세의 위치를 모른다.

현재 파이프라인 출력 계약은 확정했다 (V4/VR/Adapter 출력).
그러나 45cm 입력 계약을 모르므로 매핑/판정 불가.

판정: 보류 (명세 위치 필요).

다음: 사장님이 45cm Check Engine API 계약의 위치
  (레포명 / API 스펙 URL / 파일 경로 중 하나)를 알려주면
  현재 출력 계약과 매핑하여 DIRECT/ADAPTER/MISMATCH 즉시 판정.

추정으로 진행하지 않는다 — 그게 직전까지의 오류 원인이었다.
```
