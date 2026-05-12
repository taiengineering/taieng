# TAI 건설안전 — 백엔드 작업지시서
## 작성일: 2026-03-31 | 담당: Code 창 (Cursor)

---

## ■ 우선순위
1. DB 마이그레이션 (신규 테이블 4개)
2. API 라우터 5개 (현장/공정/작업/작업자/점검)
3. main.py 등록

---

## STEP 1. DB 마이그레이션

### 1-1. construction_sites (건설현장)

```sql
CREATE TABLE construction_sites (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID NOT NULL REFERENCES companies(id),
  site_name TEXT NOT NULL,
  site_code TEXT,                              -- 현장 코드 (자동채번)
  site_type TEXT NOT NULL DEFAULT 'BUILDING',  -- BUILDING / CIVIL
  contract_amount NUMERIC(15,2),               -- 도급금액 (억원)
  total_workers INTEGER DEFAULT 0,             -- 총 근로자 (하도급 포함)
  direct_workers INTEGER DEFAULT 0,            -- 원청 근로자
  subcon_workers INTEGER DEFAULT 0,            -- 하도급 근로자
  site_address TEXT,
  site_address_detail TEXT,
  site_sido TEXT,
  site_sigungu TEXT,
  start_date DATE,
  end_date DATE,
  manager_id UUID REFERENCES users(id),         -- 안전보건관리책임자
  safety_manager_required BOOLEAN DEFAULT FALSE, -- 안전관리자 선임 의무 (엔진 자동)
  safety_manager_count INTEGER DEFAULT 0,        -- 선임 의무 인원 수
  status_code TEXT DEFAULT 'PLANNED',            -- PLANNED/ONGOING/COMPLETED/SUSPENDED
  is_active BOOLEAN DEFAULT TRUE,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  updated_by UUID REFERENCES users(id)
);

COMMENT ON TABLE construction_sites IS '건설현장 마스터';
COMMENT ON COLUMN construction_sites.site_type IS 'BUILDING=건축, CIVIL=토목';
COMMENT ON COLUMN construction_sites.contract_amount IS '도급금액(억원), 산안법 선임 기준';
COMMENT ON COLUMN construction_sites.safety_manager_required IS '산안법 시행령 제16조 기준 자동 판정';
```

### 1-2. construction_site_processes (현장-공정 매핑)

```sql
CREATE TABLE construction_site_processes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  site_id UUID NOT NULL REFERENCES construction_sites(id) ON DELETE CASCADE,
  process_master_id UUID REFERENCES kcsc_process_master(id), -- KCSC 표준공정
  process_name TEXT NOT NULL,            -- 직접 입력 또는 KCSC 연동
  construction_type TEXT,                -- BUILDING/CIVIL/COMMON
  planned_start DATE,
  planned_end DATE,
  actual_start DATE,
  actual_end DATE,
  progress_rate INTEGER DEFAULT 0 CHECK (progress_rate BETWEEN 0 AND 100),
  worker_count INTEGER DEFAULT 0,
  is_high_risk BOOLEAN DEFAULT FALSE,    -- KCSC 기준 위험공정 여부
  status_code TEXT DEFAULT 'PENDING',    -- PENDING/IN_PROGRESS/DONE
  sort_order INTEGER DEFAULT 0,
  notes TEXT,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  updated_by UUID REFERENCES users(id)
);

COMMENT ON TABLE construction_site_processes IS '건설현장-KCSC 공정 매핑';
```

### 1-3. construction_works (위험작업/작업허가서)

```sql
CREATE TABLE construction_works (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  site_id UUID NOT NULL REFERENCES construction_sites(id) ON DELETE CASCADE,
  process_id UUID REFERENCES construction_site_processes(id),
  work_master_id UUID REFERENCES kcsc_work_master(id),  -- KCSC 작업 연동
  work_name TEXT NOT NULL,
  work_date DATE NOT NULL,
  work_time_start TIME,
  work_time_end TIME,
  work_location TEXT,                    -- 작업 위치/구역
  assigned_manager_id UUID REFERENCES users(id), -- 관리감독자
  subcontractor_id UUID REFERENCES companies(id),
  ptw_number TEXT,                       -- 작업허가서 번호 (자동채번)
  ptw_status TEXT DEFAULT 'DRAFT',       -- DRAFT/APPROVED/REJECTED/CLOSED
  ptw_approved_by UUID REFERENCES users(id),
  ptw_approved_at TIMESTAMPTZ,
  special_work_type TEXT,                -- 고소/밀폐/화기/전기/굴착/양중/발파/석면
  hazard_codes TEXT,                     -- 위험요인 코드 (쉼표 구분)
  ppe_required TEXT,                     -- 필요 PPE (쉼표 구분)
  worker_count INTEGER DEFAULT 0,
  status_code TEXT DEFAULT 'SCHEDULED',  -- SCHEDULED/IN_PROGRESS/DONE/CANCELLED
  is_active BOOLEAN DEFAULT TRUE,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  updated_by UUID REFERENCES users(id)
);

COMMENT ON TABLE construction_works IS '건설현장 위험작업 및 작업허가서(PTW)';
COMMENT ON COLUMN construction_works.ptw_number IS '작업허가서 번호: CS-{연도}-{순번}';
COMMENT ON COLUMN construction_works.special_work_type IS '특별관리작업: 고소/밀폐/화기/전기/굴착/양중/발파/석면';
```

### 1-4. construction_workers (작업자 배치)

```sql
CREATE TABLE construction_workers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  site_id UUID NOT NULL REFERENCES construction_sites(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id),
  -- 비회원 작업자 직접 입력
  worker_name TEXT,
  worker_phone TEXT,
  worker_type TEXT DEFAULT 'SUBCON',     -- DIRECT=원청 / SUBCON=하도급
  subcontractor_id UUID REFERENCES companies(id),
  role_code TEXT,                        -- 역할코드 (010~022)
  join_date DATE,
  leave_date DATE,
  certification_codes TEXT,             -- 보유 자격증 코드 (쉼표 구분)
  health_check_date DATE,               -- 특수건강검진일
  health_check_result TEXT,             -- 정상/직업병유소견/관리필요
  safety_edu_date DATE,                 -- 안전교육 완료일
  safety_edu_hours INTEGER DEFAULT 0,   -- 교육시간(h)
  entry_status TEXT DEFAULT 'OFFSITE',  -- IN/OUT/OFFSITE
  last_entry_at TIMESTAMPTZ,
  is_active BOOLEAN DEFAULT TRUE,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  updated_by UUID REFERENCES users(id)
);

COMMENT ON TABLE construction_workers IS '건설현장 작업자 배치 (원청/하도급)';
COMMENT ON COLUMN construction_workers.worker_type IS 'DIRECT=원청, SUBCON=하도급. 산안법 제16조③ 하도급 포함 계산';
```

### 1-5. construction_inspections (안전점검)

```sql
CREATE TABLE construction_inspections (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  site_id UUID NOT NULL REFERENCES construction_sites(id) ON DELETE CASCADE,
  work_id UUID REFERENCES construction_works(id),
  process_id UUID REFERENCES construction_site_processes(id),
  inspection_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  inspector_id UUID REFERENCES users(id),
  inspection_type TEXT DEFAULT 'BEFORE_WORK', -- BEFORE_WORK/DAILY/SPECIAL
  checklist_items JSONB,                 -- [{item, result, note}]
  overall_result TEXT,                   -- PASS/FAIL/CONDITIONAL
  defect_count INTEGER DEFAULT 0,
  defect_items JSONB,                    -- 이상 항목 상세
  corrective_action TEXT,
  corrective_deadline DATE,
  corrective_status TEXT DEFAULT 'PENDING', -- PENDING/IN_PROGRESS/DONE
  photo_urls TEXT[],
  is_active BOOLEAN DEFAULT TRUE,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  updated_by UUID REFERENCES users(id)
);

COMMENT ON TABLE construction_inspections IS '건설현장 안전점검 (작업 전 점검 포함)';
COMMENT ON COLUMN construction_inspections.checklist_items IS 'KCSC safety_standard 기반 자동 생성';
```

---

## STEP 2. API 라우터

### 파일: `routers/construction.py`

#### 엔드포인트 목록

```
[현장]
GET    /construction/sites                    # 목록 (페이지네이션, 필터)
POST   /construction/sites                    # 등록
GET    /construction/sites/{id}               # 상세
PATCH  /construction/sites/{id}               # 수정
DELETE /construction/sites/{id}               # 삭제 (soft)
GET    /construction/sites/{id}/stats         # 현장 통계 (인원/공정/작업)

[공정]
GET    /construction/sites/{site_id}/processes    # 공정 목록
POST   /construction/sites/{site_id}/processes    # 공정 등록
GET    /construction/processes/{id}               # 공정 상세
PATCH  /construction/processes/{id}               # 진행률·상태 수정
DELETE /construction/processes/{id}               # 삭제 (soft)

[KCSC 마스터]
GET    /construction/kcsc/processes               # KCSC 공정 전체 (검색)
GET    /construction/kcsc/works/{process_id}      # KCSC 공정별 작업 목록

[작업]
GET    /construction/sites/{site_id}/works        # 작업 목록
POST   /construction/sites/{site_id}/works        # 작업 등록
GET    /construction/works/{id}                   # 작업 상세
PATCH  /construction/works/{id}                   # 작업 수정
PATCH  /construction/works/{id}/ptw               # PTW 상태 변경 (APPROVE/REJECT/CLOSE)
DELETE /construction/works/{id}                   # 삭제 (soft)

[작업자]
GET    /construction/sites/{site_id}/workers      # 작업자 목록
POST   /construction/sites/{site_id}/workers      # 작업자 등록
GET    /construction/workers/{id}                 # 작업자 상세
PATCH  /construction/workers/{id}                 # 수정
PATCH  /construction/workers/{id}/entry           # 출입 상태 변경
DELETE /construction/workers/{id}                 # 삭제 (soft)

[점검]
GET    /construction/sites/{site_id}/inspections  # 점검 목록
POST   /construction/sites/{site_id}/inspections  # 점검 등록
GET    /construction/inspections/{id}             # 점검 상세
PATCH  /construction/inspections/{id}             # 점검 수정
PATCH  /construction/inspections/{id}/corrective  # 시정조치 업데이트
DELETE /construction/inspections/{id}             # 삭제 (soft)

[안전관리자 판정 엔진]
POST   /construction/engine/safety-manager        # 안전관리자 선임 의무 자동 판정
                                                   # body: {site_type, contract_amount, total_workers}
```

#### 안전관리자 판정 로직 (construction_engine)
```python
def calc_safety_manager(site_type: str, contract_amount: float, total_workers: int):
    """
    산안법 시행령 제16조 기준
    - 건축(BUILDING): 도급금액 >= 150억 → 선임 의무
    - 토목(CIVIL): 도급금액 >= 120억 → 선임 의무
    - 상시 근로자(하도급 포함) >= 50명 → 선임 의무 (도급금액 무관)
    """
    required = False
    count = 0
    if site_type == 'BUILDING' and contract_amount >= 150:
        required = True; count = max(1, int(contract_amount // 150))
    elif site_type == 'CIVIL' and contract_amount >= 120:
        required = True; count = max(1, int(contract_amount // 120))
    if total_workers >= 50:
        required = True; count = max(count, 1)
    return {"required": required, "count": count}
```

#### 응답 구조 (표준)
```json
{
  "status": "success",
  "data": {
    "items": [...],
    "total": 123,
    "page": 1,
    "size": 20
  }
}
```

---

## STEP 3. main.py 등록

```python
from routers import construction
app.include_router(construction.router, prefix="/construction", tags=["건설안전"])
```

---

## STEP 4. 주의사항

1. **system_codes 먼저 확인** — `construction_site_status`, `construction_work_type`, `special_work_type` 코드 필요
2. **PTW 번호 자동채번** — `CS-{YYYY}-{5자리 순번}` 형식
3. **하도급 인원 포함 계산** — `total_workers = direct_workers + subcon_workers`
4. **KCSC 연동** — `kcsc_process_master`, `kcsc_work_master` 기존 테이블 JOIN
5. **soft delete** — `is_active = false` 방식 (DELETE 금지)
6. **페이지네이션** — size <= 100, 기본 20
