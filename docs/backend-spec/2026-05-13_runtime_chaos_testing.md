# Runtime Chaos Testing
## 2026-05-13

## 목적
runtime rollout 중 contamination 탐지. production destructive write 금지.

## Scenario Types (8종)
PARTIAL_ROLLOUT_FAILURE, OBLIGATION_DRIFT_INJECTION, COMPLETENESS_CORRUPTION,
CACHE_STALE_STATE, NOTIFICATION_STORM, GRAPH_INCONSISTENCY,
UNSUPPORTED_PROPAGATION, RUNTIME_SPLIT_BRAIN

## API (6 endpoints)
- GET /runtime-chaos/scenarios
- POST /runtime-chaos/run-chaos
- GET /runtime-chaos/contamination-events
- GET /runtime-chaos/rollback-latency
- GET /runtime-chaos/tenant-isolation
- GET /runtime-chaos/status

## 차단 조건
- cross-tenant contamination → CRITICAL BLOCK
- split-brain → CRITICAL BLOCK
- rollback latency 초과 → HIGH BLOCK
- snapshot divergence → CRITICAL BLOCK
