# WO-FULL-PIPELINE-TRACE-001 관찰 결과 보고

**작성일**: 2026-06-17  
**성격**: 관찰만. 설계 변경 없음.  
**용도**: GPT에게 전달 — 다음 단계 판단 요청

---

## 한 문장 요약

> 소비자가 입력한 데이터는 엔진까지 대부분 전달된다.
> 단, Step 2(공정)와 Step 3(설비)는 입력은 받지만 판정에 미사용 상태다.
> boolean 플래그(has_boiler 등)는 입력받지만 factories에 미저장이다.

---

## 실제 소비자 입력 필드 (DiagnoseStep1Body 기준)

### INDUSTRIAL
```
worker_count, employee_count, floor_area,
ksic_major (업종코드), electric_capacity,
has_boiler, has_high_pressure_gas,
has_chemical_substance, has_hazardous_material,
gas_capacity_kg, boiler_capacity_kw
```

### CONSTRUCTION
```
contract_amount_eok, direct_workers, subcon_workers,
construction_type, has_tunnel_bridge, has_blasting,
has_crane, has_high_work
```

### BUILDING
```
building_use_type, floor_area, total_floor_area,
worker_count, floor_count, elevator_count
```

---

## 엔진 연결 흐름

```
DiagnoseStep1Body
  ↓ normalize_consumer_inp()
  ↓ create_temp_factory()     → factories 임시 행 생성
  ↓ evaluate_single_factory() → draft_slot IF_NUMERIC 비교
  ↓ fetch_compiler_candidates() → MATCH_CANDIDATE 추출
  ↓ cleanup_temp_factory()    → 임시 행 삭제
```

---

## INPUT TRACE MATRIX

| 필드 | 저장 | 평가 | Verdict | 분류 |
|---|---|---|---|---|
| worker_count | ✅ employee_count | ✅ IF_NUMERIC | ✅ | TYPE D USED |
| ksic_major | ✅ ksic_code | △ sector 필터만 | △ | TYPE B PARTIAL |
| floor_area | ✅ | ✅ IF_NUMERIC | ✅ | TYPE D USED |
| contract_amount_eok | ✅ | ✅ IF_NUMERIC | ✅ | TYPE D USED |
| electrical_capacity_kw | ✅ | ✅ IF_NUMERIC | ✅ | TYPE D USED |
| gas_capacity | ✅ | ✅ IF_NUMERIC | ✅ | TYPE D USED |
| elevator_count | ✅ | ✅ IF_NUMERIC | ✅ | TYPE D USED |
| floor_count | ✅ | ✅ IF_NUMERIC | ✅ | TYPE D USED |
| has_boiler | ❌ 미저장 | ❌ | ❌ | TYPE A UNUSED |
| has_high_pressure_gas | ❌ 미저장 | ❌ | ❌ | TYPE A UNUSED |
| has_chemical_substance | ❌ 미저장 | ❌ | ❌ | TYPE A UNUSED |
| has_hazardous_material | ❌ 미저장 | ❌ | ❌ | TYPE A UNUSED |
| has_crane | ❌ 미저장 | ❌ | ❌ | TYPE A UNUSED |
| has_high_work | ❌ 미저장 | ❌ | ❌ | TYPE A UNUSED |
| Step2 공정 | ⚠️ factory_process | ❌ 미사용 | ❌ | TYPE B PARTIAL |
| Step3 설비 | ⚠️ equipment_assets | ❌ 미사용 | ❌ | TYPE B PARTIAL |

---

## 이전 판단 오류 수정

잘못된 판단: DB 테스트 데이터 기반으로 ksic_code=null → UNKNOWN이라고 판단.

수정: 실제 소비자 진단에서는 ksic_major를 입력받아 factories.ksic_code에 저장한다.
DB의 null은 테스트 데이터 문제였다.

---

## GPT에게 질문

### 질문 1. boolean 필드 (TYPE A)

has_boiler 등이 create_temp_factory()에서 factories에 저장되지 않습니다.

- A: 의도적 설계 — IF_SCOPE로 처리 예정이라 현재 미연결이 맞다
- B: 구현 누락 — 저장해야 하는데 빠진 것이다
- C: V4 FacilityProfile에서 처리 예정 (Phase 0B 이후)

### 질문 2. 공정/설비 (TYPE B)

Step 2 공정, Step 3 설비가 evaluate_single_factory()에 미사용인 이유는?
공정과 설비가 판정에 들어가려면 draft_slot에 IF_SCOPE 조건이 있어야 하는가, 아니면 별도 경로가 필요한가?

### 질문 3. ksic_code 역할

현재 ksic_code는 law_sector_mapping sector 필터에만 간접 사용됩니다.
V4 ApplicabilityCondition INDUSTRY Scope와 직접 연결하려면 지금 상태로 충분한가?

### 질문 4. Phase 4 재정의

수치 필드는 이미 연결됨, boolean 미연결, 공정/설비 미사용인 상태에서
Phase 4 목표를 어떻게 재정의해야 하는가?

### 질문 5. 다음 우선순위

- A: boolean 필드를 create_temp_factory에 추가 연결
- B: V4 FacilityProfile에 boolean 처리 추가
- C: 공정/설비 평가 경로 설계
- D: 수치 필드 연결로 충분한지 실제 30개 검증 먼저
- E: 다른 것

---

## 절대 금지

```
Track A 수정
GPT 전속 테이블 수정
factories 구조 변경
FacilityProfile 수정 (GPT 판단 전)
새 설계 작성 (GPT 판단 전)
```
