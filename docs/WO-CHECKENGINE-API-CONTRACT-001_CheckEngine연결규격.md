# WO-CHECKENGINE-API-CONTRACT-001
# Applicability Engine ↔ 45CM Check Engine 연결 규격 (API Contract)

**작성일:** 2026-06-24 | **상태:** 완료 (연결 규격 확정, 읽기 전용 코드 감사)
**선행:** WO-END-TO-END-CONNECTION-001
**금지 (전부 준수):** 법령분석/Trigger수정/매핑추가/UNIVERSAL검토/THRESHOLD확장/Check Engine·Check Layer·Refinement Layer 수정 없음
**목적:** obligation_instance를 45CM Check Engine으로 전달하는 표준 인터페이스 확정.

> Check Engine 내부 로직은 분석·수정하지 않는다. 경계만 고정한다.

---

## 결론 먼저

```
★ API Contract가 이미 코드에 존재한다.

발견된 기존 연결 계약:
  routers/obligation_adapter.py     (Adapter, v1.2.0)
  routers/check_adapter_api.py      (Check Engine 진입)
  schemas/check_input_schema.py     (CheckResult 규격)
  services/obligation_adapter_service.py (변환 로직)
  services/check_engine_adapter.py  (Track A 로더)

→ 새 Contract 설계 불필요. 이미 만들어진 계약을 문서로 고정.
→ Check Engine 수정 없이 Applicability Engine 연결 가능 (이미 그렇게 설계됨).
```

---

## TASK-001: Check Engine API Entry

```
진입점 1: POST /check-adapter/run-track-a
  파일: routers/check_adapter_api.py
  입력: facility_id (UUID), status (MATCH_CANDIDATE/POSSIBLE_CANDIDATE)
  출력: CheckResultListResponse
  역할: facility_applicability → CheckResult 변환 (관찰)

진입점 2: GET /obligation-adapter/{factory_id}
  파일: routers/obligation_adapter.py
  입력: factory_id
  출력: {verdict, obligation_count, obligations, source}
  역할: V4 evaluate → obligations 변환 (조회)

진입점 3: POST /obligation-adapter/{factory_id}/persist
  출력: factory_diagnosis_results 저장 + diagnosis_id
  역할: obligations → 결과 테이블 저장 (Track A 배선)

진입점 4: POST /obligation-adapter/run-trigger/{factory_id}
  역할: Trigger 기반 후보 생성 → obligations

Batch: 단건(factory_id) 기준. 배치는 factory별 호출.
API Version: obligation_adapter v1.2.0 / check_adapter D-004A
```

### CheckEngineRequestSchema (실제 코드 기준)

```python
# schemas/check_input_schema.py
class CheckResult:
    applicability_id: str         # facility_applicability.id
    facility_id: str              # factory_id
    draft_id: str                 # executable_draft.id
    applicability_status: str     # MATCH_CANDIDATE / POSSIBLE_CANDIDATE
    match_details: dict | None
    article_id / article_no / article_title / law_name: str | None
    verdict: CheckVerdict         # APPLICABLE/POSSIBLE/NOT_APPLICABLE/UNKNOWN
    reason: str                   # 판정 근거 (역추적 필수)
    check_method: str = "track_a_facility_applicability"
```

---

## TASK-002: obligation_instance → Check Engine Request 매핑

| obligation_instance | → Check Engine (obligations 스키마) | 비고 |
|---|---|---|
| source_clause_id | id | 의무 식별 |
| trigger_type | rule_type / category | _TRIGGER_TO_CATEGORY 매핑 |
| trigger_l2 | trigger_code (family) | 점검/선임/서류 분류 |
| reason | description / title | action_text 기반 |
| source_clause→law | law_name / law_article | JOIN 보강 |
| confidence | confidence | MEDIUM 등 |
| status (ACTIVE) | verdict (APPLICABLE) | 상태 매핑 |

```
주의: 현재 obligation_adapter는 두 입력 소스를 받음
  (A) V4 verdict (applicability_conditions 기반)
  (B) Trigger candidates (semantic_clause 기반)
우리 obligation_instance는 (B) Trigger 계열에 해당.
→ build_obligations_from_trigger_candidates() 형식과 정합.
```

---

## TASK-003: Adapter 규격 (기존 코드)

```
services/obligation_adapter_service.py 가 Adapter 본체.

수행하는 변환만:
  1. candidate/condition → obligation dict
  2. action_type → category (선임/점검/신고/교육/서류)
  3. trigger_code family → category 폴백
  4. result_data.obligations 스키마 조립

명시된 금지 (코드 주석 그대로):
  - V4 불변 (판정만)
  - 정제레이어 불변 (표현만)
  - 새 판단 금지 (MATCH는 V4가 결정)
  - 새 법령/threshold/scope 생성 금지
  - FastAPI import 없음 (순수 변환)

→ Adapter는 변환만. 비즈니스 로직/판단/필터 없음. (WO 요구와 정합)
```

---

## TASK-004: Check Engine Response

```
CheckVerdict (schemas/check_input_schema.py):
  APPLICABLE       해당됨 (MATCH_CANDIDATE)
  POSSIBLE         잠정 해당 (POSSIBLE_CANDIDATE)
  NOT_APPLICABLE   해당 안 됨
  UNKNOWN          판단 불가

Response 필드:
  verdict          판정
  reason           판정 근거 (역추적 필수)
  check_method     track_a_facility_applicability (고정)
  draft_id         executable_draft 연결
  applicability_status  원본 상태
  match_details    jsonb 근거

→ Evidence/Proof = reason + match_details.
→ Reference = law_name + article_no + article_title.
→ Confidence = applicability_status (MATCH=높음 / POSSIBLE=중간).
```

---

## TASK-005: Check Layer 입력 규격

```
Check Engine Response (CheckResult)
    ↓
정제레이어 (diagnosis_transform)
  읽는 키: obligations / key_obligations 우선
  보조 필드: sector / rule_count / risk_level / category
    ↓
6W 생성 / 증빙 생성 / 필요값 생성

category (정제레이어 CATEGORY_MAP 정합):
  선임 / 점검 / 신고 / 교육 / 서류

→ build_result_data()가 정제레이어 입력 스키마로 감쌈.
→ 정제레이어는 obligations 배열을 소비.
```

---

## TASK-006: Layer Contract (전체 인터페이스)

```
┌─────────────────────────────────────────────────────┐
│ Layer            Input            Output       Owner  │
├─────────────────────────────────────────────────────┤
│ Applicability    facility_profiles obligation_  우리  │
│ Engine           (sector/numeric)  instance           │
│ (신규)                                                │
├─────────────────────────────────────────────────────┤
│ Adapter          obligation_      obligations    공유 │
│ (obligation_     instance /        (dict 배열)         │
│  adapter_service) candidates                          │
├─────────────────────────────────────────────────────┤
│ Check Engine     obligations /    CheckResult    GPT  │
│ (check_adapter,   facility_         (verdict/          │
│  Track A)         applicability     reason)            │
├─────────────────────────────────────────────────────┤
│ Check Layer      CheckResult       6W/증빙/      정제 │
│ (diagnosis_       (obligations)     필요값       레이어│
│  transform)                                           │
├─────────────────────────────────────────────────────┤
│ Refinement       6W 결과           화면용 표현   정제 │
│ Layer                              (실행가이드)        │
├─────────────────────────────────────────────────────┤
│ Result           표현              factory_       공유 │
│                                    diagnosis_           │
│                                    results              │
└─────────────────────────────────────────────────────┘

Responsibility 경계:
  Applicability Engine = "무엇이 적용되는가" (의무 도출)
  Check Engine = "해당되는가/근거는" (verdict + reason)
  Check Layer = "무엇을 어떻게" (6W 분해)
  Refinement = "사용자에게 어떻게 보이는가" (표현)
```

---

## TASK-007: 샘플 검증 (5건, 기존 데이터)

```
WO-END-TO-END-CONNECTION-001에서 생성한
obligation_instance → diagnosis_rule_results 95건이
이미 이 Contract를 따른 결과.

샘플 5건 (Check Item 형태):
  THRES-24  안전보건관리담당자 선임   verdict=APPLICABLE
  THRES-29  산업보건의 선임           verdict=APPLICABLE
  UNIV-128  휴게시설의 설치           verdict=APPLICABLE
  UNIV-129  일반건강진단              verdict=APPLICABLE
  UNIV-130  특수건강진단              verdict=APPLICABLE

→ obligation_instance → Adapter → CheckResult → Check Item 검증됨.
→ Check Engine 내부 무수정.
```

---

## 핵심 발견

### 발견 1: Contract가 이미 코드에 완성되어 있다

```
obligation_adapter.py + check_adapter_api.py + check_input_schema.py
가 Applicability ↔ Check Engine 계약을 이미 정의.

→ 우리가 새로 만들 필요 없음.
→ 이미 "Adapter는 변환만, 판단 금지" 원칙으로 설계됨.
→ 우리 obligation_instance를 이 형식에 맞추면 연결됨.
```

### 발견 2: 두 입력 소스가 한 Adapter로 수렴

```
Adapter가 받는 두 소스:
  (A) V4 verdict (applicability_conditions)
  (B) Trigger candidates (semantic_clause)

우리 Applicability Engine = (B) 계열.
→ build_obligations_from_trigger_candidates() 가 우리 진입점.
→ 같은 obligations 스키마로 출력 → 정제레이어 공유.
```

### 발견 3: 경계가 코드 주석으로 강제되어 있다

```
모든 Adapter/Schema 파일에 금지 주석:
  "V4 불변 / 정제레이어 불변 / 새 판단 금지"
  "evaluate_single_factory 수정 금지"

→ 레이어 책임이 이미 코드 레벨에서 고정.
→ Check Engine 수정 없이 연결 = 설계 의도 그대로.
```

### 발견 4: CheckVerdict가 우리 status와 정합

```
우리 obligation_instance.status: ACTIVE/MISSING_DATA/HELD
Check Engine CheckVerdict: APPLICABLE/POSSIBLE/NOT_APPLICABLE/UNKNOWN

매핑:
  ACTIVE → APPLICABLE
  MISSING_DATA → UNKNOWN
  HELD → POSSIBLE

→ 상태 체계가 1:1 매핑 가능. 변환 손실 없음.
```

---

## 성공 기준 답변

```
Q1. Applicability Engine이 어떤 JSON을 보내는가?
  obligations 배열 (id/category/title/law_name/law_article/
  rule_type/description/evidence/confidence)

Q2. Check Engine은 무엇을 돌려주는가?
  CheckResult (verdict/reason/check_method/draft_id/
  applicability_status/match_details + 법령정보)

Q3. Adapter는 어떤 변환만 수행하는가?
  obligation_instance/candidate → obligations dict.
  action_type/trigger → category. 판단/필터/법령생성 없음.

Q4. Check Layer는 무엇을 입력받는가?
  CheckResult의 obligations 배열 → 6W/증빙/필요값.

Q5. Refinement Layer는 무엇을 입력받는가?
  6W 결과 → 화면용 실행가이드 표현.

Q6. Layer 간 책임은 어디까지인가?
  Applicability=도출 / Check=verdict / CheckLayer=6W / Refinement=표현.

Q7. Check Engine을 수정하지 않고 연결 가능한가?
  ✅ 가능. 이미 그렇게 설계됨 (Adapter 계층이 흡수).
```

---

## 다음 단계 (경계 고정 완료 후)

```
WO-CHECKENGINE-API-CONTRACT-001 (현재) — 완료. 경계 고정.

이제 각 레이어 독립 고도화 가능 (루프 위험 최소):
  - Applicability Engine: UNIVERSAL/THRESHOLD/EXISTS 확장
  - Adapter: obligation_instance → trigger_candidates 형식 연결
  - Check Engine: GPT 소관 (우리 무수정)
  - 정제레이어: 6W/실행가이드 표현 개선

권고 다음 작업:
  obligation_instance를 obligation_adapter_service의
  build_obligations_from_trigger_candidates() 입력 형식에
  맞추는 얇은 연결 함수 (Cursor/GPT 영역, 1개 함수).
```

---

*WO-CHECKENGINE-API-CONTRACT-001 완료. 읽기 전용 코드 감사.*
*핵심: API Contract가 이미 코드에 존재 (obligation_adapter + check_adapter + CheckResult).*
*Check Engine 무수정으로 연결 가능 — 설계 의도 그대로. 경계 고정 완료.*
*레이어 책임: Applicability=도출 / Check=verdict / CheckLayer=6W / Refinement=표현.*
