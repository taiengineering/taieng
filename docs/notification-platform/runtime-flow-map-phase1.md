# Runtime Flow Map — Phase 1

작성일: 2026-05-17
범위: 실제 SaaS Flow → Runtime 연결

---

## payment_failed Flow

```
결제 실패 발생 (KG이니시스 callback)
  → billing_return API
  → wire_and_emit('payment_failed', {company_id, amount, reason})
  → WIRE_PAYMENT_FAILED
  → POLICY_RUNTIME_WARNING (channel=IN_APP, severity=WARNING)
  → Queue → Worker → IN_APP Adapter
  → notifications 테이블 INSERT
  → Feed 표시 + Timeline 기록
```

## approval_requested Flow

```
승인 요청 발생
  → wire_and_emit('approval_requested', {requester, item, company_id})
  → WIRE_APPROVAL_REQUESTED
  → POLICY_WORKFLOW_ALERT (channel=TELEGRAM, severity=WARNING)
  → Queue → Worker → TELEGRAM Adapter
  → Telegram Bot 전달 + Timeline 기록
```

## weather_work_stop Flow

```
기상청 API 작업중지 감지
  → wire_and_emit('weather_work_stop', {region, alert_type})
  → WIRE_WEATHER_ALERT
  → POLICY_RUNTIME_CRITICAL (channel=TELEGRAM, severity=CRITICAL, quiet_bypass=true)
  → Queue → Worker → TELEGRAM Adapter
  → 즉시 전달 (Quiet Hour bypass)
```

---

## Flow 연결 상태

| Flow | Wiring | Policy | Audience | 실제 호출 | 상태 |
|---|---|---|---|---|---|
| payment_failed | ✅ | ✅ | company_admin | ⬜ wire_and_emit 미연결 | **Wiring Ready** |
| approval_requested | ✅ | ✅ | tenant_admin | ⬜ wire_and_emit 미연결 | **Wiring Ready** |
| weather_work_stop | ✅ | ✅ | site_all | ⬜ wire_and_emit 미연결 | **Wiring Ready** |
| subscription_expired | ✅ | ✅ | company_admin | ⬜ | **Wiring Ready** |
| accident_reported | ✅ | ✅ | safety_manager | ⬜ | **Wiring Ready** |
| violation_detected | ✅ | ✅ | safety_manager | ⬜ | **Wiring Ready** |
