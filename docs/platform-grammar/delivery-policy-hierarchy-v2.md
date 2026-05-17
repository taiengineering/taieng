# Delivery Policy Hierarchy v2

작성일: 2026-05-17
범위: Notification Engine · 정책 충돌 해결

---

## 우선순위 (위에서 아래로)

```
1. Permission (역할 기반 접근 제어 — Phase 2)
   ↓
2. Wiring Override (wiring 레벨 cooldown/channel 오버라이드)
   ↓
3. Policy (notification_policy_registry 기본값)
   ↓
4. Preference (사용자 알림 선호 — mute/disabled)
   ↓
5. Quiet Hour (야간 억제)
   ↓
6. Runtime Default (channel_registry 기본값)
```

---

## 충돌 해결 규칙

| 충돌 | 해결 |
|---|---|
| Wiring cooldown vs Policy cooldown | Wiring이 null이면 Policy 사용, 아니면 Wiring 우선 |
| Wiring channel vs Policy channel | Wiring에 override_channel 있으면 우선 |
| Preference mute vs CRITICAL | CRITICAL은 mute 무시 |
| Quiet Hour vs CRITICAL | CRITICAL은 quiet_hour_bypass |
| Preference disabled vs Wiring enabled | Preference disabled 우선 (채널 차단) |

---

## 핵심

정책 충돌 시 상위 계층이 우선. CRITICAL은 모든 억제를 bypass.
