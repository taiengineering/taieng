# Deterministic Regression QA
## 2026-05-13

## 목적
정답 추론이 아니라 **모순과 drift 탐지**.

## Golden Scenario
- 대표 obligation 시나리오를 deterministic truth로 저장
- AI 학습 데이터 아님 — regression validation용
- 동일 scenario → 동일 결과 유지 검증

## Regression Verification
- 새 엔진 결과가 기존 truth와 일치하는지 검증
- REGRESSION_FAILURE 시 publish 차단
- Severity: obligation mismatch=HIGH, completeness mismatch=CRITICAL

## Publish Blocking
반드시: detect → collect → diff → simulate → **regression QA** → review → publish
