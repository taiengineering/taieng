# 작업지시서 — §7 작업자 수동 등록 시 is_active 반영

> 2026-08-18 · LEDGER §7 [낮] · 대상 `tai-api` `routers/worker_registry.py` (28.5KB)
> 처리: **Cursor / Claude Code** (파일 20KB↑ → 로컬 편집 후 push)
> 근거: 소스 직독(v1.4.0). 수동 등록은 is_active 를 받지 못해 항상 재직으로 저장됨.
> 범위: **수동 등록(POST /worker-registry)만.** bulk-import 는 엑셀 템플릿에 is_active 컬럼이 없으므로 불변.

## 문제 (실측)
- `WorkerCreate` 스키마에 `is_active` 필드가 없다 → 프런트가 보내도 Pydantic 이 버린다.
- `create_worker` 가 `"is_active": True, "status_code": "ACTIVE"` 를 하드코딩 → **퇴직 상태로 등록 불가**.
- 정본 쌍: `delete_worker` 는 `is_active=False` ↔ `status_code="INACTIVE"`. 생성도 이 쌍을 따라야 정합.

## 수정 (2곳, 최소)

### 1) WorkerCreate 스키마 — 필드 추가
`Optional` 은 이미 import 되어 있음. `memo` 아래(또는 임의 위치)에 한 줄 추가:
```python
class WorkerCreate(BaseModel):
    factory_id:      str
    name:            str
    phone:           str
    job_type_code:   str              # WJT001~WJT020
    contractor_name: Optional[str] = None
    department:      Optional[str] = None
    start_date:      Optional[str] = None
    birth_date:      Optional[str] = None
    id_number_last4: Optional[str] = None
    memo:            Optional[str] = None
    is_active:       Optional[bool] = True    # ← 추가 (미지정 시 재직)
```

### 2) create_worker — 하드코딩을 body 값으로
현재:
```python
    now = _now_iso()
    data = {
        "factory_id":      body.factory_id,
        "company_id":      company_id,
        "name":            body.name.strip(),
        "phone":           phone,
        "job_type_code":   body.job_type_code,
        "job_type_name":   job_type_name,
        "is_active":       True,
        "status_code":     "ACTIVE",
        "app_installed":   False,
        "created_at":      now,
        "updated_at":      now,
    }
```
변경:
```python
    now = _now_iso()
    is_active = body.is_active if body.is_active is not None else True
    data = {
        "factory_id":      body.factory_id,
        "company_id":      company_id,
        "name":            body.name.strip(),
        "phone":           phone,
        "job_type_code":   body.job_type_code,
        "job_type_name":   job_type_name,
        "is_active":       is_active,
        "status_code":     "ACTIVE" if is_active else "INACTIVE",
        "app_installed":   False,
        "created_at":      now,
        "updated_at":      now,
    }
```
그 외 코드·bulk-import·수정·삭제·초대 로직은 **불변**. 버전 노트 `v1.5.0: 수동 등록 is_active 반영` 한 줄 추가 권장.

## 완료 판정 (라이브)
1. is_active=false 로 수동 등록 → DB `worker_registry` 에 `is_active=false`, `status_code='INACTIVE'` 저장.
2. is_active 미전송(구 프런트) → 종전대로 재직(ACTIVE) 저장(회귀 없음).
3. 목록 `GET /worker-registry?is_active=false` 에 해당 작업자가 나오는지.

## 배포
main push → Railway 자동배포. `railway_list_deployments` SUCCESS 확인. `/health` 200 유지.
