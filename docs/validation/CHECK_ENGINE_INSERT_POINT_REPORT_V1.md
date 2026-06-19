# CHECK ENGINE INSERT POINT REPORT V1
# WO-CHECK-ENGINE-INSERT-POINT-001

**작성일**: 2026-06-19
**목적**: 45cm Check Engine API 명세를 찾는 게 아니라,
          현재 파이프라인에서 Check Engine이 들어갈 위치만 확정.
**금지 준수**: 45cm API / OpenAPI / URL / 레포 / 새 엔진 탐색 안 함. 위치만.

---

## 결론 (한 줄)

```
Input
 ↓
V4 (판정: verdict + evaluation_details)
 ↓
Check Engine (판정 결과 → 근거 추적 → 증명 생성)   ← 여기 삽입
 ↓
Obligation (Adapter: 증명된 의무 → obligations)
 ↓
Transform (표현 스키마)
 ↓
UI
```

**= V4 다음, Obligation 앞.**

---

## 위치 확정 근거 (역할 기반, 탐색 없음)

### Check Engine의 역할 (사장님 정의)
```
주 역할: 검증 결과 → 근거 추적 → 증명 생성
  예: 안전관리자 선임 필요
        ↓ 근로자 280명 / KSIC C28
        ↓ 산안법 시행령 별표3 50~999명 구간
        ↓ 안전관리자 1명 선임 대상 (증명됨)
```

### 각 단계가 무엇을 다루는지 (확정된 계약)
```
V4 출력:      verdict + evaluation_details
              = "무엇이 해당되는가"의 판정 (MATCH/NOT_MATCH/...)
              = 아직 "왜"는 없음 (reason은 있으나 증명 체인은 아님)

Obligation:   evaluation_details → obligations (law_name/action_text/category)
              = "해당되는 것을 의무 문장으로"
              = 증명이 아니라 의무 표현
```

### 따라서 Check Engine은 V4와 Obligation 사이
```
이유:
  1. Check Engine은 "판정 결과"를 입력으로 받는다.
     → V4가 판정을 먼저 내야 한다. ∴ V4 뒤.

  2. Check Engine은 "증명(왜 해당되는가)"을 생성한다.
     → 이 증명이 obligations에 근거로 실려야 사용자에게
       "안전관리자 선임 필요 (근거: 280명/C28/별표3)"로 보인다.
     → 따라서 Obligation이 증명을 받아 쓰려면
       Check Engine이 Obligation 앞에 있어야 한다. ∴ Obligation 앞.

  3. Transform/UI는 표현 계층 → 증명은 그 전에 완성돼야 함.

∴ V4 → Check Engine → Obligation
```

---

## 대안 위치 검토 (왜 다른 자리가 아닌가)

```
대안 A: V4 → Obligation → Check Engine → Transform
  = 의무를 먼저 만들고 그 다음 증명.
  문제: obligations가 이미 만들어진 뒤 증명하면,
        증명이 obligation 생성 근거로 못 쓰임 (순서 역전).
  단 "사후 검증" 용도라면 이 자리도 가능 —
  그러나 사장님 정의(증명 생성)는 "근거를 만들어 의무에 싣는" 것이므로
  Obligation 앞이 더 정합.

대안 B: Input → Check Engine → V4
  = 판정 전에 증명?
  문제: 증명할 "판정 결과"가 아직 없음. 성립 불가.

→ V4 → Check Engine → Obligation 이 가장 정합.
```

---

## 현재 파이프라인에서 Check Engine은 "빠져 있다"

```
현재 (실측 확정):
  Input → V4 → Obligation(Adapter) → Transform → UI
                    ↑
            여기 V4와 Obligation 사이에
            Check Engine 자리가 비어 있음.

현재 obligations의 evidence 필드:
  Adapter가 law_name + law_article을 evidence로 넣음 (단순 법령 참조)
  = "근거 추적 증명 체인"이 아니라 "법령명 표기" 수준.
  → Check Engine이 채울 자리(증명 체인)가 지금은 Adapter의
    단순 evidence로 임시 대체돼 있는 상태.
```

---

## 삽입 위치 확정

```
삽입 지점: V4 출력 직후, Obligation(Adapter) 입력 직전.

데이터 흐름:
  V4 evaluation_details (판정)
    → Check Engine (각 MATCH에 대해 근거 추적 → 증명 체인 생성)
    → Obligation Adapter (증명 체인을 evidence로 실어 obligations 생성)
    → Transform → UI

Check Engine이 추가하는 것:
  각 obligation의 evidence를 "법령명 표기"에서
  "근거 추적 증명 체인"으로 격상.
  (280명/C28/별표3 50~999명 → 선임 1명, 같은 체인)
```

---

## 원칙 준수

```
45cm API / OpenAPI / URL / 레포 / 새 엔진 탐색 안 함 ✅
기존 파이프라인 구조만 사용 ✅
위치만 확정 (호출 방법은 다음 WO) ✅
```

---

## 결론

```
Check Engine 삽입 위치:

  Input → V4 → [Check Engine] → Obligation → Transform → UI

V4 다음, Obligation 앞.

이유: Check Engine은 V4 판정 결과를 받아 증명 체인을 만들고,
  그 증명을 Obligation이 evidence로 실어야 하므로
  반드시 V4 뒤 + Obligation 앞.

현재 이 자리는 비어 있고, Adapter의 단순 evidence(법령명)가
임시로 그 역할을 대신하고 있다.

다음 (위치 확정 후): "이 자리에서 45cm Check Engine API를
  어떻게 호출할까" — 그건 위치가 정해진 지금에야 나오는 질문.
```
