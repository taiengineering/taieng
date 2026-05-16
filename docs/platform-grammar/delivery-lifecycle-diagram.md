# Delivery Lifecycle Diagram

작성일: 2026-05-16

---

## 상태 머신

```
RECEIVED (Event Intake)
    ↓
POLICY_APPLIED (Preference Check)
    │
    ├─ SUPPRESSED (mute/disabled) ─── [END]
    ├─ QUIET_HOUR_DELAYED ─── next_retry_at ───┐
    │                                            │
    └─ QUEUED                                    │
         │                                       │
         └────────────────────────────────────┘
                        │
                    PROCESSING
                    │       │
               DELIVERED    FAILED
                    │       │
                    │    RETRY_PENDING ─── next_retry_at ──┐
                    │       │                              │
                    │    DEADLETTER [END]                   │
                    │                                       │
                    └────────────────────────────────────┘
                    │                         (Worker 재포링)
                    │
                   READ
                    │
               ACKNOWLEDGED
                    │
                RESOLVED [END]
```

## 상태 정의

| 상태 | 의미 |
|---|---|
| RECEIVED | 이벤트 수신 |
| QUEUED | Queue 진입 |
| PROCESSING | Worker 처리 중 |
| QUIET_HOUR_DELAYED | 조용한 시간 지연 |
| RETRY_PENDING | 재시도 대기 |
| DELIVERED | 전달 완료 |
| FAILED | 전달 실패 |
| DEADLETTER | 반복 실패 격리 |
| READ | 수신자 확인 |
| ACKNOWLEDGED | 대응 수락 |
| RESOLVED | 해결 완료 |
| SUPPRESSED | 정책 억제 |

## 핵심

**Notification은 상태 머신이다.** 모든 전이는 audit trail로 추적 가능.
