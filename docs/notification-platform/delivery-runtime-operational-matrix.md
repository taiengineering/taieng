# Delivery Runtime Operational Matrix

작성일: 2026-05-17
범위: 실제 운영 채널 우선순위

---

## 운영 채널 매트릭스

| 이벤트 | Push | SMS | Telegram | IN_APP | 우선 |
|---|---|---|---|---|---|
| weather_work_stop | ✅ | ✅ | ✅ | ✅ | SMS+TELEGRAM |
| accident_reported | ❌ | ✅ | ✅ | ✅ | SMS+TELEGRAM |
| subscription_expired | ❌ | ✅ | ❌ | ✅ | SMS |
| payment_failed | ❌ | ✅ | ❌ | ✅ | SMS |
| schedule_overdue | ✅ | ✅ | ✅ | ✅ | TELEGRAM+Push |
| tbm_attendance | ✅ | ❌ | ❌ | ✅ | Push |
| inspection_failed | ✅ | ❌ | ✅ | ✅ | TELEGRAM |
| equipment_checkin | ✅ | ❌ | ❌ | ✅ | Push |
| education_due | ✅ | ❌ | ❌ | ✅ | Push |
| approval_requested | ✅ | ❌ | ✅ | ✅ | TELEGRAM+Push |
| approval_completed | ❌ | ❌ | ❌ | ✅ | IN_APP |
| member_invited | ❌ | ❌ | ❌ | ✅ | IN_APP |
| schedule_due | ✅ | ❌ | ❌ | ✅ | Push |
| payment_success | ❌ | ❌ | ❌ | ✅ | IN_APP |

---

## 채널 운영 상태

| 채널 | Runtime Adapter | channel_registry | 실운영 |
|---|---|---|---|
| IN_APP | ✅ Active | ✅ enabled | ✅ 작동 중 |
| SMS | ✅ Active | ✅ enabled | ✅ MessageMi 연동 |
| TELEGRAM | ✅ Active | ✅ enabled | ⬜ Bot 대기 |
| PUSH | ✅ Compat v2.0 | ✅ enabled | ⬜ FCM 대기 |
| EMAIL | ❌ 미구현 | ❌ disabled | ❌ Phase 2 |
