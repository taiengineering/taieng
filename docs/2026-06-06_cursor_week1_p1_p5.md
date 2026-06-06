# Cursor 작업지시서 — Consumer Diagnosis V1 Week1 구현 (P1 · P5)

> **발주:** Claude 기획창 · **수행:** Cursor / Claude Code (로컬 편집 + git push)
> **작성일:** 2026-06-06
> **기준 문서(새 설계 없음, 아래 확정분만 구현):**
> - `45cminc/federation-contracts/docs/WEEK1_IMPLEMENTATION_PLAN.md`
> - `45cminc/federation-contracts/docs/CONSUMER_DIAGNOSIS_V1_IMPLEMENTATION_TASKS.md`
> - `45cminc/federation-contracts/docs/TAI_INPUT_STANDARD_V1.md`
> - `45cminc/federation-contracts/docs/HANDOFF_TAI_DIAGNOSIS_PIPELINE.md`

---

## 0. 절대 금지 (어기면 작업 무효)
- 가격정책 변경 금지 (tier 코드·금액·`auto_tier`·`paid_tier_prices` 손대지 말 것)
- **엔진/룰 변경 금지** — `services/legal_context.py`, `services/legal_rules.py`, `services/rule_candidate_projection.py`, `services/legal_runtime_fetch.py`, `services/diagnosis_runtime_step1.py` **수정 금지**
- SaaS 구조 변경 금지 (factories/process/equipment 스키마·라우터 손대지 말 것)
- 입력 플로우(진단 실행 경로) 변경 금지 — 기존 `POST /diagnosis/run` 흐름 유지
- 신규 설계·신규 필드 발명 금지 — 아래 명시된 **기존 필드**만 사용
- **DB(`diagnosis_input_fields`)는 이미 P2에서 완료** — 이 지시서에서 DB 작업 없음

**전제 사실(이미 검증됨):**
- `schemas/legal_engine.py`의 `DiagnoseStep1Body`에는 `electric_capacity, floor_count, elevator_count, has_high_pressure_gas, has_boiler, has_hazardous_material, has_chemical_substance` 등이 **이미 정의되어 있음** → 엔진 스키마 추가 불필요. ctor 호출 시 "전달만" 하면 됨.
- P2 DB 반영 완료: BUILDING FREE = 5필드(address, total_floor_area, floor_count, building_use_type, worker_count), INDUSTRIAL FREE/PAID1 = 4필드(address, ksic_major, worker_count, total_floor_area).

---

## 작업 A — 화면 3계층 골격 (P1-01, P1-04)

### 대상 파일
`taiengineering/taieng` → `nexas/free-diagnosis.html`

### P1-01 — Step 2를 시설/공정/설비 패널로 분리
- 현재: Step 2가 단일 flat 동적 폼(`loadFreeForm`/`loadPaidForm`).
- 작업: Step 2 내부를 **2a 시설 / 2b 공정 / 2c 설비** 패널로 분리하고, sector·tier에 따라 show/hide.
- 노출 규칙(WEEK1 범위 = FREE 위주, 공정·설비 패널은 골격만 만들고 비노출 상태로 둠):
  - BUILDING: 시설(2a)만. 공정 패널 없음.
  - INDUSTRIAL FREE: 시설(2a)만.
  - CONSTRUCTION FREE: 시설(2a)만.
- **주의:** 공정·설비의 실제 항목 채우기(P3·P4)는 Week2다. 지금은 **패널 컨테이너와 show/hide 로직만**. 기존 본인인증·면책·섹터선택·progress bar는 그대로 유지.

### P1-04 — formValues를 3계층으로 구조화
- 현재: `formValues.free/paid`가 flat.
- 작업: 제출 직전 `form_data`를 `{ facility:{...}, process:[...], equipment:[...] }` 형태로 묶거나, field_code prefix로 계층 구분.
- **중요(백엔드 호환):** `POST /diagnosis/run` 제출 시 최종 `form_data`는 **기존 flat 구조도 그대로 포함**해야 한다(백엔드 adapter가 flat key를 읽음). 즉 계층 구조는 추가하되 flat key를 제거하지 말 것. Week1에서는 facility 값만 채워지면 됨.

### 완료 조건
- INDUSTRIAL FREE 화면에 시설 패널만 보임(공정/설비 패널 비노출).
- 제출 시 Network 탭 `POST /diagnosis/run` body.form_data에 시설 입력값이 그대로 들어감.

---

## 작업 B — 입력 전달 통로 (P5-01, P5-02)

### B-1. P5-01 — `DiagnosisRunBody`에 시설 필드 추가
**대상:** `taiengineering/tai-api` → `schemas/diagnosis_integrated.py` → `class DiagnosisRunBody`

현재 `DiagnosisRunBody`에 **없어서 adapter gate에서 버려지는** 시설 필드를 추가한다. 아래 필드만 `Optional`로 추가(기존 필드 삭제·변경 금지):

```python
    # --- P5-01: 시설 입력 전달용 (Week1 = 시설 범위) ---
    floor_count: Optional[int] = None
    electric_capacity: Optional[float] = None
    elevator_count: Optional[int] = None
    has_gas: Optional[bool] = None
    has_chemical: Optional[bool] = None
    is_multi_use: Optional[bool] = None
    has_boiler: Optional[bool] = None
    has_hazardous_material: Optional[bool] = None
    has_high_pressure_gas: Optional[bool] = None
    has_chemical_substance: Optional[bool] = None
    project_amount: Optional[float] = None
```
> 이유: adapter(`nexas_run_body_from_request`)는 `target not in DiagnosisRunBody.model_fields`면 버린다. model_fields에 있어야 통과.
> **공정/설비(process_list·equipment_list)는 Week2(P3-01·P4-02)** — 지금 추가하지 말 것.

### B-2. P5-02 — `project_amount` alias 연결
**대상:** `taiengineering/tai-api` → `services/diagnosis_nexas_adapter.py` → `_FORM_ALIASES`

현재 `_FORM_ALIASES`(파일 상단)에 `project_amount`가 없다. 한 줄 추가:
```python
_FORM_ALIASES: Dict[str, str] = {
    "workers": "worker_count",
    "ksic_code": "ksic_major",
    "project_address": "region",
    "address": "region",
    "project_amount": "contract_amount_eok",   # P5-02
}
```
> 그리고 `_NUMERIC_FIELDS`에는 `contract_amount_eok`가 이미 있으므로 숫자 변환은 자동. `project_amount` 자체는 추가 불필요(alias로 contract_amount_eok에 흡수).

---

## 작업 C — 엔진 전달 (P5-03, P5-04)

**대상:** `taiengineering/tai-api` → `services/diagnosis_integrated_svc.py`
**함수:** `run_diagnosis` (그리고 동일 패턴이 `upgrade_diagnosis`에도 있음)

### C-1. P5-03 — BUILDING `floor_count=5` 하드코드 제거
현재 `run_diagnosis`의 BUILDING 분기:
```python
    elif engine_sector == "BUILDING":
        step1_body = DiagnoseStep1Body(
            ...
            floor_count=5,            # ← 하드코드
        )
```
→ `floor_count=body.floor_count or 5` 로 변경(입력값 있으면 사용, 없을 때만 기존 기본값 5 유지 = 회귀 안전).
> `upgrade_diagnosis`의 BUILDING 분기에도 동일한 `floor_count=5`가 있음. 거기서는 `input_data`에 floor_count가 없으므로 **이번엔 건드리지 말 것**(P5-07에서 input_data 저장 후 Week2 처리). run_diagnosis 쪽만 수정.

### C-2. P5-04 — 시설 flat 필드를 Step1 ctor에 전달
`DiagnoseStep1Body`에 이미 존재하는 필드만 전달(엔진/스키마 추가 없음).

BUILDING 분기 ctor에 추가:
```python
            electric_capacity=body.electric_capacity,
            elevator_count=body.elevator_count,
            has_high_pressure_gas=body.has_gas if body.has_gas is not None else None,
            has_hazardous_material=body.has_chemical if body.has_chemical is not None else None,
```
MANUFACTURING(else) 분기 ctor에 추가:
```python
            electric_capacity=body.electric_capacity,
            has_boiler=body.has_boiler,
            has_hazardous_material=body.has_hazardous_material,
            has_high_pressure_gas=body.has_high_pressure_gas,
            has_chemical_substance=body.has_chemical_substance,
```
> **금지:** `legal_context.py`는 절대 수정하지 말 것. 위는 "엔진에 값을 넘기는 것"까지만. 엔진이 그 값을 어떻게 쓰는지는 GPT 영역.
> `is_multi_use`는 `DiagnoseStep1Body`에 필드가 없으므로 **이번엔 ctor 전달 제외**(Week2 P5-09에서 adapter inp merge 경로로 처리). 추가하지 말 것.

---

## 작업 순서 (의존성)
```
1. B-1 (P5-01)  schemas — DiagnosisRunBody 필드 추가      [먼저: adapter/ctor가 이걸 참조]
2. B-2 (P5-02)  adapter — project_amount alias
3. C-1 (P5-03)  svc — floor_count 하드코드 제거
4. C-2 (P5-04)  svc — 시설 flat ctor 전달
5. A   (P1-01, P1-04)  free-diagnosis.html  [화면, 백엔드와 병렬 가능]
```
- B·C(tai-api)와 A(taieng)는 **다른 레포라 병렬 가능**. 단 B-1을 가장 먼저.

## 배포
- tai-api: main push → Railway 자동 배포. 배포 후 `POST /cron/reload` 1회 필요.
- taieng: main push → Cloudflare Pages 자동 배포.

## 검증 (HANDOFF §10 절차로 1건 추적)
BUILDING 무료 진단에서 **층수**를 바꿔 제출 → 결과 비교:
```
1 화면      free-diagnosis.html 제출 시 form_data.floor_count 포함 (Network)
2 DTO       DiagnosisRunBody.floor_count 채워짐
3 svc       run_diagnosis BUILDING ctor floor_count = 입력값 (5 아님)
4 결과      anonymous_diagnosis_results.full_result 생성 확인
```
SQL 확인:
```sql
SELECT input_data, engine_version
FROM anonymous_diagnosis_results
ORDER BY created_at DESC LIMIT 3;
```

## 완료 보고 형식
1. 변경 파일 목록 + commit SHA
2. P5-01/02/03/04, P1-01/04 각 반영 여부
3. Railway·Cloudflare 배포 결과
4. 검증(층수 변경→결과 반영) 결과

---

## 이번 지시서에서 하지 않는 것 (Week2 이후)
- 공정·설비(P3·P4) 항목 구현, `process_list`/`equipment_list` adapter·저장(P5-07)
- ctx alias merge(P5-08)·is_multi_use(P5-09)
- CONSTRUCTION worker 분리(P5-05)·has_blasting/has_crane(P5-06)
- 회귀 테스트(P5-10), 결과 출력(P6), 결제(P7), SaaS 전환(P8)
