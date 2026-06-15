# 법령엔진 15차 구현 작업지시 (WO-D-001 ~ WO-D-007)

작성일: 2026-06-16  
상태: 승인 대기 → 순차 실행

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

새 파이프라인은 기존 경로와 병행 실행. 기존 경로는 건드리지 않는다.
```

---

## 구현 순서 (반드시 이 순서로)

```
WO-D-001  Semantic Clause Pipeline
    ↓
WO-D-002  Common Sieve Engine  
    ↓
WO-D-003  Section Sieve
    ↓
WO-D-004  Check Engine Adapter
    ↓
WO-D-005  KSIC Signal Engine
    ↓
WO-D-006  Reverse Check Engine
    ↓
WO-D-007  Refinery
```

각 WO는 이전 WO 완료 확인 후 착수. 완료조건 미충족 시 다음 단계 진행 금지.

---

## WO-D-001: Semantic Clause Pipeline

### 목표
`semantic_clause_fix` → 표준 `SemanticClause` 객체 생성기 구축  
조문(law_article_part) → 의미절 저장소 완성

### 관련 기존 파일
- `routers/anonymous_diagnosis.py` — 현재 `semantic_clause_fix` 직접 조회
- `routers/legal_engine.py` — 법령엔진 진입점
- DB 테이블: `semantic_clause_fix` (49,997 parts), `law_article_part` (143,549)

### 신규 생성 파일
```
services/
  semantic_clause_service.py   # SemanticClause 생성·조회 서비스
schemas/
  semantic_clause_schema.py    # SemanticClause Pydantic 모델
routers/
  semantic_pipeline_api.py     # 관리용 API 엔드포인트
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
    clause_text: str            # semantic_clause_fix.clause_text (또는 part text)
    sector_hint: Optional[str]  # INDUSTRIAL/BUILDING/CONSTRUCTION/None
    source_span: Optional[str]  # 원문 위치
    created_at: datetime
```

### DB 조회 쿼리 (서비스 내부)
```sql
-- semantic_clause_fix + law_article + law_master JOIN
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
# semantic_clause_service.py

async def get_semantic_clauses(
    db,
    law_id: Optional[str] = None,
    sector: Optional[str] = None,
    limit: int = 1000,
    offset: int = 0
) -> List[SemanticClause]:
    """SemanticClause 목록 조회. 페이지네이션 필수."""

async def get_semantic_clause_by_id(
    db,
    clause_id: str
) -> Optional[SemanticClause]:
    """단건 조회. 역추적용."""

async def count_semantic_clauses(
    db,
    law_id: Optional[str] = None
) -> int:
    """총 건수 확인용."""
```

### 완료조건
1. `GET /semantic-pipeline/clauses?limit=10` → SemanticClause 목록 반환
2. `GET /semantic-pipeline/clauses/count` → `{"total": N}` (N은 실제 DB 건수)
3. executor_text가 null/빈문자인 행은 결과에서 제외됨을 확인
4. 기존 `anonymous_diagnosis.py` 미수정 상태 유지

---

## WO-D-002: Common Sieve Engine

### 목표
`legal_sieve_rule` (2,219개 완성) → SemanticClause 적용 → CandidateClause 생성  
AUTHORITY 제거 / BUSINESS 유지 / FRAGMENT 제거

### 관련 기존 파일
- `routers/admin_executor_llm_fix.py` — `sieve_executor()`, `run_common_sieve()`, `diagnose_clauses_common()` 포함
- DB 테이블: `legal_sieve_rule` (2,219개), `semantic_clause_fix`

### 신규 생성 파일
```
services/
  common_sieve_service.py      # 거름망 적용 서비스
schemas/
  candidate_clause_schema.py   # CandidateClause Pydantic 모델
routers/
  common_sieve_api.py          # 실행·조회 API
```

### CandidateClause 객체 스키마
```python
class SieveResult(str, Enum):
    KEEP = "KEEP"       # BUSINESS — 다음 단계로
    DROP = "DROP"       # AUTHORITY/FRAGMENT — 제거
    PENDING = "PENDING" # 애매 — 보류, 소멸 금지

class CandidateClause(BaseModel):
    clause_id: str              # SemanticClause.clause_id
    part_id: str
    article_id: str
    law_id: str
    law_name: str
    article_no: str
    executor_text: str
    clause_text: str
    sieve_result: SieveResult   # KEEP/DROP/PENDING
    sieve_rule_id: Optional[str] # 매칭된 legal_sieve_rule.id (역추적)
    sieve_reason: Optional[str]  # 매칭된 rule의 executor_class
    sector_hint: Optional[str]
```

### 거름 로직 (기존 sieve_executor 활용)
```python
# common_sieve_service.py

async def apply_common_sieve(
    clause: SemanticClause,
    sieve_rules: List[dict]  # legal_sieve_rule 캐시
) -> CandidateClause:
    """
    1. executor_text를 sieve_rules와 대조 (word 매칭)
    2. DROP 룰 매칭 → SieveResult.DROP
    3. KEEP 룰 매칭 → SieveResult.KEEP  
    4. 미매칭 → SieveResult.PENDING (소멸 금지)
    sieve_rule_id, sieve_reason 반드시 기록
    """

async def run_common_sieve_batch(
    db,
    law_id: Optional[str] = None,
    batch_size: int = 500
) -> dict:
    """
    전체 또는 특정 법령의 SemanticClause에 거름망 적용
    반환: {"total": N, "keep": K, "drop": D, "pending": P}
    """

async def get_candidate_clauses(
    db,
    sieve_result: Optional[SieveResult] = None,
    law_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[CandidateClause]:
    """결과 조회. sieve_result 필터 가능."""
```

### 완료조건
1. `POST /common-sieve/run` → `{"keep": K, "drop": D, "pending": P}` 반환
2. `GET /common-sieve/candidates?sieve_result=KEEP&limit=10` → KEEP 목록
3. DROP 결과에 `sieve_rule_id` + `sieve_reason` 기록됨 (trace 가능)
4. PENDING (미매칭) 건수 확인 가능
5. 기존 `admin_executor_llm_fix.py`의 `sieve_executor` 미수정

---

## WO-D-003: Section Sieve

### 목표
CandidateClause(KEEP) → 섹터별(산업/건설/건물) 분리 → SectionCandidateClause  
SPECIAL_FACILITY 미사용 (의도적 휴면 유지)

### 관련 기존 파일
- DB 테이블: `law_sector_mapping` (섹터-법령 매핑), `legal_sieve_rule`
- `routers/anonymous_diagnosis.py` — 현재 sector 필터 로직 참조

### 신규 생성 파일
```
services/
  section_sieve_service.py
schemas/
  section_candidate_schema.py
routers/
  section_sieve_api.py
```

### SectionCandidateClause 객체 스키마
```python
class Sector(str, Enum):
    INDUSTRIAL = "INDUSTRIAL"
    BUILDING = "BUILDING"
    CONSTRUCTION = "CONSTRUCTION"
    # SPECIAL_FACILITY: 의도적 미사용

class SectionCandidateClause(BaseModel):
    clause_id: str
    part_id: str
    article_id: str
    law_id: str
    law_name: str
    article_no: str
    executor_text: str
    clause_text: str
    sieve_result: SieveResult       # 상위에서 KEEP
    assigned_sectors: List[Sector]  # 복수 섹터 가능 (교차 적용 법령)
    sector_source: str              # "law_sector_mapping" | "clause_hint" | "universal"
    # universal: 미매핑 법령 → 모든 섹터 통과 ("가지고 감" 원칙 유지)
```

### 섹터 판정 로직
```python
async def assign_sector(
    clause: CandidateClause,
    sector_mapping: dict  # law_id → [sector] 캐시
) -> SectionCandidateClause:
    """
    1. law_sector_mapping에서 해당 law_id 조회
    2. 매핑 있음 → assigned_sectors = 매핑된 섹터들
    3. 매핑 없음 → assigned_sectors = [INDUSTRIAL, BUILDING, CONSTRUCTION]
                   sector_source = "universal" (미매핑 통과 원칙)
    4. SPECIAL_FACILITY 절대 할당 금지
    """
```

### 입력
```python
class SectionSieveInput(BaseModel):
    facility_sector: Sector  # FacilityProfile에서 옴: INDUSTRIAL/BUILDING/CONSTRUCTION
```

### 완료조건
1. `POST /section-sieve/run` + `{"facility_sector": "INDUSTRIAL"}` → INDUSTRIAL 해당 후보 반환
2. 미매핑 법령의 절이 INDUSTRIAL 진단에도 포함됨 확인
3. SPECIAL_FACILITY 배정 건수 = 0 확인
4. `assigned_sectors`와 `sector_source` 기록됨 (trace 가능)

---

## WO-D-004: Check Engine Adapter

### 목표
FacilityProfile + SectionCandidateClause → CheckInput 변환 → CheckResult 생성  
기존 `facility_applicability_eval` 유지, 어댑터만 추가

### 관련 기존 파일
- `routers/anonymous_diagnosis.py` — `facility_applicability_eval` 호출 위치 확인
- `routers/legal_adapter_api.py` — 현재 어댑터 스텁
- `routers/legal_adapter_test.py` — 어댑터 테스트
- DB 테이블: `factories` (사업장 프로필 소스)

### 신규 생성 파일
```
services/
  check_engine_adapter.py      # CandidateClause → CheckInput 변환
schemas/
  check_input_schema.py        # CheckInput / CheckResult Pydantic 모델
routers/
  check_adapter_api.py         # 변환·실행 API
```

### FacilityProfile 객체 스키마 (입력 표준)
```python
class TriState(str, Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    UNKNOWN = "UNKNOWN"  # 결측 = UNKNOWN (0 기입 금지)

class FacilityProfile(BaseModel):
    facility_id: str
    sector: Sector
    # 수량 지표
    regular_workers: Optional[int]       # None = UNKNOWN
    construction_amount: Optional[float] # None = UNKNOWN  
    total_floor_area: Optional[float]    # None = UNKNOWN
    # TriState 표현이 필요한 경우
    worker_state: TriState = TriState.UNKNOWN
    # 원본 factories 테이블 컬럼 그대로 보존
    raw_factory_data: Optional[dict]
```

### CheckInput / CheckResult 스키마
```python
class CheckInput(BaseModel):
    clause_id: str
    facility_profile: FacilityProfile
    clause_text: str
    executor_text: str
    law_name: str
    article_no: str

class CheckVerdict(str, Enum):
    APPLICABLE = "APPLICABLE"     # 해당됨
    NOT_APPLICABLE = "NOT_APPLICABLE" # 해당 안 됨
    UNKNOWN = "UNKNOWN"           # 판단 불가 (입력값 UNKNOWN)

class CheckResult(BaseModel):
    clause_id: str
    facility_id: str
    verdict: CheckVerdict
    reason: str                   # 판정 근거 (역추적 필수)
    matched_condition: Optional[str]  # 어떤 조건이 매칭됐는지
    check_method: str             # "facility_applicability_eval" | "adapter_rule"
```

### 어댑터 함수 목록
```python
# check_engine_adapter.py

def build_check_input(
    clause: SectionCandidateClause,
    profile: FacilityProfile
) -> CheckInput:
    """CandidateClause + FacilityProfile → CheckInput 변환. 순수 함수."""

async def run_check(
    check_input: CheckInput,
    db
) -> CheckResult:
    """
    기존 facility_applicability_eval 호출.
    결과를 CheckResult로 래핑.
    기존 함수 수정 금지 — 래핑만.
    """

async def run_check_batch(
    clauses: List[SectionCandidateClause],
    profile: FacilityProfile,
    db
) -> List[CheckResult]:
    """배치 실행. 결과에 verdict별 통계 포함."""
```

### 완료조건
1. `POST /check-adapter/run` + FacilityProfile + clause_id → CheckResult 반환
2. CheckResult에 `reason` + `check_method` 필드 채워짐 (역추적 가능)
3. 입력값 UNKNOWN인 경우 verdict = UNKNOWN (0 자동 변환 금지)
4. 기존 `facility_applicability_eval` 함수 시그니처 미변경 확인

---

## WO-D-005: KSIC Signal Engine

### 목표
`process_noun_match_stats` 활용 → KSIC 기반 의무 신호 추가  
CheckResult에 KSIC 신호를 보강. 의무 제거 금지.

### 관련 기존 파일
- `routers/ksic_engine.py` — KSIC 엔진 기존 구현
- DB 테이블: `process_noun_match_stats`, `ksic_process_map` (6,957), `industry_master` (501)

### 신규 생성 파일
```
services/
  ksic_signal_service.py
schemas/
  ksic_signal_schema.py
routers/
  ksic_signal_api.py
```

### KSICSignal 객체 스키마
```python
class KSICSignal(BaseModel):
    clause_id: str
    facility_id: str
    ksic_code: Optional[str]        # 사업장 KSIC 코드
    matched_process: Optional[str]  # 매칭된 공정명
    signal_strength: float          # 0.0 ~ 1.0 (매칭 강도)
    signal_source: str              # "process_noun_match" | "industry_master"
    # 중요: 이 신호는 의무 추가용. 기존 CheckResult 제거 금지.
```

### KSIC 신호 로직
```python
async def generate_ksic_signal(
    clause: SectionCandidateClause,
    profile: FacilityProfile,
    db
) -> Optional[KSICSignal]:
    """
    1. profile에서 KSIC 코드 추출
    2. process_noun_match_stats에서 해당 공정의 법령 매칭 조회
    3. 현재 clause_id와 매칭 여부 확인
    4. 매칭 시 KSICSignal 생성 (signal_strength 포함)
    5. 미매칭 시 None 반환 (기존 CheckResult 건드리지 않음)
    """

async def merge_ksic_with_check(
    check_result: CheckResult,
    ksic_signal: Optional[KSICSignal]
) -> dict:
    """
    CheckResult + KSICSignal 병합.
    ksic_signal이 있으면 보강, 없으면 check_result 그대로.
    의무 제거 로직 절대 포함 금지.
    """
```

### 완료조건
1. `POST /ksic-signal/run` + facility_id + clause_id → KSICSignal 또는 null 반환
2. KSICSignal이 있는 경우 `signal_source` 기록됨
3. KSIC 신호가 없어도 기존 CheckResult 유지됨 확인
4. 의무 목록이 KSIC 처리 전후 줄어들지 않음 확인

---

## WO-D-006: Reverse Check Engine

### 목표
ObligationCandidate → "왜 포함됐는가" 역추적  
check_method + sieve_rule + sector 경로를 역으로 재구성

### 관련 기존 파일
- `routers/obligation_bridge.py` — ObligationCandidate 관련
- `routers/legal_engine_patch.py` — 패치 이력

### 신규 생성 파일
```
services/
  reverse_check_service.py
schemas/
  reverse_check_schema.py
routers/
  reverse_check_api.py
```

### ObligationCandidate 입력 스키마
```python
class ObligationCandidate(BaseModel):
    clause_id: str
    facility_id: str
    check_result: CheckResult
    ksic_signal: Optional[KSICSignal]
    section_candidate: SectionCandidateClause
```

### ReverseCheckResult 스키마
```python
class ReverseCheckResult(BaseModel):
    clause_id: str
    facility_id: str
    # 경로 역추적
    law_name: str
    article_no: str
    article_title: str
    executor_text: str          # 원문 주체
    sieve_rule_matched: Optional[str]  # 어떤 거름룰이 KEEP 판정했나
    sector_assigned: List[str]  # 어떤 섹터로 배정됐나
    check_verdict: CheckVerdict # APPLICABLE/UNKNOWN
    check_reason: str           # facility_applicability_eval 판정 근거
    ksic_boost: bool            # KSIC 신호로 보강됐는지
    # 원문 링크
    law_article_url: Optional[str]  # law_id + article_no 조합
    full_trace: dict            # 위 전체를 dict로 직렬화
```

### 역추적 함수
```python
def build_reverse_trace(
    obligation: ObligationCandidate
) -> ReverseCheckResult:
    """
    ObligationCandidate의 모든 필드에서 경로를 역으로 재구성.
    네트워크 호출 없음 — 순수 함수.
    """

async def run_reverse_check_batch(
    obligations: List[ObligationCandidate],
    db
) -> List[ReverseCheckResult]:
    """배치 역추적. 결과를 DB 저장 없이 반환."""
```

### 완료조건
1. `POST /reverse-check/trace` + ObligationCandidate → ReverseCheckResult 반환
2. `sieve_rule_matched` 필드가 실제 legal_sieve_rule.id 참조
3. `law_article_url` 형식: `https://www.law.go.kr/법령/{law_name}/{article_no}`
4. `full_trace`에 경로 전체가 JSON으로 직렬화됨

---

## WO-D-007: Refinery

### 목표
ObligationCandidate + ReverseCheckResult → 중복 제거 + 유사 의무 통합 + 결과 문장 생성  
→ StoredDiagnosisResult 저장

### 관련 기존 파일
- `routers/diagnosis_transform.py` — 기존 변환 로직
- `routers/diagnosis_result_web.py` — 결과 표시
- `routers/anonymous_diagnosis.py` — `assemble_refinery_result`, `emit_stored_diagnosis_result` 포함
- DB 테이블: `stored_diagnosis_result` (또는 동등 테이블)

### 신규 생성 파일
```
services/
  refinery_service.py
schemas/
  stored_diagnosis_schema.py
routers/
  refinery_api.py
```

### 중복 제거 기준
```python
# 같은 의무로 판단하는 기준 (이 중 하나라도 해당 시 중복)
# 1. article_id 동일 + executor_text 유사도 > 0.8
# 2. clause_text 핵심어 90% 이상 겹침
# → 더 구체적인 것(article_no가 작은 것 또는 clause_text가 긴 것) 우선 유지
```

### StoredDiagnosisResult 스키마
```python
class ObligationItem(BaseModel):
    obligation_id: str          # UUID
    law_name: str
    article_no: str
    article_title: str
    obligation_text: str        # 생성된 의무 문장
    obligation_type: str        # APPOINT/INSPECT/ACTION/REPORT 등
    evidence_form: Optional[str]  # 관련 서식
    penalty_summary: Optional[str]  # 벌칙 요약
    trace: ReverseCheckResult   # 역추적 전체

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
# refinery_service.py

def deduplicate_obligations(
    obligations: List[ObligationCandidate]
) -> List[ObligationCandidate]:
    """중복 제거. 소멸 시 사유 기록 (DROP_DUPLICATE)."""

def generate_obligation_text(
    obligation: ObligationCandidate,
    reverse_result: ReverseCheckResult
) -> str:
    """
    의무 문장 생성.
    형식: "[법령명] 제{article_no}조 — {executor_text}는 {action_summary}해야 합니다."
    """

async def emit_stored_diagnosis_result(
    obligations: List[ObligationCandidate],
    reverse_results: List[ReverseCheckResult],
    profile: FacilityProfile,
    db
) -> StoredDiagnosisResult:
    """
    기존 emit_stored_diagnosis_result 래핑 또는 병행 저장.
    기존 함수 수정 금지.
    """
```

### 완료조건
1. `POST /refinery/run` + facility_id → StoredDiagnosisResult 반환
2. `obligations[].trace` 필드에 ReverseCheckResult 전체 포함
3. 중복 제거 전후 건수 로그 출력 (`before_dedup`, `after_dedup`)
4. `pipeline_version: "WO-D-007-v1"` 기록됨
5. 기존 `emit_stored_diagnosis_result`, `assemble_refinery_result` 함수 미삭제 확인

---

## 전체 파이프라인 관찰 엔드포인트 (WO-D-007 완료 후)

```
GET  /pipeline/status
     → 각 WO 단계별 처리 건수 현황
     {"semantic": N, "common_sieve": {keep, drop, pending},
      "section": {INDUSTRIAL, BUILDING, CONSTRUCTION},
      "check": {applicable, not_applicable, unknown},
      "refinery": {total_obligations}}

GET  /pipeline/trace/{clause_id}
     → 특정 clause가 파이프라인을 어떻게 통과했는지 전체 경로

POST /pipeline/run/{facility_id}
     → 특정 사업장 전체 파이프라인 실행 (개발·검증용)
```

---

## 테이블 요약 (신규 생성 없음 — 기존 테이블 활용)

| 단계 | 읽는 테이블 | 쓰는 곳 |
|------|------------|----------|
| D-001 | semantic_clause_fix, law_article_part, law_article, law_master | 메모리 객체 |
| D-002 | legal_sieve_rule | 메모리 객체 |
| D-003 | law_sector_mapping | 메모리 객체 |
| D-004 | factories | 메모리 객체 |
| D-005 | process_noun_match_stats, industry_master | 메모리 객체 |
| D-006 | (없음 — 순수 변환) | 메모리 객체 |
| D-007 | (전 단계 메모리) | stored_diagnosis_result (기존 테이블) |

**DB 스키마 변경 없음. 신규 테이블 생성 없음. 기존 테이블 삭제 없음.**

---

## 검증 기준 (각 WO 완료 시)

글읽기 검증 대상 (카운트 아님):
1. D-002 완료 시: KEEP 된 절 10개 샘플 → executor_text 읽어서 사업주 주체인지 확인
2. D-004 완료 시: CheckResult APPLICABLE 5개 → reason 읽어서 말이 되는지 확인
3. D-006 완료 시: ReverseCheckResult 3개 → 경로가 실제 통과 사유와 일치하는지 확인
4. D-007 완료 시: StoredDiagnosisResult 1개 → obligations 전체 글읽기

기계 검증:
- 각 단계 건수가 이전 단계보다 줄면 줄어든 이유가 trace에 기록됐는지 확인
- PENDING/UNKNOWN 건이 소멸되지 않고 보류 상태로 유지되는지 확인

---

## 파일 배치 요약

```
tai-api/
├── schemas/
│   ├── semantic_clause_schema.py      # D-001
│   ├── candidate_clause_schema.py     # D-002  
│   ├── section_candidate_schema.py    # D-003
│   ├── check_input_schema.py          # D-004
│   ├── ksic_signal_schema.py          # D-005
│   ├── reverse_check_schema.py        # D-006
│   └── stored_diagnosis_schema.py     # D-007
├── services/
│   ├── semantic_clause_service.py     # D-001
│   ├── common_sieve_service.py        # D-002
│   ├── section_sieve_service.py       # D-003
│   ├── check_engine_adapter.py        # D-004
│   ├── ksic_signal_service.py         # D-005
│   ├── reverse_check_service.py       # D-006
│   └── refinery_service.py            # D-007
└── routers/
    ├── semantic_pipeline_api.py       # D-001
    ├── common_sieve_api.py            # D-002
    ├── section_sieve_api.py           # D-003
    ├── check_adapter_api.py           # D-004
    ├── ksic_signal_api.py             # D-005
    ├── reverse_check_api.py           # D-006
    └── refinery_api.py                # D-007
```

모든 신규 router → `router_registry/` 해당 group에 등록 필수.
