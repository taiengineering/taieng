# WO-CONDITION-MAP-001 기존 조건 구조 전수 조사 보고서

**작성일:** 2026-06-23  
**상태:** 조사 완료 / 구현 금지  
**목적:** 기존 구조가 얼마나 살아있는지 확인

---

## Deliverable A: 조건 정보 저장 위치 맵 (실건수)

```
조건 정보
│
├─ semantic_clause.condition_text          862건 (사업주 의무 1,480건 중 58.2%)
│   └─ 실제 사용 가능한 조건 텍스트 존재
│
├─ rule_candidate_slot (slot_type별)
│   ├─ CONDITION                          8,343건 (7,134개 rule에 분산)
│   │   ├─ binding_field 있는 것          3건 (has_tower_crane, has_blasting, has_asbestos_demo)
│   │   └─ binding_field NULL             8,340건 (99.96% UNRESOLVED)
│   │       ├─ UNRESOLVED_CONDITION       대부분 (형식적 토큰)
│   │       ├─ IF_AFTER_INSTALL           설치/시설 조건 (~350건)
│   │       ├─ IF_OPERATIONAL             사용 조건 (~80건)
│   │       ├─ IF_OVER_THRESHOLD          수치 초과 조건 (~200건)
│   │       ├─ IF_ON_CHANGE               변경 조건 (~100건)
│   │       └─ IF_ON_ACCIDENT             사고 발생 조건 (~50건)
│   │
│   ├─ NUMERIC                            4,230건 (3,492개 rule)
│   │   ├─ DEADLINE_THRESHOLD_FAMILY      2,332건 (기한)
│   │   ├─ DISTANCE_THRESHOLD_FAMILY      415건  (거리)
│   │   ├─ FREQUENCY_THRESHOLD_FAMILY     410건  (주기)
│   │   ├─ EMPLOYEE_THRESHOLD_FAMILY      164건  (인원수)
│   │   ├─ VOLTAGE_THRESHOLD_FAMILY       142건  (전압)
│   │   ├─ CONCENTRATION_THRESHOLD_FAMILY 110건  (농도)
│   │   └─ 기타                           657건
│   │
│   └─ SCOPE                              868건 (594개 rule)
│       └─ 소방시설/소화설비/안전장치 등
│
├─ appendix_condition                     7건 (별표 1개만 수집)
│   └─ employee_count >= 50/500/1000 (안전관리자 선임 기준)
│
├─ draft_slot (binding_field 실사용)
│   ├─ distance_value     415건
│   ├─ equipment_type     260건
│   ├─ facility_type      220건
│   ├─ voltage_level      142건
│   ├─ concentration_level 110건
│   ├─ employee_count      40건 (오분류 포함)
│   ├─ has_tower_crane      1건
│   ├─ has_blasting         1건
│   └─ has_asbestos_demo    1건
│
└─ facility_applicability (체크엔진 실행 결과)
    ├─ MISSING_DATA      3,773,215건 (98.9%)
    ├─ POSSIBLE_CANDIDATE  128,606건
    ├─ AMBIGUOUS            33,038건
    ├─ MATCH_CANDIDATE       6,976건
    └─ NOT_MATCHED           2,037건
```

---

## Deliverable B: 조건 구조화 수준 (LEVEL별 건수)

| LEVEL | 정의 | 해당 데이터 | 건수 |
|---|---|---|---|
| LEVEL 0 | 텍스트만 존재 | condition_text (binding 없음) | 약 859건 |
| LEVEL 1 | Slot 존재 (의미 분류만) | CONDITION slot (binding_field NULL) | 8,340건 |
| LEVEL 2 | 입력필드 매핑 가능 | draft_slot binding_field 有 / appendix_condition | 약 1,260건 |
| LEVEL 3 | 체크엔진 직접 사용 가능 | MATCH_CANDIDATE + has_* binding 3건 | 6,979건 |

**핵심:**  
- LEVEL 3 숫자(6,979건)는 크지만 실질은 match_details = {"checks": N} 수준
- has_* 입력 필드로 직접 연결된 것은 **3건**뿐
- TAI Safe 소비자 입력 필드(has_confined_space, has_chemical_substance 등) → **체크엔진 미연결**

---

## Deliverable C: condition_code 신규 필요성 판정

### 판정: **B. 일부 보강 필요** (단, 보강 규모가 상당함)

**살아있는 구조 (재사용 가능):**
- NUMERIC binding_field 체계 (거리/전압/농도/인원수) 약 840건
- appendix_condition의 threshold_field/operator/value 패턴
- CONDITION slot family_name 분류 (참고용)

**구멍인 구조 (보강 필요):**
- has_* 입력 필드 바인딩: has_confined_space 0건, has_chemical_substance 0건, has_mobile_crane 0건
- CONDITION slot binding_field NULL: 8,340/8,343 = 99.96%
- appendix_condition: 1개 별표만 수집 (안전관리자만)
- semantic_clause ↔ slot 연결률: 40%

**기존 구조가 다루는 것 vs 다루지 않는 것:**
```
다루는 것                    다루지 않는 것
─────────────────────        ──────────────────────────────
수치 조건 (거리/전압)          has_confined_space
설비/시설 범주                 has_chemical_substance
기한/주기                      has_tower_crane (정방향)
인원수 (일부)                  has_blasting (정확한 연결)
                               equipment_type_code 세분화
                               복합 조건 (AND/OR)
                               업종/KSIC 조건
```

---

## Deliverable D: 최종 구조 권고

### 권고: **OPTION B — condition_mapping 테이블 추가**

**OPTION A (기존 slot 체계 확장) 부적합:**
- rule_candidate_slot은 법령 파싱 엔진 산출물, 수동 개입 구조 아님
- 8,340건 UNRESOLVED 수동 매핑은 비현실적

**OPTION C (condition_code 신규 구축) 과도:**
- semantic_clause.condition_text 862건 (원문) 이미 존재
- NUMERIC binding_field 약 840건 이미 존재
- appendix_condition 패턴 재사용 가능

**OPTION B 구체적 형태:**
```
기존 구조                 추가할 구조
──────────────            ──────────────────────────────
semantic_clause  ←────── condition_mapping_candidate
  condition_text           ├─ input_field (has_confined_space 등)
                           ├─ input_value
NUMERIC binding ─────→    ├─ input_operator
(재사용)                   ├─ condition_code (식별자)
                           └─ null_condition_class
appendix_condition ──→
(재사용)

소비자 입력
  ↓
condition_mapping_candidate 조회
  ↓
semantic_clause_id 목록 반환
  ↓
의무 확정
```

---

## 5개 조사 요약

| 조사 | 결과 |
|---|---|
| 조사1 semantic_clause | 1,480건, condition_text 58.2% 존재 |
| 조사2 rule_candidate_slot | CONDITION 8,343건 중 binding_field 있는 것 3건(0.04%) |
| 조사3 연결 구조 | condition_text 있는 의무 중 slot 연결 48%, binding_field 사실상 없음 |
| 조사4 appendix_condition | 7건 (1개 별표만) — WO-APPENDIX-COLLECT-001 미완료 |
| 조사5 draft_slot | has_* 바인딩 3건, 나머지 수치/설비 범주 중심 |

**수치 조건은 살아있다. 소비자 입력 필드 바인딩은 없다.**

---

*WO-CONDITION-MAP-001 완료. 다음: condition_mapping_candidate DDL 설계 승인 또는 WO-APPENDIX-COLLECT-001 선행.*
