---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-11 GlobalSearch 교차검색
version: 2
status: DONE
owner: taiwang
---

# WO-11 — GlobalSearch (교차검색)

- **작성일:** 2026-07-28 (v2: 검증 완료)
- **Goal:** G-ms4je4z3-33eada
- **상위:** WORKPLAN §4 P1 WO-11 (P1 마지막)
- **최종:** VERIFIED. **P1 전체 완료.**

---

## 1. 대상 (실측 확정)

| 타입 | 검색 컬럼 | 이동 |
|---|---|---|
| company | name, business_number, company_code, representative_name, contact_phone, contact_email | 고객360 |
| user | name, phone, email, user_code, username | 회원 상세 |
| factory | name, site_code, manager_name, manager_phone | 사업장 상세 |
| payment | inicis_order_id, inicis_tid | 결제 원장 |

## 2. 구현 (완료)

**`services/global_search_svc.py`** (커밋 3a8132a):
- `search(query, types?, limit_per_type)`: 4타입 ilike 부분일치, soft delete 반영(deleted_at IS NULL).
- 결과 정규화 `{type, id, title, subtitle, company_id}` — 어드민이 바로 이동. 2자 미만 방어.

**`routers/global_search.py`** (커밋 82ce2e4): `GET /search?q=&types=&limit=`. saas_core 등록 26e087e.

## 3. 검증 결과

| 항목 | 상태 | 근거 |
|---|---|---|
| 교차검색 ilike + soft delete | VERIFIED | SQL 표본: 'TAI' → company 2 hits, factory 0 hits (부분일치·필터 정확) |
| 결과 정규화(type/id/title/company_id) | VERIFIED | 코드 대조 |
| types 필터 + 2자 방어 | VERIFIED | 코드 대조 |
| 앱 기동·라우팅 | VERIFIED | 배포 SUCCESS(26e087e) + `/health` |

## 4. 산출물 (커밋)

1. `services/global_search_svc.py`
2. `routers/global_search.py`
3. `router_registry/saas_core.py` (global_search 등록)

---

## P1 완료 요약 (WO-6~11)

- WO-6 고객360 · WO-7 결제원장 · WO-8 NotifyDispatcher(Gmail 통합) · WO-9/9B 파일뷰+사업장축 · WO-10 연동관제 · WO-11 교차검색 — **전부 VERIFIED/DONE.**
- P0(WO-1~5) + P1(WO-6~11) 완료. 다음 P2(WO-12~17): AutomationEngine·관제홈·StatsProvider·정산세무·공지배너·온보딩체크리스트.
