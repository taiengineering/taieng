# WO-ARCHITECTURE-FREEZE-001
# Architecture Freeze — 프로젝트 헌법

**작성일:** 2026-06-25 | **상태:** 동결 선언 (최상위 헌법)
**상위 효력:** 이 문서는 TAI Safe 엔진 아키텍처의 최상위 규범이다.
**구성 헌법:**
- docs/WO-BOUNDARY-LOCK-001_경계동결.md (책임 경계)
- docs/WO-DATA-CONTRACT-001_데이터계약.md (데이터 계약)

**이번 WO는 기능 추가가 아니다.** DB 변경 없음 / API 변경 없음 / 서비스 코드 없음.
**목적:** Boundary 변경을 금지하고, 변경 절차를 정의한다.

> 이후 프로젝트는 "구조 개발"에서 "품질 개발"로 전환한다.
> 향후 작업은 원칙적으로 Applicability Engine 내부 품질 향상만 수행한다.

---

## TASK-001: Freeze 대상 (공식 Architecture 선언)

```
아래 구조를 TAI Safe 공식 Architecture로 선언하고 동결한다:

  Input (facility_profiles)
      ↓
  Applicability Engine        ① 의무 생성
      ↓
  obligation_instance
      ↓
  Glue Adapter                ② 순수 변환
      ↓
  45CM Check Engine (API)      ③ 근거 역추적 (GPT 소관)
      ↓
  Check Layer                 ④ 6하원칙 + 필요값
      ↓
  Refinement Layer            ⑤ 중복/병합/정제
      ↓
  Result

이 구조 외의 데이터 흐름은 존재하지 않는다.
경로 추가/우회/단락(short-circuit)은 Breaking Change다.
```

---

## TASK-002: Boundary 변경 규칙

```
Boundary는 아래 5조건을 모두 만족하지 않는 한 변경 불가:

  ① 기존 Data Contract로 해결 불가능
  ② Adapter에서 흡수 불가능
  ③ 두 개 이상의 Layer 수정이 반드시 필요
  ④ 변경 효과가 기존 구조보다 명확히 우수
  ⑤ Architecture Review 승인 완료

→ 하나라도 불만족 시 Boundary 변경 금지.
→ 대부분의 요구는 ① 또는 ② 단계에서 해소된다 (변경 불필요).
```

---

## TASK-003: Data Contract 변경 규칙

```
허용 (유일):
  ✅ 신규 Optional Field 추가
     (받는 쪽이 없어도 동작하는 선택 필드만)

금지:
  ❌ 필드 삭제
  ❌ 필드 의미 변경
  ❌ 기존 필수 필드 제거
  ❌ Layer 간 책임 이동

→ Optional 추가조차 WO-DATA-CONTRACT-002 등 개정 WO로 기록.
→ 받는 쪽은 여전히 계약 필수 필드만 신뢰.
```

---

## TASK-004: Layer 추가 규칙

```
원칙: 새 Layer 추가 금지.

추가 가능 조건 (모두 만족):
  - 기존 Layer 책임을 침범하지 않음
  - 새로운 책임이 독립적으로 존재
  - 기존 Adapter로 흡수 불가능

허용 예시 (독립 책임):
  ✅ Audit Layer     (감사 — 기존 흐름 관찰만)
  ✅ Analytics Layer (분석 — 기존 흐름 비침범)

금지 예시 (기존 책임 복제):
  ❌ Applicability 2
  ❌ Check Engine 2
  ❌ Refinement 2

→ "기존 레이어를 하나 더" 는 항상 금지.
→ 추가 레이어는 읽기 전용 곁가지여야 한다.
```

---

## TASK-005: Engine 변경 규칙 (레이어별 권한)

```
① Applicability Engine
  변경 가능: Trigger / UNIVERSAL / THRESHOLD / EXISTS / Coverage / Confidence
  변경 금지: Check / 6W / Refinement / Result Format
  → 향후 대부분의 작업이 여기서 일어난다 (품질 개발의 주 무대).

③ Check Engine (GPT 소관)
  변경 가능: 근거 추적 / Draft 판정 / Evidence
  변경 금지: Applicability / Trigger / Threshold / UNIVERSAL
  → TAI(Claude)는 이 레이어 무수정 (호출만).

④ Check Layer
  변경 가능: 6W / 필요자료 / 증빙
  변경 금지: Applicability / Verdict

⑤ Refinement Layer
  변경 가능: Grouping / Merge / 표현 / Category
  변경 금지: Applicability / Verdict / Evidence
```

---

## TASK-006: Breaking Change 절차

```
Breaking Change(경계/계약/레이어 변경)는 반드시 아래 절차:

  제안
    ↓
  Architecture Review      (이 헌법 위반 여부 판정)
    ↓
  Boundary Impact          (어느 경계가 흔들리는가)
    ↓
  Data Contract Review     (필드 영향 분석)
    ↓
  승인                     (5조건 충족 확인)
    ↓
  구현

→ Architecture Review 없이 구조 변경 금지.
→ 절차를 건너뛴 변경은 무효 (롤백 대상).
```

---

## TASK-007: 신규 WO 시작 규칙 (Boundary Check 템플릿)

```
모든 신규 WO 첫머리에 아래 Boundary Check를 작성한다:

┌─────────────────────────────────────────┐
│ Boundary Check                            │
│                                           │
│  Applicability 내부 작업인가?    YES / NO │
│  Boundary 변경 필요한가?         YES / NO │
│  Data Contract 변경 필요한가?    YES / NO │
│  Breaking Change인가?            YES / NO │
└─────────────────────────────────────────┘

판정:
  - "Applicability 내부 = YES, 나머지 전부 NO"
    → 일반 작업. 바로 진행. (대부분 여기에 해당)
  - 나머지 중 YES가 하나라도 있으면
    → Architecture Review 먼저 수행 (TASK-006 절차).
```

---

## TASK-008: 성공 기준

```
다음 5개 질문에 즉시 답할 수 있으면 Freeze 성공:

  1. 이 기능은 어느 Layer인가?
     → 의무개수=① / 변환=② / 판정=③ / 6W=④ / 표현=⑤

  2. Boundary를 변경하는가?
     → TASK-002의 5조건 점검

  3. Data Contract를 변경하는가?
     → TASK-003 (Optional 추가만 허용)

  4. Adapter로 해결 가능한가?
     → 가능하면 Boundary 변경 불필요

  5. Breaking Change인가?
     → 맞으면 TASK-006 절차

→ 5개 즉답 가능 = Freeze 성공.
```

---

## 완료 기준: 단계 전환 선언

```
본 헌법 발효로 프로젝트는 전환된다:

  "구조 개발" (Structure)  →  "품질 개발" (Quality)

향후 작업 원칙:
  - 원칙적으로 Applicability Engine 내부 품질 향상만 수행
  - Boundary / Contract / Layer는 본 헌법 기준으로 유지
  - 구조를 다시 여는 것은 Breaking Change (Review 필수)

품질 개발 주요 영역 (전부 ① Applicability 내부):
  - UNIVERSAL 215 HARVESTED 추가 정제
  - THRESHOLD 별표(appendix) 임계값 확장
  - EXISTS 입력 수집 (facility_profiles has_*)
  - Coverage / Confidence 개선
  → 어느 것도 Boundary/Contract를 건드리지 않는다.
```

---

## 헌법 체계 (3문서)

```
WO-ARCHITECTURE-FREEZE-001 (본 문서)   ← 최상위: 변경 절차 + 동결 선언
  ├─ WO-BOUNDARY-LOCK-001              ← 책임: 누가 무엇을 하나
  └─ WO-DATA-CONTRACT-001             ← 데이터: 무엇이 넘어가나

세 문서가 충돌 시 본 문서(FREEZE)가 절차상 우선.
실제 책임/필드 내용은 하위 두 문서가 정의.
```

---

*WO-ARCHITECTURE-FREEZE-001. 프로젝트 헌법 — Architecture Freeze.*
*구조 개발 → 품질 개발 전환 선언. Boundary 변경은 5조건+Review 필수.*
*신규 WO는 Boundary Check로 시작. 대부분 Applicability 내부 작업.*
*핵심: 이후 구조를 다시 여는 것은 Breaking Change다.*
