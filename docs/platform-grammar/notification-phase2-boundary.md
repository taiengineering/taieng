# Notification Phase 2 Boundary

작성일: 2026-05-17
범위: Notification Engine · Phase 2 진입 범위

---

## Phase 2 허용

| 항목 | 범위 |
|---|---|
| Push Runtime 실제화 | firebase-admin SDK + FCM 연동 |
| Email Adapter | SMTP/SES 연동 |
| Feed Grouping 고도화 | 서버 aggregation + 무한 스크롤 |
| Multi-timezone | 사용자별 Quiet Hour 시간대 |
| Permission Layer | 역할 기반 알림 접근 제어 |
| WebSocket UX | 실시간 Feed 갱신 |
| Feed Search | 키워드/기간/severity 검색 |
| Read-all 통합 | 모든 Surface에 모두읽음 |
| ACKNOWLEDGED/RESOLVED | Lifecycle 확장 (2단계) |

---

## Phase 2 금지

| 항목 | 이유 |
|---|---|
| Runtime Rewrite | Phase 1 Runtime 유지 |
| Queue Rewrite | 단일 큐 아키텍처 유지 |
| Lifecycle Rewrite | Canonical Lifecycle 유지 |
| Channel-specific Runtime | 채널별 분기 금지 |
| AI Notification Analysis | 범위 확장 금지 |
| Incident Console | 별도 시스템으로 분리 |

---

## Phase 2 진입 조건

1. Phase 1 Freeze Manifest 공식 동결
2. Readiness Report S등급 달성 ✅
3. Technical Debt Critical 항목 0건 ✅
4. E2E 90% 이상 달성
5. 운영 1주 이상 무장애
