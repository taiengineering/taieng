# Mobile Notification Surface (Phase 2 준비)

작성일: 2026-05-16

---

## 모바일 중요 요소

| 요소 | 중요도 | 이유 |
|---|---|---|
| Unread Attention | ⭐⭐⭐ | 작은 화면에서 Badge가 유일한 신호 |
| Timeline Readability | ⭐⭐ | 작은 화면에서 스크롤 부담 |
| Quiet Hour Visibility | ⭐⭐ | 왜 늦었는지 즉시 확인 |
| Grouping Readability | ⭐ | 작은 화면에서 flat list가 더 적합 |

## 대상 레포

`site/full-version/html/vertical-menu-template-no-customizer/`

## 현재 상태

미구현. notification-center.html은 반응형 CSS (max-width:960px)로 제한적 모바일 지원.

## Phase 2 작업

1. vertical-menu 레포에 notification-center.html 복제
2. 모바일 전용 레이아웃 최적화
3. PWA Push Notification 연동
