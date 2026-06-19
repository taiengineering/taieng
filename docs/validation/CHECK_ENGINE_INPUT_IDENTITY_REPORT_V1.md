# CHECK ENGINE INPUT IDENTITY REPORT V1
# WO-CHECK-ENGINE-INPUT-IDENTITY-001

**작성일**: 2026-06-19
**목적**: 45cm Check Engine이 실제로 무엇을 입력받아 무엇을 증명하는지 정체 확인.
**금지 준수**: 위치 결정 안 함, 연결 설계 안 함, API 구현 안 봄.
**금지 준수**: V4/VR/Obligation/Transform 분석 안 함.

---

## 결론 먼저 (정직 보고)

```
판정 불가 — 내 접근 범위 안에서 45cm Check Engine의
실제 입력/출력/증명 코드를 찾지 못했다.

INPUT_CONFIRMED        → 아님 (미확인)
OUTPUT_CONFIRMED       → 아님 (미확인)
PROOF_TARGET_CONFIRMED → 아님 (미확인)

사장님이 준 예시 후보(FacilityProfile/Proof Chain 등)를
그대로 베껴 "확인됨"이라 쓰지 않는다.
그건 이번 세션 내내 지적받은 추정 보고 패턴이다.
```

---

## 실제로 확인한 것 (2건, 실측)

### 확인 1: proof/question/trace 류 테이블 탐색
```
DB에서 proof/missing/additional_question/reasoning/trace 검색:
  → 단 1개: runtime_evidence_trace
```

### 확인 2: runtime_evidence_trace 구조 (실측)
```
컬럼:
  id / compliance_evidence_id / obligation_id / work_order_id
  / review_decision_id / generated_document_id
  / legal_reference / trace_status / source_trace / created_at

정체 판정:
  이건 obligation → work_order → compliance_evidence → generated_document를
  잇는 "운영(runtime) 증거 이행 추적"이다.
  = "의무가 실제로 이행됐는가"를 추적하는 운영 감사 로그.

  ≠ 45cm Check Engine이 한다는 "법적 근거 추적 증명":
    (안전관리자 필요 → 280명/C28/별표3 50~999명 → 선임 1명)
    이런 "왜 이 의무가 발생하는가"의 법리 증명 체인이 아니다.

  → runtime_evidence_trace는 work_order(20,129건 운영) 세계의 것.
    45cm Check Engine의 출력이 아니다.
```

---

## 왜 정체를 확인 못 했는가 (정확히)

```
내 접근 범위 = tai-api 레포 + Supabase DB.

이 범위에서 본 "check" 관련 코드:
  check_engine_adapter = Track A 조회 어댑터 (확정, 엔진 아님)
  reverse_check        = 조회 어댑터 재사용
  runtime_evidence_*   = 운영 이행 추적 (work_order 세계)

이 범위에서 못 본 것:
  "45cm Check Engine" = 입력받아 법적 증명 체인을 생성하는 엔진.
  그 입력 스키마 / 출력 스키마 / 증명 로직 코드.

→ 45cm Check Engine이 tai-api 레포 밖(별도 위치 "45cm")에 있다면,
  내 현재 접근 범위로는 그 정체를 읽을 수 없다.
  추정으로 채우지 않는다.
```

---

## 3가지 질문에 대한 현재 상태

```
1. Check Engine 입력은 무엇인가?
   → 미확인. (후보 FacilityProfile/Factory/Verdict/Condition Result 중
     무엇인지 단정할 코드 근거 없음)

2. Check Engine 출력은 무엇인가?
   → 미확인. (runtime_evidence_trace는 운영 추적이지 법적 증명 아님.
     Proof Chain/Evidence/Missing Data 구조의 실제 코드 못 봄)

3. Check Engine은 무엇을 증명하는가?
   → 사장님 정의로는 "의무 발생의 법적 근거 체인"
     (안전관리자 필요 → 근거 → 증명).
     그러나 이를 수행하는 엔진 코드를 내 범위에서 못 찾음.
```

---

## 이 WO를 완료하려면 필요한 것 (단 하나)

```
"45cm Check Engine"의 실제 코드/위치:

  (a) 별도 레포명 (tai-api 밖이라면) → 그 레포 읽으면 입출력 확정
  (b) tai-api 안의 특정 파일 경로 (내가 아직 안 본) → 즉시 읽음
  (c) "45cm"이 가리키는 실제 의미 (서버/머신/모듈 별칭?)

이 중 하나만 알면:
  Check Engine 입력/출력/증명대상을 코드로 못 박는다.
  → INPUT_CONFIRMED / OUTPUT_CONFIRMED / PROOF_TARGET_CONFIRMED
```

---

## 원칙 준수

```
위치 결정 안 함 ✅
연결 설계 안 함 ✅
API 구현 안 봄 ✅
V4/VR/Obligation/Transform 분석 안 함 ✅
사장님 예시 후보 베껴쓰기 안 함 ✅ (추정 거부)
실측 2건만 보고 (proof 테이블 탐색 + runtime_evidence_trace 구조) ✅
```

---

## 결론

```
45cm Check Engine의 입력/출력/증명대상:
  내 접근 범위(tai-api + DB)에서는 확인 불가.

확인한 사실:
  DB의 trace 류 = runtime_evidence_trace 1개뿐이고,
  이건 운영 이행 추적(work_order 세계)이지
  법적 근거 증명 체인이 아니다.

45cm Check Engine이 tai-api 레포 밖에 있다면,
그 코드/위치를 알아야 입출력 정체를 못 박을 수 있다.

추정으로 후보를 채우지 않는다.
"45cm"의 실제 위치(레포/파일/의미) 한 줄이 이 WO를 푼다.
```
