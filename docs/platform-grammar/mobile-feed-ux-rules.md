# Mobile Feed UX Rules

작성일: 2026-05-17
범위: Notification Engine · Mobile Surface

---

## 원칙

모바일 Notification Surface는 **빠른 운영 확인 Surface**다.

---

## 우선순위

1. **Unread Visibility** — 읽지 않은 알림이 즉시 식별 가능해야 한다. 좌측 border + 배경색 구분.
2. **Severity Readability** — CRITICAL/WARNING/INFO 뱃지가 터치 타겟 내에서 읽힘.
3. **Timeline Readability** — 타임라인 모달이 모바일 full-height로 열림. 스크롤 가능.
4. **Quiet Hour Visibility** — Quiet Hour 상태가 Settings 탭에서 즉시 확인됨.
5. **Touch Interaction** — Feed 카드 최소 높이 48px. 터치 타겟 44×44 이상.

---

## 금지

- 모바일에서 Queue Admin UI 표시 금지
- Retry/DLQ 액션 버튼 금지
- 복잡한 필터 UI (모바일에선 unread_only 토글만)
- 가로 스크롤 테이블

---

## Feed Card 모바일 레이아웃

```
┌─────────────────────────────┐
│ [SEV] [CH]      title  time │
│ body text (max 2 lines)     │
└─────────────────────────────┘
```

- 본문 2줄 말줄임
- trace_id 숨김 (터치 시 timeline 진입)
- 시간 상대 표시 (방금 전, 3분 전)
