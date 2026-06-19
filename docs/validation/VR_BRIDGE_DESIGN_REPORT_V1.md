# VR BRIDGE DESIGN REPORT V1
# WO-VR-BRIDGE-DESIGN-001

**작성일**: 2026-06-19
**성격**: 설계 전용. 구현/시뮬레이션 실행/가상 사업장 생성 없음.
**정합성**: VR Engine = PROJECT_POLICY Level 4 (가설 검증, 로드맵 변경권 없음).
            이 WO는 검증 도구를 정식화하는 것이지 로드맵 변경이 아님.

---

## 목표 구조 (한 페이지)

```
Factory Input
     ↓
  ┌──────┐        ┌──────┐
  │  V4  │        │  VR  │
  └──────┘        └──────┘
     ↓               ↓
  verdict+obl    verdict+obl (대량)
     └──────┬────────┘
            ↓
       Comparison (verdict 단위)
            ↓
       Simulation Report
```

핵심: V4와 VR이 **같은 입력 계약**을 먹고 **같은 출력 계약**을 뱉어야
비교가 성립한다. 이 WO는 그 "같은 계약"을 고정한다.

---

## Step 1 — V4_INPUT_CONTRACT_V1

V4 evaluate가 실제로 소비하는 입력 (applicability_api.evaluate + FacilityProfile 기준):

```
필수 입력:
  factory_id (uuid)
    → factories 조회 → build_facility_profile()

FacilityProfile이 추출하는 평가 입력 (실제 사용분):
  ksic_code        (업종, scope 평가용)   — PRESENT/ABSENT/UNKNOWN 3-state
  regular_workers  (상시근로자 수)         — {state, value}
  sector           (INDUSTRIAL/BUILDING/CONSTRUCTION)

선택 입력:
  save (bool, default False) — 저장 여부 (평가 결과엔 영향 없음)

UNKNOWN 발생 조건 (3유형, §8에서 확정):
  SCOPE UNKNOWN     : ksic null/미해석 → scope 평가 불가
  METRIC UNKNOWN    : regular_workers.state=UNKNOWN → 수치 비교 불가
  NOT_APPLICABLE    : scope 범위 외 (해당 업종 아님)

입력 정규화 규칙:
  null → 0 자동매칭 금지 (UNKNOWN 보존)
  state 3-state 유지 (PRESENT/ABSENT/UNKNOWN)
  MANUFACTURING → INDUSTRIAL (sector 정규화)
```

산출물 위치: 이 문서 §Step1 (별도 파일 불필요, 계약은 짧음)

---

## Step 2 — V4_OUTPUT_CONTRACT_V1

V4 evaluate가 실제 반환하는 출력 (applicability_api.evaluate 반환 dict):

```
verdict 레벨:
  verdict          : REQUIRED / NOT_REQUIRED / UNKNOWN
  required_count   : 정수
  matched_conditions : [reason 문자열]

evaluation_details[] (condition 단위):
  condition_id
  evaluation_result : MATCH / NOT_MATCH / NOT_APPLICABLE / UNKNOWN
  evaluation_reason
  industry_name / threshold_value / operator / required_count
  scope_result / scope_reason
  input_state / input_value

obligation 레벨 (Adapter 경유, V4 직접 아님):
  ※ V4 evaluate 자체는 obligation 미생성 ("obligation_result 생성 금지")
  ※ Adapter(build_obligations_from_v4)가 추가:
     obligations[]: id/category/title/law_name/law_article
                    /rule_type/risk_level/description/evidence/required_count

비교에 쓰는 핵심 단위:
  (condition_id, evaluation_result) ← 이게 비교의 기본 키
```

---

## Step 3 — VR_INPUT_CONTRACT_V1

```
Q1 답: VR Engine은 V4 입력만으로 실행 가능한가?
  → YES (조건부).
  VR은 "가상 사업장"을 생성하지만, 각 가상 사업장은
  결국 V4_INPUT_CONTRACT (ksic/regular_workers/sector)로 환원된다.
  즉 VR의 출력 = V4 입력 계약의 인스턴스 다발.

Q2 답: 추가 입력이 필요한가?
  → VR 고유 입력 1개만 추가:
     generation_spec (생성 명세)
       : sector 분포 / ksic 후보 / worker_count 범위 / 표본 수
     → 이건 "어떤 가상 사업장을 몇 개 만들지"의 명세이지
       V4 평가 입력이 아님. V4엔 안 들어감.

VR_INPUT_CONTRACT_V1:
  입력:  generation_spec (VR 고유)
  생성:  [FacilityProfile 인스턴스] (= V4 입력 계약 다발)
  제약:  생성된 각 인스턴스는 반드시 V4_INPUT_CONTRACT 준수
         (ksic/regular_workers/sector, 3-state 보존)
  기존 자산 재사용:
    - 가상 사업장은 P4_ 접두사 + is_active=false (메모리 규약)
    - generate_series + CROSS JOIN으로 SQL 재현 (API 미호출)
```

---

## Step 4 — SIMULATION_COMPARISON_CONTRACT_V1

```
비교 단위: (condition_id, evaluation_result)
  V4 결과:  {condition_id → MATCH/NOT_MATCH/NOT_APPLICABLE/UNKNOWN}
  VR 결과:  {condition_id → 동일 4-verdict}

비교 방식 (4-verdict 매트릭스):
  AGREE        : V4 == VR (같은 verdict)
  DISAGREE     : V4 != VR (다른 verdict) ← 조사 대상
  세부 분류:
    V4=MATCH,    VR=NOT_MATCH  → VR이 과소판정
    V4=NOT_MATCH,VR=MATCH      → VR이 과대판정 (False Positive 후보)
    V4=KNOWN,    VR=UNKNOWN    → VR 입력 결손
    V4=UNKNOWN,  VR=KNOWN      → V4 입력 결손

Golden Case 연계:
  Golden Case(MUST/MUST_NOT)가 있는 사업장은
  V4·VR 둘 다 Golden과도 비교 → 3자 비교(V4/VR/Golden) 가능
  (단 이번 WO는 계약 정의만, 실행 안 함)

집계 지표 (정의만):
  agreement_rate = AGREE / 전체
  disagree_breakdown = {과소/과대/입력결손} 분포
  ※ 이건 분포(distribution)이지 영향도(impact) 아님 — 혼동 금지
    (PROJECT_POLICY 학습: 분포≠영향도)
```

---

## 필수 질문 답변

```
Q1. VR Engine은 V4 입력만으로 실행 가능한가?
  → YES. VR이 만드는 가상 사업장은 V4 입력 계약
    (ksic/regular_workers/sector)으로 환원됨.

Q2. 추가 입력이 필요한가?
  → generation_spec 1개만 (VR 고유, "무엇을 몇 개 만들지").
    V4 평가 입력엔 안 들어감.

Q3. 비교 결과는 어디에 저장하는 것이 맞는가?
  → 후보 2개:
    (a) 신규 테이블 simulation_comparison_result
        : V4 vs VR verdict diff 저장
    (b) 파일/문서 (taieng/docs) — 1회성 검증이면 충분
  → 권장: 초기엔 (b) 문서. 반복 운영 시 (a) 테이블.
    ※ 이번 WO는 계약만, 저장 구현 안 함.
    ※ 저장 위치 확정은 실행 WO에서 (DDL 사전점검 후).

Q4. 현재 구조에서 가장 작은 연결점은 무엇인가?
  → (condition_id, evaluation_result) 페어.
    V4도 VR도 이 단위로 결과를 내므로,
    이 페어만 맞추면 비교가 성립한다.
    = 가장 작은 브리지 = "condition_id 기준 verdict 정렬".
```

---

## 한 페이지 결론 (완료 기준)

```
무엇을 넣고:
  V4 = factory_id → FacilityProfile (ksic/regular_workers/sector, 3-state)
  VR = generation_spec → 가상 FacilityProfile 다발 (V4 입력 계약 준수)

무엇을 받고:
  양쪽 모두 → {condition_id: evaluation_result(4-verdict)} + verdict 집계
  obligation은 Adapter 경유 (V4 직접 아님)

무엇을 비교할지:
  비교 키 = (condition_id, evaluation_result)
  비교 방식 = 4-verdict 매트릭스 (AGREE/DISAGREE + 과소/과대/입력결손)
  Golden Case 있으면 3자 비교 가능

가장 작은 연결점:
  condition_id 기준 verdict 정렬 1개.
  V4·VR이 이미 같은 단위를 내므로 추가 엔진 불필요.
```

---

## 원칙 준수

```
설계 전용, 구현/시뮬레이션 실행/가상사업장 생성 0 ✅
VR Engine = Level 4 (로드맵 변경권 없음) 정합 ✅
새 엔진/법령수집/UI/결과페이지 안 건드림 ✅
Construction/Building/Authorization 안 건드림 ✅
분포≠영향도 구분 명시 (PROJECT_POLICY 학습 반영) ✅
저장 위치는 실행 WO로 미룸 (DDL 사전점검 원칙) ✅
```

---

## 다음 (실행 WO 후보, 사장님 승인 시)

```
WO-VR-BRIDGE-IMPL-001:
  - generation_spec 1개로 가상 사업장 N개 SQL 생성 (P4_, is_active=false)
  - V4 로직 SQL 재현 + VR 결과 → (condition_id, verdict) 페어
  - 4-verdict 매트릭스 비교 → DISAGREE 추출
  - Golden Case 있으면 3자 비교
  ※ 단 PROJECT_POLICY: VR 결과로 로드맵 변경 금지.
    비교는 "V4 정확도 측정 도구"로만 사용.
```
