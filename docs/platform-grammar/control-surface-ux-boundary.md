# Control Surface UX Boundary

작성일: 2026-05-17
범위: Notification Engine · 관리 UI 경계

---

## 정의

Control Surface는 **운영 제어 UI**다. Feed UX와 다른 목적.

---

## 구분

| 항목 | Control Surface | Feed UX |
|---|---|---|
| 목적 | Runtime 관리/관찰 | 사용자 알림 확인 |
| 대상 | 운영자 (admin) | 안전관리자/작업자 |
| UI 스타일 | 테이블/패널 중심 | 카드/타임라인 중심 |
| 데이터 | Wiring/Policy/Queue/DLQ | Feed/Unread/Timeline |
| 액션 | 조회 + enable/disable | 읽음 + 설정 |

---

## Control Surface 페이지

| 페이지 | 목적 |
|---|---|
| notification-admin.html | Runtime/Wiring/Policy/Delivery/Legacy 관리 |
| notification-center.html | 사용자 Feed/Timeline/Settings |

---

## 금지

- 사용자형 카드 UX (관리 페이지에서)
- 마케팅형 디자인
- Runtime mutation UI (직접 큐 변경)
- 드래그&드롭 우선순위 변경
