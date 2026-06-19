# CURRENT PROJECT STATE V2
# WO-PROJECT-STATE-REBASE-001

**작성일**: 2026-06-18
**성격**: 상태 기록만. 구현/수정/연결 없음.
**계기**: WO-END-TO-END-CHAIN-VERIFY-001 (CASE B 연결 끊김) 반영

> ⚠️ 철회: "Obligation Layer 완료" 인식 철회.
> 정확한 표현: "Obligation Metadata 존재, 단 End-to-End 연결 미완료"

---

## 4단계 정의

```
BUILT        — 코드/데이터가 존재하는가
VERIFIED     — 정답지·측정으로 검증됐는가
CONNECTED    — 실제 호출 경로로 다음 레이어와 이어졌는가
USER_VISIBLE — 소비자 화면에 실제로 보이는가
```

핵심 구분: **BUILT ≠ CONNECTED.**
이번 체인 검증으로 "있지만 안 이어진" 것들이 드러났다.

---

## 프로젝트 구성요소 전수 상태표

| 구성요소 | BUILT | VERIFIED | CONNECTED | USER_VISIBLE |
|---|---|---|---|---|
| Track A (현행 엔진) | YES | YES (FP 93%) | YES | YES (기존 운영) |
| V4 (정답 엔진) | YES | YES (§8 8/8) | YES (L1→L2) | NO |
| FacilityProfile | YES | YES (null 보존) | YES | — |
| ApplicabilityCondition | YES | YES (14건) | YES | NO |
| ConditionScope | YES | YES (IN/NOT_IN) | YES | — |
| Golden Case | YES | YES (HS2 v1.0) | — (검증도구) | — |
| Validation Engine | YES | YES | — (내부도구) | — |
| Virtual Reality Engine | YES | YES (1000개) | — (내부도구) | — |
| Obligation Metadata | YES | YES (law_name 등 14/14) | **NO** | NO |
| Obligation API | 부분 (bridge 존재) | NO (V4 미연결) | **NO** | ? |
| Frontend Result View | ? (미검증) | NO | NO | ? |
| Runtime Obligation Registry | YES (11건) | NO | **NO (V4와 단절)** | ? (work_order 20,129 운영) |

---

## 핵심 단절점 (체인 검증 결과)

```
V4 (Layer 2)
   │
   ▼  ◀── 끊긴 지점
Obligation (Layer 3)

증거:
  /applicability/evaluate 응답에 obligation 미포함
  코드 주석 "obligation_result 생성 금지"
  runtime_obligation_registry는 V4와 별도 테이블
```

---

## 두 개의 분리된 세계 (재확인)

```
세계 A — V4:
  BUILT YES / VERIFIED YES / CONNECTED(L1-L2) YES / USER_VISIBLE NO
  검증은 끝났으나 화면으로 안 흐름

세계 B — Runtime Obligation:
  BUILT YES / VERIFIED NO / CONNECTED(V4와) NO
  work_order 20,129건 운영되나 V4 verdict가 생성원 아님

두 세계를 잇는 코드 경로 없음 (= 현재 가장 큰 갭)
```

---

## BLOCKED 항목 (별도)

```
Construction (Phase 5):
  상태 BLOCKED
  원인: 별표3 건설업란 원문 부재
  해제조건: 원문(구간표) 확보

Building:
  상태 NOT_STARTED (사실상 BLOCKED 리스크)
  원인: 소방/승강기/에너지 별도 법령군 Appendix 미수집
  Construction과 동일한 원문 확보 문제 재발 가능
```

---

## 현재 로드맵 위치 재산정

```
DONE (검증 완료, 변경 불필요):
  Track A 측정 (FP 93%)
  V4 엔진 (Phase 1~4)
  §8 Golden Case 검증
  Coverage Gap 분석
  거버넌스 문서 (Decision Chain, Policy)
  Obligation Metadata 추적 (14/14 존재 확인)

ACTIVE (지금 실제 갭, 다음 판단 대상):
  V4 → Obligation 연결 (Layer 2→3 단절 해소)
    옵션1: evaluate() 응답에 obligation 필드 추가
    옵션2: V4 ↔ runtime_obligation_registry 연결
  → PROJECT_POLICY §6: 사장님/GPT 판단 후 진행

BLOCKED (주차):
  Construction (별표3 원문)
  Building (별도 법령군 원문)
```

---

## 한 장 요약

```
있는 것 (BUILT):       거의 다 있음 (V4, Obligation 메타, runtime 레지스트리)
검증된 것 (VERIFIED):  V4·§8·Track A 측정까지
연결된 것 (CONNECTED): Layer 1~2까지만 (V4 입력→verdict)
보이는 것 (USER_VISIBLE): Track A 기존 화면만. V4 결과는 아직 안 보임

= 가장 큰 진실:
  "검증은 끝났지만, 검증된 결과가 아직 사용자에게 닿지 않는다."
  이것은 엔진 정확도 문제가 아니라 연결(배선) 문제다.
```

---

## 이 문서가 막는 재발 오류

```
"Obligation Layer 완료" — 철회됨. 메타만 존재, 연결 미완.
"V4 검증됐으니 제품 됐다" — 아님. CONNECTED ≠ USER_VISIBLE.
"데이터 있으니 흐른다" — 아님. 데이터 존재와 호출 경로는 별개.
```
