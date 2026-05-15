# Decision Log — Notification vs Alert

작성일: 2026-05-15

## 결정

Alert와 Notification을 분리.

---

## 이유

초기에는:

```text
Event → Telegram
```

구조였음.

하지만 플랫폼 확장 시:

- alert fatigue
- notification chaos
- channel duplication
- dedupe conflict

발생 가능.

따라서:

```text
Alert = 운영 중요도 승격
Notification = 전달
```

로 분리.

---

## 핵심 철학

```text
Event ≠ Alert
Alert ≠ Notification
```

---

## 결과

Notification Engine을 플랫폼 공통 Runtime으로 승격.
