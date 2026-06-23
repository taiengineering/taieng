# WO-CONDITION-001 법령 의무발생조건 표준화 조사보고서

**작성일:** 2026-06-23  
**상태:** 조사 완료 / 구현 금지  
**대상:** semantic_clause 사업주 의무 100건 샘플  

---

## 핵심 결론 (먼저)

**입력값 → 조건코드 → 의무 원인추적이 가능한가?**

→ **가능하다. 단, condition_text가 있는 의무에 한해서만.**  
→ **condition_text가 NULL인 의무는 반드시 3분류 재처리가 필요하다.**

---

## 1. 샘플 100건 구성

| 그룹 | 조회 조건 | 확보 건수 |
|------|-----------|----------|
| A. CONFINED_SPACE | condition/action에 '밀폐' 포함 | 20건 |
| B. CRANE | condition/action에 '크레인' 포함 | 20건 |
| C. BLASTING | condition/action에 '발파' 포함 | 4건 (DB에 4건만 존재) |
| D. CHEMICAL | condition에 '화학물질/유해물질/관리대상' 포함 | 20건 |
| E. BUSINESS NULL | condition_text IS NULL / 산안법계열 | 30건 |
| **합계** | | **94건** |

> BLASTING은 DB에 4건만 존재. 총 94건으로 분석.

---

## 2. condition_text 유무 분류

### condition_text 있는 의무 (64건 추정)

구조화 가능. 아래 condition_code 체계로 분해 가능.

### condition_text 없는 의무 (30건 + 일부 그룹 내 NULL 포함)

반드시 3분류 재처리 필요.

---

## 3. Deliverable A: condition_text → condition_code 구조화 (샘플)

### 3-1. CONFINED_SPACE 그룹

| semantic_clause_id (앞6) | condition_text | condition_code | condition_type | input_field | input_value | action_type |
|---|---|---|---|---|---|---|
| 60f27a | 사업주는 밀폐공간에서 근로자에게 작업을 하도록 하는 경우 | WORK_ACT:CONFINED_SPACE | WORK_ACT | has_confined_space | true | WORK |
| 1567425d | 사업주는 근로자가 밀폐공간에서 작업을 하는 경우 | WORK_ACT:CONFINED_SPACE | WORK_ACT | has_confined_space | true | WORK |
| 4e59b845 | 사업주는 근로자가 밀폐공간에서 작업을 하는 경우 | WORK_ACT:CONFINED_SPACE | WORK_ACT | has_confined_space | true | WORK |
| 4684e1b7 | 사업주는 밀폐공간에서 위급한 근로자를 구출하는 작업을 하는 경우 | WORK_ACT:CONFINED_SPACE_RESCUE | WORK_ACT | has_confined_space | true | RESCUE |
| 570a62ad | 사업주는 밀폐공간에서 작업하는 근로자가 산소결핍이나 유해가스로 인하여 추락할 우려가 있는 경우 | WORK_ACT:CONFINED_SPACE_FALL_RISK | WORK_ACT | has_confined_space | true | FALL_PREVENTION |
| 2b88b62c | 사업주는 사업장 내 밀폐공간을 사전에 파악하여 밀폐공간... | WORK_ACT:CONFINED_SPACE | WORK_ACT | has_confined_space | true | ACCESS_CONTROL |
| 238f8884 | 사업주는 냉장실·냉동실 등 밀폐하여 사용하는 시설이나 설비의 출입문을 잠그는 경우 | FACILITY_ACT:COLD_STORAGE_LOCK | FACILITY_ACT | facility_type=COLD_STORAGE | true | LOCK_CHECK |
| 4733c5ed | 사업주는 근로자가 탱크·반응탑 또는 그 밖의 밀폐시설에서 작업을 하는 경우 | FACILITY_ACT:ENCLOSED_FACILITY | FACILITY_ACT | has_confined_space | true | WORK |
| 6087c90c | 사업주는 근로자가 밀폐공간의 내부를 통하는 배관이 설치되어 있는 지하실이나 피트 등의 내부에서 작업을 하는 경우 | WORK_ACT:CONFINED_SPACE_PIPE | WORK_ACT | has_confined_space | true | PIPE_WORK |
| 5f760824 | 사업주는 근로자가 노출 충전부가 있는 맨홀 또는 지하실 등의 밀폐공간에서 작업하는 경우 | WORK_ACT:CONFINED_SPACE_ELECTRIC | WORK_ACT | has_confined_space | true | ELECTRICAL_WORK |

**condition_text NULL (밀폐 관련):**
- `4153a688` "밀폐공간에서 작업을 시작하기 전에" → action_text에 조건 내포 → **B유형: action_text에 조건 있음**
- `4542164f` "밀폐공간의 산소 및 유해가스 농도를 측정" → B유형
- `5cc272ac` "긴급상황 발생 시 대응" → B유형 (밀폐공간 전제)
- `02d6287a` "관리대상 유해물질의 운반·저장 등을 위하여 사용한 용기를 밀폐하거나" → condition_text에 '밀폐'가 action에만 등장, 조건 없음 → **A유형: 모든 사업장** (관리대상 유해물질 보유 전제)
- `2e12a94b` "석면해체 작업에 종사한 근로자에게 개인보호구를 밀폐용기에 보관" → 석면 조건 → **B유형**

---

### 3-2. CRANE 그룹

| semantic_clause_id (앞6) | condition_text | condition_code | condition_type | input_field | input_value |
|---|---|---|---|---|---|
| 33d69d53 | 사업주는 **타워크레인**을 자립고 이상의 높이로 설치하는 경우 | EQUIPMENT_ACT:TOWER_CRANE_INSTALL | EQUIPMENT_ACT | has_tower_crane | true |
| a9f6fa5d | 사업주는 **타워크레인**을 벽체에 지지하는 경우 | EQUIPMENT_ACT:TOWER_CRANE_WALL_SUPPORT | EQUIPMENT_ACT | has_tower_crane | true |
| c408f352 | 사업주는 **타워크레인**을 와이어로프로 지지하는 경우 | EQUIPMENT_ACT:TOWER_CRANE_WIRE_SUPPORT | EQUIPMENT_ACT | has_tower_crane | true |
| c52ff010 | 사업주는 순간풍속이 초당 10미터를 초과하는 경우 (타워크레인) | EQUIPMENT_ACT:TOWER_CRANE_WIND | EQUIPMENT_ACT | has_tower_crane | true |
| 271d9cfa | 사업주는 **이동식 크레인**을 사용하여 작업을 하는 경우 | EQUIPMENT_ACT:MOBILE_CRANE_USE | EQUIPMENT_ACT | equipment_type_code | MOBILE_CRANE |
| 5add0e82 | 사업주는 **이동식 크레인**을 사용하는 경우 | EQUIPMENT_ACT:MOBILE_CRANE_USE | EQUIPMENT_ACT | equipment_type_code | MOBILE_CRANE |
| 23f3066b | 사업주는 **지브 크레인**을 사용하여 작업을 하는 경우 | EQUIPMENT_ACT:JIB_CRANE_USE | EQUIPMENT_ACT | equipment_type_code | JIB_CRANE |
| 4187c35e | 사업주는 **크레인**을 사용하여 작업을 하는 경우 | EQUIPMENT_ACT:CRANE_USE | EQUIPMENT_ACT | has_crane OR equipment_type_code | ANY_CRANE |
| 43cd1f5b | 사업주는 **주행 크레인** 또는 **선회 크레인**과 건설물 사이에 통로를 설치하는 경우 | EQUIPMENT_ACT:TRAVELING_CRANE_AISLE | EQUIPMENT_ACT | equipment_type_code | TRAVELING_CRANE |
| 13175a52 | 사업주는 같은 주행로에 병렬로 설치되어 있는 **주행 크레인**의 수리 작업을 하는 경우 | EQUIPMENT_ACT:TRAVELING_CRANE_REPAIR | EQUIPMENT_ACT | equipment_type_code | TRAVELING_CRANE |
| 5d69a640 | 그 크레인을 사용하여 짐을 운반하는 경우 (해지장치) | EQUIPMENT_ACT:CRANE_CARGO | EQUIPMENT_ACT | has_crane | true |
| 8cf2ab10 | 사업주는 제1항에 따른 통로 또는 주행궤도 상에서 정비·보수·점검 작업을 하는 경우 | EQUIPMENT_ACT:CRANE_TRACK_MAINTENANCE | EQUIPMENT_ACT | has_crane | true |

**condition_text NULL (크레인 관련):**
- `1c26a66d` "변형된 훅·샤클을 크레인 고리걸이용구로 사용 금지" → **B유형**
- `41ae7718` "크레인을 사용하여 근로자를 운반" → B유형
- `4aee8c6d` "갠트리 크레인 새들 돌출부 안전공간" → B유형
- `4b9abc6e` "유압을 동력으로 사용하는 크레인 안전밸브 조정" → B유형
- `987ca9c2` "조종석이 설치되지 아니한 크레인" → B유형
- `8752a3b2` "와이어로프 양단에 훅·샤클 구비" → B유형
- `ac1e9bab` "유압 이동식 크레인 안전밸브 조정" → B유형
- `6231c5f5` "타워크레인 설치·해체업 등록자로 하여금" → B유형

**핵심 발견:**  
크레인 그룹 오분류 원인 확정.
- 타워크레인 조문 4건: `condition_code = EQUIPMENT_ACT:TOWER_CRANE_*` → `input_field = has_tower_crane`
- 이동식크레인 조문: `condition_code = EQUIPMENT_ACT:MOBILE_CRANE_USE` → `input_field = equipment_type_code = MOBILE_CRANE`
- **이 둘은 완전히 다른 input_field에 연결된다.**
- 기존 Trigger `EQUIPMENT:CRANE` 하나로 묶었기 때문에 오분류 발생.

---

### 3-3. BLASTING 그룹

| semantic_clause_id (앞6) | condition_text | condition_code | condition_type | input_field | input_value |
|---|---|---|---|---|---|
| 6c64375e | 사업주는 발파작업 시 근로자가 안전한 거리로 피난할 수 없는 경우 | WORK_ACT:BLASTING_NO_ESCAPE | WORK_ACT | has_blasting | true |
| ac28a13d | 사업주는 **작업실 내에서** 발파를 하는 경우 | WORK_ACT:HIGH_PRESSURE_BLASTING | COMPOUND | has_blasting AND has_high_pressure | true |

**주목:** `ac28a13d`는 발파 + 고압작업실 **복합 조건**.  
has_blasting=true AND facility_type=HIGH_PRESSURE_CHAMBER.  
이것이 이전 세션 WORK:BLASTING 오류의 실체.

---

### 3-4. CHEMICAL 그룹

| semantic_clause_id (앞6) | condition_text | condition_code | condition_type | input_field | input_value |
|---|---|---|---|---|---|
| 0c7463b5 | 관리대상 유해물질을 취급하는 작업에 근로자를 종사 | WORK_ACT:HAZMAT_HANDLE | WORK_ACT | has_chemical_substance | true |
| 3b470472 | 관리대상 유해물질 취급설비나 그 부속설비를 사용하는 작업 | EQUIPMENT_ACT:HAZMAT_EQUIPMENT_USE | EQUIPMENT_ACT | has_chemical_substance | true |
| 418513b4 | 허가대상 유해물질을 제조·사용하는 경우 | WORK_ACT:PERMITTED_HAZMAT | WORK_ACT | has_permitted_hazmat | true |
| 426dc9b9 | 허가대상 유해물질(베릴륨·석면 제외)을 제조·사용 | WORK_ACT:PERMITTED_HAZMAT_NON_ASBESTOS | WORK_ACT | has_permitted_hazmat | true |
| 17ab738b | 금지유해물질을 제조·사용하는 경우 | WORK_ACT:PROHIBITED_HAZMAT | WORK_ACT | has_prohibited_hazmat | true |
| 68008c61 | 금지유해물질이 실험실 등에서 새는 경우 | SITUATION:PROHIBITED_HAZMAT_LEAK | SITUATION | has_prohibited_hazmat | true |
| 69dbb384 | 피부 자극성 또는 부식성 관리대상 유해물질을 취급 | WORK_ACT:HAZMAT_SKIN_IRRITANT | WORK_ACT | has_chemical_substance | true |
| 75c666c5 | 허가대상 유해물질을 운반하거나 저장하는 경우 | WORK_ACT:PERMITTED_HAZMAT_TRANSPORT | WORK_ACT | has_permitted_hazmat | true |
| 09c5e55c | 전체환기장치 설치된 실내작업장에서 단시간 관리대상 유해물질 취급 | WORK_ACT:HAZMAT_SHORT_VENTILATED | COMPOUND | has_chemical_substance AND has_ventilation | true |

**제외 대상:**
- `739cc8a7` 공동주택관리법 담보책임 종료 통보 → **C유형: TAI Safe 범위 밖**

---

### 3-5. BUSINESS NULL 그룹 3분류

**A유형: 진짜 모든 사업장 의무**
| semantic_clause_id (앞6) | action_text 요약 |
|---|---|
| 033a2152 | 휴게시설 갖추어야 |
| 0c6af11b | 안전보건관리책임자 등 직무교육 이수 |
| 014a3f8f | 안전보건관리책임자 지원 의무 |

**B유형: action_text 안에 조건이 숨어 있음**
| semantic_clause_id (앞6) | 숨은 조건 |
|---|---|
| 000c3991 | 하적단 존재 (화물 적재 작업) |
| 007926d4 | 압력용기/안전밸브 설치 전제 |
| 0a835c78 | 항타기/항발기 보유 |
| 0a383db8 | 자동차정비용 리프트 보유 |
| 06adaaf3 | 양중기 보유 |
| 0b19025e 목재가공용 둥근톱 보유 |
| 0bcac742 | 지게차 보유 |
| 0cf72208 | 직기 보유 (특정 제조업) |
| 027868c7 | 급성 독성물질 사용 전제 |
| 13ad2c34 | 소음작업 존재 |
| 14447dcc | 굴착기 보유 |
| 0be56d40 | 리프트 보유 |
| 135794dd | 위험물 건조설비 보유 |
| 010c84b2 | 고압작업 (has_high_pressure) |
| 03494616 | has_asbestos_demo |
| 12b0c775 | has_chemical_substance |
| 084e7068 | has_confined_space |

**C유형: TAI Safe 범위 밖**
- 현재 샘플에서 없음 (산안법 계열만 조회)
- 이전 세션 BUSINESS:REGISTERED 328건 중 고용보험법/장애인고용법 31건이 C유형

---

## 4. condition_mapping_candidate 테이블 설계안

```sql
-- DDL 금지 - 설계안만

CREATE TABLE condition_mapping_candidate (
  mapping_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  semantic_clause_id  UUID NOT NULL REFERENCES semantic_clause(id),
  source_article_id   UUID NOT NULL,

  condition_source    TEXT NOT NULL,
  -- 'CONDITION_TEXT' / 'ACTION_TEXT' / 'MANUAL_REVIEW'

  condition_text_raw  TEXT,
  condition_code      TEXT,
  condition_type      TEXT,
  -- WORK_ACT / EQUIPMENT_ACT / FACILITY_ACT / SITUATION / THRESHOLD / COMPOUND / NONE / OUT_OF_SCOPE

  input_field         TEXT,
  input_value         TEXT,
  input_operator      TEXT DEFAULT '=',
  input_field_2       TEXT,
  input_value_2       TEXT,
  input_operator_2    TEXT,

  action_type         TEXT,
  confidence          NUMERIC(3,2),
  review_status       TEXT DEFAULT 'PENDING',
  -- 'CONFIRMED' / 'PENDING' / 'REJECTED'

  null_condition_class TEXT,
  -- 'A_UNIVERSAL' / 'B_HIDDEN_COND' / 'C_OUT_OF_SCOPE'

  exclude_reason      TEXT,
  created_at          TIMESTAMPTZ DEFAULT now(),
  updated_at          TIMESTAMPTZ DEFAULT now()
);
```

---

## 5. Trigger vs condition_code 분리 원칙 (확정)

```
[입력 쪽]                       [법령 쪽]
소비자 입력값
  has_tower_crane = true
  equipment_type_code = 021
        ↓
  input_field + input_value  ←→  condition_code
        ↓                             ↓
  EQUIPMENT_ACT:TOWER_CRANE_INSTALL ← "타워크레인을 자립고 이상으로 설치하는 경우"
  EQUIPMENT_ACT:MOBILE_CRANE_USE   ← "이동식 크레인을 사용하여 작업을 하는 경우"
```

- Trigger = 입력 측 라벨
- condition_code = 법령 측 라벨
- **둘은 분리된 별개 코드 공간이어야 한다.**

매핑 방식:
```
input_field + input_value + input_operator
    → condition_code 조회 (condition_mapping_candidate)
    → 매칭되는 semantic_clause_id 목록 반환
    → 이것이 실제 의무 목록
```

---

## 6. condition_type 체계 (초안)

| condition_type | 의미 | 예시 condition_code |
|---|---|---|
| WORK_ACT | 특정 작업 수행 여부 | WORK_ACT:CONFINED_SPACE |
| EQUIPMENT_ACT | 특정 설비/장비 보유 + 사용 | EQUIPMENT_ACT:TOWER_CRANE_INSTALL |
| FACILITY_ACT | 특정 시설 보유 | FACILITY_ACT:COLD_STORAGE |
| SITUATION | 특정 상황 발생 시 | SITUATION:PROHIBITED_HAZMAT_LEAK |
| THRESHOLD | 수치 기준 (인원수 등) | THRESHOLD:EMPLOYEE_GTE_50 |
| COMPOUND | 복합 조건 (AND/OR) | COMPOUND:BLASTING_HIGH_PRESSURE |
| NONE | 조건 없음 (모든 사업장) | - |
| OUT_OF_SCOPE | TAI Safe 범위 밖 | - |

---

## 7. 최종 답변

**입력값 → 조건코드 → 의무 원인추적이 가능한가?**

**YES. 가능하다. 단 전제조건:**

```
[가능] condition_text 있는 의무
입력: has_tower_crane = true
  → EQUIPMENT_ACT:TOWER_CRANE_* 조회
  → 규칙 제142조 3건 확정
  ✓ 원인추적 가능

[불가, 재처리 전] condition_text NULL
입력: has_chemical_substance = true
  → BUSINESS:REGISTERED 분류
  → "왜 이 의무가?" 설명 불가
  ✗ 재처리 필요

[가능, 재처리 후] B유형 추출
  → action_text: "관리대상 유해물질을 취급하는 실내작업장"
  → WORK_ACT:HAZMAT_HANDLE 추출
  → has_chemical_substance = true 연결
  ✓ 원인추적 가능
```

---

## 8. 다음 단계

### WO-CONDITION-002
condition_text가 있는 전체 의무 → condition_code 자동 추출  
방법: GPT 배치 처리  
산출물: condition_mapping_candidate 초안 (PENDING 상태)

### WO-CONDITION-003
condition_text NULL 의무 전수 재분류 (A/B/C)

### 판단 필요
condition_code 체계 = 엔진 아키텍처 영역 → **GPT에게 설계 요청 필요**

---

## 부록: 오류 의무 확정 목록

| 오류 유형 | semantic_clause | 실제 condition | 기존 Trigger | 올바른 input_field |
|---|---|---|---|---|
| 타워크레인↔이동식크레인 혼재 | 제142조 3건 | has_tower_crane=true | EQUIPMENT:CRANE | has_tower_crane |
| 잠함↔고압가스 혼재 | (별도 조회 필요) | has_caisson=? | WORK:HIGH_PRESSURE_GAS | has_caisson |
| 고압작업실 발파 혼재 | ac28a13d | has_blasting AND has_high_pressure | WORK:BLASTING | COMPOUND 조건 |
| TAI Safe 범위 밖 | 739cc8a7 (공동주택관리법) | N/A | BUSINESS:REGISTERED | C유형 제외 |

---

*WO-CONDITION-001 완료. 다음: GPT에게 condition_code 체계 설계 요청 또는 WO-CONDITION-002 진행.*
