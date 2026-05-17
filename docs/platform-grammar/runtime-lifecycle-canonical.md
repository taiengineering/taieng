# Runtime Lifecycle Canonical

작성일: 2026-05-17
범위: Notification Engine · Lifecycle 표준

---

## Canonical Lifecycle

```
RECEIVED
  → POLICY_CHECK
  → QUEUED
  → QUIET_HOUR_DELAYED (조건부)
  → PROCESSING
  → DELIVERED
  → READ
  → ACKNOWLEDGED (Phase 2)
  → RESOLVED (Phase 2)
```

## 분기

```
FAILED
  → RETRY_PENDING (max 3회)
  → DEADLETTER (최종 실패)
```

---

## 상태 정의

| 상태 | 설명 |
|---|---|
| RECEIVED | Event Intake 수신 |
| POLICY_CHECK | Preference/Mute/Quiet Hour 검사 |
| QUEUED | 큐 진입 대기 |
| QUIET_HOUR_DELAYED | Quiet Hour로 지연 |
| PROCESSING | Worker가 Adapter 호출 중 |
| DELIVERED | Adapter 전달 성공 |
| FAILED | Adapter 전달 실패 |
| RETRY_PENDING | 재시도 대기 |
| DEADLETTER | 최종 실패 격리 |
| READ | 사용자 확인 |
| ACKNOWLEDGED | 사용자 조치 확인 (Phase 2) |
| RESOLVED | 완전 종료 (Phase 2) |

---

## 규칙

1. 새 상태 추가 금지 (Phase 1 Freeze)
2. 상태 전이는 단방향 (역행 금지)
3. DELIVERED 이후에만 READ 가능
4. FAILED에서 RETRY_PENDING은 최대 3회
5. DEADLETTER는 수동 해제만 가능 (Phase 2)
