# FEDERATION BYPASS DECISION V1
# WO-FEDERATION-BYPASS-DECISION-001

**작성일**: 2026-06-19
**성격**: 방향 결정 (DECISION). 구현/연결/재설계 없음.
**권한**: 사장님 최종 판정. 이 문서는 그 결정을 공식 고정한다.

---

## 결정 문장 (공식)

> **현재 Phase에서는 TAI 로컬 우회 경로를 공식 유지한다.**
> **Check Engine / Machine Signal 편입은 별도 Federation Restoration Phase로 분리한다.**

---

## 핵심 원칙 (못 박음)

```
우회(Bypass)는 실패가 아니다.
현재 제품화·검증을 위한 의도된 로컬 단축경로다.

  - Obligation Adapter는 버그/미완성이 아니라
    Check Engine·Machine Signal 우회 공백을 메우는 정식 로컬 부품이다.
  - "우회 중"이라는 표기는 "고쳐야 할 결함"이 아니라
    "현재 Phase에서 의도적으로 선택한 경로"라는 뜻이다.
```

---

## 판정: A (우회 유지)

```
A. 우회 유지        → ★ 채택
B. 즉시 federation 복귀 → 기각
C. 이중 경로        → 기각 (현 Phase)
```

---

## 3가지 질문 답변

```
Q1. 현재 우회 단축경로를 당분간 유지할 것인가?
  → YES. V4/Adapter/Transform 경로는 이미 작동하고 §8 검증 완료.

Q2. Check Engine / Machine Signal을 지금 편입할 것인가?
  → NO. 지금 편입하면 파이프라인 전체 재설계 위험.

Q3. federation 복귀는 별도 Phase로 분리할 것인가?
  → YES. "Federation Restoration Phase"로 분리, 현 Phase 밖.
```

---

## 채택 근거 (A: 우회 유지)

```
1. 작동성: V4 → Adapter → Transform 경로가 이미 작동함.
   (USER_VISIBLE 데이터흐름 PASS, §8 8/8)

2. 재설계 위험: 지금 federation 복귀 시 전체 체인 재설계.
   Check Engine·Machine Signal·Projection이 연쇄로 바뀜.

3. Check Engine 계약 비용: ownerless 범용엔진이라
   Claim/Evidence/Chain 계약 설계가 선행돼야 함 (별도 작업).

4. Projection 연쇄: Machine Signal 도입 시 Projection 구조도 바뀜.
   현재 Transform을 federation projection-engine으로 교체해야 함.

5. 현 목표 정합: 현재 목표 = 법령엔진 검증 + VR 실험 기반 확보.
   federation 완성이 아님. 우회 유지가 목표에 부합.
```

---

## 기각 근거 (B / C)

```
B. 즉시 federation 복귀 — 기각:
   작동 중인 경로를 흔들어 재설계 위험.
   현 Phase 목표(검증·VR)와 무관한 대공사.

C. 이중 경로 — 기각 (현 Phase):
   로컬+federation 병렬은 유지비용 2배 + 정합성 관리 부담.
   검증 단계에서 두 경로를 동시에 끌고 갈 이유 없음.
   ※ 단 장기적으로 Federation Restoration Phase 진입 시
     "전환 기간 한정 이중 경로"는 그때 재검토 가능.
```

---

## Phase 분리 정의

```
[현 Phase] TAI Local Bypass Phase (공식 유지)
  경로: Input → V4 → Obligation Adapter → factory_diagnosis_results
        → Transform → UI
  상태: 작동·유지. Check Engine/Machine Signal 편입 안 함.
  목표: 법령엔진 검증, VR 실험 기반, 제품화.

[별도 Phase] Federation Restoration Phase (장기, 미착수)
  내용: Check Engine·Machine Signal 편입, Projection을
        federation projection-engine으로 정합.
  착수 조건: 현 Phase 목표(검증·제품화) 안정화 후 + 사장님 지시.
  선행 필요: Check Engine 계약(Claim/Evidence/Chain) 설계 = GPT 영역.
```

---

## 이 결정이 막는 루프 (명시)

```
금지 (이 결정으로 차단되는 행동):
  - Check Engine 즉시 연결 ⛔
  - Machine Signal 즉시 설계 ⛔
  - Projection 재설계 ⛔
  - Obligation Adapter 제거 ⛔
  - 현재 작동 경로 파괴 ⛔

→ 향후 "Check Engine을 지금 끼우자"는 방향이 나오면
  이 문서를 근거로 "별도 Phase"임을 상기하고 멈춘다.
  우회는 결함이 아니라 현 Phase의 공식 선택이다.
```

---

## 현재 상태 확정 (이 결정 반영)

```
IMPLEMENTED:       Input, Legal Engine(V4)        — 유지
BYPASSED:          Check Engine, Machine Signal    — 의도적 우회 (공식)
LOCAL_REPLACEMENT: Obligation Adapter,             — 정식 로컬 부품
                   factory_diagnosis_results,        (결함 아님)
                   Transform
UNVERIFIED:        Synthetic Reality (VR)          — 별도 검증

→ 이 표가 현 Phase의 공식 아키텍처다.
  "우회"와 "로컬 대체"는 결함 표기가 아니라 의도된 설계 상태다.
```

---

## 원칙 준수

```
Check Engine 즉시 연결 안 함 ✅
Machine Signal 즉시 설계 안 함 ✅
Projection 재설계 안 함 ✅
Obligation Adapter 제거 안 함 ✅
현재 작동 경로 파괴 안 함 ✅
방향 결정 문서만 작성 ✅
```

---

## 결론

```
현 Phase: TAI 로컬 우회 경로를 공식 유지.
Check Engine / Machine Signal 편입 = 별도 Federation Restoration Phase.

핵심: 우회는 실패가 아니라 제품화·검증을 위한 의도된 로컬 단축경로다.
  Obligation Adapter는 그 우회를 메우는 정식 부품이다.

이로써 "Check Engine을 지금 끼우자"는 루프는 공식적으로 차단된다.
다음 작업은 federation 복귀가 아니라,
현 Phase 목표(법령엔진 검증·VR 실험·제품화) 진행이다.
```
