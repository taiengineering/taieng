# 45 Marketing Engine Runtime

## Purpose

Marketing Engine is not a domain-specific marketing tool.

It is a generic operational marketing runtime.

Domain-specific logic must be injected through Domain Packs.

```text
Marketing Runtime = Generic Operational Runtime
TAI Pack = First Domain Implementation
```

---

## Core Principles

```text
Runtime is generic.
Domain is injected.
AI assists.
Humans control.
Automation is policy-driven.
```

Marketing Engine is not an SNS automation bot.

It is:

```text
AI-assisted B2B Marketing Operations Runtime
```

---

## Runtime Structure

```text
45 Platform Core
 ├─ AI Runtime
 ├─ Event Runtime
 ├─ Queue Runtime
 ├─ Workflow Runtime
 ├─ Tenant Runtime
 └─ Notification Runtime

Marketing Engine
 ├─ Channel Runtime
 ├─ Keyword Runtime
 ├─ Draft Runtime
 ├─ Approval Runtime
 ├─ Publish Runtime
 ├─ CTA Runtime
 ├─ Lead Runtime
 ├─ Analytics Runtime
 └─ Domain Pack Runtime
```

---

## Runtime vs Domain Pack

### Marketing Runtime

Generic concepts only:

```text
campaign
keyword
channel
content
draft
approval_request
publish_job
cta
lead
conversion
analytics
```

### TAI Domain Pack

TAI-specific logic:

```text
무료 법령진단
유료 진단
안전관리 SaaS 전환
산업안전 키워드
법령 콘텐츠 프롬프트
중대재해/과태료 콘텐츠 템플릿
```

Runtime must never hardcode domain-specific concepts.

---

## Initial Channels

```text
1. LinkedIn
2. Facebook
3. Naver Kin
4. Naver Blog
5. Email
```

Each channel implements capabilities.

---

## Core Capabilities

```text
marketing.collect
marketing.keyword_monitor
marketing.classify_intent
marketing.generate_draft
marketing.rewrite_humanize
marketing.request_approval
marketing.publish
marketing.reply
marketing.track_cta
marketing.score_lead
marketing.analyze_conversion
```

---

## Workflow Examples

### Question/Issue Driven Flow

```text
keyword detected
→ content collected
→ intent classified
→ AI draft generated
→ human review
→ approval request
→ publish/reply
→ CTA tracked
→ lead created
→ conversion analyzed
```

### Content Publishing Flow

```text
theme selected
→ AI draft generated
→ human edit
→ approval request
→ scheduled publish
→ reaction collected
→ CTA tracked
→ analytics updated
```

---

## Approval Philosophy

```text
Approval Engine ≠ Groupware
```

The platform only generates approval requests.

Approval is processed through external collaboration tools.

Initial integration target:

```text
Slack
```

---

## Human Control Surface

UI is not a marketing dashboard.

It is:

```text
Marketing Operations Console
```

Core screens:

```text
1. Action Feed
2. Keyword Monitor
3. Draft Review
4. Approval Queue
5. Channel Status
6. CTA Funnel
7. Lead Feed
8. Analytics
9. Policy Settings
```

The platform must be usable even by non-marketers.

---

## AI Smell Prevention

Critical requirement:

```text
AI-generated content must not feel AI-generated.
```

Pipeline:

```text
generate_draft
→ rewrite_humanize
→ brand_voice_check
→ risk_check
→ human_review
```

---

## CTA Runtime

Marketing Engine is not only a publishing tool.

It also manages:

```text
CTA Funnel Runtime
```

Generic CTA structure:

```text
free_offer
paid_validation
subscription_conversion
```

TAI implementation:

```text
무료 법령진단 = inbound
유료 진단 = validation
SaaS 계약 = conversion
```

---

## Pricing Structure

Recommended pricing:

```text
Workspace
+ Seats
+ Customer Accounts
+ Channels
+ AI Credits
```

---

## Queue Structure

```text
45.marketing.collect
45.marketing.classify
45.marketing.draft
45.marketing.humanize
45.marketing.approval
45.marketing.publish
45.marketing.cta_track
45.marketing.analytics
```

---

## Runtime Separation

Marketing Runtime must separate:

```text
Stable Core
```

from:

```text
High-load Workers
```

Services:

```text
marketing-api
marketing-worker
marketing-collector
marketing-ai-worker
marketing-scheduler
```

All AI calls must go through 45 AI Runtime.

---

## MVP Scope

Initial MVP:

```text
1. LinkedIn or Facebook integration
2. Naver Kin collection
3. Keyword monitor
4. AI draft
5. Humanize rewrite
6. Slack approval
7. Manual/Semi-auto publish
8. CTA tracking
9. Lead feed
10. AI usage metering
```

---

## Strict Prohibitions

```text
1. No mass auto-like/comment behavior
2. No default auto-publish behavior
3. No TAI-specific logic inside Runtime Core
4. No direct LLM provider calls inside engines
5. No untracked AI usage
6. No expansion into groupware/electronic approval systems
```

---

## Final Definition

Marketing Engine is defined as:

```text
Multi-Channel Operational Marketing Runtime
```

TAI is defined as:

```text
The first Domain Pack on top of Marketing Runtime
```
