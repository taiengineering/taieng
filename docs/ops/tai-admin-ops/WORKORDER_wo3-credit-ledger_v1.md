---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-3 CreditLedger — 전환크레딧 원장
version: 2
status: ACTIVE
owner: taiwang
---

# WO-3 — CreditLedger (전환크레딧 원장)

- **작성일:** 2026-07-28 (v2: 검증 반영)
- **Goal:** G-ms4je4z3-33eada
- **상위:** WORKPLAN §4 P0 WO-3
- **오브젝트:** CreditLedger (도메인 서비스, 신설)
- **닫는 시나리오:** S6(진단→SaaS 30일 내 전환크레딧)
- **정책:** 가격 V4 — "30일 내 SaaS 전환 시 전환크레딧 100%"
- **최종 상태:** 코드·배포·스키마·로직 **VERIFIED**.

---

## 1. 현황 (실측)

- `credits`/`conversion_credits`: 없음 → 신설.
- `diagnosis_purchases`(16): `company_id, price, status, paid_at` 등 — 전환크레딧 원천.
- `companies.id`, `payments(id, company_id, product_type)`.

## 2. 정책 → 모델

진단 유료결제 회사가 30일 내 SaaS 가입 → 진단 결제액 100% 크레딧.
- grant: company 크레딧 생성, `expires_at = diagnosis.paid_at + 30일`.
- apply: SaaS 결제에 FIFO 차감(만료 제외).
- expire: expires_at 경과분은 balance 계산·apply에서 제외.

## 3. 스키마 (적용·검증 완료)

`credits(id, company_id FK, source[DIAGNOSIS_CONVERT|MANUAL], source_ref, amount>0, balance>=0, expires_at, applied_payment_id FK, status[ACTIVE|USED|EXPIRED], memo, created_by, created_at)`
- 불변식: `0 ≤ balance ≤ amount`(CHECK 2종).
- `source_ref` 부분 UNIQUE(중복 전환크레딧 발행 방지).
- 마이그레이션 git: `20260728142512_create_credits_ledger.sql`. Supabase 적용 완료(RLS off).

## 4. 오브젝트 계약 (구현 완료 — credit_svc.py)

```
grant(company_id, amount, source, source_ref, expires_at, by, memo) -> credit_id
grant_from_diagnosis(diagnosis_purchase_id, by) -> credit_id   # paid_at+30d, 중복방지
apply(company_id, payment_id, amount, actor_id) -> {applied, remaining_balance}  # FIFO·만료제외
balance(company_id) -> int  # ACTIVE·미만료 합
```
- grant/apply는 audit_svc.record(CREDIT_GRANT/CREDIT_APPLY) 기록.

## 5. 검증 결과 (2026-07-28, MCP 트랜잭션 롤백 테스트)

| 항목 | 상태 | 근거 |
|---|---|---|
| credits 테이블 생성 | VERIFIED | 12컬럼·인덱스4 확인 |
| balance() 만료 제외 | VERIFIED | c1+c3=18000, 만료 c2(5000) 제외 확인 |
| balance ≤ amount 가드 | VERIFIED | CHECK 위반 차단 |
| balance ≥ 0 가드 | VERIFIED | CHECK 위반 차단 |
| source_ref UNIQUE(중복발행 방지) | VERIFIED | unique_violation 차단 |
| 실데이터 무오염 | VERIFIED | 전체 롤백, credits 0건 |
| credit_svc.py 구현 | VERIFIED | 커밋 5186877 |
| Railway 배포 | VERIFIED | SUCCESS(5186877) + `/health` 통과 |
| 실전환 크레딧 발행/차감 | PENDING | 실 진단→SaaS 전환 발생 시(코드 경로 검증됨) |

## 6. 산출물 (커밋)

1. `supabase/migrations/20260728142512_create_credits_ledger.sql` (적용됨)
2. `services/credit_svc.py` (신설)
