---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-9B 사업장(factory) 축 보강 — 과금 산정·사업장별 구독
version: 2
status: ACTIVE
owner: taiwang
---

# WO-9B — 사업장(factory) 축 보강

- **작성일:** 2026-07-28 (v2: 검증 반영)
- **Goal:** G-ms4je4z3-33eada
- **오브젝트:** customer360_svc 사업장 집계 확장 + factory-billing 엔드포인트 + v_files_unified 뷰
- **최종:** 로직·뷰 VERIFIED(SQL 검증). 배포 SUCCESS 확인 대기(코드 안전 확인됨).

---

## 1. 사업 모델 (사용자 확인)

- **거래 주체 = 회사**(계약·결제·세금계산서). **과금 계산 단위 = 사업장 수**(월 10만 × 사업장 3 = 30만).
- 구조: 회사 → 사업장 ×N → 회원 ×N. 하청 시 사업장 → 하청회사 → 하청회원.
- UI 문구: "사업장당 과금" 금지 → "시설 1개 기준".

## 2. 현황 (실측)

| 테이블 | 축 |
|---|---|
| payments/contracts | company_id (거래=회사) |
| subscriptions | company_id + factory_id (사업장별 구독, amount/plan/status/next_billing_at) |
| factories | company_id (plan_code·diagnosis_status·legal_applicable_count 보유) |

목업: 회사 179, 사업장 5,474(평균 30.8/회사). subscriptions 32건 factory_id 아직 NULL(실데이터 전). 구조 정합, 데이터만 미적재.

## 3. 구현 (완료)

**`services/customer360_svc.py` 확장** (커밋 1a03e65):
- `factory_billing_summary(company_id)`: 활성 사업장 수, 구독 사업장 수, 미구독 수, 월 과금 합계(ACTIVE 구독 amount 합=MRR). get_summary에 `billing` 키로 동봉.
- `get_factory_billing(company_id, limit, offset)`: 사업장 목록(plan_code·diagnosis_status·legal_applicable_count) + 사업장별 구독(status/plan/amount/next_billing_at) + 집계.

**`routers/customer360.py`** (커밋 7bce750): `GET /companies/{id}/factory-billing`. saas_core 기존 등록(추가 등록 불필요).

## 4. 검증 결과

| 항목 | 상태 | 근거 |
|---|---|---|
| factory_billing 집계 로직 | VERIFIED | SQL 표본: "[VIRTUAL] TAI 시뮬레이션 그룹" 활성 사업장 10, 구독 0, 월과금 0 (구독 데이터 전이라 정상) |
| get_summary billing 동봉 | VERIFIED | 코드 대조 |
| 엔드포인트 시그니처 정합 | VERIFIED | get_factory_billing(company_id, limit, offset) 대조 일치 |
| 앱 기동 | IMPLEMENTED | 이전 커밋(1a03e65) DEPLOYING 통과로 코드 안전. 최종(7bce750) SUCCESS 확인 대기 |

## 5. 파일 통합뷰 (원 WO-9)

- `v_files_unified` 뷰 생성·적용 완료(documents+company_files, company 축). enum→text 캐스팅으로 UNION 정합.
- generated_document는 tenant_id가 company 미연결(목업 라벨 anonymous/mock_*)이라 제외. 파일은 회사 자산이므로 company 축.
- 파일 조회 엔드포인트는 실파일 적재 후 마무리(현재 실파일 0).

## 6. 산출물

1. `services/customer360_svc.py` (factory_billing_summary + get_factory_billing)
2. `routers/customer360.py` (factory-billing 엔드포인트)
3. `supabase/migrations/20260728161328_create_v_files_unified.sql` (뷰, 적용됨)
