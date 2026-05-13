# Runtime Rollout Governance
## 2026-05-13

## Tenant Risk Classification
| Risk | Rollout 우선순위 |
|------|----------------|
| LOW | 첫 번째 |
| MEDIUM | 두 번째 |
| HIGH | 세 번째 |
| CRITICAL | 마지막 |

## Rollback 조건
- obligation drift 폭증
- completeness corruption
- regression mismatch
- graph inconsistency
- unsupported propagation

## 절대 금지
- CRITICAL tenant first rollout
- mass instant activation
- AI rollout decision
