# Wiring/Policy Governance UX

작성일: 2026-05-17
범위: Notification Engine · 운영자 가시성

---

## 핵심

**"왜 이 알림이 발송되었는가"** 추적 가능해야 한다.

---

## 운영자가 반드시 볼 수 있어야 하는 것

| 항목 | 위치 |
|---|---|
| Event Source | Wiring Viewer — source_engine |
| Audience | Wiring Viewer — audience_key |
| Policy | Wiring Viewer — notification_policy_key |
| Severity | Policy Viewer — default_severity |
| Channel | Policy Viewer — default_channel |
| Cooldown | Policy Viewer — cooldown_seconds |
| Digest | Wiring Viewer — digest_enabled |
| Quiet Hour Bypass | Policy Viewer — quiet_hour_bypass |

---

## 추적 플로우

```
"이 SMS가 왜 발송되었지?"
  → Feed 카드 클릭 → trace_id
  → Timeline 모달 → EVENT → QUEUE → DELIVERED
  → Wiring Viewer → event_type → policy_key
  → Policy Viewer → channel=SMS, severity=CRITICAL
```

---

## 현재 구현 상태

| 기능 | 상태 |
|---|---|
| Wiring 조회 | ✅ notification-admin.html Wiring 탭 |
| Policy 조회 | ✅ notification-admin.html Policy 탭 |
| Timeline 추적 | ✅ notification-center.html 모달 |
| Wiring 편집 | ⬜ Phase 2 |
| Policy 편집 | ⬜ Phase 2 |
