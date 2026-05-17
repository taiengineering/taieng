# Notification Asset Inventory

작성일: 2026-05-17
범위: 알림 자산 전수 조사

---

## DB 테이블 자산

| 자산 | 유형 | 위치 | Runtime 연동 | 상태 |
|---|---|---|---|---|
| notifications | Feed (IN_APP) | Supabase | ✅ Runtime Adapter | Active |
| notification_templates | SMS/Email 템플릿 | Supabase | ❌ Legacy | Frozen |
| notification_logs | 발송 로그 | Supabase | ❌ Legacy | Frozen |
| notification_settings | 알림 설정 (Legacy) | Supabase | ❌ Legacy | Frozen |
| notification_events | 이벤트 로그 (Legacy) | Supabase | ❌ Legacy | Frozen |
| notification_queue | 큐 (Legacy) | Supabase | ❌ Legacy | Frozen |
| notification_routing_registry | 라우팅 (Legacy) | Supabase | ❌ Legacy | Frozen |
| notification_preference_registry | 선호 (Legacy) | Supabase | ❌ Legacy | Frozen |
| message_template_registry | 메시지 템플릿 | Supabase | ❌ Legacy | Active |
| system_alert_messages | 시스템 경고 | Supabase | ❌ Legacy | Active |
| defect_notification_targets | 결함 알림 대상 | Supabase | ❌ Legacy | Active |
| runtime_notification_queue | Runtime 큐 | Supabase | ✅ Runtime | Active |
| runtime_notification_timeline | 타임라인 | Supabase | ✅ Runtime | Active |
| runtime_notification_policy_audit | 정책 감사 | Supabase | ✅ Runtime | Active |
| runtime_notification_metrics | 집계 | Supabase | ✅ Runtime | Active |
| runtime_notification_deadletter | DLQ | Supabase | ✅ Runtime | Active |
| notification_channel_registry | 채널 | Supabase | ✅ Runtime | Active |
| notification_event_wiring_registry | Wiring | Supabase | ✅ Runtime | Active |
| notification_policy_registry | 정책 | Supabase | ✅ Runtime | Active |
| notification_digest_policy_registry | Digest | Supabase | ✅ Runtime | Shadow |
| runtime_notification_digest_queue | Digest 큐 | Supabase | ✅ Runtime | Shadow |

---

## 코드 자산

| 자산 | 유형 | 위치 | 상태 |
|---|---|---|---|
| sms_service.py | SMS 직접 발송 | services/ | Compatibility |
| messaging.py | SMS API 라우터 | routers/ | Compatibility |
| notification.js | 탑바 벨 팝업 | admin/tadmin/site JS | Active |
| notification-center.html | 알림센터 | admin/tadmin/site HTML | Active |
| adapters/ (telegram/sms/in_app/push) | Runtime Adapter | services/notification_engine/ | Active/Mock |
| event_wiring.py | Wiring Service | services/notification_engine/ | Active |
| digest_runtime.py | Digest Service | services/notification_engine/ | Shadow |
| audience_resolver.py | Audience Resolve | services/notification_engine/ | Foundation |

---

## Frontend Surface 자산

| Surface | 위치 | Runtime | 상태 |
|---|---|---|---|
| Header Bell Popup | notification.js | ✅ API | Active |
| Notification Center | notification-center.html | ✅ API | Active |
| Sidebar Badge | menu-tadmin.js | ✅ API | Active |
| Toast/Popup (Legacy) | 각 페이지 inline | ❌ 정적 | Frozen |
| Dashboard Banner | 없음 | ❌ | 미구현 |
| Announcement | 없음 | ❌ | 미구현 |

---

## 요약

| 분류 | 건수 |
|---|---|
| Runtime Active | 11 DB + 6 코드 + 3 Surface |
| Legacy Frozen | 8 DB |
| Shadow/Foundation | 3 DB + 2 코드 |
| 미구현 | 2 Surface |
