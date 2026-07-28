---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-5 SoftDelete — 휴지통(삭제·복구)
version: 2
status: ACTIVE
owner: taiwang
---

# WO-5 — SoftDelete (deleted_at 휴지통 + 복구)

- **작성일:** 2026-07-28 (v2: 검증 반영)
- **Goal:** G-ms4je4z3-33eada
- **상위:** WORKPLAN §4 P0 WO-5
- **오브젝트:** SoftDelete (도메인 서비스, 신설)
- **닫는 시나리오:** S11(실삭제 대신 휴지통, 복구 가능)
- **최종 상태:** 코드·배포·스키마·왕복로직 **VERIFIED**.

---

## 1. 현황 (실측)

- companies / factories / users / company_contacts: 모두 `is_active`만, `deleted_at` 없음 → 추가.

## 2. 설계 — is_active vs deleted_at 분리

- `is_active` = 활성/비활성(정지·재개, WO-6). 데이터 살아있음.
- `deleted_at` = 휴지통(삭제·복구, WO-5). NULL=정상, NOT NULL=삭제됨.
- soft delete는 물리 DELETE 없이 `deleted_at=now()` 마킹, 복구는 NULL. 기본 조회는 `deleted_at IS NULL`만.

## 3. 스키마 (적용·검증 완료)

- 4개 테이블 `deleted_at timestamptz` 추가 + 부분 인덱스(`WHERE deleted_at IS NULL`).
- 마이그레이션: `20260728145433_add_deleted_at_softdelete.sql`. Supabase 적용(ALTER, 기존 데이터 무영향).

## 4. 오브젝트 계약 (구현 완료 — soft_delete_svc.py)

```
soft_delete(table, id, by, reason=None) -> {ok, deleted_at}
restore(table, id, by) -> {ok}
list_trash(table, limit, offset) -> [rows]   # deleted_at NOT NULL
```
- 화이트리스트 `_ALLOWED={companies,factories,users,company_contacts}`. 그 외 400(임의 테이블 조작 차단).
- 물리 DELETE 절대 없음. soft_delete/restore는 audit(DATA_SOFT_DELETE/DATA_RESTORE).

## 5. 검증 결과 (2026-07-28, MCP 트랜잭션 롤백)

| 항목 | 상태 | 근거 |
|---|---|---|
| deleted_at 컬럼(4개) + 부분인덱스(4개) | VERIFIED | 카운트 4/4 확인 |
| soft_delete 마킹 | VERIFIED | deleted_at 세팅 확인 |
| 휴지통 조회(NOT NULL) 잡힘 | VERIFIED | in_trash=true |
| 활성 조회(IS NULL)에서 제외 | VERIFIED | in_active=false |
| restore 왕복 | VERIFIED | deleted_at=NULL 복구 |
| 실데이터 무오염 | VERIFIED | 전체 롤백, factories 휴지통 0건 |
| soft_delete_svc.py 구현 | VERIFIED | 커밋 6b4e4fc |
| Railway 배포 | VERIFIED | SUCCESS + `/health` 통과 |

## 6. 산출물 (커밋)

1. `supabase/migrations/20260728145433_add_deleted_at_softdelete.sql` (적용됨)
2. `services/soft_delete_svc.py` (신설)
