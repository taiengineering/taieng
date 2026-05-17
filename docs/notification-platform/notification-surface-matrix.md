# Notification Surface Matrix

작성일: 2026-05-17
범위: Notification Engine · 전달 Surface 전체

---

## Surface Matrix

| Surface | 대상 | Runtime | Feed 연결 | 목적 |
|---|---|---|---|---|
| Feed (IN_APP) | 안전관리자/작업자 | ✅ | ✅ | 운영 확인 |
| Header Bell Popup | 전체 로그인 사용자 | ✅ | ✅ | 빠른 확인 |
| Notification Center | 안전관리자/관리자 | ✅ | ✅ | 상세 조회 |
| Sidebar Badge | 전체 | ✅ | ✅ (unread) | 주의 환기 |
| SMS | 안전관리자/대표 | ✅ | ❌ | 긴급 전달 |
| Telegram | 운영자 | ✅ | ❌ | 실시간 전달 |
| Push (FCM) | 모바일 사용자 | ⬜ Mock | ❌ | 모바일 알림 |
| Email | 관리자 | ⬜ Phase 2 | ❌ | Digest/공지 |
| Toast (Legacy) | 각 페이지 | ❌ | ❌ | 즉시 피드백 |
| Dashboard Banner | 전체 | ❌ | ❌ | 시스템 공지 |
| Announcement | 전체 | ❌ | ❌ | 운영 콘텐츠 |

---

## 요약

| 분류 | 건수 |
|---|---|
| Runtime Active | 5 (Feed, Popup, Center, Badge, SMS, Telegram) |
| Mock/Phase 2 | 2 (Push, Email) |
| Non-Runtime | 3 (Toast, Banner, Announcement) |
