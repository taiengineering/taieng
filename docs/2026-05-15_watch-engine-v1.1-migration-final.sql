-- ============================================================
-- Watch Engine v1.1 Migration (FINAL)
-- Date: 2026-05-15
-- Version: v1.1-final
-- Status: REVIEW ONLY — DO NOT EXECUTE WITHOUT APPROVAL
-- ============================================================
-- Changes from draft:
--   [FIX-1] flow_step_registry: is_optional 제거, is_required만 유지
--   [FIX-2] flow_registry: requires_parent_flow 제거, parent_flow_key만 유지
--   [FIX-3] engine_integrity_event ALTER: 개별 ALTER 문으로 분리
--   [CHECK] constraint/index/unique 이름 충돌 검증 완료
-- ============================================================


-- 1. business_event (NEW)

CREATE TABLE IF NOT EXISTS business_event (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       text NOT NULL,
    environment     text NOT NULL DEFAULT 'production',
    service_key     text NOT NULL,
    flow_key        text NOT NULL,
    step_key        text NOT NULL,
    step_order      smallint NOT NULL DEFAULT 0,
    trace_id        text NOT NULL,
    parent_trace_id text,
    session_id      text,
    scenario_run_id text,
    actor_type      text NOT NULL DEFAULT 'system',
    connector_type  text NOT NULL DEFAULT 'api',
    event_type      text NOT NULL,
    result          text NOT NULL DEFAULT 'pending',
    payload_summary jsonb,
    payload_hash    text,
    created_at      timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT be_result_chk
        CHECK (result IN ('success','failure','timeout','skipped','pending')),
    CONSTRAINT be_actor_chk
        CHECK (actor_type IN ('user','admin','system','synthetic_user','scheduler')),
    CONSTRAINT be_connector_chk
        CHECK (connector_type IN ('api','browser','webhook','database','queue','scheduler')),
    CONSTRAINT be_env_chk
        CHECK (environment IN ('local','dev','staging','production'))
);

COMMENT ON TABLE business_event IS 'Watch Engine v1.1: Raw Business Event Store. PII 저장 금지.';

CREATE INDEX IF NOT EXISTS idx_be_trace ON business_event (trace_id);
CREATE INDEX IF NOT EXISTS idx_be_flow ON business_event (tenant_id, flow_key, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_be_scenario ON business_event (scenario_run_id) WHERE scenario_run_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_be_time ON business_event (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_be_result_fail ON business_event (result, created_at DESC) WHERE result != 'success';


-- 2. engine_integrity_event (ALTER)

ALTER TABLE engine_integrity_event ADD COLUMN IF NOT EXISTS tenant_id text;
ALTER TABLE engine_integrity_event ADD COLUMN IF NOT EXISTS environment text DEFAULT 'production';
ALTER TABLE engine_integrity_event ADD COLUMN IF NOT EXISTS service_key text;
ALTER TABLE engine_integrity_event ADD COLUMN IF NOT EXISTS flow_key text;
ALTER TABLE engine_integrity_event ADD COLUMN IF NOT EXISTS step_key text;
ALTER TABLE engine_integrity_event ADD COLUMN IF NOT EXISTS trace_id text;
ALTER TABLE engine_integrity_event ADD COLUMN IF NOT EXISTS scenario_run_id text;
ALTER TABLE engine_integrity_event ADD COLUMN IF NOT EXISTS integrity_status text DEFAULT 'unknown';
ALTER TABLE engine_integrity_event ADD COLUMN IF NOT EXISTS health_status text DEFAULT 'unknown';
ALTER TABLE engine_integrity_event ADD COLUMN IF NOT EXISTS source_event_id uuid;

COMMENT ON COLUMN engine_integrity_event.integrity_status IS 'pass|mismatch|missing|violation|drift|unknown';
COMMENT ON COLUMN engine_integrity_event.health_status IS 'healthy|degraded|warning|critical|unknown';
COMMENT ON COLUMN engine_integrity_event.source_event_id IS 'FK deferred → business_event.id';

CREATE INDEX IF NOT EXISTS idx_eie_trace ON engine_integrity_event (trace_id) WHERE trace_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_eie_flow ON engine_integrity_event (flow_key, created_at DESC) WHERE flow_key IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_eie_unresolved ON engine_integrity_event (severity, created_at DESC) WHERE resolved = false;


-- 3. flow_registry (NEW)

CREATE TABLE IF NOT EXISTS flow_registry (
    id                    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id             text NOT NULL,
    environment           text NOT NULL DEFAULT 'production',
    service_key           text NOT NULL,
    flow_key              text NOT NULL,
    flow_name             text NOT NULL,
    flow_type             text NOT NULL DEFAULT 'custom',
    description           text,
    parent_flow_key       text,
    is_active             boolean NOT NULL DEFAULT true,
    expected_duration_ms  integer,
    stuck_threshold_ms    integer,
    created_at            timestamptz NOT NULL DEFAULT now(),
    updated_at            timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT fr_env_chk CHECK (environment IN ('local','dev','staging','production')),
    CONSTRAINT fr_type_chk CHECK (flow_type IN ('auth','billing','registration','diagnosis','scheduler','admin','external_api','custom')),
    CONSTRAINT uq_fr_flow UNIQUE (tenant_id, environment, service_key, flow_key)
);

COMMENT ON TABLE flow_registry IS 'Watch Engine v1.1: flow 정의. parent_flow_key null=독립, 값=선행필요.';


-- 4. flow_step_registry (NEW)

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
    is_retryable      boolean NOT NULL DEFAULT false,
    max_retry_count   integer NOT NULL DEFAULT 0,
    timeout_ms        integer,
    expected_result   text DEFAULT 'success',
    payload_schema    jsonb,
    validation_rule   jsonb,
    created_at        timestamptz NOT NULL DEFAULT now(),
    updated_at        timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT fsr_env_chk CHECK (environment IN ('local','dev','staging','production')),
    CONSTRAINT fsr_connector_chk CHECK (connector_type IN ('api','browser','webhook','database','queue','scheduler')),
    CONSTRAINT uq_fsr_step UNIQUE (tenant_id, environment, service_key, flow_key, step_key)
);

COMMENT ON TABLE flow_step_registry IS 'Watch Engine v1.1: step 정의. is_required true=필수 false=optional.';

CREATE INDEX IF NOT EXISTS idx_fsr_order ON flow_step_registry (tenant_id, environment, service_key, flow_key, step_order);


-- 5. flow_integrity_rule_registry (NEW)

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
    CONSTRAINT firr_env_chk CHECK (environment IN ('local','dev','staging','production')),
    CONSTRAINT firr_rule_type_chk CHECK (rule_type IN ('required_field','field_match','db_match','sequence','timeout','stuck','regression','schema_drift','orphan')),
    CONSTRAINT firr_operator_chk CHECK (operator IN ('exists','equals','not_equals','contains','greater_than','less_than','hash_equals','in','not_in')),
    CONSTRAINT firr_timing_chk CHECK (evaluation_timing IN ('on_event','on_flow_complete','on_schedule','on_scenario_complete')),
    CONSTRAINT firr_severity_chk CHECK (severity_on_fail IN ('INFO','WARNING','CRITICAL','FATAL')),
    CONSTRAINT uq_firr_rule UNIQUE (tenant_id, environment, service_key, flow_key, rule_key)
);

COMMENT ON TABLE flow_integrity_rule_registry IS 'Watch Engine v1.1: 무결성 규칙. 범용 SaaS.';


-- 6. flow_scenario_binding (NEW)

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
    CONSTRAINT fsb_env_chk CHECK (environment IN ('local','dev','staging','production')),
    CONSTRAINT uq_fsb_binding UNIQUE (tenant_id, environment, service_key, scenario_code, flow_key)
);

COMMENT ON TABLE flow_scenario_binding IS 'Watch Engine v1.1: golden_scenario ↔ flow M:N.';


-- Deferred: FK 7건, RLS 6건, moddatetime trigger, retention policy