# Pre-QA Validation Handoff
## 2026-05-13

## 운영 밀도

| 구분 | 건수 |
|------|------|
| 회사 | 127 |
| 사업장 | 330 |
| 설비 | 1,285 |
| 점검항목 | 5,184 |
| 작업지시 | 20,129 |
| 증빙 | 50,300 |
| 알림 | 30,500 |
| 리뷰 | 5,100 |
| 에스컬레이션 | 933 |
| **총계** | **~113,000건** |

## Deterministic Boundary

- illegal_ai_decision_count: 0
- inferred obligation: 0
- semantic fallback: 0

## 최종 보고

```json
{
  "phase": "OPERATIONAL_MOCK_POPULATION",
  "companies_generated": 100,
  "facilities_generated": 300,
  "equipment_generated": 1200,
  "checklists_activated": 5184,
  "inspections_generated": 20000,
  "evidence_generated": 50000,
  "completeness_failures_generated": 8300,
  "notifications_generated": 30000,
  "reviews_generated": 5000,
  "escalations_generated": 933,
  "runtime_boundary_clean": true,
  "illegal_ai_decision_count": 0,
  "next_phase": "Adversarial QA & Operational Audit"
}
```
