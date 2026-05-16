# Mobile Notification Boundary

작성일: 2026-05-17
범위: Notification Engine · Mobile Surface

---

## 정의

모바일 Notification Surface는 **Operational Snapshot Surface**다.

운영자가 현장에서 빠르게 알림 상태를 확인하는 용도.

---

## 허용

- Feed 목록 조회
- Feed 읽음 처리
- Timeline 모달 조회
- Unread count badge
- Health 위젯 (compact mode)
- 알림 설정 조회/토글

---

## 금지

- Queue Control (큐 상태 변경)
- Retry Action (재시도 트리거)
- DLQ Control (격리 해제)
- Incident Mutation
- Runtime Grammar 변경
- Admin 전용 기능
