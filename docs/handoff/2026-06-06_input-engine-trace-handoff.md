# 핸드오프 — 소비자 입력 ↔ 법령엔진 정합성 추적 세션

> 작성: 2026-06-06 · 창: 기획창(설계/조사) · 산출물: 조사 문서(엔진/코드 미수정)
> 메인 문서: `taieng/docs/2026-06-06_building-input-standardization.md` (§0~§13, 30,356 bytes, commit `ce2d3c2`)

---

## 1. 이번 세션에서 한 일 (요약)

소비자 진단에서 **어떤 입력값이 실제로 법령엔진 판정에 쓰이는가**를 코드·DB 근거로 추적. 엔진/스키마/데이터는 **읽기만** 하고 수정하지 않음(GPT 영역). 메인 문서 §8~§13을 새로 채웠다.

- §8: 소비자(runtime) 경로 입력 소비 — v510과 다름
- §9: 실제 tadmin 입력폼 필드명(건물·산업) ↔ runtime 대조
- §10: `diagnosis_input_fields` 사용처 (tadmin 폼은 미사용)
- §11~§12: `CONDITION_CODE_TO_CONTEXT_KEY` + `evaluate_facility_conditions_db` 전수
- §13: **D/A/F 엔진 영향도 확정** (이번 핵심)

---

## 2. ★최우선 발견 (D/A/F 핵심 사실)

### 2-1. 런타임 condition_code는 "딱 4종"만 생성된다
`services/rule_candidate_projection.py` → `_apply_runtime_condition`이 `runtime_metadata_resolution.condition_value`(텍스트)를 정규식 파싱해 condition_code를 만든다. 생성 가능한 건:
- `building_area` (텍스트에 ㎡/m2)
- `electric_capacity` (kW)
- `construction_amount` (억)
- `employee_count` (명/인)

그 외 모든 행 → `condition_code=""` → `evaluate_facility_conditions_db`에서 **조건없는 룰 = (대개) 무조건 적용**.

### 2-2. 실제 데이터는 거의 비어 있다 (DB 확정)
`runtime_metadata_resolution` 총 **3,395행** 중 `condition_value`가 채워진 행 = **7건**, 4종 단위로 인식되는 건 **1건**뿐(그나마 `"별표3(종류+인원)"` → `employee_count≥3` **오파싱**). 나머지 3,388행은 무조건 적용.
→ **현재 런타임은 입력값으로 거의 필터링하지 않는다.** 대부분 의무가 입력과 무관하게 적용되는 상태.

### 2-3. [D] sector 코드
- 코어 `run_diagnose_step1_runtime`(`services/diagnosis_runtime_step1.py`)에 리터럴 `INDUSTRIAL` 도달 시 → **ValueError**(allowed-guard가 컨텍스트 생성보다 먼저, Default Context 아님).
- 변환은 진입 어댑터에서 보장됨: `diagnosis_integrated_svc.run_diagnosis`/`upgrade_diagnosis`의 `engine_sector = "MANUFACTURING" if sector=="INDUSTRIAL" else sector`, 무료는 `anonymous_diagnosis.py`의 SECTOR_BY_KIND.
- `diagnosis_nexas_adapter.py`·`normalize_sector_db`는 변환 안 함.
- 결론: 라이브 소비자 경로(통합/무료)는 정상. 미변환 위험 = 비활성 `/diagnosis/create`·직접 API 호출뿐.

### 2-4. [A] electrical_capacity_kw
- Layer C(`CONDITION_CODE_TO_CONTEXT_KEY`)는 `electrical_capacity_kw`·`electric_capacity` → ctx `electric_capacity`로 매핑.
- 그러나 런타임 룰 cc는 `electric_capacity`로만 생성되고, **DB상 kW 조건 룰 = 0건** → **현재 판정 영향 없음**.
- Layer B(`legal_context.py`) BUILDING/MANUFACTURING는 `inp["electric_capacity"]`만 읽음(폼은 `electrical_capacity_kw` 전송) → ctx 0으로 드롭. CONSTRUCTION만 둘 다 허용.
- 결론: 현재 미사용. 예방적으로 Layer B를 `electrical_capacity_kw or electric_capacity`로 통일 권장(엔진 영역).

### 2-5. [F] 건물용도 → 시설유형 파생
- 런타임 투영이 시설유형/`building_use_code` condition_code를 **생성 안 함** → 매칭 룰 0건 → **현재 파생 불필요**.
- 그런 룰은 cc=""로 무조건 적용(누락이 아니라 **과적용** 방향).
- 플래그 종류·판정기준(F2/F3) = 법령 도메인 = **확인불가(코드 근거 없음)**.
- 폼 building_use 값: 업무/판매/근린생활/의료/교육연구/숙박/운수/창고/공장/기타.

---

## 3. 즉시 정합성 이슈 (엔진 = GPT 영역, 우선순위)

1. **(최우선) 룰 condition 공백** — `condition_value` 3,388/3,395 미채움. **입력 표준화 이전에 엔진 룰 condition 구조화가 선행**돼야 입력이 판정에 의미를 가진다.
2. **sector 필터 무력화(과적용)** — `project_metadata_to_v1`이 `sector_hint`로 전 룰 sector를 요청 섹터로 덮어씀 → 원 sector(공통/제조/건설) 무시, `filter_runtime_for_sector` 전량 통과. 건물·제조는 전 카탈로그 적용(건설만 법령 prefix 필터).
3. **오파싱 1건** — `"별표3(종류+인원)"`(산안법 17조) → `employee_count≥3` 잘못 생성.
4. **카탈로그 주석 모순** — `legal_runtime_fetch.py` 헤더는 "CATALOG ONLY / 진단 격리"라 적혀 있으나 `run_diagnose_step1_runtime`은 실제 진단 소스로 사용(`rule_version="runtime_metadata_resolution:v1"`).

---

## 4. 3계층 정합 모델 (입력 표준화의 뼈대)

룰이 작동하려면 셋이 **같은 facility_ctx 키**에서 만나야 한다:
```
폼필드명 →(라우터/어댑터)→ inp키 →(_input_to_facility_context: Layer B)→ ctx키
                                   ←(CONDITION_CODE_TO_CONTEXT_KEY: Layer C)← 룰 condition_code
```
- Layer B·C·룰데이터·sector스탬프·파싱 = **엔진(GPT) 영역**
- 폼 필드명 = **입력부(Claude) 영역**

---

## 5. 진입점별 엔진 (확정)

- `/anonymous-diagnosis`(무료) → runtime (`run_diagnose_step1_runtime`)
- `/diagnosis/run`(통합·Nexas) → runtime
- `/legal-engine/diagnose/step1`(v510, factory_id) → 레거시(`master_building_legal_rules_legacy_contaminated`)
- tadmin 상세폼의 `/diagnosis/create`·`/diagnosis/{id}`(draft CRUD) → **2026-06-06 롤백·비활성**. 입력 저장 표준 = `factories`→`factory_process`→`equipment_assets`, 임시저장 = `factories.diagnosis_status='DRAFT'`.

---

## 6. 소비자 화면 필수 유지 필드 (현재 실사용, 코드 근거)

- `sector` (라우팅 필수)
- `worker_count`/`employee_count` — 건설 산안법16조 50명 선임 게이트 + `get_construction_summary`
- `contract_amount_eok` → `construction_amount` — 건설 임계(1/50/100/120/150/200억)·선임 판정
- `floor_area` — `auto_tier_func` 과금 등급 결정
- 그 외 시설 상세 입력은 **현재 판정 기여 0** (위 §2-2 사유)

---

## 7. 읽은 파일 (근거)

`services/diagnosis_runtime_step1.py`, `services/legal_runtime_fetch.py`, `services/rule_candidate_projection.py`, `services/legal_context.py`, `services/legal_rules.py`, `services/legal_engine_svc.py`, `services/diagnosis_integrated_svc.py`, `services/diagnosis_nexas_adapter.py`, tadmin `diagnosis-input-building.html`·`diagnosis-input-industry-paid1.html`·`diagnosis-input-construction.html`. DB: `runtime_metadata_resolution`(Supabase `vwlahtguyggrhvslabax`).

---

## 8. 보류/미진행 작업지시서 (참고, 미실행)

다음 두 작업지시서는 이번 세션에서 **실행하지 않음**. 산출물 0건(어느 레포에도 `docs/database/` 없음).

### 8-1. "45CM Database Architecture & Standards (2차)" — 보류("잘못 들어간 내용")
미생성: `docs/database/architecture/{SEPARATION_MODEL, ZERO_DOWNTIME_MODEL, DATA_MINIMIZATION_MODEL}.md`, `docs/database/standards/{VARIABLE_STANDARD, VIEW_STANDARD, REPLICATION_STANDARD}.md`, `docs/database/adr/{ADR-004, ADR-005, ADR-006}.md` (9개 전부 미생성).

### 8-2. "Phase 5 : Contract OS Discovery" — 미착수
요청 산출물(미생성):
- `docs/architecture/{CONTRACT_OS, CONTRACT_VERSION_MODEL, ENGINE_FEDERATION_MODEL}.md`
- `DATABASE_LAW` 제14조(Contract & Binding 원칙) 추가
- `docs/database/adr/{ADR-007-CONTRACT-FIRST-ARCHITECTURE, ADR-008-BINDING-AS-EDGE, ADR-009-FEDERATION-OF-ENGINES}.md`
- 미해결 선행조건: (a) 대상 레포 미확정(`docs/architecture/`는 `taieng`에 존재, `docs/database/`는 어느 레포에도 없음), (b) `DATABASE_LAW` 파일 위치 미확인(org 검색 0건), (c) ADR-001~003 위치 미확인(ADR-004~009 번호 전제).

> 두 지시서 모두 "탐구(Discovery) 단계 · 설계·리팩토링·분리 금지"로 명시됨. 진행 시 위 선행조건부터 확정 필요.

---

## 9. 다음 세션 추천 순서

1. (엔진/GPT) 룰 `condition_value` 구조화 — §3-(1). 이게 안 되면 입력 표준화 효과 없음.
2. (엔진/GPT) sector 스탬프 무력화·오파싱 수정 — §3-(2)(3).
3. (입력부/Claude) 3계층 ctx 키 정합 — electrical_capacity_kw·위험물 배열·industry_type·건설 토글·건물용도.
4. (의사결정) Phase 5 Contract OS Discovery 진행 여부 + 선행조건(8-2) 확정.
