# FCM Existing Runtime Analysis

작성일: 2026-05-17
범위: 기존 FCM 구조 전수 문서화 (코드 기준)

---

## 코드 자산

| 구성 | 위치 | 역할 | 상태 |
|---|---|---|---|
| FCM Router | `routers/fcm.py` v1.1.0 | 토큰 등록 + 전화번호 push + test | Active |
| FCM Utils | `utils/fcm_utils.py` | `send_push(fcm_token, title, body, data)` firebase-admin SDK | Active |
| Push Adapter (Mock) | `services/notification_engine/adapters/push.py` | Mock 로깅 전용 | dev branch |

---

## Token 저장 구조

| 테이블 | 컬럼 | 역할 |
|---|---|---|
| `users` | `push_token` | 사용자 FCM 토큰 |
| `users` | `push_platform` | ios/android/web |
| `users` | `allow_push` | Push 허용 여부 |
| `worker_registry` | `push_token` | 작업자 FCM 토큰 |

---

## Login → Token 흐름

```
App Login
  → POST /workers/fcm-token
  → {fcm_token, phone, platform, worker_id}
  → worker_id 직접 → worker_registry UPDATE
  → phone → worker_registry 검색 → 없으면 users fallback
  → push_token + push_platform 저장
```

---

## Push 발송 흐름

```
이벤트 발생 (TBM/점검/긴급/설비)
  → 전화번호로 토큰 조회 (_find_token_by_phone)
  → worker_registry.push_token 먼저
  → users.push_token fallback
  → fcm_utils.send_push(token, title, body, data)
  → Firebase Cloud Messaging → 디바이스
```

---

## 호출처 7개

| 파일 | 이벤트 | 발송 방식 |
|---|---|---|
| `routers/fcm.py` | 토큰 등록 + send-push + push-test | Direct API |
| `routers/tbm.py` | TBM 참석자 push | `fcm_utils.send_push()` 직접 |
| `routers/overdue_checker.py` | 미이행 점검 push | `fcm_utils.send_push()` 직접 |
| `routers/emergency_report.py` | 긴급상황 push | `fcm_utils.send_push()` 직접 |
| `routers/workers.py` | 작업자 push | `fcm_utils.send_push()` 직접 |
| `routers/equipment_checkins.py` | 설비 체크인 push | `fcm_utils.send_push()` 직접 |
| `routers/safety_reports.py` | 안전보고 push | `fcm_utils.send_push()` 직접 |

---

## 환경변수

| 변수 | 용도 |
|---|---|
| `GOOGLE_APPLICATION_CREDENTIALS` | Firebase 서비스 계정 JSON |
| (Railway 환경에 설정됨) | firebase-admin 초기화 |

---

## Legacy Push 필드

| 테이블 | 컬럼 | 용도 |
|---|---|---|
| `notification_queue` | `fcm_result` | Legacy 발송 결과 |
| `overdue_history` | `fcm_sent` | 미이행 push 발송 플래그 |
| `tbm_attendees` | `push_sent_at` | TBM push 발송 시간 |
| `notification_settings` | `channel_push` | Push 채널 설정 |
