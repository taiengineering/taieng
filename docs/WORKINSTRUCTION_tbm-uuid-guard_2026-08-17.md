# 작업지시서 — tbm.py get_tbm uuid 가드 (라이브 500 제거)

> 2026-08-17 · Goal G-mswtdmi1-420f8c 별건 (work_schedules 500 후속)
> 대상 `tai-api` · `routers/tbm.py` · 함수 `get_tbm` (GET /{tbm_id})
> 처리 주체: **Cursor / Claude Code** (tbm.py 19.4KB·200+줄 → MCP 전면 재작성 지양, 로컬 편집)

---

## 배경 (운영 로그 실측)

```
routers/tbm.py line 416, get_tbm
postgrest APIError: invalid input syntax for type uuid: "summary" (22P02)
→ GET /tbm/summary = 500
```

프런트가 `GET /tbm/summary` 를 호출하는데 `/tbm/summary` 라우트가 없어,
catch-all `GET /{tbm_id}`(get_tbm)가 "summary"를 `tbm_id` 로 잡아
`.eq("id","summary")` → Postgres uuid 파싱 실패 → **500**.

work_schedules 에 이미 같은 수정을 적용함(PR #146, 094e050f). tbm 은 별도 라우터라 남아 있음.

## 변경

**1) 파일 상단 import 추가**
```python
import uuid
```

**2) uuid 헬퍼 추가 (예: _now 아래)**
```python
def _is_uuid(value: str) -> bool:
    try:
        uuid.UUID(str(value))
        return True
    except (ValueError, AttributeError, TypeError):
        return False
```

**3) get_tbm 시작에 가드 추가**
```python
@router.get("/{tbm_id}")
def get_tbm(tbm_id: str):
    # 비-uuid 경로(/summary 등)가 catch-all 에 잡혀 500(22P02) 나던 것 방지
    if not _is_uuid(tbm_id):
        raise HTTPException(status_code=404, detail="TBM을 찾을 수 없습니다.")
    supabase = get_supabase()
    ...  # 이하 기존 그대로
```

- `get_tbm` 만 손대면 됨(GET catch-all 은 이 하나). 다른 `/{tbm_id}/...` 라우트는 세그먼트가 붙어 "summary"에 안 걸림.
- HTTPException 은 이미 import 되어 있음.

## 범위 (폭주 금지)
`get_tbm` 한 함수 + import/헬퍼 추가만. 다른 TBM 로직·서명·FCM 흐름은 불변.

## 검증
1. `GET /tbm/summary` → 404(500 아님).
2. 정상 uuid 로 `GET /tbm/{실제id}` → 200 정상.
3. 운영 로그(tai-api-prod: project `7c3ab53b…` / service `tai-api-prod 4cf52678…` / env `production 9dacb6f0…`)에서 이 22P02 재발 없음.

## 배포
`main` push → Railway(tai-api-prod) 자동 배포.

---

## 참고 — 근본 원인은 별건(summary원인추적)

프런트가 `/tbm/summary`, `/work-schedules/summary`, `/deterministic-qa/summary`, `/diagnosis/summary` 등
**여러 자원에 `/{자원}/summary` 를 일괄 호출**한다(로그 확인). 이 가드는 500→404 로 크래시만 막는 대응이고,
**그 화면들이 실제로 요약 데이터를 필요로 하는지(→ /summary 엔드포인트 구현) vs 잘못된 호출인지**는
프런트 호출부를 추적해 별도로 판단해야 한다.
