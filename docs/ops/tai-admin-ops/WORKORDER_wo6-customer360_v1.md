---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-6 고객360 — 통합 집계 API
version: 1
status: ACTIVE
owner: taiwang
---

# WO-6 — 고객360 (통합 집계 API)

- **작성일:** 2026-07-28
- **Goal:** G-ms4je4z3-33eada
- **상위:** WORKPLAN §4 P1 WO-6
- **오브젝트:** Customer360 집계 서비스 (백엔드, 신설) — 이번 A범위는 집계 API까지(화면은 후속)
- **닫는 시나리오:** S1(고객 통합조회)·S7·S8·S13·S37(온보딩 상태)

---

## 1. 현황 (실측 — 기존 자산 존재)

`routers/companies.py`(v2.1.0)에 회사 하위 조회가 **이미 개별 엔드포인트로 존재**:
- `GET /companies/{id}` 상세, `/{id}/users`, `/{id}/factories`, `/{id}/contacts`, `/{id}/contracts`, `/{id}/files`
- 응답 표준: `{"status":"success","data":{...}}` / 목록은 `{"data":{"items":[],"total":N}}`
- DB: `get_supabase()` 직접. prefix `/companies`.

원천 연결(실측): 전부 company_id 연결. companies 179 / factories 5,474 / users 20 / payments 132 / subscriptions 32 / diagnosis_purchases 16 / company_contacts 1 / credits·tax_invoices·refunds 0(신규). refunds는 payments 경유.

**결론: 고객360은 신설이 아니라, 흩어진 조회를 "한 번의 호출로 묶는 집계 엔드포인트" 추가.** 기존 개별 엔드포인트는 유지.

## 2. 오브젝트 계약

신규 서비스 `services/customer360_svc.py`:
```
get_summary(company_id) -> {
  company: {...},                        # companies 상세(활성)
  counts: {factories, users, contacts},  # deleted_at IS NULL 기준
  payments: {total_amount, count, last_paid_at, success_count},
  subscription: {status, plan, count},   # 현재 구독 상태
  diagnosis: {count, last_paid_at},      # diagnosis_purchases
  credit_balance: int,                   # credit_svc.balance 재사용
  invoices: {issued, cancelled},         # tax_invoices 요약
  refunds: {count, total},               # refunds 요약(payments 경유)
  recent_audit: [최근 감사 N건],          # admin_ops_audit_logs (entity_id=company or 관련 payment)
  onboarding: {done_steps, total_steps}  # ⑱ 온보딩 진행(테이블 준비 전엔 null)
}
```
라우터: `routers/companies.py`에 `GET /companies/{id}/360` 1개 추가(얇게). 집계 로직은 서비스로 분리(400줄 규칙).

## 3. 구현 원칙

- **원천 읽기만**(어드민 DB 복제 없음). 각 원천 count/sum을 그때그때 집계.
- credit_svc.balance() 재사용(중복 구현 금지).
- soft delete 반영: factories/users/contacts는 `deleted_at IS NULL` 기준.
- 결제상태는 payments 원천(status_code)만 신뢰.
- 온보딩(⑱)은 테이블 미존재 → null 반환(WO-17에서 채움). 계약만 미리 확보.
- 감사 요약: admin_ops_audit_logs에서 이 회사 관련(entity_id=company_id, 또는 이 회사 payment_id들) 최근 N건.

## 4. 완료 판정 (IMPLEMENTED)

- customer360_svc.get_summary 구현, 라우터 1개 추가.
- 실제 company로 집계 결과가 원천과 일치.
- credit_svc 재사용, 원천 읽기만. `/health` 200.

## 5. 산출물

1. `services/customer360_svc.py` (신설)
2. `routers/companies.py`에 `GET /{company_id}/360` 추가(얇은 위임)
