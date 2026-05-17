# Push Integration Direction

작성일: 2026-05-17
범위: 기존 Push → Notification Runtime 수렴 방향

---

## 유지

| 항목 | 이유 |
|---|---|
| `routers/fcm.py` FCM 토큰 등록 | 앱 → 백엔드 토큰 저장 경로 |
| `utils/fcm_utils.py` send_push() | Firebase SDK 핵심 발송 로직 |
| `users.push_token` + `worker_registry.push_token` | 토큰 저장소 |

---

## Runtime으로 흡수

| 항목 | 방법 |
|---|---|
| `routers/fcm.py` send-push | `wire_and_emit()` → Push Adapter 로 전환 |
| `tbm.py` push 호출 | `wire_and_emit('tbm_attendance')` 전환 |
| `overdue_checker.py` push 호출 | `wire_and_emit('schedule_overdue')` 전환 |
| `emergency_report.py` push 호출 | `wire_and_emit('accident_reported')` 전환 |
| `equipment_checkins.py` push 호출 | `wire_and_emit('equipment_checkin')` 전환 |
| `safety_reports.py` push 호출 | `wire_and_emit('safety_report')` 전환 |

---

## 제거

| 항목 | 시점 |
|---|---|
| `notification_queue.fcm_result` | Legacy 큐 폐기 시 |
| `overdue_history.fcm_sent` | Runtime timeline 대체 후 |
| `tbm_attendees.push_sent_at` | Runtime timeline 대체 후 |

---

## Freeze

| 항목 | 이유 |
|---|---|
| `routers/fcm.py` push-test | 개발 테스트 전용 유지 |
| `notification_settings.channel_push` | Legacy 설정 (전환 후 제거) |

---

## 실행 순서

1. `push.py` mock → `fcm_utils.send_push()` 실연동
2. `notification_channel_registry` PUSH enabled=true
3. audience_resolver에 push_token 조회 추가
4. 6개 호출처 → wire_and_emit 전환
5. Legacy push 필드 제거 (전환 검증 후)
