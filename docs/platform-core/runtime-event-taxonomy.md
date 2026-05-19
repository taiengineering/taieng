# Runtime Event Taxonomy v1.0

Canonical event registry for all runtime events.
All events MUST use EventEnvelope with tenant_id + trace_id.

## Event Naming: `<namespace>.<action>`

## Candidate Events

| event_type | source | payload |
|-----------|--------|--------|
| runtime.candidate_projected | binding_engine | candidate_id, candidate_type, title |
| runtime.candidate_approved | binding_engine | candidate_id |
| runtime.candidate_rejected | binding_engine | candidate_id, reason |
| runtime.candidate_activated | binding_engine | candidate_id, task_id, title |

## Runtime Lifecycle Events

| event_type | source | payload |
|-----------|--------|--------|
| runtime.task_created | activation_service | task_id, task_type, title |
| runtime.task_assigned | runtime | task_id, assignee_id |
| runtime.task_started | runtime | task_id |
| runtime.task_completed | runtime | task_id, completed_by |
| runtime.schedule_created | activation_service | schedule_id, task_id |
| runtime.schedule_overdue | runtime | schedule_id, task_id, overdue_since |

## Governance Events

| event_type | source | payload |
|-----------|--------|--------|
| watch.escalation_triggered | watch_engine | task_id, escalation_level |
| watch.runtime_recovered | watch_engine | task_id, recovery_action |
| watch.storm_detected | watch_engine | tenant_id, event_count |
| watch.digest_generated | watch_engine | tenant_id, digest_type |

## Recovery Events

| event_type | source | payload |
|-----------|--------|--------|
| recovery.retry_scheduled | recovery_engine | original_event_id |
| recovery.retry_succeeded | recovery_engine | original_event_id |
| recovery.retry_exhausted | recovery_engine | original_event_id, max_retries |

## Capability Events

| event_type | source | payload |
|-----------|--------|--------|
| capability.enabled | platform | tenant_id, capability_name |
| capability.disabled | platform | tenant_id, capability_name |

## Rules

1. All events MUST include tenant_id + trace_id
2. event_type format: `<namespace>.<action>` (dot-separated)
3. payload MUST NOT contain engine-internal state
4. idempotency_key SHOULD be set for state-changing events
