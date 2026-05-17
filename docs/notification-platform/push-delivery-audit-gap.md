# Push Delivery Audit Gap

작성일: 2026-05-17
범위: 기존 Push에서 부족한 운영 기능

---

## Gap 분석

| 항목 | 현재 상태 | Runtime 연결 시 |
|---|---|---|
| Delivery Audit | ❌ 없음 (일부 push_sent_at만) | ✅ runtime_notification_policy_audit 자동 |
| Timeline | ❌ 없음 | ✅ runtime_notification_timeline 자동 |
| Retry | ❌ 없음 (실패 시 예외만) | ✅ Worker retry 3회 + DLQ |
| Deadletter | ❌ 없음 | ✅ runtime_notification_deadletter |
| Read State | ❌ 없음 (Push는 read 추적 불가) | ⬜ Push 채널 특성상 불가 |
| Delivery Metrics | ❌ 없음 | ✅ runtime_notification_metrics 자동 |
| Quiet Hour | ❌ 없음 | ✅ Queue QUIET_HOUR_DELAYED |
| Mute/Preference | ❌ 없음 | ✅ Policy check + preference |
| Token Refresh | ❌ 없음 | ⬜ 별도 구현 필요 |
| Token Invalidation | ❌ 없음 | ⬜ FCM 에러 코드 기반 정리 필요 |

---

## Gap 심각도

| 심각도 | Gap | 해결 방법 |
|---|---|---|
| CRITICAL | Retry 없음 | Runtime 연결로 자동 해결 |
| HIGH | Audit/Timeline 없음 | Runtime 연결로 자동 해결 |
| MEDIUM | Token refresh 없음 | 별도 구현 필요 |
| LOW | Read state 불가 | Push 채널 특성 (해결 불필요) |

---

## 핵심

**Runtime 연결만으로 CRITICAL/HIGH gap 전부 해결.** Token 관리만 별도.
