# TAI 작업지시서 — 건설 법령엔진 완성

> 작성일: 2026-04-01  
> 대상: tai-api (백엔드) + ChatGPT (데이터)  
> 목표: 건설 섹터 법령진단 1·2·3단계 완벽 동작

---

## 현황 요약 (발견된 문제)

### 문제 1. condition_code → context key 매핑 누락 [최우선]

`legal_engine.py`의 `CONDITION_CODE_TO_CONTEXT_KEY`에 건설 전용 매핑 없음:

```python
# 현재 (누락)
CONDITION_CODE_TO_CONTEXT_KEY = {
    "employee_count": "worker_count",
    "building_area": "total_floor_area",
    "electrical_capacity_kw": "electric_capacity",
    # ... contract_amount 없음!
}

# DB에서 건설 룰의 condition_code:
# contract_amount → construction_amount 로 매핑되어야 함
# employee_count  → worker_count (이건 있음)
# electric_capacity → electric_capacity (이건 있음)
```

**결과**: `contract_amount` 조건을 가진 NOTIFY/APPOINT 12건이 모두 미적용됨

### 문제 2. 건설 site_type 분기 없음

```python
# _input_to_facility_context의 CONSTRUCTION 분기:
elif sec == "CONSTRUCTION":
    eok = float(inp.get("contract_amount_eok") or 0)
    ctx["construction_amount"] = eok * 100_000_000.0
    ctx["worker_count"] = ...
    ctx["building_use_code"] = str(inp.get("construction_type") or "")
    # ← site_type(BUILDING/CIVIL) 구분 없음!
    # ← 하도급 포함 근로자 수 없음!
    # ← tunnel_bridge 여부 없음!
```

### 문제 3. 2·3단계 룰 거의 없음

| 단계 | 건수 | 상태 |
|------|------|------|
| 1단계 | 175건 | ✅ (단, 조건 매핑 버그) |
| 2단계 | 1건 | ❌ 사실상 없음 |
| 3단계 | 1건 | ❌ 사실상 없음 |

### 문제 4. 조건 없는 룰이 너무 많음

```
ACTION 69건 중 63건이 condition_value=NULL
→ 건설현장이면 무조건 전부 적용
→ 실제 판정 의미 없음
→ 불필요한 환경/화학 법령까지 전부 노출
```

---

## 작업 1: 백엔드 엔진 버그 수정 [Cursor — 백엔드]

### 1-1. CONDITION_CODE_TO_CONTEXT_KEY 건설 매핑 추가

`routers/legal_engine.py`의 `CONDITION_CODE_TO_CONTEXT_KEY`에 추가:

```python
CONDITION_CODE_TO_CONTEXT_KEY: Dict[str, str] = {
    # 기존
    "employee_count": "worker_count",
    "building_area": "total_floor_area",
    "electrical_capacity_kw": "electric_capacity",
    "floor_count": "floor_count",
    ...
    # 건설 전용 추가
    "contract_amount": "construction_amount",  # ← 핵심 버그 수정
    "electric_capacity": "electric_capacity",
}
```

### 1-2. 건설 context 완성

`_input_to_facility_context`의 CONSTRUCTION 분기 수정:

```python
elif sec == "CONSTRUCTION":
    eok = float(inp.get("contract_amount_eok") or 0)
    ctx["construction_amount"] = eok * 100_000_000.0
    ctx["contract_amount"] = eok * 100_000_000.0  # ← condition_code 직접 매핑도 추가
    
    # 공사 종류 (BUILDING=건축, CIVIL=토목, SPECIALTY=전문)
    site_type = str(inp.get("construction_type") or inp.get("site_type") or "BUILDING")
    ctx["construction_type"] = site_type
    ctx["building_use_code"] = site_type
    ctx["is_building"] = 1 if site_type == "BUILDING" else 0
    ctx["is_civil"] = 1 if site_type == "CIVIL" else 0
    
    # 근로자 수 (하도급 포함)
    direct = int(inp.get("direct_workers") or inp.get("worker_count") or inp.get("employee_count") or 0)
    subcon = int(inp.get("subcon_workers") or 0)
    total = direct + subcon
    ctx["worker_count"] = total
    ctx["employee_count"] = total  # ← condition_code 직접 매핑도 추가
    ctx["direct_workers"] = direct
    ctx["subcon_workers"] = subcon
    
    # 터널·교량 여부
    ctx["has_tunnel_bridge"] = 1 if _truthy(inp.get("has_tunnel_bridge")) else 0
    
    # 선임 기준 자동 판정 (엔진 내부 참조용)
    if site_type == "BUILDING":
        ctx["safety_manager_threshold"] = 15_000_000_000  # 150억
    elif site_type == "CIVIL":
        ctx["safety_manager_threshold"] = 12_000_000_000  # 120억
    else:
        ctx["safety_manager_threshold"] = 15_000_000_000
```

### 1-3. 조건 없는 룰 필터링 강화

건설 섹터에서 `condition_value=NULL`인 환경/화학 계열 법령은
건설 현장과 직접 관련 없는 경우가 많음.

`_evaluate_facility_conditions_db`에 건설 전용 필터 추가:

```python
# 건설 섹터의 경우 조건 없는 룰 중 핵심 건설 법령만 포함
CONSTRUCTION_RELEVANT_LAW_PREFIXES = [
    "산업안전보건", "중대재해", "건설산업", "건설기술",
    "근로기준", "산업재해보상", "전기안전"
]

def _is_construction_relevant(rule: dict, sector: str) -> bool:
    if sector != "CONSTRUCTION":
        return True  # 다른 섹터는 그대로
    cc = rule.get("condition_code")
    cv = rule.get("condition_value")
    if cc and cv:
        return True  # 조건 있는 룰은 항상 포함
    # 조건 없는 룰은 건설 관련 법령만
    law = rule.get("law_name") or ""
    return any(prefix in law for prefix in CONSTRUCTION_RELEVANT_LAW_PREFIXES)
```

### 1-4. step1 결과에 건설 선임 판정 추가

`diagnose_step1` 결과에 건설 전용 summary 추가:

```python
# CONSTRUCTION 전용 결과 추가
if sector_raw == "CONSTRUCTION":
    amount = facility_ctx.get("construction_amount", 0)
    workers = facility_ctx.get("worker_count", 0)
    site_type = facility_ctx.get("construction_type", "BUILDING")
    
    threshold = 15_000_000_000 if site_type == "BUILDING" else 12_000_000_000
    sm_required = amount >= threshold or workers >= 50
    
    result_data["construction_summary"] = {
        "site_type": site_type,
        "contract_amount": amount,
        "contract_amount_eok": amount / 100_000_000,
        "total_workers": workers,
        "safety_manager_required": sm_required,
        "safety_manager_basis": (
            f"{'건축' if site_type == 'BUILDING' else '토목'} "
            f"{int(threshold/100_000_000)}억원 {'이상' if amount >= threshold else '미만'}"
            + (", 근로자 50명 이상" if workers >= 50 else "")
        ),
        "key_thresholds_met": {
            "1억_산업안전보건관리비": amount >= 100_000_000,
            "50억_유해위험방지계획서": amount >= 5_000_000_000,
            "50억_기초안전보건교육": amount >= 5_000_000_000,
            "120억_안전관리자선임_토목": site_type == "CIVIL" and amount >= 12_000_000_000,
            "150억_안전관리자선임_건축": site_type == "BUILDING" and amount >= 15_000_000_000,
            "200억_안전보건관리책임자": amount >= 20_000_000_000,
            "1000억_건설안전판정사": amount >= 100_000_000_000,
        }
    }
```

### 1-5. 엔진 버전 v5.1.0으로 업데이트

```python
ENGINE_VERSION = "5.1.0"
# 변경 내역:
# v5.1.0: 건설 섹터 법령엔진 완성
#   - CONDITION_CODE_TO_CONTEXT_KEY에 contract_amount 매핑 추가
#   - CONSTRUCTION context 완성 (site_type, 하도급근로자, tunnel)
#   - 건설 선임 기준 자동 판정 result 추가
#   - 건설 관련 법령 필터링 강화
```

---

## 작업 2: 건설 2단계 법령 룰 데이터 수집 [ChatGPT — 데이터]

### ChatGPT에 전달할 프롬프트

```
산업안전보건법 건설현장 2단계 법령 의무 CSV 생성해줘.

공종(construction_type)별로 적용되는 법령 의무를 아래 형식으로 작성:

컬럼:
rule_id, sector, diagnosis_stage, law_name, law_article, 
obligation_type, obligation_summary, penalty_summary,
condition_code, condition_operator_code, condition_value,
construction_type_required (해당 공종코드, 없으면 ALL)

공종코드:
- EXCAVATION: 굴착공사
- FORMWORK: 거푸집/동바리
- REINFORCEMENT: 철근작업
- CONCRETE: 콘크리트
- STEEL_FRAME: 철골공사
- HIGH_WORK: 고소작업 (2m 이상)
- TUNNEL: 터널공사
- LIFT: 리프트/양중
- BLASTING: 발파작업
- CONFINED_SPACE: 밀폐공간

obligation_type:
- ACTION: 조치 의무
- INSPECT: 점검 의무
- REPORT: 신고 의무
- APPOINT: 선임 의무

각 공종별로 최소 5개 이상 의무 항목 작성.
법령 조문 정확하게 기재 (산안법 제○조).
30개 이상 룰 작성.
```

### 수집 후 DB 적재

```sql
-- diagnosis_stage = 2로 INSERT
UPDATE rule SET diagnosis_stage = 2 WHERE sector = 'CONSTRUCTION' AND ...
```

---

## 작업 3: 건설 3단계 설비 법령 룰 [ChatGPT — 데이터]

```
건설현장 설비별 법정검사 의무 CSV 생성해줘.

설비 종류:
- TOWER_CRANE: 타워크레인
- MOBILE_CRANE: 이동식 크레인
- LIFT: 건설용 리프트
- GONDOLA: 곤돌라
- HOIST: 호이스트
- COMPRESSOR: 공기압축기
- CONCRETE_PUMP: 콘크리트 펌프카
- WELDING_MACHINE: 용접기

컬럼:
rule_id, sector, diagnosis_stage(=3), law_name, law_article,
obligation_type(=INSPECT), obligation_summary, penalty_summary,
condition_code(=equipment_type), condition_value(설비코드),
inspection_cycle_unit_code, inspection_cycle_value

inspection_cycle_unit_code:
001=일1회, 002=주1회, 003=월1회, 006=연1회, 007=2년마다
```

---

## 완료 체크리스트

### 백엔드 (Cursor)
```
□ legal_engine.py v5.1.0
  □ CONDITION_CODE_TO_CONTEXT_KEY에 contract_amount 추가
  □ CONSTRUCTION context 완성 (site_type, subcon_workers, tunnel)
  □ construction_summary 결과 추가
  □ 건설 관련 법령 필터링
□ Railway 배포
□ 검증:
  POST /legal-engine/diagnose/step1
  {
    "sector": "CONSTRUCTION",
    "input": {
      "contract_amount_eok": 200,
      "construction_type": "BUILDING",
      "worker_count": 80,
      "subcon_workers": 30,
      "has_tunnel_bridge": false
    }
  }
  → construction_summary.safety_manager_required: true
  → applicable_count >= 10
  → APPOINT 항목에 안전관리자 선임 포함
```

### 데이터 (ChatGPT → Supabase)
```
□ 2단계 룰 30건 이상 수집·적재
  □ sector = 'CONSTRUCTION'
  □ diagnosis_stage = 2
  □ construction_type_required 컬럼 추가 필요 여부 검토
□ 3단계 룰 10건 이상 수집·적재
  □ sector = 'CONSTRUCTION'
  □ diagnosis_stage = 3
  □ obligation_type = 'INSPECT'
```

---

## 검증 시나리오 (완성 후 이 창에서 확인)

```
시나리오 1: 건축 200억, 80명 현장
→ safety_manager_required: true (150억 이상)
→ APPOINT: 안전관리자, 안전보건관리책임자
→ OTHER: 산업안전보건관리비 계상, 유해위험방지계획서
→ NOTIFY: 안전관리자 선임 신고

시나리오 2: 토목 50억, 20명 현장
→ safety_manager_required: false
→ OTHER: 산업안전보건관리비 계상
→ applicable_count >= 3

시나리오 3: 건축 1,200억 터널 포함
→ safety_manager_required: true
→ APPOINT: 건설안전판정사 포함
```
