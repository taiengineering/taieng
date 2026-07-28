---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-9B 사업장(factory) 축 보강 — 과금 산정·사업장별 구독
version: 1
status: ACTIVE
owner: taiwang
---

# WO-9B — 사업장(factory) 축 보강

- **작성일:** 2026-07-28
- **Goal:** G-ms4je4z3-33eada
- **상위:** WORKPLAN §4 P1 (WO-9 파일뷰에서 사업장 축 보강으로 재조정)
- **오브젝트:** customer360_svc 사업장 집계 확장 + 조회 엔드포인트

---

## 1. 사업 모델 (사용자 확인)

- **거래 주체 = 회사(company)** — 계약·결제·세금계산서는 회사와.
- **과금 계산 단위 = 사업장(factory) 수** — 예: 월 10만원 × 사업장 3개 = 30만원.
- 구조: 회사 → 사업장 ×N → 회원 ×N. 하청 시 사업장 → 하청회사 → 하청회원.
- UI 문구 규칙: "사업장당 과금" 금지 → "시설 1개 기준" 표현.

## 2. 현황 (실측)

| 테이블 | 축 | 비고 |
|---|---|---|
| payments | company_id | 거래=회사. factory_id 없음(정상) |
| contracts | company_id | 회사 단위 |
| subscriptions | company_id + **factory_id** | 사업장별 구독. amount/supply/vat/plan_code/status/next_billing_at |
| factories | company_id | plan_code·legal_applicable_count·diagnosis_status·last_diagnosis_at 보유 |

- 목업: 회사 179, 사업장 5,474(회사당 평균 30.8). subscriptions 32건은 factory_id 아직 NULL(실데이터 전 상태). 구조는 정합, 데이터만 미적재.
- **문제:** 고객360이 사업장 개수만 표시. "사업장별 구독·과금 산정(사업장 수×요금=청구액)"이 없음.

## 3. 설계 — customer360_svc 사업장 집계 확장

`get_factory_billing(company_id)` 신설:
- 회사의 활성 사업장 목록(factories, deleted_at IS NULL) + 각 사업장 plan_code·diagnosis_status·legal_applicable_count.
- 각 사업장의 구독(subscriptions.factory_id 조인) 상태·plan·amount.
- 집계: 활성 사업장 수, 구독 있는 사업장 수, 월 과금 합계(ACTIVE 구독 amount 합=MRR), 미구독 사업장 수.
- 원천 읽기만. 데이터 없어도 0으로 정상 동작.

## 4. 엔드포인트

- `GET /companies/{company_id}/factory-billing` — 사업장별 구독·과금 요약.

## 5. 완료 판정 (IMPLEMENTED)

- get_factory_billing 구현, 라우터 추가, saas_core 등록.
- 배포 SUCCESS + `/health`. 목업 표본으로 사업장 목록·집계 동작 확인(구독 amount는 데이터 전이라 0).

## 6. 파일 통합뷰(원 WO-9)

`v_files_unified`(documents+company_files, company 축) 이미 생성됨. generated_document는 tenant_id가 company 미연결(엔진 목업)이라 제외. 파일은 회사 자산이므로 company 축 유지. 파일 조회 엔드포인트는 사업장 축 보강 후 함께 마무리.
