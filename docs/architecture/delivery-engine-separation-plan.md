# Delivery Engine Separation Plan

작성일: 2026-05-17
범위: 미래 Delivery 엔진 분리 방향

---

## 현재: 단일 Runtime

```
services/notification_engine/
  ├─ event_intake.py       ← Notification
  ├─ recipient_resolver.py ← Notification
  ├─ queue_manager.py      ← Delivery
  ├─ worker.py             ← Delivery
  ├─ pipeline.py           ← Bridge
  ├─ retry_policy.py       ← Delivery
  ├─ adapters/             ← Delivery
  ├─ event_wiring.py       ← Notification
  ├─ audience_resolver.py  ← Notification
  └─ digest_runtime.py     ← Notification
```

---

## 향후: 논리 분리 (Phase 2)

```
services/notification_engine/
  ├─ notification/          ← 판단 영역
  │   ├─ event_intake.py
  │   ├─ recipient_resolver.py
  │   ├─ event_wiring.py
  │   ├─ audience_resolver.py
  │   └─ digest_runtime.py
  │
  ├─ delivery/              ← 실행 영역
  │   ├─ queue_manager.py
  │   ├─ worker.py
  │   ├─ retry_policy.py
  │   └─ adapters/
  │
  └─ pipeline.py            ← Bridge
```

---

## 물리 분리 (Phase 3, 선택적)

```
services/notification_runtime/   ← 판단
services/delivery_runtime/       ← 실행
services/channel_adapters/       ← 채널
```

---

## 현재 단계: 물리 분리 금지

논리적 역할 구분만 정의. 파일 이동/리팩토링 금지.
