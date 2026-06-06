# 핸드오프 — 소비자 입력 ↔ 법령엔진 정합성 추적 세션

> 작성: 2026-06-06 · 창: 기획창(설계/조사) · 산출물: 조사 문서(엔진/코드 미수정)
> 메인 문서: `taieng/docs/2026-06-06_building-input-standardization.md` (§0~§13, 30,356 bytes, commit `ce2d3c2`)

---

> # ⚠️ 정정 고지 (2026-06-06 추가 — 아래 본문보다 이 블록이 우선한다)
>
> 이 문서의 §2-1·§2-2·§2-4·§2-5·§3·§6 결론은 **엔진 구조를 잘못 이해한 상태에서 작성된 오판**이다. 삭제하지 않고 "무엇을 어떻게 틀렸는지" 기록으로 남기되, **아래 정정 내용이 본문 결론을 대체한다.**
>
> ## 무엇을 틀렸나
> 작성 당시 엔진을 **"사전 추출 카탈로그 방식"**(`runtime_metadata_resolution`에 룰·조건이 미리 채워져 있고, 진단은 그걸 조회만 한다)으로 가정했다. 그래서 `condition_value` 채움 7건/3,395행만 보고 **"입력이 판정에 거의 안 쓰인다 / 과적용"**이라 결론냈다.
>
> ## 실제 구조 (확정)
> 법령엔진은 **입력이 들어오면 그때 추출을 시작하는 on-demand 방식**이다. 전체 입력을 **모아서 한 번에** 엔진에 던지고 결과를 받는다(한 필드씩 처리 아님).
> - `runtime_metadata_resolution`의 행수·`condition_value` 채움 여부로 "입력 반영도"를 판단하는 것은 **의미 없다.** 사전 카탈로그가 아니기 때문.
> - `master_rule_v2`가 현재 0행인 것은 데이터 유실이 아니라 **구(舊) 방식이라 더 이상 쓰지 않기 때문**(2026-06-06 사장님 확인).
> - 따라서 §2-2의 "입력 미반영/과적용", §2-4·§2-5의 "현재 판정 영향 없음/파생 불필요", §3-(1)의 "condition 공백이 최우선 이슈", §6의 "시설 상세 입력 판정 기여 0" — **모두 철회.**
>
> ## 코드로 확인된 입력→판정 경로 (`services/diagnosis_runtime_step1.py`, main 기준)
> `run_diagnose_step1_runtime`은 입력을 다음과 같이 **통째로** 판정 맥락에 넣는다:
> ```
> body(시설 입력 전체) → flat_fields{floor_count, electric_capacity, elevator_count,
>     has_high_pressure_gas, has_boiler, has_hazardous_material, has_chemical_substance, ...}
>   → inp 병합 → _input_to_facility_context(sector, inp) → facility_ctx
>   → evaluate_facility_conditions_db(facility_ctx, all_rules, sector)  # 한 번에 평가
> ```
> 즉 입력값이 판정 맥락으로 실제 들어가는 구조가 맞다. `flat_fields`에 시설 필드가 명시 포함돼 있음(코드 확인).
>
> ## 검증 방법에 대한 결론 (2026-06-06 사장님 지침)
> 엔진이 "전체 입력을 모아 던지는" 구조이므로 **일부 필드만 넣는 부분 진단 테스트는 무의미**하다(다른 필드가 비어 facility_ctx가 실사용과 달라져 옆으로 샘). E2E 검증은 화면(P1)·공정·설비까지 결합된 뒤 **전체 입력으로 1회** 수행한다. P5(입력 전달)의 검증은 **소스 경로 도달 확인으로 충분**하며 이미 완료.
>
> ## 여전히 유효한 부분 (정정 영향 없음)
> §2-3(sector 변환: 라이브 경로 정상, 코어 리터럴 INDUSTRIAL은 ValueError), §4(3계층 정합 모델 골격: 폼필드→inp키→ctx키), §5(진입점별 엔진), §7(읽은 파일), §8(보류 작업지시서), 그리고 P5-01~04 구현·검증 결과(2026-06-06 commit `5d25d33`, main 코드 확인 완료)는 유효하다.
>
> ## 다음 세션 정정된 우선순위
> 1. (입력부/Claude) 화면 P1 + 공정·설비(P3·P4)까지 입력 결합 → 전체 입력 E2E 1회.
> 2. 입력→`facility_ctx` 키 정합 점검(폼필드명이 엔진이 기대하는 inp 키와 일치하는지) — 단, 추출·판정 로직 자체는 GPT 영역(READ only).
> 3. ~~룰 condition_value 구조화~~ → 사전 카탈로그 전제였으므로 **삭제**.

---

## 1. 이번 세션에서 한 일 (요약)

소비자 진단에서 **어떤 입력값이 실제로 법령엔진 판정에 쓰이는가**를 코드·DB 근거로 추적. 엔진/스키마/데이터는 **읽기만** 하고 수정하지 않음(GPT 영역). 메인 문서 §8~§13을 새로 채웠다.

> ⚠️ 단, 아래 §2 이하의 "입력 미반영" 계열 결론은 위 정정 고지로 철회됨.

- §8: 소비자(runtime) 경로 입력 소비 — v510과 다름
- §9: 실제 tadmin 입력폼 필드명(건물·산업) ↔ runtime 대조
- §10: `diagnosis_input_fields` 사용처 (tadmin 폼은 미사용)
- §11~§12: `CONDITION_CODE_TO_CONTEXT_KEY` + `evaluate_facility_conditions_db` 전수
- §13: D/A/F 엔진 영향도 (← 오판 포함, 정정 고지 참조)

---

## 2. ~~최우선 발견 (D/A/F 핵심 사실)~~ → 정정 고지로 대체

> 아래 2-1·2-2·2-4·2-5는 **사전 카탈로그 오해 기반 오판**. 기록 보존용으로만 남김. 실제 결론은 상단 정정 고지 참조.

### ~~2-1. 런타임 condition_code는 "딱 4종"만 생성된다~~
(보존) `rule_candidate_projection.py`의 `_apply_runtime_condition`이 `condition_value`를 파싱해 building_area/electric_capacity/construction_amount/employee_count 4종만 만든다고 봤음. → 사전 카탈로그 전제였으므로 판정 영향 추론은 무효.

### ~~2-2. 실제 데이터는 거의 비어 있다~~
(보존·**철회**) `runtime_metadata_resolution` 3,395행 중 condition_value 7건 → "입력 미반영/과적용"으로 결론냈으나, on-demand 추출 구조에서 이 카운트는 무의미. **철회.**

### 2-3. [D] sector 코드 (유효)
- 코어 `run_diagnose_step1_runtime`에 리터럴 `INDUSTRIAL` 도달 시 → **ValueError**.
- 변환은 진입 어댑터에서 보장됨: `diagnosis_integrated_svc`의 `engine_sector = "MANUFACTURING" if sector=="INDUSTRIAL" else sector`, 무료는 `anonymous_diagnosis.py`.
- 결론: 라이브 소비자 경로(통합/무료) 정상. 미변환 위험 = 비활성 `/diagnosis/create`·직접 API 호출뿐.

### ~~2-4. [A] electrical_capacity_kw — 현재 판정 영향 없음~~
(보존·**철회**) "kW 조건 룰 0건 → 영향 없음"은 사전 카탈로그 전제. 단 Layer B 입력키 정합(`electrical_capacity_kw` vs `electric_capacity`) 점검은 여전히 유효한 후속 과제(정정 고지 다음 우선순위 2).

### ~~2-5. [F] 건물용도 → 시설유형 파생 — 현재 불필요~~
(보존·**철회**) "매칭 룰 0건 → 파생 불필요"는 사전 카탈로그 전제. 건물용도 입력이 추출에 쓰이는지는 전체 입력 E2E로 확인 대상.
- 폼 building_use 값(참고, 유효): 업무/판매/근린생활/의료/교육연구/숙박/운수/창고/공장/기타.

---

## 3. ~~즉시 정합성 이슈~~ → 정정

> §3-(1) "룰 condition 공백 최우선"은 **철회**(사전 카탈로그 전제). 나머지는 GPT 영역 관찰 기록으로만 보존하며, 진위는 엔진 담당(GPT)이 판단.

1. ~~(최우선) 룰 condition 공백~~ → **철회.**
2. (보존, GPT 판단) `project_metadata_to_v1` sector_hint 덮어쓰기 관찰.
3. (보존, GPT 판단) `"별표3(종류+인원)"` 파싱 관찰.
4. (보존) `legal_runtime_fetch.py` 주석과 사용처 표현 불일치 관찰.

---

## 4. 3계층 정합 모델 (유효 — 입력부 후속 과제의 뼈대)

입력이 판정에 닿으려면 폼필드→inp키→ctx키가 정합해야 한다:
```
폼필드명 →(라우터/어댑터)→ inp키 →(_input_to_facility_context)→ ctx키 → (추출·평가)
```
- `_input_to_facility_context`·추출·평가 로직 = **엔진(GPT) 영역(READ only)**
- 폼 필드명·어댑터 전달 = **입력부(Claude) 영역** ← P5가 여기를 고침

---

## 5. 진입점별 엔진 (확정·유효)

- `/anonymous-diagnosis`(무료) → runtime (`run_diagnose_step1_runtime`)
- `/diagnosis/run`(통합·Nexas) → runtime
- `/legal-engine/diagnose/step1`(v510, factory_id) → 레거시(`master_building_legal_rules_legacy_contaminated`)
- tadmin 상세폼 `/diagnosis/create`·`/diagnosis/{id}` → 2026-06-06 롤백·비활성. 입력 저장 표준 = `factories`→`factory_process`→`equipment_assets`.

---

## 6. ~~소비자 화면 필수 유지 필드~~ → 정정

> "그 외 시설 상세 입력은 판정 기여 0"은 **철회**. on-demand 추출 구조에서는 시설 입력 전반이 추출 입력이 될 수 있으므로, 어떤 필드가 실제 추출에 쓰이는지는 전체 입력 E2E로 확인한다. 아래 확정 항목(과금·게이트 관련)은 유효.
- `sector`(라우팅), `worker_count`/`employee_count`(건설 50명 선임 게이트), `contract_amount_eok`(건설 임계·선임), `floor_area`(과금 등급) — 유효.
- 그 외 시설 상세(층수·전기·승강기·위험물 플래그 등) — P5로 엔진 전달됨, 추출 반영 여부는 E2E 확인 대상.

---

## 7. 읽은 파일 (근거)

`services/diagnosis_runtime_step1.py`, `services/legal_runtime_fetch.py`, `services/rule_candidate_projection.py`, `services/legal_context.py`, `services/legal_rules.py`, `services/legal_engine_svc.py`, `services/diagnosis_integrated_svc.py`, `services/diagnosis_nexas_adapter.py`, `schemas/legal_engine.py`, `schemas/diagnosis_integrated.py`, tadmin 입력폼 3종. DB: `runtime_metadata_resolution`·`master_rule_v2`(0행 확인)·`diagnosis_input_fields` (Supabase `vwlahtguyggrhvslabax`).

---

## 8. 보류/미진행 작업지시서 (참고, 미실행)

### 8-1. "45CM Database Architecture & Standards (2차)" — 보류("잘못 들어간 내용")
미생성: `docs/database/architecture/*`·`docs/database/standards/*`·`docs/database/adr/{004,005,006}` (9개 전부).

### 8-2. "Phase 5 : Contract OS Discovery" — 미착수
미생성: `docs/architecture/{CONTRACT_OS, CONTRACT_VERSION_MODEL, ENGINE_FEDERATION_MODEL}.md`, `DATABASE_LAW` 제14조, `docs/database/adr/{007,008,009}`. 선행조건 미확정: 대상 레포·`DATABASE_LAW` 위치·ADR-001~003 위치.

---

## 9. 다음 세션 추천 순서 (정정 반영)

1. (입력부/Claude) 화면 P1 + 공정·설비(P3·P4) 입력 결합 → **전체 입력으로 E2E 1회**(부분 테스트 금지).
2. (입력부/Claude, READ 한도) 폼필드→inp→ctx 키 정합 점검. 추출·판정 로직은 GPT 영역.
3. (의사결정) Phase 5 Contract OS Discovery 진행 여부 + 선행조건(8-2) 확정.
4. ~~룰 condition_value 구조화~~ → 사전 카탈로그 전제였으므로 **삭제**.

---

## 부록 A. P5 구현·검증 결과 (2026-06-06, 유효)

Week1 P5(입력 전달 통로) 구현 완료·main 코드 확인:
- **P5-01** `schemas/diagnosis_integrated.py`: `DiagnosisRunBody`에 시설 필드 11종 추가(floor_count·electric_capacity·elevator_count·has_gas·has_chemical·is_multi_use·has_boiler·has_hazardous_material·has_high_pressure_gas·has_chemical_substance·project_amount).
- **P5-02** `diagnosis_nexas_adapter.py`: `_FORM_ALIASES`에 `project_amount→contract_amount_eok`, `_NUMERIC_FIELDS`에 floor_count·electric_capacity.
- **P5-03** `diagnosis_integrated_svc.run_diagnosis` BUILDING: `floor_count=body.floor_count or 5`(하드코드 5 제거, 입력 우선). `upgrade_diagnosis`는 의도적으로 5 유지(Week2).
- **P5-04** BUILDING/MANUFACTURING ctor에 시설 flat 필드 전달. `DiagnoseStep1Body`에 해당 필드 기존 존재 → 엔진/스키마 무변경.
- 엔진/룰 파일 5종 미수정. tai-api commit `5d25d33`, Railway v6.0.2 배포 + `/cron/reload` 200.
- 검증: 엔진이 전체 입력 일괄 처리 구조이므로 부분 진단 실행 생략, **소스 경로 도달 확인으로 완료**. 전체 E2E는 P1·P3·P4 결합 후.
