# Cursor 작업지시: 계약내역 페이지 — 결제내역 + 기간연장

> 대상: tai-admin (tadmin/ + site/ 동기화)
> 파일: my-contract.html (15KB)

## 현재: 계약 목록만 있음

## 추가 1: 결제내역 섹션
- GET /payments?company_id=X
- payments 테이블: paid_at, plan_code, payment_method, inicis_card_name, total_amount, period_months, status_code, expired_at
- 상태 배지: PAID(완료), PENDING_VBANK(대기), CANCELLED(취소), FAILED(실패)

## 추가 2: 기간연장 버튼
- 활성 계약 카드에 "기간연장" 버튼
- 연장 모달: 기간 선택(1/3/6/12개월) → 금액 계산 → KG이니시스 결제
- POST /payment/request (payment_type: 'RENEWAL')
- 이니시스 JS SDK: INIStdPay.pay()
- 결제 완료 → payment_post_process.py → contracts.end_date 연장

## BE 확인
1. GET /payments 엔드포인트 존재 확인
2. RENEWAL payment_type 처리 확인
3. GET /price-plans 가격 조회
