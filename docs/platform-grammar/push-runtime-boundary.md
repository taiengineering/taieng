# Push Runtime Boundary

작성일: 2026-05-17
범위: Notification Engine · Push Adapter

---

## 정의

Push는 **Notification Adapter**다. 독립 Push Engine이 아니다.

---

## 구조

```
Notification Runtime
  → Queue Manager
  → Worker
  → Channel Registry (PUSH)
  → Push Adapter (push.py)
  → FCM (Phase 2)
```

---

## 현재 상태

| 항목 | 상태 |
|---|---|
| push.py | ✅ Mock (로깅 전용) |
| channel_registry PUSH | ✅ 등록 (enabled=false) |
| FCM 연동 | ❌ Phase 2 |
| Recipient Rule | ❌ 미생성 |

---

## 금지

- Push-specific workflow 생성
- Push-only queue
- Push-only runtime
- Push-only severity
- Push를 독립 엔진으로 분리

---

## Phase 2 진입 조건

1. firebase-admin SDK 설치
2. FCM_SERVER_KEY 환경변수 설정
3. Recipient Rule PUSH 등록
4. channel_registry enabled=true
5. E2E 테스트 통과
