# Notification Control Surface Architecture

작성일: 2026-05-17
범위: Notification Engine · 운영 관리 UI

---

## Control Surface 구성

```
Notification Admin
├─ Dashboard          — 전체 상태 요약 (Health + Metrics)
├─ Runtime Monitor    — Queue/DLQ/Retry/Delayed 실시간
├─ Wiring Manager     — Event→Policy→Audience 매핑 관리
├─ Policy Manager     — 전달 정책 조회/튜닝
├─ Audience Manager   — Audience type 조회
├─ Template Manager   — SMS/Email/Push 템플릿 (Phase 2)
├─ Announcement       — 정적 공지 관리 (Phase 2)
├─ Feed Viewer        — 전체 Feed 조회
├─ Delivery Health    — 채널별 성공률/latency
└─ Digest Monitor     — Digest queue/policy 상태
```

---

## 현재 구현 상태

| Surface | 상태 | API |
|---|---|---|
| Dashboard | ✅ admin notification-center.html Health 위젯 | runtime-summary |
| Runtime Monitor | ✅ 알림센터 Health + Feed | runtime-summary + feed |
| Wiring Manager | ✅ API 조회만 | GET /wirings |
| Policy Manager | ✅ API 조회만 | GET /policies |
| Audience Manager | ⬜ 문서만 | audience_resolver.py |
| Template Manager | ⬜ Phase 2 | 미구현 |
| Announcement | ⬜ Phase 2 | 미구현 |
| Feed Viewer | ✅ 알림센터 Feed 탭 | feed API |
| Delivery Health | ⬜ 부분적 | metrics 테이블 |
| Digest Monitor | ✅ API 조회만 | GET /digest-candidates |

---

## 운영자 접근 경로

| 경로 | Surface |
|---|---|
| admin.taieng.co.kr → 시스템 > 알림센터 | Dashboard + Feed + Health |
| safe.taieng.co.kr → 사이드바 알림센터 | Feed + Timeline + Settings |
| API 직접 | Wiring/Policy/Digest 조회 |
