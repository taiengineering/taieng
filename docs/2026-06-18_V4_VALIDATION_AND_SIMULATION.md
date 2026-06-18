# V4 검증 및 시뮬레이션 운영계획
# (V4 Validation & Simulation Operating Plan)

**작성일**: 2026-06-18  
**문서 성격**: 개발 문서 아님. 검증 운영 문서.  
**기준 기획서**: docs/2026-06-11_LEGAL_ENGINE_V4_LAYER_REDESIGN.md (v2.1) — **수정하지 않음**

---

## 문서 목적

이 문서는 V4 엔진을 개발하기 위한 문서가 아니다.  
V4 엔진을 **검증하는 체계**를 정의한다.

기존 V4 기획서는 그대로 유지되고,  
최근 확립된 §8 / Golden Case / 가상현실 엔진을 공식 프로세스로 편입한다.

**최종 목표**: 엔진을 더 만드는 것이 아니라, 검증된 규칙만 엔진에 반영하는 체계를 만드는 것.

---

## 1. 현재 상태 요약

| 단계 | 내용 | 상태 |
|---|---|---|
| Phase 1 | FacilityProfile (TriValue + Provenance) | ✅ 완료 |
| Phase 2 | ApplicabilityCondition 파일럿 | ✅ 완료 |
| Phase 3 | ConditionScope Layer | ✅ 완료 |
| Phase 4 | Real Facility Validation | ✅ INDUSTRIAL 10/10 |
| §8 | Golden Case Validation | ✅ 1차 완료 (케이스 8/8) |

### §8 최종 측정값

```
Track A False Positive: 93% (화성 제2공장 114건 중 106건 MUST_NOT)
  원인: SUBJECT_UNRESOLVED actor 미분류

V4 MUST 커버율: 12.5% → 100% (WO-01 후)
  C1 코드 수정: 0줄 (condition_scopes 데이터 추가만)

UNKNOWN 3유형 구분:
  SCOPE UNKNOWN (건설/건물)
  METRIC UNKNOWN (빈 입력)
  NOT_APPLICABLE (업종 범위 외)
```

---

## 2. 현재 확보된 자산

| 자산 | 역할 | 상태 |
|---|---|---|
| **Track A** | 현행 운영 엔진 (전체 탐색) | 운영 중, 수정 금지 (비교 기준) |
| **V4** | 신규 법령 엔진 (정답 엔진) | INDUSTRIAL 검증 완료 |
| **Golden Case** | 정답지 (MUST / MUST_NOT) | HS2 v1.0 확정 |
| **Simulation Engine** | 가상 사업장 생성기 | 목업 30건 + 경계값 생성 경험 확보 |

### Golden Case 현황

```
GOLDEN_CASE_HS2 v1.0 (화성 제2공장 C28 280명)
  MUST 8건
  MUST_CANDIDATE 15건
  MUST_NOT 43건

GOLDEN_CASE_MFG49 v1.0 (49명 경계값)
```

---

## 3. 검증 철학

```
금지:
  발견 → 즉시 수정

반드시:
  발견 → 영향 분석 → 우선순위 → 수정
```

15차까지 반복된 실패 루프(발견→수정→발견→수정)를 차단한다.  
부분 최적화 금지. 시작부터 결과까지 전체 파이프라인을 본다.

---

## 4. 검증 루프

```
가상 사업장 생성
  ↓
V4 평가
  ↓
Golden Case 채점
  ↓
점수 계산 (TP/FP/FN/Unknown)
  ↓
100점 후보 식별
  ↓
반영 검토 (즉시 수정 아님)
```

---

## 5. 점수 체계

| 지표 | 정의 |
|---|---|
| **True Positive (TP)** | MUST에 있고 엔진도 MATCH |
| **False Positive (FP)** | MUST_NOT인데 엔진이 MATCH (오염) |
| **False Negative (FN)** | MUST인데 엔진이 놓침 (누락) |
| **Unknown** | 입력 부족 또는 Scope 미구현으로 판단 보류 |

### 현재 측정 (화성 제2공장)

```
Track A:  TP 극소, FP 106건 (93%)
V4:       TP 8건 (MUST 100%), FP 0건, FN 0건
```

V4는 Positive Space Engine이므로 구조적으로 FP=0.  
적용 가능한 것만 생성하고 MUST_NOT은 원천적으로 만들지 않는다.

---

## 6. Golden Case 운영 전략

```
현재:
  HS2 (제조업 280명) ✅
  MFG49 (제조업 49명) ✅

향후 확장:
  Industrial — 고위험군(C20, H49 등) 회귀 세트
  Construction — 공사금액 구간별
  Building — 용도별 (별도 법령군)
```

Golden Case는 정확도 측정의 기준선.  
새 Golden Case 없이 엔진 확장 금지.

---

## 7. 가상현실 엔진 역할

```
실제 사용자 반응을 기다리지 않는다.
시간을 압축한다.
대량 사업장을 생성한다.
입력 분포를 시뮬레이션한다.
법령 결과를 검증한다.
```

경계값(49/50), NULL 입력, SCOPE 부재 등을  
실사용자 없이 재현하여 엔진 반응을 미리 관찰.

---

## 8. 우선순위 결정 기준

```
새 기능 추가 금지
측정 우선

구현 검토 조건 (4개 모두 만족 시에만):
  1. Golden Case 존재
  2. 재현 가능
  3. 영향도 측정 완료
  4. 우선순위 상위
```

---

## 9. 현재 보류 목록

```
Boolean 연결
Equipment 연결
Process 연결
CONSTRUCTION Scope 확장
BUILDING Scope 확장
Obligation 생성
Track A 수정
```

모두 "측정 완료 + Golden Case 존재 + 우선순위 상위" 조건을 만족할 때까지 보류.

단, GPT 1순위 판정(CONSTRUCTION ApplicabilityCondition)은  
별도 WO(WO-V4-PHASE5-001)로 진행하되, 그 전에  
Golden Case Construction을 먼저 구축한다.

---

## 10. 다음 단계

```
가상 사업장 생성 전략 수립
Golden Case 자동 채점 체계
V4 점수 대시보드
영향도 측정
우선순위 재산정
```

---

## 부록: 연결 문서

```
기준 기획서 (수정 금지):
  docs/2026-06-11_LEGAL_ENGINE_V4_LAYER_REDESIGN.md

검증 산출물:
  docs/validation/GOLDEN_CASE_HS2_v10.md
  docs/validation/GOLDEN_CASE_MFG49_v10.md
  docs/validation/GOLDEN_CASE_HS2_LLM_REVIEW_v03.md

세션 핸드오프:
  docs/2026-06-18_SESSION_HANDOFF_16H.md
```

---

**본 문서는 검증 운영 문서이다. 설계 변경 판단을 포함하지 않는다.**
