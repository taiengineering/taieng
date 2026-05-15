-- ============================================================
-- Watch Engine v1.1 Migration
-- Date: 2026-05-15
-- Status: REVIEW ONLY — DO NOT EXECUTE WITHOUT APPROVAL
-- ============================================================
-- Based on:
--   TASK 01 — Watch Engine Resource Mapping
--   TASK 02 — Standard Event Schema
--   TASK 02-1 — Trace / Flow Relationship Spec
--   TASK 02-2 — Flow Registry Spec
-- ============================================================
-- Principles:
--   - No DROP, no DELETE, no destructive changes
--   - CREATE TABLE IF NOT EXISTS / ADD COLUMN IF NOT EXISTS only
--   - Existing data untouched
--   - FK deferred (comments only)
--   - RLS deferred (TODO)
--   - No triggers/functions
-- ============================================================


-- ────────────────────────────────────────────────────────────
-- 1. business_event (NEW)
-- Role: Raw Business Event Store
-- ────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS business_event (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Tenant / Environment
    tenant_id       text NOT NULL,
    environment     text NOT NULL DEFAULT 'production',
    service_key     text NOT NULL,

    -- Flow position
    flow_key        text NOT NULL,
    step_key        text NOT NULL,
    step_order      smallint NOT NULL DEFAULT 0,

    -- Trace / Correlation
    trace_id        text NOT NULL,
    parent_trace_id text,
    session_id      text,
    scenario_run_id text,

    -- Actor / Connector
    actor_type      text NOT NULL DEFAULT 'system',
    connector_type  text NOT NULL DEFAULT 'api',

    -- Event body
    event_type      text NOT NULL,
    result          text NOT NULL DEFAULT 'pending',

    -- Payload (PII prohibited)
    payload_summary jsonb,
    payload_hash    text,

    -- Timestamp
    created_at      timestamptz NOT NULL DEFAULT now(),

    -- Constraints
    CONSTRAINT be_result_check
        CHECK (result IN ('success', 'failure', 'timeout', 'skipped', 'pending')),
    CONSTRAINT be_actor_check
        CHECK (actor_type IN ('user', 'admin', 'system', 'synthetic_user', 'scheduler')),
    CONSTRAINT be_connector_check
        CHECK (connector_type IN ('api', 'browser', 'webhook', 'database', 'queue', 'scheduler')),
    CONSTRAINT be_env_check
        CHECK (environment IN ('local', 'dev', 'staging', 'production'))
);

COMMENT ON TABLE business_event IS 'Watch Engine v1.1: Raw Business Event Store. PII 저장 금지.';

-- Indexes
CREATE INDEX IF NOT EXISTS idx_be_trace
    ON business_event (trace_id);
CREATE INDEX IF NOT EXISTS idx_be_flow
    ON business_event (tenant_id, flow_key, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_be_scenario
    ON business_event (scenario_run_id) WHERE scenario_run_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_be_time
    ON business_event (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_be_result
    ON business_event (result, created_at DESC) WHERE result != 'success';

-- TODO: RLS policy — tenant_id 기반 row-level security
-- TODO: Retention policy — 90일 이상 데이터 아카이빙/삭제 정책


-- ────────────────────────────────────────────────────────────
-- 2. engine_integrity_event (ALTER — extend existing)
-- Role: Integrity Result Store
-- Backward-compatible: all new columns nullable or with defaults
-- ────────────────────────────────────────────────────────────

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
    -- FK deferred: source_event_id → business_event.id
    -- Reason: avoid FK constraint on existing table with 0 rows but active schema

COMMENT ON COLUMN engine_integrity_event.tenant_id IS 'Watch Engine v1.1: 고객사 식별';
COMMENT ON COLUMN engine_integrity_event.integrity_status IS 'pass|mismatch|missing|violation|drift|unknown';
COMMENT ON COLUMN engine_integrity_event.health_status IS 'healthy|degraded|warning|critical|unknown';
COMMENT ON COLUMN engine_integrity_event.source_event_id IS 'FK → business_event.id (deferred, no constraint)';

-- Indexes
CREATE INDEX IF NOT EXISTS idx_eie_trace
    ON engine_integrity_event (trace_id) WHERE trace_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_eie_flow
    ON engine_integrity_event (flow_key, created_at DESC) WHERE flow_key IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_eie_unresolved
    ON engine_integrity_event (severity, created_at DESC) WHERE resolved = false;


-- ────────────────────────────────────────────────────────────
-- 3. flow_registry (NEW)
-- Role: "정상 flow란 무엇인가" 기준 정의
-- ────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS flow_registry (
    id                    uuid PRIMARY KEY DEFAULT gen_random_uuid(),

    tenant_id             text NOT NULL,
    environment           text NOT NULL DEFAULT 'production',
    service_key           text NOT NULL,
    flow_key              text NOT NULL,
    flow_name             text NOT NULL,
    flow_type             text NOT NULL DEFAULT 'custom',
    description           text,

    requires_parent_flow  boolean NOT NULL DEFAULT false,
    parent_flow_key       text,

    is_active             boolean NOT NULL DEFAULT true,
    expected_duration_ms  integer,
    stuck_threshold_ms    integer,

    created_at            timestamptz NOT NULL DEFAULT now(),
    updated_at            timestamptz NOT NULL DEFAULT now(),

    -- Constraints
    CONSTRAINT fr_env_check
        CHECK (environment IN ('local', 'dev', 'staging', 'production')),
    CONSTRAINT fr_type_check
        CHECK (flow_type IN ('auth', 'billing', 'registration', 'diagnosis',
                             'scheduler', 'admin', 'external_api', 'custom')),

    CONSTRAINT uq_flow_registry
        UNIQUE (tenant_id, environment, service_key, flow_key)
);

COMMENT ON TABLE flow_registry IS 'Watch Engine v1.1: 업무 flow 기본 정의. TAI 전용 아님, 범용 SaaS 구조.';

-- TODO: RLS policy


-- ────────────────────────────────────────────────────────────
-- 4. flow_step_registry (NEW)
-- Role: Flow 내 step 정의
-- ────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS flow_step_registry (
    id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),

    tenant_id         text NOT NULL,
    environment       text NOT NULL DEFAULT 'production',
    service_key       text NOT NULL,
    flow_key          text NOT NULL,
    step_key          text NOT NULL,
    step_order        smallint NOT NULL,
    step_name         text NOT NULL,

    connector_type    text NOT NULL DEFAULT 'api',
    is_required       boolean NOT NULL DEFAULT true,
    is_optional       boolean NOT NULL DEFAULT false,
    is_retryable      boolean NOT NULL DEFAULT false,
    max_retry_count   integer NOT NULL DEFAULT 0,
    timeout_ms        integer,
    expected_result   text DEFAULT 'success',

    payload_schema    jsonb,
    validation_rule   jsonb,

    created_at        timestamptz NOT NULL DEFAULT now(),
    updated_at        timestamptz NOT NULL DEFAULT now(),

    -- Constraints
    CONSTRAINT fsr_env_check
        CHECK (environment IN ('local', 'dev', 'staging', 'production')),
    CONSTRAINT fsr_connector_check
        CHECK (connector_type IN ('api', 'browser', 'webhook', 'database', 'queue', 'scheduler')),

    CONSTRAINT uq_flow_step_registry
        UNIQUE (tenant_id, environment, service_key, flow_key, step_key)
);

COMMENT ON TABLE flow_step_registry IS 'Watch Engine v1.1: flow 내 step 정의. step_order 0-based 연속은 application validation.';

-- Step order lookup index
CREATE INDEX IF NOT EXISTS idx_fsr_order
    ON flow_step_registry (tenant_id, environment, service_key, flow_key, step_order);

-- TODO: RLS policy


-- ────────────────────────────────────────────────────────────
-- 5. flow_integrity_rule_registry (NEW)
-- Role: Step 간 비교/무결성 규칙 정의
-- ────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS flow_integrity_rule_registry (
    id                       uuid PRIMARY KEY DEFAULT gen_random_uuid(),

    tenant_id                text NOT NULL,
    environment              text NOT NULL DEFAULT 'production',
    service_key              text NOT NULL,
    flow_key                 text NOT NULL,
    rule_key                 text NOT NULL,

    rule_type                text NOT NULL,
    source_step_key          text,
    target_step_key          text,
    source_field_path        text,
    target_field_path        text,
    operator                 text NOT NULL,

    evaluation_timing        text NOT NULL DEFAULT 'on_flow_complete',

    severity_on_fail         text NOT NULL DEFAULT 'WARNING',
    integrity_status_on_fail text NOT NULL DEFAULT 'violation',
    health_status_on_fail    text NOT NULL DEFAULT 'warning',

    description              text,
    is_active                boolean NOT NULL DEFAULT true,

    created_at               timestamptz NOT NULL DEFAULT now(),
    updated_at               timestamptz NOT NULL DEFAULT now(),

    -- Constraints
    CONSTRAINT firr_env_check
        CHECK (environment IN ('local', 'dev', 'staging', 'production')),
    CONSTRAINT firr_rule_type_check
        CHECK (rule_type IN ('required_field', 'field_match', 'db_match',
                             'sequence', 'timeout', 'stuck', 'regression',
                             'schema_drift', 'orphan')),
    CONSTRAINT firr_operator_check
        CHECK (operator IN ('exists', 'equals', 'not_equals', 'contains',
                            'greater_than', 'less_than', 'hash_equals',
                            'in', 'not_in')),
    CONSTRAINT firr_timing_check
        CHECK (evaluation_timing IN ('on_event', 'on_flow_complete',
                                     'on_schedule', 'on_scenario_complete')),
    CONSTRAINT firr_severity_check
        CHECK (severity_on_fail IN ('INFO', 'WARNING', 'CRITICAL', 'FATAL')),

    CONSTRAINT uq_flow_integrity_rule
        UNIQUE (tenant_id, environment, service_key, flow_key, rule_key)
);

COMMENT ON TABLE flow_integrity_rule_registry IS 'Watch Engine v1.1: step 간 비교/무결성 규칙. 범용 SaaS 구조.';

-- TODO: RLS policy


-- ────────────────────────────────────────────────────────────
-- 6. flow_scenario_binding (NEW)
-- Role: golden_scenario_registry ↔ flow_registry 연결
-- ────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS flow_scenario_binding (
    id                    uuid PRIMARY KEY DEFAULT gen_random_uuid(),

    tenant_id             text NOT NULL,
    environment           text NOT NULL DEFAULT 'production',
    service_key           text NOT NULL,

    scenario_code         text NOT NULL,
    flow_key              text NOT NULL,
    execution_order       smallint NOT NULL DEFAULT 0,

    is_active             boolean NOT NULL DEFAULT true,
    expected_trace_count  integer,
    expected_result_rule  jsonb,

    created_at            timestamptz NOT NULL DEFAULT now(),
    updated_at            timestamptz NOT NULL DEFAULT now(),

    -- Constraints
    CONSTRAINT fsb_env_check
        CHECK (environment IN ('local', 'dev', 'staging', 'production')),

    CONSTRAINT uq_flow_scenario_binding
        UNIQUE (tenant_id, environment, service_key, scenario_code, flow_key)
);

COMMENT ON TABLE flow_scenario_binding IS 'Watch Engine v1.1: golden_scenario_registry ↔ flow_registry M:N 연결.';

-- TODO: RLS policy


-- ============================================================
-- Deferred items (DO NOT implement in this migration)
-- ============================================================
-- FK: business_event (flow_key) → flow_registry (flow_key) — deferred
-- FK: business_event (flow_key, step_key) → flow_step_registry — deferred
-- FK: engine_integrity_event.source_event_id → business_event.id — deferred
-- FK: flow_step_registry (flow_key) → flow_registry (flow_key) — deferred
-- FK: flow_integrity_rule_registry (flow_key) → flow_registry — deferred
-- FK: flow_scenario_binding (scenario_code) → golden_scenario_registry — deferred
-- FK: flow_scenario_binding (flow_key) → flow_registry — deferred
--
-- RLS: All 5 new tables need tenant_id based RLS policies
-- Triggers: updated_at auto-update trigger (standard moddatetime)
-- Retention: business_event 90-day archival policy
-- ============================================================