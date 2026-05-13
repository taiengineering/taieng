# Rollout Drift Verification
## 2026-05-13

## 감시 대상
- obligation drift 증가
- completeness failure 증가
- notification storm
- checklist explosion
- unsupported coverage 증가
- regression mismatch

## drift_status
- CLEAN: 0 events
- WARNING: 1~2 events
- DETECTED: 3~9 events
- CRITICAL: 10+ events → 자동 BLOCKED

## Event Types
- ACTIVATION_DRIFT_DETECTED
- RUNTIME_ROLLOUT_BLOCKED
- ROLLBACK_TRIGGERED
