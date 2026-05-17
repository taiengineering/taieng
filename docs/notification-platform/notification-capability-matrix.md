# Notification Capability Matrix

작성일: 2026-05-17
범위: Notification Engine Phase 1

---

## Capability 현황

| Capability | 상태 | 비고 |
|---|---|---|
| Queue Runtime | ✅ Production | PENDING/PROCESSING/DELIVERED/FAILED |
| Retry Runtime | ✅ Production | max 3회, exponential backoff |
| Quiet Hour | ✅ Production | DELAYED → RESUMED |
| CRITICAL Bypass | ✅ Production | Quiet Hour 무시 |
| Mute/Disabled Suppression | ✅ Production | Policy Audit 기록 |
| Feed (In-App) | ✅ Production | notifications 테이블 |
| Timeline | ✅ Production | trace_id 기반 step 추적 |
| Preference | ✅ Production | source_type × channel_key |
| Policy Audit | ✅ Production | 모든 정책 결정 기록 |
| Mobile Surface | ✅ Production | compact health + fullscreen timeline |
| Push Adapter | ⬜ Mock | push.py + channel registry (enabled=false) |
| Scheduler Automation | ✅ Production | queue_worker 1분 + metrics 10분 |
| Feed Grouping | ✅ Frontend | 날짜/유형/중요도/채널 |
| Sidebar Badge | ✅ Production | slot + updateBadge 동기화 |
| Popup Read Flow | ✅ Production | POST read → center 이동 |
| Admin Bell | ✅ Production | ensureBell 자동 주입 |
| E2E Verification | ✅ 7 시나리오 | 86.8% (33/38) |
| Runtime Consistency | ✅ 6-Layer | A등급 93/100 |

---

## Platform Readiness

**완료: 16/18 = 89%**

미완료:
1. Push Adapter 실제 FCM 연동 (Phase 2)
2. E2E 100% 달성 (5건 미통과 — WebSocket/Email 관련)
