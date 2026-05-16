# Notification UX Stability Report

작성일: 2026-05-17
범위: Notification Engine Phase 1 · UX 안정성 평가

---

## 평가 항목

| 항목 | 상태 | 점수 |
|---|---|---|
| Feed Readability | 2줄 ellipsis + severity badge + 상대시간 | 9/10 |
| Attention Flow | unread → severity → read 계층 구분 | 8/10 |
| Timeline Readability | trace_id 기반 step 추적 + 모바일 fullscreen | 9/10 |
| Mobile Usability | compact health + 2줄 feed + fullscreen timeline | 8/10 |
| Badge Consistency | extractCount 버그 수정 + 30초 갱신 + 3 Surface 동기 | 9/10 |
| Navigation Consistency | 6/6 entry point 연결 (admin 벨 자동주입 포함) | 10/10 |

---

## UX Stability Score

**53/60 = 88% — A 등급**

---

## 발견된 UX Gap

1. **Feed Grouping** — 날짜 기준 그룹핑 미구현 (오늘/어제/이번주/이전)
2. **Delayed Badge** — QUIET_HOUR_DELAYED 상태 Feed 카드에 badge 미표시
3. **Feed Grouping by Source** — source_type 그룹핑 UI 미구현
4. **admin notification-center** — Vuexy 레이아웃 적용 완료, Feed Grouping 동기화 필요

---

## Phase 2 UX 우선순위

1. Feed Date Grouping (오늘/어제/이번주)
2. Push Notification UX (FCM 도착 시 토스트)
3. Delayed/Resumed badge
4. Read-all 액션 모든 Surface 통일
