# Notification Feed Concept

작성일: 2026-05-16
상태: Concept Definition (구현 전 단계)

---

## 핵심 공식

```
Runtime Notification + Service Notification = Unified Notification Feed
```

---

## Feed 구성 요소

### 1. Inbox

사용자별 알림 목록. In-App Adapter를 통해 `notifications` 테이블에 저장.

| 요소 | 설명 |
|---|---|
| title | 알림 제목 |
| message | 알림 본문 |
| notification_type | SYSTEM / ALERT / WORKFLOW / SERVICE |
| is_read | 읽음 여부 |
| reference_id | 관련 엔티티 ID |

### 2. Timeline

상태 변화 이력. trace_id 기반 추적.

- Runtime: `/notification-engine/timeline/{trace_id}`
- Workflow: `/workflow/timeline/{workflow_id}`
- Alert: `/workflow/alerts/timeline/{workflow_id}`

### 3. Read State

In-App Adapter가 `is_read` 필드 관리. 추후 `read_at` timestamp 추가 가능.

### 4. Notification Grouping

동일 `event_type` + `source_engine` 기준 그룹화. 현재: dedupe_key로 부분 처리.

### 5. Feed Rendering

Frontend에서 `notifications` 테이블 조회 → 렌더링. 현재: SaaS/Admin에서 JS 직접 fetch.

---

## Runtime → Feed 흐름

```
Any Engine
    ↓
Notification Event (runtime_notification_event)
    ↓
Recipient Resolution
    ↓
Queue (delivery_channel = IN_APP)
    ↓
In-App Adapter
    ↓
notifications 테이블 INSERT
    ↓
Frontend Fetch → Inbox Render
```

---

## 원칙

- Feed는 **Delivery 결과물**이다 (Delivery Layer 이후)
- Feed 내부에서 운영 판단 금지
- Read/ACK는 Feed Layer 책임
