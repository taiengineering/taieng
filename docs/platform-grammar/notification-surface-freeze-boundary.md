# Notification Surface Freeze Boundary

작성일: 2026-05-16
상태: Phase 1 Surface Freeze Active

---

## Freeze 대상

| 영역 | 설명 | Freeze 이유 |
|---|---|---|
| **Header Bell Grammar** | `#notif-bell` + `#notif-badge` + 팝업 | 모든 페이지에서 사용 |
| **Badge Grammar** | unread count, 60s refresh, 99+ 상한 | 전체 UX 의존 |
| **Feed Entry Grammar** | severity/channel/source badge | Feed UX Contract |
| **Timeline Entry Flow** | trace_id → Timeline Modal | Trace Integrity |
| **Notification Center Nav** | notification-center.html 경로 | Legacy redirect 의존 |

## 변경 가능

| 영역 | 조건 |
|---|---|
| 팝업 Feed 수 | 기본 5개 → 조정 가능 |
| Badge 색상 | 기존 색상 유지 |
| 신규 진입점 | 추가 가능 |
| 모바일 Surface | Phase 2 신규 |

## 핵심

**Operational UX를 안정화한 상태에서만 확장한다.**
