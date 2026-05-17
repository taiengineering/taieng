# Legacy Notification Convergence Plan

작성일: 2026-05-17
범위: Notification Engine · Legacy 수렴

---

## Legacy 자산 분류

| 자산 | 유형 | 분류 | 근거 |
|---|---|---|---|
| sms_service.py | SMS 직접 | **흡수** | Runtime SMS Adapter로 대체 |
| messaging.py | SMS API | **흡수** | wire_and_emit 전환 |
| overdue_checker.py SMS | SMS 직접 | **흡수** | wire_and_emit 전환 필요 |
| workers.py SMS | SMS 직접 | **흡수** | wire_and_emit 전환 필요 |
| pw_reset.py SMS | 인증 SMS | **Freeze** | auth 플로우 — 전환 불필요 |
| notification_templates | Legacy DB | **Freeze** | Phase 2 Template Registry 통합 예정 |
| notification_logs | Legacy DB | **폐기** | runtime_notification_timeline으로 대체 |
| notification_settings | Legacy DB | **폐기** | notification_preferences로 대체 |
| notification_events | Legacy DB | **폐기** | runtime_notification_event로 대체 |
| notification_queue (Legacy) | Legacy DB | **폐기** | runtime_notification_queue로 대체 |
| notification_routing_registry | Legacy DB | **폐기** | notification_event_wiring_registry로 대체 |
| notification_preference_registry | Legacy DB | **폐기** | notification_preferences로 대체 |
| message_template_registry | SMS 템플릿 | **유지** | MessageMi 템플릿 활용 중 |
| system_alert_messages | 시스템 경고 | **유지** | 독립 용도 |
| defect_notification_targets | 결함 대상 | **유지** | 건설 특화 |
| runtime_compat.py | Compat Layer | **흡수** | 전환 후 제거 |
| compat_send.py | Compat Layer | **흡수** | 전환 후 제거 |

---

## 요약

| 분류 | 건수 |
|---|---|
| 유지 | 3 |
| 흡수 (전환 후 제거) | 6 |
| Freeze (변경 금지) | 2 |
| 폐기 (Runtime 대체) | 6 |

---

## 핵심

**Legacy 제거보다 안전한 수렴.** 전환 후 검증 완료까지 Legacy 유지.
