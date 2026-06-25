# WO-COVERAGE-GAP-001
# Applicability Engine Coverage Report (품질 기준점)

**작성일:** 2026-06-25 | **상태:** 완료 (읽기 전용 측정 — ① Applicability 내부)
**헌법:** WO-ARCHITECTURE-FREEZE-001 준수

## Boundary Check (헌법 TASK-007)

```
Applicability 내부 작업인가?    YES  (Coverage 측정)
Boundary 변경 필요한가?         NO
Data Contract 변경 필요한가?    NO
Breaking Change인가?            NO
→ 전부 통과. 읽기 전용.
```

---

## 결론 먼저 (Coverage Baseline 확정)

```
산안법 4법 Coverage = 20.4% (444 / 2,174 조문)

법령별:
  산업안전보건기준에 관한 규칙  30.9%  (395/1,277)  ← 작업·설비 안전
  산업안전보건법                 8.3%  ( 33/  398)  ← 의무 근거
  산업안전보건법 시행령          4.9%  (  4/   81)  ← 선임·조직
  산업안전보건법 시행규칙        2.9%  ( 12/  418)  ← 서류·절차

→ 이것이 품질 개선의 기준점.
→ 기준규칙(현장 안전)은 31% 커버, 절차·서류법은 한 자릿수.
→ 앞으로 이 숫자가 올라가는 게 품질 개발의 척도.
```

> ⚠️ 분모 주의: 전체 semantic_clause 58,495(OBLIGATION 29,665)에는
> 수백 개 타 법령(건축/의료/환경/재난법)이 섞여 있다.
> 진짜 분모는 산안법 4법(2,174). 1.4% 같은 숫자는 오해.

---

## TASK-001: CONFIRMED 유형별 측정

```
EXISTS 계열:
  WORK_ACT      187
  MATERIAL_ACT  160
  EQUIPMENT_ACT  94
  FACILITY_ACT   11
  ─────────────────
  소계          452

UNIVERSAL (NONE)   94
THRESHOLD           3
─────────────────────
CONFIRMED 합계     549 (cmc 행 기준)
distinct clause    447 (조문 기준, 일부 조문 다중 매핑)
```

---

## TASK-002: 모집단 대비 Coverage

```
모집단 (semantic_clause):
  전체        58,495
  OBLIGATION  29,665  ← 전체 법령 (타법 포함, 분모 부적절)
  PROHIBITION  1,742
  DELEGATION   9,055

산안법 4법 한정 (진짜 분모):
  OBLIGATION + PROHIBITION = 2,174
  CONFIRMED distinct        = 444
  Coverage                  = 20.4%
```

---

## TASK-003: Coverage Gap (법령별)

| 법령 | 의무조문 | CONFIRMED | Coverage | Gap |
|---|---|---|---|---|
| 기준규칙 | 1,277 | 395 | **30.9%** | 882 |
| 산안법 | 398 | 33 | 8.3% | 365 |
| 시행규칙 | 418 | 12 | 2.9% | 406 |
| 시행령 | 81 | 4 | 4.9% | 77 |
| **합계** | **2,174** | **444** | **20.4%** | **1,730** |

```
Gap 해석:
  - 기준규칙 882 미커버 = 대부분 특정 설비/작업 방호 (EXISTS)
  - 시행규칙 406 미커버 = 서류·신고·절차 (FRAGMENT 다수)
  - 산안법 365 미커버 = 다항 조문 하위항 (FRAGMENT)
```

---

## TASK-004: 미적용 원인 자동 분류 (1,730건)

```
F_FRAGMENT/주어불명     916  (53%)  주어 사업주 아님/문장조각/하위항
G_미매핑(잠재 기타)     521  (30%)  사업주 의무이나 미수확
A_EXISTS_조건부         246  (14%)  작업/설비 전제 (has_* 필요)
B_APPENDIX_별표위임      36  ( 2%)
C_THRESHOLD_수치          7  
D_BUILDING_HOLD           6  

직독 검증 (G 521건 실체):
  - 상당수가 실제로는 EXISTS(버프연마기/띠톱/로봇 덮개·방호)
  - 일부 FRAGMENT (절단 문장: "작업하게 하여야 한다")
  - 순수 UNIVERSAL은 소수 → UNIVERSAL 천장(94) 재확인
  → G의 실질 기회는 대부분 A_EXISTS로 수렴.
```

---

## TASK-005: 우선순위 ROI 계산

```
효과(커버 가능 조문) × 실현성(데이터 준비도) = ROI

★★★★★ EXISTS 입력 수집
  - 잠재 커버: A 246 + G속 설비조건부 ≈ 400+ 조문
  - 기준규칙 Gap 882의 핵심
  - 단 입력단(진단 UI has_*) 동반 필요
  - 효과 최대, 실현성 중 (입력 UI 작업)

★★★★☆ FRAGMENT 재파싱 (시행규칙/산안법)
  - 잠재 커버: F 916 중 다항 하위항 복원분
  - executor 파싱 개선 시 상당수 회복
  - semantic_clause 재처리 (GPT 영역 인접 — 주의)
  - 효과 큼, 실현성 중하 (파싱 로직)

★★★☆☆ APPENDIX 별표 확장
  - 잠재 커버: B 36 + 별표 본조쌍
  - 안전관리자(완료)/검사대상 등
  - ksic 업종 매칭 필요분 많음
  - 효과 중, 실현성 중

★★☆☆☆ THRESHOLD 수치 확장
  - 잠재 커버: C 7 (본조 명시 거의 소진)
  - worker 축 천장 근접
  - 효과 소, 실현성 상

★☆☆☆☆ UNIVERSAL 추가
  - 천장 도달(94). 직독상 추가분 거의 0
  - 효과 최소
```

---

## 핵심 발견

### 발견 1: 진짜 분모는 산안법 4법 2,174

```
전체 58,495는 수백 법령 총합 — Coverage 분모로 부적절.
산안법 4법 2,174가 타겟 모집단.
→ Coverage 20.4%가 정확한 baseline.
→ "1.4%" 같은 숫자는 타법 포함 착시.
```

### 발견 2: Coverage가 법령 성격별로 갈린다

```
기준규칙(현장 안전기준) 31% — 작업·설비 의무, EXISTS로 확장.
시행규칙/시행령(서류·절차) 3~5% — FRAGMENT 다수, 파싱 의존.
→ 두 영역은 다른 전략 필요.
→ 현장의무=EXISTS, 절차의무=파싱개선.
```

### 발견 3: 최대 Gap은 EXISTS로 수렴

```
미커버 1,730 중:
  A_EXISTS 246 + G속 설비조건부 ≈ 400+
  = 기준규칙 Gap의 핵심.
→ EXISTS 입력만 수집되면 Coverage 20% → 35%+ 가능.
→ ROI 1순위 확정 (단 입력 UI 동반).
```

### 발견 4: FRAGMENT 916이 숨은 절반

```
미커버의 53%가 주어불명/조각.
→ semantic_clause 파싱이 다항 조문을 절단.
  ("작업하게 하여야 한다" = 상위 주어 분실)
→ 재파싱하면 상당수 회복 가능.
→ 단 파싱은 GPT 엔진 인접 영역 (경계 주의).
```

---

## 성공 기준 답변

```
산업안전보건법 의무 중 몇 %를 커버했는가?

✅ 측정 완료:
  산안법 4법 20.4% (444/2,174)
  기준규칙 31% / 산안법 8% / 시행규칙 3% / 시행령 5%

미적용 원인 분류 + ROI 우선순위 확정.
→ 이후 "다음 뭐하지?"가 Coverage 수치로 자동 결정.
```

---

## 다음 WO 자동 결정 (ROI 순)

```
1순위: EXISTS Coverage (★★★★★)
  - WO-EXISTS-COVERAGE-001
  - 입력 수집(진단 UI has_*) + 기존 EXISTS 375 활성화
  - 기대: Coverage 20% → 35%+
  - 입력단 동반 (Cursor 영역)

2순위: FRAGMENT 재파싱 (★★★★☆)
  - 시행규칙/산안법 다항 조문 복원
  - executor 파싱 개선 (GPT 경계 주의)

3순위: APPENDIX 확장 (★★★☆☆)
  - 별표 본조쌍 + ksic 업종 매칭

→ EXISTS가 명확한 1순위. 입력 UI가 관문.
```

---

## Coverage 추적 기준 (이후 WO마다 갱신)

```
현재 baseline: 산안법 4법 20.4%
  목표 궤적 (ROI 순 작업 시):
    EXISTS 활성화    → ~35%
    FRAGMENT 복원    → ~50%
    APPENDIX 확장    → ~55%

→ 각 품질 WO 완료 시 이 수치 갱신.
→ "감"이 아닌 Coverage 증분으로 성과 측정.
```

---

*WO-COVERAGE-GAP-001 완료. 품질 기준점 확정 — ① Applicability 내부.*
*핵심: 산안법 4법 Coverage 20.4%(444/2,174). 기준규칙 31%, 절차법 3~5%.*
*미커버 1,730 = FRAGMENT 916 + 미매핑 521 + EXISTS 246. ROI 1순위=EXISTS.*
*Boundary/Data Contract 무변경. 이후 우선순위는 Coverage 수치로 자동 결정.*
