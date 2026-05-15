# Standard Event Schema

**TASK 02 산출물 | 2026-05-15**

---

## 설계 원칙

1. **행위 이벤트 ≠ 판단 결과** — 분리 필수
2. **서비스/DB/프론트엔드/API 종속 금지** — 범용 SaaS 구조
3. **Flow/Trace 기반 운영 해석** — 단일 이벤트 저장이 아님
4. **PII 저장 금지** — payload_summary + payload_hash만 허용
5. **기존 자산 재사용** — engine_integrity_event → Integrity Result Store

---

## A. Raw Business Event — `business_event`

신규 테이블. 실제 발생한 업무 이벤트를 기록.

```sql
CREATE TABLE business_event (
    -- ─── Identity ───
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- ─── Tenant / Environment ───
    tenant_id       text NOT NULL,                -- 고객사 식별 (서비스 종속 아님)
    environment     text NOT NULL DEFAULT 'production',
                    -- local | dev | staging | production
    
    -- ─── Flow 위치 ───
    service_key     text NOT NULL,                -- 서비스 식별 (예: tai-api, tai-admin)
    flow_key        text NOT NULL,                -- 업무 흐름 식별 (예: process_registration, login, diagnosis)
    step_key        text NOT NULL,                -- 단계 식별 (예: submit_form, validate, db_save, read_result)
    step_order      smallint NOT NULL DEFAULT 0,  -- 흐름 내 순서 (0-based)
    
    -- ─── Trace / Correlation ───
    trace_id        text NOT NULL,                -- 단일 흐름 추적 ID
    parent_trace_id text,                         -- 상위 흐름 연결 (multi-step)
    session_id      text,                         -- 사용자 세션 연결
    scenario_run_id text,                         -- synthetic/regression 실행 연결
    
    -- ─── Actor / Connector ───
    actor_type      text NOT NULL DEFAULT 'system',
                    -- user | admin | system | synthetic_user | scheduler
    connector_type  text NOT NULL DEFAULT 'api',
                    -- api | browser | webhook | database | queue | scheduler
    
    -- ─── Event 본체 ───
    event_type      text NOT NULL,                -- 이벤트 유형 (예: submit, validate, save, read, timeout, error)
    result          text NOT NULL DEFAULT 'pending',
                    -- success | failure | timeout | skipped | pending
    
    -- ─── Payload (PII 금지) ───
    payload_summary jsonb,                        -- 구조화된 요약만 허용
                    -- 허용: required_field_exists, enum_key, count, boolean_status
                    -- 금지: 이름, 전화번호, 주소, 이메일 등 PII
    payload_hash    text,                         -- payload 무결성 검증용 hash
    
    -- ─── Timestamp ───
    created_at      timestamptz NOT NULL DEFAULT now(),
    
    -- ─── Constraints ───
    CONSTRAINT business_event_result_check 
        CHECK (result IN ('success','failure','timeout','skipped','pending')),
    CONSTRAINT business_event_actor_check 
        CHECK (actor_type IN ('user','admin','system','synthetic_user','scheduler')),
    CONSTRAINT business_event_connector_check 
        CHECK (connector_type IN ('api','browser','webhook','database','queue','scheduler')),
    CONSTRAINT business_event_env_check 
        CHECK (environment IN ('local','dev','staging','production'))
);

-- ─── 조회 패턴 기반 인덱스 ───
CREATE INDEX idx_be_trace ON business_event (trace_id);
CREATE INDEX idx_be_flow  ON business_event (tenant_id, flow_key, created_at DESC);
CREATE INDEX idx_be_scenario ON business_event (scenario_run_id) WHERE scenario_run_id IS NOT NULL;
CREATE INDEX idx_be_time  ON business_event (created_at DESC);
CREATE INDEX idx_be_result ON business_event (result, created_at DESC) WHERE result != 'success';
```

---

## B. Integrity Result — `engine_integrity_event` 확장

기존 테이블 재사용. Watch Engine이 Business Event를 해석한 **판단 결과**.

```sql
-- 기존 engine_integrity_event에 필드 추가 (ALTER)
ALTER TABLE engine_integrity_event
    ADD COLUMN IF NOT EXISTS tenant_id        text,
    ADD COLUMN IF NOT EXISTS environment      text DEFAULT 'production',
    ADD COLUMN IF NOT EXISTS service_key      text,
    ADD COLUMN IF NOT EXISTS flow_key         text,
    ADD COLUMN IF NOT EXISTS step_key         text,
    ADD COLUMN IF NOT EXISTS trace_id         text,
    ADD COLUMN IF NOT EXISTS scenario_run_id  text,
    ADD COLUMN IF NOT EXISTS integrity_status text DEFAULT 'unknown',
    ADD COLUMN IF NOT EXISTS health_status    text DEFAULT 'unknown',
    ADD COLUMN IF NOT EXISTS source_event_id  uuid;
    -- source_event_id → business_event.id 참조 (FK 선택)

-- 기존 필드 매핑:
--   event_type    → 그대로 (integrity 이벤트 유형: payload_missing, db_mismatch, stuck_detected 등)
--   severity      → 그대로 (INFO, WARNING, CRITICAL, FATAL)
--   domain        → service_key로 대체 가능하나 하위호환 유지
--   description   → 그대로
--   detail(jsonb) → 그대로
--   input_hash    → payload_hash 역할
--   source_trace  → trace_id로 대체 가능하나 하위호환 유지
--   resolved/*    → 그대로 (해결 추적)

-- ─── 추가 인덱스 ───
CREATE INDEX IF NOT EXISTS idx_eie_trace ON engine_integrity_event (trace_id) WHERE trace_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_eie_flow  ON engine_integrity_event (flow_key, created_at DESC) WHERE flow_key IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_eie_unresolved ON engine_integrity_event (severity, created_at DESC) WHERE resolved = false;
```

---

## 필드 배치 매트릭스 (Architect 지정 20개 필드)

| # | 필드 | Business Event | Integrity Result | 비고 |
|---|------|:-:|:-:|------|
| 1 | tenant_id | ✅ NOT NULL | ✅ 추가 | 고객사 식별 |
| 2 | environment | ✅ NOT NULL | ✅ 추가 | local/dev/staging/production |
| 3 | service_key | ✅ NOT NULL | ✅ 추가 | 서비스 식별 |
| 4 | flow_key | ✅ NOT NULL | ✅ 추가 | 업무 흐름 식별 |
| 5 | step_key | ✅ NOT NULL | ✅ 추가 | 단계 식별 |
| 6 | step_order | ✅ NOT NULL | — | 흐름 내 순서 (이벤트 전용) |
| 7 | trace_id | ✅ NOT NULL | ✅ 추가 | 단일 흐름 추적 |
| 8 | parent_trace_id | ✅ | — | 상위 흐름 연결 (이벤트 전용) |
| 9 | session_id | ✅ | — | 세션 연결 (이벤트 전용) |
| 10 | scenario_run_id | ✅ | ✅ 추가 | synthetic/regression 연결 |
| 11 | actor_type | ✅ NOT NULL | — | 행위자 유형 (이벤트 전용) |
| 12 | connector_type | ✅ NOT NULL | — | 연결 방식 (이벤트 전용) |
| 13 | event_type | ✅ NOT NULL | ✅ 기존 | 이벤트/판단 유형 |
| 14 | result (event_result) | ✅ NOT NULL | — | 행위 결과 (이벤트 전용) |
| 15 | integrity_status | — | ✅ 추가 | 무결성 판단 |
| 16 | health_status | — | ✅ 추가 | 건강 상태 판단 |
| 17 | severity | — | ✅ 기존 | 심각도 (판단 전용) |
| 18 | payload_summary | ✅ | — | 요약 데이터 (이벤트 전용) |
| 19 | payload_hash | ✅ | ✅ 기존(input_hash) | 무결성 검증 |
| 20 | timestamp | ✅ created_at | ✅ 기존 created_at | 발생 시각 |

---

## 두 테이블의 관계

```
[Service]
    │
    │ emitEvent(...)
    ▼
┌─────────────────────┐
│   business_event    │  ← Raw 행위 이벤트
│                     │     "무슨 일이 일어났는가"
│  trace_id ──────────┼──┐
│  flow_key           │  │
│  step_key           │  │
│  result             │  │
└─────────────────────┘  │
                         │  Watch Engine이 해석
                         ▼
┌─────────────────────────────────┐
│   engine_integrity_event        │  ← 판단 결과
│                                 │     "그것이 정상인가"
│  trace_id (같은 흐름 참조)       │
│  source_event_id → business_event.id │
│  integrity_status               │
│  health_status                  │
│  severity                       │
│  resolved / resolved_at / by    │
└─────────────────────────────────┘
```

**해석 예시:**

```
business_event:
  flow_key = process_registration
  step_key = db_save
  result = success
  payload_summary = {"process_type": "PRESS", "field_count": 12}

engine_integrity_event:
  flow_key = process_registration
  step_key = db_save
  event_type = field_mismatch
  integrity_status = mismatch        ← "저장은 성공했으나 값이 다르다"
  health_status = warning
  severity = WARNING
  detail = {"field": "process_type", "submitted": "PRESS", "stored": "press"}
```

→ `result = success` (행위는 성공) 이지만 `integrity_status = mismatch` (무결성은 실패)
→ 이것이 **행위 ≠ 판단** 분리의 핵심.

---

## Event Type 예시 (서비스 비종속)

### Business Event — event_type

| event_type | 설명 |
|------------|------|
| submit | 폼/요청 제출 |
| validate | 검증 실행 |
| save | DB 저장 |
| read | 조회 |
| render | 화면 렌더 |
| dispatch | 발송/전달 |
| schedule | 일정 생성 |
| timeout | 시간 초과 |
| error | 오류 발생 |
| heartbeat | 생존 신호 |

### Integrity Result — event_type

| event_type | 설명 |
|------------|------|
| payload_missing | 필수 필드 누락 |
| field_mismatch | write/read 값 불일치 |
| db_mismatch | 저장 결과 불일치 |
| stuck_detected | 흐름 중단 감지 |
| timeout_exceeded | 응답 시간 초과 |
| regression_detected | 이전 대비 결과 변경 |
| schema_drift | 스키마 변경 감지 |
| sequence_violation | step_order 순서 위반 |
| orphan_event | 흐름에 연결되지 않는 이벤트 |
| health_degraded | 서비스 건강 저하 |

---

## Enum 정의

```
-- result (Business Event)
success | failure | timeout | skipped | pending

-- integrity_status (Integrity Result)
pass | mismatch | missing | violation | drift | unknown

-- health_status (Integrity Result)
healthy | degraded | warning | critical | unknown

-- severity (Integrity Result)
INFO | WARNING | CRITICAL | FATAL

-- actor_type
user | admin | system | synthetic_user | scheduler

-- connector_type
api | browser | webhook | database | queue | scheduler

-- environment
local | dev | staging | production
```

---

## payload_summary 규칙

**허용:**
```json
{
    "required_field_exists": true,
    "process_type": "PRESS",
    "field_count": 12,
    "has_attachment": false,
    "status_code": 200,
    "row_count": 3
}
```

**금지:**
```json
{
    "user_name": "(PII)",
    "phone": "(PII)",
    "email": "(PII)",
    "full_payload": "(전체 payload 금지)",
    "request_body": "(raw body 금지)"
}
```

---

## Trace 구조

```
scenario_run_id: "regression_2026-05-15_001"
  │
  ├── trace_id: "t_login_001"
  │     step_order 0: submit (connector: browser)
  │     step_order 1: validate (connector: api)
  │     step_order 2: db_save (connector: database)
  │     step_order 3: read_result (connector: api)
  │
  ├── trace_id: "t_register_001"
  │     parent_trace_id: "t_login_001"  ← 로그인 후 등록
  │     step_order 0: open_form
  │     step_order 1: select_process_type
  │     step_order 2: submit_payload
  │     step_order 3: db_saved
  │     step_order 4: read_result
  │
  └── trace_id: "t_diagnosis_001"
        parent_trace_id: null  ← 독립 흐름
        step_order 0: input_conditions
        step_order 1: evaluate_rules
        step_order 2: generate_result
        step_order 3: read_result
```

---

## 기존 자산 매핑

| 기존 자산 | 새 구조에서의 역할 |
|-----------|-------------------|
| engine_integrity_event | **Integrity Result Store** — 필드 추가로 확장 |
| cron_job_log | **Business Event 소스** — 기존 로그를 emitEvent로 전환 |
| golden_scenario_registry | scenario_run_id의 정의 소스 |
| regression_execution_log | Integrity Result의 집계 뷰 |
| internal_api_registry | flow_key + step_key 매핑 카탈로그 |
| monitoring_config | 알림 설정 |

---

## 구현 우선순위

1. **business_event 테이블 생성** (migration)
2. **engine_integrity_event ALTER** (필드 추가)
3. **emitEvent() 공통 함수** 설계 (Thin Agent 역할)
4. **Trace/Flow Relationship 설계** (TASK 02 후속 — Architect 권장)
5. **Flow DSL에서 flow_key/step_key/step_order 정의** 연결