# Push vs SMS Operational Matrix

작성일: 2026-05-17
범위: 운영 채널 우선순위

---

## Matrix

| 이벤트 | Push | SMS | 우선 | 이유 |
|---|---|---|---|---|
| schedule_due | ✅ | ❌ | Push | 일반 알림, 비용 절감 |
| schedule_overdue | ✅ | ✅ | Push+SMS | 중요, 이중 전달 |
| inspection_failed | ✅ | ❌ | Push | 내부 운영 |
| weather_work_stop | ✅ | ✅ | SMS+Push | 긴급, SMS 우선 |
| accident_reported | ❌ | ✅ | SMS | 긴급 접근성 |
| payment_failed | ❌ | ✅ | SMS | 재무 중요도 |
| subscription_expired | ❌ | ✅ | SMS | 재무 긴급 |
| education_due | ✅ | ❌ | Push | 일반 리마인더 |
| tbm_attendance | ✅ | ❌ | Push | 현장 작업자 |
| equipment_checkin | ✅ | ❌ | Push | 현장 작업자 |
| approval_requested | ✅ | ❌ | Push | 내부 운영 |
| member_invited | ✅ | ❌ | Push | 일반 알림 |

---

## 운영 기준

| 기준 | Push | SMS |
|---|---|---|
| 비용 | 무료 | 건당 20원+ |
| 도달률 | 앱 설치 사용자만 | 전체 |
| 즉시성 | 1~3초 | 5~30초 |
| 긴급성 | 중 | 높음 |
| 앱 미설치 시 | 전달 불가 | 전달 가능 |

---

## 결론

- 긴급 (CRITICAL): **SMS 우선** + Push 병행
- 일반 운영: **Push 우선** (SMS 비용 절감)
- 현장 작업자: **Push 전용** (TBM/설비/교육)
