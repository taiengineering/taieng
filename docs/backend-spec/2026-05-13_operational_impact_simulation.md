# Operational Impact Simulation
## 2026-05-13

## 목적
법령 개정이 실제 운영에 미치는 영향 deterministic 계산.

## 계산 대상
- 영향 회사/사업장 수
- 신규/제거 obligation
- checklist/document/evidence delta

## Severity
| 조건 | Severity |
|------|----------|
| 영향 1~10회사 | INFO |
| 10~100회사 | WARNING |
| 100+회사 | HIGH |
| mandatory rule 변경 | CRITICAL |

## 절대 금지
- AI impact prediction
- probabilistic estimation
- semantic guessing

## 필수 흐름
detect → collect → diff → **simulate** → review → QA → publish

simulation 없이 publish 금지.
