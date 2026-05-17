# Notification Density Governance

작성일: 2026-05-17
범위: Notification Engine · 전달 밀도 관리

---

## Density 수준

| 수준 | 의미 | 일간 알림 수 | 대응 |
|---|---|---|---|
| LOW | 거의 없음 | 0~5 | 정상 |
| NORMAL | 운영 가능 | 6~20 | 정상 |
| HIGH | 피로 시작 | 21~50 | Digest 권장 |
| CRITICAL | 운영 마비 위험 | 50+ | Digest 필수 + cooldown 강화 |

---

## 핵심 원칙

**알림 수 ≠ 운영 품질**

많은 알림이 더 좋은 운영을 의미하지 않는다.

---

## Density 조절 전략

| 전략 | 대상 | 효과 |
|---|---|---|
| Cooldown | 동일 이벤트 | 중복 제거 |
| Digest | 동일 유형 복수 | 묶음 전달 |
| Quiet Hour | 야간 | 시간대 억제 |
| Severity 분리 | INFO/WARNING | 즐시 전달 |
| Mute | 사용자 선택 | 채널 차단 |

---

## 모니터링 기준

- `runtime_notification_metrics` 일간 발송 수 추적
- audience별 수신 알림 수 모니터링 (Phase 2)
- Density CRITICAL 도달 시 자동 경고 (Phase 2)
