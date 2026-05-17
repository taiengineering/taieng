# Notification Platform Freeze Manifest

작성일: 2026-05-17
상태: Phase 1 Freeze 공식 선언

---

## Freeze 선언

Notification Platform Phase 1은 **동결(Freeze)** 상태에 진입한다.
신규 Runtime 기능 추가, Grammar 변경, Lifecycle 변경을 금지한다.

---

## Runtime Freeze 대상

| 대상 | 고정 내용 |
|---|---|
| Queue Grammar | PENDING → PROCESSING → DELIVERED / FAILED / RETRY_PENDING / DEADLETTER / QUIET_HOUR_DELAYED |
| Delivery Lifecycle | RECEIVED → POLICY_CHECK → QUEUED → DELIVERED → READ (+ 분기) |
| Policy Audit | MUTE_SUPPRESSED, DISABLED_SUPPRESSED, QUIET_HOUR_DELAYED, CRITICAL_BYPASS |
| Timeline Contract | EVENT → QUEUE → POLICY_* → DELIVERED → FEED_CREATED → READ |
| Feed Contract | notification_id, title, body, severity, channel_key, source_type, is_read, created_at, trace_id |
| Adapter Interface | `send(message, context) → (success, error)` |

---

## UX Freeze 대상

| Surface | 고정 내용 |
|---|---|
| Notification Center | Feed/Timeline/Settings/Health 4탭 |
| Header Bell | Popup 5건 + unread badge + 알림센터 링크 |
| Sidebar Badge | `.notif-sidebar-badge` slot + updateBadge 동기화 |
| Feed Card | severity badge + channel badge + 2줄 body + 상대시간 |
| Timeline Viewer | trace_id 기반 step 추적 모달 |
| Preference Surface | source_type × channel_key 토글 |

---

## Naming Freeze

| 필드 | 고정 값 |
|---|---|
| trace_id | UUID v4 |
| source_type | runtime_alert, service_notice, workflow_event 등 |
| channel_key | TELEGRAM, SMS, IN_APP, PUSH, EMAIL, SITE, KAKAO |
| severity | INFO, WARNING, CRITICAL |
| delivery_status | PENDING, PROCESSING, DELIVERED, FAILED, RETRY_PENDING, DEADLETTER |

---

## Freeze 해제 조건

Phase 2 진입 시에만 해제. Phase 2 Boundary 문서에 정의된 범위 내에서만 변경 허용.
