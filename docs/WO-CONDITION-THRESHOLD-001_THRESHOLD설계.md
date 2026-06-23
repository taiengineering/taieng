# WO-CONDITION-THRESHOLD-001
# THRESHOLD Path 설계 보고서

**작성일:** 2026-06-23 | **상태:** 설계 완료 / INSERT 미실행
**INSERT 금지 — WO-CONDITION-THRESHOLD-001-APPLY에서 실행**

---

## 산출물 A: THRESHOLD 원천 데이터 맵

### A-1. appendix_condition (주 원천)

| source_id | threshold_field | op | value | sector | industry_name | law_basis | semantic_clause 연결 | 설명 가능 |
|---|---|---|---|---|---|---|---|---|
| 375f1daa | employee_count | >= | 50 | INDUSTRIAL | 식료품·음료 등 고위험 제조업 | 산업안전보건법 시행령 | 법 제17조 → `66772b0d`, `2fc6b8a9` | ✅ |
| d316d7c2 | employee_count | >= | 50 | INDUSTRIAL | 운수·창고업(49~52) | 동일 | 동일 | ✅ |
| d14d9e61 | employee_count | >= | 50 | INDUSTRIAL | 제1~27호 외의 사업 | 동일 | 동일 | ✅ |
| a3e72e04 | employee_count | >= | 50 | INDUSTRIAL | 토사석 광업(071) | 동일 | 동일 | ✅ |
| e825f6ae | employee_count | >= | 500 | INDUSTRIAL | 식료품·음료 등 고위험 | 동일 | 동일 (안전관리자 2명) | ✅ |
| b9929c23 | employee_count | >= | 500 | INDUSTRIAL | 운수·창고업(49~52) | 동일 | 동일 (안전관리자 2명) | ✅ |
| ea0589c5 | employee_count | >= | 1000 | INDUSTRIAL | 제1~27호 외의 사업 | 동일 | 동일 (안전관리자 2명) | ✅ |

**appendix_condition 특이사항:**
- 7건 전부 `condition_type = '안전관리자_선임기준'`
- `sector` 전부 INDUSTRIAL — CONSTRUCTION·BUILDING 기준은 별표에 별도 존재하나 미입력 상태
- `ksic_code` 전부 NULL — 업종 코드가 없어 정밀 매핑은 COMPOUND로 처리 필요
- **핵심 문제:** 50명 조건이 업종마다 다름(고위험 제조업 50명 / 기타 업종 50명). 단순 `employee_count >= 50` 하나로 통합하면 업종 조건 누락.

### A-2. semantic_clause 직접 탐색 결과

| sc_id | article_no | 의무 내용 | threshold 포함 여부 | 비고 |
|---|---|---|---|---|
| 66772b0d | 17 | 안전관리자를 보좌 업무 수행자를 두어야 한다 | condition_text NULL — 기준은 시행령 위임 | 안전관리자 선임 의무 본조 |
| 2fc6b8a9 | 17 | 관리감독자에게 지도·조언하는 사람을 두어야 한다 | 동일 | 17조 항1 단편 |
| 566c1a83 | 17 | 전담 안전관리자 의무 | condition_text NULL | 전담 기준도 시행령 위임 |
| 879aeeac | 19 | 안전보건관리담당자를 사업장에 두어야 한다 | condition_text NULL — 기준은 시행령 위임 | 안전보건관리담당자 선임 의무 본조 |
| 67055d7d | 25 | 안전보건관리규정을 작성하여야 한다 | condition_text NULL — 기준은 시행규칙 위임 | 안전보건관리규정 작성 의무 본조 |
| ff0f73e7 | 15 | 안전보건관리책임자 지정 의무 | condition_text NULL | 규모 기준 시행령 위임 |
| 94e85f9b | 19(기준규칙) | 옥내작업장 경보용 설비 | **50명 이상 OR 400㎡ 이상 — condition_text에 직접 명시** | COMPOUND 후보 |

### A-3. draft_slot employee_count 탐색 결과

**결론: 사용 불가.**

draft_slot의 `binding_field = 'employee_count'`는 실제 인원 기준이 아니라 "기한(일수, 년도)" 슬롯에 잘못 분류되어 있음. value가 0~100이나 단위가 '일', '년'으로 오매핑. 인원 기준 THRESHOLD 설계에 draft_slot을 원천으로 사용하지 않는다.

### A-4. 기타 수치 조건 (draft_slot binding_field 분포)

| binding_field | 단위 | 범위 | THRESHOLD 활용 가능성 | 우선순위 |
|---|---|---|---|---|
| distance_value | m, mm | 0.01~600 | 거리 기준 의무 — 1차 외 | 낮음 |
| voltage_level | V, kV, kVA | 10~2000 | 전기 설비 기준 의무 | 중간 |
| concentration_level | % | 0.06~125 | 화학물질 농도 기준 | 중간 |
| storage_capacity | 톤, 리터 | 1~2400 | 위험물 저장 기준 | 중간 |
| area_size | ㎡ | 60~120 | 면적 기준 | 중간 |
| monetary_value | 억원 | 1~300 | 공사금액 기준(CONSTRUCTION) | 낮음 |
| power_capacity | kW | 0.7~500 | 전력 설비 기준 | 낮음 |

---

## 산출물 B: employee_count 기반 의무 후보

### 핵심 발견: 3개 의무 계층

법적 구조를 먼저 이해해야 한다.

```
산업안전보건법 본법 (조문)
    제17조 — 안전관리자를 두어야 한다
              ↳ 기준은 "대통령령으로 정한다" (위임)
    제19조 — 안전보건관리담당자를 두어야 한다
              ↳ 기준은 "대통령령으로 정한다" (위임)
    제25조 — 안전보건관리규정을 작성하여야 한다
              ↳ 기준은 "고용노동부령으로 정한다" (위임)

산업안전보건법 시행령 (별표)
    별표 3 — 안전관리자 선임 기준
              ↳ 업종별 employee_count 기준 → appendix_condition 7건
    별표 5 — 안전보건관리담당자 선임 기준
              ↳ employee_count >= 20 (상시근로자 20~49명 사업장)
    별표 ? — 안전보건관리규정 작성 의무 사업장
              ↳ employee_count >= 100
```

### B-1. 안전관리자 선임 의무

**Q1. 어떤 입력값?** `employee_count`
**Q2. 비교 연산자?** `>=`
**Q3. 기준값?** `50` (업종에 따라 더 낮을 수 있으나 가장 일반적)
**Q4. 법령 근거?** 산업안전보건법 제17조 + 시행령 별표 3
**Q5. 발생 의무?** 안전관리자를 사업장에 두어야 함

**의무 발생 경로:**
```
employee_count >= 50 (업종별 기준)
  + sector IN ['INDUSTRIAL','CONSTRUCTION','BUILDING']
    → appendix_condition → 법 제17조 semantic_clause
      → 안전관리자 선임 의무
```

**주의사항:**
- 업종(ksic_code)별 기준이 다름 — 50명이 가장 광범위한 기준이나 전부가 아님
- CONSTRUCTION·BUILDING 기준은 appendix_condition에 미입력 — 현재 INDUSTRIAL만 근거 있음
- 업종 조건 없이 employee_count만으로 매핑하면 과매핑 → COMPOUND 처리 필요성 있음
- **1차 매핑 결정:** 업종 무관 최소 기준으로 `employee_count >= 50 → 전 sector` 1건 우선 설계. 업종별 세분화는 별도 WO.

| condition_code | input_field | op | value | sectors | appendix_condition_id | semantic_clause_id | condition_type |
|---|---|---|---|---|---|---|---|
| THRESHOLD:EMPLOYEE_GTE_50:SAFETY_MANAGER | employee_count | >= | 50 | ['INDUSTRIAL','CONSTRUCTION','BUILDING'] | d14d9e61 (기타사업 대표) | 66772b0d (법17조) | THRESHOLD |

---

### B-2. 안전보건관리담당자 선임 의무

**Q1. 어떤 입력값?** `employee_count`
**Q2. 비교 연산자?** `>=`
**Q3. 기준값?** `20` (상시근로자 20~49명 사업장 — 안전관리자 선임 의무 없는 사업장)
**Q4. 법령 근거?** 산업안전보건법 제19조 + 시행령 별표 5
**Q5. 발생 의무?** 안전보건관리담당자를 사업장에 두어야 함

**의무 발생 경로:**
```
employee_count >= 20 AND employee_count < 50
  → 법 제19조 semantic_clause(879aeeac, 60fbb658)
    → 안전보건관리담당자 선임 의무
```

**핵심 주의:** 이 의무는 `20 <= employee_count < 50` 구간 의무. 단순 `>= 20`으로 하면 50인 이상 사업장에도 발동. 실제로는 안전관리자 선임 의무와 대체 관계. **1차 설계는 `>= 20`으로 하되 review_status = PENDING.**

| condition_code | input_field | op | value | sectors | appendix_condition_id | semantic_clause_id | condition_type |
|---|---|---|---|---|---|---|---|
| THRESHOLD:EMPLOYEE_GTE_20:SAFETY_HEALTH_OFFICER | employee_count | >= | 20 | ['INDUSTRIAL'] | NULL (미입력) | 879aeeac (법19조) | THRESHOLD |

**appendix_condition 부재:** 시행령 별표 5 기준이 appendix_condition에 미입력. semantic_clause만 연결. PENDING 처리.

---

### B-3. 안전보건관리규정 작성 의무

**Q1. 어떤 입력값?** `employee_count`
**Q2. 비교 연산자?** `>=`
**Q3. 기준값?** `100` (상시근로자 100명 이상 — 시행규칙 별표 2)
**Q4. 법령 근거?** 산업안전보건법 제25조 + 시행규칙 별표 2
**Q5. 발생 의무?** 안전보건관리규정을 작성하여야 함

**의무 발생 경로:**
```
employee_count >= 100
  + 특정 업종 (시행규칙 별표 2 열거 업종)
    → 법 제25조 semantic_clause(67055d7d)
      → 안전보건관리규정 작성 의무
```

**appendix_condition 부재:** 시행규칙 별표 2가 appendix_condition에 미입력. semantic_clause만 연결. PENDING.

| condition_code | input_field | op | value | sectors | appendix_condition_id | semantic_clause_id | condition_type |
|---|---|---|---|---|---|---|---|
| THRESHOLD:EMPLOYEE_GTE_100:SAFETY_HEALTH_RULES | employee_count | >= | 100 | ['INDUSTRIAL','CONSTRUCTION','BUILDING'] | NULL (미입력) | 67055d7d (법25조) | THRESHOLD |

---

### B-4. 경보용 설비 설치 의무 (COMPOUND 전환 필요)

**조문:** 안전보건기준규칙 제19조
**조건:** 연면적 400㎡ 이상 **OR** 상시 50명 이상 옥내작업장

**이 조문은 THRESHOLD 단독이 아니다:**
```
employee_count >= 50  OR  building_area >= 400(㎡)
→ 경보용 설비 설치 의무 (sc_id: 94e85f9b)
```

compound_operator = 'OR', 두 조건 중 하나만 충족해도 발동.
→ **COMPOUND Path로 이관. 이번 WO에서 THRESHOLD 단독 INSERT 불가.**

---

## 산출물 C: THRESHOLD 후보 분류

### CONFIRMED_CANDIDATE (즉시 적재 가능)

| condition_code | 근거 | 신뢰도 |
|---|---|---|
| THRESHOLD:EMPLOYEE_GTE_50:SAFETY_MANAGER | appendix_condition 4건 + 법17조 semantic_clause 연결 명확 | 높음 |

**단, 업종 조건 미반영 — 전 업종 적용으로 단순화한 1차 버전. 향후 업종별 COMPOUND로 세분화 예정.**

### PENDING_REVIEW (조문·근거 확인됐으나 appendix_condition 미입력)

| condition_code | 이유 |
|---|---|
| THRESHOLD:EMPLOYEE_GTE_20:SAFETY_HEALTH_OFFICER | 시행령 별표 5 appendix_condition 미입력. 20~49명 구간 의무 — 50인 이상과 대체 관계 설계 필요. |
| THRESHOLD:EMPLOYEE_GTE_100:SAFETY_HEALTH_RULES | 시행규칙 별표 2 appendix_condition 미입력. 업종 열거 조건 있음. |

### COMPOUND 전환

| condition_code 예정 | 이유 |
|---|---|
| COMPOUND:EMPLOYEE_OR_AREA_50:ALARM | 안전보건기준규칙 19조 — employee >= 50 OR area >= 400㎡. 단독 THRESHOLD 불가. |

### DEFERRED (이번 WO 외)

| 항목 | 이유 |
|---|---|
| construction_amount | factories.contract_amount 컬럼 미존재 |
| chemical_daily_volume_liter | factories 컬럼 미존재. has_chemical 2건(dd47, a88d)은 COMPOUND로 이관 대기. |
| voltage_level | draft_slot 데이터 있으나 factories 입력 필드 미연결 |
| concentration_level | 동일 |
| storage_capacity | 동일 |
| area_size | factories.building_area 존재하나 법령 기준 appendix_condition 미입력 |

### EXCLUDED

해당 없음. 탐색한 의무 전부 사업주 의무이며 THRESHOLD 경로 적합.

---

## 산출물 D: INSERT SQL 초안 (실행 금지 — APPLY에서 실행)

```sql
-- ============================================================
-- WO-CONDITION-THRESHOLD-001-APPLY INSERT 초안
-- 실행 금지: WO-CONDITION-THRESHOLD-001-APPLY 승인 후 실행
-- ============================================================

-- [1] 안전관리자 선임 의무 — employee_count >= 50 (업종 무관 최소 기준)
INSERT INTO condition_mapping_candidate (
  semantic_clause_id,
  source_article_id,
  appendix_condition_id,
  applicable_sectors,
  condition_source,
  condition_type,
  condition_code,
  input_field,
  input_operator,
  input_value,
  confidence,
  review_status
) VALUES (
  '66772b0d-516d-4eae-b5ec-c99729e63d3c',  -- 법 제17조 항1 (안전관리자를 두어야 한다)
  '3cec4dca-4827-4676-818d-edb356ad8219',  -- 법 제17조 article_id
  'd14d9e61-8334-4c05-807b-f0b839b15f23',  -- appendix_condition: 기타사업 50명 이상
  ARRAY['INDUSTRIAL','CONSTRUCTION','BUILDING'],
  'APPENDIX',
  'THRESHOLD',
  'THRESHOLD:EMPLOYEE_GTE_50:SAFETY_MANAGER',
  'employee_count',
  '>=',
  '50',
  0.90,
  'PENDING'  -- 업종 조건 미반영으로 PENDING (전 업종 적용 단순화 버전)
);

-- [2] 안전보건관리담당자 선임 의무 — employee_count >= 20
INSERT INTO condition_mapping_candidate (
  semantic_clause_id,
  source_article_id,
  applicable_sectors,
  condition_source,
  condition_type,
  condition_code,
  input_field,
  input_operator,
  input_value,
  confidence,
  review_status
) VALUES (
  '879aeeac-9a1b-4307-a04b-777130093ead',  -- 법 제19조 항1 (안전보건관리담당자를 두어야 한다)
  'c7b7f29b-c862-4484-97bb-53264b98692d',  -- 법 제19조 article_id
  ARRAY['INDUSTRIAL'],
  'APPENDIX',
  'THRESHOLD',
  'THRESHOLD:EMPLOYEE_GTE_20:SAFETY_HEALTH_OFFICER',
  'employee_count',
  '>=',
  '20',
  0.80,
  'PENDING'  -- appendix_condition 미입력, 20~49명 구간 의미이나 >= 로 단순화
);

-- [3] 안전보건관리규정 작성 의무 — employee_count >= 100
INSERT INTO condition_mapping_candidate (
  semantic_clause_id,
  source_article_id,
  applicable_sectors,
  condition_source,
  condition_type,
  condition_code,
  input_field,
  input_operator,
  input_value,
  confidence,
  review_status
) VALUES (
  '67055d7d-a9ab-4c22-bba6-35a9aebd6456',  -- 법 제25조 항1 (안전보건관리규정 작성)
  'f4838223-0576-439e-b72f-961a438aec37',  -- 법 제25조 article_id
  ARRAY['INDUSTRIAL','CONSTRUCTION','BUILDING'],
  'APPENDIX',
  'THRESHOLD',
  'THRESHOLD:EMPLOYEE_GTE_100:SAFETY_HEALTH_RULES',
  'employee_count',
  '>=',
  '100',
  0.85,
  'PENDING'  -- 시행규칙 별표 2 appendix_condition 미입력
);

-- ============================================================
-- 총 3건. 전부 review_status = 'PENDING'
-- CONFIRMED 승격 조건:
--   - 업종 조건 포함 COMPOUND 설계 또는
--   - 전 업종 적용 단순화 버전으로 명시적 승인
-- ============================================================
```

---

## 핵심 발견 및 결론

### 발견 1: semantic_clause condition_text NULL 구조 확인

안전관리자 선임(법17조), 안전보건관리담당자(법19조), 안전보건관리규정(법25조) 모두 **본조 condition_text = NULL**.

이유: 법에서 "대통령령으로 정한다" / "고용노동부령으로 정한다"로 위임했기 때문.
→ **THRESHOLD 의무의 원인 = appendix_condition (별표)이지 semantic_clause.condition_text가 아님.**
→ condition_mapping_candidate에서 `appendix_condition_id`를 원인으로 쓰는 것이 정확.

### 발견 2: appendix_condition 부족

현재 appendix_condition은 7건 전부 `안전관리자_선임기준`만 존재.
안전보건관리담당자(별표 5), 안전보건관리규정(시행규칙 별표 2)는 미입력.

**다음 WO 선행 과제:** appendix_condition에 20명·100명 기준 별표 데이터 입력.

### 발견 3: 업종 조건 — THRESHOLD vs COMPOUND 경계

안전관리자 기준이 업종별로 다름(50명 / 기타 업종 다름). 업종 조건을 포함하면 COMPOUND.
1차 설계는 "최소 공통 기준(50명)"으로 THRESHOLD 단순화. 향후 COMPOUND로 세분화.

### 발견 4: draft_slot employee_count 오매핑

draft_slot의 employee_count 슬롯은 인원 기준이 아니라 기한(일수) 슬롯으로 오분류됨.
THRESHOLD 원천으로 사용 불가. appendix_condition이 유일한 정합 원천.

---

## 다음 단계

1. **선행 작업:** appendix_condition에 아래 데이터 입력 필요
   - 시행령 별표 5: 안전보건관리담당자 선임 기준 (employee_count >= 20, 20~49명 구간)
   - 시행규칙 별표 2: 안전보건관리규정 작성 의무 (employee_count >= 100, 업종 목록)

2. **WO-CONDITION-THRESHOLD-001-REVIEW** — 3건 조문 감사 (HAS_* AUDIT과 동일 기준)

3. **WO-CONDITION-THRESHOLD-001-APPLY** — 3건 INSERT

4. **WO-CONDITION-COMPOUND-001** — 경보용 설비(19조) + has_chemical 100리터 + DIVING/고압 복합 처리

---

*WO-CONDITION-THRESHOLD-001 완료. INSERT 미실행. 3건 후보 설계 완료.*
*핵심: THRESHOLD 의무의 원인은 appendix_condition(별표)이며, semantic_clause.condition_text NULL은 위임 구조의 결과.*
