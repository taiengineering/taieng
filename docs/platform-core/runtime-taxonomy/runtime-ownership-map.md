# Runtime Ownership Map

---

## Runtime 별 Ownership

| Runtime | Ownership | \uc18c\uc720 \ub370\uc774\ud130 |
|---------|-----------|------------|
| **Control** | Operational Truth | engine_integrity_event, incident_action_log, incident_pattern_registry, alert_rule_registry, alert_history, workflow_recovery_registry, operational_playbook_registry |
| **Governance** | Tenant Impact | tenant_operational_registry, workflow_risk_registry, workflow_sla_registry |
| **Knowledge** | Historical Intelligence | incident_pattern_registry (\uc77d\uae30), stability \uacc4\uc0b0 |
| **Notification** | Communication Projection | message_template_registry, notification_routing_registry |
| **Delivery** | Transport Execution | (\uc678\ubd80: Telegram API, SMS API) |
| **Workflow** | Business Process | business_event, flow_registry, flow_step_registry |
| **Semantic** | Meaning Translation | legacy_state_mapping |
| **Scheduler** | Job Execution | cron_job_master, cron_schedule_config, cron_job_log |
| **UI** | Projection Surface | (\uc18c\uc720 \ub370\uc774\ud130 \uc5c6\uc74c \u2014 \ud45c\uc2dc\ub9cc) |

## Contract \uad00\uacc4

| Runtime | \uc0ac\uc6a9 Contract |
|---------|----------------|
| Control | Operational Event Contract (`control-event-contract.md`) |
| Notification | Projection Contract (audience + routing + template) |
| Delivery | Delivery Contract (transport + retry + timeout) |
| Workflow | Workflow Contract (event emission + state transition) |
| Semantic | Translation Contract (legacy \u2192 canonical mapping) |
| Scheduler | Cron Contract (DIRECT handler + HTTP handler) |
| Platform Core | Event Envelope + Runtime Contract |

## Merge \ubd84\uc11d

| \ud6c4\ubcf4 | \ud310\uc815 | \uc774\uc720 |
|------|:---:|------|
| Feed Runtime | ❌ \ubd88\ud544\uc694 | Notification Projection\uc73c\ub85c \ucda9\ubd84 |
| Timeline Runtime | ❌ \ubd88\ud544\uc694 | UI \ub0b4\ubd80 \ucee8\ud3ec\ub10c\ud2b8 |
| Queue Runtime | ❌ \ubd88\ud544\uc694 | Delivery \ub0b4\ubd80 \uad6c\ud604 |
| Policy Runtime | ❌ \ubd88\ud544\uc694 | Knowledge\uc5d0 \ud3ec\ud568 |
| Orchestration | ❌ \ubd88\ud544\uc694 | Workflow\uacfc \ub3d9\uc77c |
| Dashboard | ❌ \ubd88\ud544\uc694 | UI\uc640 \ub3d9\uc77c |
| Contract Runtime | ❌ \ubd88\ud544\uc694 | Platform Core\uc5d0 \ud3ec\ud568 |
| Governance | ✅ Control \ud558\uc704 | \ub3c5\ub9bd \ubd84\ub9ac \ubd88\ud544\uc694 |
| Knowledge | ✅ Control \ud558\uc704 | \ub3c5\ub9bd \ubd84\ub9ac \ubd88\ud544\uc694 |

**\uacb0\ub860: 7\uac1c \ud6c4\ubcf4 Runtime \uc804\ubd80 \ubd88\ud544\uc694. \ud604\uc7ac 8\uac1c \ub3c5\ub9bd Runtime\uc774 \ucd5c\uc801.**

## Runtime Evolution \ubc29\ud5a5

1. **Runtime \uc218 \uc99d\uac00\ubcf4\ub2e4 Ownership \uac15\ud654**
2. **\uc2e0\uaddc Runtime \uc0dd\uc131 \uc804 Merge \uac00\ub2a5\uc131 \uac80\ud1a0 \ud544\uc218**
3. **\ub3c5\ub9bd Runtime \ucd5c\ub300 10\uac1c \uc81c\ud55c**
4. **\ubaa8\ub4e0 Runtime\uc740 Platform Core Contract \uc900\uc218**
5. **Truth Runtime \u2192 Projection/Execution \ubc29\ud5a5\ub9cc \ud5c8\uc6a9**
