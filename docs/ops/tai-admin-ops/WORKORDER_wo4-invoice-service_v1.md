---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-4 InvoiceService — 세금계산서·현금영수증(팝빌 API)
version: 1
status: ACTIVE
owner: taiwang
---

# WO-4 — InvoiceService (세금계산서 + 현금영수증, 팝빌 API 실연동)

- **작성일:** 2026-07-28
- **Goal:** G-ms4je4z3-33eada
- **상위:** WORKPLAN §4 P0 WO-4
- **오브젝트:** InvoiceService (도메인 서비스, 신설)
- **닫는 시나리오:** S31 선행(세무자료), 결제 후 증빙 발급
- **대행:** 팝빌(링크허브) — 설치비 0·최소사용료 0·충전식, 웹훅(PUSH) 지원, 2004년 국내 표준

---

## 1. 팝빌 API 학습 결과 (핵심)

**공통:** SDK `pip install popbill`, `TaxinvoiceService/CashbillService(LinkID, SecretKey)`, `IsTest`로 테스트/운영 분리. **공급자(TAI) 공동인증서 팝빌 사전등록 필수**(실연동 시 사람 1회). 문서번호(mgtKey)를 우리가 할당해 중복발행 방지·상태조회 키로 사용. 상태변경은 **웹훅(PUSH)** 또는 getInfo(폴링).

**세금계산서(매출 정발행):**
- `registIssue(CorpNum, taxinvoice)` → 즉시발행. 응답 `ntsConfirmNum`(국세청승인번호)
- `cancelIssue(CorpNum, "SELL", mgtKey, memo)` → 국세청 전송 전 발행취소
- Taxinvoice 필수: issueType="정발행", taxType="과세", chargeDirection="정과금", writeDate(yyyyMMdd), purposeType(영수/청구), supplyCostTotal/taxTotal/totalAmount, 공급자(invoicerCorpNum=TAI 등 고정), 공급받는자(invoiceeType="사업자", invoiceeCorpNum/CorpName/CEOName/Email1), detailList(품목)

**현금영수증:**
- `registIssue(CorpNum, cashbill, memo)` → 즉시발행. `revokeRegistIssue(...)` → 취소(전체/부분)
- Cashbill 필수: mgtKey, tradeDT(yyyyMMddHHmmss), tradeType="승인거래", taxationType="과세", tradeOpt="일반", **tradeUsage**(개인=소득공제용 / 사업자=지출증빙용), supplyCost/tax/totalAmount, franchiseCorpNum(TAI), **identityNum**(소득공제용=휴대폰/주민번호, 지출증빙용=사업자번호)

## 2. 통합 설계 — 한 서비스·한 원장, doc_type 분기

세금계산서·현금영수증은 SDK·인증서·mgtKey·웹훅 패턴이 동일 → `invoice_svc.py` 하나가 `doc_type`으로 분기.
- 사업자 + 세금계산서 → TAX_INVOICE
- 사업자 + 현금영수증 → CASH_RECEIPT(지출증빙용)
- 개인 → CASH_RECEIPT(소득공제용)

## 3. 스키마 (마이그레이션 git 고정 → 사람 적용)

```sql
CREATE TABLE IF NOT EXISTS public.tax_invoices (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  payment_id    uuid REFERENCES public.payments(id),
  company_id    uuid REFERENCES public.companies(id),
  doc_type      text NOT NULL CHECK (doc_type IN ('TAX_INVOICE','CASH_RECEIPT')),
  mgt_key       text NOT NULL,                 -- 팝빌 문서번호(우리 할당, 중복방지)
  trade_usage   text,                          -- 현금영수증: 소득공제용|지출증빙용
  invoicee_type text,                          -- 사업자|개인|외국인
  identity_num  text,                          -- 현금영수증 식별번호(사업자번호/휴대폰/주민)
  supply_cost   integer NOT NULL,
  tax           integer NOT NULL,
  total_amount  integer NOT NULL,
  nts_confirm_num text,                        -- 국세청승인번호(발행 후)
  status        text NOT NULL DEFAULT 'PENDING'
                CHECK (status IN ('PENDING','ISSUED','CANCELLED','FAILED')),
  popbill_raw   jsonb,
  issued_at     timestamptz,
  created_by    text,
  created_at    timestamptz NOT NULL DEFAULT now()
);
-- idx: payment_id, company_id, status; UNIQUE(doc_type, mgt_key)
```

## 4. 오브젝트 계약 (WORKPLAN §2-A)

```
issue_tax_invoice(payment_id, invoicee{corpNum,corpName,ceoName,email}, by) -> {invoice_id, nts_confirm_num}
issue_cash_receipt(payment_id, trade_usage, identity_num, by) -> {invoice_id, nts_confirm_num}
cancel(invoice_id, reason, by) -> {status}
status(payment_id) -> [invoices]
handle_webhook(payload) -> None   # 팝빌 상태변경 수신 → tax_invoices.status 동기화
```
- 팝빌 SDK는 **지연 import**(미설치 시 501, 배포 안전). LinkID/SecretKey·공급자정보는 env 상수(R-008).
- 발행/취소는 audit(`INVOICE_ISSUE`/`INVOICE_CANCEL`) 기록.
- mgt_key = payment_id 기반 유일 생성(중복발행 방지).

## 5. 서비스 로직

**issue_tax_invoice:** payment 조회(SUCCESS) → split_supply_vat로 공급가/세액 → Taxinvoice 구성(공급자 TAI 고정 env, 공급받는자 인자) → tax_invoices PENDING 선기록 → registIssue → 성공 시 ISSUED+ntsConfirmNum, 실패 FAILED. audit.
**issue_cash_receipt:** 동일 + tradeUsage/identityNum 분기(개인 소득공제용/사업자 지출증빙용).
**cancel:** doc_type별 cancelIssue/revokeRegistIssue → CANCELLED. audit.
**handle_webhook:** 팝빌 PUSH payload의 mgtKey·stateCode로 tax_invoices.status 갱신(발행/전송/실패).

## 6. 완료 판정 (IMPLEMENTED)

- tax_invoices 생성 + issue/cancel/status/webhook 구현.
- SDK 지연 import로 미설치 시에도 배포 `/health` 200.
- 실발행 검증(VERIFIED)은 팝빌 가입 + 공동인증서 등록 + LinkID/SecretKey 발급 후 사람 게이트.

## 7. 산출물

1. `supabase/migrations/*_create_tax_invoices.sql`
2. `services/invoice_svc.py` (신설, 팝빌 세금계산서+현금영수증)
3. (실연동 시) 팝빌 웹훅 수신 라우터 + env: POPBILL_LINK_ID, POPBILL_SECRET_KEY, POPBILL_IS_TEST, TAI 공급자 정보
