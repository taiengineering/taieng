# WO-INPUT-MODEL-AUDIT-001
# 입력모델 정규화 감사 보고서

**작성일:** 2026-06-23 | **상태:** 완료
**근거:** WO-CONDITION-AUDIT-001 FLAG-INPUT / FLAG-SECTOR 발견 사항

---

## 감사 배경

AUDIT-001에서 `has_high_pressure_gas` 하나의 필드가 실제로는 3개 이상의 다른 물리 개념을 대표하고 있음이 드러났다.
하나의 has_* 필드는 하나의 현실 개념만 대표해야 한다는 입력모델 설계 원칙에 위배된다.

---

## 현재 입력모델 필드 목록 (factories 테이블)

```
has_asbestos_demo
has_blasting
has_boiler
has_chemical_substance
has_confined_space
has_diving
has_high_pressure_gas   ← 감사 대상
has_safety_manager
has_tower_crane
```

총 9개. `has_safety_manager`는 THRESHOLD 처리 예정으로 별도.

---

## 감사 대상 1: has_high_pressure_gas

### 현재 매핑된 5건 조문 분석

| condition_code | article_no | 조문 핵심 | 실제 물리 개념 |
|---|---|---|---|
| EQUIPMENT_ACT:PRESSURE_VESSEL:COVER:84a5 | 87 | 압력용기·공기압축기 회전부 덮개 | **압력용기 보유** |
| EQUIPMENT_ACT:PRESSURE_VESSEL:MARK:5d06 | 120 | 압력용기 최고사용압력 각인 표시 | **압력용기 보유** |
| WORK_ACT:HIGH_PRESSURE:PILE_DRIVER:66e3 | 217 | 압축공기 동력 항타기·항발기 사용 시 준수 | **항타기 보유** |
| FACILITY_ACT:HIGH_PRESSURE:COMPRESSOR_TEMP:3dc7 | 528 | 기압조절실 공기압축기 온도 이상 시 자동경보 | **기압조절실(잠함·고압작업)** |
| WORK_ACT:HIGH_PRESSURE:CAISSON_LOWER:5acf | 540 | 잠함 침하 시 고압작업자 대피 | **잠함(caisson) 사용** |

### 결론: has_high_pressure_gas는 3개 개념의 혼합

```
has_high_pressure_gas
  ├── 압력용기 보유      → has_pressure_vessel (신규 후보)
  ├── 항타기 보유        → has_pile_driver (신규 후보)
  └── 잠함·기압조절실    → has_caisson (신규 후보) 또는 has_high_pressure_work
```

### 현재 사업장 데이터 현황

```
전체 factories: 5,812개
has_high_pressure_gas = true: 19개 (0.33%)
  - INDUSTRIAL: 8개
  - CONSTRUCTION: 7개
  - BUILDING: 3개
  - NULL/기타: 1개

has_high_pressure_gas AND has_diving 동시: 5개
  - 전부 복합위험 테스트/목업 데이터
```

**해석:** 실사용자가 `has_high_pressure_gas`를 입력할 때 압력용기인지 항타기인지 잠함인지 구분 없이 체크함.
엔진이 5건을 전부 발동시키면 항타기 없는 사업장에도 항타기 조문이 붙는 과매핑 발생.

---

## 감사 대상 2: has_chemical_substance (수량 조건)

### 현재 매핑된 문제 2건

| condition_code | article_no | 조문 핵심 | 문제 |
|---|---|---|---|
| MATERIAL_ACT:HAZMAT:ALARM:dd47 | 434 | **1일 100리터 이상** 취급 시 경보설비 설치 | condition_text에 수량 조건 명시 — has_chemical_substance=true만으로는 과매핑 |
| MATERIAL_ACT:HAZMAT:SPILL_KIT:a88d | 434 | **제1항(100리터 이상) 사업장**에서 누출 시 약제 구비 | 동일 — 434조 제1항 전제 |

**해석:** `has_chemical_substance=true`인 모든 사업장에 100리터 기준 의무가 발동됨.
실제로는 소량 취급 사업장(100리터 미만)에는 해당 안 됨. **현재는 과매핑 상태.**

---

## 감사 대상 3: has_diving (구조적 이슈 없음 — 확인)

has_diving 14건 조문을 재검토한 결과:
- 14건 전원 "잠수작업자", "잠수작업", "스쿠버 잠수작업", "표면공급식 잠수작업" 명시
- 잠함(caisson)과 조문이 완전히 분리되어 있음 (잠함 조문은 530~540조대, 잠수 조문은 527~557조대)
- **has_diving 자체는 단일 개념 대표 — 정규화 이슈 없음**

---

## 산출물 A: 유지 확정 (현행 has_* 유지)

| 필드 | 판정 | 근거 |
|---|---|---|
| has_confined_space | **유지** | 밀폐공간 단일 개념. 16건 전원 조문 직결. |
| has_tower_crane | **유지** | 타워크레인 단일 개념. 5건 전원 조문 직결. |
| has_boiler | **유지** | 보일러 단일 개념. 4건 전원 조문 직결. |
| has_diving | **유지** | 잠수작업 단일 개념. 14건 전원 조문 직결. |
| has_blasting | **유지** | 발파 단일 개념. 2건 전원 조문 직결. |
| has_asbestos_demo | **유지** | 석면해체·제거 단일 개념. 7건 전원 조문 직결. |
| has_chemical_substance | **유지 (수량조건 분리 전제)** | 관리대상 유해물질 취급 단일 개념. 단, 100리터 조건 2건은 THRESHOLD 전환 필요. |
| has_safety_manager | **보류** | THRESHOLD(employee_count) 처리 예정. 별도 WO. |

---

## 산출물 B: 신규 필드 후보

### B-1. has_pressure_vessel (권고: 추가)

**근거:**
- 87조: 압력용기 회전부 덮개
- 120조: 압력용기 각인 표시

**정의:** 압력용기(pressure vessel) 또는 공기압축기를 사업장 내에 보유·운용하는 경우.
**적용 sector:** INDUSTRIAL, CONSTRUCTION
**현재 has_high_pressure_gas와 관계:** has_high_pressure_gas ⊃ has_pressure_vessel. 분리 시 has_high_pressure_gas는 나머지(잠함·항타기) 담당.

**우선순위:** **높음** — 압력용기는 INDUSTRIAL 사업장에 가장 일반적. 현재 19개 사업장 중 상당수가 이 개념으로 체크했을 가능성.

---

### B-2. has_pile_driver (권고: 검토 후 추가)

**근거:**
- 217조: 압축공기 동력 항타기·항발기 사용 시 준수사항

**정의:** 압축공기 동력 항타기(pile driver) 또는 항발기를 사용하는 공사.
**적용 sector:** CONSTRUCTION 전용
**현재 has_high_pressure_gas와 관계:** 항타기가 압축공기(고압)를 사용하지만, 의무의 주체는 "고압가스 보유"가 아니라 "항타기 사용".

**우선순위:** **중간** — CONSTRUCTION 특화 필드. 현재 매핑 1건뿐이나 미적재 조문 더 있을 수 있음.

---

### B-3. has_caisson / has_high_pressure_work (권고: 검토)

**근거:**
- 528조: 기압조절실 공기압축기 온도 이상 경보
- 540조: 잠함 침하 시 고압작업자 대피
- COMPOUND 후보 3건(532·535조): 고압작업자 또는 잠수작업자 가압·감압

**정의:** 잠함(caisson) 또는 기압조절실을 사용한 고압 환경 작업.
**적용 sector:** CONSTRUCTION 전용
**현재 has_high_pressure_gas, has_diving과 관계:**
```
잠함 고압작업 = has_caisson (또는 has_high_pressure_work)
기압조절실 + 잠수 = has_caisson AND has_diving → COMPOUND
```

**우선순위:** **중간** — 건설 현장에서 잠함공법 사용 시 전용 필드로 분리하면 COMPOUND 설계가 명확해짐.

---

## 산출물 C: THRESHOLD 전환 대상

| condition_code | 현재 input_field | THRESHOLD 조건 | 전환 방식 |
|---|---|---|---|
| MATERIAL_ACT:HAZMAT:ALARM:dd47 | has_chemical_substance = true | + chemical_daily_volume_liter ≥ 100 | input_field_2 추가 또는 별도 THRESHOLD 매핑 |
| MATERIAL_ACT:HAZMAT:SPILL_KIT:a88d | has_chemical_substance = true | + chemical_daily_volume_liter ≥ 100 (434조 1항 연계) | 동일 |

**설계 방향:**
```sql
-- 현행 (과매핑)
input_field = 'has_chemical_substance', input_value = 'true'

-- 개선안 A: compound 조건 추가
input_field   = 'has_chemical_substance', input_value = 'true'
input_field_2 = 'chemical_daily_volume_liter', input_operator_2 = '>=', input_value_2 = '100'
compound_operator = 'AND'

-- 개선안 B: factories에 chemical_daily_volume_liter 컬럼 추가 후 THRESHOLD 처리
```

**선행 조건:** `factories` 테이블에 `chemical_daily_volume_liter` 컬럼 존재 여부 확인 필요.

**우선순위:** **높음** — 현재 과매핑 상태. WO-CONDITION-SEED-002(THRESHOLD 설계) 시 반드시 반영.

---

## 산출물 D: COMPOUND 전환 대상

| 관련 semantic_clause | 조번호 | 현재 상태 | 전환 후 설계 |
|---|---|---|---|
| 80135fef | 532 | 미적재(PENDING_REVIEW) | has_high_pressure_work = true OR has_diving = true |
| 3cba36fb | 535 | 미적재(PENDING_REVIEW) | 동일 |
| 6edd3dd8 | 535 | 미적재(PENDING_REVIEW) | 동일 |
| FACILITY_ACT:HIGH_PRESSURE:COMPRESSOR_TEMP:3dc7 (528조) | 528 | **현재 has_high_pressure_gas로 적재됨** | has_caisson = true (또는 has_high_pressure_work) |
| WORK_ACT:HIGH_PRESSURE:CAISSON_LOWER:5acf (540조) | 540 | **현재 has_high_pressure_gas로 적재됨** | has_caisson = true |

---

## 핵심 판단: has_high_pressure_gas 처리 방향

### 옵션 1: 필드 분리 (권고)

```
has_high_pressure_gas  →  has_pressure_vessel (압력용기·압축기)
                       →  has_pile_driver (항타기·항발기)
                       →  has_caisson (잠함·기압조절실)
```

- factories 테이블에 3개 컬럼 신규 추가
- condition_mapping 재매핑 (5건 → 각 필드로 이동)
- 기존 has_high_pressure_gas는 deprecated 또는 삭제

### 옵션 2: has_high_pressure_gas 유지 + null_condition_class 활용

```
has_high_pressure_gas = true
  + sub_type = 'PRESSURE_VESSEL' / 'PILE_DRIVER' / 'CAISSON'
```

- factories 테이블에 has_high_pressure_gas_type TEXT 컬럼 추가
- condition_mapping에 required_equipment_type 활용
- 기존 API 변경 최소화

### 옵션 3: 현행 유지 + 과매핑 수용

- 19개 사업장 전용으로 5건 전부 발동
- 실제 오탐 발생: 압력용기 없는데 항타기 조문 붙음
- **권고하지 않음**

---

## 최종 권고

### 즉시 조치 (다음 WO 앞단)

1. **dd47, a88d 2건 input 조건 수정** — `chemical_daily_volume_liter` 컬럼 여부 확인 후:
   - 컬럼 없으면: condition_mapping에서 일시 PENDING으로 review_status 변경
   - 컬럼 있으면: compound 조건 추가

2. **528조(3dc7), 540조(5acf) 2건 review_status 검토** — 현재 has_high_pressure_gas로 CONFIRMED 적재된 상태. 잠함 전용 조문이므로 has_caisson 분리 전까지 PENDING_REVIEW로 강등 검토.

### WO-CONDITION-SEED-002 전 선행 확정 사항

| 항목 | 결정 필요 |
|---|---|
| has_pressure_vessel 신규 추가 여부 | 사업 판단 |
| has_pile_driver 신규 추가 여부 | 사업 판단 |
| has_caisson 신규 추가 여부 | 사업 판단 |
| chemical_daily_volume_liter 컬럼 추가 여부 | 기술 결정 |
| 기존 has_high_pressure_gas 처리 방향 (분리/유지) | 최종 결정 필요 |

---

## 다음 단계

```
INPUT-MODEL-AUDIT-001 (현재)
      ↓
입력필드 분리 결정 (has_high_pressure_gas → 3개 또는 유지)
      ↓
WO-CONDITION-SEED-002 (THRESHOLD 설계)
      ↓
WO-CONDITION-COMPOUND-001 (COMPOUND 3건)
      ↓
VCF-02 원인 검증
```

---

*WO-INPUT-MODEL-AUDIT-001 완료. 핵심 이슈: has_high_pressure_gas 개념 과적재 + 화학물질 수량 조건 과매핑.*
