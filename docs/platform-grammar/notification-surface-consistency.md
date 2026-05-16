# Notification Surface Consistency

작성일: 2026-05-17
범위: Notification Engine · All Surfaces

---

## 원칙

모든 Surface는 **동일한 Runtime Reality**를 표현해야 한다.

---

## Surface 목록

| Surface | 위치 | Feed Source |
|---|---|---|
| Header Popup | tadmin/site 탑바 | `/notification-inbox/feed?limit=5` |
| Notification Center (Desktop) | tadmin horizontal | `/notification-inbox/feed` |
| Notification Center (Mobile) | site vertical | `/notification-inbox/feed` |
| Admin Notification Center | admin horizontal | `/notification-inbox/feed` |

---

## Feed Contract

모든 Surface에서 동일 필드 사용:

- `notification_id` — 고유 식별자
- `title` — 제목
- `body` — 본문
- `severity` — INFO / WARNING / CRITICAL
- `channel_key` — 채널
- `source_type` — 발생 유형
- `is_read` — 읽음 여부
- `created_at` — 생성 시각
- `trace_id` — 타임라인 추적 ID

---

## Unread Count Contract

- API: `GET /notification-inbox/unread-count`
- 응답: `{status: "success", data: {count: N}}` 또는 `{status: "success", data: N}`
- 클라이언트: `extractCount()` 헬퍼로 두 형태 모두 처리

---

## 일관성 규칙

1. 한 Surface에서 read 처리하면 다른 Surface에서도 반영
2. Badge 갱신 주기는 전 Surface 동일 (30초)
3. Severity 색상 체계 전 Surface 동일
4. Timeline 진입 방식 동일 (trace_id 기반)
