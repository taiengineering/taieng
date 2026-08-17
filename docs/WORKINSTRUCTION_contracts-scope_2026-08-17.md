# 작업지시서 — /contracts·/quotes 회사 스코프 (LEDGER §38·§35 / P13)

> 2026-08-17 · 스코프 클러스터 · 대상 `tai-api` · `routers/contracts.py` (26KB)
> 처리: **Cursor / Claude Code** (20KB+ · 보안 변경 · 라이브 테스트 필요)
> 근거: `DESIGN_safe-company-scope-p13_2026-08-17.md` + 정본 `routers/leader_scope.py`

---

## 문제
`routers/contracts.py` 는 **인증이 전혀 없다.**
- **§38**: `GET /contracts?company_id=` 는 클라이언트가 준 company_id 를 그대로 신뢰, `GET /contracts/{id}`·`/history` 는 스코프 검사 없음 → **타사 계약 열람 가능.**
- **§35**: my-contract(고객 결제내역)가 자사 계약을 못 본다 → 토큰 company_id 로 조회하면 함께 풀린다.
safe 어드민은 항상 토큰을 보내므로(useTaiApi) 인증 추가는 안전하다.

## 공통 패턴 (leader_scope 와 동일)
```python
from routers.auth import get_current_user

def _scope(supabase, role_code):
    r = supabase.table("role_data_scope").select("scope_type").eq("role_code", role_code).limit(1).execute()
    return (r.data[0]["scope_type"] if r.data and r.data[0].get("scope_type") else "TEAM")

def _is_admin(ctx_scope): return ctx_scope == "ALL"   # 플랫폼 총관리자만 전사
```
모든 라우트에 `current = Depends(get_current_user)` 추가.

## 엔드포인트 분류·조치

### A. 읽기 — 비-ALL 은 자사로 강제/소유권 확인 (§38·§35 핵심)
| 엔드포인트 | 조치 |
|---|---|
| `GET /contracts` | 비-ALL: `company_id = 토큰` 강제(클라 파라미터 덮어씀). **데모 제외 로직은 ALL 경로에서만 유지.** |
| `GET /contracts/{id}` · `GET /contracts/{id}/history` | 대상 계약 `company_id != 토큰` & 비-ALL → **404**(존재 숨김). |
| `GET /quotes` | 비-ALL: `company_id = 토큰` 강제. |
| `GET /quotes/{id}` | 대상 견적 `company_id != 토큰` & 비-ALL → 404. |

### B. 계약 수명주기 쓰기 — 어드민(ALL) 전용
`POST /contracts`(생성) · `PATCH /contracts/{id}` · `PATCH /contracts/{id}/status` · `POST /contracts/{id}/activate|payment|suspend|cancel`
→ **비-ALL 이면 403.** (고객은 계약 상태를 바꾸지 않는다. 활성화·입금확인·정지·취소는 운영자 행위.)

### C. 견적 쓰기 — 기본 어드민(ALL) 전용, 단 확인 필요
`POST /quotes`(생성) · `PATCH /quotes/{id}` · `POST /quotes/{id}/confirm` · `POST /quotes/{id}/convert`
→ 기본 **비-ALL 403**.
**〔확인〕** 고객 화면에서 이 중 하나라도 직접 호출하는 자가서비스 흐름이 있으면(예: 고객이 스스로 견적→계약 전환), 그 엔드포인트만 403 대신 **자사 company_id 로 스코프**(생성 시 body.company_id 를 토큰으로 강제, convert 시 견적 소유권 확인)로 바꾼다. safe 프런트 호출부 확인 후 결정.

## 회귀 금지
- **ALL(어드민) 경로는 종전 동작 유지** — 전사 목록·전체 company_id 조회·모든 수명주기 조작 가능.
- 금액 계산(VAT)·상태 전이 규칙·응답 형태 불변. 스코프 가드만 추가.
- 라우트 순서 불변(`/contracts/{id}/status` 등 고정 세그먼트 유지).

## 완료 판정 (라이브 2종, 둘 다)
1. **고객 토큰**: `/contracts`·`/quotes` 가 자사만. 남의 company_id 넣어도 자사만. 남의 계약 id → 404. my-contract 에 **자사 결제내역이 보인다**(§35 해소). 수명주기 쓰기 → 403.
2. **어드민(ALL) 토큰**: 전사 목록·조회·활성화·입금확인·정지·취소 종전대로(회귀 없음).
운영 로그: project 7c3ab53b… / tai-api-prod 4cf52678… / production 9dacb6f0….

## 헬프센터
반영 확인 후 `GUIDE-safe-my-contract` 의 §35 danger 제거 가능(고객이 자기 결제내역을 본다).
