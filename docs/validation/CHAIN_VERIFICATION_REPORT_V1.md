# CHAIN VERIFICATION REPORT V1
# WO-END-TO-END-CHAIN-VERIFY-001

**작성일**: 2026-06-18
**성격**: 관찰만. 구현/수정/제안 없음. 실제 코드·호출 기준 증명.
**테스트 케이스**: 화성 제2공장 (C28, 280명)

---

## 최종 결론: CASE B — 중간 레이어에서 연결 끊김

```
끊긴 위치: Layer 2(V4 Evaluation) → Layer 3(Obligation) 사이

V4 평가기(/applicability/evaluate)는 verdict만 반환하고
Obligation 문장을 생성하지 않는다.
Obligation Bridge(/bridge/obligations)는 별도 테이블
(runtime_obligation_registry)을 읽으며 V4와 연결되지 않는다.
```

---

## Layer별 검증 (실제 코드 기준)

### Layer 1 — Input
```
상태: EXISTS + CONNECTED
근거: routers/applicability_api.py
  GET /applicability/evaluate/{factory_id}
  → factories 테이블 조회 → build_facility_profile()
  화성 제2공장(C28,280명) 입력이 FacilityProfile로 변환됨 (§8에서 실증)
```

### Layer 2 — V4 Evaluation
```
상태: EXISTS + CONNECTED + VISIBLE
근거: applicability_api.py evaluate()
  FacilityProfile → ApplicabilityCondition + condition_scopes
  → Scope 평가 → 수치 비교 → verdict 집계
  반환: verdict, matched_conditions, evaluation_details
  화성 280명 → MATCH 8건 (§8 실증)
```

### Layer 3 — Obligation Metadata
```
상태: EXISTS (데이터) / NOT CONNECTED (V4와 단절)

근거:
  applicability_conditions에 law_name/appendix_no/action_text 존재 (14/14)
  → 그러나 evaluate() 응답에 이 필드들이 포함되지 않음
  → evaluation_details는 industry_name/threshold/required_count만 반환
  → law_name/action_text는 SELECT * 로 읽지만 응답 JSON에서 제외됨

결정적 증거 (applicability_api.py 주석):
  "obligation_result 생성 금지"
  → V4 평가기는 의도적으로 Obligation을 생성하지 않도록 설계됨
```

### Layer 4 — API Response
```
상태: EXISTS / 부분 CONNECTED

/applicability/evaluate 응답에 실제 포함되는 것:
  ✅ verdict
  ✅ matched_conditions (condition_id 목록)
  ✅ evaluation_details (industry_name, threshold, required_count)
  ❌ obligation (law_name, action_text 미포함)
  ❌ rules_table

별도 경로 /bridge/obligations:
  runtime_obligation_registry 테이블 조회 (11건)
  → V4 applicability_conditions(14건)와 다른 테이블
  → factory_id로 V4 verdict와 조인하는 코드 없음
```

### Layer 5 — Frontend
```
상태: 확인 불가 (이번 WO 범위 내 미도달)

이유:
  Layer 3~4에서 이미 연결이 끊겨,
  프론트가 V4 Obligation을 받을 경로 자체가 없음
  diagnosis.py의 /diagnosis/run은 존재하지 않음
  (diagnosis.py는 견적/결제만 담당: request-quote, access-check)
```

### Layer 6 — Consumer Result
```
상태: 확인 불가

Layer 3 단절로 인해
"안전관리자 선임/관리감독자 지정/..." 의무 문장이
V4 경로로 소비자 화면에 도달하는 코드 경로가 현재 없음

(별도로 runtime_obligation_registry 기반 화면이
 존재할 수 있으나, 그것은 V4 Verdict와 무관한 별도 흐름)
```

---

## 체인 연결 맵 (실측)

```
Layer 1 Input          ✅ EXISTS + CONNECTED
   │  (factories → FacilityProfile)
   ▼
Layer 2 V4 Evaluation  ✅ EXISTS + CONNECTED + VISIBLE
   │  (verdict + evaluation_details 반환)
   ▼
Layer 3 Obligation     ⚠️ 데이터 EXISTS / 연결 BROKEN  ◀── 끊긴 지점
   │  (law_name/action_text는 DB에 있으나
   │   evaluate() 응답에 포함 안 됨,
   │   "obligation_result 생성 금지" 주석)
   ▼
Layer 4 API Response   ⚠️ verdict만 / obligation 미포함
   │
   ▼
Layer 5 Frontend       ❓ V4→화면 경로 없음
   ▼
Layer 6 Consumer       ❓ V4 의무 문장 미도달
```

---

## 별도 발견: 두 개의 분리된 Obligation 세계

```
세계 A — V4 (검증 완료, 화면 미연결):
  applicability_conditions 14건
  law_name/appendix_no/action_text 보유
  /applicability/evaluate로 verdict 계산
  → 그러나 Obligation 문장으로 변환 안 됨

세계 B — Runtime Obligation (운영 중, V4 미연결):
  runtime_obligation_registry 11건
  runtime_obligation_assignment 129건
  runtime_operational_work_order 20,129건
  /bridge/obligations로 조회
  → 그러나 V4 verdict가 이걸 생성하지 않음
  → 11건이 어디서 왔는지는 이번 WO 범위 아님 (관찰만)

두 세계가 같은 "의무" 개념을 다루지만
현재 서로 연결하는 코드 경로가 없다.
```

---

## 성공 기준 대비

```
이번 WO 목적: "체인이 연결되어 있는가?"
답: 부분 연결. Layer 1~2는 살아있음. Layer 3에서 끊김.

추정 없이 코드로 증명된 것:
  - Layer 1~2 연결됨 (applicability_api.py)
  - Layer 3 단절 ("obligation_result 생성 금지" 주석 + 응답 필드 부재)
  - 별도 runtime_obligation 세계 존재 (obligation_bridge.py)
```

---

## 결론 (CASE B)

```
CASE B: 중간 레이어에서 연결 끊김

정확한 위치:
  Layer 2 (V4 Verdict) → Layer 3 (Obligation 문장) 전환점

원인 (관찰된 사실):
  V4 평가기가 의도적으로 obligation을 생성하지 않음
  (설계상 "obligation_result 생성 금지")
  → WO-OBLIGATION-LAYER-IMPL-001에서 SQL로 문장 생성은 검증했으나
    그것이 실제 API 응답/화면으로는 아직 연결되지 않음

즉:
  "데이터는 있다" (Layer 3 메타 존재)
  "변환 SQL도 검증됐다" (직전 WO)
  그러나 "실제 호출 경로로는 아직 안 흐른다" (이 WO)
```

---

## 다음 단계 (관찰 결과 기반, 구현 아님)

```
체인을 살리려면 둘 중 하나가 필요 (판단은 사장님/GPT):

옵션 1: V4 evaluate() 응답에 obligation 필드 추가
  → law_name/action_text를 evaluation_details에 포함
  → 가장 짧은 경로 (데이터 이미 있음)

옵션 2: 세계 A(V4)와 세계 B(runtime_obligation) 연결
  → V4 verdict → runtime_obligation_registry 매핑
  → 더 큰 작업 (두 모델 정합 필요)

이번 WO는 측정만. 어느 옵션인지는 다음 판단 단계.
```
