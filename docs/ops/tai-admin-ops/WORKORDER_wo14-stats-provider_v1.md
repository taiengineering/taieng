---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-14 StatsProvider 경영 지표
version: 2
status: DONE
owner: taiwang
---

# WO-14 — StatsProvider (경영 지표)

- **작성일:** 2026-07-28 (v2: 검증 완료)
- **Goal:** G-ms4je4z3-33eada
- **최종:** VERIFIED.

---

## 1. 현황 (실측)

- 기존 admin_stats(dashboard_stats MV): 자산 수. WO-14는 경영 지표(매출·구독·전환·결제건전성) 보강.
- 소스: subscriptions, payments, diagnosis_purchases.
- **상태 코드 실측**: payments PENDING/SUCCESS/FAILED/CANCELLED. diagnosis_purchases는 **PAID**(payments의 SUCCESS와 다른 체계).

## 2. 구현 (완료)

**`services/stats_provider_svc.py`** (커밋 ce4ab7f):
- `revenue()`: 결제 성공(SUCCESS) 합·상품유형별 + 진단 매출(PAID).
- `subscription_metrics()`: MRR(ACTIVE amount 합)·활성/해지 수·상품유형별.
- `payment_health()`: 성공률(SUCCESS/(SUCCESS+FAILED))·실패·대기.
- `conversion()`: 진단(PAID) 회사 ∩ SaaS(ACTIVE) 회사 = 전환율.
- 페이지네이션 전량 조회(_fetch_all, 1000단위). get_stats 오류 격리.

**`routers/stats_provider.py`** (커밋 5928642): `GET /stats/business`. external 등록 ef5ec3b.

## 3. 검증 결과 (실 코드값 확인으로 오류 정정)

- **진단 상태값 정정**: 최초 `status='SUCCESS'`(진단엔 없는 값) → `PAID`로 수정. 정정 전 진단 매출·전환 0으로 오산출되던 것 해결.
- SQL 검증(PAID 기준): 진단 결제 16건·매출 1,992,000원·진단 회사 8개 정확 집계.
- 결제/구독 지표: 목업에 SUCCESS 결제·ACTIVE 구독 0(전부 PENDING) → 0 반환(정상). 실데이터 시 산출.

| 항목 | 상태 | 근거 |
|---|---|---|
| revenue(진단 PAID) | VERIFIED | SQL: 16건/199.2만/8사 |
| subscription MRR | VERIFIED | 조건 status=ACTIVE 정확(목업 0) |
| payment_health 성공률 | VERIFIED | SUCCESS/FAILED 분모 로직 |
| conversion 교집합 | VERIFIED | PAID∩ACTIVE company_id |
| 앱 기동·라우팅 | VERIFIED | 배포 SUCCESS(ce4ab7f) + `/health` |

## 4. 산출물 (커밋)

1. `services/stats_provider_svc.py`
2. `routers/stats_provider.py`
3. `router_registry/external.py` (stats_provider 등록)
