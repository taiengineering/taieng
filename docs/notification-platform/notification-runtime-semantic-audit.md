# Notification Runtime Semantic Audit

작성일: 2026-05-17
범위: Notification Runtime 내부 의미 요소 전수 감사

---

## 의미 요소 전수 조사

| 요소 | 현재 위치 | 실제 Owner | 충돌 여부 | 상태 |
|---|---|---|---|---|
| severity (default_severity) | notification_policy_registry | Control Runtime | ⚠️ WARNING | Notification이 기본값 제공 중 — Control에서 받아야 함 |
| severity (override) | wire_and_emit override_severity | Control Runtime | ✅ SAFE | 외부에서 주입, Notification은 소비만 |
| escalation_enabled | notification_event_wiring_registry | Control Runtime | ⚠️ WARNING | Wiring에 escalation 플래그 존재 — Control 판단 영역 |
| escalation_delay | notification_policy_registry | Control Runtime | ⚠️ WARNING | Policy에 에스컬레이션 지연 존재 |
| suppression (mute) | notification_preferences | Notification | ✅ SAFE | 사용자 선호 — 정당한 Notification 영역 |
| suppression (cooldown) | policy + wiring | Notification | ✅ SAFE | 전달 빈도 조절 — Notification 영역 |
| quiet_hour_bypass | notification_policy_registry | Notification | ✅ SAFE | 전달 시간대 제어 |
| recovery | 없음 | Control Runtime | ✅ SAFE | 미구현 — 충돌 없음 |
| incident_ref | 없음 | Control Runtime | ✅ SAFE | 미구현 — 충돌 없음 |
| ACK (acknowledged) | runtime_notification_queue | Delivery Runtime | ✅ SAFE | Delivery 상태 관리 |
| RESOLVED | runtime_notification_queue | Delivery Runtime | ✅ SAFE | Delivery 상태 관리 |
| delivery_priority | 없음 (severity로 대체) | Notification | ✅ SAFE | severity 기반 우선순위 |
| retry 의미 | retry_policy.py | Delivery Runtime | ✅ SAFE | Delivery 전용 |
| fatigue | cooldown + digest + mute | Notification | ✅ SAFE | 전달 밀도 조절 |
| audience | audience_resolver + wiring | Notification | ✅ SAFE | 수신 대상 결정 |
| channel | policy_registry | Notification | ✅ SAFE | 채널 결정 |
| digest | digest_policy_registry | Notification | ✅ SAFE | 묶음 전달 |

---

## 요약

| 분류 | 건수 |
|---|---|
| SAFE | 14 |
| WARNING | 3 (severity default, escalation_enabled, escalation_delay) |
| CRITICAL | 0 |

---

## WARNING 항목 분석

1. **severity default_severity** — Policy에 기본 severity가 존재. Control Runtime이 없는 현재 단계에서는 허용. Control Runtime 구현 시 이관.
2. **escalation_enabled** — Wiring에 플래그만 존재, 실제 에스컬레이션 로직 미구현. 현재 충돌 없음.
3. **escalation_delay** — Policy에 값만 존재, 실제 사용 없음. 현재 충돌 없음.

**결론: 현재 단계에서 CRITICAL 충돌 없음. WARNING 3건은 Control Runtime 구현 시 이관 예정.**
