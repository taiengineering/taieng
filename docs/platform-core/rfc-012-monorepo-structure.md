# RFC-012 Monorepo Structure

## Purpose

Define the recommended monorepo structure for 45cm.

---

## Principle

```text
Single repository.
Multiple runtimes.
Shared platform contracts.
```

---

## Recommended Structure

```text
/apps
  /marketing-api
  /marketing-worker
  /marketing-collector
  /marketing-ai-worker
  /watch-api
  /watch-worker
  /workflow-api
  /scheduler

/packages
  /core-ai-runtime
  /core-event-runtime
  /core-queue-runtime
  /core-policy-runtime
  /core-workflow-runtime
  /core-auth-runtime
  /core-shared-types

  /channel-linkedin
  /channel-facebook
  /channel-naver-kin
  /channel-naver-blog

  /domain-pack-tai

/docs
  /platform-core
  /engines
```

---

## Runtime Separation

Recommended:

```text
Stable Core
+
Dedicated Workers
```

---

## Stable Core

Critical runtime:

```text
auth
workflow
queue contracts
AI gateway
policy runtime
```

Must remain lightweight and reliable.

---

## Dynamic Workers

Heavy runtime:

```text
collectors
AI draft workers
analytics
publish workers
```

May scale independently.

---

## Important Principle

```text
Workers may fail.
Platform core must survive.
```

---

## Shared Package Philosophy

Shared packages own:

```text
contracts
types
runtime rules
```

Applications own:

```text
execution logic
```

---

## Prohibitions

```text
1. No duplicated runtime contracts.
2. No direct cross-app internal imports.
3. No provider SDK leakage into shared contracts.
4. No domain pack logic inside core packages.
```
