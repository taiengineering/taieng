# Runtime Push Integration Direction

작성일: 2026-05-17
범위: Push ↔ Notification Runtime 수렴 최종 방향

---

## 방향

**기존 Push 유지 + Runtime이 orchestration 담당.**

---

## 구조

```
[기존 유지]              [Runtime 추가]

fcm.py (토큰 등록)      wire_and_emit(event_type)
fcm_utils.send_push()   → Queue Manager
users.push_token        → Worker
worker_registry.token   → Push Adapter (push.py)
                        → fcm_utils.send_push() ← 여기서 연결
                        → Timeline + Audit + Retry
```

---

## 유지 대상

| 자산 | 이유 |
|---|---|
| `routers/fcm.py` fcm-token | 앱 → 백엔드 토큰 저장 경로 |
| `utils/fcm_utils.py` | Firebase SDK 핵심 발송 로직 |
| `users.push_token` | 토큰 저장소 |
| `worker_registry.push_token` | 작업자 토큰 저장소 |

---

## Runtime 흡수 대상

| 자산 | Runtime 대체 |
|---|---|
| 직접 send_push 호출 (6곳) | wire_and_emit → Push Adapter |
| push_sent_at / fcm_sent | runtime_notification_timeline |
| fcm_result | runtime_notification_policy_audit |

---

## 금지

| 금지 | 이유 |
|---|---|
| Push rewrite | 기존 작동하는 FCM 유지 |
| Mobile rewrite | 앱 수정 불필요 |
| New push infra | OneSignal/Expo 등 신규 도입 금지 |
| Push-only queue | 단일 Runtime Queue 사용 |
| Push-only lifecycle | Canonical Lifecycle 유지 |

---

## 핵심

**"이미 존재하는 Push를 Runtime OS에 연결."**
새로 만들지 않는다. 기존 것을 Runtime 파이프라인에 편입시킨다.
