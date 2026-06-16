# 법령엔진 15차 구현 작업지시 (WO-D-001 ~ WO-D-007)

작성일: 2026-06-16  
상태: 승인 대기 → 순차 실행  
수정이력: 2026-06-16 실측 기반 D-004 분리 (D-004A/D-004B), WO-APPENDIX-COLLECT-001 추가

---

## ⚠️ 최우선 원칙 (Cursor·Claude 필독, 위반 시 즉시 중단)

```
본 WO의 목표는 기존 엔진 교체가 아니다.

기존 Track A 엔진을 유지한 상태에서
공용거름망 → 의미절 → 후보 → 섹터거름망 → 체크 → KSIC Signal → 역검증 → 정제
관찰 가능한 파이프라인을 구축하는 것이다.

기존 함수 삭제 금지:
  - facility_applicability_eval
  - fetch_compiler_candidates
  - assemble_refinery_result
  - emit_stored_diagnosis_result

기존 테이블 삭제 금지:
  - semantic_clause_fix
  - legal_sieve_rule
  - executable_draft / draft_slot
  - constraint_node

GPT 관리 테이블 — 읽기만 허용, 수정·삭제 절대 금지:
  - constraint_node
  - numeric_constraint
  - rule_candidate
  - executable_draft
  - draft_slot
  - compatibility_validation

새 파이프라인은 기존 경로와 병행 실행. 기존 경로는 건드리지 않는다.
```

---

## ★ 핵심 발견 (2026-06-16 실측 확정)

```
[발견] SemanticClause 경로 ≠ Track A 경로. 현재 동일한 엔진이 아니다.

Track A (기존):
  factories row
  + draft_slot (binding_field 존재하는 것만)
  → evaluate_draft_for_facility
  → facility_applicability

Track B (신규 관찰 경로):
  semantic_clause_fix
  → CandidateClause
  → SectionCandidateClause
  → ??? (평가 방법 미정)

[결론]
SemanticClause를 facility_applicability_eval에 억지로 연결하면
평가 대상이 0건이 된다 (binding_field 없음).
이것이 D-004를 A/B로 분리하는 이유.

[별표 상태]
산안법 시행령 제16조: "별표 3과 같다" 언급만 있음.
별표 3 본체 데이터 DB 미수집.
→ WO-APPENDIX-COLLECT-001 선행 필요.
```

---

## 구현 순서

```
[1단계 — 현재 범위]
WO-D-001  Semantic Clause Pipeline
    ↓
WO-D-002  Common Sieve Engine
    ↓
WO-D-003  Section Sieve
    ↓
WO-D-004A Track A Check Adapter   ← 기존 facility_applicability 결과 래핑
    ↓
WO-D-005  KSIC Signal Engine
    ↓
WO-D-006  Reverse Check Engine
    ↓
WO-D-007  Refinery

[2단계 — D-001~007 완료 후]
WO-APPENDIX-COLLECT-001  별표 수집
    ↓
WO-D-004B Semantic Candidate Evaluator  ← SemanticClause 직접 평가 (미설계)
```

각 WO는 이전 WO 완료 확인 후 착수. 완료조건 미충족 시 다음 단계 진행 금지.

---

## WO-D-001: Semantic Clause Pipeline

### 목표
`semantic_clause_fix` → 표준 `SemanticClause` 객체 생성기 구축

### 관련 기존 파일
- `routers/anonymous_diagnosis.py` — 현재 `semantic_clause_fix` 직접 조회
- `routers/legal_engine.py` — 법령엔진 진입점
- DB 테이블: `semantic_clause_fix` (49,997 parts), `law_article_part` (143,549)

### 신규 생성 파일
```
services/
  semantic_clause_service.py
schemas/
  semantic_clause_schema.py
routers/
  semantic_pipeline_api.py
```

### SemanticClause 객체 스키마
```python
class SemanticClause(BaseModel):
    clause_id: str              # semantic_clause_fix.id
    part_id: str                # law_article_part.id
    article_id: str             # law_article.id
    law_id: str                 # law_master.id
    law_name: str
    article_no: str
    article_title: str
    executor_text: str          # semantic_clause_fix.executor_text
    clause_text: str            # part_text
    sector_hint: Optional[str]  # INDUSTRIAL/BUILDING/CONSTRUCTION/None
    source_span: Optional[str]
    created_at: datetime
```

### DB 조회 쿼리
```sql
SELECT
  scf.id as clause_id,
  scf.part_id,
  la.id as article_id,
  lm.id as law_id,
  lm.law_name,
  la.article_no,
  la.article_title,
  scf.executor_text,
  lap.part_text as clause_text,
  scf.sector_hint,
  scf.created_at
FROM semantic_clause_fix scf
JOIN law_article_part lap ON scf.part_id = lap.id
JOIN law_article la ON lap.article_id = la.id
JOIN law_master lm ON la.law_id = lm.id
WHERE scf.executor_text IS NOT NULL
  AND scf.executor_text != ''
```

### 함수 목록
```python
async def get_semantic_clauses(db, law_id=None, sector=None, limit=1000, offset=0) -> List[SemanticClause]
async def get_semantic_clause_by_id(db, clause_id: str) -> Optional[SemanticClause]
async def count_semantic_clauses(db, law_id=None) -> int
```

### 완료조건
1. `GET /semantic-pipeline/clauses?limit=10` → SemanticClause 목록 반환
2. `GET /semantic-pipeline/clauses/count` → `{"total": N}`
3. executor_text null/빈문자 행 제외 확인
4. 기존 `anonymous_diagnosis.py` 미수정 확인

---

## WO-D-002: Common Sieve Engine

### 목표
`legal_sieve_rule` (2,219개) → SemanticClause 적용 → CandidateClause 생성

### ⚠️ 거름 기준 제한
```
허용: AUTHORITY / BUSINESS / FRAGMENT 수준 분류
금지: 법 해석 기반 DROP (예: "산안법이면 DROP", "소방법이면 KEEP" 같은 해석성 규칙)
      → 해석성 규칙은 GPT 영역
```

### 관련 기존 파일
- `routers/admin_executor_llm_fix.py` — `sieve_executor()`, `run_common_sieve()` 포함
- DB 테이블: `legal_sieve_rule` (2,219개)

### 신규 생성 파일
```
services/common_sieve_service.py
schemas/candidate_clause_schema.py
routers/common_sieve_api.py
```

### CandidateClause 객체 스키마
```python
class SieveResult(str, Enum):
    KEEP = "KEEP"
    DROP = "DROP"
    PENDING = "PENDING"  # 미매칭 — 소멸 금지

class CandidateClause(BaseModel):
    clause_id: str
    part_id: str
    article_id: str
    law_id: str
    law_name: str
    article_no: str
    executor_text: str
    clause_text: str
    sieve_result: SieveResult
    sieve_rule_id: Optional[str]   # 매칭된 legal_sieve_rule.id
    sieve_reason: Optional[str]    # 매칭된 rule의 executor_class
    sector_hint: Optional[str]
```

### 함수 목록
```python
async def apply_common_sieve(clause: SemanticClause, sieve_rules: List[dict]) -> CandidateClause
async def run_common_sieve_batch(db, law_id=None, batch_size=500) -> dict
async def get_candidate_clauses(db, sieve_result=None, law_id=None, limit=100, offset=0) -> List[CandidateClause]
```

### 완료조건
1. `POST /common-sieve/run` → `{"keep": K, "drop": D, "pending": P}`
2. `GET /common-sieve/candidates?sieve_result=KEEP&limit=10`
3. DROP 결과에 `sieve_rule_id` + `sieve_reason` 기록
4. PENDING 건수 확인 가능
5. 기존 `sieve_executor` 미수정

---

## WO-D-003: Section Sieve

### 목표
CandidateClause(KEEP) → 섹터별 분리 → SectionCandidateClause

### ⚠️ 제한
```
SPECIAL_FACILITY 절대 할당 금지 (의도적 휴면)
미매핑 법령 → universal (전 섹터 통과, "가지고 감" 원칙)
```

### 신규 생성 파일
```
services/section_sieve_service.py
schemas/section_candidate_schema.py
routers/section_sieve_api.py
```

### SectionCandidateClause 스키마
```python
class Sector(str, Enum):
    INDUSTRIAL = "INDUSTRIAL"
    BUILDING = "BUILDING"
    CONSTRUCTION = "CONSTRUCTION"

class SectionCandidateClause(BaseModel):
    clause_id: str
    part_id: str
    article_id: str
    law_id: str
    law_name: str
    article_no: str
    executor_text: str
    clause_text: str
    sieve_result: SieveResult
    assigned_sectors: List[Sector]
    sector_source: str  # "law_sector_mapping" | "clause_hint" | "universal"
```

### 완료조건
1. `POST /section-sieve/run` + `{"facility_sector": "INDUSTRIAL"}` → 해당 후보 반환
2. 미매핑 법령 절이 INDUSTRIAL 진단에 포함됨 확인
3. SPECIAL_FACILITY 배정 건수 = 0
4. `sector_source` 기록됨

---

## WO-D-004A: Track A Check Adapter

### 목표
기존 Track A(`facility_applicability`) 결과를 표준 `CheckResult`로 변환  
**새 엔진 제작 아님 — 기존 결과 래핑만**

### ⚠️ 절대 제한
```
금지:
  - evaluate_single_factory 수정
  - evaluate_draft_for_facility 수정
  - draft_slot 수정
  - binding_field 수정
  - SemanticClause를 facility_applicability_eval에 연결 시도
    (binding_field 없어 평가 대상 0건이 됨 — 가짜 연결)

허용:
  - facility_applicability 테이블 결과 읽기
  - CheckResult 객체로 변환
  - 변환 결과를 새 파이프라인에서 참조
```

### 실측 확인 사항 (2026-06-16)
```
evaluate_single_factory 실제 동작:
  1. factories 테이블에서 사업장 row 읽음
  2. draft_slot에서 binding_field IS NOT NULL + section IN (IF_NUMERIC, IF_SCOPE) 적재
  3. evaluate_draft_for_facility에 facility row + numeric_slots + scope_slots 전달
  4. facility_applicability 테이블에 MATCH_CANDIDATE / POSSIBLE_CANDIDATE INSERT

→ SectionCandidateClause는 이 경로에 직접 진입 불가
→ D-004A는 facility_applicability 결과를 읽어 CheckResult로 변환하는 것만 담당
```

### 신규 생성 파일
```
services/check_engine_adapter.py
schemas/check_input_schema.py
routers/check_adapter_api.py
```

### CheckResult 스키마
```python
class CheckVerdict(str, Enum):
    APPLICABLE = "APPLICABLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNKNOWN = "UNKNOWN"  # 입력값 UNKNOWN 또는 binding 없음

class CheckResult(BaseModel):
    clause_id: str          # SectionCandidateClause.clause_id (연결 키)
    facility_id: str
    draft_id: Optional[str] # facility_applicability.draft_id (Track A 연결)
    verdict: CheckVerdict
    reason: str             # 판정 근거 (역추적 필수)
    applicability_status: Optional[str]  # MATCH_CANDIDATE / POSSIBLE_CANDIDATE / 없음
    check_method: str       # "track_a_facility_applicability"
```

### 어댑터 함수
```python
# check_engine_adapter.py

async def load_track_a_results(
    db,
    facility_id: str
) -> List[dict]:
    """
    facility_applicability 테이블에서
    해당 facility_id의 MATCH_CANDIDATE / POSSIBLE_CANDIDATE 읽기.
    """

def map_applicability_to_check_result(
    applicability_row: dict,
    clause_id: Optional[str] = None
) -> CheckResult:
    """
    facility_applicability row → CheckResult 변환.
    clause_id는 draft_id → semantic_clause_fix 역매핑으로 찾거나 None.
    check_method = "track_a_facility_applicability"
    """

async def run_track_a_adapter(
    db,
    facility_id: str
) -> List[CheckResult]:
    """Track A 전체 결과를 CheckResult 목록으로 반환."""
```

### 완료조건
1. `POST /check-adapter/run-track-a` + facility_id → CheckResult 목록 반환
2. 각 CheckResult에 `draft_id` + `applicability_status` + `check_method` 기록
3. `check_method = "track_a_facility_applicability"` 일관되게 기록
4. `evaluate_single_factory` 함수 시그니처 미변경 확인
5. SemanticClause → facility_applicability_eval 연결 코드 없음 확인

---

## WO-D-004B: Semantic Candidate Evaluator

### 목표
SectionCandidateClause를 사업장 프로필과 직접 비교하는 평가 전략 설계 및 구현

### ⚠️ 현재 상태: NOT IMPLEMENTED

```
미구현 이유:
  - SectionCandidateClause는 semantic_clause_fix 기반
  - semantic_clause_fix에는 binding_field 없음
  - draft_slot과 연결 없음
  - 따라서 "SemanticClause를 어떻게 사업장과 비교할 것인가"가 미설계

선행 조건:
  1. WO-D-001~007 완료 (Track A 관찰 파이프라인 구축)
  2. WO-APPENDIX-COLLECT-001 완료 (별표 본체 수집)
  3. Track A 결과와 Track B 결과 diff 분석으로 누락 의무 확인
  4. 누락 의무의 평가 방법 설계 (별표 조건 직접 비교? executor 텍스트 매칭?)

착수 금지 조건:
  - D-001~007 미완료 상태에서 이 WO 착수 금지
  - SemanticClause를 facility_applicability_eval에 억지 연결 금지
```

### 향후 설계 방향 (미확정, 참고용)
```
후보 A: executor_text + clause_text 기반 규칙 매칭
         (binding_field 없이 텍스트 패턴으로 사업장 조건 비교)
후보 B: 별표 AppendixCondition 테이블과 article_id 연결
         (WO-APPENDIX-COLLECT-001 완료 후 가능)
후보 C: GPT Compiler-003으로 actor 추출 개선 후
         constraint_node 활용 경로 재설계
```

---

## WO-D-005: KSIC Signal Engine

### 목표
`process_noun_match_stats` 활용 → KSIC 기반 의무 신호 추가  
**KSIC 신호를 제거 근거로 사용 금지**

### 신규 생성 파일
```
services/ksic_signal_service.py
schemas/ksic_signal_schema.py
routers/ksic_signal_api.py
```

### KSICSignal 스키마
```python
class KSICSignal(BaseModel):
    clause_id: str
    facility_id: str
    ksic_code: Optional[str]
    matched_process: Optional[str]
    signal_strength: float          # 0.0 ~ 1.0
    signal_source: str              # "process_noun_match" | "industry_master"
    # 이 신호는 의무 추가용. 기존 CheckResult 제거 금지.
```

### 함수 목록
```python
async def generate_ksic_signal(clause, profile, db) -> Optional[KSICSignal]
async def merge_ksic_with_check(check_result, ksic_signal) -> dict
# merge: ksic_signal 있으면 보강, 없으면 check_result 그대로
# 의무 제거 로직 절대 포함 금지
```

### 완료조건
1. `POST /ksic-signal/run` + facility_id + clause_id → KSICSignal 또는 null
2. KSIC 신호 없어도 기존 CheckResult 유지 확인
3. 의무 목록이 KSIC 처리 전후 줄어들지 않음 확인

---

## WO-D-006: Reverse Check Engine

### 목표
ObligationCandidate → "왜 포함됐는가" 역추적

### 신규 생성 파일
```
services/reverse_check_service.py
schemas/reverse_check_schema.py
routers/reverse_check_api.py
```

### ReverseCheckResult 스키마
```python
class ReverseCheckResult(BaseModel):
    clause_id: str
    facility_id: str
    law_name: str
    article_no: str
    article_title: str
    executor_text: str
    sieve_rule_matched: Optional[str]  # legal_sieve_rule.id
    sector_assigned: List[str]
    check_verdict: CheckVerdict
    check_reason: str
    check_method: str                  # "track_a_facility_applicability" 등
    ksic_boost: bool
    law_article_url: Optional[str]
    full_trace: dict
```

### 함수 목록
```python
def build_reverse_trace(obligation: ObligationCandidate) -> ReverseCheckResult
    # 순수 함수. 네트워크 호출 없음.
async def run_reverse_check_batch(obligations, db) -> List[ReverseCheckResult]
```

### 완료조건
1. `POST /reverse-check/trace` + ObligationCandidate → ReverseCheckResult
2. `sieve_rule_matched` 실제 legal_sieve_rule.id 참조
3. `law_article_url` 형식: `https://www.law.go.kr/법령/{law_name}/{article_no}`
4. `full_trace`에 경로 전체 JSON 직렬화

---

## WO-D-007: Refinery

### 목표
ObligationCandidate + ReverseCheckResult → 중복 제거 + 문장 생성 → StoredDiagnosisResult

### 신규 생성 파일
```
services/refinery_service.py
schemas/stored_diagnosis_schema.py
routers/refinery_api.py
```

### StoredDiagnosisResult 스키마
```python
class ObligationItem(BaseModel):
    obligation_id: str
    law_name: str
    article_no: str
    article_title: str
    obligation_text: str
    obligation_type: str        # APPOINT/INSPECT/ACTION/REPORT
    evidence_form: Optional[str]
    penalty_summary: Optional[str]
    trace: ReverseCheckResult

class StoredDiagnosisResult(BaseModel):
    diagnosis_id: str
    facility_id: str
    sector: Sector
    obligations: List[ObligationItem]
    total_count: int
    generated_at: datetime
    pipeline_version: str       # "WO-D-007-v1"
```

### 함수 목록
```python
def deduplicate_obligations(obligations) -> List[ObligationCandidate]
    # 중복 시 사유 기록 (DROP_DUPLICATE)
def generate_obligation_text(obligation, reverse_result) -> str
    # 형식: "[법령명] 제{article_no}조 — {executor_text}는 {action}해야 합니다."
async def emit_stored_diagnosis_result(obligations, reverse_results, profile, db) -> StoredDiagnosisResult
    # 기존 emit_stored_diagnosis_result 래핑 또는 병행. 기존 함수 수정 금지.
```

### 완료조건
1. `POST /refinery/run` + facility_id → StoredDiagnosisResult
2. `obligations[].trace`에 ReverseCheckResult 전체 포함
3. 중복 제거 전후 건수 로그 (`before_dedup`, `after_dedup`)
4. `pipeline_version: "WO-D-007-v1"` 기록
5. 기존 `emit_stored_diagnosis_result`, `assemble_refinery_result` 미삭제 확인

---

## WO-APPENDIX-COLLECT-001: 별표 수집

### 목표
시행령·시행규칙 별표/별지/서식 본체를 DB에 수집

### 배경
```
현재 상태 (2026-06-16 실측):
  산안법 시행령 제16조 article_text:
  "...선임방법은 별표 3과 같다."
  → 별표 3 본체 데이터 미수집
  → law_article에 article_type='별표' 없음
  → AppendixCondition 테이블 구축 불가

선행 조건:
  WO-D-001~007 완료 후 착수
```

### 산출물 (신규 테이블)
```sql
-- 별표 본체
CREATE TABLE law_appendix (
  id UUID PRIMARY KEY,
  law_id TEXT NOT NULL,           -- law_master.id
  article_id TEXT,                -- 참조 조문 law_article.id
  appendix_no TEXT NOT NULL,      -- "별표 3", "별지 제1호 서식"
  appendix_title TEXT,
  appendix_text TEXT,             -- raw 전문
  created_at TIMESTAMPTZ
);

-- 별표 조건 구조화
CREATE TABLE appendix_condition (
  id UUID PRIMARY KEY,
  appendix_id UUID NOT NULL,      -- law_appendix.id
  condition_text TEXT NOT NULL,   -- "제조업, 상시근로자 50명 이상"
  industry_type TEXT,             -- "제조업", "건설업" 등
  threshold_field TEXT,           -- "employee_count", "construction_amount"
  threshold_operator TEXT,        -- ">=", "<"
  threshold_value NUMERIC,
  threshold_unit TEXT,
  created_at TIMESTAMPTZ
);
```

### 성공 기준
```
산안법 시행령 별표 3 조회 시:
  SELECT * FROM appendix_condition
  WHERE appendix_id = (별표3 id)
  → 제조업 50인 이상 / 100인 이상 / 건설업 120억 이상 등 행 존재
```

### 착수 금지 조건
- WO-D-001~007 미완료 상태에서 착수 금지
- 별표 수집기 코드를 GPT 전속 영역(law_collector.py) 내부에 직접 작성 금지
  → 별도 파일(`routers/law_appendix_collector.py`)로 분리

---

## 전체 파이프라인 관찰 엔드포인트 (WO-D-007 완료 후)

```
GET  /pipeline/status
     → 각 단계별 처리 건수
     {"semantic": N, "common_sieve": {keep, drop, pending},
      "section": {INDUSTRIAL, BUILDING, CONSTRUCTION},
      "check_track_a": {applicable, unknown},
      "refinery": {total_obligations}}

GET  /pipeline/trace/{clause_id}
     → 특정 clause의 전체 통과 경로

POST /pipeline/run/{facility_id}
     → 특정 사업장 전체 파이프라인 실행 (개발·검증용)
```

---

## 테이블 요약

| 단계 | 읽는 테이블 | 쓰는 곳 |
|------|------------|----------|
| D-001 | semantic_clause_fix, law_article_part, law_article, law_master | 메모리 객체 |
| D-002 | legal_sieve_rule | 메모리 객체 |
| D-003 | law_sector_mapping | 메모리 객체 |
| D-004A | facility_applicability (읽기만) | 메모리 객체 |
| D-004B | 미설계 (WO-APPENDIX 완료 후) | — |
| D-005 | process_noun_match_stats, industry_master | 메모리 객체 |
| D-006 | (없음 — 순수 변환) | 메모리 객체 |
| D-007 | (전 단계 메모리) | stored_diagnosis_result (기존) |
| APPENDIX-001 | law_master, law_article | law_appendix, appendix_condition (신규) |

**D-001~007: DB 스키마 변경 없음. 신규 테이블 없음. 기존 테이블 삭제 없음.**

---

## 검증 기준

글읽기 검증 (카운트 아님):
1. D-002 완료: KEEP 10개 샘플 → executor_text가 사업주 주체인지 확인
2. D-004A 완료: CheckResult 5개 → reason이 말이 되는지 확인
3. D-006 완료: ReverseCheckResult 3개 → 경로가 통과 사유와 일치하는지 확인
4. D-007 완료: StoredDiagnosisResult 1개 → obligations 전체 글읽기

기계 검증:
- 각 단계 건수 감소 시 이유가 trace에 기록됐는지
- PENDING/UNKNOWN 건이 소멸되지 않고 보류 유지되는지

---

## 파일 배치 요약

```
tai-api/
├── schemas/
│   ├── semantic_clause_schema.py      # D-001
│   ├── candidate_clause_schema.py     # D-002
│   ├── section_candidate_schema.py    # D-003
│   ├── check_input_schema.py          # D-004A
│   ├── ksic_signal_schema.py          # D-005
│   ├── reverse_check_schema.py        # D-006
│   └── stored_diagnosis_schema.py     # D-007
├── services/
│   ├── semantic_clause_service.py     # D-001
│   ├── common_sieve_service.py        # D-002
│   ├── section_sieve_service.py       # D-003
│   ├── check_engine_adapter.py        # D-004A
│   ├── ksic_signal_service.py         # D-005
│   ├── reverse_check_service.py       # D-006
│   └── refinery_service.py            # D-007
└── routers/
    ├── semantic_pipeline_api.py       # D-001
    ├── common_sieve_api.py            # D-002
    ├── section_sieve_api.py           # D-003
    ├── check_adapter_api.py           # D-004A
    ├── ksic_signal_api.py             # D-005
    ├── reverse_check_api.py           # D-006
    ├── refinery_api.py                # D-007
    └── law_appendix_collector.py      # APPENDIX-001
```

모든 신규 router → `router_registry/` 해당 group에 등록 필수.
