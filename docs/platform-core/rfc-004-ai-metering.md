# RFC-004 AI Metering

## Purpose

AI usage is a platform resource.

All AI activity must be measurable.

---

## Principle

```text
No AI execution without usage tracking.
```

---

## Metering Scope

Track:

```text
workspace
engine
capability
provider
model
prompt tokens
completion tokens
estimated cost
latency
status
```

---

## Budget Model

Recommended:

```text
Workspace Budget
+
AI Credits
```

---

## Runtime Protections

Support:

```text
- daily limit
- monthly budget
- capability restrictions
- model downgrade
- budget alerts
- emergency stop
```

---

## Capability Cost Awareness

Example:

| Capability | Cost Level |
|---|---|
| draft_reply | low |
| summarize | low |
| rewrite_humanize | medium |
| legal_analysis | high |
| keyword_cluster | high |

---

## AI Gateway Requirement

All engines must use:

```text
45 AI Runtime Gateway
```

Direct provider calls are prohibited.

---

## User Experience

Users should not see token terminology.

Expose:

```text
AI Usage
AI Credits
AI Budget
Remaining AI Capacity
```

---

## Prohibitions

```text
1. No untracked AI usage.
2. No unlimited AI plans.
3. No direct provider exposure to end users.
4. No engine-level provider lock-in.
```
