# RFC-003 Engine Interface

## Purpose

All engines in 45cm should follow a shared operational interface philosophy.

This enables interoperability, observability, and runtime consistency.

---

## Principle

```text
Engines are operational capability providers.
```

Each engine may implement different subsets of capabilities.

---

## Standard Capability Lifecycle

Recommended lifecycle:

```text
collect
analyze
decide
execute
notify
learn
```

Not all engines must implement every stage.

---

## Engine Manifest

Every engine should expose a manifest.

Example:

```yaml
engine: marketing-engine
version: 1.0

capabilities:
  - collect
  - draft
  - publish
  - approval

queues:
  - 45.marketing.collect
  - 45.marketing.publish

emits:
  - marketing.keyword.detected
  - marketing.draft.generated

consumes:
  - workflow.approval.completed
```

---

## Required Runtime Metadata

Every engine must expose:

```text
engine_name
engine_version
capabilities
queue_bindings
event_bindings
health_status
```

---

## Health Model

Minimum states:

```text
healthy
degraded
maintenance
failed
```

---

## Ownership Principle

```text
Each engine owns its runtime logic.
Shared core owns platform contracts.
```

---

## Isolation Principle

Heavy runtime failure in one engine must not crash the entire platform.

Examples:

```text
Marketing AI overload must not break Auth.
Collector failure must not stop Workflow Runtime.
```

---

## Prohibitions

```text
1. No direct cross-engine DB writes.
2. No engine-private queue standards.
3. No runtime contract override.
4. No shared mutable runtime state without ownership.
```
