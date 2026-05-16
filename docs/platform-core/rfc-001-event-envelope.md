# RFC-001 Event Envelope

## Purpose

All engines in 45cm must emit and consume events using a shared Event Envelope.

This prevents event chaos as engines increase.

---

## Principle

```text
Events are records of operational facts.
Events are not commands.
Events do not decide business logic by themselves.
```

---

## Event Envelope

```ts
interface PlatformEvent<TPayload = unknown, TContext = unknown> {
  event_id: string
  event_type: string
  event_version: number

  workspace_id: string
  tenant_id?: string

  engine: string
  source: string
  capability?: string

  trace_id?: string
  correlation_id?: string
  causation_id?: string

  priority: "P1" | "P2" | "P3" | "P4"
  severity?: "INFO" | "WARNING" | "CRITICAL"

  status: "created" | "queued" | "processing" | "completed" | "failed" | "ignored"

  payload: TPayload
  context?: TContext

  created_at: string
  updated_at?: string
}
```

---

## Required Fields

| Field | Purpose |
|---|---|
| event_id | unique event id |
| event_type | canonical event name |
| event_version | schema version |
| workspace_id | billing and ownership boundary |
| engine | owner engine |
| source | source system/channel |
| payload | event data |
| created_at | event creation time |

---

## Naming Convention

```text
<engine>.<domain>.<action>
```

Examples:

```text
marketing.keyword.detected
marketing.draft.generated
marketing.cta.clicked
watch.incident.created
workflow.approval.requested
ai.usage.recorded
```

---

## Event Versioning

Event payloads must be versioned.

Breaking changes require a new version.

```text
marketing.draft.generated v1
marketing.draft.generated v2
```

---

## Event Registry

Every event type must be registered before production use.

Registry fields:

```text
event_type
version
owner_engine
payload_schema
status
description
```

---

## Prohibitions

```text
1. No unregistered production event types.
2. No engine-specific private event format.
3. No event without workspace_id.
4. No business decision logic inside event payload naming.
5. No provider-specific event names in core runtime.
```
