# Cursor 작업지시: 결제→계약→알림 자동화 플로우

> 대상: `tai-api` (main 브랜치)
> 핵심 파일: `routers/payment.py` (52KB), `routers/contracts.py`
> 신규 파일: `services/payment_post_process.py`
> 원칙: payment.py 최소 수정 — 서비스 함수 호출 1줄 추가만

---

## 1. 전체 플로우

```
마케팅사이트 결제 (KG이니시스 V3)
  → PG 승인 콜백 → payments UPDATE (status_code: PAID)
  → ★ payment_post_process.on_payment_success(payment_id)
      ├─ ① contracts INSERT (plan_code, 기간, 금액)
      ├─ ② payments.contract_id UPDATE (생성된 계약 연결)
      └─ ③ 알림 발송 (SMS + Email + 인앱)
  → 사용자 로그인 시 fetchContractInfo() → 등급 반영 → 메뉴 활성화
```

---

## 2. 핵심 구현

### 신규: `services/payment_post_process.py`

- `on_payment_success(payment_id)` — 결제 완료 후처리
  - payments 조회 → status_code == PAID 확인
  - 중복 방지: contract_id 이미 있으면 스킵
  - contracts INSERT (plan_code, company_id, 기간, 금액)
  - payments.contract_id 연결
  - 기존 ACTIVE 계약 EXPIRED 처리
  - SMS(MessageMi) + Email + 인앱 알림 발송

### payment.py 수정 — 최소 1줄

결제 status_code → PAID 변경 직후에:
```python
try:
    from services.payment_post_process import on_payment_success
    await on_payment_success(str(payment_id))
except Exception as e:
    logger.error(f"Payment post-process failed: {e}")
```

### PLAN_MAP (menu-tadmin.js와 동일)
```
BUILDING_LITE/BASIC/STANDARD/CUSTOM → FACILITY 1/2/3/4
INDUSTRY_STARTER_V2/BUSINESS_V2/PRO/CUSTOM_V2 → INDUSTRIAL 1/2/3/4
CONSTRUCTION_STANDARD_V2/PREMIUM_V2/CUSTOM_V2 → CONSTRUCTION 1/2/3
```

---

## 3. 체크리스트

- [ ] services/payment_post_process.py 생성
- [ ] payment.py PAID 변경 지점 찾아서 hook 추가
- [ ] SMS: utils/messagemi.py send_sms() 확인
- [ ] Email: 유틸 없으면 TODO
- [ ] 테스트 결제 → contracts 생성 확인
