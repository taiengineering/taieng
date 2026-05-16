# Inbox API Boundary

작성일: 2026-05-16

---

## 정의

**Inbox API는 Communication Surface다.**

알림의 표시/읽음 상태만 담당한다.

## API 목록

| API | 목적 |
|---|---|
| `GET /notification-inbox/feed` | Unified Feed 조회 |
| `GET /notification-inbox/unread-count` | Unread 건수 |
| `POST /notification-inbox/{id}/read` | Read 상태 |
| `POST /notification-inbox/{id}/unread` | Unread 복구 |
| `GET /notification-inbox/timeline/{trace_id}` | Feed Timeline |

## 금지 사항

Inbox API 내부에서 아래 절대 금지:

- Incident 생성/수정
- Alert 생성/수정
- Severity 재계산
- Workflow 상태 변경
- Governance 계산
- SLA 계산
- 사용자 권한 변경

## 관계

| 영역 | Inbox API와의 관계 |
|---|---|
| Alert Layer | Inbox는 Alert을 표시만 함. 수정 금지 |
| Notification Engine | Inbox는 전달 결과를 조회만 함 |
| Workflow Engine | Inbox는 Workflow 상태를 변경하지 않음 |
| Identity Core | Inbox는 user_id로 필터만 함 |
