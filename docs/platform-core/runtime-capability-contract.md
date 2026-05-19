# Runtime Capability Contract v1.0

Tenant-level feature flags for runtime behaviors.

## RuntimeCapabilityContract

```json
{
  "runtime_overdue": true,
  "runtime_candidate_projection": true,
  "runtime_activation": true,
  "advanced_governance": false,
  "cross_runtime_monitoring": false,
  "digest": true,
  "auto_escalation": false,
  "document_generation": true,
  "evidence_collection": true,
  "schedule_management": true,
  "notification_dispatch": true,
  "api_access": false,
  "multi_facility": true
}
```

## Capability Tiers

| capability | Free | Standard | Premium |
|-----------|------|----------|--------|
| runtime_overdue | ✅ | ✅ | ✅ |
| runtime_candidate_projection | ✅ | ✅ | ✅ |
| runtime_activation | ✅ | ✅ | ✅ |
| advanced_governance | ❌ | ❌ | ✅ |
| cross_runtime_monitoring | ❌ | ✅ | ✅ |
| digest | ❌ | ✅ | ✅ |
| auto_escalation | ❌ | ❌ | ✅ |
| document_generation | ✅ | ✅ | ✅ |
| evidence_collection | ✅ | ✅ | ✅ |
| schedule_management | ✅ | ✅ | ✅ |
| notification_dispatch | ❌ | ✅ | ✅ |
| api_access | ❌ | ❌ | ✅ |
| multi_facility | ❌ | ✅ | ✅ |

## Usage

1. Binding Engine checks capabilities before projection
2. Activation Service checks capabilities before creating runtime objects
3. Watch Engine checks capabilities before governance actions
4. Capability state stored in tenant settings (companies table)
