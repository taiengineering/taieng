# GPT 질의 — Phase 1 WO 설계 요청 (최종본)

**작성일**: 2026-06-17  
**용도**: 16차 세션 시작 전 GPT에게 전달  
**버전**: v2 (사장님 추가 지시 반영)

---

## 한 문장 요약

> Phase 1은 새로운 엔진을 만드는 작업이 아니라, factories의 110개 컬럼에서 소비자 입력을 손실 없이 FacilityProfile로 투영(Projection)하고 다시 복원 가능한지 검증하는 작업이다. 정확도 개선·법령 매핑·ApplicabilityCondition·Registry는 범위 밖이다.

---

## 배경

15차 세션 완료 기준:
- D-001~007 완료 (관찰 파이프라인)
- Appendix 수집 완료 (law_appendix 1건, appendix_condition 7건)
- Actor Resolution Overlay 완료 (118 패턴, 29,986건)
- Domain Filter 완료 \[OBSERVATION ASSET — 측정기, 엔진 아님\]
- Phase 0A Schema Freeze 사장님 승인 완료

**15차 핵심 발견:**
```
Track A 오염 원인 = law_sector_mapping 부재 아님
실제 원인 = facility_applicability가 sector를 전혀 참조하지 않고 실행됨

현재 factories 테이블: 110개 컬럼 평탄화
  미입력 컬럼 = null (또는 0)
  0값 → "N 이하" 조건에 자동 매칭
  "누가 280명인가"가 사라지고 숫자만 남음
  입력값/추론값/기본값 구분 불가
```

**15차 핵심 교훈:**
> 입력→표현→판정 사이에서 정보가 계속 사라진다.
> 지금은 더 똑똑한 엔진보다 정보를 잃어버리지 않는 표준 입력 객체를 먼저 만드는 순서가 맞다.

---

## Phase 0A 확정 내용 (이미 승인됨, 변경 금지)

```
TriValue<T> = { state: PRESENT|ABSENT|UNKNOWN, value: T|null }
TriList<T>  = { confirmed:[T], denied:[T], unknown_rest:bool }

원칙: 결측 = UNKNOWN. 0으로 채우지 않는다.

FacilityProfile v1.0 골격:
  profile_id, sector, ksic_code
  building:  { use_code, floor_area, floor_count }  ← TriValue
  workforce: { regular_workers, subcontract_workers }  ← TriValue
  processes/equipment/materials/activities  ← Phase 0B (미착수)
  metrics:   { construction_amount, electrical_kw, gas_capacity }  ← TriValue
  provenance: { 입력값/확장값/기본값 }  ← 필수

ACTOR namespace: 10개 코드 확정
METRIC namespace: EMPLOYEE_COUNT, FLOOR_AREA, CONSTRUCTION_AMT, ELECTRICAL_KW
BLDG namespace: USE_CODE, FLOOR_COUNT
```

---

## 추가 제약 (절대 원칙)

```
FacilityProfile은 factories를 대체하지 않는다.

Phase 1 동안 factories는 Source of Record이다.

FacilityProfile은 Projection Layer이다.

삭제·이관·정규화 제안 금지.
```

factories 110개 컬럼은 Phase 1 동안 건드리지 않는다.

---

## Phase 1 산출물 정의

**반드시 생성되어야 하는 것:**

1. FacilityProfile 스키마 v1.0 (DB 구조)
2. factories → FacilityProfile 변환 규칙 (컬럼 매핑)
3. FacilityProfile 저장 구조
4. FacilityProfile 복원 구조 (재현 가능성 검증)
5. Provenance 구조 (입력값/확장값/기본값 구분 방법)

**생성 금지:**

1. ApplicabilityCondition
2. CheckResult
3. Match Engine
4. Registry 구현
5. 법령 매핑 로직

---

## 현재 factories 테이블 실측 (참고용)

FacilityProfile과 연관된 주요 컬럼:

```
인원:
  employee_count (integer, nullable)
  contractor_count (integer, nullable)
  subcontractor_worker_count (integer, nullable)
  total_worker_count_calc (integer, nullable)

건물:
  building_area (numeric, nullable)
  floor_count (integer, nullable)
  underground_floor_count (integer, nullable)
  building_use_code (text, nullable)
  main_purpose_code (text, nullable)

설비:
  electrical_capacity_kw (numeric, nullable)
  gas_capacity_m3 (numeric, nullable)
  gas_capacity_kg (numeric, nullable)
  boiler_capacity_kw (numeric, nullable)

공사:
  construction_amount (numeric, nullable)

업종:
  ksic_code (text, nullable)
  sector (varchar, nullable)
  site_type (text, nullable)

Boolean 플래그 (미입력 시 null):
  has_safety_manager, has_high_pressure_gas, has_chemical_substance,
  has_boiler, has_tower_crane, has_confined_space, has_asbestos_demo,
  has_blasting, has_diving, hazardous_material
```

---

## 질문 1. FacilityProfile 필수/선택 필드 구분

Phase 1 구현 범위를 정해주세요.

Phase 0A 골격 중:
- Phase 1 필수 구현 항목
- Phase 2 이후 미뤄도 되는 항목
- factories 컬럼 → FacilityProfile 필드 매핑 (1:1 또는 변환 규칙)

---

## 질문 2. 저장 전략

후보:
- A: JSON 단일 객체 (factories에 `facility_profile` 컬럼 추가)
- B: `facility_profiles` 별도 테이블 (factories와 1:1)
- C: 둘 다 (JSON snapshot + 정규화된 별도 테이블)

판정 기준:
- 소비자 입력 재현 가능성 (핵심)
- 디버깅 용이성
- 기존 factories 테이블 영향 최소화
- 향후 ApplicabilityCondition 연동 용이성

**참고**: 사장님 의견은 C안 유력. JSON Snapshot이 있어야 입력→생성→저장→재로드 전 과정의 손실 여부를 나중에 감사할 수 있기 때문.

---

## 질문 3. TriValue 구현 범위

모든 nullable numeric 필드에 TriValue를 적용할지, Phase 1에서는 핵심 필드만 적용할지 결정해주세요.

특히:
- null과 UNKNOWN을 DB 레벨에서 처리할지 애플리케이션 레벨에서 처리할지
- boolean 플래그 (has_boiler 등)에 TriValue를 적용하는 방법

---

## 질문 4. Provenance 구현 방법

입력값/확장값/기본값 3가지를 어떻게 추적할지 구체적인 구현 방법을 제안해주세요.

예:
- 사용자가 `employee_count=280` 직접 입력 → 입력값
- KSIC C28에서 "금속 가공" 추론 → 확장값
- sector 미입력 시 INDUSTRIAL 기본 적용 → 기본값

나중에 이 3가지를 구분할 수 있어야 합니다.

---

## 질문 5. Phase 1 성공 기준

Claude가 구현 후 검증 가능한 정량 기준으로 작성해주세요.

아래 4개 테스트 케이스를 기준으로 설명해주세요:

```
CASE-01: 화성 제2공장 (INDUSTRIAL, C28, 280명)
CASE-02: 빈 사업장 (모든 값 null)
CASE-03: 건설현장 (공사금액 49억)
CASE-04: 건설현장 (공사금액 50억)
```

각 케이스에서:
- FacilityProfile 생성 결과 (어떤 필드가 PRESENT/ABSENT/UNKNOWN인가)
- 저장 → 재로드 후 원본과 동일한가
- UNKNOWN 필드가 0 또는 false로 변질되는 경우가 0건인가

---

## 범위 고정 (재확인)

```
Phase 1 = 입력 보존 + 입력 재현 + 입력 추적

금지:
  Check Engine 수정
  Registry 구현
  ApplicabilityCondition 구현
  정확도 개선 작업
  Rule 개선 작업
  factories 기존 컬럼 삭제/변경
  "factories 폐기 가능" 류의 제안
```

GPT는 구현 코드가 아니라 WO 설계 문서 수준으로 답변해주세요.

---

## 참고 문서

- Phase 0A 확정: `docs/2026-06-16_WO_V4_PHASE0_001.md`
- 15차 Closing Report: `docs/2026-06-16_WO_015_CLOSING_REPORT.md`
- 기획서: `docs/2026-06-11_LEGAL_ENGINE_V4_LAYER_REDESIGN.md` (v2.1)
