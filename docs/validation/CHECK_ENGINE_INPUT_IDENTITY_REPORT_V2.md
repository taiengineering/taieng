# CHECK ENGINE INPUT IDENTITY REPORT V2
# WO-CHECK-ENGINE-INPUT-IDENTITY-001 (45cminc/check 실측)

**작성일**: 2026-06-19
**출처**: 45cminc/check 레포 README.md + src/types.ts (실측, 추정 아님)
**대체**: REPORT_V1 (미확인 보류) → 이 V2가 코드 실측으로 확정

---

## 판정: 3가지 전부 CONFIRMED (단 사장님 정의와 차이 있음)

```
INPUT_CONFIRMED        → ✅ (CheckInput 계약, types.ts)
OUTPUT_CONFIRMED       → ✅ (EvidenceReport 계약, types.ts)
PROOF_TARGET_CONFIRMED → ✅ (단, "증명"이 아니라 "연결 상태 관찰")
```

---

## 결정적 발견: Check Engine은 "증명 엔진"이 아니다

```
README 명시 (원문 그대로):
  "It is NOT a judgement engine. It does not decide, judge, infer,
   recommend, or produce human language. effect is always 'abstain'."

= 판단/추론/추천/증명/인간언어 생성을 하지 않는다.
  effect는 항상 abstain(판단 보류).

→ 사장님이 정의하신 "안전관리자 필요 → 왜 → 근거 증명 체인 생성"은
  이 Check Engine이 하는 일이 아니다.
  이 엔진은 정반대로 "판단하지 않음"을 설계 원칙으로 못박았다.
```

---

## 1. Check Engine 입력 (CheckInput, 확정)

```
CheckInput {
  scope:           CheckScope { scope_ref }      ← 관찰 범위 (소비만)
  claims:          Claim[]                       ← 주장 (의무 주장)
  evidence:        Evidence[]                    ← 증거
  evidence_chains: EvidenceChain[]               ← 증거 체인
  request_ref:     string  (불투명, 분기 안 함)
  runtime_owner:   string  (기록만)
  observer:        string  (관찰 인스턴스 id)
  now:             string  (호스트 주입 결정적 시계)
}

Claim {
  claim_ref / scope_ref / claim_body? / origin_ref?
}
Evidence {
  evidence_ref / scope_ref / attached(bool) / evidence_body? / resolves_to_ref?
}
EvidenceChain {
  evidence_chain_ref / claim_ref / evidence_refs[] / scope_ref
}

→ 입력은 FacilityProfile/Factory/Verdict가 아니다.
  입력은 (Claim, Evidence, Evidence Chain) + Scope 다.
```

---

## 2. Check Engine 출력 (EvidenceReport, 확정)

```
EvidenceReport {
  report_id / scope_ref
  inventory:        { claims_received, evidence_received, chains_received }
  status_summary:   { claim:{...}, evidence:{...}, chain:{...} }   ← 상태 집계
  observation_records: ObservationRecord[]
  evidence_matrix:  EvidenceMatrixRow[]
  metadata:         { engine:"check", output_kind:"evidence_report", ... }
}

ObservationRecord {
  claim_ref / claim_status / evidence_statuses[] / chain_status / ...
}

→ 출력은 Proof Chain/Additional Questions가 아니다.
  출력은 "연결 상태 관찰 기록"(Evidence Report)이다.
  = 기계 산출물(machine artifact), 절대 고객 노출 안 됨(never customer-facing).
```

---

## 3. Check Engine이 "관찰"하는 것 (증명 아님)

```
관찰 대상: Claim ↔ Evidence ↔ Evidence Chain 사이의 "연결 상태".

상태값 (고정 enum):
  Claim:    CLAIM_PRESENT / CLAIM_REF_MISSING / CLAIM_OUT_OF_SCOPE
  Evidence: EVIDENCE_ATTACHED / NOT_ATTACHED / REF_RESOLVED
            / REF_MISSING / OUT_OF_SCOPE
  Chain:    CHAIN_NOT_DECLARED / PRESENT / COMPLETE / BROKEN / OUT_OF_SCOPE

= "이 주장(Claim)에 증거(Evidence)가 붙어 있는가,
   증거 체인이 완성(COMPLETE)인가 끊겼(BROKEN)는가"를 관찰.
  "왜 이 의무가 필요한가"를 증명하는 게 아니다.
```

---

## Federation 역할 (README)

```
Type:   Ownerless Runtime Asset (infra)
        — TAI 소유 아님, LEG 소유 아님, 어떤 엔진의 확장도 아님
Reads:  Check Scope + Claim/Evidence/Evidence Chain
Emits:  Evidence Report (기계 산출물, 고객 비노출)
Contract: 45cminc/federation-contracts schemas/check

설계 경계 (강제):
  Domain-blind (law_type/industry 분기 없음)
  Caller/Order/Workflow-blind
  No mutation / Deterministic (같은 입력 → 같은 출력)
```

---

## 사장님 정의 vs 실제 Check Engine (정합성 점검)

```
사장님 정의 (이전 WO들):
  주 역할: 검증 결과 → 근거 추적 → 증명 생성
           (안전관리자 필요 → 280명/C28/별표3 → 증명)
  부 역할: 데이터 결손 탐지 → 추가 질문 생성

실제 45cminc/check (코드 실측):
  주 역할: Claim/Evidence/Chain 연결 상태 관찰 → Evidence Report
  명시적 비역할: 판단/추론/추천/증명/인간언어 생성 안 함 (abstain)

→ 차이 큼.
  사장님이 머릿속에 둔 "증명 엔진"과
  실제 구현된 "연결상태 관찰 엔진"은 다른 것이다.

  부분 일치:
    부 역할(데이터 결손 탐지)은 유사 —
    Check이 EVIDENCE_NOT_ATTACHED / CHAIN_BROKEN / REF_MISSING로
    "증거 결손"을 관찰함. = 결손 탐지 기능은 실재.
    단 "추가 질문 생성"은 안 함 (abstain, 인간언어 생성 안 함).

  불일치:
    "근거 추적 증명 체인 생성"(주 역할)은 이 엔진에 없음.
    이 엔진은 증명을 "생성"하지 않고 연결을 "관찰"만 함.
```

---

## 원칙 준수

```
이번엔 추정 안 하고 실제 코드(README + types.ts) 읽음 ✅
입력/출력/관찰대상 전부 코드 근거로 확정 ✅
사장님 정의와의 차이를 정직하게 명시 (베끼지 않음) ✅
위치 결정/연결 설계/구현 안 함 ✅
```

---

## 결론

```
45cminc/check Check Engine 정체 (코드 확정):

  입력 = CheckInput { scope, claims[], evidence[], evidence_chains[], ... }
  출력 = EvidenceReport { inventory, status_summary, observation_records,
                          evidence_matrix }
  하는 일 = Claim↔Evidence↔Chain "연결 상태 관찰" (COMPLETE/BROKEN/MISSING)
  안 하는 일 = 판단/추론/추천/증명생성/인간언어 (effect=abstain)

★ 중요: 이 엔진은 "증명 엔진"이 아니라 "연결상태 관찰 엔진"이다.
  사장님이 정의하신 "근거 추적 증명 생성"과는 다르다.
  부 역할(증거 결손 탐지)은 일부 일치하나,
  주 역할(증명 체인 생성)은 이 엔진의 설계 비역할(abstain)이다.

→ 다음 판단 필요:
  Check Engine을 파이프라인에 넣으려면,
  먼저 "TAI가 기대하는 것(증명)"과 "Check이 하는 것(관찰)"의
  차이를 어떻게 메울지 = GPT 아키텍처 영역.
  (Claim/Evidence를 누가 만들어 Check에 넣는가도 별도 문제)
```
