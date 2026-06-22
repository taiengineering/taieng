# CURSOR-TASK-001
Trigger 기반 의무후보 생성기 구현 작업지시서

작성일: 2026-06-22
작성자: Claude
대상: Cursor (구현 담당)

---

## 배경 및 목적

기존 구조 (이미 동작 중):
```
factories 입력
  ↓
applicability_api.evaluate()       ← 수정 금지
  ↓
obligation_adapter_service.build_obligations_from_v4()  ← 수정 금지
  ↓
factory_diagnosis_results 저장
```

이 구조는 `applicability_conditions` 14건에만 의존한다.
14건으로는 사업주 의무 1,200건의 74.3%를 커버할 수 없다.

**이번 작업의 목적**:
`semantic_clause` 기반으로 Trigger → 의무후보를 생성해서,
기존 `obligation_adapter_service`가 소비할 수 있는 형태로 앞단에 붙인다.

**핵심 원칙**:
```
신규 라우터 생성 금지
applicability_api.evaluate() 수정 금지
evaluate_draft_for_facility() 수정 금지
obligation_adapter_service.py 수정 금지
facility_applicability_eval.py 수정 금지
```

---

## 작성할 파일: 2개

### 파일 1: `services/trigger_generator.py`
### 파일 2: `services/trigger_obligation_generator.py`

---

## TASK-001: `services/trigger_generator.py`

### 역할
factory_id → factories + equipment_assets 조회 → Trigger Code Set 반환

### 함수 시그니처
```python
def generate_trigger_codes(factory_id: str, supabase) -> list[str]:
    """
    factory_id로 factories + equipment_assets 조회 후
    Trigger Code Set을 반환한다.

    Returns:
        ["BUSINESS:REGISTERED", "WORK:CONFINED_SPACE", "EQUIPMENT:CRANE", ...]
    """
```

### 변환 규칙 (정확히 이대로 구현)

```python
# 규칙 A: 직접 변환 (항상 포함)
trigger_codes = ["BUSINESS:REGISTERED"]

# 규칙 A: has_* boolean flags (True인 경우에만)
FLAG_TO_TRIGGER = {
    "has_confined_space":    "WORK:CONFINED_SPACE",
    "has_blasting":          "WORK:BLASTING",
    "has_diving":            "WORK:DIVING",
    "has_asbestos_demo":     "WORK:ASBESTOS",
    "has_tower_crane":       "EQUIPMENT:TOWER_CRANE",
    "has_high_pressure_gas": "WORK:HIGH_PRESSURE",
    "has_chemical_substance":"HAZARD_FACTOR:CHEMICAL",
    "has_boiler":            "EQUIPMENT:BOILER",
}

# 규칙 B: employee_count 임계값 (누적 적용)
EMPLOYEE_THRESHOLDS = [
    (20,  "THRESHOLD:EMPLOYEE_20_PLUS"),
    (50,  "THRESHOLD:EMPLOYEE_50_PLUS"),
    (100, "THRESHOLD:EMPLOYEE_100_PLUS"),
    (300, "THRESHOLD:EMPLOYEE_300_PLUS"),
]

# 규칙 C: equipment_type_code → Trigger
# equipment_assets 테이블에서 factory_id로 조회
EQUIPMENT_CODE_TO_TRIGGER = {
    "CRANE":           ["EQUIPMENT:CRANE", "EQUIPMENT_ACT:CRANE_USE"],
    "PRESS":           ["EQUIPMENT:PRESS"],
    "CONVEYOR":        ["EQUIPMENT:CONVEYOR"],
    "PRESSURE_VESSEL": ["EQUIPMENT:PRESSURE_VESSEL"],
    "008":             ["EQUIPMENT:WELDER", "WORK:WELDING"],     # 용접기
    "011":             ["EQUIPMENT:CHEMICAL_VESSEL"],             # 반응기/혼합기
    "014":             ["EQUIPMENT:BOILER"],                      # 보일러
    "021":             ["EQUIPMENT:MOBILE_CRANE"],                # 이동식크레인
    "024":             ["EQUIPMENT:CONVEYOR"],                    # 컨베이어
    "025":             ["EQUIPMENT:ELEVATOR"],                    # 승강기
    "036":             ["EQUIPMENT:LOCAL_EXHAUST"],               # 집진기
    "040":             ["EQUIPMENT:EXCAVATOR", "WORK:EXCAVATION"],# 굴착기
}
```

### DB 조회
```python
# factories 조회 (필요 컬럼만)
factories 테이블에서:
  has_confined_space, has_blasting, has_diving, has_asbestos_demo,
  has_tower_crane, has_high_pressure_gas, has_chemical_substance,
  has_boiler, employee_count, ksic_code

# equipment_assets 조회
equipment_assets 테이블에서:
  WHERE factory_id = factory_id
  SELECT equipment_type_code
```

### 반환 형식
```python
# 중복 제거 후 정렬된 리스트
["BUSINESS:REGISTERED", "EQUIPMENT:CRANE", "EQUIPMENT_ACT:CRANE_USE", "WORK:CONFINED_SPACE"]
```

---

## TASK-002: `services/trigger_obligation_generator.py`

### 역할
Trigger Code Set → semantic_clause 의무후보 배치 생성

### 함수 시그니처
```python
def generate_obligation_candidates(
    trigger_codes: list[str],
    factory_row: dict,
    supabase,
) -> list[dict]:
    """
    Trigger Code Set → semantic_clause 검색 → 의무후보 배치 반환

    Returns:
        [
            {
                "semantic_clause_id": "uuid",
                "source_article_id": "uuid",
                "trigger_codes": ["WORK:CONFINED_SPACE"],
                "trigger_route": "A",
                "match_source": "condition_text",  # or "action_text" or "condition_text_null"
                "confidence": "HIGH",              # or "MEDIUM"
                "executor_text": "사업주",
                "condition_text": "...",
                "action_text": "...",
                "law_name": "...",
                "article_no": 618,
            },
            ...
        ]
    """
```

### Trigger별 semantic_clause 검색 키워드 (정확히 이대로)

```python
TRIGGER_KEYWORD_MAP = {
    # BUSINESS: condition_text IS NULL 조건
    "BUSINESS:REGISTERED": None,  # None = condition_text IS NULL 특수 처리

    # WORK
    "WORK:CONFINED_SPACE":  r"(밀폐공간|산소결핍|황화수소|밀폐된 공간)",
    "WORK:BLASTING":        r"(발파|화약류|폭발물)",
    "WORK:DIVING":          r"(잠수|잠함|잠수작업자)",
    "WORK:ASBESTOS":        r"(석면|석면해체|석면분진)",
    "WORK:HIGH_PRESSURE":   r"(고압작업|고압가스|기압조절실)",
    "WORK:WELDING":         r"(용접|용단)",
    "WORK:EXCAVATION":      r"(굴착|굴착공사)",

    # EQUIPMENT
    "EQUIPMENT:CRANE":           r"(크레인|양중기)",
    "EQUIPMENT:TOWER_CRANE":     r"(타워크레인)",
    "EQUIPMENT:MOBILE_CRANE":    r"(이동식 크레인|이동식크레인)",
    "EQUIPMENT:PRESS":           r"(프레스)",
    "EQUIPMENT:PRESSURE_VESSEL": r"(압력용기)",
    "EQUIPMENT:CONVEYOR":        r"(컨베이어)",
    "EQUIPMENT:ELEVATOR":        r"(승강기|리프트|엘리베이터)",
    "EQUIPMENT:BOILER":          r"(보일러)",
    "EQUIPMENT:WELDER":          r"(용접기|용접전원|아크용접)",
    "EQUIPMENT:CHEMICAL_VESSEL": r"(화학설비|반응기|혼합기)",
    "EQUIPMENT:LOCAL_EXHAUST":   r"(국소배기|집진기|후드)",
    "EQUIPMENT:EXCAVATOR":       r"(굴착기|차량계 건설기계|건설기계)",

    # EQUIPMENT_ACT
    "EQUIPMENT_ACT:CRANE_USE":   r"(크레인.{0,10}(사용|작업)|크레인을 사용하여)",
    "EQUIPMENT_ACT:WELDING":     r"(용접.{0,10}(작업|하는 경우)|용접작업)",
    "EQUIPMENT_ACT:EXCAVATOR_USE": r"(차량계 건설기계.{0,15}(작업|사용)|굴착기.{0,10}(사용|작업))",

    # HAZARD_FACTOR
    "HAZARD_FACTOR:CHEMICAL":    r"(관리대상 유해물질|허가대상 유해물질|금지유해물질|화학물질)",
}
```

### 검색 방법

```python
# 각 Trigger별로 semantic_clause 검색
# 조건: content_type IN ('OBLIGATION', 'PROHIBITION') AND executor_text = '사업주'

# BUSINESS:REGISTERED 특수 처리
if trigger == "BUSINESS:REGISTERED":
    WHERE condition_text IS NULL

# 나머지 Trigger
else:
    WHERE (COALESCE(condition_text, '') || action_text) ~ keyword_pattern
    → condition_text 매칭 시 confidence = "HIGH"
    → action_text만 매칭 시 confidence = "MEDIUM"

# THRESHOLD Trigger: applicability_conditions 경유 (Route B)
# THRESHOLD:EMPLOYEE_*는 applicability_conditions에서
# metric='METRIC:EMPLOYEE_COUNT', operator='>=', threshold_value <= employee_count
# 충족 시 → appendix_no → law_article 조회 → semantic_clause 연결
# 현재 14건 범위에서만 동작
```

### 중복 제거 및 합집합

```python
# 모든 Trigger 결과를 합산
# source_article_id 기준 중복 제거
# 동일 source_article_id에 여러 Trigger가 매칭 시 → trigger_codes 배열에 모두 포함

# 결과 예시
{
    "semantic_clause_id": "uuid",
    "trigger_codes": ["EQUIPMENT:CRANE", "EQUIPMENT_ACT:CRANE_USE"],  # 두 Trigger가 같은 조문 매칭
    ...
}
```

### DB 조회 필요 정보

semantic_clause 테이블에서:
- id, source_article_id, source_part_id
- content_type, executor_text
- condition_text, action_text

law_article 테이블 JOIN:
- article_no

law_master 테이블 JOIN:
- law_name

---

## 연결 확인 (TASK-003: 구현 아님, 확인만)

위 두 파일 작성 후, 아래 흐름이 동작하는지 확인한다.

```python
# 기존 obligation_adapter 라우터에서 호출 테스트
from services.trigger_generator import generate_trigger_codes
from services.trigger_obligation_generator import generate_obligation_candidates

# 1. Trigger 생성
triggers = generate_trigger_codes(factory_id, supabase)

# 2. 의무후보 생성
candidates = generate_obligation_candidates(triggers, factory_row, supabase)

# 3. 후보 건수 확인
# has_confined_space=True 사업장 → WORK:CONFINED_SPACE 후보 22건 이상 존재해야 함
# BUSINESS:REGISTERED → 491건 내외 존재해야 함
```

기존 `obligation_adapter_service.build_obligations_from_v4()`와의 연결은
**이번 작업 범위에 포함되지 않는다.**
후보 생성이 정상 동작함을 확인한 후 다음 작업에서 연결한다.

---

## 완료 조건

### TASK-001 완료 조건
다음 입력에 대해 정확한 Trigger Code Set 반환:
```python
# 입력
factory_id = "[테스트 factory_id]"
# factories.has_confined_space = True
# factories.employee_count = 80
# equipment_assets: CRANE 보유

# 기대 출력 (최소 포함)
[
    "BUSINESS:REGISTERED",
    "THRESHOLD:EMPLOYEE_50_PLUS",
    "WORK:CONFINED_SPACE",
    "EQUIPMENT:CRANE",
    "EQUIPMENT_ACT:CRANE_USE"
]
```

### TASK-002 완료 조건
다음 Trigger Set에 대해 의무후보 반환:
```python
trigger_codes = ["BUSINESS:REGISTERED", "WORK:CONFINED_SPACE", "EQUIPMENT:CRANE"]

# 기대 결과
# - 총 후보 30건 이상
# - WORK:CONFINED_SPACE 후보 중 confidence="HIGH" 존재
# - source_article_id 기준 중복 제거 완료
# - 각 후보에 law_name, article_no 포함
```

---

## 금지사항

```
applicability_api.py 수정 금지
obligation_adapter.py 수정 금지
obligation_adapter_service.py 수정 금지
facility_applicability_eval.py 수정 금지
six_w_heuristic.py 수정 금지
신규 라우터 생성 금지 (이번 작업에서)
router_registry 수정 금지 (이번 작업에서)
테이블 생성 금지
마이그레이션 금지
```

---

## 참고: 주요 기존 파일 경로

```
services/facility_applicability_eval.py   ← 체크엔진 (수정 금지)
services/obligation_adapter_service.py    ← 기존 어댑터 (수정 금지)
routers/obligation_adapter.py             ← 기존 라우터 (수정 금지)
routers/applicability_api.py              ← V4 평가 (수정 금지)
engine/six_w_heuristic.py                 ← 6W 추출 (수정 금지)
```

---

## 작업 순서

1. `services/trigger_generator.py` 작성 및 단위 테스트
2. `services/trigger_obligation_generator.py` 작성 및 단위 테스트
3. 두 파일 연동 확인 (factory_id 입력 → 후보 배치 출력)
4. 결과 Claude에게 보고
