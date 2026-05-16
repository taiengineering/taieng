# Notification Navigation Boundary

작성일: 2026-05-16

---

## 정의

Notification Navigation은 **Operational Entry Flow**이다.

**아닌 것:** Queue Admin Navigation이 아님.

## 허용

| 허용 | 금지 |
|---|---|
| Feed 조회 | Queue mutation |
| Timeline 조회 | Runtime control |
| Read/Unread 전환 | Retry trigger |
| Preference 설정 | DLQ action |
| Health 조회 | Incident 판단 |
| 알림센터 이동 | Governance 판단 |

## 진입점

| 진입점 | 동작 |
|---|---|
| Header Bell | 팝업 → 알림센터 |
| notification-list.html | redirect → notification-center.html |
| worker-home.html | 알림 링크 (기존) |
