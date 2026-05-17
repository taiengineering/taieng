# Cursor 작업지시서 034: Runtime Actualization

작성일: 2026-05-17
대상: tai-api 레포 (dev 브랜치)
우선순위: P1

---

## 배경

033 Cursor 지시서와 동일 목표. 대형 파일 수정이므로 Cursor로 실행.
wire_and_emit()을 실제 운영 코드에 삽입하되, 기존 로직 제거 없이 compat 공존.

---

## 절대 규칙

1. **기존 로직 제거 금지** — wire_and_emit을 **추가**만
2. **try/except 필수** — 실패 시 기존 로직에 영향 없음
3. **import는 함수 내부에서** — 순환 import 방지
4. **dev 브랜치에만 커밋**

---

## TASK 1 — payment_failed (billing_return)

### 대상
```
routers/payment_billing.py
```

### 삽입 위치
billing_return 함수에서 **결제 성공 시** (PENDING→ACTIVE 변경 후):

```python
# ── Notification Runtime (034) ──
try:
    from services.notification_engine.event_wiring import wire_and_emit
    import asyncio
    asyncio.ensure_future(wire_and_emit(
        event_type="subscription_activated",
        payload={"title": "구독 활성화", "body": f"결제 완료. 구독이 활성화되었습니다.",
                 "company_id": str(company_id) if 'company_id' in dir() else None,
                 "order_id": str(order_id) if 'order_id' in dir() else None}
    ))
except Exception:
    pass
```

**결제 실패 시:**

```python
try:
    from services.notification_engine.event_wiring import wire_and_emit
    import asyncio
    asyncio.ensure_future(wire_and_emit(
        event_type="payment_failed",
        payload={"title": "결제 실패", "body": f"결제가 실패했습니다.",
                 "company_id": str(company_id) if 'company_id' in dir() else None}
    ))
except Exception:
    pass
```

### 주의
- 변수명은 실제 코드에서 확인 후 매핑
- billing_return이 동기 함수면 asyncio.ensure_future 사용

---

## TASK 2 — schedule_overdue (overdue_checker)

### 대상
```
routers/overdue_checker.py
```

### 삽입 위치
미이행 점검 발견 후 SMS/push 발송 직전 또는 직후:

```python
try:
    from services.notification_engine.event_wiring import wire_and_emit
    await wire_and_emit(
        event_type="schedule_overdue",
        payload={"title": f"점검 미이행: {inspection_name or ''}",
                 "body": f"점검이 예정일을 초과했습니다.",
                 "factory_id": str(factory_id) if factory_id else None,
                 "company_id": str(company_id) if company_id else None}
    )
except Exception:
    pass
```

---

## TASK 3 — weather_work_stop

### 대상
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
        payload={"title": f"작업중지 경보: {alert_type or ''}",
                 "body": f"{region or ''} 지역 작업중지 경보가 발령되었습니다.",
                 "region": region, "alert_type": alert_type}
    )
except Exception:
    pass
```

---

## TASK 4 — approval_requested

approval 워크플로우가 구현되면 해당 지점에 삽입.
현재는 **Wiring Ready 상태만 유지.**

---

## 확인 방법

1. `git diff`로 추가된 wire_and_emit 확인
2. 기존 로직 제거 없음 확인
3. try/except 감싸기 확인
4. dev 브랜치 커밋

---

## 성공 기준

| # | 기준 |
|---|---|
| 1 | billing_return에 wire_and_emit 삽입 (성공+실패) |
| 2 | overdue_checker에 wire_and_emit 삽입 |
| 3 | weather_work_stop에 wire_and_emit 삽입 |
| 4 | 기존 로직 유지 |
| 5 | try/except 감싸기 |
| 6 | dev 브랜치 커밋 |
