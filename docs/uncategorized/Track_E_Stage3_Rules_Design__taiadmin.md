# Track E — Stage 3 객체화 룰 설계 시안

**작성일**: 2026-05-10  
**작성자**: PM 창 (Claude 기획창)  
**대상 인스턴스**: Track E 작업 인스턴스 + v3.0 마스터 구조 결정자  
**선행 보고서**: `Track_E_20260510_Stage1_Phase1.md`, `Track_E_20260510_Stage2_Phase1.md`  
**선행 시안**: `Track_E_Stage1_Rules_Design.md`

---

## 1. 본 시안의 위치 + 한계

### 1.1 Stage 3의 본질

Stage 3 = **stage_2_elements (sub_type 분류된 의미 요소) → 마스터 객체 (target_master_table) 정규화**

```
stage_2_elements (151,751 row, 25 sub_type)
   ↓ [rule_objectify 매칭]
   ↓ [field_mapping jsonb 변환]
stage_3_objects (object_type별 정규화된 의미 객체)
   ↓ [target_master_id 채우기 (마스터 테이블 INSERT/UPDATE)]
master_object_* (의무/금지/처벌/정의 등)
```

### 1.2 DB 스키마 (점검 결과)

**rule_objectify** (10 cols):
- `source_sub_type`: stage_2_elements.sub_type (25 enum 중)
- `target_master_table`: 객체화 대상 테이블명 (text)
- `field_mapping` (jsonb): {target_field: source_path} 매핑 (예: `{"duty_actor": "executor", "duty_action": "what"}`)
- `priority`, `enabled`, `description`

**stage_3_objects** (10 cols):
- `element_id`: stage_2_elements 참조 (NOT NULL)
- `target_master_table`: 어느 마스터 테이블에 매핑 (NOT NULL)
- `target_master_id`: 마스터 row id (UPSERT 후 채워짐)
- `field_values` (jsonb): 객체화된 필드 값 (NOT NULL)
- `mapping_rule_id`: 어느 rule_objectify 매칭 (FK SET NULL)
- `mapping_status`: SUCCESS / FAILED / SKIPPED 등 (NOT NULL)
- `error_message`: 매핑 실패 시 사유

### 1.3 본 PM 창의 한계 (중요)

| 항목 | 본 창 가능 | 후속 결정 영역 |
|---|---|---|
| sub_type → target_master_table 매핑 시안 | ✅ | - |
| field_mapping jsonb 시안 (24 sub_type) | ✅ | - |
| rule_objectify 룰 INSERT (DB) | ✅ | - |
| **v3.0 마스터 객체 테이블 신규 정의** | ❌ | **별도 마이그레이션 시안 + 사용자 결정** |
| stage_3_objects 적재 (Stage 2 Kiwi 정밀화 후) | ❌ | **Cursor (Stage 2 Phase 2 완료 후)** |
| target_master_id 채우기 (마스터 UPSERT) | ❌ | **마스터 테이블 정의 후** |

**중요 결정 사항** (v3.0 마스터 구조):
- 옵션 A: v3.0 신규 마스터 객체 테이블 신규 정의 (object_duty, object_prohibition, object_penalty, object_authority, object_definition, object_delegation, object_exemption, object_deeming) — 권고
- 옵션 B: 기존 master_rule_v2 활용 (40 cols, but v2.0 구조라 v3.0 의미 표현 한계)
- 옵션 C: stage_3_objects의 field_values jsonb에만 보전, 마스터 테이블 X (단순화, 후속 정규화 가능)

→ **본 시안은 옵션 A (신규 마스터 테이블) 가정**. 실제 적용 시 사용자 결정.

---

## 2. 25 sub_type → target_master_table 매핑 시안

### 2.1 핵심 8 객체화 (HEADER + DELEGATION + AS_본다)

| sub_type | target_master_table | 본질 |
|---|---|---|
| **OBLIGATION_HEADER** | `object_duty` | 의무 |
| **PROHIBITION_HEADER** | `object_prohibition` | 금지 |
| **PENALTY_HEADER** | `object_penalty` | 처벌 |
| **AUTHORITY_HEADER** | `object_authority` | 권한 |
| **EXEMPTION_HEADER** | `object_exemption` | 적용제외 |
| **DEFINITION_HEADER** | `object_definition` | 정의 |
| **DELEGATION_ACTIVE** | `object_delegation` | 위임 |
| **AS_본다** | `object_deeming` | 간주 (의제) |

### 2.2 ITEM 객체화 (parent의 child / target)

ITEM은 parent HEADER를 통해 객체화. parent 정보는 stage_1_clauses의 part 계층 (depth/parent_id) 또는 stage_2_elements 인접성에서 추출.

| sub_type | parent → target_master_table | child 역할 |
|---|---|---|
| OBLIGATION_DETAIL_ITEM | parent OBLIGATION_HEADER → `object_duty.detail_items` (jsonb array) | 의무 세부 항목 |
| PENALTY_VIOLATOR_ITEM | parent PENALTY_HEADER → `object_penalty.violator_target` | 처벌 대상자 |
| AUTHORITY_TARGET_ITEM | parent AUTHORITY_HEADER → `object_authority.target` | 권한 대상 |
| EXEMPTION_TARGET_ITEM | parent EXEMPTION_HEADER → `object_exemption.target` | 제외 대상 |
| DEFINITION_TARGET_ITEM | parent DEFINITION_HEADER → `object_definition.term` | 정의 용어 |
| PROHIBITION_TARGET_ITEM | parent PROHIBITION_HEADER → `object_prohibition.target` | 금지 대상 |

### 2.3 인접 단편 (parent에 통합)

| sub_type | 통합 대상 | 본질 |
|---|---|---|
| EXCEPTION_CLAUSE | parent object의 `exception` 필드 (text) | 단서 (다만,) |
| ENUMERATION_ITEM | parent object의 `enumeration_items` (jsonb array) | 열거 항목 |
| DEFINITION_INTRO | parent DEFINITION_HEADER 그룹의 metadata | 정의 도입 |
| DELEGATED_WAIVER | parent OBLIGATION/PROHIBITION의 `waiver` 필드 | 위임된 면제 |

### 2.4 SKIP (객체화 X)

| sub_type | 사유 |
|---|---|
| **DELETED** | 삭제된 조문, 마스터 객체 X |
| **PARSE_FRAGMENT** | 파싱 단편, 의미 객체 아님 |
| **UNCLASSIFIED** | 미분류, Stage 2 정밀화 후 재시도 |
| **TITLE_HEADER** | 조문 제목 메타데이터 (별도 marker 가능) |
| **DATE_EFFECTIVE** | 시행일 메타데이터 (별도 marker 가능) |
| **WEAK_한다단순 / WEAK_있다단순** | 약함 (다른 룰 매칭 X 후 fallback), 객체 모호 |

→ Track A `Stage3Objectifier.SKIP_MAPPING_SUBTYPES = {UNCLASSIFIED, DELETED, PARSE_FRAGMENT}` 정합.

---

## 3. field_mapping jsonb 시안 (8 핵심 객체)

### 3.1 OBLIGATION_HEADER → object_duty

```json
{
  "rule_name": "OBJECTIFY_OBLIGATION",
  "source_sub_type": "OBLIGATION_HEADER",
  "target_master_table": "object_duty",
  "priority": 10,
  "field_mapping": {
    "duty_actor":         "$.executor",
    "duty_recipient":     "$.recipient",
    "duty_action":        "$.what",
    "duty_timing":        "$.when_value",
    "duty_location":      "$.where_value",
    "duty_method":        "$.how",
    "duty_condition":     "$.condition",
    "duty_if_pattern":    "$.if_pattern",
    "duty_exception":     "$.exception",
    "duty_source_clause": "$.clause_id",
    "duty_source_text":   "$.source_text"
  }
}
```

### 3.2 PROHIBITION_HEADER → object_prohibition

```json
{
  "rule_name": "OBJECTIFY_PROHIBITION",
  "source_sub_type": "PROHIBITION_HEADER",
  "target_master_table": "object_prohibition",
  "priority": 20,
  "field_mapping": {
    "prohib_actor":      "$.executor",
    "prohib_action":     "$.what",
    "prohib_target":     "$.recipient",
    "prohib_condition":  "$.condition",
    "prohib_if_pattern": "$.if_pattern",
    "prohib_exception":  "$.exception",
    "prohib_source_clause": "$.clause_id",
    "prohib_source_text": "$.source_text"
  }
}
```

### 3.3 PENALTY_HEADER → object_penalty

```json
{
  "rule_name": "OBJECTIFY_PENALTY",
  "source_sub_type": "PENALTY_HEADER",
  "target_master_table": "object_penalty",
  "priority": 30,
  "field_mapping": {
    "penalty_violator":   "$.recipient",
    "penalty_offense":    "$.condition",
    "penalty_punishment": "$.what",
    "penalty_amount_max": null,
    "penalty_amount_min": null,
    "penalty_imprisonment_max": null,
    "penalty_source_clause": "$.clause_id",
    "penalty_source_text":   "$.source_text"
  }
}
```
※ amount/imprisonment 값은 별도 정규식 추출 후속 (예: "1년 이하의 징역" → imprisonment_max=1, unit=year)

### 3.4 AUTHORITY_HEADER → object_authority

```json
{
  "rule_name": "OBJECTIFY_AUTHORITY",
  "source_sub_type": "AUTHORITY_HEADER",
  "target_master_table": "object_authority",
  "priority": 40,
  "field_mapping": {
    "auth_actor":      "$.executor",
    "auth_action":     "$.what",
    "auth_target":     "$.recipient",
    "auth_condition":  "$.condition",
    "auth_if_pattern": "$.if_pattern",
    "auth_exception":  "$.exception",
    "auth_source_clause": "$.clause_id",
    "auth_source_text":   "$.source_text"
  }
}
```

### 3.5 EXEMPTION_HEADER → object_exemption

```json
{
  "rule_name": "OBJECTIFY_EXEMPTION",
  "source_sub_type": "EXEMPTION_HEADER",
  "target_master_table": "object_exemption",
  "priority": 50,
  "field_mapping": {
    "exempt_target":    "$.recipient",
    "exempt_subject":   "$.what",
    "exempt_condition": "$.condition",
    "exempt_scope":     "$.where_value",
    "exempt_source_clause": "$.clause_id",
    "exempt_source_text":   "$.source_text"
  }
}
```

### 3.6 DEFINITION_HEADER → object_definition

```json
{
  "rule_name": "OBJECTIFY_DEFINITION",
  "source_sub_type": "DEFINITION_HEADER",
  "target_master_table": "object_definition",
  "priority": 60,
  "field_mapping": {
    "def_term":           null,
    "def_explanation":    "$.what",
    "def_scope":          "$.where_value",
    "def_source_clause":  "$.clause_id",
    "def_source_text":    "$.source_text"
  }
}
```
※ def_term은 head 토큰 분석 (例: "「자동차」란") 또는 인접 DEFINITION_INTRO/TARGET_ITEM에서 추출

### 3.7 DELEGATION_ACTIVE → object_delegation

```json
{
  "rule_name": "OBJECTIFY_DELEGATION",
  "source_sub_type": "DELEGATION_ACTIVE",
  "target_master_table": "object_delegation",
  "priority": 70,
  "field_mapping": {
    "deleg_subject":    "$.what",
    "deleg_target":     "$.where_value",
    "deleg_authority":  "$.executor",
    "deleg_condition":  "$.condition",
    "deleg_source_clause": "$.clause_id",
    "deleg_source_text":   "$.source_text"
  }
}
```
※ deleg_target = 위임 대상 ("대통령령으로", "총리령으로", "산업통상자원부령으로" 등)

### 3.8 AS_본다 → object_deeming

```json
{
  "rule_name": "OBJECTIFY_DEEMING",
  "source_sub_type": "AS_본다",
  "target_master_table": "object_deeming",
  "priority": 80,
  "field_mapping": {
    "deem_subject":    "$.executor",
    "deem_target":     "$.what",
    "deem_condition":  "$.condition",
    "deem_source_clause": "$.clause_id",
    "deem_source_text":   "$.source_text"
  }
}
```

---

## 4. ITEM 객체화 룰 (parent join)

ITEM 시안은 parent HEADER 정보가 필요. Stage 3 적용 시 stage_2_elements에 인접성 + part 계층 정보 활용:

```sql
-- ITEM의 parent HEADER 발견 (예: OBLIGATION_DETAIL_ITEM의 parent OBLIGATION_HEADER)
SELECT 
  child.id AS item_element_id,
  parent.id AS header_element_id,
  child.sub_type AS item_subtype,
  parent.sub_type AS header_subtype
FROM stage_2_elements child
JOIN stage_1_clauses cc ON cc.id = child.clause_id
JOIN law_article_part child_part ON child_part.id = cc.part_id
JOIN law_article_part parent_part ON parent_part.id = child_part.parent_id
JOIN stage_1_clauses pc ON pc.part_id = parent_part.id
JOIN stage_2_elements parent ON parent.clause_id = pc.id
WHERE child.sub_type LIKE '%_ITEM' AND parent.sub_type LIKE '%_HEADER';
```

ITEM 룰 시안 (예: OBLIGATION_DETAIL_ITEM):

```json
{
  "rule_name": "OBJECTIFY_OBLIGATION_DETAIL_ITEM",
  "source_sub_type": "OBLIGATION_DETAIL_ITEM",
  "target_master_table": "object_duty",
  "priority": 110,
  "field_mapping": {
    "_join_to_parent":   "find_parent_OBLIGATION_HEADER",
    "_action": "append_to_detail_items",
    "detail_item_text":  "$.source_text",
    "detail_item_clause_id": "$.clause_id"
  }
}
```

→ 본 ITEM 룰은 별도 적재 X, parent object_duty의 `detail_items` jsonb array에 append.

---

## 5. 인접 단편 처리 룰 (EXCEPTION/ENUMERATION/DEFINITION_INTRO)

### 5.1 EXCEPTION_CLAUSE 통합

EXCEPTION_CLAUSE는 직전 sibling object의 `exception` 필드에 통합:

```sql
-- 직전 sibling 발견 (같은 part, clause_position - 1)
WITH prev_siblings AS (
  SELECT 
    s2_curr.id AS exception_id,
    s2_prev.id AS parent_id,
    s2_prev.sub_type AS parent_subtype,
    s2_curr.clause_id,
    s1_curr.source_text AS exception_text
  FROM stage_2_elements s2_curr
  JOIN stage_1_clauses s1_curr ON s1_curr.id = s2_curr.clause_id
  JOIN stage_1_clauses s1_prev ON s1_prev.part_id = s1_curr.part_id 
    AND s1_prev.clause_position = s1_curr.clause_position - 1
  JOIN stage_2_elements s2_prev ON s2_prev.clause_id = s1_prev.id
  WHERE s2_curr.sub_type = 'EXCEPTION_CLAUSE'
)
-- parent object의 field_values.exception에 append
```

### 5.2 ENUMERATION_ITEM 통합

ENUMERATION_ITEM은 parent의 `enumeration_items` jsonb array에 append (ITEM과 동일 패턴).

### 5.3 DEFINITION_INTRO 통합

DEFINITION_INTRO는 parent DEFINITION_HEADER 그룹의 metadata로 통합 (예: "다음 각 호와 같다" 헤더).

---

## 6. rule_objectify INSERT SQL 시안

### 6.1 핵심 8 룰 (HEADER + DELEGATION + AS_본다)

```sql
INSERT INTO rule_objectify (rule_name, source_sub_type, target_master_table, field_mapping, priority, enabled, description) VALUES
  ('OBJECTIFY_OBLIGATION',  'OBLIGATION_HEADER',  'object_duty', 
   '{"duty_actor":"$.executor","duty_recipient":"$.recipient","duty_action":"$.what","duty_timing":"$.when_value","duty_location":"$.where_value","duty_method":"$.how","duty_condition":"$.condition","duty_if_pattern":"$.if_pattern","duty_exception":"$.exception","duty_source_clause":"$.clause_id","duty_source_text":"$.source_text"}'::jsonb,
   10, true, '의무 객체화 (~어야 한다 / ~해야 한다)'),

  ('OBJECTIFY_PROHIBITION', 'PROHIBITION_HEADER', 'object_prohibition',
   '{"prohib_actor":"$.executor","prohib_action":"$.what","prohib_target":"$.recipient","prohib_condition":"$.condition","prohib_if_pattern":"$.if_pattern","prohib_exception":"$.exception","prohib_source_clause":"$.clause_id","prohib_source_text":"$.source_text"}'::jsonb,
   20, true, '금지 객체화 (~할 수 없다 / ~지 아니된다)'),

  ('OBJECTIFY_PENALTY', 'PENALTY_HEADER', 'object_penalty',
   '{"penalty_violator":"$.recipient","penalty_offense":"$.condition","penalty_punishment":"$.what","penalty_source_clause":"$.clause_id","penalty_source_text":"$.source_text"}'::jsonb,
   30, true, '처벌 객체화 (처한다 / 과한다 / 부과한다). 후속: amount/imprisonment 정규식 추출.'),

  ('OBJECTIFY_AUTHORITY', 'AUTHORITY_HEADER', 'object_authority',
   '{"auth_actor":"$.executor","auth_action":"$.what","auth_target":"$.recipient","auth_condition":"$.condition","auth_if_pattern":"$.if_pattern","auth_exception":"$.exception","auth_source_clause":"$.clause_id","auth_source_text":"$.source_text"}'::jsonb,
   40, true, '권한 객체화 (~할 수 있다)'),

  ('OBJECTIFY_EXEMPTION', 'EXEMPTION_HEADER', 'object_exemption',
   '{"exempt_target":"$.recipient","exempt_subject":"$.what","exempt_condition":"$.condition","exempt_scope":"$.where_value","exempt_source_clause":"$.clause_id","exempt_source_text":"$.source_text"}'::jsonb,
   50, true, '적용 제외 객체화 (적용하지 아니한다 / 제외한다)'),

  ('OBJECTIFY_DEFINITION', 'DEFINITION_HEADER', 'object_definition',
   '{"def_term":null,"def_explanation":"$.what","def_scope":"$.where_value","def_source_clause":"$.clause_id","def_source_text":"$.source_text"}'::jsonb,
   60, true, '정의 객체화 (말한다 / 이라 한다). def_term은 head 토큰 분석 후속.'),

  ('OBJECTIFY_DELEGATION', 'DELEGATION_ACTIVE', 'object_delegation',
   '{"deleg_subject":"$.what","deleg_target":"$.where_value","deleg_authority":"$.executor","deleg_condition":"$.condition","deleg_source_clause":"$.clause_id","deleg_source_text":"$.source_text"}'::jsonb,
   70, true, '위임 객체화 (~으로 정한다)'),

  ('OBJECTIFY_DEEMING', 'AS_본다', 'object_deeming',
   '{"deem_subject":"$.executor","deem_target":"$.what","deem_condition":"$.condition","deem_source_clause":"$.clause_id","deem_source_text":"$.source_text"}'::jsonb,
   80, true, '간주(의제) 객체화 (~으로 본다)');
```

### 6.2 ITEM 6 룰 (parent join 패턴)

```sql
INSERT INTO rule_objectify (rule_name, source_sub_type, target_master_table, field_mapping, priority, enabled, description) VALUES
  ('OBJECTIFY_OBLIGATION_DETAIL_ITEM', 'OBLIGATION_DETAIL_ITEM', 'object_duty',
   '{"_action":"append_to_parent","_parent_field":"detail_items","item_text":"$.source_text","item_clause_id":"$.clause_id"}'::jsonb,
   110, true, 'OBLIGATION_HEADER의 detail_items array에 append'),
  ('OBJECTIFY_PENALTY_VIOLATOR_ITEM', 'PENALTY_VIOLATOR_ITEM', 'object_penalty',
   '{"_action":"append_to_parent","_parent_field":"violators","item_text":"$.source_text","item_clause_id":"$.clause_id"}'::jsonb,
   120, true, 'PENALTY_HEADER의 violators array에 append'),
  ('OBJECTIFY_AUTHORITY_TARGET_ITEM', 'AUTHORITY_TARGET_ITEM', 'object_authority',
   '{"_action":"append_to_parent","_parent_field":"targets","item_text":"$.source_text","item_clause_id":"$.clause_id"}'::jsonb,
   130, true, 'AUTHORITY_HEADER의 targets array에 append'),
  ('OBJECTIFY_EXEMPTION_TARGET_ITEM', 'EXEMPTION_TARGET_ITEM', 'object_exemption',
   '{"_action":"append_to_parent","_parent_field":"targets","item_text":"$.source_text","item_clause_id":"$.clause_id"}'::jsonb,
   140, true, 'EXEMPTION_HEADER의 targets array에 append'),
  ('OBJECTIFY_DEFINITION_TARGET_ITEM', 'DEFINITION_TARGET_ITEM', 'object_definition',
   '{"_action":"append_to_parent","_parent_field":"terms","item_text":"$.source_text","item_clause_id":"$.clause_id"}'::jsonb,
   150, true, 'DEFINITION_HEADER의 terms array에 append'),
  ('OBJECTIFY_PROHIBITION_TARGET_ITEM', 'PROHIBITION_TARGET_ITEM', 'object_prohibition',
   '{"_action":"append_to_parent","_parent_field":"targets","item_text":"$.source_text","item_clause_id":"$.clause_id"}'::jsonb,
   160, true, 'PROHIBITION_HEADER의 targets array에 append');
```

### 6.3 인접 단편 4 룰

```sql
INSERT INTO rule_objectify (rule_name, source_sub_type, target_master_table, field_mapping, priority, enabled, description) VALUES
  ('OBJECTIFY_EXCEPTION_CLAUSE', 'EXCEPTION_CLAUSE', 'parent_object',
   '{"_action":"append_to_prev_sibling","_target_field":"exception","exception_text":"$.source_text","exception_clause_id":"$.clause_id"}'::jsonb,
   200, true, '직전 sibling object의 exception 필드에 append'),
  ('OBJECTIFY_ENUMERATION_ITEM', 'ENUMERATION_ITEM', 'parent_object',
   '{"_action":"append_to_parent","_parent_field":"enumeration_items","item_text":"$.source_text","item_clause_id":"$.clause_id"}'::jsonb,
   210, true, 'parent object의 enumeration_items array에 append'),
  ('OBJECTIFY_DEFINITION_INTRO', 'DEFINITION_INTRO', 'object_definition',
   '{"_action":"merge_to_parent_metadata","_target_field":"intro","intro_text":"$.source_text"}'::jsonb,
   220, true, 'DEFINITION 그룹의 intro 메타데이터로 통합'),
  ('OBJECTIFY_DELEGATED_WAIVER', 'DELEGATED_WAIVER', 'parent_object',
   '{"_action":"append_to_parent","_parent_field":"waiver","waiver_text":"$.source_text","waiver_clause_id":"$.clause_id"}'::jsonb,
   230, true, 'parent OBLIGATION/PROHIBITION의 waiver 필드에 추가');
```

### 6.4 SKIP / metadata-only 4 룰

```sql
INSERT INTO rule_objectify (rule_name, source_sub_type, target_master_table, field_mapping, priority, enabled, description) VALUES
  ('OBJECTIFY_TITLE_HEADER_METADATA', 'TITLE_HEADER', 'object_metadata',
   '{"meta_type":"article_title","title_text":"$.source_text","title_clause_id":"$.clause_id"}'::jsonb,
   300, true, '조문 제목 메타데이터 (별도 marker)'),
  ('OBJECTIFY_DATE_EFFECTIVE_METADATA', 'DATE_EFFECTIVE', 'object_metadata',
   '{"meta_type":"effective_date","date_text":"$.source_text","date_clause_id":"$.clause_id"}'::jsonb,
   310, true, '시행일 메타데이터'),
  ('OBJECTIFY_WEAK_HANDA', 'WEAK_한다단순', 'object_uncategorized',
   '{"weak_type":"한다","source_text":"$.source_text","clause_id":"$.clause_id"}'::jsonb,
   400, true, 'WEAK_한다단순 fallback 보전 (Stage 2 정밀화 후 재시도 후보)'),
  ('OBJECTIFY_WEAK_ITDA', 'WEAK_있다단순', 'object_uncategorized',
   '{"weak_type":"있다","source_text":"$.source_text","clause_id":"$.clause_id"}'::jsonb,
   410, true, 'WEAK_있다단순 fallback 보전');
```

### 6.5 SKIP (룰 없음, Track A SKIP_MAPPING_SUBTYPES 정합)

- **DELETED**: 객체화 X (skip)
- **PARSE_FRAGMENT**: 객체화 X
- **UNCLASSIFIED**: 객체화 X (Stage 2 Phase 2 Kiwi 정밀화 후 재시도)

총 룰 시안: **22개** (HEADER 8 + ITEM 6 + 단편 4 + metadata/weak 4)

---

## 7. Stage 3 적용 절차 (Track E 작업 인스턴스용)

### 7.1 사전 조건

- ✅ Track E Stage 1 Phase 1 완료 (151,751 stage_1_clauses)
- ✅ Track E Stage 2 Phase 1 완료 (151,751 stage_2_elements, 5.41% 정확 분류)
- ⏳ Track E Stage 2 Phase 2 (Kiwi 정밀화) — sub_type UNCLASSIFIED 143,542건 정밀 분류 필요
- ⏳ v3.0 마스터 객체 테이블 정의 (object_duty, object_prohibition 등)

### 7.2 Stage 3 진입 조건

마스터 §3.4 정합:
- **Stage 2 sub_type 정확 분류 ≥ 90%** (현재 5.41% → Kiwi 정밀화 후 70-85% 도달 필수)
- **6하원칙 분해 sample 정확도 ≥ 90%** (현재 0% — Kiwi 정밀화 결과)

→ Stage 3는 Stage 2 Phase 2 (Cursor) 완료 + sample 검증 후 진입.

### 7.3 적용 SQL 패턴

```sql
-- Stage 3 1차 적용 (UNCLASSIFIED/DELETED/PARSE_FRAGMENT skip)
INSERT INTO stage_3_objects (element_id, target_master_table, field_values, mapping_rule_id, mapping_status)
SELECT 
  s2.id AS element_id,
  ro.target_master_table,
  -- field_mapping의 $.executor → s2.executor 등 변환
  jsonb_build_object(
    'duty_actor', s2.executor,
    'duty_recipient', s2.recipient,
    'duty_action', s2.what,
    -- ...
    '_metadata', jsonb_build_object(
      'sub_type', s2.sub_type,
      'if_pattern', s2.if_pattern,
      'confidence', s2.confidence_score,
      'phase', 'phase_1'
    )
  ) AS field_values,
  ro.id AS mapping_rule_id,
  CASE 
    WHEN s2.confidence_score >= 0.7 THEN 'SUCCESS'
    WHEN s2.confidence_score >= 0.5 THEN 'PARTIAL'
    ELSE 'FAILED'
  END AS mapping_status
FROM stage_2_elements s2
JOIN rule_objectify ro ON ro.source_sub_type = s2.sub_type AND ro.enabled = true
WHERE s2.sub_type NOT IN ('UNCLASSIFIED', 'DELETED', 'PARSE_FRAGMENT');
```

### 7.4 검증 (마스터 §3.4 + Track A validator.py)

| check_name | expected | threshold |
|---|---|---|
| count_mapping_classifiable_subtype | UNCLASSIFIED/DELETED/PARSE_FRAGMENT 외 → stage_3_objects | 100% |
| target_master_table_check | NULL 0건 (모두 매칭) | 0 |
| field_values_keys_check | 룰별 필수 키 보유 | 0 |
| sample_accuracy (사람) | ≥ 90% (마스터 §3.4) | 90% |
| mapping_status_success_rate | ≥ 70% (confidence ≥ 0.7) | 70% |

---

## 8. v3.0 마스터 객체 테이블 정의 시안 (별도 마이그레이션)

### 8.1 권고 테이블 8개 (옵션 A)

```sql
-- object_duty (의무)
CREATE TABLE object_duty (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  duty_actor TEXT,
  duty_recipient TEXT,
  duty_action TEXT,
  duty_timing TEXT,
  duty_location TEXT,
  duty_method TEXT,
  duty_condition TEXT,
  duty_if_pattern TEXT,
  duty_exception TEXT,
  duty_source_clause UUID REFERENCES stage_1_clauses(id),
  duty_source_text TEXT,
  detail_items JSONB DEFAULT '[]'::jsonb,
  enumeration_items JSONB DEFAULT '[]'::jsonb,
  waiver TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- object_prohibition (금지)
CREATE TABLE object_prohibition (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  prohib_actor TEXT,
  prohib_action TEXT,
  prohib_target TEXT,
  prohib_condition TEXT,
  prohib_if_pattern TEXT,
  prohib_exception TEXT,
  prohib_source_clause UUID REFERENCES stage_1_clauses(id),
  prohib_source_text TEXT,
  targets JSONB DEFAULT '[]'::jsonb,
  enumeration_items JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- object_penalty (처벌)
CREATE TABLE object_penalty (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  penalty_violator TEXT,
  penalty_offense TEXT,
  penalty_punishment TEXT,
  penalty_amount_max NUMERIC,
  penalty_amount_min NUMERIC,
  penalty_imprisonment_max INTEGER,
  penalty_unit TEXT,
  penalty_source_clause UUID REFERENCES stage_1_clauses(id),
  penalty_source_text TEXT,
  violators JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- object_authority (권한)
CREATE TABLE object_authority (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  auth_actor TEXT,
  auth_action TEXT,
  auth_target TEXT,
  auth_condition TEXT,
  auth_if_pattern TEXT,
  auth_exception TEXT,
  auth_source_clause UUID REFERENCES stage_1_clauses(id),
  auth_source_text TEXT,
  targets JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- object_exemption (적용제외)
CREATE TABLE object_exemption (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  exempt_target TEXT,
  exempt_subject TEXT,
  exempt_condition TEXT,
  exempt_scope TEXT,
  exempt_source_clause UUID REFERENCES stage_1_clauses(id),
  exempt_source_text TEXT,
  targets JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- object_definition (정의)
CREATE TABLE object_definition (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  def_term TEXT,
  def_explanation TEXT,
  def_scope TEXT,
  def_source_clause UUID REFERENCES stage_1_clauses(id),
  def_source_text TEXT,
  intro TEXT,
  terms JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- object_delegation (위임)
CREATE TABLE object_delegation (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  deleg_subject TEXT,
  deleg_target TEXT,
  deleg_authority TEXT,
  deleg_condition TEXT,
  deleg_source_clause UUID REFERENCES stage_1_clauses(id),
  deleg_source_text TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- object_deeming (간주/의제)
CREATE TABLE object_deeming (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  deem_subject TEXT,
  deem_target TEXT,
  deem_condition TEXT,
  deem_source_clause UUID REFERENCES stage_1_clauses(id),
  deem_source_text TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- object_metadata (TITLE_HEADER, DATE_EFFECTIVE 등)
CREATE TABLE object_metadata (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  meta_type TEXT NOT NULL CHECK (meta_type IN ('article_title','effective_date','amendment_date')),
  meta_text TEXT,
  meta_clause_id UUID REFERENCES stage_1_clauses(id),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- object_uncategorized (WEAK fallback)
CREATE TABLE object_uncategorized (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  weak_type TEXT,
  source_text TEXT,
  clause_id UUID REFERENCES stage_1_clauses(id),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

→ **8 핵심 + 1 metadata + 1 uncategorized = 10 테이블** 신규 마이그레이션.

---

## 9. 마스터 §2 절대 원칙 점검

| 원칙 | 본 시안 정합 |
|---|---|
| ① LLM X | ✅ 룰베이스 객체화 + Kiwi POS 시그니처 |
| ② 법령 보전 | ✅ source_text 모두 보전 (각 객체에 source_clause_id + source_text) |
| ③ 누락 0건 | ✅ SKIP 3 sub_type 외 모두 stage_3_objects 적재 + UNCLASSIFIED는 Stage 2 Phase 2 후 재시도 |
| ④ 100% 매핑 | ✅ stage_2_elements → stage_3_objects 1:N (parent + ITEM 통합) |
| ⑤ 오염 = 폐기 | ✅ confidence_score < 0.5 → mapping_status='FAILED' (별도 처리) |
| ⑥ 검증 부담 0 | ✅ 룰베이스 + verification_log |
| ⑦ Ground Truth 우선 | ✅ source_text 보전 |
| ⑧ DB가 ground truth | ✅ rule_objectify CHECK 제약 + stage_3_objects FK 검증 |

---

## 10. 펜딩 사항 + 후속 트리거

### 10.1 본 시안 적용 전 결정 사항 (사용자/별도 인스턴스)

1. **v3.0 마스터 객체 테이블 정의** — §8 시안 또는 다른 방식 (옵션 A/B/C 결정)
2. **Stage 2 Phase 2 완료** (Cursor) — UNCLASSIFIED 143,542건 Kiwi 정밀화
3. **6하원칙 분해 적용** (Cursor) — executor/recipient/what 등 stage_2_elements 컬럼 채우기

### 10.2 Stage 3 적용 시점 작업 (후속 인스턴스)

1. **마이그레이션** §8의 10 테이블 CREATE TABLE
2. **rule_objectify 22 룰 INSERT** (§6 SQL)
3. **stage_3_objects 적재** (§7.3 INSERT-SELECT)
4. **target_master_id UPSERT** (object_duty 등 마스터 row 생성 + stage_3_objects.target_master_id 채우기)
5. **검증** (§7.4)
6. **verification_log 적재** (Stage 3, 5+ row)

### 10.3 v3 마스터 합성 (Stage 3 후속)

object_duty / object_prohibition 등 = v3.0 마스터의 본질 산출물. 이걸 어떻게 외부 사용자(법무 담당자)에게 노출할지는 별도 결정 (API + UI + 검색).

---

## 11. 산출물 인덱스

### 본 시안 산출물
- 본 문서: `docs/extraction/v3/log/Track_E_Stage3_Rules_Design.md`
- rule_objectify 22 룰 INSERT SQL (§6)
- v3.0 마스터 객체 테이블 10 CREATE TABLE 시안 (§8)
- field_mapping jsonb 24 sub_type 시안 (§3, §4, §5)

### DB 영향 (적용 시)
- `rule_objectify`: +22 row
- 신규 테이블 10개 (object_*)
- `stage_3_objects`: 약 130,000~140,000 row 예상 (UNCLASSIFIED 제외)

### 보고서 chronology
- 선행: Stage 1 Phase 1 + Stage 2 Phase 1 (PM 창)
- 본 시안: Stage 3 진입 가능한 룰 골격 + 마스터 구조 결정 안내
- 후속: Stage 2 Phase 2 (Cursor Kiwi 정밀화) → v3.0 마스터 결정 → Stage 3 진입

---

**END — Stage 3 진입 가능한 룰 시안 + v3.0 마스터 구조 결정 트리거. Stage 2 Phase 2 완료 + 마스터 결정 후 적용.**
