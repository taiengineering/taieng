# 45 AI Runtime

## Purpose

All engines in 45cm must use a centralized AI Runtime instead of calling LLM providers directly.

The AI Runtime is responsible for:

- LLM cost control
- Token usage tracking
- Workspace-level AI budget enforcement
- Capability-based model routing
- Prompt quality management
- Audit logging
- Provider abstraction

---

## Core Principle

```text
Engines do not know models.
Engines request capabilities.
AI Runtime controls models, costs, prompts, routing, and limits.
```

Example:

```ts
ai.generate({
  workspaceId,
  engine: "marketing",
  capability: "draft_reply",
  input,
  context
})
```

---

## Runtime Structure

```text
Marketing Engine
Watch Engine
Workflow Engine
TAI Engine
        ↓
  45 AI Runtime
        ↓
Provider Adapters
        ↓
OpenAI / Claude / Gemini / Local Models
```

---

## Modules

```text
packages/core-ai-runtime/
 ├─ gateway/
 ├─ metering/
 ├─ budgeting/
 ├─ routing/
 ├─ prompt-registry/
 ├─ provider-adapter/
 ├─ policy/
 ├─ audit-log/
 └─ types/
```

---

## Gateway Responsibilities

- Validate requests
- Resolve workspace policy
- Check AI budget
- Route models
- Build prompts
- Execute provider requests
- Record usage logs
- Handle retries/fallbacks

---

## Metering

Track:

- workspace_id
- engine
- capability
- model
- token usage
- estimated cost
- request status
- execution time

---

## Budgeting

Support:

- Monthly AI budget
- Daily AI limits
- Capability-specific restrictions
- Automatic downgrade policies
- Budget alerts
- Hard-stop limits

---

## Routing

Capability-based routing.

Examples:

| Capability | Routing |
|---|---|
| draft_reply | low-cost model |
| rewrite_humanize | medium model |
| legal_analysis | high-quality model |
| summary | low-cost model |

---

## Prompt Registry

Prompts must not be hardcoded inside engine logic.

Registry fields:

- prompt_key
- version
- engine
- capability
- template
- status

---

## Policies

Examples:

- Draft limit per day
- Workspace AI budget limit
- Paid-only deep analysis
- Humanization requirement before publish
- High-risk content restrictions

---

## DB Schemas

```text
core_ai.ai_usage_log
core_ai.ai_budget
core_ai.ai_model_policy
core_ai.prompt_registry
core_ai.ai_call_audit
```

---

## Important Runtime Rules

```text
1. Engines must never directly call OpenAI APIs.
2. AI usage must always be logged.
3. Prompts must be versioned.
4. AI usage must be workspace scoped.
5. Model names should not be exposed to end users.
6. Unlimited AI plans are prohibited.
```
