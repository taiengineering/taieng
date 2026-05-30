# 법령진단 샘플 데이터 생성 — 실제 엔진 호출 방식

> 작성일: 2026-05-30
> 대상: tai-api + taieng(nexas/)
> 목적: 실제 법령엔진에 현실적 입력을 넣어 결과를 받고, 그 JSON을 sample HTML의 SAMPLE_DATA로 사용

---

## 방법

tai-api 로컬에서 1회성 스크립트 실행:

```bash
cd ~/tai-api
python scripts/generate_sample_data.py
```

결과물: `scripts/output/sample_construction.json`, `sample_manufacturing.json`, `sample_facility.json`

이 JSON을 sample-*.html의 `const SAMPLE_DATA = ...`에 붙여넣는다.

---

## 스크립트: `scripts/generate_sample_data.py`

```python
"""
샘플 법령진단 결과 생성 — 실제 런타임 엔진 호출

사용법:
  cd ~/tai-api
  python scripts/generate_sample_data.py

결과:
  scripts/output/sample_construction.json
  scripts/output/sample_manufacturing.json
  scripts/output/sample_facility.json
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.supabase_client import get_supabase
from schemas.legal_engine import DiagnoseStep1Body
from services.diagnosis_runtime_step1 import run_diagnose_step1_runtime

ALLOWED = frozenset({"BUILDING", "MANUFACTURING", "CONSTRUCTION", "SPECIAL_FACILITY", "SPECIAL"})


def run_and_save(name: str, body: DiagnoseStep1Body):
    supabase = get_supabase()
    result = run_diagnose_step1_runtime(supabase, body, ALLOWED)
    os.makedirs("scripts/output", exist_ok=True)
    path = f"scripts/output/{name}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    rules_count = len(result.get("rules") or result.get("rules_table") or [])
    print(f"[OK] {name}: {rules_count} rules -> {path}")


# ============================================================
# 1. 건물 (대형 오피스 복합건물, 시설관리)
# ============================================================
facility_body = DiagnoseStep1Body(
    factory_id=None,
    sector="BUILDING",
    input={
        "company_name": "서울타워 오피스 복합건물",
        "business_no": "111-22-33333",
        "ceo_name": "박관리",
        "address": "서울특별시 중구 남대문로 789",
    },
    building_use_type="오피스",              # 오피스 복합 건물
    floor_area=25000.0,                    # 바닥면적 25,000㎡
    total_floor_area=85000.0,              # 연면적 85,000㎡ (대형)
    floor_count=28,                        # 28층 (지하 5층 포함)
    worker_count=120,                      # 상시근로자 120명
    employee_count=120,
    electric_capacity=3000.0,              # 수변용량 3,000kVA
    elevator_count=12,                     # 승강기 12대 (승객8 + 화물2 + 비상2)
    gas_capacity_m3=500.0,                 # 도시가스 500m³/h
    boiler_capacity_kw=2000.0,             # 보일러 2,000kW
    annual_energy_toe=800.0,               # 연간에너지 800TOE
    has_high_pressure_gas=False,           # 고압가스 없음
    has_boiler=True,                       # 보일러 있음
    has_hazardous_material=False,          # 위험물 없음
    has_chemical_substance=False,          # 화학물질 없음
)

# ============================================================
# 2. 산업(제조) — 300인 대형 제조공장
# ============================================================
manufacturing_body = DiagnoseStep1Body(
    factory_id=None,
    sector="MANUFACTURING",
    input={
        "company_name": "한국정밀제조(주) 안산 제2공장",
        "business_no": "222-33-44444",
        "ceo_name": "김제조",
        "address": "경기도 안산시 단원구 산업로 456",
        # 공정 정보 (엔진이 input dict에서 읽을 수 있는 경우)
        "processes": [
            {"name": "제련·원료처리", "equipments": ["용해로", "전기로", "냉각탑", "집진기", "원료이송컨베이어"]},
            {"name": "가공·성형", "equipments": ["프레스기", "CNC선반", "레이저절단기", "연삭기", "용접기"]},
            {"name": "도장·표면처리", "equipments": ["스프레이부스", "도장건조로", "산세정수장치", "환기장치"]},
            {"name": "조립·검사", "equipments": ["조립라인", "품질검사장비", "지게차(2대)"]},
            {"name": "포장·출하", "equipments": ["포장기계", "대량저장시설", "지게차(1대)"]}
        ],
        # 위험물질 상세
        "hazardous_chemicals": ["톨루엔", "아세톤", "염산", "수산화나트륨"],
        "hazardous_material_types": ["인화성액체", "산화성액체"],
    },
    ksic_major="C24",                      # 제1차 금속 제조업
    floor_area=15000.0,                    # 15,000㎡
    total_floor_area=22000.0,              # 연면적 22,000㎡
    worker_count=300,                      # 상시근로자 300명
    employee_count=300,
    electric_capacity=5000.0,              # 수변 5,000kVA (대형 공장)
    has_high_pressure_gas=True,            # 고압가스 사용 (질소, 산소)
    has_boiler=True,                       # 보일러 있음
    has_hazardous_material=True,           # 위험물 있음 (인화성액체, 산화성)
    has_chemical_substance=True,           # 화학물질 있음 (톨루엔, 아세톤, 염산 등)
    boiler_capacity_kw=3000.0,             # 보일러 3,000kW
    gas_capacity_m3=200.0,                 # 가스 200m³/h
    elevator_count=3,                      # 화물엘리베이터 3대
    annual_energy_toe=1500.0,              # 연간 1,500TOE (에너지다소비)
)

# ============================================================
# 3. 건설 — 300억 지하주차장 포함 오피스 신축
# ============================================================
construction_body = DiagnoseStep1Body(
    factory_id=None,
    sector="CONSTRUCTION",
    input={
        "company_name": "대한건설(주) 강남 오피스빌딩 신축 현장",
        "business_no": "333-44-55555",
        "ceo_name": "이건설",
        "address": "서울특별시 강남구 삼성동 123-4",
        # 건설 공정 상세
        "construction_phases": [
            {"name": "토공·기초", "works": ["굴착", "토류운반", "항타공사", "파일공사", "흘막이공사"]},
            {"name": "구조체", "works": ["철근배근", "거푸집", "콘크리트타설", "철골조립", "용접"]},
            {"name": "방수·단열", "works": ["외부방수", "내부방수", "단열시공"]},
            {"name": "전기·설비", "works": ["전기배선", "수변실", "승강기설치", "소방설비", "기계설비(HVAC)", "배관"]},
            {"name": "마감·인테리어", "works": ["외벽마감", "내부마감", "유리시공", "도장"]}
        ],
        # 장비 목록
        "heavy_equipment": ["타워크레인(2대)", "굴삭기(3대)", "덤프트럭(5대)", "콘크리트펌프카", "철근절단기"],
    },
    construction_type="건축",               # 건축공사
    contract_amount_eok=300.0,             # 300억원
    direct_workers=200,                    # 직영 근로자 200명
    subcon_workers=150,                    # 하도급 근로자 150명 (총 350명)
    electrical_capacity_kw=2000.0,         # 가설전기 2,000kW
    has_tunnel_bridge=False,               # 터널/교량 없음
    has_blasting=False,                    # 발파 없음
    has_crane=True,                        # 크레인 있음 (2대)
    has_high_work=True,                    # 고소작업 있음 (28층)
    floor_count=28,                        # 28층 (지하 5층 포함)
)


if __name__ == "__main__":
    print("=== 샘플 법령진단 데이터 생성 ===")
    print()
    run_and_save("sample_facility", facility_body)
    run_and_save("sample_manufacturing", manufacturing_body)
    run_and_save("sample_construction", construction_body)
    print()
    print("=== 완료 ===")
    print("결과 파일: scripts/output/sample_*.json")
    print("이 JSON을 nexas/sample-*.html의 SAMPLE_DATA로 붙여넣으세요.")
```

---

## 입력 데이터 상세

### 건물 (대형 오피스 복합건물)

| 필드 | 값 | 설명 |
|---|---|---|
| building_use_type | "오피스" | 오피스 복합 건물 |
| total_floor_area | 85,000㎡ | 연면적 대형 |
| floor_count | 28 | 지하 5층 + 지상 23층 |
| worker_count | 120 | 상시근로자 |
| electric_capacity | 3,000kVA | 대형 수변 |
| elevator_count | 12 | 승객8+화물2+비상2 |
| gas_capacity_m3 | 500 | 도시가스 |
| boiler_capacity_kw | 2,000 | 냉난방용 |
| annual_energy_toe | 800 | 에너지다소비 대상 |
| has_boiler | true | 보일러 있음 |

적용될 법령: 건축물관리법, 소방시설법, 승강기안전관리법, 전기안전관리법, 도시가스사업법, 에너지이용합리화법, 산업안전보건법, 중대재해처벌법, 화재예방법, 근로기준법 등

### 제조업 (300인 대형 공장)

| 필드 | 값 | 설명 |
|---|---|---|
| ksic_major | C24 | 1차 금속 제조 |
| worker_count | 300 | 대형 사업장 |
| total_floor_area | 22,000㎡ | 연면적 |
| electric_capacity | 5,000kVA | 대형 수변 |
| has_high_pressure_gas | true | 질소, 산소 |
| has_boiler | true | 3,000kW |
| has_hazardous_material | true | 인화성/산화성 액체 |
| has_chemical_substance | true | 톨루엔, 아세톤, 염산 |
| annual_energy_toe | 1,500 | 에너지다소비 대상 |
| elevator_count | 3 | 화물엘리베이터 |

공정 5개: 제련·원료처리 / 가공·성형 / 도장·표면처리 / 조립·검사 / 포장·출하
설비 18개: 용해로, 전기로, 냉각탑, 집진기, 컨베이어, 프레스기, CNC선반, 레이저절단기, 연삭기, 용접기, 스프레이부스, 도장건조로, 산세정수장치, 환기장치, 조립라인, 검사장비, 지게차(3대), 포장기계
유해화학물질: 톨루엔, 아세톤, 염산, 수산화나트륨

### 건설 (300억 오피스 신축)

| 필드 | 값 | 설명 |
|---|---|---|
| construction_type | "건축" | 건축공사 |
| contract_amount_eok | 300 | 300억원 |
| direct_workers | 200 | 직영 근로자 |
| subcon_workers | 150 | 하도급 (총 350명) |
| electrical_capacity_kw | 2,000 | 가설전기 |
| has_crane | true | 타워크레인 2대 |
| has_high_work | true | 28층 고소작업 |
| floor_count | 28 | 지하 5층 포함 |

공정 5단계: 토공·기초 / 구조체 / 방수·단열 / 전기·설비 / 마감·인테리어
작업: 굴착, 토류운반, 항타, 파일, 흘막이, 철근배근, 거푸집, 콘크리트타설, 철골조립, 용접, 방수, 단열, 전기배선, 수변실, 승강기설치, 소방설비, HVAC, 배관, 외벽마감, 유리시공, 도장
장비: 타워크레인 2대, 굴삭기 3대, 덤프트럭 5대, 콘크리트펌프카, 철근절단기

---

## Cursor 작업 순서

1. `scripts/generate_sample_data.py` 생성 (위 코드 그대로)
2. 로컬에서 실행: `python scripts/generate_sample_data.py`
3. `scripts/output/sample_*.json` 3개 결과 확인
4. 각 JSON의 내용을 기존 `nexas/sample-*.html`의 `const SAMPLE_DATA = ...` 블록에 붙여넣기
5. 브라우저에서 렌더링 확인
6. 정상이면 taieng 레포에 커밋·푸시

---

## 결과 JSON → SAMPLE_DATA 변환 시 주의

엔진 출력이 `diagnosis_result_web.py`의 `_build_result_payload()`가 반환하는 형식과 다를 수 있다.
필요시 `_build_result_payload`를 직접 호출하거나,
엔진 출력을 해당 함수에 넣어서 변환한 후 사용:

```python
# 옵션: 엔진 출력을 _build_result_payload 형식으로 변환
from routers.diagnosis_result_web import _build_result_payload

# 1. 엔진 결과를 anonymous_diagnosis_results에 임시 저장
# 2. _build_result_payload(token) 호출
# 3. 반환값의 ["data"] 전체를 SAMPLE_DATA로 사용
```

이렇게 하면 paid-diagnosis-result.html의 렌더링 로직과 100% 호환된다.

---

## 금지사항

- 목업 데이터 수동 작성 금지 — 반드시 엔진 출력 사용
- 기존 paid-diagnosis-result.html 수정 금지
- 엔진 코드 수정 금지
