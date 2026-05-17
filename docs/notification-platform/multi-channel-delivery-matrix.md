# Multi-Channel Delivery Matrix

작성일: 2026-05-17
범위: 이벤트별 채널 우선순위 (9채널)

---

## Matrix

| 이벤트 | Primary | Secondary | Tertiary | Feed |
|---|---|---|---|---|
| payment_failed | ALIMTALK | SMS | IN_APP | ✅ |
| payment_success | ALIMTALK | IN_APP | — | ✅ |
| subscription_expired | ALIMTALK | SMS | IN_APP | ✅ |
| subscription_activated | IN_APP | — | — | ✅ |
| weather_work_stop | TELEGRAM | PUSH | SMS | ✅ |
| accident_reported | SMS | TELEGRAM | IN_APP | ✅ |
| schedule_overdue | TELEGRAM | PUSH | IN_APP | ✅ |
| inspection_failed | TELEGRAM | IN_APP | — | ✅ |
| approval_requested | TELEGRAM | SLACK | IN_APP | ✅ |
| workflow_stuck | TELEGRAM | SLACK | IN_APP | ✅ |
| backup_failed | TELEGRAM | SLACK | EMAIL_GMAIL | ✅ |
| service_degraded | TELEGRAM | SLACK | EMAIL_GMAIL | ✅ |
| education_due | PUSH | IN_APP | — | ✅ |
| member_invited | IN_APP | EMAIL_GMAIL | — | ✅ |

---

## 채널 우선순위 원칙

1. **CRITICAL**: TELEGRAM + SMS (이중 전달)
2. **비즈 공식**: ALIMTALK (결제/계약/구독)
3. **운영 실시간**: TELEGRAM
4. **운영 협업**: SLACK
5. **공식 문서**: EMAIL_GMAIL
6. **현장 작업자**: PUSH
7. **기본**: IN_APP (Feed)
