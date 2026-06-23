# WO-INPUT-CODE-ARCHITECTURE-001
# 입력 코드 체계 확정

**작성일:** 2026-06-23 | **상태:** 확정
**선행:** WO-STAGE-OBJECTIVE-001 / WO-LAW-CODE-ARCHITECTURE-001
**STAGE-OBJECTIVE 검증:** Q1(입력 분석) ✅ / Q2(코드 체계 발견) ✅ / Q3(매핑 생성 아님) ✅ / Q4(원칙 준수) ✅
**금지:** 법령 매핑, 패턴 매칭, 엔진 수정, VCF 실행

---

## 핵심 원칙

```
입력값은 수집 대상이 아니라 코드화 대상이다.

입력값 원천 → 입력코드 → 섹션 → 사용/미사용/고아 상태
```

---

## 산출물 A: INPUT_SECTION_POLICY

### 섹션 4종 확정

| 섹션 | 의미 | KSIC 대응 |
|---|---|---|
| **INDUSTRIAL** | 산업 (제조·화학·물류·에너지) | B 광업 / C 제조업 / D 전기가스 / E 수도하수폐기물 / H 운수창고 |
| **CONSTRUCTION** | 건설 (건축·토목 공사) | F 건설업(41~42) |
| **BUILDING** | 건물 (완공 후 유지관리·운영) | G 도소매 / I 숙박음식 / J 정보통신 / K 금융 / L 부동산 / M 전문서비스 / N 사업시설관리 / P 교육 / Q 보건복지 / R 예술스포츠 / S 협회단체 |
| **UNUSED** | 서비스 범위 밖 (의도적 미사용) | A 농림어업 / O 공공행정 / T 가구내고용 / U 국제기관 |

### UNUSED vs ORPHAN 구분 (핵심)

```
UNUSED = 섹션이다.
  - 서비스에서 의도적으로 사용하지 않는 입력
  - 향후 검토 대상도 아님
  - 예: A 농림어업, O 공공행정 KSIC
  - status = 'UNUSED'

ORPHAN = 상태다. 섹션이 아니다.
  - 분류 실패 / 코드 원천 불명 / 서비스 적용 여부 미확정
  - section = NULL 또는 후보 섹션
  - status = 'ORPHAN'
  - 예: lv1_code = NULL인 265개 공정
```

**둘은 절대 혼동하지 않는다.**
UNUSED는 "안 쓰기로 결정한 것", ORPHAN은 "아직 결정 못 한 것".

---

## 산출물 B: INPUT_CODE_TYPE_POLICY

### 입력 코드 타입 9종 확정

| code_type | 원천 | 설명 | 현재 DB 규모 |
|---|---|---|---|
| **KSIC_CODE** | ksic_process_map | 한국표준산업분류 (lv1~lv4) | 501개 세분류 (lv4) |
| **CONSTRUCTION_STANDARD_CODE** | (미존재 — 추가 필요) | 건설표준코드(공종) | F 건설업 16개 lv4 + 223 공정 |
| **PROCESS_CODE** | ksic_process_map.process_id | 공정/작업 코드 | 3,378개 process_id |
| **EQUIPMENT_CODE** | equipment_assets | 설비 종류 코드 | 40종 (정수 36 + 의미 4) |
| **FACILITY_CODE** | (시설 종류) | 건물 시설 | 보일러/승강기/전기/소방/냉동 |
| **MATERIAL_CODE** | (위험물 종류) | 취급 물질 | 화학물질/화약류/석면 등 |
| **HAZARD_CODE** | factories.has_* | 유해인자 boolean | has_confined_space 등 |
| **NUMERIC_FIELD** | factories 수치컬럼 | 수치 입력 | employee_count, building_area 등 8개 |
| **BOOLEAN_FIELD** | factories.has_* | 보유여부 boolean | has_* 9개 |

**주의:** HAZARD_CODE와 BOOLEAN_FIELD는 현재 DB에서 동일한 has_* 컬럼을 공유.
- HAZARD_CODE = 유해인자 의미 강조 (has_confined_space, has_blasting)
- BOOLEAN_FIELD = 단순 보유여부 (has_tower_crane, has_boiler)
- 코드화 시 의미 기준으로 분리.

---

## 산출물 C: UNUSED vs ORPHAN 정의

### UNUSED 분류 기준

```
status = 'UNUSED' 조건:
  - KSIC 대분류 A(농림어업), O(공공행정), T(가구내고용), U(국제기관)
  - executor가 행정기관인 법령에만 연결되는 입력
  - 산업안전보건법 적용 제외 업종
```

| UNUSED 대상 | KSIC | lv4 코드 수 | 사유 |
|---|---|---|---|
| 농업·임업·어업 | A (01~03) | 21 | 산안법 적용 특례, TAI Safe 1차 외 |
| 공공행정·국방 | O (84) | 10 | 행정기관 — 사업주 의무 아님 |
| 가구내 고용활동 | T (97~98) | 3 | 사업장 개념 부적합 |
| 국제·외국기관 | U (99) | 1 | 적용 제외 |

**UNUSED 합계: 35개 lv4 코드**

### ORPHAN 분류 기준

```
status = 'ORPHAN' 조건:
  - lv1_code = NULL (KSIC 분류 실패) — 265개 공정
  - 섹션 판단 불가 (제조이면서 건물관리 혼재)
  - 코드 원천 불명
```

| ORPHAN 후보 | 규모 | 사유 |
|---|---|---|
| lv1_code NULL 공정 | 265개 process_id | KSIC 미연결 — 분류 실패 |
| equipment 정수코드 (040, 036 등) | 36종 | 의미 불명 코드 — 표준화 필요 |
| 경계 업종 (G 도소매 일부) | 미정 | INDUSTRIAL/BUILDING 경계 모호 |

---

## 산출물 D: input_code_catalog DDL 초안

```sql
CREATE TABLE input_code_catalog (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- 섹션 (UNUSED 포함 4종, ORPHAN은 status로 표현)
  section           TEXT,                         -- INDUSTRIAL/CONSTRUCTION/BUILDING/UNUSED/NULL(ORPHAN)

  -- 코드 타입
  code_type         TEXT NOT NULL,                -- 9종

  -- 원천 정보 (원본 보존 — 참조만)
  source_table      TEXT NOT NULL,                -- ksic_process_map / factories / equipment_assets 등
  source_code       TEXT,                         -- 원천 코드 (C20, P-WELDING, 040 등)
  source_name       TEXT,                         -- 원천 명칭 (화학물질 제조업 등)

  -- 표준화 코드
  standard_code     TEXT,                         -- 표준 코드 (있는 경우)
  normalized_code   TEXT,                         -- {SECTION}-{TYPE}-{CODE} 형식
  display_name      TEXT,                         -- 화면 표시 명칭

  -- 상태 관리
  status            TEXT NOT NULL DEFAULT 'CANDIDATE',  -- CANDIDATE/CONFIRMED/UNUSED/ORPHAN/REJECTED
  orphan_reason     TEXT,                         -- ORPHAN인 경우 사유

  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),

  CONSTRAINT icc_section_check CHECK (
    section IS NULL OR section IN ('INDUSTRIAL','CONSTRUCTION','BUILDING','UNUSED')
  ),
  CONSTRAINT icc_code_type_check CHECK (
    code_type IN (
      'KSIC_CODE',
      'CONSTRUCTION_STANDARD_CODE',
      'PROCESS_CODE',
      'EQUIPMENT_CODE',
      'FACILITY_CODE',
      'MATERIAL_CODE',
      'HAZARD_CODE',
      'NUMERIC_FIELD',
      'BOOLEAN_FIELD'
    )
  ),
  CONSTRAINT icc_status_check CHECK (
    status IN ('CANDIDATE','CONFIRMED','UNUSED','ORPHAN','REJECTED')
  ),
  -- ORPHAN이면 reason 필수
  CONSTRAINT icc_orphan_reason_check CHECK (
    status != 'ORPHAN' OR orphan_reason IS NOT NULL
  ),
  -- 중복 방지
  CONSTRAINT icc_unique_code UNIQUE (source_table, source_code, code_type)
);

CREATE INDEX idx_icc_section ON input_code_catalog (section, status);
CREATE INDEX idx_icc_code_type ON input_code_catalog (code_type, status);
CREATE INDEX idx_icc_normalized ON input_code_catalog (normalized_code);
CREATE INDEX idx_icc_status ON input_code_catalog (status);
CREATE INDEX idx_icc_source ON input_code_catalog (source_table, source_code);
```

### 표준 코드 형식 (TASK-004)

```
{SECTION}-{TYPE}-{CODE}

예시:
  INDUSTRIAL-KSIC-C20              화학물질 제조업
  INDUSTRIAL-PROCESS-반응          반응 공정
  INDUSTRIAL-BOOLEAN-has_chemical  화학물질 보유
  CONSTRUCTION-STANDARD-토공사      토공사 (건설표준코드)
  CONSTRUCTION-BOOLEAN-has_tower_crane  타워크레인 보유
  BUILDING-FACILITY-ELEVATOR       승강기 시설
  BUILDING-NUMERIC-building_area   건물 면적
  UNUSED-KSIC-A01                  농업 (미사용)
  (ORPHAN)-PROCESS-UNKNOWN_265     KSIC 미연결 공정 — section NULL, status ORPHAN
```

---

## 산출물 E: 섹션별 코드 원천 목록

### INDUSTRIAL 코드 원천

| code_type | 원천 | 규모 |
|---|---|---|
| KSIC_CODE | ksic_process_map (B,C,D,E,H 대분류) | 약 230개 lv4 |
| PROCESS_CODE | ksic_process_map.process_id (제조 공정) | 약 1,600개 |
| EQUIPMENT_CODE | equipment_assets | 40종 |
| MATERIAL_CODE | 화학물질·위험물 | 미정 (별도 원천) |
| HAZARD_CODE | has_confined_space, has_chemical_substance, has_high_pressure_gas, has_boiler | 4개 |
| NUMERIC_FIELD | employee_count, building_area, electrical_capacity_kw | 3개 |
| BOOLEAN_FIELD | has_* (산업 해당) | 4개 |

### CONSTRUCTION 코드 원천

| code_type | 원천 | 규모 |
|---|---|---|
| KSIC_CODE | ksic_process_map (F 대분류) | 16개 lv4 |
| CONSTRUCTION_STANDARD_CODE | (테이블 미존재 — 추가 필요) | 223개 건설 공정 |
| PROCESS_CODE | ksic_process_map.process_id (건설 공종) | 약 223개 |
| HAZARD_CODE | has_blasting, has_diving, has_asbestos_demo, has_confined_space | 4개 |
| NUMERIC_FIELD | construction_amount, contractor_count | 2개 |
| BOOLEAN_FIELD | has_tower_crane | 1개 |

### BUILDING 코드 원천

| code_type | 원천 | 규모 |
|---|---|---|
| KSIC_CODE | ksic_process_map (G,I,J,K,L,M,N,P,Q,R,S 대분류) | 약 250개 lv4 |
| FACILITY_CODE | 보일러/승강기/전기/소방/냉동 | 5종 (미정 원천) |
| NUMERIC_FIELD | building_area, occupant_capacity, elevator_count | 3개 |
| BOOLEAN_FIELD | has_boiler, has_asbestos_demo | 2개 |

### UNUSED 코드 원천

| code_type | 원천 | 규모 |
|---|---|---|
| KSIC_CODE | ksic_process_map (A,O,T,U 대분류) | 35개 lv4 |

### ORPHAN 후보

| 원천 | 규모 | orphan_reason |
|---|---|---|
| ksic_process_map (lv1_code NULL) | 265개 process_id | KSIC 미연결 |
| equipment_assets (정수코드) | 36종 | 의미코드 미표준화 |

---

## 핵심 확정 사항

### KSIC 실제 규모 (확인됨)

```
ksic_process_map 기준:
  대분류(lv1): 21개
  중분류(lv2): 77개
  소분류(lv3): 234개
  세분류(lv4): 501개  ← 실제 KSIC 코드 단위
  연결 공정(process_id): 3,378개
```

> 지시서의 "4,000여 개"는 KSIC 세분류(501) + 공정(3,378) + 설비(40) + has_*(9) + numeric(8) = **약 3,936개**로 확인.
> 입력값 코드화 대상 총량과 일치.

### 섹션 분류 매핑 (KSIC 대분류 기준)

```
INDUSTRIAL:   B, C, D, E, H        (약 230개 lv4)
CONSTRUCTION: F                     (16개 lv4)
BUILDING:     G,I,J,K,L,M,N,P,Q,R,S (약 250개 lv4)
UNUSED:       A, O, T, U            (35개 lv4)
ORPHAN:       lv1_code NULL         (265개 process)
```

---

## 성공 기준 답변

> 입력값은 어느 섹션에 속하는가? → KSIC 대분류로 4섹션 분류 가능
> 어떤 코드 타입인가? → 9종 code_type으로 분류 가능
> 서비스에서 사용할 것인가? → status = CANDIDATE/CONFIRMED
> 미사용인가? → status = UNUSED (A,O,T,U)
> 고아인가? → status = ORPHAN (lv1 NULL 265개)
> 법령 매핑 전에 어떤 코드로 표현되는가? → {SECTION}-{TYPE}-{CODE}

---

## 다음 단계

```
WO-INPUT-CODE-ARCHITECTURE-001 (현재) — 완료
      ↓
WO-INPUT-CODE-INVENTORY-001
  input_code_catalog 테이블 생성 (apply_migration)
  실제 DB 입력값을 코드 체계에 맞춰 적재 후보로 정리
  - KSIC 501개 → 섹션 분류
  - PROCESS 3,378개 → 섹션 분류
  - EQUIPMENT 40종 → 코드화
  - has_* / numeric → 코드화
      ↓
WO-PATTERN-MAPPING-001
  입력코드(input_code_catalog) ↔ 법령코드(law_pattern) 교차 매핑
```

---

*WO-INPUT-CODE-ARCHITECTURE-001 완료.*
*섹션 4종(+ORPHAN 상태) / 코드타입 9종 / input_code_catalog DDL 확정.*
*핵심: UNUSED(섹션)와 ORPHAN(상태) 분리. KSIC 501 세분류 + 공정 3,378 = 약 3,936개 코드화 대상.*
