# WO-PLAN-001
Trigger 기반 법령의무도출 시스템 구현계획서

작성일: 2026-06-22
작성자: Claude (계획 전담)
단계: 실행계획 (구현 없음)

---

## 0. 핵심 원칙

**"새 엔진을 만들지 말고, Trigger → 의무후보 구간만 채워서 기존 자산을 살린다."**

신규 개발 영역: 전체의 10~20%
기존 자산 재활용: 80~90%

---

## 1. 재활용 자산 목록 (코드 레벨 확인 완료)

| 파일 | 역할 | 재사용 방식 |
|---|---|---|
| `services/facility_applicability_eval.py` | Check Engine (평가 로직) | 함수 호출, 수정 없음 |
| `engine/six_w_heuristic.py` | 6W 추출 | 함수 호출, 수정 없음 |
| `routers/obligation_adapter.py` | 기존 어댑터 라우터 | 참조, Trigger 버전 별도 작성 |
| `services/obligation_adapter_service.py` | obligations → result_data 변환 | 구조 참조 |
| `facility_applicability` 테이블 | 판정 결과 저장 | 구조 그대로 |
| `task_candidate` 체계 | 의무 유형 | 구조 그대로 |
| `factories` has_* 컬럼 | 소비자 입력 | 그대로 조회 |
| `equipment_assets` 테이블 | 설비 데이터 | factory_id JOIN |
| `semantic_clause` 테이블 | 법령 조문 | 키워드 검색 |
| `applicability_conditions` 14건 | Route B 데이터 | 그대로 사용 |

---

## 2. 신규 작성 목록

| 파일 | 역할 | 크기 | 담당 |
|---|---|---|---|
| `services/trigger_generator.py` | 입력값 → Trigger Code Set | ~100줄 | Cursor |
| `services/trigger_obligation_generator.py` | Trigger → 의무후보 (Route A) | ~200줄 | Cursor |
| `services/trigger_applicability_adapter.py` | 의무후보 → facility_applicability | ~150줄 | Cursor |
| `routers/trigger_diagnosis.py` | API 엔드포인트 | ~80줄 | Cursor |
| `router_registry/diagnosis.py` | 라우터 등록 1줄 추가 | +1줄 | GitHub MCP |

**총 신규 코드: 약 530줄**

---

## 3. 절대 수정 금지 파일

```
services/facility_applicability_eval.py    (evaluate_draft_for_facility 등)
engine/six_w_heuristic.py                  (extract_six_w)
services/obligation_adapter_service.py     (기존 V4 어댑터)
routers/obligation_adapter.py              (기존 V4 어댑터 라우터)
routers/applicability_api.py              (V4 evaluate)
```

---

## 4. 구현 단계

---

### Phase 1: Trigger Generator (TASK-001)

**목적**: 소비자 입력값 → Trigger Code Set 변환

**파일**: `services/trigger_generator.py`

**입력**:
```python
{
    "employee_count": 80,
    "has_confined_space": True,
    "has_blasting": False,
    "has_diving": False,
    "has_asbestos_demo": False,
    "has_tower_crane": False,
    "has_high_pressure_gas": False,
    "has_chemical_substance": False,
    "has_boiler": False,
    "equipment_type_codes": ["CRANE"],  # equipment_assets에서 조회
    "ksic_code": "C2511"
}
```

**출력**:
```python
{
    "trigger_codes": [
        "BUSINESS:REGISTERED",
        "THRESHOLD:EMPLOYEE_50_PLUS",
        "WORK:CONFINED_SPACE",
        "EQUIPMENT:CRANE"
    ]
}
```

**변환 규칙 (코드화)**:
```
규칙 A (직접 변환):
  항상 → BUSINESS:REGISTERED
  has_confined_space=True → WORK:CONFINED_SPACE
  has_blasting=True       → WORK:BLASTING
  has_diving=True         → WORK:DIVING
  has_asbestos_demo=True  → WORK:ASBESTOS
  has_tower_crane=True    → EQUIPMENT:TOWER_CRANE
  has_high_pressure_gas=True → WORK:HIGH_PRESSURE + EQUIPMENT:HIGH_PRESSURE_VESSEL
  has_chemical_substance=True → HAZARD_FACTOR:CHEMICAL
  has_boiler=True         → EQUIPMENT:BOILER

규칙 B (임계값):
  employee_count >= 20  → THRESHOLD:EMPLOYEE_20_PLUS
  employee_count >= 50  → THRESHOLD:EMPLOYEE_50_PLUS
  employee_count >= 100 → THRESHOLD:EMPLOYEE_100_PLUS

규칙 C (설비 코드):
  equipment_type_code = CRANE         → EQUIPMENT:CRANE + EQUIPMENT_ACT:CRANE_USE
  equipment_type_code = PRESS         → EQUIPMENT:PRESS
  equipment_type_code = CONVEYOR      → EQUIPMENT:CONVEYOR
  equipment_type_code = PRESSURE_VESSEL → EQUIPMENT:PRESSURE_VESSEL
  코드 008 (용접기)                    → EQUIPMENT:WELDER + WORK:WELDING
  코드 011 (반응기/혼합기)             → EQUIPMENT:CHEMICAL_VESSEL
  코드 014 (보일러)                   → EQUIPMENT:BOILER
  코드 021 (이동식크레인)             → EQUIPMENT:MOBILE_CRANE
  코드 024 (컨베이어)                 → EQUIPMENT:CONVEYOR
  코드 025 (승강기)                   → EQUIPMENT:ELEVATOR
  코드 036 (집진기)                   → EQUIPMENT:LOCAL_EXHAUST
  코드 040 (굴착기/차량계건설기계)     → EQUIPMENT:EXCAVATOR + WORK:EXCAVATION
```

**완료 조건**: 위 입력값으로 위 출력 생성 가능

---

### Phase 2: Obligation Generator (TASK-002)

**목적**: Trigger Code Set → semantic_clause 의무후보 생성

**파일**: `services/trigger_obligation_generator.py`

**Route A 처리 방식**:
```
각 Trigger Code에 대해:
  1. 키워드 패턴 매핑 테이블 조회 (하드코딩 dict, DB 조회 아님)
  2. semantic_clause 검색:
       WHERE content_type IN ('OBLIGATION', 'PROHIBITION')
         AND executor_text = '사업주'
         AND (COALESCE(condition_text, '') || action_text) ~ keyword_pattern
  3. 결과 합집합
  4. source_article_id 기준 중복 제거
```

**특수 처리**:
```
BUSINESS:REGISTERED:
  WHERE content_type IN ('OBLIGATION', 'PROHIBITION')
    AND executor_text = '사업주'
    AND (condition_text IS NULL OR condition_text = '')

THRESHOLD:*:
  applicability_conditions 테이블 조회 (Route B)
  → 현재 14건 범위에서만 동작
  → appendix_no → law_article.article_no → semantic_clause 연결
```

**출력** (의무후보 배치):
```python
[
    {
        "candidate_id": "uuid",
        "semantic_clause_id": "uuid",
        "source_article_id": "uuid",
        "trigger_codes": ["WORK:CONFINED_SPACE"],
        "trigger_route": "A",
        "match_source": "condition_text",
        "confidence": "HIGH",
        "executor_text": "사업주",
        "condition_text": "...",
        "action_text": "..."
    },
    ...
]
```

**완료 조건**: WORK:CONFINED_SPACE → 밀폐공간 관련 의무 22건 이상 반환

---

### Phase 3: Applicability Adapter (TASK-003)

**목적**: 의무후보 → evaluate_draft_for_facility() 호출 → facility_applicability 저장

**파일**: `services/trigger_applicability_adapter.py`

**핵심 로직**:
```
1. 의무후보 배치 수신
2. Trigger Code → numeric_slots / scope_slots 변환:
     BUSINESS:REGISTERED     → slots 없음, 직접 MATCH_CANDIDATE
     THRESHOLD:EMPLOYEE_50_PLUS → numeric_slots: [{binding_field:'employee_count', op:'>=', val:50}]
     WORK:CONFINED_SPACE     → scope_slots: [{binding_field:'has_confined_space'}]
     EQUIPMENT:CRANE         → scope_slots: [{binding_field:'equipment_type_code'}]

3. FIELD_MAP 확장 적용 (TRIGGER_FIELD_MAP_EXTENSION):
     has_confined_space → ('has_confined_space', 'DIRECT')
     has_blasting       → ('has_blasting', 'DIRECT')
     ... (WO-CHECK-001 §5 전체 목록)

4. facility_applicability_eval.evaluate_draft_for_facility() 호출
   (draft_id = semantic_clause_id로 사용)

5. 결과를 facility_applicability에 INSERT:
   {
     factory_id: factory_id,
     draft_id: semantic_clause_id,  ← 의미 재사용
     part_id: source_part_id,
     applicability_status: overall_status,
     match_details: {
       trigger_codes: [...],
       satisfied_by: {...},
       confidence: "HIGH",
       source: "trigger_based"
     }
   }
```

**완료 조건**: facility_applicability에 MATCH_CANDIDATE 레코드 생성

---

### Phase 4: Check Engine 연결 (TASK-004)

**목적**: evaluate_draft_for_facility() 재사용 확인 + 판정 결과 검증

**추가 작업**:
```
FIELD_MAP 확장이 평가 함수에 적용되는지 검증:
  → evaluate_numeric_check() 호출 시 has_confined_space → DIRECT 처리 확인
  → evaluate_scope_check() 호출 시 POSSIBLE_CANDIDATE 반환 확인

BUSINESS:REGISTERED 특수 처리:
  → slots 없음 → evaluate_draft_for_facility() 반환 None
  → 어댑터가 직접 MATCH_CANDIDATE 로 facility_applicability 저장

판정 결과:
  MATCH_CANDIDATE    → 의무 확정 (task_candidate 생성)
  POSSIBLE_CANDIDATE → 조건 충족 가능 (추가 확인)
  NOT_MATCHED        → 의무 미발생
  AMBIGUOUS          → 판단 보류
```

**수정 금지**: evaluate_draft_for_facility, evaluate_scope_check, evaluate_numeric_check

**완료 조건**: MATCH / POSSIBLE / NOT_MATCHED 판정 정상 동작

---

### Phase 5: 6W 연결 (TASK-005)

**목적**: Check 결과 → 6W 생성 → runtime_metadata_resolution 저장

**처리 흐름**:
```
1. MATCH_CANDIDATE 의무후보에 대해:
   semantic_clause.action_text 조회

2. Kiwi 형태소 분석 (engine.morpheme 기존 활용)

3. extract_six_w(tok_json, action_text) 호출 (수정 없음)

4. where_text NULL 보완:
   condition_text에서 장소 키워드 추출
   또는 Trigger Code에서 유추
   (WORK:CONFINED_SPACE → '밀폐공간')

5. runtime_metadata_resolution 저장:
   {
     runtime_name: action_text[:50],
     source_law_name: law_master.law_name,
     source_article_no: law_article.article_no,
     who_status: 'RESOLVED', who_value: '사업주',
     when_status: ..., when_value: ...,
     where_status: ..., where_value: ...,
     what_status: 'RESOLVED', what_value: action_text,
     how_status: ..., how_value: ...,
     condition_status: ..., condition_value: condition_text,
     overall_completeness: 계산값
   }
```

**수정 금지**: extract_six_w

**완료 조건**: 6W 중 최소 4개 항목 RESOLVED

---

### Phase 6: 결과 출력 (TASK-006)

**목적**: 최종 의무 목록 반환

**파일**: `routers/trigger_diagnosis.py`

**API 엔드포인트**:
```
POST /trigger-diagnosis/{factory_id}/evaluate

처리 흐름:
  1. factories + equipment_assets 조회
  2. trigger_generator.generate() 호출
  3. trigger_obligation_generator.generate() 호출
  4. trigger_applicability_adapter.evaluate() 호출
  5. MATCH_CANDIDATE 필터
  6. 6W 보강
  7. 결과 반환
```

**출력 포맷**:
```json
{
  "factory_id": "uuid",
  "trigger_codes": ["BUSINESS:REGISTERED", "WORK:CONFINED_SPACE", "EQUIPMENT:CRANE"],
  "obligations": [
    {
      "obligation_id": "uuid",
      "semantic_clause_id": "uuid",
      "obligation": "사업주는 밀폐공간에서 작업 시 산소 농도를 측정하여야 한다",
      "law_basis": "산업안전보건기준에 관한 규칙 제618조",
      "trigger_codes": ["WORK:CONFINED_SPACE"],
      "status": "MATCH_CANDIDATE",
      "confidence": "HIGH",
      "six_w": {
        "who": "사업주",
        "when": null,
        "where": "밀폐공간",
        "what": "산소 농도 측정",
        "how": null,
        "why": "산업안전보건기준에 관한 규칙 제618조"
      }
    }
  ],
  "obligation_count": 35,
  "source": "trigger_based_v1"
}
```

**router_registry 등록** (GitHub MCP, +1줄):
```python
# router_registry/diagnosis.py에 추가
{"module": "routers.trigger_diagnosis"},
```

**완료 조건**: POST 요청 → 의무 목록 JSON 반환

---

## 5. 검증 단계 (VERIFY-001)

### 검증 대상: 샘플 사업장 10개

**검증 입력 예시 (성공 기준 케이스)**:
```json
{
  "factory_id": "[실제 테스트 factory_id]",
  "override_input": {
    "employee_count": 80,
    "has_confined_space": true,
    "has_blasting": false,
    "equipment_assets": ["CRANE"]
  }
}
```

**기대 출력**:
```
- BUSINESS:REGISTERED → 사업장 기본 의무 (40건 내외)
- WORK:CONFINED_SPACE → 밀폐공간 관련 의무 (22건)
- THRESHOLD:EMPLOYEE_50_PLUS → (applicability_conditions 연결 시)
- EQUIPMENT:CRANE → 크레인 관련 의무 (29건)
중복 제거 후 총 50~80건 예상
```

### 검증 항목 5개

| 항목 | 확인 방법 | 성공 기준 |
|---|---|---|
| Trigger 생성 | trigger_codes 목록 확인 | BUSINESS + WORK + EQUIPMENT 포함 |
| 의무후보 생성 | semantic_clause_id 목록 수 | 20건 이상 |
| Check Engine 판정 | facility_applicability.applicability_status | MATCH_CANDIDATE 존재 |
| 6W 생성 | runtime_metadata_resolution.overall_completeness | 60% 이상 |
| 최종 출력 | API 응답 obligations 배열 | 비어 있지 않음 |

---

## 6. 구현 금지 범위

```
Semantic Engine 재설계 금지
Check Engine (facility_applicability_eval.py) 재설계 금지
Check Layer (six_w_heuristic.py) 재설계 금지
기존 V4 obligation_adapter 수정 금지
facility_applicability 테이블 구조 변경 금지
task_candidate 구조 변경 금지
router_registry 내 기존 항목 삭제 금지
```

---

## 7. 구현 우선순위 및 담당

| 순서 | 작업 | 파일 | 담당 | 예상 크기 |
|---|---|---|---|---|
| 1 | Trigger Generator | `services/trigger_generator.py` | Cursor | ~100줄 |
| 2 | Obligation Generator | `services/trigger_obligation_generator.py` | Cursor | ~200줄 |
| 3 | Applicability Adapter | `services/trigger_applicability_adapter.py` | Cursor | ~150줄 |
| 4 | API 엔드포인트 | `routers/trigger_diagnosis.py` | Cursor | ~80줄 |
| 5 | 라우터 등록 | `router_registry/diagnosis.py` +1줄 | GitHub MCP | 1줄 |
| 6 | 검증 | API 호출 10회 | Claude | - |

**총 신규 코드: 약 530줄 (전부 Cursor 담당)**

---

## 8. Phase별 의존관계

```
TASK-001 (Trigger Generator)
  ↓
TASK-002 (Obligation Generator)
  ↓
TASK-003 (Applicability Adapter) ← evaluate_draft_for_facility() 재사용
  ↓
TASK-004 (Check Engine 연결 검증)
  ↓
TASK-005 (6W 연결) ← extract_six_w() 재사용
  ↓
TASK-006 (출력 API)
  ↓
VERIFY-001 (샘플 10개 검증)
```

순차 의존. 각 Task 완료 후 다음 Task 시작.

---

## 9. Post-MVP 범위 (이번 구현 제외)

```
THRESHOLD:EMPLOYEE_* 전체 범위
  → WO-APPENDIX-COLLECT-001 완료 후 applicability_conditions 확장 시

INDUSTRY:* Trigger
  → 별표 데이터 구축 후

HAZARD_FACTOR 세분화
  → 유해인자 입력 UI 구축 후

EVENT Trigger
  → SaaS 런타임 레이어 (기존 runtime_event_log 활용)

REFERENCE 처리
  → WO-APPENDIX-COLLECT-001 + 수작업 화이트리스트
```

---

*WO-PLAN-001 완료 | 구현 없음 | 다음: Cursor에서 TASK-001부터 순차 구현*
