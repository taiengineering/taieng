# Flow Registry Spec

**TASK 02-2 산출물 | 2026-05-15**

---

## 1. Flow Registry 개념

Flow Registry는 Watch Engine의 **기준(truth)** 역할을 한다.

```
business_event    = "무슨 일이 일어났는가" (사실)
engine_integrity  = "그것이 정상인가" (판단)
flow_registry     = "정상이란 무엇인가" (기준)
```

Watch Engine은 business_event를 수신했을 때 Flow Registry를 조회하여:
- 이 flow_key가 등록된 flow인가?
- 이 step_key가 해당 flow에 존재하는가?
- step_order 순서가 맞는가?
- timeout 범위 안인가?
- 비교해야 할 step 쌍이 있는가?

를 판단한다. **Registry에 없으면 판단 불가 → orphan_event.**

---

## 2. Registry 구조 (4개 테이블)

### 2.1 flow_registry — Flow 정의

| 필드 | 타입 | 필수 | 기본값 | 설명 |
|------|------|:---:|--------|------|
| id | uuid | ✅ | gen_random_uuid() | PK |
| tenant_id | text | ✅ | — | 고객사 식별 |
| environment | text | ✅ | 'production' | local/dev/staging/production |
| service_key | text | ✅ | — | 서비스 식별 |
| flow_key | text | ✅ | — | 업무 흐름 식별 |
| flow_name | text | ✅ | — | 사람이 읽을 수 있는 이름 |
| flow_type | text | ✅ | 'custom' | auth/billing/registration/diagnosis/scheduler/admin/external_api/custom |
| description | text | — | — | 흐름 설명 |
| is_active | bool | ✅ | true | 비활성 flow는 판단 대상에서 제외 |
| expected_step_count | smallint | ✅ | — | 정상 완료 시 기대 step 수 |
| expected_duration_ms | int | — | — | 전체 flow 기대 소요시간 |
| stuck_threshold_ms | int | ✅ | 60000 | stuck 판단 임계값 |
| max_retry_per_step | smallint | ✅ | 3 | flow 전체 기본 retry 상한 |
| requires_parent_flow | text | — | — | 선행 flow_key |
| created_at | timestamptz | ✅ | now() | — |
| updated_at | timestamptz | ✅ | now() | — |

**UK:** `(tenant_id, environment, service_key, flow_key)`

### 2.2 flow_step_registry — Step 정의

| 필드 | 타입 | 필수 | 기본값 | 설명 |
|------|------|:---:|--------|------|
| id | uuid | ✅ | gen_random_uuid() | PK |
| tenant_id | text | ✅ | — | — |
| environment | text | ✅ | 'production' | — |
| service_key | text | ✅ | — | — |
| flow_key | text | ✅ | — | FK → flow_registry |
| step_key | text | ✅ | — | 단계 식별 |
| step_order | smallint | ✅ | — | 0-based 순서 |
| step_name | text | ✅ | — | 사람이 읽을 수 있는 이름 |
| connector_type | text | ✅ | 'api' | api/browser/webhook/database/queue/scheduler |
| is_required | bool | ✅ | true | 필수 step |
| is_retryable | bool | ✅ | false | retry 허용 |
| max_retry_count | smallint | — | — | step별 retry 상한 |
| timeout_ms | int | — | — | step별 timeout |
| expected_result | text | ✅ | 'success' | 정상 결과 |
| is_branch_point | bool | ✅ | false | 분기점 여부 |
| branch_group | text | — | — | 분기 그룹 |
| payload_schema | jsonb | — | — | 기대 payload 구조 |
| created_at | timestamptz | ✅ | now() | — |
| updated_at | timestamptz | ✅ | now() | — |

**UK:** `(tenant_id, environment, service_key, flow_key, step_key)`

### 2.3 flow_integrity_rule_registry — Integrity Rule 정의

| 필드 | 타입 | 필수 | 기본값 | 설명 |
|------|------|:---:|--------|------|
| id | uuid | ✅ | gen_random_uuid() | PK |
| tenant_id | text | ✅ | — | — |
| environment | text | ✅ | 'production' | — |
| service_key | text | ✅ | — | — |
| flow_key | text | ✅ | — | FK → flow_registry |
| rule_key | text | ✅ | — | 규칙 식별 |
| rule_type | text | ✅ | — | required_field/field_match/hash_match/sequence/timeout/stuck/regression/schema_drift/required_step |
| source_step_key | text | — | — | 비교 원본 step |
| target_step_key | text | — | — | 비교 대상 step |
| source_field_path | text | — | — | jsonpath |
| target_field_path | text | — | — | jsonpath |
| operator | text | — | — | exists/equals/not_equals/contains/greater_than/less_than/hash_equals/is_true/is_subset |
| expected_value | text | — | — | 기대값 |
| severity_on_fail | text | ✅ | 'WARNING' | INFO/WARNING/CRITICAL/FATAL |
| integrity_status_on_fail | text | ✅ | 'mismatch' | — |
| health_status_on_fail | text | ✅ | 'warning' | — |
| description | text | — | — | — |
| is_active | bool | ✅ | true | — |
| evaluation_timing | text | ✅ | 'on_flow_complete' | on_event/on_flow_complete/on_schedule/on_scenario_complete |
| created_at | timestamptz | ✅ | now() | — |
| updated_at | timestamptz | ✅ | now() | — |

**UK:** `(tenant_id, environment, service_key, flow_key, rule_key)`

### 2.4 flow_scenario_binding — Golden Scenario 연결

| 필드 | 타입 | 필수 | 기본값 | 설명 |
|------|------|:---:|--------|------|
| id | uuid | ✅ | gen_random_uuid() | PK |
| tenant_id | text | ✅ | — | — |
| environment | text | ✅ | 'production' | — |
| service_key | text | ✅ | — | — |
| scenario_code | text | ✅ | — | FK → golden_scenario_registry |
| flow_key | text | ✅ | — | FK → flow_registry |
| execution_order | smallint | ✅ | 0 | scenario 내 flow 순서 |
| requires_parent_binding_id | uuid | — | — | 선행 binding |
| expected_trace_count | smallint | ✅ | 1 | 기대 trace 수 |
| expected_final_result | text | ✅ | 'success' | 최종 기대 결과 |
| is_active | bool | ✅ | true | — |
| created_at | timestamptz | ✅ | now() | — |

**UK:** `(tenant_id, environment, service_key, scenario_code, flow_key)`

---

## 3. 전체 관계도

```
golden_scenario_registry
        │ scenario_code
        ▼
flow_scenario_binding
        │ flow_key
        ▼
flow_registry ─── "정상 flow란 무엇인가"
    │         │
    │         │
    ▼         ▼
flow_step_   flow_integrity_rule_
registry     registry
    │              │
    │ 검증          │ 판단
    ▼              ▼
business_event ──▶ engine_integrity_event
```

---

## 4. 예시 3개

### 4.1 login (4 steps, 3 rules)

| step_order | step_key | connector | required | retryable | timeout_ms |
|:---:|----------|-----------|:---:|:---:|:---:|
| 0 | open_form | browser | ✅ | ❌ | — |
| 1 | submit_form | browser | ✅ | ✅ | 5000 |
| 2 | validate_auth | api | ✅ | ❌ | 5000 |
| 3 | read_result | api | ✅ | ❌ | 3000 |

Rules: login_cred_exists (required_field, on_event), login_timeout (timeout, on_event), login_sequence (sequence, on_flow_complete)

### 4.2 process_registration (7 steps, 6 rules)

| step_order | step_key | connector | required | retryable | timeout_ms |
|:---:|----------|-----------|:---:|:---:|:---:|
| 0 | open_form | browser | ✅ | ❌ | — |
| 1 | select_process_type | browser | ✅ | ❌ | — |
| 2 | submit_form | api | ✅ | ✅ | 10000 |
| 3 | validate_input | api | ✅ | ❌ | 5000 |
| 4 | save_db | database | ✅ | ❌ | 10000 |
| 5 | read_result | api | ✅ | ❌ | 5000 |
| 6 | render_result | browser | ✅ | ❌ | — |

Rules: reg_field_exists, reg_type_match (submit→read field_match), reg_hash_match (save→read), reg_sequence, reg_required_steps, reg_stuck

### 4.3 diagnosis_submit (6 steps, 7 rules)

| step_order | step_key | connector | required | retryable | timeout_ms |
|:---:|----------|-----------|:---:|:---:|:---:|
| 0 | input_conditions | browser | ✅ | ❌ | — |
| 1 | submit_form | api | ✅ | ✅ | 10000 |
| 2 | evaluate_rules | api | ✅ | ❌ | 30000 |
| 3 | save_db | database | ✅ | ❌ | 10000 |
| 4 | generate_output | api | ✅ | ✅ | 30000 |
| 5 | read_result | api | ✅ | ❌ | 5000 |

Rules: diag_field_exists, diag_eval_timeout (5s), diag_obligation_match (evaluate→read), diag_hash_match (save→read), diag_sequence, diag_stuck, diag_regression

Scenario bindings: FIRE_BUILDING_6200, OSH_FACTORY_50WORKERS, ELEC_TRANSFORMER_300KVA → diagnosis_submit

---

## 5. 위험 요소

1. Registry 미등록 = 판단 불가 (가장 큰 위험)
2. payload_schema 방치 = schema_drift 오탐 폭발
3. branch에서 expected_step_count 변동
4. tenant+env+service 조합 반복 → 데이터 양 증가
5. requires_parent_flow 검증 비용

---

## 6. 다음 구현 제안

| 순서 | 작업 | 도구 |
|------|------|------|
| 1 | Supabase migration 일괄 실행 (6개 테이블) | Supabase MCP |
| 2 | 3개 예시 flow 초기 데이터 INSERT | Supabase MCP |
| 3 | emitEvent() Python 함수 구현 | Cursor (tai-api) |
| 4 | TASK 03: Process Registration Flow Mapping | 기획창 |