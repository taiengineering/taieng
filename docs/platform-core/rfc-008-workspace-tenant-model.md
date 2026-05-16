# RFC-008 Workspace and Tenant Model

## Purpose

Define ownership, isolation, and billing boundaries.

---

## Principle

```text
Workspace is the operational boundary.
Tenant is the platform isolation boundary.
```

---

## Workspace

Represents:

```text
- company
- team
- agency customer
- operating organization
```

Workspace owns:

```text
channels
keywords
drafts
approvals
leads
analytics
AI budget
```

---

## Tenant

Tenant isolates platform runtime.

Future use cases:

```text
multi-region
enterprise isolation
dedicated infrastructure
white-label SaaS
```

Initial phase may use:

```text
single tenant
multiple workspaces
```

---

## Billing Boundary

Recommended billing:

```text
workspace
+ seats
+ customer accounts
+ channels
+ AI credits
```

---

## Agency Model

Marketing agencies may manage multiple customer workspaces.

Recommended structure:

```text
Agency Workspace
 ├─ Customer Workspace A
 ├─ Customer Workspace B
 └─ Customer Workspace C
```

---

## Ownership Rules

```text
Workspace owns operational data.
Core Runtime owns platform contracts.
```

---

## Isolation Rules

```text
1. Workspace data must not leak.
2. AI budget must be workspace scoped.
3. Queue jobs must include workspace_id.
4. Event envelopes must include workspace_id.
```

---

## Prohibitions

```text
1. No shared mutable customer data across workspaces.
2. No AI usage without workspace attribution.
3. No workspace-less publish execution.
```
