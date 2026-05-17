# Notification Platform Canonical Architecture

작성일: 2026-05-17
범위: Notification Engine · 전체 아키텍처

---

## 아키텍처 흐름

```
Event Source
  │
  ▼
Event Intake (event_intake.py)
  │
  ▼
Recipient Resolver (recipient_resolver.py)
  │
  ▼
Queue Manager (queue_manager.py)
  │  ├─ Policy Check (preference, mute, quiet_hour)
  │  ├─ Policy Audit (runtime_notification_policy_audit)
  │  └─ CRITICAL Bypass
  ▼
Notification Queue (runtime_notification_queue)
  │
  ▼
Worker (worker.py)
  │  ├─ Channel Registry 조회
  │  ├─ Adapter 호출 (telegram/sms/in_app/push)
  │  ├─ Retry Logic
  │  └─ Deadletter 격리
  ▼
Feed (notifications 테이블)
  │
  ▼
Timeline (runtime_notification_timeline)
  │
  ▼
UX Surface
  ├─ Header Bell Popup
  ├─ Notification Center
  ├─ Mobile Notification Center
  └─ Sidebar Badge
```

---

## 연결 엔진

| 엔진 | 연결 지점 | 역할 |
|---|---|---|
| Watch Engine | Event Source → Event Intake | 감시 이벤트 → 알림 변환 |
| Workflow Engine | Event Source → Event Intake | 워크플로우 트리거 → 알림 |
| Integrity Engine | Runtime Consistency Validator | 전달 무결성 검증 |
| Alert Layer | severity 결정 | CRITICAL/WARNING/INFO 분류 |

---

## 데이터 저장소

| 테이블 | 역할 |
|---|---|
| notification_event_registry | 이벤트 유형 등록 |
| runtime_notification_queue | 큐 |
| notifications | Feed (전달된 알림) |
| runtime_notification_timeline | 타임라인 |
| runtime_notification_policy_audit | 정책 감사 |
| runtime_notification_metrics | 집계 지표 |
| runtime_notification_deadletter | 실패 격리 |
| notification_channel_registry | 채널 등록 |
| notification_recipient_rules | 수신자 규칙 |
| notification_preferences | 사용자 선호 |

---

## Adapter 목록

| Adapter | 파일 | 상태 |
|---|---|---|
| Telegram | `adapters/telegram.py` | ✅ Active |
| SMS | `adapters/sms.py` | ✅ Active |
| In-App | `adapters/in_app.py` | ✅ Active |
| Push (FCM) | `adapters/push.py` | ⬜ Mock |
