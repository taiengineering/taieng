# Operational Navigation Completion

작성일: 2026-05-17
범위: Notification Engine · Navigation Integration

---

## 현재 연결된 운영 흐름

```
Sidebar / Top Nav
  ↓
Notification Center
  ↓
Feed (필터: 그룹/severity/채널/unread)
  ↓
Timeline Modal (trace_id 기반)
  ↓
Read 처리 (POST /notification-inbox/{id}/read)
```

---

## Surface별 Navigation 상태

| Surface | Entry Point | Status |
|---|---|---|
| tadmin 사이드바 | menu-tadmin.js `알림센터` | ✅ 완료 |
| tadmin 헤더 벨 | nav-tadmin.js `#notif-bell` → 팝업 → 알림센터 | ✅ 완료 |
| site 사이드바 | menu-tadmin.js `알림센터` | ✅ 완료 |
| site 헤더 벨 | notification.js 팝업 → 알림센터 | ✅ 완료 |
| admin 탑바 메뉴 | menu-nav.js `시스템 > 알림센터` | ✅ 완료 |
| admin 헤더 벨 | 미연동 (notification.js 없음) | ⬜ PENDING |

---

## Popup Read Flow 상태

| Surface | Click → Read | Status |
|---|---|---|
| tadmin popup | href 직접 이동 (read 미호출) | ⬜ PENDING |
| site popup | href 직접 이동 (read 미호출) | ⬜ PENDING |
| 알림센터 Feed | onFeedClick → POST read → loadFeed | ✅ 완료 |

---

## Sidebar Badge 상태

| Surface | Badge Slot | 실시간 연동 | Status |
|---|---|---|---|
| tadmin 사이드바 | 미준비 | 미연동 | ⬜ PENDING |
| site 사이드바 | 미준비 | 미연동 | ⬜ PENDING |
| 헤더 벨 badge | `#notif-badge` | 30초/60초 갱신 | ✅ 완료 |

---

## Operational Surface Completion

| 항목 | 완료 | 전체 |
|---|---|---|
| Navigation Entry | 5 | 6 |
| Popup Read Flow | 1 | 3 |
| Sidebar Badge | 1 | 3 |
| Feed Consistency | 4 | 4 |
| Timeline Access | 4 | 4 |
| Mobile Surface | 1 | 1 |
| Platform Grammar 문서 | 7 | 7 |

**전체 완료율: 23/28 = 82%**

---

## 미완료 항목 (다음 작업)

1. admin 헤더 벨 → notification.js 연동
2. tadmin/site popup click → read API 호출
3. tadmin/site sidebar badge slot 준비
4. tadmin notification-center.html extractCount 버그 수정
5. site notification-center.html 모바일 최적화 (compact health widget)
