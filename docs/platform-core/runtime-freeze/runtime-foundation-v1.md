# Runtime Foundation v1 — Stable Release

선언일: 2026-05-16

---

## 선언

TAI Safe Platform Runtime Foundation v1을 **Stable**로 선언한다.

이하 Runtime Core는 **Freeze** 상태로 진입하며, 구조적 확장은 제한된다.

---

## v1 구성 요소

| 계층 | 구성 | 상태 |
|------|------|:---:|
| **Platform Core** | Event Envelope + Runtime Contract + Engine Namespace | ✅ Frozen |
| **Runtime Taxonomy** | 8\uac1c \ub3c5\ub9bd Runtime + 6 Layer Model | ✅ Frozen |
| **Runtime Sovereignty** | Capability Registry + Truth Enforcer + Permission | ✅ Frozen |
| **Canonical Vocabulary** | 39\uac1c Event + Naming Standard + Quality Rules | ✅ Frozen |
| **Runtime Validation** | 6\ub2e8\uacc4 Event Validator + Error Model | ✅ Frozen |
| **Runtime Event Bus** | Central emit + Event Store + EventResult | ✅ Frozen |
| **Runtime Gateway** | Ingest + Output + Workflow Observability + Tenant Boundary | ✅ Frozen |
| **Runtime Dependency** | \ud5c8\uc6a9 12\uac1c + \uae08\uc9c0 10\uac1c \uc758\uc874 \ubc29\ud5a5 | ✅ Frozen |
| **Watch Engine Domain** | 24 DB + 17 Router + 9 Scheduler + 18 Cockpit | ✅ Frozen |
| **Control Boundary** | Truth Ownership 15\uac1c + Incident Lifecycle + Event Contract | ✅ Frozen |

## \ubb38\uc11c \ubaa9\ub85d (24\uac1c)

### platform-core/ (10\uac1c)
- event-envelope.md
- runtime-contract.md
- engine-namespace.md
- runtime-sovereignty.md
- runtime-validation.md
- runtime-event-bus.md
- runtime-gateway-implementation.md
- runtime-taxonomy/runtime-categories.md
- runtime-taxonomy/runtime-dependency-graph.md
- runtime-taxonomy/runtime-ownership-map.md

### runtime-gateway/ (4\uac1c)
- control-ingest-gateway.md
- control-output-gateway.md
- workflow-observability-contract.md
- external-runtime-contract.md

### runtime-vocabulary/ (2\uac1c)
- canonical-event-registry.md
- event-naming-and-quality.md

### engines/watch/ (5\uac1c)
- watch-domain.md
- control-runtime-boundary.md
- operational-truth-ownership.md
- control-event-contract.md
- incident-lifecycle-ownership.md

### platform-grammar/ (7\uac1c) \u2014 \uae30\uc874
- core-language.md, platform-entity-map.md, AI_SHARED_CONTEXT.md, ownership-matrix.md, permission-system-interface.md, semantic-adapter.md, alert-vs-notification.md

## \ucf54\ub4dc \ubaa8\ub4c8 (v1)

| \ubaa8\ub4c8 | \ubc84\uc804 |
|------|:---:|
| watch_engine/integrity/ | evaluator v1.3 |
| watch_engine/incident/ | repeated v1.1 |
| watch_engine/governance/ | tenant_impact v1.1 |
| watch_engine/knowledge/ | stability v1.1 |
| watch_engine/semantic_adapter/ | v1.0 |
| watch_engine/document/ | activation v1.2 |
| watch_engine/runtime_sovereignty/ | v1.0 |
| watch_engine/runtime_validation/ | v1.0 |
| watch_engine/runtime_bus/ | v1.0 |
| routers/control_runtime_gateway_api.py | v1.0 |
| scheduler.py | v1.7 |
| routers/cron_manager.py | v2.0 |
