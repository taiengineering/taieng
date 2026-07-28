---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-1 RefundService — refunds 대장 + 이니시스 환불 실연동
version: 1
status: ACTIVE
owner: taiwang
---

# WO-1 — RefundService (refunds 대장 + 이니시스 환불 실연동)

- **작성일:** 2026-07-28
- **Goal:** G-ms4je4z3-33eada
- **상위:** WORKPLAN_admin-rebuild-object-oriented_v1.md §4 P0 WO-1
- **오브젝트:** RefundService (도메인 서비스, 상태 PARTIAL → IMPLEMENTED 목표)
- **닫는 시나리오:** S3(이중결제 환불)·S4(청약철회 전체환불)·S5(부분환불)

---

## 1. 현황 (실측 확정)

- `services/payment_svc.py`: `run_refund`·`run_partial_refund` 둘 다 `raise PaymentPrepareError(501)`. **미구현.**
- `routers/payment.py`: `POST /payments/{id}/refund`·`/partial-refund` 라우터는 존재(서비스만 비어있음).
- `services/payment_helpers.py`: `REFUND_URL=https://iniapi.inicis.com/api/v1/refund`, `INICIS_INIAPI_KEY`, `INICIS_CLIENT_IP=115.68.227.222`, `sha512()`, `ts_yyyymmddhhmmss()` 모두 준비됨.
- `payments` 컬럼: `inicis_tid`(취소 대상 tid), `total_amount`, `pg_method`, `payment_type`, `status_code`.
- `refunds` 테이블: **없음**(실측).

## 2. 이니시스 취소/환불 규격 (INICIS_INTEGRATION_SPEC §4)

- URL `https://iniapi.inicis.com/api/v1/refund`, Key=INIAPI Key, timestamp=YYYYMMDDhhmmss, clientIp=115.68.227.222.
- **전체취소** hashData = `SHA512(INIAPIKey + type + paymethod + timestamp + clientIp + mid + tid)`
  - params: type="Refund", paymethod(Card|Vacct…), timestamp, clientIp, mid, tid, msg(사유), hashData
- **부분취소** hashData = `SHA512(INIAPIKey + type + paymethod + timestamp + clientIp + mid + tid + price + confirmPrice)`
  - 추가 params: price(취소금액), confirmPrice(잔여금액=total-누적취소-price)
- 성공: resultCode="00".

## 3. 오브젝트 계약 (WORKPLAN §2-A 고정)

```
run_refund(payment_id, reason, by) -> {status, refund_id, inicis}
run_partial_refund(payment_id, amount, reason, by) -> {status, refund_id, cumulative}
```
- 본문은 신규 `services/refund_svc.py`에 구현하고 `payment_svc.py`는 위임(파일 비대화 방지, 한 파일 400줄·15KB 이내 규칙).
- 모든 성공/실패는 `refunds` 대장 기록 + AuditHook(WO-2 배선 전까지는 refunds.processed_by로 최소 추적).

## 4. refunds 대장 스키마 (마이그레이션 파일로 커밋 — AI-003: 적용은 사람)

```sql
CREATE TABLE IF NOT EXISTS public.refunds (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  payment_id    uuid NOT NULL REFERENCES public.payments(id),
  refund_type   text NOT NULL CHECK (refund_type IN ('FULL','PARTIAL')),
  amount        integer NOT NULL CHECK (amount > 0),
  cumulative_refunded integer NOT NULL DEFAULT 0,
  reason_code   text,
  reason_text   text NOT NULL,
  inicis_tid    text,
  inicis_refund_tid text,
  inicis_raw    jsonb,
  status        text NOT NULL DEFAULT 'REQUESTED' CHECK (status IN ('REQUESTED','DONE','FAILED')),
  processed_by  text,
  created_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_refunds_payment ON public.refunds(payment_id);
```
- 불변식: 한 payment 다건 허용, `SUM(amount) WHERE status='DONE' ≤ payments.total_amount`. 서비스 로직에서 강제(부분취소 시 confirmPrice 계산에 사용).
- `reason_text` NOT NULL(사유 강제 — Stripe 벤치마크).

## 5. 서비스 로직 순서 (refund_svc.py)

**전체취소 run_refund:**
1. payment 조회(status_code='SUCCESS', inicis_tid 존재 확인). 아니면 400.
2. 기존 DONE 환불 합계 조회 → 이미 전액 환불이면 409.
3. refunds INSERT status='REQUESTED'(감사 흔적 선기록).
4. 이니시스 refund 호출(전체취소 해시). 프록시(OUTBOUND_PROXY) 경유.
5. resultCode='00' → refunds status='DONE', inicis_refund_tid·raw 기록, payments.status_code='CANCELLED'.
6. 실패 → refunds status='FAILED', fail 사유 raw 저장, payments 불변.

**부분취소 run_partial_refund(amount):**
1~2. 동일 + 누적 환불액 계산. `amount + 누적 > total_amount`이면 400(원금 초과 금지).
3. confirmPrice = total_amount - 누적 - amount.
4. refunds INSERT REQUESTED → 이니시스 부분취소 호출(price=amount, confirmPrice).
5. 성공 → DONE, cumulative_refunded 갱신. 전액 도달 시 payments.status_code='CANCELLED', 아니면 'PARTIAL_REFUNDED'.
6. 실패 → FAILED.

## 6. 완료 판정 (IMPLEMENTED)

- `raise 501` 2개 제거, 계약 시그니처대로 구현.
- refunds 기록 + 원금초과 차단 + 누적 검증 동작.
- `/health` 200 유지. DDL은 마이그레이션 파일(사람 적용).
- ⚠️ 실제 이니시스 호출 검증(VERIFIED)은 프록시·INIAPI 키·실거래 tid 필요 → 사람 게이트. 코드 IMPLEMENTED까지가 이 WO 범위.

## 7. 산출물

1. `supabase/migrations/*_create_refunds.sql` (migration 도구, 사람 적용)
2. `services/refund_svc.py` (신규, 실연동 본문)
3. `services/payment_svc.py` 위임 수정(501 → refund_svc 호출)
4. 배포·검증은 사람 게이트(프록시·키·실거래 필요)
