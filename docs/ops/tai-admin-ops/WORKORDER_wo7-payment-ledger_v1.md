---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-7 결제·구독 원장 — WO1~4 서비스 결선
version: 1
status: ACTIVE
owner: taiwang
---

# WO-7 — 결제·구독 원장 (RefundService·CreditLedger·InvoiceService 결선)

- **작성일:** 2026-07-28
- **Goal:** G-ms4je4z3-33eada
- **상위:** WORKPLAN §4 P1 WO-7
- **오브젝트:** PaymentLedger 결선 라우터 (백엔드, 신설) — 기존 payment_ops에 WO1~4 결선
- **닫는 시나리오:** S2(결제 상세/원장)·S24(구독 상태)

---

## 1. 현황 (실측 — 기존 자산 풍부)

`router_registry/payment.py`에 결제·계약·정산 라우터 다수 등록됨:
- `routers/payment_ops.py`: `GET /payments`(v_payments_list 뷰, 필터·검색), `GET /payments/expiring`(만료임박), `POST /payments/manual/confirm`(수동활성화), `POST /payments/{id}/cancel`(취소+계약비활성), `GET /payments/{id}/vbank-status`.
- `routers/payment_billing.py`, `routers/contracts.py`, `routers/settlements.py`(정산) 등 존재.
- subscriptions(32건): 전용 라우터 없음. 결제 원장에서 상태만 조회.

**미결선(문제):** WO-1~4 신규 서비스가 결제 운영에 연결 안 됨.
- cancel은 상태만 변경 → 실환불(refund_svc) 미연결.
- manual/confirm·cancel이 감사(audit_svc) 미기록.
- 전환크레딧(credit_svc) 발행 엔드포인트 없음.
- 세금계산서·현금영수증(invoice_svc) 발행 엔드포인트 없음.
- 결제 상세에 환불·크레딧·증빙 요약 없음.

## 2. 설계 — 기존 유지, 결선만 추가 (payment_ledger.py 신설)

기존 payment_ops.py는 건드리지 않고, 신규 얇은 라우터 `routers/payment_ledger.py`로 WO1~4를 결선. prefix `/payments`.

**엔드포인트:**
```
POST /payments/{id}/refund          → refund_svc.run_refund (전액) + 감사
POST /payments/{id}/refund/partial  → refund_svc.run_partial_refund (부분) + 감사
POST /payments/{id}/credit          → credit_svc.grant_from_diagnosis 또는 grant + 감사
POST /payments/{id}/invoice/tax     → invoice_svc.issue_tax_invoice + 감사
POST /payments/{id}/invoice/cash    → invoice_svc.issue_cash_receipt + 감사
GET  /payments/{id}/ledger          → 결제 1건의 환불·크레딧·증빙 통합 조회(원장)
```
- 각 서비스가 이미 내부에서 audit 기록(WO-1~4). ledger 조회는 refunds·credits·tax_invoices를 payment_id/company_id로 묶어 반환.

## 3. 구현 원칙

- **기존 엔드포인트 불변.** payment_ops의 cancel/manual/confirm는 그대로. (실환불은 신규 `/refund`로 분리 — cancel은 계약상태 전환, refund는 실제 돈 반환으로 의미 분리)
- 각 결선은 WO1~4 서비스 **위임만**(로직 중복 금지). 서비스가 payment_id로 자기 검증.
- ledger 조회는 원천 읽기만.
- 새 env 없음.

## 4. 완료 판정 (IMPLEMENTED)

- payment_ledger.py 6개 엔드포인트, payment 그룹 등록.
- 각각 refund_svc/credit_svc/invoice_svc 위임 + 서비스 내부 감사.
- `/health` 200. 배포 SUCCESS.

## 5. 산출물

1. `routers/payment_ledger.py` (신설)
2. `router_registry/payment.py`에 payment_ledger 등록
