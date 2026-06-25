# WO-BOUNDARY-LOCK-001
# 아키텍처 경계 동결 (Boundary Lock)

**작성일:** 2026-06-25 | **상태:** 계약 동결 (구현 아님)
**선행:** CURSOR-TASK-001 (Glue 연결 검증 완료 — 95건 통과, 경계 실증)
**목적:** 누구도 레이어를 침범하지 못하도록 책임 경계를 계약으로 고정한다.

> 지금은 기능을 더 만드는 시점이 아니라 아키텍처를 동결(freeze)하는 시점.
> 이 문서는 "이 기능은 어느 Layer인가?"를 즉시 결정하기 위한 헌법이다.

---

## 전체 파이프라인 (동결 대상)

```
입력 (facility_profiles)
   │
   ▼
① Applicability Engine     의무 생성
   │
   ▼
   obligation_instance
   │
   ▼
② Glue Adapter             순수 변환
   │
   ▼
③ 45CM Check Engine (API)  근거 역추적
   │
   ▼
④ Check Layer              6하원칙 + 필요값
   │
   ▼
⑤ Refinement Layer         중복/병합/정제
   │
   ▼
Result
```

---

## ① Applicability Engine

**소유:** TAI (cmc / obligation_instance 생성기)
**입력:** facility_profiles (sector / numeric / has_*)
**출력:** obligation_instance

```
한다:
  ✅ 의무 생성 (obligation_instance)
  ✅ Trigger 평가 (WORK/EQUIPMENT/MATERIAL/FACILITY)
  ✅ Threshold 평가 (worker_count ≥ N 등)
  ✅ Universal 평가 (sector baseline)
  ✅ Scope 필터 (범위밖 제거)

절대 안 한다:
  ❌ 증빙 생성 (Evidence) — Check Layer 소관
  ❌ 6하원칙 (6W) — Check Layer 소관
  ❌ UI 문장 / 화면 표현 — Refinement 소관
  ❌ 결과 병합 / 중복 제거 — Refinement 소관
  ❌ Verdict 생성 — Check Engine 소관
```

---

## ② Glue Adapter

**소유:** TAI (obligation_instance_adapter)
**입력:** obligation_instance (+semantic_clause JOIN)
**출력:** candidate dict 배열

```
한다:
  ✅ 필드명 변환 (obligation_instance → candidate)
  ✅ trigger_code 조립 (trigger_type:trigger_l2)
  ✅ confidence 밴드화 (numeric → HIGH/MEDIUM/LOW)

절대 안 한다:
  ❌ 판단 / 필터 (status='ACTIVE'는 Engine이 정한 것, 새 판단 아님)
  ❌ 의무 생성 / 제거
  ❌ 법령 해석
  ❌ Verdict 부여

원칙: Glue는 판단하지 않고 변환만 한다.
검증됨: CURSOR-TASK-001 — 95 candidate, NULL 0, 무수정 통과.
```

---

## ③ 45CM Check Engine (API)

**소유:** GPT (Deterministic Compiler 계보 — TAI 무수정)
**입력:** candidate / facility_applicability
**출력:** Verdict + Reason + Evidence(근거) + Draft

```
한다:
  ✅ 근거 역추적 (clause → article → law)
  ✅ Draft 검증 (executable_draft 적용성)
  ✅ Verdict 생성 (APPLICABLE/POSSIBLE/NOT_APPLICABLE/UNKNOWN)

절대 안 한다:
  ❌ 의무 생성 — Applicability Engine 소관
  ❌ Trigger 평가 — Applicability Engine 소관
  ❌ Threshold 평가 — Applicability Engine 소관
  ❌ Refinement (병합/표현) — Refinement 소관

경계 주의: 이 레이어는 GPT 소관. TAI(Claude)는 수정 금지.
  build_obligations_from_trigger_candidates 등 무수정 호출만.
```

---

## ④ Check Layer

**소유:** TAI (diagnosis_transform)
**입력:** Verdict + Reason + Evidence + Draft
**출력:** 6W + Required Evidence + 필요 데이터

```
한다:
  ✅ 6W 생성 (누가/무엇을/언제/어디서/왜/어떻게)
  ✅ 필요 데이터 계산 (의무 이행에 필요한 입력값)
  ✅ Required Evidence 생성 (제출/보관 서류 목록)

절대 안 한다:
  ❌ Applicability 변경 (의무 추가/제거)
  ❌ Verdict 변경 (Check Engine 판정 뒤집기)
  ❌ 법령 재해석

원칙: Verdict는 받은 그대로. 6W는 그 위에 얹는다.
```

---

## ⑤ Refinement Layer

**소유:** TAI (정제레이어)
**입력:** 6W 결과
**출력:** 화면용 표현 (Result)

```
한다:
  ✅ 중복 제거 (같은 의무 dedup)
  ✅ Merge (관련 의무 병합)
  ✅ Category (선임/점검/신고/교육/서류)
  ✅ 화면 표현 (실행 가이드 문장)

절대 안 한다:
  ❌ Applicability 변경 (의무 추가/제거)
  ❌ Verdict 변경
  ❌ 법령 판단

원칙: 표현만 바꾼다. 내용(의무/판정)은 못 바꾼다.
```

---

## 경계 결정 규칙 (성공 기준)

```
앞으로 어떤 기능이 추가되어도 아래 질문으로 Layer가 즉시 결정된다:

Q. 이 기능은 무엇을 하는가?
  의무를 만들/없앤다           → ① Applicability Engine
  필드명만 바꾼다              → ② Glue Adapter
  "해당되는가/근거는"을 판정    → ③ Check Engine (GPT)
  "무엇을 어떻게"를 푼다(6W)    → ④ Check Layer
  중복/병합/문장/카테고리       → ⑤ Refinement Layer

판별 테스트:
  - 의무 개수가 바뀌면 → ① (다른 레이어는 개수 불변)
  - 판정(APPLICABLE 등)이 바뀌면 → ③ (다른 레이어는 판정 불변)
  - 화면 글자가 바뀌면 → ⑤ (다른 레이어는 표현 안 함)
```

### 위반 예시 (해서는 안 되는 것)

```
✗ Refinement에서 "이 의무는 안 맞으니 빼자" → Applicability 침범
✗ Check Layer에서 "Verdict를 POSSIBLE로 바꾸자" → Check Engine 침범
✗ Applicability에서 "UI 문장을 예쁘게" → Refinement 침범
✗ Glue에서 "이건 노이즈니 거르자" → Applicability 침범
  (CURSOR-TASK-001의 executor 2건이 바로 이 함정 — 걸렀으면 THRESHOLD 손실)
```

---

## 동결 선언

```
이 경계는 동결(freeze)된다.

변경하려면:
  - 별도 WO로 경계 재정의를 명시적으로 선언해야 함
  - "편의상" 레이어를 넘는 것은 금지
  - 기능 추가 시 먼저 "어느 Layer인가"를 이 문서로 판별

목적: 엔진을 아무리 고도화해도 서로의 내부 구현을
      건드리지 않고 독립 발전 가능하게.
```

---

*WO-BOUNDARY-LOCK-001. 아키텍처 경계 동결.*
*5개 레이어 책임 고정. "이 기능은 어느 Layer인가" 즉시 결정.*
*핵심: 의무개수=① / 판정=③ / 표현=⑤. 편의상 레이어 침범 금지.*
*데이터 계약은 WO-DATA-CONTRACT-001 참조.*
