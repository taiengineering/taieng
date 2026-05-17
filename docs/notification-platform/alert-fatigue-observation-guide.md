# Alert Fatigue Observation Guide

작성일: 2026-05-17
범위: Notification Engine · 피로 관찰

---

## 목적

**사람의 피로를 관찰**한다.

---

## 관찰 포인트

| 포인트 | 신호 | 의미 |
|---|---|---|
| Unread Accumulation | 미읽음이 계속 증가 | 알림을 무시하고 있음 |
| Mute 증가 | mute 설정 빈도 상승 | 특정 알림이 성가심 |
| Quiet Hour 확대 | quiet hour 시간대 확장 | 야간 알림이 부담 |
| Repeated Ignore | 동일 source_type 반복 무시 | 해당 알림 가치 낮음 |
| Rapid Dismiss | 팝업 즉시 닫기 | 내용 확인 안 함 |
| Read-all 남용 | 전체 읽음 빈번 사용 | 개별 확인 포기 |
| Badge 무시 | badge 99+ 지속 | 알림 시스템 신뢰 상실 |

---

## 대응 전략

| 신호 | 대응 |
|---|---|
| Unread 50+ 지속 | Digest 활성화 검토 |
| Mute 3+ source_type | 해당 알림 가치 재평가 |
| Quiet Hour 12h+ | 알림 빈도 전체 재검토 |
| Read-all 일 3회+ | Feed 밀도 과다 — cooldown 강화 |
| Badge 99+ 1주+ | 알림 시스템 재설계 필요 |

---

## 핵심

피로는 시스템이 아닌 **사람에게서** 관찰된다.
