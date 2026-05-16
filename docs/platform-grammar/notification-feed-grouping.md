# Notification Feed Grouping Concept

작성일: 2026-05-16
상태: Concept Only (구현 금지)

---

## Grouping 기준 (예시)

| 기준 | 의미 | 예시 |
|---|---|---|
| trace_id | 동일 Runtime 흐름 | WATCH-STUCK-20260516 |
| workflow_id | 동일 Workflow | 승인 요청 → 타임아웃 |
| incident_id | 동일 Incident | 장애 발생 → 해결 |
| source_type | 동일 유형 | billing_notice 모음 |
| tenant_id | 동일 업체 | 업체별 알림 |

## Grouping 방식 (Phase 2+ 예정)

1. **시간 기반 묶기** — 같은 trace_id + 5분 이내 → 1그룹
2. **유형 기반 묶기** — 같은 trigger_code + 같은 날 → 1그룹
3. **Badge count** — 그룹 내 unread 건수 표시

## 현재 단계

구현 금지. Feed Query는 flat list로 반환.
Grouping은 Frontend 또는 Phase 2 Feed Service에서 처리.
