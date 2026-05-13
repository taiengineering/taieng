# Staged Runtime Activation
## 2026-05-13

## 핵심: Publish ≠ 즉시 전체 적용

## Rollout Stages
```
INTERNAL (1%) → PILOT (5%) → LIMITED (10%) → EXPANDED (50%) → FULL (100%)
```

## Stage 진행 조건
- regression_status = PASSED
- drift_status ≠ DETECTED/CRITICAL
- activation_status = ACTIVE

## 자동 차단
- CRITICAL regression → BLOCKED
- Mass obligation drift → BLOCKED
- Completeness corruption → rollback
- Unsupported propagation → rollback

## CHECK 제약
- FULL stage는 regression PASSED 필수
