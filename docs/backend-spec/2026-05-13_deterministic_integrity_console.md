# Deterministic Integrity Console
## 2026-05-13

## 목적

9종 detector 결과를 UI에서 실시간 확인.

## Console 구성

### Drift Detection
- OBLIGATION_DRIFT_DETECTED
- COMPLETENESS_DRIFT_DETECTED
- MANDATORY_DRIFT_DETECTED

### AI Contamination
- AI_CONTAMINATION_DETECTED
- UNSUPPORTED_INFERENCE_DETECTED

### Operational
- CHECKLIST_EXPLOSION_DETECTED
- NOTIFICATION_STORM_DETECTED

### Explainability
- EXPLAINABILITY_LOSS_DETECTED

## 핵심 원칙

- 탐지만 수행, 자동 수정 금지
- 모든 이벤트에 source_trace 필수
- severity 4단계: INFO/WARNING/HIGH/CRITICAL
