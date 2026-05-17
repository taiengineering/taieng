# Cursor 작업지시서 033: Real Event Runtime Injection

작성일: 2026-05-17
대상: tai-api 레포 (dev 브랜치)
우선순위: P1

---

## 배경

Notification Runtime 완성, Delivery Runtime 준비 완료.
실제 운영 코드에서 `wire_and_emit()` 호출이 없음.
이벤트 발생 지점에 wire_and_emit 삽입 필요.

---

## 절대 규칙

1. **기존 로직 제거 금지** — wire_and_emit을 **추가**하되, 기존 SMS/push 발송 로직은 그대로 유지 (compat 공존)
2. **try/except 필수** — wire_and_emit 실패가 기존 로직을 막으면 안 됨
3. **import는 함수 내부에서** — 순환 import 방지
4. **`services/notification_engine/event_wiring.py`는 dev 브랜치에만 존재** — main에 없으면 import 실패 → except에서 무시

---

## TASK 1 — billing_return (payment_failed / payment_success)

### 대상 파일
```
routers/payment_billing.py
```

### 삽입 위치

`billing_return` 함수 내부에서 **구독 상태 변경 완료 후** (PENDING→ACTIVE 또는 실패 처리 후):

```python
# ── Notification Runtime 연결 (033) ──
try:
    from services.notification_engine.event_wiring import wire_and_emit
    import asyncio
    asyncio.create_task(wire_and_emit(
        event_type="subscription_activated",  # 또는 payment_success
        payload={
            "title": f"구독 활성화: {company_name or ''}",
            "body": f"결제 완료. 구독이 활성화되었습니다.",
            "company_id": str(company_id) if company_id else None,
            "order_id": order_id,
        }
    ))
except Exception as e:
    import logging
    logging.getLogger("notification").warning(f"[NOTIF] wire_and_emit failed: {e}")
```

### 실패 시 코드 (결제 실패 시):

```python
try:
    from services.notification_engine.event_wiring import wire_and_emit
    import asyncio
    asyncio.create_task(wire_and_emit(
        event_type="payment_failed",
        payload={
            "title": "결제 실패",
            "body": f"결제가 실패했습니다. 사유: {result_msg or '알 수 없음'}",
            "company_id": str(company_id) if company_id else None,
            "order_id": order_id,
        }
    ))
except Exception as e:
    import logging
    logging.getLogger("notification").warning(f"[NOTIF] wire_and_emit failed: {e}")
```

### 주의
- `billing_return`은 **동기 함수**일 수 있음 — `asyncio.create_task` 또는 `asyncio.ensure_future` 사용
- 비동기 함수면 `await wire_and_emit(...)` 직접 사용
- 기존 로직 절대 제거 금지

---

## TASK 2 — overdue_checker (schedule_overdue)

### 대상 파일
```
routers/overdue_checker.py
```

### 삽입 위치

미이행 점검 발견 후 SMS/push 발송 직전 또는 직후:

```python
# ── Notification Runtime 연결 (033) ──
try:
    from services.notification_engine.event_wiring import wire_and_emit
    await wire_and_emit(
        event_type="schedule_overdue",
        payload={
            "title": f"점검 미이행: {inspection_name or ''}",
            "body": f"{factory_name or ''} 점검이 예정일을 초과했습니다.",
            "factory_id": str(factory_id) if factory_id else None,
            "company_id": str(company_id) if company_id else None,
            "inspection_id": str(inspection_id) if inspection_id else None,
        }
    )
except Exception as e:
    import logging
    logging.getLogger("notification").warning(f"[NOTIF] schedule_overdue wire failed: {e}")
```

### 주의
- 기존 SMS/push 로직 유지 (compat 공존)
- overdue_checker는 cron에서 호출되므로 async context 확인 필요

---

## TASK 3 — weather_work_stop

### 대상 파일
```
routers/weather_work_stop.py 또는 기상청 연계 파일
```

### 삽입 위치

작업중지 경보 발생 지점:

```python
try:
    from services.notification_engine.event_wiring import wire_and_emit
    await wire_and_emit(
        event_type="weather_work_stop",
        payload={
            "title": f"작업중지 경보: {alert_type or ''}",
            "body": f"{region or ''} 지역 작업중지 경보가 발령되었습니다.",
            "region": region,
            "alert_type": alert_type,
        }
    )
except Exception as e:
    import logging
    logging.getLogger("notification").warning(f"[NOTIF] weather_work_stop wire failed: {e}")
```

---

## TASK 4 — 변수명 확인

각 파일에서 실제 변수명을 확인하고 payload에 적절히 매핑해주세요.
- `company_id`, `factory_id`, `order_id` 등이 실제 코드에서 어떤 변수로 존재하는지
- 문자열 변환 (`str()`) 적용
- None 처리

---

## 확인 방법

1. `git diff` 로 추가된 wire_and_emit 호출 확인
2. 기존 로직이 그대로 유지되는지 확인
3. try/except로 감싸져 있는지 확인
4. dev 브랜치에만 커밋

---

## 성공 기준

| # | 기준 |
|---|---|
| 1 | billing_return에 wire_and_emit 삽입 (성공+실패 모두) |
| 2 | overdue_checker에 wire_and_emit 삽입 |
| 3 | weather_work_stop에 wire_and_emit 삽입 |
| 4 | 기존 SMS/push 로직 유지 (제거 없음) |
| 5 | try/except 감싸기 |
| 6 | dev 브랜치 커밋 |
