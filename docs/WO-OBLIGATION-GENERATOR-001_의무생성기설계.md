# WO-OBLIGATION-GENERATOR-001
# cmc 기반 obligation_instance 생성기 설계

**작성일:** 2026-06-24 | **상태:** 완료 (설계 전용, 읽기 전용 조사 기반)
**선행:** WO-OBLIGATION-GENERATION-ARCHITECTURE-001
**금지:** 기존 Check Engine / facility_applicability / executable_draft 수정 / 새 매핑 생성
**목적:** cmc 452 CONFIRMED를 원재료로 factory 입력값에 맞는 obligation_instance 생성.

> 체크엔진 이전 단계의 새 엔진. cmc를 독립 의무생성기로 먼저 세운다.

---

## 핵심 흐름

```
factory 입력 (facility_profiles)
      ↓
sector 결정 (sector + ksic_code)
      ↓
[1] UNIVERSAL 후보  (condition_type='NONE', sector 매칭)
[2] EXISTS 후보     (input_fields의 has_* 매칭)
[3] THRESHOLD 후보  (numeric 비교 — DIRECT만, APPENDIX 보류)
      ↓
obligation_instance 생성
      ↓
Check Engine / 6W 레이어로 전달
```

---

## 1. obligation_instance 테이블 구조

```sql
-- 설계안 (이번 WO는 설계만, 생성 안 함)
CREATE TABLE obligation_instance (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  factory_id          UUID NOT NULL,
  generation_batch    TEXT NOT NULL,        -- 생성 회차 추적
  -- 근거
  source_cmc_id       UUID NOT NULL,        -- 어느 cmc 규칙에서
  source_clause_id    UUID NOT NULL,        -- semantic_clause_id
  -- Trigger 정보
  trigger_type        TEXT NOT NULL,        -- WORK_ACT/EQUIPMENT_ACT/MATERIAL_ACT/FACILITY_ACT/NONE
  trigger_l2          TEXT,                 -- WELDING/BOILER/UNIVERSAL
  detail              TEXT,                 -- RECORD/PPE/INSPECT/VENTILATION
  -- 발동 근거
  fired_by            TEXT,                 -- 'has_welding=true' / 'sector=INDUSTRIAL'
  input_field         TEXT,                 -- NULL이면 UNIVERSAL
  reason              TEXT NOT NULL,        -- "용접작업 있음 → 국소배기장치 설치"
  -- 메타
  applicable_sectors  TEXT[] NOT NULL,
  confidence          NUMERIC NOT NULL,
  status              TEXT NOT NULL,        -- ACTIVE/MISSING_DATA/AMBIGUOUS/HELD
  generated_at        TIMESTAMPTZ DEFAULT now(),
  UNIQUE(factory_id, source_cmc_id)         -- 같은 규칙 중복 방지
);
```

```
설계 원칙:
  - factory_id별 생성 (재실행 시 batch로 구분)
  - source_cmc_id로 규칙 역추적 (감사 가능)
  - status로 실행 가능/보류 구분
  - 기존 cmc/facility_applicability와 물리적 분리 (독립 테이블)
```

---

## 2. cmc → obligation_instance 변환 규칙

| cmc 필드 | → obligation_instance | 변환 |
|---|---|---|
| id | source_cmc_id | 직접 |
| semantic_clause_id | source_clause_id | 직접 |
| condition_type | trigger_type | 직접 (WORK_ACT 등) |
| condition_code split[1] | trigger_l2 | WELDING/BOILER |
| condition_code split[2] | detail | RECORD/PPE |
| input_field | input_field, fired_by | has_welding |
| applicable_sectors | applicable_sectors | 직접 |
| confidence | confidence | 직접 |
| (생성 시점) | reason | 조합 생성 |
| (평가 결과) | status | ACTIVE/HELD |

```
reason 생성 규칙:
  EXISTS:    "{input_field 한글명} 있음 → {조문 요지}"
  UNIVERSAL: "{sector} 사업장 공통 의무 → {조문 요지}"
  THRESHOLD: "{필드}={값}이 기준 충족 → {조문 요지}"
```

---

## 3. factory 입력값 평가 순서

```
입력 소스: facility_profiles (factory_id 기준)
  sector, ksic_code
  *_state / *_value / *_provenance (regular_workers, floor_area, ...)
  input_fields (JSON — has_* boolean)

평가 순서:
  1. SCOPE 확정
     - facility_profiles.sector 읽기
     - sector NULL이면 ksic_code로 추론
     - 범위밖(주택/파견 등)이면 생성 중단

  2. UNIVERSAL 평가
     - cmc WHERE condition_type='NONE'
       AND sector ∈ applicable_sectors
     - 입력 무관, sector만으로 발동

  3. EXISTS 평가
     - facility_profiles.input_fields JSON 파싱
     - has_*=true인 필드 추출
     - cmc WHERE input_field ∈ {has_*=true}
       AND review_status='CONFIRMED'

  4. THRESHOLD 평가 (DIRECT만)
     - *_state='PROVIDED'인 numeric 읽기
     - DIRECT_THRESHOLD 조문과 수치 비교
     - APPENDIX는 보류(아래 7번)

  5. 통합 → obligation_instance INSERT
```

---

## 4. review_status 사용 정책

```
실행 정책 (CODE-AUDIT/REALITY-CHECK 반영):

  CONFIRMED  → 실행 O (452건)
  HARVESTED  → 실행 X (310건, 미검증 — UNIVERSAL 포함)
  REJECTED   → 실행 X (35건)
  PENDING    → 실행 X (0건)

생성기 WHERE 절:
  WHERE review_status = 'CONFIRMED'   -- 이것만

→ HARVESTED 310(UNIVERSAL)은 아직 obligation 생성 안 함.
→ UNIVERSAL을 의무로 쓰려면 먼저 REVIEW → CONFIRMED 승격 필요.
→ 현재 생성 가능한 것은 EXISTS 계열 CONFIRMED 452뿐.
```

**중요:** 현재 CONFIRMED 452는 거의 전부 EXISTS(WORK/EQUIPMENT/MATERIAL/FACILITY). UNIVERSAL은 HARVESTED라 baseline 생성 안 됨. 완전한 진단에는 UNIVERSAL 승격이 선행되어야 함.

---

## 5. UNIVERSAL 처리

```
조회:
  cmc WHERE condition_type='NONE'
    AND review_status='CONFIRMED'        -- 현재 0건 (전부 HARVESTED)
    AND {factory.sector} = ANY(applicable_sectors)

생성:
  input_field=NULL
  fired_by='sector={sector}'
  reason='{sector} 사업장 공통 의무'

현재 상태:
  UNIVERSAL CONFIRMED = 0 → 생성 0건.
  → UNIVERSAL REVIEW WO 선행 시 baseline 226/223/289 생성 가능.
```

---

## 6. EXISTS 처리

```
입력 추출:
  facility_profiles.input_fields JSON에서
  has_*=true 키 목록 추출
  예: {has_welding:true, has_crane:true} → [has_welding, has_crane]

조회:
  cmc WHERE condition_type IN
    ('WORK_ACT','EQUIPMENT_ACT','MATERIAL_ACT','FACILITY_ACT')
    AND review_status='CONFIRMED'
    AND input_field = ANY({has_*=true 목록})
    AND input_value = 'true'
    AND {factory.sector} = ANY(applicable_sectors)

생성:
  fired_by='{input_field}=true'
  reason='{input_field 한글명} 있음 → {조문 요지}'

예 (has_welding=true, INDUSTRIAL):
  → WORK_ACT:WELDING 조문 18개 → 18 obligation_instance
```

---

## 7. THRESHOLD 보류 처리

```
DIRECT_THRESHOLD (본조 직접 수치):
  facility_profiles.floor_area_value 등과 비교
  현재 cmc에 DIRECT_THRESHOLD CONFIRMED 거의 없음(수확 2건).
  → 생성 가능하나 극소량.

APPENDIX_THRESHOLD (별표 위임):
  appendix_condition 7건 병목.
  status='HELD'로 표시, 생성 보류.
  reason='별표 기준 미입력 — 판정 보류'

처리:
  THRESHOLD 충족 → status='ACTIVE'
  THRESHOLD 미입력 → status='MISSING_DATA' (생성하되 보류 표시)
  APPENDIX → status='HELD'

→ 보류도 obligation_instance로 생성하되 status로 구분.
→ "데이터 넣으면 켜질 의무"를 사용자에게 보여줄 수 있음.
```

---

## 8. Check Engine 인계 방식

```
obligation_instance → Check Engine 전달:

  방식 A (권장): obligation_instance 테이블을 Check Engine이 조회
    - status='ACTIVE'인 것만 인계
    - 기존 Check Engine 수정 없이 새 입력 소스로 추가

  방식 B: 6W 레이어 직접 호출
    - obligation_instance → 6W 분해 → 체크항목

현재 실제 Check Engine (CODE-AUDIT):
  facility_applicability를 읽음.
  → obligation_instance는 그와 별개 경로.
  → 충돌 없음 (독립 테이블).

인계 규격:
  Check Engine은 obligation_instance를 받아
  status='ACTIVE'만 체크항목/일정/담당자로 전개.
  HELD/MISSING_DATA는 "추가 입력 필요" 안내.
```

---

## 생성기 의사코드 (설계)

```python
def generate_obligations(factory_id):
    profile = get_facility_profile(factory_id)

    # 1. SCOPE
    sector = profile.sector or infer_sector(profile.ksic_code)
    if sector in OUT_OF_SCOPE_SECTORS:
        return []

    instances = []

    # 2. UNIVERSAL (현재 CONFIRMED 0건)
    universal = query_cmc(
        condition_type='NONE',
        review_status='CONFIRMED',
        sector_in=sector)
    instances += [to_instance(c, fired_by=f'sector={sector}') for c in universal]

    # 3. EXISTS
    active_fields = [k for k,v in profile.input_fields.items()
                     if k.startswith('has_') and v is True]
    exists = query_cmc(
        condition_type_in=['WORK_ACT','EQUIPMENT_ACT','MATERIAL_ACT','FACILITY_ACT'],
        review_status='CONFIRMED',
        input_field_in=active_fields,
        sector_in=sector)
    instances += [to_instance(c, fired_by=f'{c.input_field}=true') for c in exists]

    # 4. THRESHOLD (DIRECT만, APPENDIX는 HELD)
    # ... numeric 비교, 미입력은 MISSING_DATA

    # 5. INSERT obligation_instance
    return instances
```

---

## 성공 기준 답변

```
factory_id 하나를 넣으면 cmc CONFIRMED 452 중
적용되는 obligation_instance 목록을 생성할 수 있는 설계가 나왔는가?

✅ 나왔다.

흐름:
  facility_profiles(factory_id) 읽기
  → sector 확정
  → UNIVERSAL(NONE) + EXISTS(has_*) + THRESHOLD(numeric) 조회
  → review_status='CONFIRMED'만
  → obligation_instance 생성

예 (제조업, has_welding+has_crane+has_chemical):
  UNIVERSAL: 0 (CONFIRMED 0, HARVESTED 상태)
  EXISTS: welding 18 + crane 25 + chemical 32 = 75
  → 75 obligation_instance (status=ACTIVE)
```

---

## 핵심 발견

### 발견 1: 입력 소스는 facility_profiles다

```
facility_profiles에 모든 입력이 정규화되어 있음:
  sector, ksic_code (SCOPE/UNIVERSAL용)
  *_state/*_value (THRESHOLD용, PROVIDED 여부 추적)
  input_fields JSON (EXISTS용, has_*)

→ provenance까지 추적 (입력/추론/기본값 구분).
→ 생성기는 이 한 테이블만 읽으면 됨.
```

### 발견 2: 현재 즉시 생성 가능한 것은 EXISTS뿐

```
CONFIRMED 452 = 거의 전부 EXISTS.
UNIVERSAL 310 = HARVESTED (실행 제외).

→ 지금 생성기 돌리면 EXISTS 의무만 나옴.
→ baseline(UNIVERSAL) 없는 불완전 진단.
→ UNIVERSAL REVIEW 승격이 다음 우선순위.
```

### 발견 3: 독립 테이블로 충돌 회피

```
obligation_instance는 facility_applicability와 별개.
→ 기존 Check Engine(GPT Compiler) 안 건드림.
→ cmc → obligation_instance → (선택적) Check Engine.
→ 두 시스템 평행 유지하며 cmc 경로 독립 가동.
```

### 발견 4: 보류도 생성한다 (MISSING_DATA/HELD)

```
THRESHOLD 미입력/APPENDIX 병목도 obligation_instance로 생성.
status로 ACTIVE/MISSING_DATA/HELD 구분.
→ "데이터 넣으면 켜질 의무"를 사용자에게 노출.
→ 진단 완성도를 사용자가 인지 가능.
```

---

## 다음 단계 권고

```
WO-OBLIGATION-GENERATOR-001 (현재) — 설계 완료.
      ↓
구현 선택:
  1. obligation_instance 테이블 생성 (DDL) + 생성 함수 구현
     - 단, UNIVERSAL CONFIRMED 0건이라 EXISTS만 나옴
  2. 선행: UNIVERSAL 310 REVIEW → CONFIRMED 승격
     - 그래야 baseline 포함 완전 생성
  3. facility_profiles.input_fields JSON 실제 구조 검증
     - has_* 키가 실제로 어떻게 저장되는지 확인

권장 순서:
  3(입력 구조 확인) → 2(UNIVERSAL 승격) → 1(생성기 구현)
```

---

*WO-OBLIGATION-GENERATOR-001 완료. 설계 전용. INSERT/DDL 없음.*
*입력=facility_profiles. CONFIRMED만 실행. EXISTS 즉시 가능, UNIVERSAL은 승격 필요.*
*obligation_instance 독립 테이블 → Check Engine 충돌 없음. 보류도 status로 생성.*
