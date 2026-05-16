# Operational Navigation Completion

작성일: 2026-05-17
범위: Notification Engine · Navigation Integration
최종 업데이트: 2026-05-17 (Cursor 018 커밋 `cf74cadd` 반영)

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
| tadmin 사이드바 | menu-tadmin.js `알림센터` + `.notif-sidebar-badge` slot | ✅ 완료 |
| tadmin 헤더 벨 | nav-tadmin.js `#notif-bell` → 팝업 → read → 알림센터 | ✅ 완료 |
| site 사이드바 | menu-tadmin.js `알림센터` + `.notif-sidebar-badge` slot | ✅ 완료 |
| site 헤더 벨 | notification.js 팝업 → read → 알림센터 | ✅ 완료 |
| admin 탑바 메뉴 | menu-nav.js `시스템 > 알림센터` | ✅ 완료 |
| admin 헤더 벨 | 미연동 (notification.js 없음) | ⬜ PENDING |

---

## Popup Read Flow 상태

| Surface | Click → Read | Status |
|---|---|---|
| tadmin popup | `data-notif-id` → POST read → center 이동 | ✅ 완료 (`cf74cadd`) |
| site popup | `data-notif-id` → POST read → center 이동 | ✅ 완료 (`cf74cadd`) |
| 알림센터 Feed | onFeedClick → POST read → loadFeed | ✅ 완료 |

---

## Sidebar Badge 상태

| Surface | Badge Slot | 실시간 연동 | Status |
|---|---|---|---|
| tadmin 사이드바 | `.notif-sidebar-badge` ✅ | updateBadge 동기화 | ✅ 완료 (`cf74cadd`) |
| site 사이드바 | `.notif-sidebar-badge` ✅ | updateBadge 동기화 | ✅ 완료 (`cf74cadd`) |
| 헤더 벨 badge | `#notif-badge` | 30초 갱신 | ✅ 완료 |

---

## extractCount 버그 수정 상태

| 파일 | 수정 | Status |
|---|---|---|
| admin notification-center.html | `extractCount()` 헬퍼 | ✅ 완료 (`e576444b`) |
| tadmin notification-center.html | `extractCount()` 헬퍼 | ✅ 완료 (`cf74cadd`) |
| tadmin notification.js | `extractCount()` + 30초 refresh | ✅ 완료 (`cf74cadd`) |
| site notification.js | `extractCount()` + 30초 refresh | ✅ 완료 (`cf74cadd`) |

---

## 모바일 최적화 상태

| 항목 | Status |
|---|---|
| site notification-center.html inbox 교체 | ✅ 완료 (`cf74cadd`) |
| Health compact mode | ✅ 완료 |
| Feed 2줄 말줄임 | ✅ 완료 |
| Timeline 모바일 전체화면 | ✅ 완료 |
| worker-home 뒤로가기 | ✅ 완료 |

---

## Operational Surface Completion

| 항목 | 완료 | 전체 |
|---|---|---|
| Navigation Entry | 5 | 6 |
| Popup Read Flow | 3 | 3 |
| Sidebar Badge | 3 | 3 |
| Feed Consistency | 4 | 4 |
| Timeline Access | 4 | 4 |
| Mobile Surface | 1 | 1 |
| extractCount 수정 | 4 | 4 |
| Platform Grammar 문서 | 7 | 7 |

**전체 완료율: 31/32 = 97%**

---

## 미완료 항목

1. admin 헤더 벨 → notification.js 연동 (admin/ 경로에 notification.js 미존재)
