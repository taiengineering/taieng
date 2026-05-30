# 샘플 데이터 재생성 — 정제 파이프라인 포함 (v2)

> 수정일: 2026-05-30
> 문제: v1 스크립트가 엔진 원본만 사용, `_build_result_payload()` 정제 미적용
> 해결: 엔진 결과를 임시 DB 저장 → `_build_result_payload()` 통과 → 정제된 JSON 사용

---

## 문제점

v1 generate_sample_data.py는 `run_diagnose_step1_runtime()`만 호출.
`diagnosis_result_web.py`의 정제를 안 거쳐서:

- 중복 미제거 (`_dedupe_rules_table()` 미적용)
- 카테고리 미정규화 (FAMILY 코드 → 한글 변환 안 됨)
- obligation_counts 누락 (도넛차트 데이터 없음)
- law_groups 누락 (bar chart 없음)
- penalty 총액 미계산
- who/what/when 미주입

---

## 수정된 스크립트

`scripts/generate_sample_data.py` 전체 교체:

```python
"""
샘플 법령진단 결과 생성 v2 — 정제 파이프라인 포함

1. 엔진 호출 → full_result
2. anonymous_diagnosis_results에 임시 저장
3. _build_result_payload() 호출 → 정제된 JSON
4. 임시 레코드 삭제
5. JSON 저장

사용법:
  cd ~/tai-api
  python scripts/generate_sample_data.py
"""
import json
import os
import sys
import uuid
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.supabase_client import get_supabase
from schemas.legal_engine import DiagnoseStep1Body
from services.diagnosis_runtime_step1 import (
    RUNTIME_ENGINE_VERSION,
    run_diagnose_step1_runtime,
)
from routers.diagnosis_result_web import _build_result_payload

ALLOWED = frozenset({"BUILDING", "MANUFACTURING", "CONSTRUCTION", "SPECIAL_FACILITY", "SPECIAL"})


def generate_sample(name: str, body: DiagnoseStep1Body, tier_code: str = "SAMPLE"):
    supabase = get_supabase()

    # 1. 엔진 호출
    print(f"[{name}] 엔진 호출...")
    full_result = run_diagnose_step1_runtime(supabase, body, ALLOWED)
    raw_rules = len(full_result.get("rules_table") or full_result.get("rules") or [])
    print(f"[{name}] 엔진 원본: {raw_rules} rules")

    # 2. 임시 저장
    token = f"SAMPLE-{name.upper()}-{uuid.uuid4().hex[:6]}"
    now = datetime.now(timezone.utc)
    input_data = dict(body.input or {})
    # worker_count 등 DiagnoseStep1Body 필드를 input_data에도 반영
    for field in ["worker_count", "employee_count", "floor_area", "total_floor_area",
                   "direct_workers", "subcon_workers", "contract_amount_eok"]:
        val = getattr(body, field, None)
        if val is not None and field not in input_data:
            input_data[field] = val
    # sector
    input_data["sector"] = body.sector

    row = {
        "public_token": token,
        "input_data": input_data,
        "partial_result": {},
        "full_result": full_result,
        "created_at": now.isoformat(),
        "expires_at": (now + timedelta(days=1)).isoformat(),
        "status": "ACTIVE",
        "source_type": "sample_generator",
        "engine_version": RUNTIME_ENGINE_VERSION,
        "tier_code": tier_code,
    }
    supabase.table("anonymous_diagnosis_results").insert(row).execute()

    # 3. _build_result_payload → 정제 통과
    try:
        payload = _build_result_payload(token, free_preview_limit=None)
        refined = payload.get("data", payload)
        refined_rules = len(refined.get("rules_table") or [])
        print(f"[{name}] 정제 후: {refined_rules} rules (중복제거: {raw_rules - refined_rules}건)")
        print(f"[{name}] obligation_counts: {refined.get('obligation_counts', {})}")
        print(f"[{name}] law_groups: {len(refined.get('law_groups', []))}개 법령")
        print(f"[{name}] risk_level: {refined.get('risk_level')}")
    except Exception as e:
        print(f"[{name}] 정제 실패, 원본 사용: {e}")
        refined = full_result

    # 4. 임시 삭제
    supabase.table("anonymous_diagnosis_results").delete().eq("public_token", token).execute()

    # 5. JSON 저장
    os.makedirs("scripts/output", exist_ok=True)
    path = f"scripts/output/{name}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(refined, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{name}] → {path}")
    return refined


# === 입력 데이터 (변경 없음 — v1과 동일) ===

facility_body = DiagnoseStep1Body(
    factory_id=None, sector="BUILDING",
    input={"company_name":"서울타워 오피스 복합건물","business_no":"111-22-33333","ceo_name":"박관리","address":"서울특별시 중구 남대문로 789"},
    building_use_type="오피스", floor_area=25000.0, total_floor_area=85000.0,
    floor_count=28, worker_count=120, employee_count=120,
    electric_capacity=3000.0, elevator_count=12,
    gas_capacity_m3=500.0, boiler_capacity_kw=2000.0, annual_energy_toe=800.0,
    has_boiler=True, has_high_pressure_gas=False, has_hazardous_material=False, has_chemical_substance=False,
)

manufacturing_body = DiagnoseStep1Body(
    factory_id=None, sector="MANUFACTURING",
    input={"company_name":"한국정밀제조(주) 안산 제2공장","business_no":"222-33-44444","ceo_name":"김제조","address":"경기도 안산시 단원구 산업로 456",
        "processes":[
            {"name":"제련·원료처리","equipments":["용해로","전기로","냉각탑","집진기","원료이송컨베이어"]},
            {"name":"가공·성형","equipments":["프레스기","CNC선반","레이저절단기","연삭기","용접기"]},
            {"name":"도장·표면처리","equipments":["스프레이부스","도장건조로","산세정수장치","환기장치"]},
            {"name":"조립·검사","equipments":["조립라인","품질검사장비","지게차(2대)"]},
            {"name":"포장·출하","equipments":["포장기계","대량저장시설","지게차(1대)"]}],
        "hazardous_chemicals":["톨루엔","아세톤","염산","수산화나트륨"],
        "hazardous_material_types":["인화성액체","산화성액체"]},
    ksic_major="C24", floor_area=15000.0, total_floor_area=22000.0,
    worker_count=300, employee_count=300, electric_capacity=5000.0,
    has_high_pressure_gas=True, has_boiler=True, has_hazardous_material=True, has_chemical_substance=True,
    boiler_capacity_kw=3000.0, gas_capacity_m3=200.0, elevator_count=3, annual_energy_toe=1500.0,
)

construction_body = DiagnoseStep1Body(
    factory_id=None, sector="CONSTRUCTION",
    input={"company_name":"대한건설(주) 강남 오피스빌딩 신축 현장","business_no":"333-44-55555","ceo_name":"이건설","address":"서울특별시 강남구 삼성동 123-4",
        "construction_phases":[
            {"name":"토공·기초","works":["굴착","토류운반","항타공사","파일공사","흙막이공사"]},
            {"name":"구조체","works":["철근배근","거푸집","콘크리트타설","철골조립","용접"]},
            {"name":"방수·단열","works":["외부방수","내부방수","단열시공"]},
            {"name":"전기·설비","works":["전기배선","수변실","승강기설치","소방설비","기계설비(HVAC)","배관"]},
            {"name":"마감·인테리어","works":["외벽마감","내부마감","유리시공","도장"]}],
        "heavy_equipment":["타워크레인(2대)","굴삭기(3대)","덤프트럭(5대)","콘크리트펌프카","철근절단기"]},
    construction_type="건축", contract_amount_eok=300.0,
    direct_workers=200, subcon_workers=150,
    electrical_capacity_kw=2000.0, has_crane=True, has_high_work=True,
    has_tunnel_bridge=False, has_blasting=False, floor_count=28,
)


if __name__ == "__main__":
    print("=" * 60)
    print("샘플 법령진단 데이터 생성 v2 (정제 파이프라인 포함)")
    print("=" * 60)
    print()
    for name, body, tier in [
        ("sample_facility", facility_body, "BUILDING_LARGE_V2"),
        ("sample_manufacturing", manufacturing_body, "INDUSTRY_STANDARD"),
        ("sample_construction", construction_body, "CONSTRUCTION_PREMIUM"),
    ]:
        try:
            generate_sample(name, body, tier)
        except Exception as e:
            print(f"[{name}] 실패: {e}")
            import traceback; traceback.print_exc()
        print()
    print("완료. scripts/output/sample_*.json 확인 후 nexas/sample-*.html SAMPLE_DATA 교체.")
```

---

## 정제 검증 포인트

스크립트 실행 후 JSON에 아래 필드 모두 존재해야 함:

```
✓ rules_table       — 중복 제거됨 (원본보다 적어야 정상)
✓ obligation_counts  — {"선임":N, "점검":N, ...}
✓ law_groups         — [{law_name:"산업안전보건법", count:N}, ...]
✓ summary            — total, inspection, appointment, action, report, law_count, worker_count
✓ key_obligations    — 핵심 의무 리스트
✓ inspection_schedule — periodic / before_work
✓ risk_level         — HIGH/MEDIUM/LOW
✓ recommended_plan   — {name, price}
✓ input_data         — company_name, worker_count 등
✓ pdf_url
```

하나라도 없으면 `_build_result_payload()` 통과 실패.

## 실행

```bash
cd ~/tai-api
python scripts/generate_sample_data.py
```

## 이후 작업

1. JSON 검증 (위 체크포인트)
2. nexas/sample-*.html의 SAMPLE_DATA 교체
3. 브라우저 렌더링 확인
4. taieng 레포 커밋·푸시

## 금지사항

- 엔진 수정 금지
- `_build_result_payload()` 수정 금지
- 목업 데이터 수동 작성 금지
