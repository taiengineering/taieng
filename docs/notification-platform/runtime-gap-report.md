# Runtime Gap Report

작성일: 2026-05-16
상태: Phase 1 완료 시점

---

## Gap 목록

| Gap | 영향 | 우선순위 | 해결 방향 |
|---|---|---|---|
| SMS external delivery 검증 부재 | 발송 성공 확인 불가 | P2 | MessageMi callback 연동 |
| Worker Cron 자동화 미완료 | Queue 수동 처리 필요 | **P1** | scheduler.py에 1분 주기 등록 |
| Metrics Cron 자동화 미완료 | 지표 수동 수집 | P2 | scheduler.py에 10분 주기 등록 |
| Preference 캐시 레이어 | 매 Queue 생성마다 DB 조회 | P2 | 인메모리 / Redis 캐시 |
| Feed grouping 미구현 | flat list만 제공 | P3 | Feed Service Phase 2 |
| Edge Function SMS ↔ MessageMi 이중 경로 | 혼란 가능 | P2 | MessageMi 단일화 |
| Push(FCM) Adapter 미구현 | overdue FCM 전환 불가 | P2 | adapters/push.py |
| Email Adapter 미구현 | 이메일 채널 없음 | P3 | adapters/email.py |
| Slack Adapter 미구현 | Slack webhook 직접 유지 | P3 | adapters/slack.py |
| Multi-timezone 미지원 | KST 단일 | P3 | Tenant locale 연동 |
| Permission Layer 미구현 | Preference만 존재 | P3 | Identity Core 연동 |
| Frontend 알림 센터 UI | API만 존재 | P2 | Inbox API 연동 |
| notifications.py Legacy 공존 | 이름 충돌 가능 | P3 | Phase 3 제거 |
| runtime_compat.py ↔ compatibility/compat_send.py 중복 | 두 경로 공존 | P2 | runtime_compat.py로 통일 |
