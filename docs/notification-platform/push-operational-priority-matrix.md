# Push Operational Priority Matrix

작성일: 2026-05-17
범위: Push 이벤트 운영 우선순위

---

## 우선순위 Matrix

| 이벤트 | Push 우선순위 | 이유 | SMS 병행 |
|---|---|---|---|
| weather_work_stop | ★★★ CRITICAL | 현장 전체 즉시 전달 | ✅ SMS 우선 |
| accident_reported | ★★★ CRITICAL | 긴급 사고 보고 | ✅ SMS 우선 |
| schedule_overdue | ★★☆ HIGH | 미이행 점검 독촉 | ✅ SMS 병행 |
| tbm_attendance | ★★☆ HIGH | 현장 작업자 참석 | ❌ Push 전용 |
| inspection_failed | ★★☆ HIGH | 점검 실패 알림 | ❌ Push 전용 |
| equipment_checkin | ★☆☆ MEDIUM | 설비 체크인 알림 | ❌ Push 전용 |
| education_due | ★☆☆ MEDIUM | 교육 리마인더 | ❌ Push 전용 |
| safety_report | ★☆☆ MEDIUM | 안전보고 알림 | ❌ Push 전용 |
| approval_requested | ★☆☆ MEDIUM | 승인 요청 | ❌ Push 전용 |
| schedule_due | ☆☆☆ LOW | 일반 점검일정 | ❌ Push 전용 |
| member_invited | ☆☆☆ LOW | 멤버 초대 | ❌ Push 전용 |
| payment_success | ☆☆☆ LOW | 결제 성공 | ❌ IN_APP 전용 |

---

## Runtime 전환 우선순위

1. **CRITICAL 이벤트** — weather_work_stop, accident_reported (SMS 병행 필수)
2. **HIGH 이벤트** — schedule_overdue, tbm_attendance, inspection_failed
3. **MEDIUM 이벤트** — 현장 작업자 대상
4. **LOW 이벤트** — 일반 운영 알림
