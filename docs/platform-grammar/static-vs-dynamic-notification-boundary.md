# Static vs Dynamic Notification Boundary

작성일: 2026-05-17
범위: Notification Engine · 유형 경계

---

## 정의

| 유형 | 정의 | 예시 |
|---|---|---|
| **Static** | 운영 콘텐츠 — 사람이 작성하여 전달 | 공지, 마케팅, 캠페인, 점검안내, 수동발송 |
| **Dynamic** | 운영 이벤트 — 시스템이 발생시켜 전달 | Alert, Workflow Event, SLA Breach, Runtime Incident |

---

## 핵심

정적은 **운영 콘텐츠**, 동적은 **운영 이벤트**.

통합해서 보되 동일 개념으로 섹지 않는다.

---

## 구분

| 항목 | Static | Dynamic |
|---|---|---|
| 발생 주체 | 운영자 | 시스템 |
| 시점 | 예정된 시점 | 이벤트 발생 시 | 
| 본문 | 운영자 작성 | 템플릿 + 변수 |
| 대상 | 전체/그룹 | Wiring audience |
| 중요도 | 운영자 판단 | Policy severity |
| Runtime | ❌ 미경유 (향후 경유 가능) | ✅ Queue→Worker→Adapter |
| Feed | 별도 Surface | 알림센터 Feed |

---

## Static Notification 예시

- 점검공지: "내일 10시 소방시설 점검이 예정되어 있습니다"
- 장애공지: "오늘 14~16시 서버 점검으로 서비스가 중단됩니다"
- 마케팅: "새로운 기능이 추가되었습니다"

## Dynamic Notification 예시

- workflow_stuck: "[CRITICAL] 워크플로우 이상 감지"
- sla_breach: "[CRITICAL] SLA 위반 발생"
- schedule_overdue: "[WARNING] 점검일정 초과"
