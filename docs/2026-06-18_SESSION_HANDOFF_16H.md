# 세션 핸드오프 — 16H (§8 1차 완료, Coverage Expansion 진입)

**작성일**: 2026-06-18

---

## 핵심 전환점

```
"정확도 문제" → "커버리지 문제"로 이동
엔진 검증 단계 종료, Coverage Expansion 단계 진입
```

---

## §8 1차 완료 판정 (GPT)

```
§8 = 조건부 완료 (1차)
  케이스 매트릭스 8종 완료
  49/50명 경계, NULL 입력, SCOPE 부재 모두 검증
  C20/H49 고위험군은 필수 아닌 회귀테스트 확대 → 보류
  다음 단계로 이동 확정
```

## GPT 확정 사항

```
1. V4 = Positive Space Engine 유지
   적용 가능한 것만 생성, MUST_NOT 명시 생성 안 함
   (수십만 건 부정판정 방지)

2. V4 ↔ Track A 통합 = 아직 이름
   V4 = 정답 엔진, Track A = 전체 탐색 엔진
   지금 통합하면 Track A 잡음 재유입

3. Track A 93% 오염 = 수정 대상 아닌 비교 기준으로 유지
```

---

## 다음 우선순위 (GPT 판정)

| 순위 | 작업 | 이유 |
|---|---|---|
| 1 | CONSTRUCTION ApplicabilityCondition (공사금액 기반) | contract_amount/sector 입력 이미 존재 |
| 2 | Obligation 생성 | 소비자에게 보여줄 결과 필요 |
| 3 | BUILDING 법령군 | 별도 Appendix 수집 필요 |
| 4 | Boolean/Equipment | 실제 Coverage Gap 확인 시 |
| 5 | Track A 수정 | 가장 뒤 (비교 기준 유지) |

---

## GPT 제안 로드맵

```
Phase 5: CONSTRUCTION 안전관리자 (공사금액 기반)
  ↓
Golden Case Construction 구축
  ↓
CONSTRUCTION 검증
  ↓
Obligation Layer
  ↓
BUILDING 법령군 진입
  ↓
Boolean / Equipment / Process (Coverage Gap 확인 시)
```

---

## 다음 세션 시작점

```
WO-V4-PHASE5-001: CONSTRUCTION 안전관리자 ApplicabilityCondition

설계 (GPT 이전 판정):
  scope_type = SECTOR, scope_values = ["CONSTRUCTION"]
  metric = METRIC:CONSTRUCTION_AMOUNT
  공사금액 구간별 required_count
  → 산안법 시행령 별표3 건설업 조항 원문 확인 필요 (임의 구간 금지)

선행 작업:
  C1 평가기가 SECTOR scope_type + CONSTRUCTION_AMOUNT metric을
  평가할 수 있는지 condition_scope_service 확인
```

---

## 절대 금지 (유효)

```
Track A 수정
GPT 전속 테이블 수정
factories 구조 변경
Obligation 즉시 생성 (Phase 5 완료 전)
BUILDING/Boolean/Equipment 선행 구현
공사금액 임의 구간 확정 (원문 확인 전)
```
