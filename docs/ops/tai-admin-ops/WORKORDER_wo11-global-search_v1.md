---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-11 GlobalSearch 교차검색
version: 1
status: ACTIVE
owner: taiwang
---

# WO-11 — GlobalSearch (교차검색)

- **작성일:** 2026-07-28
- **Goal:** G-ms4je4z3-33eada
- **상위:** WORKPLAN §4 P1 WO-11 (P1 마지막)
- **오브젝트:** global_search_svc(신설) + 검색 엔드포인트
- **닫는 시나리오:** S29(한 검색창에서 회사·회원·사업장·결제 교차검색)

---

## 1. 대상 (실측 확정)

| 타입 | 검색 컬럼 | 이동 |
|---|---|---|
| company | name, business_number, company_code, representative_name, contact_phone, contact_email | 고객360 |
| user | name, phone, email, user_code, username | 회원 상세 |
| factory | name, site_code, manager_name, manager_phone | 사업장 상세 |
| payment | inicis_order_id, inicis_tid | 결제 원장 |

- 모두 company_id 축으로 연결(회사=본체, 나머지는 company_id 보유). soft delete 반영(deleted_at IS NULL).

## 2. 설계

**`services/global_search_svc.py`(신설):**
- `search(query, types?, limit_per_type=5)`: 4개 테이블 병렬(순차) 조회, ilike 부분일치.
- 각 결과: `{type, id, title, subtitle, company_id}` 정규화. 어드민이 바로 이동.
- types 필터(선택): 특정 타입만 검색.
- 짧은 검색어(2자 미만) 방어.

## 3. 엔드포인트

- `GET /search?q=...&types=company,user&limit=5` — 통합 검색.

## 4. 완료 판정 (IMPLEMENTED)

- global_search_svc.search 구현, 라우터, 등록.
- 4타입 교차검색, 정규화 결과. soft delete 반영.
- `/health` 200, 배포 SUCCESS. 목업 표본으로 검색 동작 확인.

## 5. 산출물

1. `services/global_search_svc.py`
2. `routers/global_search.py`
3. router_registry 등록(saas_core)
