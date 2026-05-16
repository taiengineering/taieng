# Notification Surface Freeze Boundary

작성일: 2026-05-17
범위: Notification Engine · Phase 1 Surface Freeze

---

## Freeze 대상

Phase 1에서 정의된 Surface 범위를 고정한다.

---

## 고정된 Surface

1. Header Bell Popup — Feed 5건 + Unread Badge + 알림센터 링크
2. Notification Center — Feed/Timeline/Settings/Health 4탭
3. Mobile Notification Center — 동일 기능 compact

---

## Phase 1 종료 시점 이후 금지

- 새 Surface 추가 (Slack bot, Email digest 등)
- Feed 구조 변경 (필드 추가/제거)
- Timeline step 추가
- Health 위젯 지표 변경
- Queue/Retry/DLQ UI

---

## Phase 2 진입 조건

1. Operational Navigation Completion 100%
2. 모든 Surface에서 Read Flow 정상 동작
3. Sidebar Badge Slot 연동 완료
4. 모바일 최적화 검증 완료
