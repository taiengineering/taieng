# Feed Attention Hierarchy

작성일: 2026-05-17
범위: Notification Engine · Feed UX

---

## 우선순위

1. **Unread CRITICAL** — 즉시 확인 필요
2. **Unread WARNING** — 주의 필요
3. **Unread INFO** — 일반 알림
4. **Delayed** (QUIET_HOUR_DELAYED) — 지연 중
5. **Read** — 확인 완료

---

## 핵심 원칙

Unread Attention ≠ Incident Priority

알림의 읽지 않음 상태는 운영자의 **주의 대상**이지,
사고의 **심각도**가 아니다.

---

## 시각적 구분

| 상태 | 좌측 border | 배경 |
|---|---|---|
| Unread CRITICAL | `#dc3545` red | `#fff5f5` |
| Unread WARNING | `#fd7e14` orange | `#fff8f0` |
| Unread INFO | `#0dcaf0` cyan | `#f0fbff` |
| Delayed | `#f59e0b` amber | `#fef3c7` |
| Read | transparent | transparent |

---

## 금지

- Unread 상태로 인시던트 우선순위 판단
- Severity로 읽음 상태 자동 변경
- Unread count로 위험 수준 판단
