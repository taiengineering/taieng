# Event Naming Standard & Quality Rules

---

## Naming 형식

```
<domain>.<action>
```

| 요소 | 규칙 | 예시 |
|------|------|------|
| domain | 소문자 단수 명사 | workflow, step, payment, document, runtime, incident |
| action | 소문자 과거분사 | started, completed, failed, timeout, blocked |
| 구분자 | `.` (\ub3c8) | |
| 복합\uc5b4 | `_` (\uc5b8\ub354\uc2a4\ucf54\uc5b4) | `template_missing`, `risk_changed` |

## \ud5c8\uc6a9 \uc608\uc2dc

\u2705 `workflow.failed` \u2014 \uba85\ud655, \ub3c4\uba54\uc778+\uc561\uc158
\u2705 `payment.completed` \u2014 \uba85\ud655, \uacfc\uac70\ubd84\uc0ac
\u2705 `document.template_missing` \u2014 \ubcf5\ud569\uc5b4 \ud5c8\uc6a9
\u2705 `watch.integrity_detected` \u2014 \uc5d4\uc9c4 \ub3c4\uba54\uc778 \ud5c8\uc6a9

## \uae08\uc9c0 \uc608\uc2dc

\u274c `something_wrong` \u2014 \ubaa8\ud638\ud55c \uc758\ubbf8
\u274c `paymentBad` \u2014 camelCase \uae08\uc9c0
\u274c `workflow.error` \u2014 `workflow.failed`\uc640 \uc758\ubbf8 \uc911\ubcf5
\u274c `alert.failed` \u2014 `watch.alert_fired`\uc640 \uc758\ubbf8 \ucda9\ub3cc
\u274c `WORKFLOW_FAILED` \u2014 \ub300\ubb38\uc790 \uae08\uc9c0
\u274c `wf.fail` \u2014 \uc57d\uc5b4 \uae08\uc9c0

---

## Event Quality Rules

### \ud544\uc218 \ud544\ub4dc

| \ud544\ub4dc | \ud544\uc218 | \uac80\uc99d |
|------|:---:|------|
| event_type | \u2705 | `<domain>.<action>` \ud615\uc2dd |
| timestamp | \u2705 | UTC ISO-8601 |
| tenant_id | \u2705 | \ube44\uc5b4\uc788\uc73c\uba74 \uac70\ubd80 |
| trace_id | \u2705 | \ube44\uc5b4\uc788\uc73c\uba74 \uc790\ub3d9 \uc0dd\uc131 |
| source.service | \u2705 | \ucd9c\ucc98 \uc2dd\ubcc4 |
| severity | \u2705 | INFO / WARNING / CRITICAL / FATAL |

### \uae08\uc9c0 \ud328\ud134

| \ud328\ud134 | \uc774\uc720 |
|--------|------|
| Anonymous event (tenant \uc5c6\uc74c) | Tenant Isolation \uc704\ubc18 |
| Missing trace | \ucd94\uc801 \ubd88\uac00 |
| Free-text severity ("bad", "urgent") | \uc758\ubbf8 \ud63c\ub780 |
| Overlapping meaning | Semantic Chaos |
| UI-origin truth event | Sovereignty \uc704\ubc18 |
| Projection-origin truth event | Sovereignty \uc704\ubc18 |
| \uc911\ubcf5 \uc758\ubbf8 event \ub4f1\ub85d | Vocabulary \uc624\uc5fc |

### \uc911\ubcf5 \ubc29\uc9c0 \uc608\uc2dc

| \ub4f1\ub85d \uae08\uc9c0 | \uc0ac\uc6a9\ud574\uc57c \ud560 \uac83 | \uc774\uc720 |
|----------|------------|------|
| `workflow.error` | `workflow.failed` | \uc758\ubbf8 \ub3d9\uc77c |
| `payment.error` | `payment.failed` | \uc758\ubbf8 \ub3d9\uc77c |
| `notification.failed` | `watch.alert_fired` + delivery \uc2e4\ud328 \ubd84\ub9ac | \uc5ed\ud560 \ub2e4\ub984 |
| `step.error` | `step.failed` | \uc758\ubbf8 \ub3d9\uc77c |

---

## Severity Model

| Severity | \uc758\ubbf8 | \uc608\uc2dc | Ownership |
|:---:|------|------|:---:|
| **INFO** | \uc815\uc0c1 \ud750\ub984 | workflow.completed, payment.completed | \ubaa8\ub4e0 Runtime |
| **WARNING** | \ubd80\ubd84 \uc774\uc0c1 | workflow.timeout, step.failed | Control \ud310\uc815 |
| **CRITICAL** | \uc6b4\uc601 \uc601\ud5a5 | workflow.failed, subscription.failed | Control \ud310\uc815 |
| **FATAL** | \uc804\uccb4 \ucc28\ub2e8 | runtime.failed (\uc2dc\uc2a4\ud15c \uc804\uccb4) | Control \ud310\uc815 |

**\ud575\uc2ec: INFO\ub294 \uc5b4\ub290 Runtime\uc774\ub098 \uc124\uc815 \uac00\ub2a5. WARNING/CRITICAL/FATAL\uc740 Control Runtime\ub9cc.**

---

## Core vs Domain Vocabulary

| \uad6c\ubd84 | Vocabulary | \uc608\uc2dc |
|------|-----------|------|
| **Platform Core** | \ubaa8\ub4e0 Engine \uacf5\ud1b5 | workflow.*, step.*, payment.*, document.*, runtime.*, incident.* |
| **Engine Domain** | \uc5d4\uc9c4 \uc804\uc6a9 | watch.*, marketing.*, tai.* |
| **External Custom** | \uc678\ubd80 SaaS \uc804\uc6a9 | custom.*, partner.* |

\uc678\ubd80 Custom Event\ub294 Canonical\uacfc \ucda9\ub3cc \uae08\uc9c0. Semantic Runtime\uc774 custom \u2192 canonical \ubcc0\ud658 \uac00\ub2a5.

## Event Versioning

- \ubaa8\ub4e0 event\uc5d0 `version` \ud544\ub4dc \ud544\uc218 (\uae30\ubcf8: `"1.0"`)
- Minor change: \ud544\ub4dc \ucd94\uac00 (\ud558\uc704 \ud638\ud658)
- Major change: \ud544\ub4dc \uc81c\uac70/\uc758\ubbf8 \ubcc0\uacbd (breaking) \u2192 version \uc99d\uac00
- \uc18c\ube44\uc790\ub294 \uc774\ud574\ud558\ub294 version\ub9cc \ucc98\ub9ac
- \uad6c\ubc84\uc804: 90\uc77c \ubcf4\uad00 \ud6c4 \uc544\uce74\uc774\ube0c

## \ud5a5\ud6c4 \ud655\uc7a5

| Phase | \ubc29\uc2dd |
|:---:|------|
| 1 | \ubb38\uc11c Registry \u2705 |
| 2 | DB Registry (event_type_registry \ud14c\uc774\ube14) |
| 3 | Runtime Validation (\ubbf8\ub4f1\ub85d event \uac70\ubd80) |
| 4 | SDK Validation (\ud074\ub77c\uc774\uc5b8\ud2b8 \uac80\uc99d) |
| 5 | Event Lint (CI/CD \uac80\uc99d) |
