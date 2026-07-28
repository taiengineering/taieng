---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-5 SoftDelete — 휴지통(삭제·복구)
version: 1
status: ACTIVE
owner: taiwang
---

# WO-5 — SoftDelete (deleted_at 휴지통 + 복구)

- **작성일:** 2026-07-28
- **Goal:** G-ms4je4z3-33eada
- **상위:** WORKPLAN §4 P0 WO-5
- **오브젝트:** SoftDelete (도메인 서비스, 신설)
- **닫는 시나리오:** S11(실삭제 대신 휴지통, 복구 가능)

---

## 1. 현황 (실측 확정)

- companies / factories / users / company_contacts: **모두 `is_active`만 존재, `deleted_at` 없음.** id·is_active 공통.

## 2. 설계 — is_active vs deleted_at 분리

두 개념을 명확히 나눈다:
- **`is_active`** = 활성/비활성 (정지·재개). WO-6 회원조작 소관. 데이터는 살아있음.
- **`deleted_at`** = 휴지통 (삭제·복구). 이번 WO-5. `NULL`=정상, `NOT NULL`=삭제됨.

즉 soft delete는 물리 삭제(DELETE)를 하지 않고 `deleted_at=now()`로 마킹, 복구는 `deleted_at=NULL`. 조회 시 기본적으로 `deleted_at IS NULL`만 노출, 휴지통 화면만 `NOT NULL` 조회.

## 3. 스키마 (마이그레이션 git 고정 → 사람 적용)

```sql
ALTER TABLE public.companies        ADD COLUMN IF NOT EXISTS deleted_at timestamptz;
ALTER TABLE public.factories        ADD COLUMN IF NOT EXISTS deleted_at timestamptz;
ALTER TABLE public.users            ADD COLUMN IF NOT EXISTS deleted_at timestamptz;
ALTER TABLE public.company_contacts ADD COLUMN IF NOT EXISTS deleted_at timestamptz;
-- 부분 인덱스: 활성 행 조회 최적화
CREATE INDEX IF NOT EXISTS idx_companies_active ON public.companies(id) WHERE deleted_at IS NULL;
... (factories/users/company_contacts 동일)
```
- 기존 데이터 무영향(전부 deleted_at=NULL=정상).

## 4. 오브젝트 계약 (WORKPLAN §2-A)

```
soft_delete(table, id, by, reason=None) -> {ok, deleted_at}
restore(table, id, by) -> {ok}
list_trash(table, limit, offset) -> [rows]   # deleted_at NOT NULL
```
- 화이트리스트 테이블만 허용(companies/factories/users/company_contacts). 임의 테이블 조작 차단(SQL injection·오조작 방지).
- soft_delete/restore는 audit(`DATA_SOFT_DELETE`/`DATA_RESTORE`) 기록.
- 물리 DELETE 절대 없음. CONFIRMED 레코드 불변 원칙과 일치.

## 5. 서비스 로직 (soft_delete_svc.py)

- `_ALLOWED = {companies, factories, users, company_contacts}`. 그 외 table 인자는 400.
- **soft_delete:** 대상 존재+미삭제 확인 → `deleted_at=now()` UPDATE → audit DATA_SOFT_DELETE(before: deleted_at=null).
- **restore:** 대상 존재+삭제됨 확인 → `deleted_at=NULL` UPDATE → audit DATA_RESTORE.
- **list_trash:** `deleted_at IS NOT NULL` 페이지네이션 조회.

## 6. 완료 판정 (IMPLEMENTED)

- 4개 테이블 deleted_at 컬럼 + 부분 인덱스.
- soft_delete/restore/list_trash 구현, 화이트리스트 가드, 물리삭제 없음.
- 감사 기록. `/health` 200. DDL 마이그레이션 경로.

## 7. 산출물

1. `supabase/migrations/*_add_deleted_at_softdelete.sql`
2. `services/soft_delete_svc.py` (신설)
