# WO-INPUT-NORMALIZATION-EXISTENCE-001 — 입력 정규화 계층 존재 증명

**작성일:** 2026-06-29 | **성격:** 읽기 전용 전수 검색·직독. 새 코드/매핑 0.
**판정: A — 기존 입력 정규화가 존재한다(라이브 동작 중).** 단, 종착지가 facility_profiles가 아니라 임시 factories + 엔진이다.

> 결론은 A/B 둘 중 하나만 허용 → **A. 정규화는 이미 존재한다.** 새로 만들 필요 없음. "끊김"은 정규화 부재가 아니라 **정규화의 종착지가 facility_profiles로 향하지 않음**이다.

---

## 검색 결과 (지정 키워드 전수)
```
normalize / normalizer:
  ✔ services/input_normalizer.py            ← 입력 정규화 본체 (존재·라이브)
  ✔ services/condition_normalizer.py         (조건 정규화, 엔진측)
  ✔ engine/evidence_normalizer.py            (근거 정규화, 엔진측)
  ✔ docs/WORKORDER_STEP_A_NORMALIZER_WIRING.md  ← 배선 워크오더 (존재)
binding:  WO-INPUT-BINDING-ARCHITECTURE-001 (규격, 앞 WO에서 확인)
mapper / field_mapper:  ALIAS_MAP (input_normalizer 내), to_mapping_sector (constants.sectors)
contract:  DiagnoseStep1Body (schemas), facility profile 계약 (facility_profile_service)
staging:  WO-INPUT-STAGING-001/002 (문서)
profile_builder / profile_contract / diagnosis_mapper / input_mapper / profile_input / facility_profile_input:
  → 해당 명칭 파일 없음. 단 기능은 build_facility_profile(존재)·input_normalizer(존재)가 담당.
```

## 증거 1 — input_normalizer.py 는 정확히 "진단 입력 → 표준 필드명" 정규화다 (라이브)
```
services/input_normalizer.py  normalize_input(payload)
  ALIAS_MAP (진단 field_code → 정규 필드명):
    workers/worker/num_workers        → worker_count
    employees/employee                → employee_count
    floor_area/total_floor_area/area  → building_area
    electric_capacity/power_capacity  → electrical_capacity_kw
    contract_amount_eok/_won          → contract_amount
    gas_capacity                      → gas_capacity_kg
    floors/num_floors/FLOOR_COUNT     → floor_count
  + 타입 변환·빈값 None·단위 문자 제거·단위 환산(전력→kW, 금액→원, 거리→m)
  규칙: "별칭 통합·타입·빈값·단위 환산. 금지: 판단/추정/기본값 생성."
→ 앞 WO에서 "얇은 정규화가 필요하다"던 그 정규화(worker_count↔employee_count 등)는 이미 구현되어 있다.
```

## 증거 2 — 이 정규화는 이미 소비자 경로에 라이브 배선돼 있다
```
services/anonymous_factory_service.py (소비자 진단 경로, 라이브):
  run_anonymous_diagnosis(body)
    inp = normalize_consumer_inp(body)              ← normalize_input 호출 (정규화 실행)
      = _merge_body_input(body) → normalize_input({**base, sector})
    facility_ctx = _input_to_facility_context(sector_raw, inp)
    factory_id = create_temp_factory(supabase, body)  ← 정규화된 값으로 임시 factories row INSERT
       row = {employee_count, building_area, electrical_capacity_kw, gas_capacity_kg,
              construction_amount, ksic_code, site_type, construction_type, floor_count …}
    evaluate_single_factory(factory_id)             ← facility_applicability 평가
    ... fetch_compiler_candidates → step1 결과
    cleanup_temp_factory(factory_id)                ← 임시 factory 삭제
docs/WORKORDER_STEP_A_NORMALIZER_WIRING.md:
  "normalize_input을 소비자 진단 경로(legal_context 앞)에 연결" — 배선 완료 기록.
```

## 증거 3 — 그러나 종착지가 facility_profiles 가 아니다 (끊김의 정체)
```
정규화된 입력이 흘러가는 곳:
  진단 입력 → normalize_input → create_temp_factory(임시 factories row) → 엔진 평가 → 결과 → 임시 row 삭제
정규화된 입력이 facility_profiles 로 가는 경로:
  ✗ 없음. create_temp_factory는 factories에만 INSERT하고, build_facility_profile/facility_profiles를 호출하지 않는다.
  ✗ 임시 factory는 cleanup_temp_factory로 즉시 삭제됨 → 영구 입력표준(facility_profiles) 미적재.
```

---

## 최종 판정 — A (정규화 존재) + 끊김의 정확한 위치
```
A. 입력 정규화 계층은 이미 존재하고 라이브로 동작한다.
   - services/input_normalizer.py (ALIAS_MAP = 진단 field_code → 표준 필드명)
   - services/anonymous_factory_service.py 에서 소비자 경로에 배선됨(normalize_consumer_inp).
   → "최초 설계부터 미구현(B)"이 아니다. 정규화는 구현·배선·동작 중이다.

끊김의 정체(앞 WO들의 단절-1 재정의):
   정규화의 종착지가 facility_profiles 가 아니라 "임시 factories row(즉시 삭제)"이다.
   - 같은 정규화 결과가 build_facility_profile → facility_profiles 로는 흐르지 않는다.
   - 즉 부재한 것은 "정규화"가 아니라 "정규화된 입력을 facility_profiles 로 영구 적재하는 종착 배선"이다.

→ 복원 대상: 새 정규화 작성이 아니라, 이미 있는 normalize_input/normalize_consumer_inp의 출력을
   facility_profiles(build_facility_profile)로 향하게 하는 종착지 연결.
   (create_temp_factory가 factories에 넣는 그 정규화된 dict가, 영구 입력표준으로는 안 감)
```

## 참고 — 정규화 키와 build_facility_profile 기대 키의 관계 (사실만)
```
normalize_input 출력 키 = 엔진/factories 표준명(employee_count, building_area, electrical_capacity_kw, gas_capacity_kg, construction_amount, floor_count …)
build_facility_profile 기대 키 = factories 컬럼명(employee_count, building_area, electrical_capacity_kw …)
→ 두 키 체계는 이미 factories 컬럼명으로 수렴한다(create_temp_factory가 그 증거: 정규화 출력으로 factories row를 만든다).
→ 따라서 facility_profiles 적재도 "정규화 출력 dict를 build_facility_profile에 그대로 넘기는" 종착 연결로 성립한다(새 매핑 불요).
  (단 has_*는 normalize_input ALIAS_MAP 대상 아님 — boolean 통과. 이는 별도 사실.)
```

## Boundary 준수
```
읽기 전용. 코드/DB/INSERT/UPDATE/DELETE 0. 새 정규화/매핑/코드 0.
프로젝트 전체 검색 + 직독만으로 A/B 판정. → A(존재) 확정.
```

*WO-INPUT-NORMALIZATION-EXISTENCE-001 — 판정 A. input_normalizer.py(ALIAS_MAP)가 진단 field_code→표준명 정규화를 이미 수행하고, anonymous_factory_service가 소비자 경로에 라이브 배선. 끊김은 정규화 부재가 아니라 종착지가 facility_profiles 아닌 임시 factories(즉시삭제). 복원=정규화 출력을 facility_profiles로 보내는 종착 연결.*
