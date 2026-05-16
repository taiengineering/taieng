# Notification Entry Flow

작성일: 2026-05-16

---

## 진입 흐름

```
Header Bell (모든 페이지)
  │
  ├─ 실시간 Unread Badge (60초 주기)
  ├─ 클릭 → 팝업 (Feed 5개 미리보기)
  └─ "알림센터 열기" → notification-center.html
         │
         ├─ Health Widget (unread/delayed/retry/dlq)
         ├─ Inbox Feed (피드 탭)
         │    ├─ Severity Badge (INFO/WARNING/CRITICAL)
         │    ├─ Channel Badge (TELEGRAM/SMS/IN_APP)
         │    ├─ source_type 표시
         │    ├─ Grouping (UI only: 유형/중요도/채널)
         │    └─ 클릭 → Read 처리 + Timeline Modal
         ├─ Timeline Modal (trace_id 기반)
         │    ├─ EVENT → QUEUE → PROCESSING → DELIVERED
         │    └─ Policy Events (MUTE/QH/CRITICAL_BYPASS)
         └─ Notification Settings (설정 탭)
              ├─ 채널 on/off
              ├─ 음소거
              └─ 조용한 시간 범위
```

## Legacy 경로

- `notification-list.html` → `notification-center.html` 자동 redirect
- notification.js v2.0: 모든 페이지의 알림 벨 → 알림센터 연결

## 핵심

**Notification은 운영 Attention Flow다.**
