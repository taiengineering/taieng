# Runtime Sovereignty — Enforcement Layer

## 목적

TASK 32에서 선언한 Runtime Boundary를 실제 코드 수준에서 강제.

---

## 구조

```
watch_engine/runtime_sovereignty/
├── __init__.py              # 패키지 export
├── capability_registry.py   # Runtime별 허용/금지 등록부
├── truth_enforcer.py        # 권한 검증 + violation 로깅
└── runtime_permission.py    # RuntimeContext + decorator
```

## Capability Registry

### 허용 (CAPABILITY_REGISTRY)

| Runtime | 허용 Action |
|---------|-------------|
| **control** | create_incident, set_severity, escalate_incident, resolve_incident, close_incident, set_ack, complete_ack, set_recovery, close_recovery, set_operational_status, set_degradation, set_suppression, detect_anomaly, detect_pattern, compute_stability, compute_tenant_impact, set_workflow_blockage, create_alert, evaluate_integrity, detect_repeated, evaluate_sla |
| **notification** | create_projection, map_audience, apply_digest, apply_quiet_hour, apply_fatigue_reduction, apply_cooldown, route_notification, log_delivery |
| **delivery** | enqueue, retry_delivery, execute_transport, timeout_delivery, log_delivery_audit, select_provider |
| **workflow** | execute_workflow, execute_step, emit_event, transition_state, activate_document |
| **ui** | request_ack, request_resolve, request_ignore, request_escalate, request_retry, render_projection, filter_sort |
| **adapter** | translate_state, translate_record, invalidate_cache |

### 금지 (FORBIDDEN_REGISTRY)

| Runtime | 금지 Action |
|---------|-------------|
| notification | create_incident, set_severity, escalate_incident, resolve_incident, close_incident, set_ack, complete_ack, set_recovery, close_recovery, set_operational_status, set_degradation, set_suppression, detect_anomaly, set_workflow_blockage |
| delivery | create_incident, set_severity, escalate_incident, resolve_incident, set_ack, set_suppression, map_audience |
| workflow | create_incident, set_severity, escalate_incident, resolve_incident, set_ack, complete_ack, set_recovery, set_operational_status, set_degradation |
| ui | create_incident, set_severity, escalate_incident, resolve_incident, close_incident, set_ack, complete_ack, set_recovery, set_operational_status, set_suppression |
| adapter | create_incident, set_severity, escalate_incident, resolve_incident, set_ack, set_operational_status |

## 사용법

### 1. 직접 검증
```python
from watch_engine.runtime_sovereignty import enforce

# \ud5c8\uc6a9\ub428
enforce(runtime="control", action="create_incident")

# \ucc28\ub2e8\ub428 \u2192 RuntimeCapabilityViolation
enforce(runtime="notification", action="create_incident")

# \uc608\uc678 \uc5c6\uc774 False \ubc18\ud658
result = enforce(runtime="notification", action="create_incident", raise_on_violation=False)
```

### 2. Decorator
```python
from watch_engine.runtime_sovereignty import with_runtime_context

@with_runtime_context("control", "create_incident")
def create_incident(tenant_id, trace_id, ...):
    # \uc774 \ud568\uc218\ub294 control runtime\ub9cc \ud638\ucd9c \uac00\ub2a5
    ...
```

### 3. RuntimeContext
```python
from watch_engine.runtime_sovereignty import RuntimeContext, CONTROL_CONTEXT

ctx = RuntimeContext(runtime="control", tenant_id="tai", trace_id="abc")
# ctx.capabilities = {"create_incident", "set_severity", ...}
```

## Violation \ucc98\ub9ac

1. `logger.warning` \ub85c\uae45
2. `engine_integrity_event` \ud14c\uc774\ube14\uc5d0 `runtime_capability_violation` \uc774\ubca4\ud2b8 \uae30\ub85d (severity=CRITICAL)
3. `raise_on_violation=True`\uc774\uba74 `RuntimeCapabilityViolation` \uc608\uc678

## \uc810\uc9c4\uc801 \uc801\uc6a9 \ubc29\ud5a5

\ud604\uc7ac\ub294 Guard Layer\ub85c \ucd94\uac00. \uae30\uc874 \ucf54\ub4dc \ubbf8\ubcc0\uacbd.
\ud5a5\ud6c4 \ud575\uc2ec \ud568\uc218\uc5d0 `@with_runtime_context` decorator \uc801\uc6a9:

1. evaluator.py \u2192 `@with_runtime_context("control", "evaluate_integrity")`
2. repeated.py \u2192 `@with_runtime_context("control", "detect_repeated")`
3. governance/__init__.py \u2192 `@with_runtime_context("control", "compute_tenant_impact")`
4. stability.py \u2192 `@with_runtime_context("control", "compute_stability")`
