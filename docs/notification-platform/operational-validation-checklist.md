# Operational Validation Checklist

작성일: 2026-05-17
범위: Notification Engine · 운영 안정성

---

## 체크리스트

| # | 항목 | 검증 방법 | 상태 |
|---|---|---|---|
| 1 | Queue 정상 처리 | emit-test → queue → DELIVERED 확인 | ⬜ |
| 2 | Retry 정상 | adapter 강제 실패 → RETRY_PENDING → 재시도 | ⬜ |
| 3 | DLQ 정상 | 3회 실패 → DEADLETTER 확인 | ⬜ |
| 4 | Quiet Hour 정상 | quiet hour 시간대 emit → DELAYED → 종료 후 RESUMED | ⬜ |
| 5 | CRITICAL Bypass | quiet hour 중 CRITICAL → 즉시 전달 | ⬜ |
| 6 | Feed 정상 | IN_APP 전달 → notifications 테이블 + 알림센터 표시 | ⬜ |
| 7 | Read 정상 | Feed 카드 클릭 → POST read → is_read=true | ⬜ |
| 8 | Timeline 정상 | trace_id → timeline steps 5+ | ⬜ |
| 9 | Mobile 정상 | site center 접속 → feed + timeline + health | ⬜ |
| 10 | Badge 정상 | unread-count API → 숫자 반환 (not object) | ⬜ |
| 11 | Popup Read | 헤더 벨 → 팝업 → 클릭 → POST read → center 이동 | ⬜ |
| 12 | Sidebar Badge | .notif-sidebar-badge 표시 + 30초 갱신 | ⬜ |
| 13 | Wiring Test | POST /wirings/test → wiring lookup → emit | ⬜ |
| 14 | Digest Shadow | POST /digest-test → queue append | ⬜ |
| 15 | Scheduler 자동화 | queue_worker 1분 + metrics 10분 cron 실행 | ⬜ |

---

## 완료 기준

15/15 = 100% 통과 시 운영 안정성 확인.
현재: **0/15 = 0%** (실사용 시작 전)
