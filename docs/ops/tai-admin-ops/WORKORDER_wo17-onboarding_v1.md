---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-17 온보딩 체크리스트
version: 1
status: ACTIVE
owner: taiwang
---

# WO-17 — 온보딩 체크리스트 (OnboardingChecklist)

- **작성일:** 2026-07-28
- **Goal:** G-ms4je4z3-33eada
- **상위:** WORKPLAN §4 P2 WO-17 (P2 마지막)
- **오브젝트:** onboarding_svc(신설) + customer360 onboarding 키 채움
- **닫는 시나리오:** S17(신규 회사가 어디까지 왔고 다음에 뭘 해야 하는지)

---

## 1. 현황 (실측 — 파생 판정, 신설 없음)

체크리스트 계열 테이블은 전부 엔진/런타임 소관(격리):
- `checklist_*_candidate`·`saas_setup_candidate`: 엔진 컴파일러 산출 후보.
- `flow_step_registry`·`runtime_checklist_*`: 런타임 엔진.
→ **건드리지 않음.** 온보딩은 새 테이블 불필요 — 기존 데이터로 **파생 판정**.

**판정 기준(실측 확정):**
1. 회사정보 등록 — companies.name + business_number 존재.
2. 사업장 등록 — factories 행 ≥ 1(회사).
3. 법령진단 — 사업장 중 diagnosis_status ≠ 'NONE'(FREE/PAID/DONE) 또는 last_diagnosis_at 존재.
4. 구독 시작 — subscriptions status='ACTIVE' 존재.

(diagnosis_status 실측: NONE 5452·FREE 16·PAID 5·DONE 1)

## 2. 설계 — 파생 온보딩 진행률

**`services/onboarding_svc.py`(신설):**
- `get_checklist(company_id)`: 4단계 각 완료 여부(bool) + 완료 수/총계 + 진행률(%) + next_step(첫 미완료 단계).
- customer360 `onboarding` 키(현재 null)에 이 요약 동봉.

## 3. 엔드포인트

- `GET /companies/{id}/onboarding` — 회사 온보딩 체크리스트.
- customer360 get_summary에 onboarding 키 채움(연계).

## 4. 완료 판정 (IMPLEMENTED)

- onboarding_svc 4단계 파생 판정, 라우터, customer360 연계.
- 신규 테이블 없음, 엔진 격리.
- `/health` 200, 배포 SUCCESS. 목업 회사 표본으로 단계 판정 검증.

## 5. 산출물

1. `services/onboarding_svc.py`
2. `routers/onboarding_ops.py` (또는 customer360 확장)
3. customer360_svc onboarding 키 연계
4. router_registry 등록
