# Notification Policy Readiness Report

작성일: 2026-05-17
범위: Notification Engine · Policy Layer 평가

---

## 평가 항목

| 항목 | 상태 | 점수 |
|---|---|---|
| Event Registry Coverage | notification_event_registry 58,495행 + event wiring 14건 | 8/10 |
| Wiring Coverage | 14 wiring entries, 7 source engines | 8/10 |
| Policy Coverage | 8 policies, severity 3단계 | 9/10 |
| Audience Mapping | 7 audience types 정의 | 7/10 |
| Direct Send 제거율 | wire_and_emit() 준비, 기존 코드 전환 미완 | 5/10 |
| Alert Fatigue 대응 | cooldown + quiet hour + mute + severity 분리 | 8/10 |
| Delivery Hierarchy | v2 6계층 정의 완료 | 9/10 |
| Wiring API | GET wirings + GET policies + POST test | 9/10 |

---

## Policy Readiness Score

**63/80 = 79% — B+ 등급**

---

## 미완료 항목

1. **Direct Send 전환** — 기존 pipeline.emit_notification() 직접 호출 → wire_and_emit() 전환 필요
2. **Audience 실제 해석** — audience_key를 실제 user_id/company_id로 변환하는 resolver 미구현
3. **Cooldown 실제 검사** — last_sent 테이블 필요
4. **Digest Runtime** — 필드만 준비, 실제 묶음 전달 미구현
5. **Escalation Runtime** — 필드만 준비, 실제 지연 에스컬레이션 미구현

---

## 다음 단계

1. Watch Engine → wire_and_emit() 연결
2. Scheduler → wire_and_emit() 연결
3. Audience Resolver 실제 구현
4. Cooldown last_sent 테이블 + 검사 로직
