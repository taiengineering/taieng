# 작업지시서 — /inspection-schedule 회사 스코프 (LEDGER ㊽ / P13)

> 2026-08-17 · 스코프 클러스터 · 대상 `tai-api` · `routers/inspection_schedule.py` (24.3KB)
> 처리: **Cursor / Claude Code** (20KB+ · 보안 변경 · 라이브 테스트 필요)
> 근거: `DESIGN_safe-company-scope-p13_2026-08-17.md` + 정본 `routers/leader_scope.py`

---

## 문제 (§48)
`/inspection-schedule/*` 에 **인증도 회사 파라미터 강제도 없다.** `company_id` 는 클라이언트가 주는 선택 쿼리라, 안 주면 **전 테넌트 합계**가 나오고, 남의 company_id 를 주면 타사 데이터가 보인다. safe 어드민은 항상 토큰을 보내므로(useTaiApi) 인증 추가는 안전하다.

## 공통 패턴 (leader_scope 와 동일)
```python
from routers.auth import get_current_user

WIDE = ("ALL",)   # 이 라우터는 회사 경계가 기준. ALL(플랫폼 총관리자)만 무제한.

def _scope(supabase, role_code):
    r = supabase.table("role_data_scope").select("scope_type").eq("role_code", role_code).limit(1).execute()
    return (r.data[0]["scope_type"] if r.data and r.data[0].get("scope_type") else "TEAM")
```
- 모든 라우트에 `current = Depends(get_current_user)`.
- `scope_type == "ALL"` → 종전대로 무제한(어드민).
- 그 외 → **토큰 company_id 로 강제**(클라이언트 company_id 무시).

## 엔드포인트별 적용

| 엔드포인트 | 조치 |
|---|---|
| `GET /summary` | 비-ALL: `company_id = current["company_id"]` 강제(클라 파라미터 덮어씀). **전 테넌트 합계 차단 핵심.** |
| `GET /sets` | 동일 — 비-ALL 은 company_id 강제. |
| `GET /sets/{id}` · `PATCH /sets/{id}` · `POST /sets/{id}/confirm-anchor` | 대상 set 의 `company_id != 토큰` 이고 비-ALL 이면 **404**(존재 숨김). |
| `GET /rules/{id}/factories` | 비-ALL: factories 조회에 `.eq("company_id", 토큰)` 추가 — 지금은 전사 시설을 반환한다. |
| `GET /sets/summary-by-rule` | 비-ALL: inspection_sets 집계에 company_id 필터. (전사 통계이므로 ALL 아니면 자사로 한정) |
| `POST /generate` | 비-ALL: factory_ids 각각이 **토큰 company_id 소속인지 확인** 후에만 생성(남의 시설에 세트 생성 차단). |
| `GET /rules` | 마스터 카탈로그(회사 무관 법령 목록) — 인증만 추가, 회사 필터 불필요. |

## 회귀 금지
- **ALL(어드민) 경로는 종전 동작 유지** — 전사 조회·생성이 되어야 한다.
- 산출 로직(next_planned_date·휴무 보정)·응답 형태 불변. 스코프 가드만 추가.

## 완료 판정 (라이브 2종, 둘 다)
1. **고객 토큰**: `/summary`·`/sets` 가 자사 건수만. 남의 company_id 넣어도 자사만(또는 무시). 남의 set_id → 404.
2. **어드민(ALL) 토큰**: 전사 조회·생성 종전대로(회귀 없음).
운영 로그: project 7c3ab53b… / tai-api-prod 4cf52678… / production 9dacb6f0….

## 헬프센터
반영 확인 후 `engine-schedule` 문서에서 "숫자가 전 테넌트 합계" 경고 제거 가능(§48). 단 §47(참조 테이블 개명)은 별건.
