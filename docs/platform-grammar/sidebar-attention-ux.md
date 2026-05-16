# Sidebar Attention UX

작성일: 2026-05-17
범위: Notification Engine · Navigation

---

## 정의

Sidebar Badge는 **Operational Attention Indicator**다.

미읽음 알림이 존재한다는 사실만 전달한다.

---

## 규칙

1. Badge는 숫자(unread count)만 표시
2. 색상: Primary color 단일 (severity 색상 금지)
3. 99+ cap (100 이상은 99+)
4. 0이면 badge 숨김
5. 갱신 주기: 30초 (notification.js와 동기)

---

## Sidebar Badge Slot

```html
<span class="notif-sidebar-badge"></span>
```

menu-tadmin.js 렌더러에 slot 준비. 실시간 연동은 optional.

---

## 금지

- Severity color overload (빨강/주황/파랑 구분 금지)
- Blinking/pulse 애니메이션
- Incident semantics (사고 의미 부여 금지)
- Badge 클릭 시 팝업 (사이드바 badge는 페이지 이동만)
