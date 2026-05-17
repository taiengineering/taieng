# Real Runtime Flow Report

작성일: 2026-05-17
범위: 실제 연결된 이벤트 흐름

---

## 상태

현재 실제 wire_and_emit() 호출 중인 이벤트: **0건**

Cursor 작업지시서 `2026-05-17_cursor-033-runtime-injection.md` 실행 후 연결 예정:

---

## 예정 Flow (Cursor 삽입 후)

### payment_failed
```
KG이니시스 callback → billing_return
  → 구독 상태 판단 (PENDING 유지 = 실패)
  → wire_and_emit('payment_failed', {company_id, order_id, reason})
  → WIRE_PAYMENT_FAILED → POLICY_RUNTIME_WARNING
  → Queue → Worker → IN_APP Adapter
  → Feed + Timeline + Audit
```

### schedule_overdue
```
cron (overdue_checker) → 미이행 점검 발견
  → wire_and_emit('schedule_overdue', {inspection_id, factory_id})
  → WIRE_SCHEDULE_OVERDUE → POLICY_WORKFLOW_ALERT
  → Queue → Worker → TELEGRAM Adapter
  → Telegram + Timeline + Audit
  (기존 SMS/push도 병행 유지)
```

### weather_work_stop
```
기상청 API 감지 → 작업중지 경보
  → wire_and_emit('weather_work_stop', {region, alert_type})
  → WIRE_WEATHER_ALERT → POLICY_RUNTIME_CRITICAL (quiet bypass)
  → Queue → Worker → TELEGRAM Adapter (즉시)
  → Telegram + Timeline + Audit
```
