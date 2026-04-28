# Cursor 작업지시서: SaaS 결제 → 빌링(구독결제) 전환

> **레포**: `taiengineering/taieng` (Cloudflare Pages `taieng-new`)
> **파일**: `nexas/service/saas.html` (84KB)
> **백엔드 준비 완료**: `/payments/billing/pay`, `/payments/inicis/billing/prepare`, `/billing/return`, `/billing/charge`

---

## 변경 1: accept-charset 수정

```bash
grep -n 'euc-kr' nexas/service/saas.html
```

```html
<!-- 찾기 -->
<form id="sp_inicis_form" accept-charset="euc-kr"

<!-- 변경 -->
<form id="sp_inicis_form" accept-charset="UTF-8"
```

## 변경 2: api.taieng.co.kr 도메인 수정

```bash
grep -n 'api\.taieng\.co\.kr' nexas/service/saas.html
```

모든 `api.taieng.co.kr` → `taieng.co.kr/_api` 변경
(Cloudflare Pages Function 프록시 경유, 이니시스 V023 방지)

## 변경 3: spPay 함수 → 빌링 리다이렉트로 교체

현재 `spPay` 함수 (67줄)를 아래로 **전체 교체**:

```javascript
function spPay(e, productType, planCode, amount, goodname) {
  e.preventDefault();

  // 로그인 확인 (기존 로직 유지)
  var userId = localStorage.getItem('tai_user_id');
  if (!userId) {
    alert('로그인이 필요합니다.');
    window.location.href = '/auth/login?redirect=' + encodeURIComponent(window.location.href);
    return;
  }

  // 빌링키 발급 페이지로 리다이렉트
  // 백엔드에서 billing_pay.html 템플릿 렌더 → inilitepay.inicis.com 자동 제출
  var url = 'https://taieng.co.kr/_api/payments/billing/pay'
    + '?user_id=' + encodeURIComponent(userId)
    + '&amount=' + amount
    + '&product_type=' + encodeURIComponent(productType)
    + '&goodname=' + encodeURIComponent(goodname)
    + '&plan_code=' + encodeURIComponent(planCode);
  
  window.location.href = url;
}
```

## 변경 4: INIStdPay.js 스크립트 제거 (선택)

빌링 결제는 INIStdPay를 사용하지 않으므로 아래 스크립트를 제거하거나 주석 처리:

```bash
grep -n 'stdpay\|INIStdPay' nexas/service/saas.html
```

```html
<!-- 제거 또는 주석 처리 -->
<script src="https://stdpay.inicis.com/stdjs/INIStdPay.js"></script>
```

※ `sp_inicis_form` 폼도 더 이상 사용하지 않지만, 다른 곳에서 참조할 수 있으므로 우선 유지.

## 빌링 결제 전체 플로우 (변경 후)

```
1. 사용자: SaaS 페이지 "결제하기" 클릭
2. spPay() → window.location.href = taieng.co.kr/_api/payments/billing/pay?...
3. Cloudflare 프록시 → api.taieng.co.kr/payments/billing/pay
4. 백엔드: run_billing_prepare() → billing_pay.html 템플릿 렌더
5. billing_pay.html: 자동으로 inilitepay.inicis.com에 form POST
6. 이니시스: 빌링키 발급 화면 (카드 정보 입력)
7. 사용자: 카드 입력 → 빌링키 발급
8. 이니시스 → taieng.co.kr/_api/payments/inicis/billing/return POST
9. 백엔드: run_billing_return() → billkey 저장 + 구독 활성화
10. 리다이렉트 → /payments/result (결제 완료 페이지)
```

## 검증

변경 후:
1. `taieng.co.kr/service/saas` 접속
2. 아무 플랜 "결제하기" 클릭
3. 이니시스 빌링키 발급 화면 표시 확인
4. V023 에러 없음 확인

## 가격 참고 (VAT 별도, 백엔드에서 자동 추가)

| onclick 파라미터 | 공급가액 | 결제금액(VAT포함) |
|---|---|---|
| BUILDING_BASIC, 145000 | 145,000 | 159,500 |
| BUILDING_STANDARD, 249000 | 249,000 | 273,900 |
| INDUSTRY_STARTER_V2, 79000 | 79,000 | 86,900 |
| INDUSTRY_BUSINESS_V2, 149000 | 149,000 | 163,900 |
| INDUSTRY_PRO_V2, 249000 | 249,000 | 273,900 |
| CONSTRUCTION_BASIC, 145000 | 145,000 | 159,500 |
| CONSTRUCTION_PRO, 385000 | 385,000 | 423,500 |

onclick의 amount는 공급가액 그대로 유지. 백엔드 `run_billing_prepare`에서 `add_vat()` 적용됨.
