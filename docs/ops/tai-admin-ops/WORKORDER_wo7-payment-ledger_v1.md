---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-7 결제·구독 원장 — WO1~4 서비스 결선
version: 2
status: ACTIVE
owner: taiwang
---

# WO-7 — 결제·구독 원장 (RefundService·CreditLedger·InvoiceService 결선)

- **작성일:** 2026-07-28 (v2: 검증 반영)
- **Goal:** G-ms4je4z3-33eada
- **상위:** WORKPLAN §4 P1 WO-7
- **오브젝트:** PaymentLedger 결선 라우터 (백엔드) — 기존 payment_ops에 WO1~4 결선
- **최종 상태:** 코드·배포·시그니처 정합성 **VERIFIED**. 실환불/실발행은 WO-1/WO-4 사람게이트 상속.

---

## 1. 현황 (실측 — 기존 자산 풍부)

`router_registry/payment.py`에 결제·계약·정산 라우터 다수 등록됨(payment_ops·payment_billing·contracts·settlements 등). payment_ops.py에 목록/만료임박/수동확정/취소/vbank 이미 존재. subscriptions는 전용 라우터 없음(상태 조회만).

**미결선(문제):** WO-1~4 신규 서비스가 결제 운영에 연결 안 됨(실환불·전환크레딧·증빙발행·결제원장 조회 부재).

## 2. 구현 (완료) — 기존 유지, 결선만 추가

기존 payment_ops.py 불변. 신규 얇은 라우터 `routers/payment_ledger.py`(prefix `/payments`)로 WO1~4 결선:

| 엔드포인트 | 위임 | 
|---|---|
| `POST /payments/{id}/refund` | refund_svc.run_refund (전액, 이니시스) |
| `POST /payments/{id}/refund/partial` | refund_svc.run_partial_refund (부분) |
| `POST /payments/{id}/credit` | credit_svc.grant_from_diagnosis(진단전환) 또는 grant(수동) |
| `POST /payments/{id}/invoice/tax` | invoice_svc.issue_tax_invoice (세금계산서) |
| `POST /payments/{id}/invoice/cash` | invoice_svc.issue_cash_receipt (현금영수증) |
| `GET /payments/{id}/ledger` | refunds·credits·tax_invoices 통합 조회 |

- 각 서비스가 내부에서 audit 기록(WO-1~4). 감사 자동.
- cancel(payment_ops)과 refund(신규)는 의미 분리: cancel=계약상태 전환, refund=실제 돈 반환.

## 3. 검증 결과 (2026-07-28)

| 항목 | 상태 | 근거 |
|---|---|---|
| payment_ledger.py 6개 엔드포인트 | VERIFIED | 커밋 f3bfc240·ddc3ff3 |
| payment 그룹 등록 | VERIFIED | 커밋 8b6e22a |
| 앱 기동(import 정상) | VERIFIED | 배포 SUCCESS + `/health` 통과 |
| 서비스 시그니처 정합성 | VERIFIED | refund/credit/invoice 6개 호출 = 실제 함수 시그니처 대조 일치(credit_svc created_by 정정 반영) |
| 기존 payment_ops 불변 | VERIFIED | 파일 미수정, 신규 라우터로만 추가 |
| 감사 자동 | VERIFIED | 각 서비스 내부 audit_svc.record(WO1~4에서 검증됨) |

> 실 HTTP·실환불·실발행 검증은 컨테이너 네트워크 차단 + 팝빌/이니시스 사람게이트 → 배포 성공(import·라우팅) + 시그니처 대조로 검증. 실동작은 WO-1(실결제 환불)·WO-4(팝빌 발행) 사람게이트에서 완결.

## 4. 산출물 (커밋)

1. `routers/payment_ledger.py` (신설)
2. `router_registry/payment.py` (payment_ledger 등록)
