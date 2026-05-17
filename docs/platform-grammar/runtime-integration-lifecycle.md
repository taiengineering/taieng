# Runtime Integration Lifecycle

작성일: 2026-05-17
범위: 이벤트 발생 → 전달 완료 전체 흐름

---

## Lifecycle

```
1️⃣ Truth 발생
   External Runtime에서 운영 이벤트 발생
   (e.g. 결제 실패, 점검 초과, 작업중지)

2️⃣ Event Publish
   wire_and_emit(event_type, payload) 호출
   Operational Event Contract 준수

3️⃣ Wiring Resolve
   notification_event_wiring_registry 조회
   event_type → policy_key + audience_key

4️⃣ Policy Resolve
   notification_policy_registry 조회
   channel, severity, cooldown, quiet_hour_bypass

5️⃣ Notification Projection
   severity_snapshot + audience + channel 결정
   Truth 수정 금지 (Snapshot 전용)

6️⃣ Delivery Queue
   runtime_notification_queue INSERT
   status: PENDING

7️⃣ Worker Consume
   1분 cron → PENDING → PROCESSING
   channel_registry 조회 → Adapter 호출

8️⃣ Adapter Delivery
   SMS/Telegram/Push/IN_APP 전달
   (success, error) 반환

9️⃣ Audit & Timeline
   policy_audit + timeline 자동 기록
   DELIVERED / FAILED / RETRY_PENDING

🔁 Retry (max 3)
   FAILED → RETRY_PENDING → 재처리
   3회 실패 → DEADLETTER

📨 Feed Projection
   IN_APP → notifications 테이블 INSERT
   알림센터 Feed 표시
```

---

## 단계별 Owner

| 단계 | Owner |
|---|---|
| 1~2 | External Runtime |
| 3~5 | Notification Intelligence |
| 6~9 | Delivery Runtime |
