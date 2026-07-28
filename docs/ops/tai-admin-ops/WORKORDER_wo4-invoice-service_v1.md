---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-4 InvoiceService — 세금계산서·현금영수증(팝빌 API)
version: 2
status: ACTIVE
owner: taiwang
---

# WO-4 — InvoiceService (세금계산서 + 현금영수증, 팝빌 API 실연동)

- **작성일:** 2026-07-28 (v2: 검증 반영)
- **Goal:** G-ms4je4z3-33eada
- **상위:** WORKPLAN §4 P0 WO-4
- **오브젝트:** InvoiceService (도메인 서비스, 신설)
- **대행:** 팝빌(링크허브) — 설치비 0·최소사용료 0·충전식, 웹훅 지원, 국내 표준
- **최종 상태:** 코드·배포·스키마·가드 **VERIFIED**. 실발행은 팝빌 가입+인증서 등록 후 사람 게이트.

---

## 1. 팝빌 API 학습 결과 (핵심)

**공통:** SDK `pip install popbill`, `TaxinvoiceService/CashbillService(LinkID, SecretKey)`, `IsTest`로 테스트/운영 분리. 공급자(TAI) 공동인증서 팝빌 사전등록 필수. 문서번호(mgtKey)로 중복발행 방지·상태조회. 상태변경 웹훅(PUSH) 또는 getInfo(폴링).

**세금계산서:** `registIssue(CorpNum, taxinvoice)`→즉시발행(ntsConfirmNum 반환). `cancelIssue(CorpNum,"SELL",mgtKey,memo)`→발행취소. Taxinvoice: issueType="정발행"/taxType="과세"/chargeDirection="정과금"/purposeType/writeDate/supplyCostTotal·taxTotal·totalAmount/공급자(invoicer*)/공급받는자(invoicee*)/detailList.

**현금영수증:** `registIssue(CorpNum, cashbill, memo)`→즉시발행. `revokeRegistIssue`→취소. Cashbill: mgtKey/tradeDT/tradeType="승인거래"/taxationType="과세"/tradeOpt="일반"/**tradeUsage**(개인 소득공제용, 사업자 지출증빙용)/supplyCost·tax·totalAmount/franchise*(TAI 가맹점)/**identityNum**(식별번호).

## 2. 통합 설계 — 한 서비스·한 원장, doc_type 분기

`invoice_svc.py` 하나가 doc_type으로 세금계산서·현금영수증 분기. 사업자+세금계산서→TAX_INVOICE, 사업자+현금영수증→CASH_RECEIPT(지출증빙용), 개인→CASH_RECEIPT(소득공제용).

## 3. 스키마 (적용·검증 완료)

`tax_invoices(id, payment_id FK, company_id FK, doc_type[TAX_INVOICE|CASH_RECEIPT], mgt_key, trade_usage, invoicee_type, identity_num, supply_cost, tax, total_amount, nts_confirm_num, status[PENDING|ISSUED|CANCELLED|FAILED], popbill_raw jsonb, issued_at, created_by, created_at)`
- UNIQUE(doc_type, mgt_key) — 중복발행 방지. 마이그레이션: `20260728143944_create_tax_invoices.sql`. Supabase 적용(RLS off).

## 4. 오브젝트 계약 (구현 완료 — invoice_svc.py)

```
issue_tax_invoice(payment_id, invoicee{corpNum,corpName,ceoName,email,...}, by) -> {invoice_id, nts_confirm_num, status}
issue_cash_receipt(payment_id, trade_usage, identity_num, by) -> {invoice_id, nts_confirm_num, status}
cancel(invoice_id, reason, by) -> {status}
status(payment_id) -> [invoices]
handle_webhook(payload) -> None   # 팝빌 상태변경 → tax_invoices.status 동기화(best-effort)
```
- 팝빌 SDK **지연 import**(미설치 시 501, 배포 안전). LinkID/SecretKey·TAI 공급자정보는 env 상수(R-008).
- 발행/취소는 audit(INVOICE_ISSUE/INVOICE_CANCEL).

## 5. 검증 결과 (2026-07-28, MCP)

| 항목 | 상태 | 근거 |
|---|---|---|
| tax_invoices 생성 | VERIFIED | 17컬럼·인덱스5 확인 |
| doc_type/status CHECK | VERIFIED | 잘못된 값 차단 |
| mgt_key UNIQUE(중복발행 방지) | VERIFIED | unique_violation 차단 |
| 세금계산서·현금영수증 2종 삽입 | VERIFIED | 정상 삽입, 롤백으로 residual 0 |
| invoice_svc.py 구현 | VERIFIED | 커밋 18e4f9b |
| **SDK 미설치 배포 안전** | VERIFIED | 팝빌 SDK 미설치인데도 배포 SUCCESS + `/health` 통과 = 지연 import 정상 |
| 실발행(팝빌 호출) | PENDING | 팝빌 가입 + 공동인증서 등록 + LinkID/SecretKey + `pip install popbill` 후 사람 게이트 |

## 6. 실연동 시 필요 (사람 게이트)

1. 팝빌 가입 → LinkID/SecretKey 발급, 테스트 공동인증서 신청
2. `requirements.txt`에 `popbill` 추가
3. env: `POPBILL_LINK_ID`, `POPBILL_SECRET_KEY`, `POPBILL_IS_TEST`, `POPBILL_USER_ID`, `TAI_CORP_NUM/CORP_NAME/CEO_NAME/CORP_ADDR/BIZ_TYPE/BIZ_CLASS`
4. 팝빌 웹훅 Callback URL 등록 → 수신 라우터 배선(handle_webhook)
5. 테스트 환경(IsTest=true)에서 발행 1건 검증 → 운영 전환

## 7. 산출물 (커밋)

1. `supabase/migrations/20260728143944_create_tax_invoices.sql` (적용됨)
2. `services/invoice_svc.py` (신설)
