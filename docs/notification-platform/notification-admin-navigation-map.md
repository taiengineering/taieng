# Notification Admin Navigation Map

작성일: 2026-05-17
범위: Notification Engine · 운영자 네비게이션

---

## 운영자 Navigation

```
Notification Admin
├─ 대시보드
│   ├─ Health 위젯 (Unread/Delayed/Retry/DLQ/상태)
│   └─ 일간 발송 통계
├─ Runtime Health
│   ├─ Queue Depth
│   ├─ Delivery Latency
│   └─ DLQ 현황
├─ Feed
│   ├─ 전체 Feed 조회
│   ├─ 날짜별 그룹핑
│   └─ Timeline 모달
├─ Policies
│   ├─ 정책 목록
│   └─ 정책 상세
├─ Wiring
│   ├─ Wiring 목록
│   ├─ Wiring 테스트
│   └─ 새 Wiring 등록 (Phase 2)
├─ Templates (Phase 2)
│   ├─ SMS 템플릿
│   ├─ Email 템플릿
│   └─ Push 템플릿
├─ Announcements (Phase 2)
│   ├─ 공지 작성
│   └─ 공지 내역
├─ Digest
│   ├─ Digest 정책
│   └─ Digest 후보 큐
└─ Delivery Logs
    ├─ 채널별 성공률
    └─ 실패 로그
```

---

## 현재 구현 상태

| 메뉴 | 상태 |
|---|---|
| 대시보드 | ✅ Health 위젯 |
| Feed | ✅ 알림센터 |
| Wiring | ✅ API 조회 |
| Policies | ✅ API 조회 |
| Digest | ✅ API 조회 |
| Templates | ⬜ Phase 2 |
| Announcements | ⬜ Phase 2 |
| Delivery Logs | ⬜ Phase 2 |
