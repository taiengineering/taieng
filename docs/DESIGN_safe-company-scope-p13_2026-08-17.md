# 설계 — 회사 스코프 전수(P13) 공통 방식·라우터 감사 (LEDGER 〔패턴〕)

> 2026-08-17 · 캠페인 레인 A · 근거: `routers/leader_scope.py`(정본 패턴) + 라우터 실측
> LEDGER: "여섯 건이 각각의 결함이 아니라 하나의 설계 공백. 라우터 전수로 한 번에."

---

## 1. 정본 패턴 (leader_scope.py 에서 검증됨)

```python
from routers.auth import get_current_user   # 토큰 → users 행(company_id, role_code, ...)

def _scope_of(supabase, role_code) -> str:   # role_data_scope.scope_type
    # ALL / COMPANY / FACTORY / TEAM. 미정의는 가장 좁게(TEAM).
```

**규칙 — 회사 스코프 리소스에 일괄 적용:**
1. 인증: 모든 대상 라우트에 `current_user = Depends(get_current_user)`.
2. **목록/조회 스코프**: `scope_type == "ALL"`(플랫폼 총관리자) → 무제한(어드민 전체목록 유지). **그 외 전부 → `company_id = current_user["company_id"]` 강제**(클라이언트가 보낸 company_id 는 무시/덮어쓰기).
3. **단건 `/{id}`**: 리소스의 `company_id != 토큰 company_id` 이고 ALL 아니면 **404**(존재 여부도 숨김 — leader_scope 원칙).
4. 클라이언트가 지정하는 하위 id(예: factory_id)는 받되 **내 회사 소속인지 서버가 재확인**.

**핵심: 어드민(ALL) 경로를 깨뜨리지 않는다.** 이중용도 라우터는 role 로 분기.

## 2. 라우터 감사 (실측)

| 라우터 | 현재 상태 | 소유 | 파일 |
|---|---|---|---|
| **`/contracts`** (§38·§35) | **인증 전무.** get_contracts 는 클라 company_id 신뢰, get_contract/{id} 스코프 무검사. **이중용도**(company_id 없으면 어드민 전체). | **Cursor**(26KB) | contracts.py |
| **`/inspection-schedule/*`** (§48) | 인증·회사 파라미터 없음 → **전 테넌트 합계 표시** | 크기 확인 후 저/Cursor | inspection_schedule 계열 |
| **`/education/*`** (§patterns) | 인증 의존성 없음, `localStorage.company_id` 를 쿼리로 | 크기 확인 후 | education.py 계열 |
| **`/factories`** (진단1 경로) | 클라 company_id 그대로 신뢰 | 크기 확인 후 | factories 계열 |
| `/quotes/survey/list` (§51·51-b) | **개인정보 노출 + 무인증 계약** | **지시서 발행됨**(별도) | — |
| `POST /legal-engine/diagnose/step1` | 시설 **소유권 미검사**(존재만 확인) | **GPT(엔진)** | legal_engine |

## 3. 실행 순서 (정보 노출 위험 큰 순)

1. **`/quotes/survey`** — 지시서 완료(51). 
2. **`/inspection-schedule`** — 전 테넌트 합계가 그대로 노출. company_id 강제 시급.
3. **`/contracts`** — 고객이 남의 결제/계약 열람 가능(§38). 단 어드민 전체목록 보존 필수.
4. **`/education`** · **`/factories`** — company_id 강제.
5. **`legal-engine step1`** — GPT 로 이관(소유권 검사 추가).

## 4. 적용 시 라우터별 주의 (contracts 예)

- `get_contracts`(목록): `scope_type=="ALL"` 이면 현행(전체+데모제외) 유지. 아니면 `company_id = 토큰` 강제(클라 파라미터 무시).
- `get_contract/{id}`·`/history`: 토큰 company_id 와 대조, ALL 아니면 404.
- 생성/활성화/정지/취소(`POST .../activate` 등): **어드민(ALL) 전용**으로 가드 — 고객 토큰이면 403.
- my-contract(고객 화면)는 결국 토큰 company_id 로만 조회되므로 §35("고객이 자기 결제내역을 없다고 통보받음")도 함께 풀린다.

## 5. 완료 판정 (라우터마다 라이브 2종)
1. **고객 토큰** — 남의 company_id 를 넣어도 내 회사 데이터만 나온다(또는 403/404).
2. **어드민 토큰** — 전체/타사 조회가 종전대로 동작한다(회귀 없음).
둘 다 만족해야 완료. 배포 후 운영 로그로 확인(project 7c3ab53b… / tai-api-prod 4cf52678… / production 9dacb6f0…).

## 6. 소유 배분
- **Cursor**: contracts(26KB, 이중용도) 및 20KB+ 라우터.
- **저(MCP)**: 20KB 미만 라우터(inspection-schedule/education/factories 중 크기 확인 후).
- **GPT**: legal-engine step1.
- 각 라우터는 `get_current_user`+`_scope_of` 를 leader_scope 와 동일하게 사용. 공통 헬퍼를 shared 모듈로 뽑는 것도 검토(중복 방지).
