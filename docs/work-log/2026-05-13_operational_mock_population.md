# Operational Mock Population
## 2026-05-13

## 생성 결과

| 테이블 | 건수 | 비고 |
|--------|------|------|
| companies | 127 | 100 mock + 27 기존 |
| factories | 330 | 300 mock + 30 기존 |
| equipment_assets | 1,285 | 1,200 mock + 85 기존 |
| inspection_set_items | 5,184 | 324세트 × 16항목 |
| runtime_work_orders | 20,129 | 20K mock |
| runtime_evidence | 50,300 | 50K mock |
| runtime_notifications | 30,500 | 30K mock |
| runtime_reviews | 5,100 | 5K mock |
| runtime_escalations | 933 | overdue 기반 |
| runtime_submissions | 50 | 기존 |
| runtime_sub_failures | 20 | 기존+mock |

## 다양성

- 업종: 제철/화학/건설/물류/병원/식품/반도체/에너지/쇼핑/관광
- 규모: 5명~800명
- 지역: 서울/경기/부산/인천/대전/광주
- 설비: BOILER/CRANE/PRESS/CONVEYOR/PRESSURE_VESSEL/FORKLIFT/FIRE_PUMP/TRANSFORMER
- 점검: 16종 항목 (필수 10 + 선택 6)
- 상태: GENERATED/ASSIGNED/IN_PROGRESS/SUBMITTED/REVIEW_PENDING/APPROVED/REJECTED/ARCHIVED

## 실패 시나리오

- evidence REJECTED: ~8,300건
- work_order overdue: ~6,000건 (due_date < today)
- review REJECT/ESCALATE: ~2,000건
- escalation PENDING: 933건
