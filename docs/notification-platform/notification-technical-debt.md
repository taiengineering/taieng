# Notification Technical Debt Registry

작성일: 2026-05-17
범위: Notification Engine Phase 1

---

## Critical

| Debt | 설명 | 영향 |
|---|---|---|
| — | Critical debt 없음 | — |

---

## Medium

| Debt | 설명 | 해결 방향 |
|---|---|---|
| Push Mock 상태 | push.py가 로깅만 수행, FCM 미연동 | Phase 2: firebase-admin SDK |
| Edge SMS 이중화 | SMS adapter + Supabase Edge Function 이중 존재 | MessageMi 단일화 |
| notification.js 3중 복사 | admin/tadmin/site에 동일 로직 별도 파일 | 공통 JS 모듈화 또는 CDN |
| Feed grouping frontend-only | 날짜 그룹핑이 클라이언트 측 | 대규모 시 서버 aggregation 필요 |
| E2E 86.8% | 38건 중 5건 미통과 (WebSocket/Email 관련) | Phase 2 adapter 추가 후 보완 |

---

## Low

| Debt | 설명 | 해결 방향 |
|---|---|---|
| WebSocket 미지원 | 실시간 push 없이 30초 polling | Phase 2 WebSocket 검토 |
| Feed 무한 스크롤 미구현 | 더보기 버튼 방식 | UX 개선 시 적용 |
| Read-all Popup 미통합 | 알림센터에만 read-all 존재 | Popup에 모두읽음 추가 |
| Timeline step 한글화 | EVENT/QUEUE/DELIVERED 영문 | i18n 적용 시 |
| diagrams 버킷 SVG 미이전 | 구프로젝트 25개 SVG | Seoul 프로젝트로 이전 |
