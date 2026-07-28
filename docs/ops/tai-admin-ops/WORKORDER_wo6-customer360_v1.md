---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-6 고객360 — 통합 집계 API
version: 2
status: ACTIVE
owner: taiwang
---

# WO-6 — 고객360 (통합 집계 API)

- **작성일:** 2026-07-28 (v2: 검증 반영)
- **Goal:** G-ms4je4z3-33eada
- **상위:** WORKPLAN §4 P1 WO-6
- **오브젝트:** Customer360 집계 서비스 (백엔드) — A범위(집계 API)까지. 화면은 후속.
- **최종 상태:** 코드·배포·집계정합성 **VERIFIED**. 화면(B범위)은 미착수.

---

## 1. 현황 (실측 — 기존 자산 존재)

`routers/companies.py`(v2.1.0)에 회사 하위 조회가 이미 개별 엔드포인트로 존재(`/{id}`, `/{id}/users`, `/{id}/factories`, `/{id}/contacts`, `/{id}/contracts`, `/{id}/files`). 응답 표준 `{"status":"success","data":{...}}`. 원천 전부 company_id 연결(refunds만 payments 경유).

→ 고객360은 신설이 아니라 흩어진 조회를 한 번에 묶는 **집계 엔드포인트 추가**.

## 2. 구현 (완료)

- **`services/customer360_svc.py`** (신설): `get_summary(company_id, audit_limit)` — 회사상세 + counts(시설/회원/담당자, deleted_at IS NULL) + 결제요약(성공건 total/count/최근) + 구독(최근) + 진단 + credit_balance(credit_svc 재사용) + 세금계산서/현금영수증(ISSUED/CANCELLED) + 환불(payments 경유 DONE) + 최근감사(admin_ops_audit_logs) + 온보딩(null, WO-17 예약).
- **`routers/customer360.py`** (신설, 얇은 위임): `GET /companies/{company_id}/360`.
- **`router_registry/saas_core.py`**: `routers.customer360` 등록(companies 뒤).

## 3. 검증 결과 (2026-07-28)

| 항목 | 상태 | 근거 |
|---|---|---|
| customer360_svc 구현 | VERIFIED | 커밋 02a932a |
| customer360 라우터 + 등록 | VERIFIED | 커밋 6246517·e7a05022 |
| 앱 기동(import 정상) | VERIFIED | 배포 SUCCESS + `/health` 통과 |
| 집계 로직 정합성 | VERIFIED | 코드 집계식 = SQL 정답값. 표본 `타이엔지니어링`(f49f05da): 시설6·회원2·결제2건·성공0·구독0·진단0 |
| 원천 읽기만(복제 없음) | VERIFIED | 각 원천 count/sum 즉시 집계, credit_svc.balance 재사용 |
| soft delete 반영 | VERIFIED | factories/users/contacts는 deleted_at IS NULL 기준 |

> 실제 HTTP 호출 검증은 컨테이너 네트워크 차단으로 불가 → 배포 성공(import·라우팅 정상) + 코드-정답 집계 대조로 검증.

## 4. 후속 (B범위 — 화면)

- 고객360 화면(admin, Vuexy/HTML)에서 이 API 소비. WO-7(결제·구독 원장)과 함께 화면 레이어에서 진행.
- 온보딩 요약은 WO-17(onboarding 테이블) 완료 후 null→실제값.

## 5. 산출물 (커밋)

1. `services/customer360_svc.py` (신설)
2. `routers/customer360.py` (신설)
3. `router_registry/saas_core.py` (customer360 등록)
