# Notification Runtime Refactoring Plan

작성일: 2026-05-17
범위: 관제로 이동해야 하는 의미 목록

---

## 이동 대상

| 의미 | 현재 위치 | 이동 대상 | 단계 | 우선순위 |
|---|---|---|---|---|
| default_severity | notification_policy_registry | Control Runtime severity API | Phase 2 | MEDIUM |
| escalation_enabled | notification_event_wiring_registry | Control Runtime escalation API | Phase 2 | LOW |
| escalation_delay_seconds | notification_policy_registry | Control Runtime escalation API | Phase 2 | LOW |

---

## 단계별 전략

### Immediate (현재)

이동 대상 **없음**. 현재 CRITICAL 충돌 0건.

### Phase 2 (Control Runtime 구현 시)

1. Control Runtime에서 severity API 제공
2. wire_and_emit에서 Control severity 우선 조회
3. Policy default_severity는 fallback으로 유지
4. escalation 플래그/지연을 Control로 이관

### Observation (관찰)

- severity 충돌 발생 여부 모니터링
- escalation 실제 사용 여부 확인
- 운영 데이터 기반 이동 시점 결정

---

## 핵심

**현재 단계에서 이동 필요 없음.** CRITICAL 충돌 0건. Control Runtime 구현 시 점진적 이관.
