# OBLIGATION LAYER DESIGN REPORT V1
# WO-OBLIGATION-LAYER-DESIGN-001

**작성일**: 2026-06-18
**성격**: 설계 검토. 구현/테이블생성/API수정/엔진수정 없음.
**근거**: PROJECT_POLICY §6 (발견→측정→기록→비교→승인→진행)

---

## 1. Obligation Layer 목적

```
현재 V4 출력: MATCH / NOT_MATCH / NOT_APPLICABLE / UNKNOWN
현재 사용자 가치: 없음

사용자는 "MATCH 1건"이 아니라 "무엇을 해야 하는가"를 원한다.

변환 계층:
  ApplicabilityCondition
      ↓
  Evaluation Result (MATCH 등)
      ↓
  Obligation (의무 = 사용자가 할 일)
      ↓
  사용자 문장
```

---

## 2. Obligation 최소 구조 (제안)

```
obligation_type   : 의무 유형 (예: DESIGNATION, EDUCATION, HEALTH_CHECK)
title             : 의무명 (예: "안전관리자 선임")
legal_basis       : 근거 법령 (예: "산업안전보건법 시행령 별표3")
reason            : 적용 이유 (예: "제조업(C28), 상시근로자 280명")
required_action   : 권장 조치 (예: "안전관리자 1명 선임")
required_count    : 필요 수량 (V4에 이미 존재)
```

이 중 V4가 **이미 가진 것** / **없는 것**을 구분해야 한다.

---

## 3. MUST 8건 적용 가능 여부 (실측 기반)

현재 applicability_conditions가 가진 컬럼:
```
✅ 있음: industry_name, threshold_value, operator, required_count,
         metric, sector, scope_type, scope_operator
❌ 없음: legal_basis (근거 법령 조문)
❌ 없음: required_action (사용자 행동 문구)
❌ 없음: obligation_title (의무명 — industry_name으로 대체 가능하나 부정확)
```

MUST 8건별 변환 가능성:

| 의무 | V4 보유 정보 | 부족한 정보 |
|---|---|---|
| 안전관리자 선임 | threshold, required_count, scope | legal_basis, required_action |
| 관리감독자 지정 | threshold=1, required_count=1 | legal_basis, required_action |
| 정기 안전보건교육 | threshold=1 | legal_basis, required_action, 주기 |
| 신규채용자 교육 | threshold=1 | legal_basis, required_action |
| 일반건강진단 | threshold=1 | legal_basis, required_action, 주기 |
| 위험성평가 | threshold=1 | legal_basis, required_action |
| 작업내용 변경 교육 | threshold=1 | legal_basis, required_action |
| 경보용 설비 설치 | threshold=50 | legal_basis, required_action |

**핵심: 8건 모두 "판정"은 되지만 "사용자 문장"에 필요한 2개 요소(legal_basis, required_action)가 없다.**

---

## 4. 사용자 화면 예시 (목표)

```
[안전관리자 선임 필요]
  근거: 산업안전보건법 시행령 별표3
  적용 이유: 제조업(C28), 상시근로자 280명
  권장 조치: 안전관리자 1명 선임
```

현재 V4 결과만으로 생성 가능한 부분:
```
[안전관리자 선임 필요]          ← industry_name으로 일부 가능
  근거: ???                     ← legal_basis 없음 (생성 불가)
  적용 이유: 제조업(C28), 280명  ← factory 입력 + threshold로 생성 가능
  권장 조치: ???                ← required_action 없음 (생성 불가)
```

즉 4줄 중 2줄(적용 이유, 제목 일부)은 생성 가능, 2줄(근거, 권장 조치)은 데이터 부족.

---

## 5. V4 결과와 연결 가능성 판정

```
생성 가능 (현재 데이터로):
  - 의무 발생 여부 (MATCH → 의무 있음)
  - 적용 이유 (업종 + 인원, factory 입력에서)
  - 필요 수량 (required_count)

생성 불가 (데이터 부족):
  - legal_basis (근거 법령 조문 텍스트)
  - required_action (구체적 권장 조치 문구)
```

---

## 최종 판정: 조건부 GO

```
GO 가능한 범위:
  "의무 있음 + 적용 이유 + 필요 수량"까지는
  현재 V4 데이터만으로 사용자 문장 생성 가능

BLOCKED 되는 범위:
  "근거 법령 + 권장 조치"는 데이터 부족
  → 단, 이건 Construction처럼 "원문 부재"가 아님
  → applicability_conditions에 legal_basis / required_action
     컬럼을 추가하고 8건에 값을 채우면 해결 (소규모 작업)
  → 8건은 이미 사장님이 판정한 항목이라 값 입력 가능
```

**결론: GO (단계적)**

```
1단계 (즉시 가능):
  현재 데이터로 "의무명 + 적용 이유 + 수량" 표시
  → 사용자가 "무엇이 해당되는가"는 이해 가능

2단계 (소규모 보강 후):
  legal_basis / required_action 값 8건 입력
  → "근거 + 권장 조치"까지 완전한 문장 생성
  → 이것은 Construction 같은 Block이 아니라
     8건 수동 입력으로 해결되는 작업
```

---

## 6. 구현 착수 가능 여부

```
GO. 단 PROJECT_POLICY §6에 따라 즉시 구현 아님.

다음 단계 (승인 후):
  WO-OBLIGATION-LAYER-IMPL-001 (실제 구현)
    - obligation 표현 구조 확정
    - legal_basis / required_action 8건 값 정의 (사장님 판정 항목)
    - V4 Evaluation Result → Obligation 변환 로직

부족 데이터 규명 완료:
  legal_basis 8건, required_action 8건
  → 새 법령 수집 아님 (이미 검증된 8건의 메타 정보)
  → 사장님이 이미 MUST로 판정한 항목이므로 값 확정 가능
```

---

## 결론 요약

```
질문: 현재 V4 결과만으로 사용자가 이해할 수 있는 결과를 만들 수 있는가?

답: GO (조건부)
  - "의무 있음 + 이유 + 수량" → 즉시 가능
  - "근거 + 권장 조치" → legal_basis/required_action 8건 입력 후 가능
  - 이 입력은 Block이 아닌 소규모 보강 (검증된 8건 메타)

다음: WO-OBLIGATION-LAYER-IMPL-001 (사장님 승인 시)
```
