# Delayed Delivery Boundary

작성일: 2026-05-16

---

## 구분

| 개념 | 의미 | 원인 | Queue 상태 |
|---|---|---|---|
| **Retry** | 실패 재시도 | Adapter 발송 실패 | RETRY_PENDING |
| **Delay** | 정책 지연 | Quiet Hour | QUIET_HOUR_DELAYED |
| **Cooldown** | 중복 방지 | 동일 dedupe_key | Queue 생성 skip |
| **Suppression** | 전달 차단 | Mute/Disabled | Queue 생성 안 함 |

## 핵심

```
Retry와 Delay는 다르다
```

- **Retry**: 발송 시도 후 실패 → 재시도 (exponential backoff)
- **Delay**: 발송 시도 전 정책에 의해 대기 (quiet hour end 까지)

## Worker 처리

두 개 모두 `next_retry_at` 기반으로 포링:
- RETRY_PENDING: `next_retry_at <= now()` 도래 시 poll
- QUIET_HOUR_DELAYED: `next_retry_at <= now()` 도래 시 poll

둘 다 PROCESSING → Adapter → DELIVERED/FAILED 흐름 동일.
