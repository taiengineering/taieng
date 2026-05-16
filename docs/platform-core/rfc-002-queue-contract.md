# RFC-002 Queue Contract

## Purpose

Queues are the execution backbone of 45cm.

All asynchronous processing must follow a shared queue contract.

---

## Principles

```text
Queues execute work.
Events describe facts.
Workers consume jobs.
```

---

## Queue Naming

```text
45.<engine>.<capability>
```

Examples:

```text
45.marketing.collect
45.marketing.draft
45.marketing.publish
45.ai.generate
45.watch.analyze
```

---

## Queue Job Contract

```ts
interface QueueJob<TPayload = unknown> {
  job_id: string
  queue: string

  workspace_id: string
  engine: string
  capability: string

  priority: "P1" | "P2" | "P3" | "P4"

  retry_count: number
  max_retry: number

  trace_id?: string
  correlation_id?: string

  payload: TPayload

  created_at: string
}
```

---

## Retry Policy

Default retry:

```text
max_retry = 3
```

Recommended backoff:

```text
1st retry: 30s
2nd retry: 2m
3rd retry: 10m
```

---

## Dead Letter Queue

Every critical queue must support a DLQ.

Examples:

```text
45.marketing.draft.dlq
45.ai.generate.dlq
45.marketing.publish.dlq
```

---

## Queue Ownership

Queues must have a single owning engine.

Consumers may subscribe, but only the owning engine defines the queue contract.

---

## Priority Rules

```text
P1 = immediate / operationally critical
P2 = important / should run soon
P3 = normal background work
P4 = low priority / batch work
```

---

## Idempotency

Workers must be idempotent.

Repeated processing of the same job must not create duplicated external actions.

Examples:

```text
No duplicate post publishing.
No duplicate Slack approval request.
No duplicate AI cost billing.
```

---

## Prohibitions

```text
1. No anonymous queue payload.
2. No queue without workspace_id.
3. No direct provider payload leakage into core queue contract.
4. No engine-specific queue naming style.
5. No non-idempotent external action worker.
```
