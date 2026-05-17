# Push Infrastructure Inventory

작성일: 2026-05-17
범위: 기존 Push 인프라 전수 조사

---

## 코드 자산

| 구성 | 존재 | 위치 | 상태 |
|---|---|---|---|
| FCM 토큰 등록 API | ✅ | `routers/fcm.py` POST /workers/fcm-token | Active (v1.1.0) |
| 전화번호 기반 Push 발송 | ✅ | `routers/fcm.py` POST /workers/send-push | Active |
| Push 테스트 | ✅ | `routers/fcm.py` POST /workers/push-test | Active |
| firebase-admin SDK | ✅ | `utils/fcm_utils.py` `send_push()` | Active |
| Push Adapter (Notification Engine) | ✅ | `services/notification_engine/adapters/push.py` | Mock (dev) |
| PUSH Channel Registry | ✅ | `notification_channel_registry` PUSH row | enabled=false |

---

## DB 자산

| 테이블 | 칼럼 | 역할 |
|---|---|---|
| `users` | `push_token` | 사용자 FCM 토큰 |
| `users` | `push_platform` | ios / android / web |
| `users` | `allow_push` | Push 허용 여부 |
| `worker_registry` | `push_token` | 작업자 FCM 토큰 |
| `notification_queue` | `fcm_result` | Legacy 발송 결과 |
| `overdue_history` | `fcm_sent` | 미이행 push 발송 플래그 |
| `tbm_attendees` | `push_sent_at` | TBM push 발송 시간 |
| `notification_settings` | `channel_push` | Push 채널 설정 |

---

## 실데이터

| 항목 | 값 |
|---|---|
| push_token 등록 사용자 | 2명 |
| push_platform | 1종 |
| allow_push | 미확인 |

---

## Push 호출처 (7개)

| 파일 | 용도 |
|---|---|
| `routers/fcm.py` | FCM 토큰 등록 + push 발송 |
| `routers/tbm.py` | TBM 참석자 push |
| `routers/overdue_checker.py` | 미이행 점검 push |
| `routers/emergency_report.py` | 긴급상황 push |
| `routers/workers.py` | 작업자 push |
| `routers/equipment_checkins.py` | 설비 체크인 push |
| `routers/safety_reports.py` | 안전보고 push |
