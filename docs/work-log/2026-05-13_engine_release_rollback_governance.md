# Engine Release Rollback Governance
## 2026-05-13

## Rollback 흐름
PUBLISHED → ROLLED_BACK

## Event Types
- ENGINE_PUBLISH_BLOCKED
- ENGINE_RELEASE_PUBLISHED
- ENGINE_RELEASE_ROLLED_BACK
- REGRESSION_BLOCK_TRIGGERED
- GRAPH_VALIDATION_FAILED

## immutable version 기반
각 release는 독립 version. rollback = 이전 version 복원.
