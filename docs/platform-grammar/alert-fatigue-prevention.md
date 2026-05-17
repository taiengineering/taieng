# Alert Fatigue Prevention

작성일: 2026-05-17
범위: Notification Engine · 알림 피로 방지

---

## 핵심 원칙

**사람을 계속 깨우지 말 것.**

---

## 전략

| 전략 | 설명 | 구현 상태 |
|---|---|---|
| Cooldown | 동일 이벤트 중복 억제 | ✅ Policy + Wiring cooldown_seconds |
| Digest | 일정 기간 복수 알림 묶음 전달 | ⬜ 필드 준비 (digest_enabled) |
| Escalation Delay | 즉시 깨우지 않고 대기 후 에스컬레이션 | ⬜ 필드 준비 (escalation_delay_seconds) |
| Quiet Hour | 야간 억제 | ✅ Queue QUIET_HOUR_DELAYED |
| Feed Grouping | 동일 유형 알림 그룹 표시 | ✅ Frontend groupBy |
| Mute | 사용자 선택적 음소거 | ✅ Preference mute_enabled |
| Severity 분리 | CRITICAL만 즉시, 나머지는 정상 큐 | ✅ CRITICAL_BYPASS |

---

## Cooldown 정책 기준

| 유형 | Cooldown |
|---|---|
| 런타임 장애 | 0s (즉시) |
| 워크플로우 경고 | 300~600s |
| 서비스 공지 | 3600s |
| 일정 리마인더 | 86400s (1일) |

---

## 금지

- 모든 이벤트를 CRITICAL로 설정
- cooldown 0으로 전체 설정
- 반복 발송 제한 없는 wiring
- 사용자 mute 무시 (CRITICAL 외)
