# Quiet Hour Boundary

작성일: 2026-05-16

---

## 구분

| 개념 | 의미 | Queue 상태 | 전달 여부 |
|---|---|---|---|
| **Quiet Hour** | 전달 지연 | QUIET_HOUR_DELAYED | ✅ 지연 후 전달 |
| **Suppression** | 전달 차단 | SUPPRESSED (audit만) | ❌ 전달 안 함 |
| **Mute** | 사용자 선택 차단 | Queue 생성 안 함 | ❌ 전달 안 함 |
| **CRITICAL bypass** | 운영 예외 | QUEUED (즉시) | ✅ 뮤트/QH 무시 |

## 핵심

```
Quiet Hour는 삭제가 아니라 지연이다
```

## 동작 흐름

```
Queue 생성 시 Quiet Hour 확인
  → QH 범위 내: delivery_status = QUIET_HOUR_DELAYED, next_retry_at = QH 종료 시각
  → QH 범위 외: delivery_status = QUEUED (정상)
  → severity=CRITICAL: QUEUED (즉시, QH 무시)

Worker poll
  → QUIET_HOUR_DELAYED + next_retry_at 도래 → QUEUED 전환 → 발송
```

## 현재 제한

- KST 단일 timezone (한국 전용)
- tenant timezone 미지원 (Phase 2)
