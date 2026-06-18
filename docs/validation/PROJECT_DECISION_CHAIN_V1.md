# PROJECT DECISION CHAIN V1
# 프로젝트 의사결정 흐름 영구 보존

**작성일**: 2026-06-18
**성격**: 의사결정 흐름 기록. 새 분석/구현/법령수집 없음.
**목적**: 신규 인력(GPT/Claude/개발자)이 이 문서 하나로 "왜 여기까지 왔는가"를 복원.

> 이 문서는 기획서가 아니다. 기획서는 `docs/2026-06-11_LEGAL_ENGINE_V4_LAYER_REDESIGN.md`에 있다.
> 이 문서는 "그 기획을 왜, 어떤 순서로 실행했는가"의 기록이다.
> 프로젝트에서 가장 비싼 자산은 코드가 아니라 "왜 이 결정을 했는가"이다.

---

## 1. 최초 문제 — Track A 왜곡

**현행 운영 엔진 Track A는 전체 법령을 탐색하지만 결과가 오염되어 있었다.**

관찰 (화성 제2공장, C28 전기장비제조, 280명):
```
Track A가 MATCH_CANDIDATE로 잡은 114건 중 106건이 틀림 (93%)

예시 오탐:
  제조업 사업장에 → 의료법
  제조업 사업장에 → 건설산업기본법
  제조업 사업장에 → 특수교육법
```

원인 진단:
```
SUBJECT_UNRESOLVED 문제
  법령의 적용 주체(actor)가 분류되지 않음
  → 건설업자/의료기관/교육기관 대상 법령이
     "근로자 280명 >= 2명" 같은 숫자 조건만 보고 통과
  → 업종/주체를 무시한 숫자 매칭이 오염의 근본 원인
```

**결론: Track A는 "숫자는 보지만 누구에게 적용되는지는 모르는" 엔진이었다.**

---

## 2. 대응 전략 — 왜 V4를 만들었는가

Track A를 수정하지 않고 **별도의 정답 엔진 V4**를 만들기로 결정.

이유:
```
Track A 수정 = 오염된 엔진을 계속 패치하는 무한 루프
V4 신규 = 처음부터 "적용 가능한 것만 생성"하는 엔진
```

V4 설계 3원칙:
```
1. 입력 보존 (FacilityProfile)
   null을 0으로 변환하지 않음
   → "값 없음"과 "값 0"을 구분
   → TriValue (PRESENT / UNKNOWN / NOT_APPLICABLE)

2. Scope 분리 (ConditionScope)
   업종(INDUSTRY)/부문(SECTOR) 범위를 조건에서 분리
   → 업종 범위 밖이면 NOT_APPLICABLE로 정직하게 처리

3. ApplicabilityCondition 독립화
   각 의무를 독립된 적용조건으로 표현
   → C1 코드 수정 없이 condition_scopes 데이터만 추가하면 확장
```

**핵심 철학: V4 = Positive Space Engine**
```
적용될 수 있는 것만 생성한다.
MUST_NOT(해당 없음)은 원천적으로 만들지 않는다.
→ 구조적으로 False Positive = 0
→ 수십만 건의 부정 판정 생성을 방지
```

---

## 3. Phase 1 — FacilityProfile

검증한 것: 입력값이 null일 때 엔진이 어떻게 반응하는가
증명한 것:
```
근로자수 null → UNKNOWN (0으로 변환 안 함)
"수치 비교 불가"로 정직하게 처리
```
다음으로 간 이유: 입력 보존이 확인됐으니 조건 표현으로 진행

---

## 4. Phase 2 — ApplicabilityCondition

검증한 것: 의무를 독립 조건으로 표현 가능한가
증명한 것:
```
안전관리자 선임 7건(업종군별) + 일반의무 7건(M-02~M-08)
= 14건 조건이 독립적으로 평가됨
```
다음으로 간 이유: 조건 구조가 작동하니 Scope 분리 검증으로 진행

---

## 5. Phase 3 — ConditionScope

검증한 것: 업종 범위 IN/NOT_IN이 정확히 작동하는가
증명한 것:
```
scope_operator = IN  → 해당 업종만 SCOPE_MATCH
scope_operator = NOT_IN → 배타집합 제외 후 SCOPE_MATCH
업종 범위 밖 → NOT_APPLICABLE
```
다음으로 간 이유: Scope가 작동하니 실제 사업장 검증(Phase 4)으로 진행

(Phase 4: Real Facility Validation — INDUSTRIAL 실제 사업장 10건 평가 통과)

---

## 6. §8 검증 — 왜 수행했는가

**Phase 1~4는 "엔진이 작동하는가"를 봤다. §8은 "엔진이 정답을 내는가"를 본다.**

Golden Case가 필요한 이유:
```
엔진이 MATCH를 내도, 그게 법적으로 맞는 MATCH인지
판단할 "정답지"가 없으면 정확도를 측정할 수 없다.
→ 사장님이 화성 제2공장 4건을 직접 판정하여 정답지 구축
   (취업규칙 MUST_CANDIDATE, 경보설비 MUST,
    장애인고용 MUST_CANDIDATE, 수소설비없음 MUST_NOT)
```

케이스 매트릭스 8종으로 측정:
```
#1 C28 280명       → MUST 8/8 MATCH
#2 C28 49명        → 안전관리자 NOT_MATCH (경계값 정확)
#3 C28 50명        → MUST 8/8 (경계값 정확)
#4 건설 49억       → 전체 UNKNOWN (Scope 미구현)
#5 건설 50억       → 전체 UNKNOWN (Scope 미구현)
#6 빈 입력         → UNKNOWN (수치 비교 불가)
#7 전부 채운 입력  → MUST 8/8 (=#1)
#8 건물 100명      → 전체 UNKNOWN (Scope 미구현)
```

측정된 것: UNKNOWN이 3유형으로 정확히 구분됨
```
SCOPE UNKNOWN    — 건설/건물 (업종 평가 불가)
METRIC UNKNOWN   — 빈 입력 (수치 비교 불가)
NOT_APPLICABLE   — 업종 범위 외
```

---

## 7. 측정 결과의 의미

```
Track A False Positive 93%:
  → Track A를 그대로 소비자에게 보여주면 안 된다는 증거
  → 단, 표본 1개(화성 제2공장)이므로 일반화는 제한적

V4 MUST 커버율 100% (12.5% → 100%):
  → WO-01로 M-02~M-08 추가하여 달성
  → C1 코드 0줄 수정 (condition_scopes 데이터만 추가)
  → V4 설계(데이터 확장만으로 커버 확대)가 작동한다는 증거
  → 단, INDUSTRIAL 한정. CONSTRUCTION/BUILDING은 0%
```

**이 시점에서 프로젝트 성격이 전환됨: "정확도 문제" → "커버리지 문제"**

---

## 8. 왜 Construction이 다음 단계가 되었는가 (감 아님, 측정값 근거)

V4 미커버 영역은 CONSTRUCTION, BUILDING 둘뿐. 측정으로 우선순위 결정.

WO-COVERAGE-GAP-PRIORITY-001 측정값:
```
법령 모집단 (law_sector_mapping):
  BUILDING 175 > INDUSTRIAL 158 > CONSTRUCTION 130

사업장당 발생량 (facility_applicability, 정규화):
  CONSTRUCTION 232.2 > INDUSTRIAL 172.1 > BUILDING 135.7
```

두 지표가 상반됨. CONSTRUCTION을 1순위로 선정한 실제 근거:
```
1. 사업장당 발생량 232.2 — 3개 sector 중 최고
2. 입력 이미 존재 (construction_amount, sector)
   → 새 입력체계 불필요
3. 단일 METRIC 구조 (공사금액)
   → 구현 난이도 낮음

(주의: 232.2는 Track A 기준이라 93% 오염 포함된 수치.
 "232.2 > 135.7이라 더 중요"는 약한 근거.
 진짜 근거는 입력 존재 + 구조 단순함.)

BUILDING 2순위 이유:
  법령 수는 최대(175)지만 소방시설법/승강기법/에너지법 등
  별도 법령군 → 새 Appendix 수집 필요 → 난이도 높음
```

---

## 9. 왜 Construction이 Blocked 되었는가

착수 전 검증 4연속 WO 수행 결과:

```
WO-V4-PHASE5-PRECHECK-001:
  appendix_condition에 건설업 조항 없음 (INDUSTRIAL 7건만)

WO-CONSTRUCTION-CONSTRAINT-TRACE-001:
  건설업 안전관리자가 의미 레이어엔 존재, 실행 레이어엔 미도달
  constraint_node는 공사금액을 DEFINITION으로만 보유

WO-PHASE5-CHARACTERIZATION-001:
  의미절의 건설업 공사금액은 전부 다른 의무
    제73조=기술지도, 제75조=노사협의체,
    제17조제3항=전담 안전관리자, 제16조제2항=공동선임, 제62조=총괄책임자
  별표3 본문(건설업 선임 인원 구간)은 "별표3과 같다" 참조만, 미분해

WO-APPENDIX3-CONSTRUCTION-LOCATE-001:
  별표3 건설업란 본문 DB 부재 확정
  INDUSTRIAL 7건은 자동파싱 아닌 수동입력(MANUAL)
  appendix_runtime_metadata 값 충돌: 50억 vs 120억 (둘 다 요약, 신뢰불가)
```

확정된 사실:
```
건설업 안전관리자 의미는 DB에 존재 (law_article_part, semantic_clause)
공사금액 120억 = "전담" 안전관리자 경계 (제17조제3항)
```

미확정 사실:
```
건설업 안전관리자 "선임 의무 발생" 최소 공사금액
건설업 선임 인원 구간 (몇 명)
전담/공동선임 구조
→ 별표3 건설업란 원문(구간표)이 DB에 없어서 확정 불가
```

**상태: BLOCKED. Block 해제 조건 = 별표3 건설업란 원문(구간표) 확보.**

---

## 10. 현재 프로젝트 위치

```
✅ 완료 (검증됨):
  Phase 1 FacilityProfile
  Phase 2 ApplicabilityCondition
  Phase 3 ConditionScope
  Phase 4 Real Facility Validation
  §8 Golden Case Validation (케이스 8/8)
  INDUSTRIAL 안전관리자 + 일반의무 8건 MUST 100%
  Coverage Gap 분석

⛔ 진행 불가:
  Phase 5 CONSTRUCTION = BLOCKED
  (별표3 건설업란 원문 부재)

다음 우선순위 후보 (사장님 재선정 대기):
  후보 1: Obligation Layer (Block 없음, 즉시 가능) — 권장
  후보 2: BUILDING Coverage (원문 확보 리스크 재발 가능)
  후보 3: INDUSTRIAL 심화 (Block 없음, 기존 구조 재사용) — 권장
  후보 4: 건설업 원문 확보 → Construction 재개
```

---

## 11. 절대 재분석 금지 항목 (이미 결론난 것)

다음 항목들은 이미 측정·결론이 나왔다. 재조사 금지.

```
1. Track A False Positive 93%
   → 이미 측정됨 (화성 제2공장, 표본 1). 재측정 불필요.

2. V4 = Positive Space Engine, MUST_NOT 미생성
   → 설계 확정. "V4도 NOT_APPLICABLE 생성해야 하나?" 재논의 금지.

3. UNKNOWN 3유형 (SCOPE/METRIC/NOT_APPLICABLE)
   → 구분 확인 완료. 재분석 금지.

4. Equipment/Process/Boolean Impact 미측정
   → 평가기 미연결로 ablation 불가. "Equipment가 중요한가?" 재논의 금지.
     (42.4%는 규칙 분포이지 영향도 아님 — 이미 정정됨)

5. Equipment 우선순위 미확정
   → Impact 측정 전까지 결론 불가. 우선순위 추정 금지.

6. Construction Coverage Gap 존재 (0%)
   → 측정 완료. 재확인 금지.

7. CONSTRUCTION 1순위 선정 근거
   → 입력 존재 + 단일 METRIC 구조. 재논의 금지.
     "왜 Construction부터?" 질문 시 이 문서 8번 참조.

8. 별표3 건설업란 원문 DB 부재
   → 4개 WO로 확정. 별표3/appendix/metadata/attachment 재탐색 금지.

9. 50억 vs 120억 충돌
   → appendix_runtime_metadata 요약 오류. 둘 다 신뢰불가.
     이 논쟁 반복 금지. 원문 확보로만 해결.

10. 120억의 의미
    → "전담 안전관리자 경계"이지 "선임 의무 발생 기준" 아님. 재해석 금지.

11. INDUSTRIAL 7건이 수동입력이었다는 사실
    → appendix_text=NULL에서 파싱된 게 아님. 자동 추출 경로 재탐색 금지.
```

---

## 복원 체크 (이 문서 완료 조건)

신규 인력이 이 문서만 읽고 답할 수 있어야 하는 질문:
```
Q. 왜 V4를 만들었나?        → 2번 (Track A 오염, 수정 대신 신규)
Q. §8을 왜 했나?           → 6번 (작동 검증 후 정답 검증)
Q. Golden Case가 왜 필요?  → 6번 (정답지 없으면 정확도 측정 불가)
Q. 왜 Construction 1순위?  → 8번 (입력 존재 + 단일 METRIC)
Q. 왜 지금 Blocked?        → 9번 (별표3 건설업란 원문 부재)
Q. 다음에 뭘 하나?         → 10번 (후보 1 또는 3 권장)
```

기획서를 읽지 않아도, WO들을 읽지 않아도, 이 문서만으로 복원 가능.
