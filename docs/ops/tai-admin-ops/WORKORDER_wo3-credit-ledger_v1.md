---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-3 CreditLedger — 전환크레딧 원장
version: 1
status: ACTIVE
owner: taiwang
---

# WO-3 — CreditLedger (전환크레딧 원장)

- **작성일:** 2026-07-28
- **Goal:** G-ms4je4z3-33eada
- **상위:** WORKPLAN §4 P0 WO-3
- **오브젝트:** CreditLedger (도메인 서비스, 신설)
- **닫는 시나리오:** S6(진단→SaaS 30일 내 전환크레딧)
- **정책 근거:** 가격 V4 — "30일 내 SaaS 전환 시 전환크레딧 100%"

---

## 1. 현황 (실측 확정)

- `credits`/`conversion_credits`: **없음**(신설).
- `diagnosis_purchases`(16건): `id, company_id, price, status, paid_at, expires_at, diagnosis_id, ...` — 전환크레딧 원천(진단 결제) 참조 가능.
- `companies.id`, `payments(id, company_id, product_type)` 확인.

## 2. 정책 → 데이터 모델 매핑

"진단 유료결제한 회사가 30일 내 SaaS에 가입하면, 진단 결제액을 100% 크레딧으로 준다."
- 발행(grant): 진단 결제 시점 또는 SaaS 결제 시점에 company 크레딧 생성. `expires_at = diagnosis.paid_at + 30일`.
- 적용(apply): SaaS 결제(payment)에 크레딧 차감. balance 감소, applied_payment_id 기록.
- 소멸(expire): expires_at 경과 시 status=EXPIRED(배치 또는 조회 시 판정).

## 3. 스키마 (마이그레이션 git 고정 → 사람 적용)

```sql
CREATE TABLE IF NOT EXISTS public.credits (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id    uuid NOT NULL REFERENCES public.companies(id),
  source        text NOT NULL CHECK (source IN ('DIAGNOSIS_CONVERT','MANUAL')),
  source_ref    uuid,                    -- diagnosis_purchase.id 등 원천
  amount        integer NOT NULL CHECK (amount > 0),
  balance       integer NOT NULL,        -- 잔액(발행 시 amount, 사용 시 감소)
  expires_at    timestamptz,
  applied_payment_id uuid REFERENCES public.payments(id),
  status        text NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','USED','EXPIRED')),
  memo          text,
  created_by    text,
  created_at    timestamptz NOT NULL DEFAULT now()
);
-- idx: company_id, status
```
- 불변식: `balance ≤ amount`, `balance ≥ 0`. 서비스 로직 강제.

## 4. 오브젝트 계약 (WORKPLAN §2-A)

```
grant(company_id, amount, source, source_ref=None, expires_at=None, by=None, memo=None) -> credit_id
apply(company_id, payment_id, amount) -> {applied, remaining_balance}   # 여러 크레딧 FIFO 차감
balance(company_id) -> int                                             # ACTIVE·미만료 합계
grant_from_diagnosis(diagnosis_purchase_id) -> credit_id               # 정책 헬퍼(paid_at+30d)
```
- 모든 grant/apply는 audit_svc.record(`CREDIT_GRANT`, `CREDIT_APPLY`) 기록.
- apply는 만료 크레딧 제외, 오래된 것부터(FIFO) 차감.

## 5. 서비스 로직 (credit_svc.py)

**grant:** company 존재 확인 → credits INSERT(balance=amount, status=ACTIVE) → audit CREDIT_GRANT.
**grant_from_diagnosis:** diagnosis_purchase 조회(status 유료·paid) → 중복발행 방지(source_ref 유일) → expires_at=paid_at+30d로 grant.
**apply(payment):** company의 ACTIVE·미만료 크레딧을 created_at ASC로 조회 → 필요액까지 FIFO 차감(balance 감소, 0되면 status=USED, applied_payment_id 기록) → 부족하면 가능한 만큼만. audit CREDIT_APPLY.
**balance:** ACTIVE·(expires_at IS NULL OR expires_at>now())의 balance 합.

## 6. 완료 판정 (IMPLEMENTED)

- credits 테이블 생성 + grant/apply/balance/grant_from_diagnosis 구현.
- balance 불변식(0≤balance≤amount)·만료 제외·FIFO 차감 동작.
- 감사 기록. `/health` 200. DDL 마이그레이션 경로.

## 7. 산출물

1. `supabase/migrations/*_create_credits.sql`
2. `services/credit_svc.py` (신설)
