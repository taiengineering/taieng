# Requirement Graph Stress Validation
## 2026-05-13

## 검증 환경

- companies: 127
- factories: 330
- equipment: 1,285
- checklist items: 5,184
- work orders: 20,129
- evidence: 50,300
- notifications: 30,500

## Requirement Graph 안정성

| 검증 | 결과 |
|------|------|
| obligation → document 맨핑 | 11건 유지 |
| document → checklist 맨핑 | 5,184 items 활성 |
| checklist → evidence 맨핑 | 50,300 evidence 연결 |
| orphan work order | 0 |
| orphan evidence | 0 |

## Deterministic Boundary

| 항목 | 결과 |
|------|------|
| inferred obligation | 0 |
| semantic fallback | 0 |
| AI decision | 0 |
| guessed mapping | 0 |

## Worker UX

점검항목 16개/세트 → 3~5초 UX 유지 가능
