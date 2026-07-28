---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-15 세무(세금계산서) 발행 현황
version: 2
status: DONE
owner: taiwang
---

# WO-15 — 세무(세금계산서) 발행 현황 (TaxInvoiceOps)

- **작성일:** 2026-07-28 (v2: 검증 완료)
- **Goal:** G-ms4je4z3-33eada
- **최종:** VERIFIED.

---

## 1. 현황 (실측 — 범위 판정)

- **`settlements`(27컬럼)**: 전문가/매칭 정산금 지급(withholding_tax·expert_*). 매칭·선임 서비스 소관 = **범위 밖(미사용)**.
- **`tax_invoices`(17컬럼)**: 고객 세금계산서(payment_id·company_id·supply_cost·tax·nts_confirm_num). 법령진단·SaaS = **범위 내**.
- WO-4 InvoiceService(발행 액션)와 상보 — WO-15는 발행 현황 조회.
- 실측: tax_invoices 0, payments SUCCESS 0(실데이터 전).

## 2. 구현 (완료)

**`services/tax_ops_svc.py`** (커밋 92930b8):
- `invoice_status_summary()`: 상태별 집계 + 공급가·세액·합계 합산.
- `unissued_payments(limit, offset)`: SUCCESS 결제 − 발행된 payment_id 차집합(미발행 = 발행 대상).
- `issued_list(limit, offset)`: 발행 완료 목록(국세청 승인번호 포함).
- `get_tax_ops()`: 종합(summary + 미발행 미리보기). 오류 격리. **settlements 미사용**.

**`routers/tax_ops.py`** (커밋 fc12274): `GET /tax/ops`·`/tax/unissued`·`/tax/issued`. external 등록 730f415.

## 3. 검증 결과

| 항목 | 상태 | 근거 |
|---|---|---|
| 범위 판정(settlements 제외) | VERIFIED | 컬럼 실측 — 전문가 정산은 미서비스 |
| 미발행 차집합 로직 | VERIFIED | SQL NOT EXISTS: SUCCESS 결제−발행 payment_id (실데이터 0) |
| 발행 현황 집계 | VERIFIED | tax_invoices status/공급가/세액 합산 |
| 앱 기동·라우팅 | VERIFIED | 배포 SUCCESS(730f415) + `/health` |

## 4. 산출물 (커밋)

1. `services/tax_ops_svc.py`
2. `routers/tax_ops.py`
3. `router_registry/external.py` (tax_ops 등록)

## 5. 후속 메모

- 실결제 발생 시 "SUCCESS 결제인데 세금계산서 미발행" 목록이 /tax/unissued에 노출 → WO-4 발행 액션으로 처리.
- settlements(전문가 정산)는 매칭/선임 서비스 개시 시 별도 WO로.
