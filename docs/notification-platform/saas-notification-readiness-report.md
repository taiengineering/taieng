# SaaS Notification Readiness Report

작성일: 2026-05-17
범위: SaaS 기본 알림 체계 평가

---

## 평가 항목

| 항목 | 점수 | 상태 |
|---|---|---|
| Auth Coverage | 8/10 | 6 이벤트 정의, pw_reset/otp frozen 유지 |
| Billing Coverage | 9/10 | 6 이벤트 정의, 기존 wiring 2건 연결 |
| Organization Coverage | 7/10 | 6 이벤트 정의, approval 워크플로우 미구현 |
| Workflow Coverage | 9/10 | 6 이벤트 정의, 기존 wiring 4건 연결 |
| Safety Coverage | 8/10 | 6 이벤트 정의, accident/violation 미구현 |
| System Coverage | 9/10 | 6 이벤트 정의, 기존 wiring 2건 연결 |
| Event Taxonomy | 9/10 | 8 category, 명명 규칙 정의 |
| Audience Matrix | 8/10 | 36 이벤트 × audience 매핑 |
| Channel Matrix | 8/10 | 36 이벤트 × channel 매핑 |
| Catalog Governance | 9/10 | 8단계 절차 + 금지 목록 |

---

## SaaS Notification Catalog Readiness

**84/100 = 84% — A- 등급**

---

## 발견된 공백

1. **approval 워크플로우** — approval_requested/completed 이벤트 정의만, 실제 워크플로우 미구현
2. **accident_reported** — 사고 보고 시스템 미구현
3. **violation_detected** — 법위반 감지 시스템 미구현
4. **Marketing Pack** — 3 이벤트 정의만, Campaign Runtime 미구현 (Phase 2)
5. **Email 채널** — 전체 미구현 (Phase 2)

---

## Legacy 충돌

| 충돌 | 설명 |
|---|---|
| pw_reset.py | Auth Pack password_reset과 중복 — frozen 유지로 공존 |
| sms_service.py | Billing Pack payment_failed와 경로 중복 — compat layer 경유 |

---

## 다음 우선순위

1. Workflow Pack 4건 실 wiring 연결 (schedule_due/overdue, inspection_completed/failed)
2. Billing Pack payment_failed SMS → wire_and_emit 전환
3. Safety Pack weather_work_stop 기존 wiring 연결 확인
4. Template 본문 작성 시작 (Phase 2)
