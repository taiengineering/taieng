# Integrity Event Bus UI
## 2026-05-13

## Event Types 연결

| Event Type | Tab | Severity |
|------------|-----|----------|
| OBLIGATION_DRIFT_DETECTED | Drift | CRITICAL |
| COMPLETENESS_DRIFT_DETECTED | Drift | CRITICAL |
| MANDATORY_DRIFT_DETECTED | Mandatory | HIGH |
| AI_CONTAMINATION_DETECTED | AI | CRITICAL |
| UNSUPPORTED_INFERENCE_DETECTED | Unsupported | HIGH |
| CHECKLIST_EXPLOSION_DETECTED | Explosion | HIGH |
| NOTIFICATION_STORM_DETECTED | Drift | WARNING |
| EXPLAINABILITY_LOSS_DETECTED | Explainability | CRITICAL |

## UI 표시
- event_type, severity badge, description, created_at
- input_hash (있으면 표시)
- 색상 코드로 구분
