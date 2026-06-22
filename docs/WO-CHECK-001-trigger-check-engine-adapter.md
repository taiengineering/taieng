# WO-CHECK-001
Trigger 후보 → 기존 Check Engine 연결 어댑터 설계서

작성일: 2026-06-22
작성자: Claude (설계 전담)
단계: 해결책 강구 (구현 없음)

---

## 0. 설계 전제

코드 확인 완료:
- `services/facility_applicability_eval.py` — `evaluate_draft_for_facility()` 함수 (Pure logic, no DB I/O)
- `engine/six_w_heuristic.py` — `extract_six_w()` 함수
- `scripts/run_facility_applicability.py` — 배치 실행 스크립트

**절대 수정 금지 함수:**
- `evaluate_draft_for_facility()` — services/facility_applicability_eval.py
- `evaluate_scope_check()`, `evaluate_numeric_check()` — 동일 파일
- `extract_six_w()` — engine/six_w_heuristic.py

---

## 1. 기존 Check Engine 재사용 범위

### 코드 레벨 확인

```python
# evaluate_draft_for_facility 시그니처
def evaluate_draft_for_facility(
    facility: Dict[str, Any],      # ← 소비자 입력 (factories row)
    draft_id: str,                  # ← executable_draft.id
    numeric_slots: List[Dict],      # ← draft_slot (IF_NUMERIC, binding_field, operator, value)
    scope_slots: List[Dict],        # ← draft_slot (IF_SCOPE, binding_field)
) -> Optional[Tuple[str, str, List[CheckResult]]]:
    # Returns: (overall_status, part_id, check_results) or None
```

### FIELD_MAP 현황 (기존 정의)

```python
FIELD_MAP = {
    "employee_count":     ("employee_count",           "DIRECT"),
    "area_size":          ("building_area",             "DIRECT"),
    "power_capacity":     ("electrical_capacity_kw",   "DIRECT"),
    "voltage_level":      ("transformer_capacity_kva", "AMBIGUOUS"),
    "storage_capacity":   ("gas_capacity_m3",           "AMBIGUOUS"),
    "equipment_type":     (None,                        "EQUIPMENT_JOIN"),
    "facility_type":      ("site_type",                 "AMBIGUOUS"),
    "process_type":       ("ksic_code",                 "AMBIGUOUS"),
    "monetary_value":     ("construction_amount",       "AMBIGUOUS"),
    "concentration_level":(None,                        "MISSING"),
    "distance_value":     (None,                        "MISSING"),
}
```

### 그대로 재사용 가능한 것

```
evaluate_draft_for_facility()   → 로직 그대로 사용
evaluate_numeric_check()        → 로직 그대로 사용
evaluate_scope_check()          → 로직 그대로 사용
aggregate_applicability_status()→ 로직 그대로 사용
extract_six_w()                 → 로직 그대로 사용
facility_applicability 테이블   → 구조 그대로 사용
task_candidate 유형 체계         → 그대로 사용
runtime_metadata_resolution     → 6W 구조 그대로 사용
```

### 수정 없이 활용 조건

`evaluate_draft_for_facility()`는 `executable_draft.id`를 `draft_id`로 받는다.
Trigger 기반 구조에서는 `executable_draft`가 없다.

→ **어댑터가 필요한 이유**: `semantic_clause_id`를 `executable_draft` 없이
  직접 체크엔진에 넘길 수 없다. 어댑터가 변환을 담당한다.

---

## 2. Adapter 입력 정의

WO-TRIGGER-001 의무후보 구조:

```json
{
  "candidate_id": "uuid",
  "semantic_clause_id": "uuid",
  "trigger_codes": ["WORK:CONFINED_SPACE"],
  "trigger_route": "A",
  "match_source": "condition_text",
  "confidence": "HIGH",
  "reason": "condition_text에서 '밀폐공간' 직접 매칭"
}
```

체크엔진에 넘기려면 추가로 필요한 필드:

```json
{
  "candidate_id": "uuid",
  "semantic_clause_id": "uuid",
  "trigger_codes": ["WORK:CONFINED_SPACE"],
  "trigger_route": "A",
  "match_source": "condition_text",
  "confidence": "HIGH",
  "reason": "...",

  // === 어댑터가 추가하는 필드 ===
  "source_article_id": "uuid",      // semantic_clause.source_article_id
  "executor_text": "사업주",         // semantic_clause.executor_text
  "condition_text": "...",          // semantic_clause.condition_text (원문)
  "action_text": "...",             // semantic_clause.action_text (원문)
  "satisfied_by": {                 // Trigger를 충족시킨 입력값
    "field": "has_confined_space",
    "value": true
  },
  "numeric_slots": [],             // 체크엔진 numeric_slots 형식
  "scope_slots": []                // 체크엔진 scope_slots 형식
}
```

---

## 3. Adapter 출력 정의

### 선택: A. facility_applicability 직접 생성

근거:
- facility_applicability가 이미 check 결과 저장 테이블로 설계됨
- task_candidate가 facility_applicability.id를 참조함
- runtime_candidate가 facility_applicability 이후 단계에서 생성됨
- 기존 평가 로직(aggregate_applicability_status)을 그대로 사용 가능

대안 B(runtime_candidate 직접), C(임시 구조), D(view)보다 A가 최소 수정이다.

어댑터 출력 구조:
```
facility_applicability 레코드:
  factory_id           → 소비자 factory_id
  draft_id             → semantic_clause_id (UUID 그대로 사용)
  part_id              → semantic_clause.source_part_id
  applicability_status → evaluate_draft_for_facility() 반환값
  match_details        → { trigger_codes, satisfied_by, confidence }
```

**핵심 설계 결정**: `draft_id` 컬럼에 `semantic_clause_id`를 넣는다.
기존 체크엔진에서 `draft_id`는 `executable_draft.id`를 참조하지만,
facility_applicability 테이블 자체에 FK 제약이 없으므로 가능하다.
이후 단계에서 `match_details.source = 'trigger_based'`로 구분한다.

---

## 4. 최적 연결 지점

**A. facility_applicability 직접 생성** — 선택

```
[어댑터 처리 흐름]

1. 의무후보 배치 (300~600건) 수신
2. semantic_clause 조회 (source_article_id, executor_text, condition_text)
3. Trigger → numeric_slots/scope_slots 변환 (아래 §5 참조)
4. evaluate_draft_for_facility() 호출 (수정 없음)
5. 결과를 facility_applicability에 INSERT
   (draft_id = semantic_clause_id, source = 'trigger_based')
6. MATCH_CANDIDATE → task_candidate 자동 생성 (기존 로직 활용)
```

**채택 이유:**
- evaluate_draft_for_facility() 수정 불필요
- 기존 task_candidate 생성 파이프라인 그대로 연결
- facility_applicability.match_details에 trigger 정보 추가로 구분 가능
- 소규모 변경으로 최대 재사용

---

## 5. binding_field 확장 설계

### 기존 binding_field vs 신규 Trigger 필요 binding_field

| 신규 binding_field | Trigger | factories 컬럼 | match_quality |
|---|---|---|---|
| has_confined_space | WORK:CONFINED_SPACE | has_confined_space | DIRECT |
| has_blasting | WORK:BLASTING | has_blasting | DIRECT |
| has_diving | WORK:DIVING | has_diving | DIRECT |
| has_asbestos_demo | WORK:ASBESTOS | has_asbestos_demo | DIRECT |
| has_tower_crane | WORK:HIGH_PRESSURE / EQUIPMENT:TOWER_CRANE | has_tower_crane, has_high_pressure_gas | DIRECT |
| has_high_pressure_gas | WORK:HIGH_PRESSURE | has_high_pressure_gas | DIRECT |
| has_chemical_substance | HAZARD_FACTOR:CHEMICAL | has_chemical_substance | DIRECT |
| has_boiler | EQUIPMENT:BOILER | has_boiler | DIRECT |
| equipment_type_code | EQUIPMENT:CRANE 등 | (equipment_assets JOIN) | EQUIPMENT_JOIN |
| ksic_code | INDUSTRY:CONSTRUCTION | ksic_code | DIRECT |
| construction_amount | THRESHOLD:CONSTRUCTION_20BIL | construction_amount | DIRECT |
| building_area | THRESHOLD:AREA_400_PLUS | building_area | DIRECT |
| hazard_factor_code | HAZARD_FACTOR:DUST 등 | (hazard_factor_codes 신규) | DIRECT (신규 입력 후) |

### 어댑터가 Trigger → numeric_slots/scope_slots 변환하는 방법

```
Trigger 타입별 변환 규칙:

BUSINESS:REGISTERED
  → numeric_slots: [] / scope_slots: []
  → applicability_status: 직접 MATCH_CANDIDATE 설정 (슬롯 없음)

THRESHOLD:EMPLOYEE_50_PLUS
  → numeric_slots: [{ binding_field: 'employee_count', operator: '>=', value: 50 }]
  → scope_slots: []

WORK:CONFINED_SPACE
  → numeric_slots: []
  → scope_slots: [{ binding_field: 'has_confined_space', family: 'WORK_FLAG' }]
  (FIELD_MAP에 'has_confined_space' → ('has_confined_space', 'DIRECT') 추가 필요)

EQUIPMENT:CRANE
  → numeric_slots: []
  → scope_slots: [{ binding_field: 'equipment_type_code', family: 'EQUIPMENT_SCOPE' }]
  (evaluate_scope_check에서 equipment_assets JOIN 로직 기존과 동일)

HAZARD_FACTOR:CHEMICAL
  → scope_slots: [{ binding_field: 'has_chemical_substance', family: 'HAZARD_FLAG' }]
```

### FIELD_MAP 확장 범위 (어댑터 파일에서 정의, facility_applicability_eval.py 수정 불필요)

```python
# 어댑터 전용 FIELD_MAP 확장 (기존 파일 수정 없음, 어댑터에서 덮어씌움)
TRIGGER_FIELD_MAP_EXTENSION = {
    "has_confined_space":    ("has_confined_space",   "DIRECT"),
    "has_blasting":          ("has_blasting",          "DIRECT"),
    "has_diving":            ("has_diving",            "DIRECT"),
    "has_asbestos_demo":     ("has_asbestos_demo",     "DIRECT"),
    "has_high_pressure_gas": ("has_high_pressure_gas", "DIRECT"),
    "has_chemical_substance":("has_chemical_substance","DIRECT"),
    "has_boiler":            ("has_boiler",            "DIRECT"),
    "has_tower_crane":       ("has_tower_crane",       "DIRECT"),
    "ksic_code":             ("ksic_code",             "DIRECT"),
    "equipment_type_code":   (None,                    "EQUIPMENT_JOIN"),
    "hazard_factor_code":    (None,                    "MISSING"),  # 신규 입력 전까지
}
```

---

## 6. MISSING_DATA 제거 전략

### 기존 MISSING_DATA 95.7% 원인

```
NO_FACILITY_COLUMN (21,600건): concentration_level, distance_value
  → factories 테이블에 해당 컬럼 없음

FACILITY_VALUE_NULL (6,770건): 컬럼은 있으나 값 없음
  → employee_count=NULL 등 입력 미완료
```

### 신규 구조에서 MISSING_DATA 제거 방법

**원칙: Trigger 기반 후보는 이미 조건이 충족된 것만 생성된다.**

```
BUSINESS:REGISTERED → 항상 MATCH_CANDIDATE (슬롯 검사 불필요)
WORK:CONFINED_SPACE → has_confined_space=true인 경우에만 Trigger 생성
                       → evaluate_scope_check() 호출 시 MISSING_DATA 불가
EQUIPMENT:CRANE     → equipment_assets에 CRANE이 있을 때 Trigger 생성
                       → 해당 facility에 CRANE 존재 = MATCH_CANDIDATE

즉, 어댑터는 "Trigger가 발생한 사실 자체"를 satisfied_by로 전달하고
evaluate_draft_for_facility()는 그것을 재검증하는 역할만 한다.

MISSING_DATA는 오직:
  - Route B(THRESHOLD) 후보 중 numeric_slots 값이 NULL인 경우만 발생
  - 이 경우는 어댑터가 사전에 필터링 가능
```

### satisfied_by 전달 방식

```json
numeric_slots 예시 (THRESHOLD:EMPLOYEE_50_PLUS, employee_count=80):
[{
  "binding_field": "employee_count",
  "operator": ">=",
  "value": 50,
  "satisfied_by": { "field": "employee_count", "actual_value": 80 }
}]
```

evaluate_numeric_check()는 기존 로직대로 80 >= 50 = MATCH_CANDIDATE 반환.
MISSING_DATA는 발생하지 않는다.

---

## 7. Check Layer 연결 방식

### semantic_clause_id만으로 6W 생성 가능한가?

```
[6W 항목별 데이터 소스]

누가 (executor):
  semantic_clause.executor_text = '사업주' → 직접 사용 가능 ✅

언제 (when):
  semantic_clause.cycle_text → 있으면 사용
  없으면: extract_six_w(tok_json, action_text)의 when_value
  → semantic_clause_id만으로 가능 ✅

어디서 (where):
  semantic_clause.where_text → 전량 NULL (WO-PROBLEM-001 확인)
  대안: extract_six_w()의 where_value (형태소 분석 필요)
  → semantic_clause.action_text + Kiwi 분석 → 부분 가능 △

무엇을 (what):
  semantic_clause.action_text → 직접 사용 가능 ✅

어떻게 (how):
  extract_six_w()의 how → action_text에서 추출 가능 ✅

왜 (why/legal_basis):
  semantic_clause.source_article_id → law_article.article_no + law_master.law_name
  → semantic_clause_id만으로 가능 ✅
```

### where_text NULL 처리 방안

```
where_text가 NULL인 의무의 "어디서" 처리 전략:

1순위: condition_text에서 장소 키워드 추출
  "밀폐공간에서 작업을 하는 경우" → "밀폐공간"
  "크레인을 사용하는 경우" → 장소 없음 → NULL 허용

2순위: Trigger Code에서 유추
  WORK:CONFINED_SPACE → "밀폐공간"
  WORK:DIVING → "잠수 작업 장소"
  EQUIPMENT:CRANE → NULL (장소 특정 불가)

3순위: NULL 그대로 허용
  runtime_metadata_resolution.when_status = 'UNRESOLVED'로 기록
```

### 6W 연결 키 정합성

```
runtime_metadata_resolution.source_article_no (integer)
  ↕
law_article.article_no (integer) + law_master.law_name

semantic_clause.source_article_id (UUID)
  ↕
law_article.id (UUID)

연결:
  semantic_clause_id → semantic_clause.source_article_id
    → law_article.article_no + law_master.law_name
      → runtime_metadata_resolution 조회 or 신규 생성

키 정합성 문제: source_article_no가 정수, source_article_id가 UUID.
어댑터가 semantic_clause_id → source_article_id → article_no 변환을 담당.
```

---

## 8. 수정 금지 함수 영향 검토

### evaluate_draft_for_facility() — 수정 불필요

```
기존 시그니처로 호출 가능:
  facility = factories row (dict)                    ← 그대로
  draft_id = semantic_clause_id (UUID as string)     ← 의미만 바뀜
  numeric_slots = 어댑터가 생성한 슬롯 목록           ← 어댑터 담당
  scope_slots = 어댑터가 생성한 슬롯 목록             ← 어댑터 담당

반환값 그대로 사용:
  (overall_status, part_id, check_results)
  → facility_applicability에 저장 시 draft_id = semantic_clause_id
```

### evaluate_numeric_check() — 수정 불필요

```
binding_field에 신규 필드(has_confined_space 등)가 오더라도
FIELD_MAP에 없으면 'MISSING_DATA' 반환.
어댑터에서 FIELD_MAP을 확장하여 해결 (기존 파일 수정 없음).
```

### evaluate_scope_check() — 수정 불필요

```
SCOPE_FIELD_EXISTS 로직:
  fac_col이 None이면 MISSING_DATA
  fac_val이 None이면 MISSING_DATA
  존재하면 POSSIBLE_CANDIDATE

has_confined_space=True → POSSIBLE_CANDIDATE 반환.
단, Trigger 기반에서는 이미 true임이 확인된 후보이므로
POSSIBLE_CANDIDATE → 어댑터가 MATCH_CANDIDATE로 승격 처리 가능.
```

### extract_six_w() — 수정 불필요

```
Kiwi 토큰 + action_text를 입력으로 받아 6W 반환.
semantic_clause_id → action_text 조회 후 호출 가능.
where_text NULL 상황에서 where_value를 부분적으로 채워준다.
```

---

## 9. 판정 결과 구조 (최종)

```json
{
  "semantic_clause_id": "uuid",
  "factory_id": "uuid",
  "status": "MATCH_CANDIDATE",
  "trigger_codes": ["WORK:CONFINED_SPACE", "BUSINESS:REGISTERED"],
  "satisfied_by": [
    { "trigger": "WORK:CONFINED_SPACE", "field": "has_confined_space", "value": true },
    { "trigger": "BUSINESS:REGISTERED", "field": null, "value": null }
  ],
  "legal_basis": "산업안전보건기준에 관한 규칙 제618조",
  "confidence": "HIGH",
  "missing_fields": [],
  "check_reason": "condition_text 직접 매칭, has_confined_space=true 확인"
}
```

이 구조가 facility_applicability.match_details에 저장된다.

---

## 10. 다음 구현 단계에서 필요한 최소 작업 목록

### 작업 1: 어댑터 함수 신규 작성 (Cursor 담당)
```
파일: services/trigger_to_applicability_adapter.py (신규)
역할:
  - 의무후보 배치 수신
  - semantic_clause 조회 (source_article_id, executor_text 등)
  - Trigger Code → numeric_slots/scope_slots 변환
  - FIELD_MAP 확장 (TRIGGER_FIELD_MAP_EXTENSION 적용)
  - evaluate_draft_for_facility() 호출
  - facility_applicability INSERT (draft_id = semantic_clause_id)
크기: 150~200줄 예상 (Cursor 적합)
```

### 작업 2: Trigger → 의무후보 생성 함수 신규 작성 (Cursor 담당)
```
파일: services/trigger_obligation_generator.py (신규)
역할:
  - factory_id + 소비자 입력 → Trigger Code Set 생성
  - semantic_clause 키워드 검색 (condition_text OR action_text)
  - Route A/B 분기 처리
  - 의무후보 배치 반환
크기: 200~300줄 예상 (Cursor 적합)
```

### 작업 3: binding_field 매핑 테이블 등록 (DB 작업, Supabase MCP)
```
기존 FIELD_MAP에 없는 신규 binding_field:
  has_confined_space, has_blasting, has_diving, has_asbestos_demo,
  has_high_pressure_gas, has_chemical_substance, has_boiler, has_tower_crane,
  ksic_code, equipment_type_code
→ trigger_binding_field_map 테이블에 등록 (신규 테이블, 소규모)
```

### 작업 4: API 엔드포인트 (Cursor 담당)
```
POST /diagnosis/trigger-evaluate
  입력: factory_id
  처리: Trigger 생성 → 의무후보 → 어댑터 → facility_applicability 저장
  출력: { matched_count, possible_count, task_candidates_created }
크기: 50줄 이하 (router 파일에 추가)
```

### 수정 불필요한 파일 목록
```
services/facility_applicability_eval.py  → 수정 금지
engine/six_w_heuristic.py               → 수정 금지
scripts/run_facility_applicability.py   → 수정 금지 (배치 전용)
facility_applicability 테이블 구조       → 수정 금지
task_candidate 유형 체계                 → 수정 금지
```

---

*WO-CHECK-001 완료 | 코드 수정 없음 | 테이블 생성 없음 | 마이그레이션 없음*
