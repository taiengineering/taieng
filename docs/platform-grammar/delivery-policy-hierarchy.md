# Delivery Policy Hierarchy

작성일: 2026-05-16

---

## 우선순위 (높은 것이 우선)

```
1. Permission (플랫폼 정책)        ← 미구현, Phase 2
2. CRITICAL bypass (운영 예외)    ← ✅ 구현 완료
3. User Preference (사용자 선택) ← ✅ 구현 완료
4. Quiet Hour (조용한 시간)       ← ✅ 구현 완료
5. Cooldown/Dedupe (중복 방지)   ← ✅ 기존 구현
6. Default Policy (기본값)        ← ✅ 기존 구현
```

## 적용 로직

```
if severity == CRITICAL:
    bypass (mute/quiet hour 무시)
elif is_channel_muted(actor, source, channel):
    SUPPRESSED
elif is_quiet_hour(actor):
    QUIET_HOUR_DELAYED
elif is_in_cooldown(dedupe_key):
    skip
else:
    QUEUED
```

## 핵심

**Preference는 정책 계층 중 하나다.** 유일한 정책이 아님.

## Policy Audit

모든 정책 결정은 `runtime_notification_policy_audit`에 기록.
API: `GET /notification-engine/policy-audit/{notification_id}`
