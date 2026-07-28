---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-14 StatsProvider 경영 지표
version: 1
status: ACTIVE
owner: taiwang
---

# WO-14 — StatsProvider (경영 지표)

- **작성일:** 2026-07-28
- **Goal:** G-ms4je4z3-33eada
- **상위:** WORKPLAN §4 P2 WO-14
- **오브젝트:** stats_provider_svc(신설) + 지표 엔드포인트
- **닫는 시나리오:** S14(매출·구독·전환을 한눈에)

---

## 1. 현황 (실측)

- 기존 `admin_stats`(dashboard_stats MV): **자산 수**(회사·시설·계약·회원·진단·점검·설비). "얼마나 있나".
- 부족: **경영 지표**(매출·구독·전환·결제 성공률). "얼마 버나·잘 되나".
- 소스: subscriptions(status/amount/product_type/started_at/cancelled_at), payments(status_code/total_amount/paid_at/product_type), diagnosis_purchases(price/status/paid_at).
- 결제 상태값(system_codes payment_status): PENDING/SUCCESS/FAILED/CANCELLED.

## 2. 설계 — 경영 지표 집계

**`services/stats_provider_svc.py`(신설):**
- `revenue()`: 총 결제 매출(SUCCESS 합), 상품유형별 매출(product_type), 진단 매출(diagnosis_purchases).
- `subscription_metrics()`: MRR(ACTIVE subscriptions.amount 합), 활성 구독 수, 해지 수(cancelled), 상품유형별 구독.
- `payment_health()`: 결제 성공률(SUCCESS/(SUCCESS+FAILED)), 실패 수, 대기 수.
- `conversion()`: 진단→SaaS 전환(진단 구매 회사 중 SaaS 구독 보유 비율). 전환 추적 컬럼 없어 company_id 교집합으로 간접 산출.
- `get_stats()`: 종합. 오류 격리.

## 3. 엔드포인트

- `GET /stats/business` — 경영 지표 종합(매출·구독·결제건전성·전환).

## 4. 완료 판정 (IMPLEMENTED)

- stats_provider_svc 집계, 라우터, 등록.
- SUCCESS 기준 매출·MRR·성공률·전환 산출. 오류 격리.
- `/health` 200, 배포 SUCCESS. 목업 표본으로 집계 동작 확인.

## 5. 산출물

1. `services/stats_provider_svc.py`
2. `routers/stats_provider.py`
3. router_registry 등록(external)
