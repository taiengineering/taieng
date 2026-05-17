# Push Runtime Topology

작성일: 2026-05-17
범위: 실제 Push 구조 흐름 (코드 기준)

---

## 현재 실제 흐름

```
App Login / 작업자 등록
  │
  ▼
POST /workers/fcm-token
  │  fcm_token + phone + platform
  │  ├─ worker_registry.push_token UPDATE (작업자)
  │  └─ users.push_token UPDATE (fallback)
  ▼
토큰 저장 완료
  │
  ▼
이벤트 발생 (TBM/점검/긴급/설비 등)
  │
  ▼
전화번호로 토큰 조회
  │  _find_token_by_phone()
  │  worker_registry → users fallback
  ▼
utils/fcm_utils.send_push()
  │  firebase-admin SDK
  │  fcm_token + title + body + data
  ▼
FCM 서버 → 디바이스 Push
```

---

## 토큰 조회 순서

1. `worker_registry.push_token` (phone 기준)
2. `users.push_token` (phone 기준, 하이픈 포맷 재시도)

---

## 발송 방식

- **Direct send**: 각 라우터에서 `fcm_utils.send_push()` 직접 호출
- **큐 없음**: Notification Runtime Queue 미경유
- **Retry 없음**: 실패 시 예외 발생만
- **Timeline 없음**: push 발송 기록 없음 (tbm_attendees.push_sent_at 외)
