# NEXT PRIORITY SELECTION REPORT V1
# WO-NEXT-PRIORITY-SELECTION-001

**작성일**: 2026-06-18
**성격**: 우선순위 재산정. 새 방향/엔진/로드맵 변경 없음.
**근거 문서**: PROJECT_DECISION_CHAIN_V1, PROJECT_POLICY_VIRTUAL_REALITY_ENGINE_V1, 기획서 v2.1

---

## 전제: Construction = 주차(Parking) 상태

```
Construction은 BLOCKED.
BLOCKED는 "계속 파고드는 상태"가 아니라 "주차 상태"다.

재탐색 금지 (다음 조건 전까지):
  - 별표3 건설업란 원문 확보
  - 신규 데이터 확보
  - 사장님 명시 지시

이번 WO에서 Construction 관련 신규 분석/WO 생성 없음.
```

---

## 진행 가능한 후보 (기획서 로드맵 내, Block 없음)

현재 DB 상태 확인:
```
INDUSTRIAL conditions: 14건 (검증 완료)
CONSTRUCTION conditions: 0건 (BLOCKED)
BUILDING conditions: 0건 (원문 확보 리스크)
```

진행 가능한 후보는 Block이 없는 것만 추출:

| 후보명 | 목적 | 예상 효과 | 성공확률 | Block 여부 | 비고 |
|---|---|---|---|---|---|
| **A. Obligation Layer** | V4 INDUSTRIAL MUST 8건을 소비자에게 문장으로 표시 | 검증된 결과가 처음으로 사용자 가치로 전환 | **높음** | 없음 | 이미 검증된 데이터 사용 |
| **B. INDUSTRIAL 의무 확장** | 보건관리자/안전보건관리담당자 등 추가 의무 | INDUSTRIAL 커버 의무 수 증가 | 중간 | 없음 | 기존 구조 재사용, 단 새 조건 정답지 필요 |
| **C. Golden Case 확대** | C20/H49 등 고위험 업종 정답지 추가 | 회귀 테스트 세트 강화 | 중간 | 없음 | 가치는 간접적(검증 강화) |
| **D. Track A 비교 자동화** | Track A vs V4 diff를 자동 측정 | FP 측정 표본 확대(현재 표본 1) | 중간 | 없음 | 가치는 간접적(측정 신뢰도) |
| **E. V4 결과 표현 정제** | UNKNOWN 3유형을 사용자 메시지로 표현 | 사용자가 "왜 판단 불가"인지 이해 | 중간 | 없음 | Obligation Layer와 일부 중복 |

---

## 후보별 평가 상세

### A. Obligation Layer
```
가치:    높음 — 검증된 MUST 8건이 처음으로 화면에 표시됨
            (지금까지의 모든 검증이 사용자 가치로 전환되는 지점)
난이도:  낮음 — 데이터는 이미 있음, 표현 레이어만 추가
성공확률: 높음 — Block 없음, 정답지 이미 존재
의존성:  V4 INDUSTRIAL (완료됨)
```

### B. INDUSTRIAL 의무 확장
```
가치:    중간 — 커버 의무 증가하나 이미 8건 검증됨
난이도:  중간 — 새 의무마다 Golden Case 정답지 필요
성공확률: 중간 — 정답지 구축 작업이 선행되어야 함
의존성:  새 의무별 정답지 (미구축)
```

### C. Golden Case 확대
```
가치:    간접 — 회귀 테스트 강화 (사용자 직접 가치 아님)
난이도:  중간 — 업종별 정답지 수동 판정 필요
성공확률: 중간
참고:    §8 1차 완료 시 "회귀 테스트 세트 확대"로 분류됨 (필수 아님)
```

### D. Track A 비교 자동화
```
가치:    간접 — FP 측정 표본 확대 (현재 표본 1 → N)
난이도:  중간 — 자동 diff 파이프라인 필요
성공확률: 중간
참고:    측정 신뢰도는 올라가나 사용자 가치는 간접적
```

### E. V4 결과 표현 정제
```
가치:    중간 — UNKNOWN 이유를 사용자에게 설명
난이도:  낮음
성공확률: 높음
참고:    Obligation Layer(A)와 표현 레이어에서 중복 → A에 흡수 가능
```

---

## 최종 우선순위 (Priority 1~3만)

```
Priority 1: A. Obligation Layer
  근거: 가치 최고 + 난이도 최저 + 성공확률 최고 + Block 없음
        검증된 MUST 8건을 사용자 가치로 전환하는 첫 지점
        (E. 결과 표현 정제는 여기에 흡수)
  ※ WO-DECISION-CHAIN-001의 P1과 일치

Priority 2: B. INDUSTRIAL 의무 확장
  근거: Block 없음, 기존 구조 재사용
        단 새 의무별 정답지 구축이 선행 필요
  ※ WO-DECISION-CHAIN-001의 P2와 일치

Priority 3: C. Golden Case 확대 / D. Track A 비교 자동화 (측정 강화)
  근거: 둘 다 검증 신뢰도를 높이나 사용자 직접 가치는 간접적
        Priority 1~2 진행 중 병행 가능한 보조 작업
```

---

## 로드맵 정합성 확인

```
이 우선순위는 기획서·Decision Chain을 변경하지 않는다.
WO-DECISION-CHAIN-001이 지정한 P1(Obligation)/P2(Industrial)와 일치.

PROJECT_POLICY 준수:
  - 새 방향 제안 없음 ✅
  - 새 엔진 제안 없음 ✅
  - 로드맵 변경 없음 ✅
  - 기획서 안에서 가장 성공확률 높은 다음 작업만 선정 ✅
```

---

## 결론

```
다음 작업: Priority 1 = Obligation Layer

이유:
  검증은 충분히 했다 (§8 8/8, MUST 100%).
  이제 그 검증 결과를 사용자에게 보여줄 차례다.
  Block 없고, 데이터 있고, 정답지 있고, 성공확률 가장 높다.

단, PROJECT_POLICY §6에 따라:
  Obligation Layer도 "즉시 구현"이 아니라
  검토 WO부터 시작한다 (발견→측정→기록→비교→승인→진행).
```
