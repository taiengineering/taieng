# Implementation Sprint 001 — Marketing Runtime First Vertical Slice

## Purpose

This sprint implements the first end-to-end runtime flow for Marketing Engine.

The goal is not to build every marketing feature.

The goal is to prove that the platform runtime works across:

```text
Keyword Detect
→ AI Draft
→ Humanize Rewrite
→ Slack Approval
→ Publish
→ CTA Track
```

---

## Core Principle

```text
Build one complete operational flow before expanding channels or features.
```

---

## Sprint Goal

Implement a minimal but real vertical slice that validates:

```text
- Marketing DB schema
- Queue contract
- Event envelope
- AI Runtime usage
- Slack approval flow
- Channel adapter boundary
- CTA tracking
- Lead creation
```

---

## MVP Flow

```text
1. Keyword is monitored.
2. External content is collected.
3. Content is classified.
4. AI draft is generated through 45 AI Runtime.
5. Draft is humanized.
6. Slack approval request is created.
7. Human approves or rejects.
8. Publish job is created.
9. Publish executes manually or semi-automatically.
10. CTA click/conversion is tracked.
```

---

## Initial Channel Choice

Recommended first channel:

```text
Naver Kin collection + Slack approval + manual/semi-auto publish
```

Reason:

```text
- Existing TAI context already has Naver Kin collection experience.
- Lower OAuth complexity than LinkedIn/Facebook.
- Validates keyword-driven marketing model quickly.
```

LinkedIn/Facebook adapters should follow after runtime validation.

---

## Required Packages / Apps

```text
/apps/marketing-api
/apps/marketing-worker
/apps/marketing-collector
/apps/marketing-ai-worker
/apps/scheduler

/packages/core-ai-runtime
/packages/core-event-runtime
/packages/core-queue-runtime
/packages/core-policy-runtime
/packages/channel-naver-kin
/packages/domain-pack-tai
```

---

## Step 1 — Database Migration

Create schemas:

```text
core_ai
marketing
```

Apply tables from:

```text
docs/platform-core/ai-runtime.md
docs/engines/marketing/rfc-007-marketing-db-schema.md
```

Minimum required tables for Sprint 001:

```text
core_ai.ai_usage_log
core_ai.ai_budget
core_ai.ai_model_policy
core_ai.prompt_registry

marketing.workspaces
marketing.channels
marketing.keywords
marketing.contents
marketing.drafts
marketing.approval_requests
marketing.publish_jobs
marketing.ctas
marketing.leads
marketing.conversions
marketing.analytics_events
marketing.channel_policies
marketing.domain_pack_bindings
```

---

## Step 2 — Queue Setup

Minimum queues:

```text
45.marketing.collect
45.marketing.classify
45.marketing.draft
45.marketing.humanize
45.marketing.approval
45.marketing.publish
45.marketing.cta_track
45.ai.generate
```

All jobs must follow:

```text
docs/platform-core/rfc-002-queue-contract.md
```

---

## Step 3 — AI Runtime MVP

Implement:

```text
ai.generate()
```

Minimum features:

```text
- workspace_id required
- engine required
- capability required
- prompt registry lookup
- OpenAI provider adapter
- token usage logging
- estimated cost logging
- budget check placeholder
```

Initial capabilities:

```text
marketing.generate_draft
marketing.rewrite_humanize
marketing.classify_intent
```

---

## Step 4 — Naver Kin Collector

Implement as Channel Adapter:

```text
packages/channel-naver-kin
```

Responsibilities:

```text
- read workspace keywords
- query Naver Kin search API
- normalize external content
- save marketing.contents
- emit marketing.keyword.detected event
- enqueue 45.marketing.classify
```

Adapter must not call AI directly.

---

## Step 5 — Draft Pipeline

Pipeline:

```text
45.marketing.classify
→ 45.marketing.draft
→ 45.marketing.humanize
```

Rules:

```text
- Draft generation must use 45 AI Runtime.
- Humanize rewrite must use 45 AI Runtime.
- Generated drafts must be stored in marketing.drafts.
- AI usage log id should be linked when possible.
```

---

## Step 6 — Slack Approval

Implement:

```text
45.marketing.approval
```

Flow:

```text
marketing.drafts created
→ marketing.approval_requests created
→ Slack message sent
→ Slack action callback updates approval_requests
```

States:

```text
pending
approved
rejected
expired
cancelled
```

Slack is transport only.

Marketing Runtime owns approval state.

---

## Step 7 — Publish MVP

Initial publish mode:

```text
manual or semi-auto
```

Reason:

```text
Avoid platform policy and brand risk during Sprint 001.
```

Publish job can generate:

```text
- copyable final answer
- target URL
- CTA link
- manual action checklist
```

Full auto-publish is not required in Sprint 001.

---

## Step 8 — CTA Tracking

Implement basic CTA tracking:

```text
cta link clicked
→ marketing.analytics_events
→ marketing.leads optional
→ marketing.conversions optional
```

TAI Pack default CTA:

```text
무료 법령진단
```

---

## Sprint 001 Success Criteria

Sprint is successful when one real keyword can travel through the whole flow:

```text
Keyword configured
→ Naver Kin content collected
→ AI draft generated
→ humanized
→ Slack approval requested
→ approved
→ publish job created
→ CTA tracked
```

---

## Out of Scope

```text
- Full LinkedIn OAuth
- Full Facebook OAuth
- Auto-like / auto-comment growth automation
- Full groupware approval
- Advanced analytics
- Multi-domain pack marketplace
- Full billing integration
```

---

## Strict Prohibitions

```text
1. No direct LLM provider call outside AI Runtime.
2. No TAI-specific columns in Marketing Runtime tables.
3. No auto-publish as default behavior.
4. No approval state owned by Slack.
5. No queue job without workspace_id.
6. No AI call without usage log.
```

---

## Next Sprint Candidates

After Sprint 001:

```text
1. LinkedIn adapter POC
2. Facebook page adapter POC
3. Marketing Operations Console UI
4. Brand Voice Profile
5. Policy Runtime enforcement
6. Billing / AI Credit integration
```
