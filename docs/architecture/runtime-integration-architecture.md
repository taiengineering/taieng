# Runtime Integration Architecture

작성일: 2026-05-17
범위: 외부 Runtime 연결 구조

---

## 구조

```
┌───────────────────────────────┐
│  External Runtimes           │
│  (Control/Workflow/Billing/  │
│   Safety/ERP/Mobile)         │
└───────────────┬───────────────┘
                │
    Operational Event Contract
    (event_type + severity + payload)
                │
┌───────────────┼───────────────┐
│  Notification Intelligence   │
│  (Wiring → Policy → Audience │
│   → Projection)              │
└───────────────┬───────────────┘
                │
┌───────────────┼───────────────┐
│  Delivery Runtime            │
│  (Queue → Worker → Adapter   │
│   → Retry → Audit)           │
└───────────────┬───────────────┘
                │
┌───────────────┼───────────────┐
│  External Channels           │
│  (SMS/Telegram/Push/IN_APP)  │
└───────────────────────────────┘
```

---

## 연결 가능 대상

| Runtime | 연결 방식 | 상태 |
|---|---|---|
| Control Runtime (Watch Engine) | wire_and_emit 직접 | ✅ Wiring Ready |
| Workflow Runtime | wire_and_emit 직접 | ✅ Wiring Ready |
| Billing Runtime | wire_and_emit 직접 | ✅ 코드 삽입 완료 (dev) |
| Safety Runtime | wire_and_emit 직접 | ✅ 코드 삽입 완료 (dev) |
| ERP | REST API → wire_and_emit | ⬜ Phase 2 |
| Mobile Backend | wire_and_emit 직접 | ✅ Push Adapter Compat |
| External SaaS | Webhook → wire_and_emit | ⬜ Phase 3 |
