# WO-CONDITION-MAPPING-001
# Condition Mapping 섹션 구조 설계서

**작성일:** 2026-06-23 | **상태:** 설계 완료 / 승인 대기

---

## 핵심 원칙

```
금지:  법령 → COMMON 섹션
허용:  법령 → 적용영역(다중) → [INDUSTRIAL, CONSTRUCTION, BUILDING, SPECIAL]

"공용 법령"은 없다.
"다중 적용영역 법령"이 있을 뿐이다.
```

---

## 실데이터 확인 (law_sector_mapping 기존 존재)

```
성업안전보건기준에 관한 규칙: ['BUILDING','INDUSTRIAL','CONSTRUCTION']
실업안전보건법:          ['BUILDING','INDUSTRIAL','CONSTRUCTION']
승강기안전관리법:          ['BUILDING','CONSTRUCTION']
소방시설 설치 및 관리에 관한 법률: ['BUILDING','CONSTRUCTION']
엔리지이용 합리화법 시행령:    ['INDUSTRIAL','BUILDING']
건설기계관리법:              ['CONSTRUCTION']

→ law_sector_mapping 테이블은 이미 sectors = ARRAY 타입으로 다중 섹션 지원
→ COMMON 대신 다중 적용영역은 이미 구현된 실제 컴실
```

---

## 적용영역 정의

| 영역 | 대상 | 대표 입력값 |
|---|---|---|
| INDUSTRIAL | 제조업 공장, 플랜트 | has_chemical_substance, has_hpg, has_boiler, ksic C10~C39 |
| CONSTRUCTION | 건설현장, 토목 | has_tower_crane, has_blasting, has_asbestos_demo, ksic F41/F42 |
| BUILDING | 건물관리, 시설관리 | has_boiler, has_confined_space, 승강기, 소방시설 |
| SPECIAL | 잠수, 항만 | has_diving | 1차 제외 |

---

## COMMON 유혽 대응 표

| 유혽 상황 | 잘못된 처리 | 올바른 처리 |
|---|---|---|
| "이 의무는 모든 사업장에 적용" | COMMON | `[IND, CON, BLD]` |
| 안전보건교육 | COMMON | `[IND, CON, BLD]` |
| 보일러 의무 | IND | `[IND, BLD]` |
| 타워크레인 의무 | COMMON | `[CON]` |
| 밀폐공간 의무 | COMMON | `[IND, CON, BLD]` |
| 안전관리자 50인 | COMMON | `[IND, CON, BLD]` |

---

## has_* 입력값 × applicable_sectors

| input_field | applicable_sectors | 이유 |
|---|---|---|
| has_chemical_substance | `[INDUSTRIAL]` | 관리대상 유해물질 = 제조업 |
| has_high_pressure_gas | `[INDUSTRIAL, CONSTRUCTION]` | 공장+고압건설 |
| has_confined_space | `[INDUSTRIAL, CONSTRUCTION, BUILDING]` | 탱크/터널/지하실 |
| has_blasting | `[CONSTRUCTION]` | 발파굴착 = 건설 |
| has_tower_crane | `[CONSTRUCTION]` | 타워크레인 = 건설 |
| has_boiler | `[INDUSTRIAL, BUILDING]` | 공장+건물 |
| has_asbestos_demo | `[CONSTRUCTION, BUILDING]` | 해체공사+리모델링 |
| has_diving | `[CONSTRUCTION, SPECIAL]` | 수중공사+특수 |
| employee_count >= 50 | `[INDUSTRIAL, CONSTRUCTION, BUILDING]` | 안전관리자 3개 샥터 |

---

## DDL 보완 (적용할 필드)

```sql
-- condition_mapping_candidate에 추가
applicable_sectors  TEXT[],

CONSTRAINT cmc_applicable_sectors_check CHECK (
  applicable_sectors IS NULL OR (
    NOT ('COMMON' = ANY(applicable_sectors))
    AND applicable_sectors <@ ARRAY['INDUSTRIAL','CONSTRUCTION','BUILDING','SPECIAL']
  )
)

-- 성공 검증 쿼리
SELECT COUNT(*) FROM condition_mapping_candidate
WHERE 'COMMON' = ANY(applicable_sectors);
-- 결과: 0 이어야 성공
```

---

## 안전보건기준 규칙 챕터별 적용영역

| 챕터 | 조문 범위 | 건수 | applicable_sectors |
|---|---|---|---|
| 1장 총칙 | 1~99조 | 181건 | `[IND, CON, BLD]` |
| 2장 기계·기구 | 100~175조 | 91건 | `[IND, CON]` |
| 3장 양중기 | 176~230조 | 69건 | `[IND, CON]` |
| 4장 폭발·화재 | 231~270조 | 60건 | `[IND, CON, BLD]` |
| 5장 전기설비 | 271~350조 | 132건 | `[IND, CON, BLD]` |
| 6장 굴착·발파·건설 | 351~450조 | 147건 | `[CON]` |
| 7장 화학설비 | 451~520조 | 97건 | `[IND]` |
| 8장 고압작업 | 521~560조 | 74건 | `[IND, CON]` |
| 9장 관리대상유해물질 | 561~600조 | 64건 | `[IND]` |
| 10장 밀폐공간 | 601~680조 | 100건 | `[IND, CON, BLD]` |

---

*WO-CONDITION-MAPPING-001 완료. 승인 후 WO-CONDITION-DDL-001 DDL에 applicable_sectors 필드 추가.*
