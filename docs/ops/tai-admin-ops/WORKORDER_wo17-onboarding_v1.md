---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-17 온보딩 체크리스트
version: 2
status: DONE
owner: taiwang
---

# WO-17 — 온보딩 체크리스트 (OnboardingChecklist)

- **작성일:** 2026-07-28 (v2: 검증 완료)
- **Goal:** G-ms4je4z3-33eada
- **최종:** VERIFIED. **P2 마지막 WO 완료.**

---

## 1. 현황 (실측 — 파생 판정)

체크리스트 계열 테이블은 전부 엔진/런타임 소관(checklist_*_candidate·saas_setup_candidate·flow_step_registry·runtime_checklist_*) = **격리, 미사용**. 온보딩은 기존 데이터로 파생 판정(신설 없음).

## 2. 구현 (완료)

**`services/onboarding_svc.py`** (커밋 79d200b):
- `get_checklist(company_id)`: 4단계 파생 판정.
  1. company_info: companies.name + business_number.
  2. factory_added: factories 행 ≥ 1.
  3. diagnosis_done: 사업장 diagnosis_status ≠ 'NONE' 또는 last_diagnosis_at.
  4. subscription_active: subscriptions status='ACTIVE'.
- items + completed/total + progress_pct + next_step(첫 미완료) + is_complete.

**`routers/onboarding_ops.py`** (커밋 3d8bc02): `GET /companies/{id}/onboarding`. saas_core 등록 11054c9(기존 routers.onboarding과 구분).

## 3. 검증 결과

| 항목 | 상태 | 근거 |
|---|---|---|
| 4단계 파생 판정 | VERIFIED | 진단 회사 3곳: 회사정보·사업장·진단 done, 구독 미완 → 75%, next=구독 |
| next_step 계산 | VERIFIED | 첫 미완료=subscription_active 정확 |
| 엔진 격리 | VERIFIED | 체크리스트 엔진 테이블 미사용 |
| 앱 기동·라우팅 | VERIFIED | 배포 SUCCESS(11054c9) + `/health` |

## 4. 실전 가치

진단까지 왔으나 구독 안 한 회사(75%, next=구독)를 즉시 식별 → 구독 전환 유도. 1인 운영자의 세일즈 우선순위 큐.

## 5. 산출물 (커밋)

1. `services/onboarding_svc.py`
2. `routers/onboarding_ops.py`
3. `router_registry/saas_core.py` (onboarding_ops 등록)

## 6. 후속 (선택)

- customer360 get_summary의 onboarding 키(현재 null)에 get_checklist 요약 동봉 — 후속 연계.
