# WORKORDER — LEDGER §19 건설 작업자 등록 통합 (worker_registry 명부 + construction_workers 배치)

> 작성 2026-08-18 · 대상 **Cursor**(로컬 `tai-api` 클론에서 반영·배포) · 검증 **기획창(Claude)**
> 성격 **작업지시** — 아래 변경을 그대로 적용하고 main push(→ Railway 자동배포)한다.
> 로컬에서 `ast.parse` 검증 완료. 변경은 정확히 2개 파일, 각 국소 블록이다.

---

## 0. 배경 (실측 근거)

건설 작업자 등록(`POST /construction/sites/{id}/workers`)이 종전에는 `construction_workers` 에만 직접 써서
화면 10필드 중 8개가 버려지고(§19), org(부서·팀·그룹)·리더 체계에서 이탈했다.

**FK 실측**: org 배정·리더는 `worker_registry.id` 를 기준점으로 한다 —
`worker_group.worker_id → worker_registry`, `groups.lead_worker_id → worker_registry`,
`teams.lead_worker_id → worker_registry`. 그리고 `construction_workers.worker_registry_id → worker_registry`.

**데이터 실측(목업)**: construction_workers 전원이 worker_registry_id 로 연결돼 있고, 그 명부 레코드는
`factory_id = NULL` · `company_id` 스코프로 등록돼 있었다(건설현장은 factory_id 미보유 0/1).

→ 선례대로 **등록 시 worker_registry 명부(factory_id=NULL, company 스코프)를 만들고 construction_workers 를
worker_registry_id 로 연결**한다. 이로써 8필드가 명부/배치에 분산 저장되고, 건설 작업자도 worker_registry.id 를
얻어 부서·팀·그룹 배정·리더 지정이 가능해진다.

---

## 1. `schemas/construction.py`

### 1-1. import 교체
```
- from pydantic import BaseModel, Field
+ from pydantic import AliasChoices, BaseModel, ConfigDict, Field
```

### 1-2. `WorkerCreate` 클래스 전체 교체
**기존:**
```python
class WorkerCreate(BaseModel):
    user_id: Optional[str] = None
    worker_name: Optional[str] = None
    worker_phone: Optional[str] = None
    worker_type: Optional[str] = "SUBCON"
    subcontractor_id: Optional[str] = None
    role_code: Optional[str] = None
    join_date: Optional[date] = None
    certification_codes: Optional[str] = None
    safety_edu_date: Optional[date] = None
    safety_edu_hours: Optional[int] = 0
    notes: Optional[str] = None
```
**변경:**
```python
class WorkerCreate(BaseModel):
    """건설 작업자 등록 입력 (LEDGER §19 통합).

    화면(construction-worker-list)이 보내는 필드명을 1급으로 받는다. 등록 시
    worker_registry(통합 명부) + construction_workers(현장배치)를 동시 생성하기 위한 입력이며,
    종전처럼 construction_workers 에만 직접 쓰지 않는다. 종전 서버 필드명
    (worker_phone·join_date·safety_edu_date·notes)도 alias 로 수용해 하위호환을 유지한다.
    """
    model_config = ConfigDict(populate_by_name=True)

    worker_name: str
    phone: Optional[str] = Field(default=None, validation_alias=AliasChoices("phone", "worker_phone"))
    worker_type: Optional[str] = "DIRECT"
    job_type: Optional[str] = None
    company_name: Optional[str] = None
    hire_date: Optional[date] = Field(default=None, validation_alias=AliasChoices("hire_date", "join_date"))
    safety_training_date: Optional[date] = Field(default=None, validation_alias=AliasChoices("safety_training_date", "safety_edu_date"))
    safety_training_hours: Optional[float] = Field(default=None, validation_alias=AliasChoices("safety_training_hours", "safety_edu_hours"))
    memo: Optional[str] = Field(default=None, validation_alias=AliasChoices("memo", "notes"))
    entry_status: Optional[str] = "OFFSITE"
```
> `WorkerPatch`·`EntryPatch` 등 나머지 클래스는 건드리지 않는다. `WorkerCreate` 는 `create_worker` 만 사용한다(다른 호출자 없음).

---

## 2. `routers/construction_workflow_router.py`

### 2-1. import 추가 (파일 최상단)
```
- import uuid
+ import re
+ import uuid
```
> `normalize_date_fields`·`create_record` import 는 다른 함수(create_process/create_work/update_worker 등)에서
> 계속 쓰이므로 **유지**한다. create_worker 만 직접 처리로 바뀐다.

### 2-2. `create_worker` 교체 (앞에 `_iso_date` 헬퍼 추가)
**기존:**
```python
@router.post("/sites/{site_id}/workers")
async def create_worker(site_id: str, body: WorkerCreate):
    site_id = _validate_uuid(site_id)
    supabase = get_supabase()
    try:
        data = body.model_dump(exclude_none=True)
        data["site_id"] = site_id
        data = normalize_date_fields(data, ("join_date", "safety_edu_date"))
        created = create_record(supabase, "construction_workers", data, _now_iso, "등록 실패")
        return {"status": "success", "data": created}
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```
**변경:**
```python
def _iso_date(v) -> Optional[str]:
    """date 객체면 ISO 문자열로, 그 외(str/None)는 그대로."""
    if v is None:
        return None
    return v.isoformat() if hasattr(v, "isoformat") else str(v)


@router.post("/sites/{site_id}/workers")
async def create_worker(site_id: str, body: WorkerCreate):
    """건설 작업자 등록 — 통합 명부(worker_registry) + 현장배치(construction_workers) 동시 생성.

    LEDGER §19: 종전에는 construction_workers 에만 직접 써서 화면 8필드가 버려지고, org
    (부서·팀·그룹)·리더 체계에서 이탈했다. 실측상 org 배정·리더는 worker_registry.id 를
    기준점으로 하고(worker_group·groups.lead_worker_id·teams.lead_worker_id FK),
    construction_workers 는 worker_registry_id 로 명부와 연결된다(기존 데이터 전원 연결·
    worker_registry.factory_id=NULL·company 스코프). 그 선례대로:
      1) worker_registry 명부 생성(factory_id=NULL, company 스코프) — org·리더 편입 가능
      2) construction_workers 현장배치 생성(worker_registry_id 연결 + 건설 특화: 고용형태·
         안전교육·출입상태)
    실패 시 명부 고아를 남기지 않도록 보상 삭제한다.
    """
    site_id = _validate_uuid(site_id)
    supabase = get_supabase()

    name = (body.worker_name or "").strip()
    if not name:
        raise HTTPException(status_code=422, detail="이름은 필수입니다.")

    # site → company_id (worker_registry 는 factory_id 없이 company 스코프로 담는다)
    site = supabase.table("construction_sites").select("company_id").eq("id", site_id).single().execute()
    if not site.data:
        raise HTTPException(status_code=404, detail="현장을 찾을 수 없습니다.")
    company_id = site.data.get("company_id")

    phone = re.sub(r"[^0-9]", "", body.phone or "") or None
    job_label = (body.job_type or "").strip() or None
    contractor = (body.company_name or "").strip() or None
    memo = (body.memo or "").strip() or None
    hire = _iso_date(body.hire_date)
    now = _now_iso()

    # 1) 통합 명부(worker_registry) — factory_id=NULL, company 스코프 (실측 선례)
    reg_payload = {
        "company_id":      company_id,
        "factory_id":      None,
        "name":            name,
        "phone":           phone,
        "job_type_code":   job_label,
        "job_type_name":   job_label,
        "contractor_name": contractor,
        "start_date":      hire,
        "memo":            memo,
        "is_active":       True,
        "status_code":     "ACTIVE",
        "created_at":      now,
        "updated_at":      now,
    }
    reg_payload = {k: v for k, v in reg_payload.items() if v is not None}
    try:
        reg = supabase.table("worker_registry").insert(reg_payload).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"작업자 명부 등록 실패: {e}")
    if not reg.data:
        raise HTTPException(status_code=500, detail="작업자 명부 등록 실패")
    worker_registry_id = reg.data[0]["id"]

    # 2) 현장배치(construction_workers) — 명부 연결 + 건설 특화(고용형태·안전교육·출입)
    edu_hours = int(body.safety_training_hours) if body.safety_training_hours is not None else None
    cw_payload = {
        "site_id":            site_id,
        "worker_registry_id": worker_registry_id,
        "worker_name":        name,
        "worker_phone":       phone,
        "worker_type":        body.worker_type,
        "join_date":          hire,
        "safety_edu_date":    _iso_date(body.safety_training_date),
        "safety_edu_hours":   edu_hours,
        "entry_status":       body.entry_status,
        "notes":              memo,
        "is_active":          True,
        "created_at":         now,
        "updated_at":         now,
    }
    cw_payload = {k: v for k, v in cw_payload.items() if v is not None}
    try:
        res = supabase.table("construction_workers").insert(cw_payload).execute()
        if not res.data:
            raise Exception("현장 배치 저장 결과가 비어 있습니다.")
    except Exception as e:
        # 보상: 명부 고아 방지
        try:
            supabase.table("worker_registry").delete().eq("id", worker_registry_id).execute()
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"현장 배치 등록 실패: {e}")

    return {"status": "success", "data": res.data[0]}
```

---

## 3. 저장 매핑 (화면 필드 → 저장 위치)

| 화면 전송 | worker_registry(명부) | construction_workers(배치) |
|---|---|---|
| worker_name | name | worker_name |
| phone | phone | worker_phone |
| job_type | job_type_code · job_type_name | — |
| company_name | contractor_name | — |
| hire_date | start_date | join_date |
| worker_type | — | worker_type |
| safety_training_date | — | safety_edu_date |
| safety_training_hours | — | safety_edu_hours(int 변환) |
| memo | memo | notes |
| entry_status | — | entry_status |
| (site→company_id) | company_id | — |
| — | factory_id=NULL | worker_registry_id=명부.id |

→ 화면 10필드 전부 보존. (종전 버려지던 8개 해소)

---

## 4. 검증

1. `python -c "import ast; ast.parse(open('schemas/construction.py').read())"` — 통과 확인(로컬 통과 완료).
2. `python -c "import ast; ast.parse(open('routers/construction_workflow_router.py').read())"` — 통과 확인(로컬 통과 완료).
3. main push → Railway 배포 SUCCESS, `/health` 200 유지.
4. **라이브 검증(기획창이 SQL로 확인)**: 건설 작업자 1명 등록 후
   - `worker_registry` 에 factory_id=NULL·company 스코프로 1행 생성됐는지
   - `construction_workers` 에 worker_registry_id 가 그 명부를 가리키는지
   - 화면 필드(phone·job_type·company_name·hire_date·safety_training_*·memo·entry_status)가 표대로 저장됐는지

---

## 5. 범위 밖(후속·별건)

- **화면**: useConstructionWorkerPanel.ts 는 무수정(현재 전송 필드명 그대로 수용). 단 등록 후 org(부서·팀·그룹) 배정 UI 는 건설 부서·팀이 `construction_site_id` 로 걸리므로(산업은 factory_id) 별도 과제.
- **수정/목록**: 화면에 건설 작업자 수정 진입점이 없어 이번 범위 밖. update_worker(construction_workers)만 존재.
- **subcontractor_id(FK)**: 협력사는 명부 contractor_name(텍스트)로 보존. FK 연결은 별건(이름→id 변환).
- **job_type**: worker_registry.job_type_code 에 직종명 자유텍스트(산업 WJT 코드와 상이하나 실측 선례 준수).
