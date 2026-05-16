# Notification Lifecycle

작성일: 2026-05-16

---

## 상태 정의

| 상태 | 의미 | 전이 출발 |
|---|---|---|
| RECEIVED | 이벤트 수신 | 시작 |
| POLICY_APPLIED | 정책 적용 (cooldown/dedupe/mute) | RECEIVED |
| QUEUED | Queue 진입 | POLICY_APPLIED |
| PROCESSING | Worker 처리 중 | QUEUED / RETRY_PENDING |
| DELIVERED | 전달 완료 | PROCESSING |
| READ | 수신자 확인 | DELIVERED |
| ACKNOWLEDGED | 수신자 ACK | DELIVERED / READ |
| RESOLVED | 해결 완료 | ACKNOWLEDGED |
| FAILED | 전달 실패 | PROCESSING |
| RETRY_PENDING | 재시도 대기 | FAILED |
| DEADLETTER | 반복 실패 격리 | RETRY_PENDING (max_retry 초과) |
| MUTED | 사용자 뮤트 | POLICY_APPLIED |
| QUIET_HOUR_DELAYED | 조용한 시간 지연 | POLICY_APPLIED |
| SUPPRESSED | 정책에 의해 억제 (cooldown/dedupe) | POLICY_APPLIED |

## 흐름

```
RECEIVED → POLICY_APPLIED → QUEUED → PROCESSING → DELIVERED → READ → ACKNOWLEDGED → RESOLVED
                          → SUPPRESSED
                          → MUTED
                          → QUIET_HOUR_DELAYED → QUEUED
                                      PROCESSING → FAILED → RETRY_PENDING → PROCESSING
                                                                            → DEADLETTER
```

## 중요 원칙

이 상태는 **운영 상태가 아니라 전달 상태**다.
