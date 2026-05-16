# RFC-009 Policy Runtime

## Purpose

Policy Runtime controls operational boundaries.

Automation must always be policy-driven.

---

## Principle

```text
AI can recommend.
Policy decides.
Humans control.
```

---

## Policy Scope

Policies may control:

```text
publish rules
approval requirements
AI limits
channel restrictions
rate limits
risk thresholds
cooldown rules
workspace permissions
```

---

## Example Policies

```yaml
publish_policy:
  linkedin_post:
    requires_approval: true

  facebook_reply:
    requires_approval: false

risk_policy:
  high_risk_keyword:
    force_human_review: true

ai_policy:
  daily_ai_credit_limit: 100
```

---

## Runtime Responsibilities

Policy Runtime evaluates:

```text
- can execute?
- requires approval?
- allowed channel?
- AI budget exceeded?
- cooldown active?
```

---

## Policy Hierarchy

Recommended order:

```text
Platform Policy
→ Tenant Policy
→ Workspace Policy
→ Channel Policy
→ Capability Policy
```

---

## Important Principle

```text
Policy Runtime is not business logic.
It is operational boundary control.
```

---

## Prohibitions

```text
1. No hardcoded policy logic inside workers.
2. No publish execution without policy evaluation.
3. No AI execution without budget policy check.
4. No provider-specific rules in core policy layer.
```
