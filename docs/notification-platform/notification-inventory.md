# Notification Surface Inventory

작성일: 2026-05-16
상태: Inventory Complete (Boundary Freeze)

---

## Backend Notification Surface

| 위치 | 종류 | Runtime/Service | 채널 | 현재 구현 | Runtime 사용 | Direct Send | 통합 우선 |
|---|---|---|---|---|---|---|---|
| `services/notification_engine/adapters/telegram.py` | Runtime Alert | Runtime | Telegram | Notification Engine Pipeline | ✅ | ❌ | - |
| `watch_engine/alert/engine.py` (`_send_telegram`) | Legacy Compat | Runtime | Telegram | adapter 경유 (v2.0) | ✅ | ⚠️ legacy | P2 제거 |
| `routers/watch_engine_alert_api.py` | Test Endpoint | Runtime | Telegram | `_send_telegram` 직접 | ❌ | ✅ | P1 |
| `services/sms_service.py` | Service SMS | Service | SMS (MessageMi) | HTTP 직접 호출 | ❌ | ✅ | P1 |
| `routers/messaging.py` | Service SMS | Service | SMS | sms_service 경유 | ❌ | ✅ | P1 |
| `routers/_messaging_compat.py` | Legacy SMS Compat | Service | SMS | 직접 호출 | ❌ | ✅ | P2 |
| `routers/pw_reset.py` | Auth SMS | Service | SMS | sms_service 경유 | ❌ | ✅ | P2 |
| `routers/auth.py` / `auth_oauth.py` | Auth SMS | Service | SMS | sms_service 경유 | ❌ | ✅ | P2 |
| `routers/notifications.py` | Legacy Notification | Service | In-App | DB 직접 INSERT | ❌ | ✅ | P1 |
| `routers/overdue_checker.py` | Overdue SMS | Runtime | SMS | sms_service 직접 | ❌ | ✅ | P1 |
| `services/inbox_notify_svc.py` | In-App Notification | Service | In-App | DB INSERT | ❌ | ✅ | P1 |
| `services/slack_dispatcher.py` | Slack Alert | Service | Slack | Webhook 직접 | ❌ | ✅ | P3 |
| `workflow_alert/evaluator.py` | Alert Notification | Runtime | Telegram | Pipeline 경유 | ✅ | ❌ | - |
| `routers/alert_messages.py` | Alert Message Template | Service | DB | 템플릿 저장 | ❌ | ❌ | P3 |

## Frontend Notification Surface (tai-admin)

| 위치 | 종류 | 채널 | 현재 구현 | Runtime 연동 | Direct Render |
|---|---|---|---|---|---|
| Cockpit Dashboard | System Alert | Dashboard Feed | JS 직접 렌더링 | ❌ | ✅ |
| Watch Telegram Section | Telegram Status | Dashboard | API 호출 | ✅ | ❌ |
| Admin Notice Banner | Maintenance Notice | Banner | 하드코딩/DB | ❌ | ✅ |
| SaaS Toast | 작업 완료/오류 | Toast | Frontend JS | ❌ | ✅ |

## Marketing (taieng)

| 위치 | 종류 | 채널 | 현재 구현 | Runtime 연동 |
|---|---|---|---|---|
| Landing Page | Campaign Banner | HTML Banner | 하드코딩 | ❌ |
| Pricing Page | Event Popup | Modal | JS | ❌ |

## 요약

- **Runtime 경유**: 3개 (Notification Engine Pipeline, Watch Engine v2.0, Alert Evaluator)
- **Direct Send**: 11개 (SMS 6, Telegram 1, In-App 2, Slack 1, Legacy Notification 1)
- **Frontend Direct Render**: 4개 (Dashboard, Banner, Toast, Cockpit)
- **Marketing**: 2개 (하드코딩)
