# Quiet Hour Contract

작성일: 2026-05-16
상태: Concept Only

---

## 정의

Quiet Hour는 **delivery policy**다. notification suppression이 아니다.

## 동작 방식

1. Quiet Hour 기간 동안 알림이 도착하면 `QUIET_HOUR_DELAYED` 상태로 Queue 대기
2. Quiet Hour 종료 시 Worker가 poll하여 발송
3. 알림이 삭제되는 것이 아님 (지연 전달)

## Escalation Bypass

CRITICAL severity는 Quiet Hour를 무시할 수 있음 (Phase 2 구현 예정).

## Timezone 고려

- tenant 로컬 timezone 기준으로 Quiet Hour 판단
- 현재 TAI Safe는 KST 단일 timezone
- Multi-timezone 지원은 Phase 2+

## 테이블

`notification_preference_registry`의 `quiet_hour_enabled`, `quiet_hour_start`, `quiet_hour_end` 필드 사용.

## 현재 단계

Timezone engine 구현 금지. Concept만 정의.
