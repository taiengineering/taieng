# INPUT PIPELINE CONNECTION REPORT V1
# WO-INPUT-PIPELINE-CONNECTION-001

**작성일**: 2026-06-20
**목적**: 섹터별 입력부 → 거름망 → Compiler Core 연결.
**금지 준수**: 법령/rule/draft_slot/Compiler Core/거름망/VR 수정 없음. 결과·의무 분석 없음.
**결과**: STEP-1 매핑 수행 + STEP-4 도달 실측 완료. STEP-2/3 구조적 차단 보고.

---

## STEP-1: field_code → FacilityProfile 매핑표 (수행 완료)

```
3섹터 입력 필드 55개 중 36개가 FacilityProfile field에 매핑됨 (이름차 해소).
미매핑 19개 = FacilityProfile에 대응 필드 없음
  (address, process_list, equipment_list, subcontractor,
   소방 5종, 다중이용 2종, 저수조 2종 등 — 평가에 안 쓰이는 입력).
```

| sector | field_code | FacilityProfile field | 매핑 |
|---|---|---|---|
| BUILDING | worker_count | workforce.regular_workers | O |
| BUILDING | total_floor_area | building.floor_area | O |
| BUILDING | building_use_type | building.use_code | O |
| BUILDING | electric_capacity | metrics.electrical_kw | O |
| BUILDING | transformer_capacity_kva | facility_physical.transformer_kva | O |
| BUILDING | elevator_count | facility_physical.elevator_count | O |
| BUILDING | annual_energy_toe | facility_physical.annual_energy_toe | O |
| BUILDING | (소방/다중이용/저수조 등 12종) | 없음 | X |
| INDUSTRIAL | worker_count | workforce.regular_workers | O |
| INDUSTRIAL | ksic_major | ksic_code | O |
| INDUSTRIAL | has_chemical_substance | facility_hazard.has_chemical_material | O |
| INDUSTRIAL | has_high_pressure_gas | facility_hazard.has_high_pressure_gas | O |
| INDUSTRIAL | electric_capacity | metrics.electrical_kw | O |
| INDUSTRIAL | process_list / equipment_list / address | 없음 | X |
| CONSTRUCTION | project_amount | metrics.construction_amount | O |
| CONSTRUCTION | construction_type | construction.construction_type | O |
| CONSTRUCTION | has_tower_crane | construction.has_tower_crane | O |
| CONSTRUCTION | has_blasting | construction.has_blasting | O |
| CONSTRUCTION | has_asbestos_demo | construction.has_asbestos | O |
| CONSTRUCTION | has_confined_space | construction.has_confined_space | O |
| CONSTRUCTION | has_diving | construction.has_diving_work | O |
| CONSTRUCTION | subcontractor_count | construction.subcontractor_company_count | O |
| CONSTRUCTION | worker_count | workforce.regular_workers | O |
| CONSTRUCTION | process_list / project_address / subcontractor | 없음 | X |

```
IC-01 (field_code 매핑): 평가 대상 필드는 100% 매핑.
  단 19개는 FacilityProfile에 대응 필드 자체가 없음(매핑 불가).
```

---

## ★ STEP-4: Compiler Core 도달 실측 (현재 상태, 수정 없음)

```
각 sector 실제 factory 10건을 현재 상태 그대로 측정:

| sector       | factory 10건 | facility_applicability 도달 | task_candidate 도달 |
|--------------|--------------|----------------------------|---------------------|
| BUILDING     | 10           | 1 (YES 1/NO 9)             | 1 (YES 1/NO 9)      |
| INDUSTRIAL   | 10           | 0 (NO 10)                  | 0 (NO 10)           |
| CONSTRUCTION | 10           | 0 (NO 10)                  | 0 (NO 10)           |
```

---

## ★★ 핵심 발견: 거름망이 전체 factory에 실행되지 않았음

```
facility_applicability 29,096건의 실제 분포 (factory 단위):
  INDUSTRIAL   16개 factory → 14,974건
  BUILDING     10개 factory →  8,640건
  CONSTRUCTION  6개 factory →  5,482건
  합계 = 단 32개 factory

전체 factory ≈ 700개 (BUILDING 278 / INDUSTRIAL 225 / CONSTRUCTION 195).

= 거름망(run_facility_applicability)은 전체 factory가 아니라
  과거에 32개 테스트 factory에만 실행되었다.
  나머지 ~670개 factory는 거름망을 한 번도 통과하지 않았다.

→ "입력→Compiler Core 끊김"의 1차 원인은 매핑이 아니라
  배치 미실행(전체 factory 대상 거름망 미가동).
```

---

## STEP-2: auto_source 연결 — 구조적 차단 (구현 안 함)

```
직전 WO 실측:
  auto_source는 "입력→엔진 매핑"이 아니라
  "입력→외부 데이터소스 자동조회" 컬럼이다.
  (BUILDING 일부가 auto_source='building_register'=건축물대장 자동조회)

  여기에 FacilityProfile field를 넣으면:
    (1) auto_source 원래 의미(어디서 자동으로 값 끌어오나) 오염.
    (2) 거름망(run_facility_applicability)은 auto_source를 읽지 않음
        (배치는 factories 11컬럼 + FIELD_MAP만 봄).
  → auto_source를 채워도 거름망에 전달 안 됨.

IC-02 (auto_source NULL 0건): 미수행.
  채우면 의미 오염 + 거름망 미연결로 무효. 구현하지 않음.
```

---

## STEP-3: 거름망 입력 연결 — 구조적 차단 (구현 안 함)

```
거름망 입력 통로 = draft_slot.binding_field (11종).
  건설 전용 binding_field = 0종 (직전 WO 확인).
  tower_crane/blasting/process_list를 연결하려 해도
  매칭될 draft_slot이 없음.

IC-05 (task_candidate 생성 확인)와 "draft_slot 생성 금지"가 충돌:
  건설 task_candidate가 생성되려면 건설 draft_slot 필요.
  그러나 draft_slot 생성 금지 명시.
  → Claude 단독으로 건설 도달 생성 불가 (GPT 법령 컴파일 선행).
```

---

## 완료 기준 점검 (정직)

```
IC-01 field_code 100% 매핑  → 평가대상 100%, 단 19개는 대응필드 부재
IC-02 auto_source 연결      → 미수행 (의미충돌+거름망 미연결, 구현 안 함)
IC-03 3섹터 입력 도달 확인  → 실측: 건물1/산업0/건설0 (대부분 미도달)
IC-04 facility_applicability 생성 → 32개 factory만 존재(과거 부분실행)
IC-05 task_candidate 생성   → 동일 32개만. 건설 도달은 draft_slot 부재로 불가
IC-06 법령 수정 0건         → ✅
IC-07 엔진 수정 0건         → ✅
```

---

## 연결 리포트 (각 단계 YES/NO)

```
입력항목(diagnosis_input_fields)
  ↓ YES (55개 정의, 36개 프로파일 매핑 가능)
FacilityProfile
  ↓ 부분 (build_facility_profile은 factories row→프로파일 생성 가능)
거름망(run_facility_applicability)
  ↓ NO (전체 factory 미실행. 32개만 과거 실행)
facility_applicability
  ↓ 부분 (32개 factory만 존재)
task_candidate
     (32개 factory만. 건설 고유 의무는 binding_field 0으로 미생성)
```

---

## 정직한 결론 (이 WO가 도달한 지점)

```
"입력→Compiler Core 끊김"은 단일 원인이 아니라 3겹이다:

[1] 배치 미실행 (최우선, Claude 영역일 수 있음)
    거름망이 전체 factory(~700)가 아닌 32개에만 실행됨.
    → 전체 대상 재실행하면 산업/건물은 도달 늘어날 것
      (단 railway run 실행 = Claude 환경에서 직접 불가, 사장님/로컬 실행).

[2] auto_source 미연결 (구조)
    입력 UI 필드와 거름망 입력이 다른 경로. auto_source는 외부조회용.

[3] 건설 binding_field 0 (GPT 선행 필요)
    건설은 배치를 돌려도 매칭할 draft_slot이 없어 미도달.

이 WO는 STEP-1 매핑 + STEP-4 도달 실측까지 수행.
STEP-2/3는 구조적 차단으로 구현하지 않음(추정 구현 금지).
다음 가능한 실제 작업 = [1] 전체 factory 거름망 재실행
  (Claude는 스크립트 준비 가능, 실행은 railway 환경 필요).
```
