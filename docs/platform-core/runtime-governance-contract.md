# Runtime Governance Contract v1.0

Standard governance policies for runtime objects.

## RuntimeGovernanceContract

```
governance_level: passive | standard | strict | critical
escalation:
  enabled: bool
  threshold_hours: int
  target: user | team | facility_manager
retry:
  enabled: bool
  max_retries: int
  backoff: linear | exponential
digest:
  enabled: bool
  frequency: daily | weekly
  channel: email | sms | in_app
throttling:
  enabled: bool
  max_per_hour: int
storm_protection:
  enabled: bool
  threshold: int
  window_minutes: int
replay:
  enabled: bool
  retention_days: int
integrity:
  validation_mode: lenient | strict
  hash_verification: bool
```

## governance_level Defaults

| level | escalation | retry | digest | storm | integrity |
|-------|-----------|-------|--------|-------|-----------|
| passive | ❌ | ❌ | ✅ daily | ❌ | lenient |
| standard | ✅ 48h | ✅ 3x | ✅ daily | ❌ | lenient |
| strict | ✅ 24h | ✅ 5x | ✅ daily | ✅ | strict |
| critical | ✅ 4h | ✅ 10x | ✅ hourly | ✅ | strict+hash |

## Rules

1. Every runtime_task inherits governance from its candidate
2. Governance MUST NOT modify task state directly
3. Governance actions go through EventEnvelope
4. Watch Engine is the sole consumer of governance policies
5. Escalation targets MUST respect tenant boundary
