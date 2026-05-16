# RFC-005 Slack Approval Flow

## Purpose

Marketing Engine requires human-controlled approval.

Approval must integrate with existing collaboration tools instead of implementing full groupware.

Initial target:

```text
Slack
```

---

## Principle

```text
Approval Runtime ≠ Groupware
```

The platform creates approval requests.

Humans approve through Slack.

---

## Approval Flow

```text
Draft Generated
→ Approval Request Created
→ Slack Message Sent
→ User Approves / Rejects
→ Runtime State Updated
→ Publish Queue Triggered
```

---

## Slack Message Requirements

Approval messages should contain:

```text
- draft preview
- workspace
- channel
- risk level
- CTA summary
- approve/reject actions
```

---

## Approval States

```text
pending
approved
rejected
expired
cancelled
```

---

## Policy Support

Workspace policy examples:

```yaml
publish_policy:
  linkedin_post:
    requires_approval: true

  comment_reply:
    requires_approval: false
```

---

## Important Principles

```text
1. Slack is a transport layer.
2. Approval truth belongs to Marketing Runtime.
3. Slack actions must be idempotent.
4. Approval history must be auditable.
```

---

## Prohibitions

```text
1. No full electronic approval workflow.
2. No complex organizational hierarchy logic.
3. No Slack-only approval ownership.
4. No approval action without audit log.
```
