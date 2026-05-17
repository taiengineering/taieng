# Billing Notification Pack

작성일: 2026-05-17
범위: 결제/재무 알림

---

## 원칙

**재무 이벤트.** 결제 실패는 즉시, 성공은 일반 전달.

---

## 이벤트

| event_key | 설명 | audience | channel | severity | digest | quiet bypass |
|---|---|---|---|---|---|---|
| payment_success | 결제 성공 | company_admin | IN_APP | INFO | ✅ | ❌ |
| payment_failed | 결제 실패 | company_admin | SMS+IN_APP | WARNING | ❌ | ✅ |
| invoice_issued | 청구서 발행 | company_admin | IN_APP | INFO | ✅ | ❌ |
| subscription_expiring | 구독 만료 예정 | company_admin | IN_APP | WARNING | ❌ | ❌ |
| subscription_expired | 구독 만료 | company_admin | SMS+IN_APP | CRITICAL | ❌ | ✅ |
| refund_processed | 환불 처리 | company_admin | IN_APP | INFO | ✅ | ❌ |

---

## 규칙

- payment_failed: 즉시 SMS + IN_APP (cooldown 0)
- subscription_expired: CRITICAL — quiet hour bypass
- payment_success, invoice_issued: 일간 digest 가능
