# Operational Event Taxonomy v2

작성일: 2026-05-17
범위: 이벤트 분류 체계 v2 (Truth Source 기반)

---

## 카테고리

| 카테고리 | truth_source | prefix | 예시 |
|---|---|---|---|
| control | `control` | workflow_, sla_ | workflow_stuck, sla_breach |
| workflow | `workflow` | schedule_, inspection_ | schedule_overdue, inspection_failed |
| billing | `billing` | payment_, subscription_, invoice_ | payment_failed, subscription_activated |
| auth | `auth` | login_, account_, password_ | login_detected, account_locked |
| organization | `organization` | member_, role_, approval_ | member_invited, approval_requested |
| safety | `safety` | weather_, accident_, violation_, risk_ | weather_work_stop, accident_reported |
| education | `education` | education_ | education_due, education_completed |
| system | `system` | maintenance_, backup_, scheduler_, service_ | backup_failed, service_degraded |
| marketing | `marketing` | campaign_, newsletter_, feature_ | campaign_sent |

---

## v1 → v2 변화

| 변화 | 설명 |
|---|---|
| truth_source 추가 | 각 카테고리에 발생 주체 명시 |
| control 카테고리 추가 | Watch Engine 발생 이벤트 분리 |
| education 카테고리 추가 | safety에서 분리 |

---

## 명명 규칙

1. `{category_noun}_{past_participle}` — `payment_failed`
2. snake_case 소문자
3. 약어 금지
4. truth_source와 category 일치 권장
