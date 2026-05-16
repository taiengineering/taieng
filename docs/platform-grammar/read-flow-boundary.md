# Read Flow Boundary

작성일: 2026-05-17
범위: Notification Engine · Read Flow

---

## 정의

READ는 **확인(Acknowledgement)**이지 **조치 완료(ACK)**가 아니다.

---

## Read Flow

```
Popup Click
  → POST /notification-inbox/{id}/read
  → Badge Count 갱신
  → notification-center.html 이동
  → Timeline 진입 (trace_id 존재 시)
```

---

## 규칙

1. Popup 알림 클릭 시 반드시 read API 호출 후 이동
2. 알림센터 Feed 카드 클릭 시 동일 read 처리
3. Read 처리 실패 시 이동은 계속 진행 (best-effort)
4. Read 상태는 UI에서 즉시 반영 (unread border 제거)
5. 전체 읽음(read-all) 액션은 알림센터 내에서만 제공

---

## 금지

- Read를 조치 완료로 해석하는 것
- Read 상태로 severity를 변경하는 것
- Read 처리를 자동(timer 기반)으로 수행하는 것
