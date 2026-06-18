# PROJECT DECISION CHAIN V1
# 프로젝트 의사결정 흐름 — 완전 복원용

**작성일**: 2026-06-18  
**성격**: 의사결정 흐름 영구 보존. 새 분석/구현/수집 없음.  
**목적**: 이 문서 하나만 읽으면 "왜 지금 여기까지 왔는가"를 이해 가능

> 기획서를 읽지 않아도, WO들을 읽지 않아도,  
> 이 Decision Chain만으로 복원 가능해야 한다.

---

## 1. 최초 문제

```
Track A(기존 엔진)가 왜곡된 결과를 생성한다.

관찰 (화성 제2공장 C28 제조업 280명):
  - 제조업인데 의료법이 MATCH
  - 제조업인데 건설산업기본법이 MATCH
  - 제조업인데 특수교육법이 MATCH

원인:
  SUBJECT_UNRESOLVED — actor(법령 주체) 미분류
  건설업자·의료기관 대상 법령이
  "280명 >= 2" 수치 조건만 보고 통과됨
```

---

## 2. 대응 전략 — 왜 V4를 만들었는가

```
Track A를 직접 고치지 않고 V4를 별도 구축.

목적:
  - 입력 보존 (null을 0으로 변환하지 않음)
  - Scope 분리 (업종/섭터/메트릭 독립)
  - ApplicabilityCondition 독립화 (조건을 데이터로, 코드 아님)

핵심 철학:
  V4 = Positive Space Engine
  = 적용 가능한 것만 생성, MUST_NOT은 원천적으로 안 만듦
  → 구조적으로 False Positive = 0

Track A는 수정 대상이 아니라 비교 기준으로 유지.
```

---

## 3. Phase 1 — FacilityProfile

```
검증: 사업장 속성을 TriValue(PRESENT/ABSENT/UNKNOWN)로 보존
증명: null을 0으로 착각하지 않고 UNKNOWN으로 유지 가능
다음으로 간 이유: 입력 구조가 확정되어야 조건 설계 가능
```

## 4. Phase 2 — ApplicabilityCondition

```
검증: 안전관리자 선임 조건 7건을 데이터로 정의
증명: 조건을 코드가 아닌 데이터로 표현 가능
다음으로 간 이유: 조건이 있으면 Scope 분리 필요
```

## 5. Phase 3 — ConditionScope

```
검증: INDUSTRY IN/NOT_IN 배타집합으로 업종 범위 분리
증명: C28이 고위험군 배타집합에 없으면 일반조항 해당
다음으로 간 이유: 조건+섭터가 실제 사업장에서 작동하는지 확인 필요
```

## 6. §8 검증 — 왜 수행했는가

```
문제의식:
  "부분 성공"을 확인했지만, 전체가 얼마나 정확한지 모름
  채점하려면 정답지가 필요함

Golden Case가 왜 필요한가:
  Track A가 114건 MATCH, V4가 1건 MATCH일 때
  누가 맞고 틀렸는지 판단할 기준이 없었음
  → "시험지 채점 전에 정답지부터 만든다"

Golden Case 구축 방식:
  Claude 1차 판정 (LLM이 명 subj백한 건설/의료/교육 오염은 직접 분류)
  사장님은 UNCERTAIN만 확인 (취업규칙/경보설비/장애인고용/수소설비 4건)

측정된 것:
  GOLDEN_CASE_HS2 v1.0: MUST 8건, MUST_NOT 43건
```

## 7. 측정 결과의 의미

```
Track A False Positive 93%:
  화성 제2공장 114건 중 106건이 MUST_NOT (오염)
  = Track A는 안 나와야 할 것을 많이 낸다
  (표본 1개 기준)

V4 MUST Coverage 12.5% → 100%:
  WO-01로 M-02~M-08 추가 (condition_scopes 데이터만, C1 코드 0줄)
  = V4는 나와야 할 것을 정확히 낸다

결론:
  정확도 문제는 해결됨 (V4가 INDUSTRIAL에서 목표 도달)
  남은 것은 커버리지 문제
```

## 8. 왜 Construction이 다음 단계가 되었는가 (측정값 근거)

```
V4 Coverage 실측:
  INDUSTRIAL = 100% (검증 완료)
  CONSTRUCTION = 0%
  BUILDING = 0%

둘 중 우선순위 (WO-COVERAGE-GAP-PRIORITY-001):
  사업장당 발생량: CONSTRUCTION 232.2 > BUILDING 135.7
  입력 존재: CONSTRUCTION은 construction_amount 이미 있음
  구현 난이도: CONSTRUCTION은 단일 METRIC (공사금액)
                  BUILDING은 소방/승강기/에너지 별도 법령군

판정: CONSTRUCTION 1순위 (감이 아닌 수치 근거)
```

## 9. 왜 Construction이 Blocked 되었는가

```
착수 전 검증 4단계 수행:
  PRECHECK → CONSTRAINT-TRACE → CHARACTERIZATION → APPENDIX3-LOCATE

발견:
  건설업 안전관리자 선임 구간이
  의미 레이어(law_article_part, semantic_clause)에는 있으나
  실행 레이어(constraint/rule/condition)에는 없음

  DB 수치 충돌:
    appendix_runtime_metadata: 건설업 50억 vs 120억 (둘 다 요약)
    120억 = 전담 안전관리자 경계 (선임 기준 아님)

  별표3 건설업란 본문(구간표)이 DB에 없음

확정 사실:
  - INDUSTRIAL appendix_condition 7건은 수동 입력이었음 (자동파싱 아님)
  - 그 수동 작업에서 CONSTRUCTION이 빠졌을 뿐

미확정 사실:
  - 건설업 선임 의무 발생 최소 공사금액
  - 건설업 선임 인원 구간

결론: 추정 금지 원칙상 ApplicabilityCondition 설계 불가 → BLOCKED
```

## 10. 현재 프로젝트 위치

```
완료:
  Phase 1 (FacilityProfile)
  Phase 2 (ApplicabilityCondition)
  Phase 3 (ConditionScope)
  §8 검증 (케이스 8/8)
  WO-01 (V4 MUST Coverage 100%)
  Coverage Gap 분석

진행 불가:
  Phase 5 CONSTRUCTION — 상태: BLOCKED
  해제 조건: 별표3 건설업란 원문(구간표) 확보

다음 우선순위 후보 (재선정 대기):
  1. Obligation Layer (Block 없음)
  2. BUILDING Coverage (원문 확보 리스크 재발 가능)
  3. INDUSTRIAL 심화 (Block 없음)
  4. 건설업 원문 확보 (Block 해제)
```

## 11. 절대 재분석 금지 항목

아래는 이미 결론난 것. 다시 조사하면 안 됨:

```
1. Track A False Positive 93%
   → 측정 완료 (화성 제2공장 기준). 재측정 불필요.

2. V4 = Positive Space Engine (MUST_NOT 미생성)
   → 설계 확정. "V4도 NOT_APPLICABLE 생성해야 하나" 재논의 금지.

3. Construction Coverage Gap 존재
   → 확인됨. "왜 Construction이죠?" 재질문 금지.

4. Construction 1순위 근거 (사업장당 232.2, 입력 존재, 단일 METRIC)
   → 판정 완료. 재분석 금지.

5. Equipment/Process/Boolean 우선순위
   → Impact 미측정 (평가기 연결 안 됨 → ablation 불가).
     "Equipment 42.4%"는 분포이지 영향도 아님. 재해석 금지.

6. V4 MUST Coverage 100% (INDUSTRIAL)
   → 검증 완료. 재측정 불필요.

7. §8 케이스 8/8
   → 완료. UNKNOWN 3유형(SCOPE/METRIC/NOT_APPLICABLE) 구분 확정.

8. INDUSTRIAL appendix_condition이 수동 입력이었다
   → 확인됨. "자동 파싱이었나?" 재조사 금지.

9. 120억 = 전담 경계 (선임 기준 아님)
   → 의미절 글읽기로 확인. "120억이 선임 기준인가" 재논의 금지.

10. appendix_runtime_metadata 50억/120억 충돌 → 신뢰불가
    → 확인됨. 이 메타데이터로 threshold 확정 시도 금지.
```

---

## 완료 조건 충족

```
새로운 사람이 이 문서 하나만 읽고
"왜 지금 여기까지 왔는가"를 이해할 수 있음:

  Track A 오염 → V4 구축 → Phase 1~3 검증
  → §8 Golden Case 채점 → 정확도 문제 해결 확인
  → 커버리지 문제로 전환 → Construction 1순위 선정
  → 원문 부재로 BLOCKED → 다음 우선순위 재선정 대기
```
