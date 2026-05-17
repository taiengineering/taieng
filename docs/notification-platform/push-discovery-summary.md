# Push Runtime Discovery Summary

작성일: 2026-05-17
범위: Push 전수 조사 결과 요약

---

## 핵심 발견

**Push 인프라가 이미 존재한다.**

- `routers/fcm.py` v1.1.0 — FCM token 등록 + 전화번호 기반 push 발송 + push test
- `utils/fcm_utils.py` — `send_push()` (firebase-admin SDK)
- DB: `users.push_token` + `users.push_platform` + `users.allow_push` + `worker_registry.push_token`
- 호출처 7개: fcm.py, tbm.py, overdue_checker.py, emergency_report.py, workers.py, equipment_checkins.py, safety_reports.py
- 실데이터: 2명 push token 등록
- Legacy: notification_queue.fcm_result, overdue_history.fcm_sent, tbm_attendees.push_sent_at, notification_settings.channel_push

---

## 상태 요약

| 항목 | 상태 |
|---|---|
| FCM SDK | ✅ 존재 + 동작 |
| Token 저장 | ✅ 2테이블 |
| Push 발송 | ✅ direct send (7개 호출처) |
| Queue | ❌ 없음 |
| Retry | ❌ 없음 |
| Audit/Timeline | ❌ 없음 |
| Notification Engine 연결 | ⬜ Mock adapter (dev) |
| Push Readiness | 51% C |

---

## 결론

**신규 구축 불필요.** 기존 `fcm_utils.send_push()`를 Notification Runtime Push Adapter에 연결하면 Queue/Retry/Audit/Timeline 자동 확보.
