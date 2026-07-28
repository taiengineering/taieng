---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-15 세무(세금계산서) 발행 현황
version: 1
status: ACTIVE
owner: taiwang
---

# WO-15 — 세무(세금계산서) 발행 현황 (TaxInvoiceOps)

- **작성일:** 2026-07-28
- **Goal:** G-ms4je4z3-33eada
- **상위:** WORKPLAN §4 P2 WO-15
- **오브젝트:** tax_ops_svc(신설) + 발행 현황 엔드포인트
- **닫는 시나리오:** S15(어느 결제에 세금계산서가 발행됐고 무엇이 미발행인지)

---

## 1. 현황 (실측 — 범위 판정 포함)

두 테이블 존재:
- **`settlements`(27컬럼)**: matching_contract_id·expert_user_id·expert_name·tai_fee_rate·withholding_tax·withholding_reported. → **전문가/매칭 정산금 지급**. 매칭·선임 서비스 소관 = **범위 밖(제외)**. TAI 서비스 범위(법령진단·SaaS 2종)에 해당 안 됨.
- **`tax_invoices`(17컬럼)**: payment_id·company_id·doc_type·supply_cost·tax·total_amount·nts_confirm_num·popbill_raw·status. → **고객(회사) 세금계산서 발행**. 법령진단·SaaS 결제 대상 = **범위 내**.

WO-4 InvoiceService(발행 액션, tax_invoices INSERT)는 이미 존재. **WO-15는 발행 현황 조회**(상보): SUCCESS 결제 대비 발행/미발행.

실측: tax_invoices 0건, payments SUCCESS 0건(실데이터 전). 로직 검증만.

## 2. 설계 — 세무 발행 현황(고객 세금계산서)

**`services/tax_ops_svc.py`(신설):**
- `invoice_status_summary()`: tax_invoices 상태별 집계(발행/대기/실패) + 총 공급가·세액.
- `unissued_payments(limit, offset)`: SUCCESS 결제 중 tax_invoices에 payment_id 없는 건(미발행 목록). 세금계산서 발행 대상.
- `issued_list(limit, offset)`: 발행된 세금계산서 목록(회사·결제·국세청 승인번호).
- `get_tax_ops()`: 종합. 오류 격리.
- **settlements 미사용**(범위 밖).

## 3. 엔드포인트

- `GET /tax/ops` — 세무 발행 현황 종합.
- `GET /tax/unissued` — 미발행 결제 목록(발행 대상).
- `GET /tax/issued` — 발행 완료 목록.

## 4. 완료 판정 (IMPLEMENTED)

- tax_ops_svc, 라우터, 등록. settlements 제외.
- 미발행 결제 = SUCCESS 결제 − tax_invoices(payment_id) 차집합 로직.
- `/health` 200, 배포 SUCCESS. (실데이터 0이라 로직 검증 중심)

## 5. 산출물

1. `services/tax_ops_svc.py`
2. `routers/tax_ops.py`
3. router_registry 등록(external)
