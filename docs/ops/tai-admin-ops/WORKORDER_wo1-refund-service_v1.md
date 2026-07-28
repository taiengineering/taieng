---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-1 RefundService — refunds 대장 + 이니시스 환불 실연동
version: 2
status: ACTIVE
owner: taiwang
---

# WO-1 — RefundService (refunds 대장 + 이니시스 환불 실연동)

- **작성일:** 2026-07-28 (v2: 검증 결과 반영)
- **Goal:** G-ms4je4z3-33eada
- **상위:** WORKPLAN_admin-rebuild-object-oriented_v1.md §4 P0 WO-1
- **오브젝트:** RefundService (도메인 서비스)
- **닫는 시나리오:** S3(이중결제 환불)·S4(청약철회 전체환불)·S5(부분환불)
- **최종 상태:** 코드·배포·스키마·제약 **VERIFIED**. 실거래 환불 1건만 실결제 발생 시 검증 예정.

---

## 8. 검증 결과 (2026-07-28, MCP 실측)

| 항목 | 상태 | 근거 |
|---|---|---|
| refund_svc 구현 | VERIFIED | 커밋 1b00ff0 — 전체/부분환불 이니시스 규격대로 |
| payment_svc 위임(501 제거) | VERIFIED | 커밋 c137e361 |
| Railway 배포 | VERIFIED | 배포 SUCCESS(commit c137e361) + `/health` 통과 = 앱 정상 기동(refund_svc import 무오류) |
| refunds 테이블 생성 | VERIFIED | 13컬럼·인덱스3·CHECK·FK1 전부 확인. Supabase SQL 편집기 적용(RLS off — payments 계열 일관) |
| DB 제약 가드 | VERIFIED | FK/amount>0/refund_type/status 4개 가드 전부 작동. 트랜잭션 롤백으로 실데이터 무오염(refunds 0건 확인) |
| 실거래 환불 1건 | PENDING | 실 이니시스 tid 결제가 현재 0건(테스트만 존재). 첫 실결제 발생 시 환불 1건으로 최종 검증 |

**BKP-004 준수:** DDL은 콘솔 직접 실행이 차단되어 마이그레이션 파일(20260728135122_create_refunds_ledger.sql)로 git 고정 후 사람이 적용. 콘솔은 SELECT·검증용으로만 사용.

**RLS 결정:** refunds는 결제 계열이므로 payments/subscriptions/billing_keys와 동일하게 RLS off + service_role(백엔드) 전용 접근. 프론트는 refunds 직접 접근 없이 백엔드 API(`/payments/{id}/refund`)만 경유.

---

## 1. 현황 (실측 확정)

- `services/payment_svc.py`: `run_refund`·`run_partial_refund` 둘 다 과거 `raise 501` → **refund_svc 위임으로 교체 완료.**
- `routers/payment.py`: `POST /payments/{id}/refund`·`/partial-refund` 라우터 존재(변경 없음, 위임으로 자동 연결).
- `services/payment_helpers.py`: `REFUND_URL`, `INICIS_INIAPI_KEY`, `INICIS_CLIENT_IP`, `sha512()`, `ts_yyyymmddhhmmss()` 준비됨.
- `payments` 컬럼: `inicis_tid`, `total_amount`, `pg_method`, `payment_type`, `status_code`.
- `refunds` 테이블: **생성 완료(검증됨).**

## 2. 이니시스 취소/환불 규격 (INICIS_INTEGRATION_SPEC §4)

- URL `https://iniapi.inicis.com/api/v1/refund`, Key=INIAPI Key, timestamp=YYYYMMDDhhmmss, clientIp=115.68.227.222(프록시 IP).
- 전체취소 hashData = SHA512(INIAPIKey + type + paymethod + timestamp + clientIp + mid + tid); params: type="Refund", paymethod, timestamp, clientIp, mid, tid, msg(사유), hashData
- 부분취소 hashData = SHA512(... + tid + price + confirmPrice); 추가 params: price(취소금액), confirmPrice(잔여=total-누적-price)
- 성공: resultCode="00".

## 3. 오브젝트 계약 (WORKPLAN §2-A)

```
run_refund(payment_id, reason, by) -> {status, refund_id, inicis}
run_partial_refund(payment_id, amount, reason, by) -> {status, refund_id, cumulative}
```
- 본문은 `services/refund_svc.py`. `payment_svc.py`는 지연 import로 위임(순환 방지, 파일 비대화 방지).
- URL·키·IP는 payment_helpers env 상수만 참조(R-008 하드코딩 금지).

## 4. refunds 대장 스키마 (적용 완료)

```sql
CREATE TABLE IF NOT EXISTS public.refunds (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  payment_id uuid NOT NULL REFERENCES public.payments(id),
  refund_type text NOT NULL CHECK (refund_type IN ('FULL','PARTIAL')),
  amount integer NOT NULL CHECK (amount > 0),
  cumulative_refunded integer NOT NULL DEFAULT 0,
  reason_code text, reason_text text NOT NULL,
  inicis_tid text, inicis_refund_tid text, inicis_raw jsonb,
  status text NOT NULL DEFAULT 'REQUESTED' CHECK (status IN ('REQUESTED','DONE','FAILED')),
  processed_by text, created_at timestamptz NOT NULL DEFAULT now()
);
```
- 불변식: 한 payment 다건 허용, `SUM(amount WHERE status='DONE') ≤ payments.total_amount`. 서비스 로직 강제(부분취소 confirmPrice 계산).
- `reason_text` NOT NULL(사유 강제 — Stripe 벤치마크).

## 5. 서비스 로직 (refund_svc.py — 구현 완료)

**전체취소 run_refund:** payment 조회(SUCCESS·tid 확인) → 누적 DONE 합계 → 잔여≤0이면 409 → refunds REQUESTED 선기록 → 이니시스 전체취소 호출(프록시 경유) → '00'이면 DONE + payments CANCELLED, 실패면 FAILED.

**부분취소 run_partial_refund(amount):** 동일 + `done+amount>total`이면 400(원금초과 차단) → confirmPrice 계산 → 부분취소 호출 → 성공 시 누적 갱신, 전액 도달 CANCELLED / 아니면 PARTIAL_REFUNDED.

## 6. 완료 판정 (달성)

- `raise 501` 2개 제거 ✅ / refunds 기록·원금초과 차단·누적 검증 로직 ✅ / `/health` 200 유지 ✅ / DDL 마이그레이션 경로 ✅.
- 실 이니시스 호출(실거래) 검증만 실결제 발생 대기.

## 7. 산출물 (전부 커밋됨)

1. `supabase/migrations/20260728135122_create_refunds_ledger.sql`
2. `services/refund_svc.py` (신규)
3. `services/payment_svc.py` (위임 수정)
4. refunds 테이블 DB 적용 완료(검증됨)
