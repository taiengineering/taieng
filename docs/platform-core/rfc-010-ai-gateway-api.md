# RFC-010 AI Gateway API

## Purpose

Define the standard API contract for 45 AI Runtime.

---

## Principle

```text
Engines request capabilities.
AI Runtime handles providers.
```

---

## Generate API

```ts
interface GenerateRequest {
  workspaceId: string

  engine: string
  capability: string

  promptKey?: string
  promptVersion?: number

  input: unknown
  context?: unknown

  priority?: "P1" | "P2" | "P3" | "P4"

  metadata?: Record<string, unknown>
}
```

---

## Generate Response

```ts
interface GenerateResponse {
  requestId: string

  provider: string
  model: string

  output: unknown

  usage: {
    promptTokens: number
    completionTokens: number
    totalTokens: number
    estimatedCost: number
  }

  latencyMs: number

  status: "success" | "fallback" | "failed"
}
```

---

## Runtime Responsibilities

AI Runtime handles:

```text
model routing
provider selection
budget validation
usage logging
retry
fallback
prompt resolution
```

---

## Prompt Resolution

Recommended:

```text
promptKey + version
```

instead of raw prompt templates from engines.

---

## Fallback Strategy

Recommended:

```text
primary model
→ fallback model
→ queue retry
→ failure event
```

---

## Important Principles

```text
1. Engines must not know provider internals.
2. Engines must not hardcode model names.
3. AI Runtime owns AI observability.
4. All requests must be workspace-scoped.
```

---

## Prohibitions

```text
1. No direct OpenAI SDK usage inside engines.
2. No unmetered AI generation.
3. No provider-specific payloads in engine runtime.
```
