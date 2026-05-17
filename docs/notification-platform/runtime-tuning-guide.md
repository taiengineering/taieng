# Runtime Tuning Guide

작성일: 2026-05-17
범위: Notification Engine · 운영 파라미터

---

## 튜닝 가능 파라미터

| 파라미터 | 현재값 | 위치 | 범위 |
|---|---|---|---|
| cooldown_seconds | 0~86400 | notification_policy_registry / wiring | 이벤트별 |
| retry_max | 3 | retry_policy.py | 전역 |
| retry_interval | 60→180→540s | retry_policy.py | 전역 |
| quiet_hour_start/end | 사용자 설정 | notification_preferences | 사용자별 |
| REFRESH_MS | 30000 (30s) | notification.js | 전역 |
| queue_worker_interval | 1분 | cron_job_master | 전역 |
| metrics_interval | 10분 | cron_job_master | 전역 |
| feed_page_size | 20 | notification-center.html | 전역 |
| popup_preview_size | 5 | notification.js | 전역 |
| digest_window_minutes | 60~10080 | digest_policy_registry | 정책별 |
| badge_cap | 99+ | notification.js | 전역 |

---

## 튜닝 절차

1. 변경 사유 기록
2. 현재값 기록
3. 변경 후 1시간 관찰
4. 이상 시 즉시 복원

---

## 금지

- Runtime Rewrite
- Lifecycle Rewrite
- Queue 구조 변경
- Feed Contract 변경
