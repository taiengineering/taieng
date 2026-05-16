# RFC-006 Channel Adapter

## Purpose

Marketing Runtime must support multiple channels without polluting Runtime Core.

Each platform integration is implemented as a Channel Adapter.

---

## Principle

```text
Channels implement capabilities.
Runtime orchestrates workflows.
```

---

## Adapter Responsibilities

Adapters may implement:

```text
collect
publish
reply
monitor
react
```

Not every channel supports every capability.

---

## Example Matrix

| Channel | collect | publish | reply | monitor |
|---|---:|---:|---:|---:|
| LinkedIn | O | O | O | O |
| Facebook | O | O | O | O |
| Naver Kin | O | partial | O | O |
| Naver Blog | X | O | X | O |

---

## Adapter Structure

```text
channels/
 ├─ linkedin/
 ├─ facebook/
 ├─ naver-kin/
 ├─ naver-blog/
 └─ email/
```

---

## Standard Adapter Interface

```ts
interface ChannelAdapter {
  channel: string

  collect?(input: unknown): Promise<unknown>
  publish?(input: unknown): Promise<unknown>
  reply?(input: unknown): Promise<unknown>
  monitor?(input: unknown): Promise<unknown>
}
```

---

## OAuth Principle

Preferred approach:

```text
OAuth first
```

Manual/browser-assisted integration may exist for unsupported platforms.

---

## Important Runtime Rules

```text
1. Runtime must not contain provider-specific logic.
2. Adapters isolate provider complexity.
3. Adapters must emit standard platform events.
4. Adapters must respect rate limits.
5. Adapters must support retry safety.
```

---

## Prohibitions

```text
1. No provider SDK leakage into Runtime Core.
2. No hardcoded channel-specific workflow logic.
3. No direct AI calls inside adapters.
4. No untracked external API calls.
```
