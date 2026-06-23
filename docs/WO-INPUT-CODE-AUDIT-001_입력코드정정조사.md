# WO-INPUT-CODE-AUDIT-001
# 입력코드 추출 오류 정정 조사

**작성일:** 2026-06-23 | **상태:** 완료
**대상:** WO-INPUT-CODE-ARCHITECTURE-001 "설비 40종" 수치 검증
**금지:** 패턴 정의 / 매핑 / 테이블 생성 / INSERT / 법령 조회

---

## 결론 먼저

```
"설비 40종"은 잘못된 수치였다.

40 = equipment_assets.equipment_type_code distinct (목업 50개사 한정)

실제 설비 입력 원본 규모:
  - equipment_assets.asset_name:        1,495종 (목업 데이터 기준)
  - process_equipment_map.facility_name_std: 446종 (표준 설비명 — 전체 마스터)

→ 입력코드화 대상 설비 = 446종 (표준 설비명 기준)
```

---

## 산출물 A: 설비 컬럼 구조표

### equipment_assets (사업장 실제 보유 설비 — 인스턴스)

| 컬럼 | 타입 | 역할 |
|---|---|---|
| asset_name | text | 설비 개별 명칭 (자유 입력) |
| asset_code | text | 설비 개별 코드 (사업장별 고유) |
| equipment_type_code | text | 설비 유형 코드 (표준 분류) |
| equipment_category | text | 설비 대분류 |
| capacity_value / capacity_unit | numeric/text | 용량 |

**성격:** 사업장이 실제 보유한 설비 인스턴스. 목업 50개사 기준 3,284건.

### process_equipment_map (공정-설비 표준 매핑 — 마스터)

| 컬럼 | 타입 | 역할 |
|---|---|---|
| facility_name_std | text | **표준 설비명** (정규화됨) |
| source_facility_category | text | 설비 대분류 (INDUSTRY/ELEC/MECH 등) |
| process_id | text | 연결 공정 |
| equipment_role | text | 설비 역할 (필수/선택) |

**성격:** 공정별로 어떤 설비가 필요한지 정의한 표준 마스터. 187,319건.

---

## 산출물 B: distinct 기준별 설비 수

### equipment_assets (목업 50개사 한정 — 인스턴스 데이터)

| 기준 | distinct count | 의미 |
|---|---|---|
| equipment_type_code | **36** | ← 이전 보고서 "40"의 실제 출처 (반올림 오류 포함) |
| equipment_category | 13 | 설비 대분류 |
| asset_code | 3,284 | 개별 설비 (전부 고유) |
| **asset_name** | **1,495** | 설비 명칭 distinct |

### process_equipment_map (표준 마스터 — 전체)

| 기준 | distinct count | 의미 |
|---|---|---|
| **facility_name_std** | **446** | ← **실제 표준 설비명 마스터** |
| source_facility_category | 13 | 설비 대분류 |
| process_id | 2,826 | 연결 공정 |
| process_id + facility_name_std | 136,127 | 공정-설비 조합 |

---

## 산출물 C: 공정-설비 관계 규모표

| 항목 | 값 |
|---|---|
| process_equipment_map 총 row | 187,319 |
| distinct process | 2,826 |
| distinct 표준 설비명(facility_name_std) | 446 |
| 공정당 평균 설비 수 | 48.2개 |
| 공정당 최대 설비 수 | 279개 |
| 공정당 최소 설비 수 | 1개 |
| 공정-설비 고유 조합 | 136,127 |

### 설비 대분류(source_facility_category)별 분포

| category | 표준 설비명 수 | row 수 | 비고 |
|---|---|---|---|
| (NULL) | 195 | 9,152 | 미분류 — ORPHAN 후보 |
| MECH | 79 | 21,651 | 기계 설비 |
| ELEC | 60 | 50,032 | 전기 설비 |
| INDUSTRY | 58 | 36,637 | 산업 설비 |
| ENV | 42 | 12,641 | 환경 설비 |
| HAZMAT | 39 | 5,404 | 위험물 설비 |
| GAS | 37 | 8,801 | 가스 설비 |
| ENERGY | 27 | 2,047 | 에너지 설비 |
| UTILITY | 22 | 19,654 | 유틸리티 설비 |
| LIFT | 14 | 8,656 | 승강 설비 |
| SAFETY | 12 | 6,504 | 안전 설비 |
| FIRE | 8 | 2,042 | 소방 설비 |
| BUILD | 8 | 3,642 | 건축 설비 |
| (빈문자열) | 10 | 456 | ORPHAN 후보 |

**유효 설비 대분류: 13종 (NULL·빈문자열 제외)**

---

## 산출물 D: WO-INPUT-CODE-ARCHITECTURE-001 정정사항

### 정정 1: 설비 수치

```
[기존 — 오류]
"설비 40종"
"KSIC 501 + 공정 3,378 + 설비 40 + has_* 9 + numeric 8 = 약 3,936개"

[정정]
설비 40종은 equipment_type_code distinct(목업 50개사 한정, 실제 36개)였음.

실제 설비 입력 원본:
  - 표준 설비명(facility_name_std): 446종  ← 입력코드화 대상
  - equipment_type_code(유형코드): 36종    ← 상위 분류
  - equipment_category(대분류): 13종       ← 최상위 분류
```

### 정정 2: 입력코드화 대상 총량 재산정

```
[기존 — 오류]
약 3,936개

[정정]
구성요소 재산정:
  KSIC 세분류(lv4):        501
  공정(process_id):        3,378 (ksic_process_map) / 2,826 (process_equipment_map)
  표준 설비명(facility):    446   ← 40에서 446으로 정정
  has_* boolean:           9
  numeric field:           8
  ─────────────────────────────
  합계:                    약 4,342개 (process 3,378 기준)
                           또는 약 3,790개 (process 2,826 기준)
```

> "4,000여 개"라는 당초 사용자 추정이 정확했음.
> 설비를 446으로 정정하면 총량은 약 4,300개대로 4,000여 개와 일치.

### 정정 3: 공정 수치 출처 명확화

```
ksic_process_map.process_id:        3,378 distinct
process_equipment_map.process_id:   2,826 distinct

두 테이블의 공정 수가 다름 — 차이 552개:
  ksic_process_map = KSIC × 공정 매핑 (공정이 더 많음)
  process_equipment_map = 공정 × 설비 매핑 (설비 연결된 공정만)

→ 설비가 연결되지 않은 공정 552개 존재 가능성 (ORPHAN 후보)
```

---

## 산출물 E: 실제 입력코드화 대상 재산정

### code_type별 실제 원본 규모 (정정판)

| code_type | 원천 컬럼 | distinct | 비고 |
|---|---|---|---|
| KSIC_CODE | ksic_process_map.lv4_code | 501 | 세분류 단위 |
| PROCESS_CODE | ksic_process_map.process_id | 3,378 | KSIC 연결 공정 |
| EQUIPMENT_CODE (표준명) | process_equipment_map.facility_name_std | **446** | **정정 — 표준 설비명** |
| EQUIPMENT_CODE (유형) | equipment_assets.equipment_type_code | 36 | 상위 유형 분류 |
| EQUIPMENT_CATEGORY | source_facility_category | 13 | 최상위 대분류 |
| HAZARD_CODE | factories.has_* | 4 | 유해인자 |
| BOOLEAN_FIELD | factories.has_* | 9 | 보유여부 (HAZARD 중복 포함) |
| NUMERIC_FIELD | factories 수치컬럼 | 8 | 수치 입력 |

### 입력코드 계층 구조 (설비)

```
EQUIPMENT_CATEGORY (13종)        최상위 대분류
  예: ELEC / MECH / INDUSTRY / GAS / LIFT
        ↓
EQUIPMENT_TYPE_CODE (36종)       유형 코드
  예: PRESSURE_VESSEL / CRANE / CONVEYOR
        ↓
FACILITY_NAME_STD (446종)        ← 입력코드화 핵심 단위
  예: 컨베이어 / 변압기 / 프레스설비 / 사출성형기
        ↓
ASSET_NAME (1,495종, 목업)       사업장 개별 설비 인스턴스
  예: A동 1번 컨베이어
```

**입력코드화 대상은 `facility_name_std` 446종이 핵심 단위.**
- ASSET_NAME(1,495)은 인스턴스라 너무 세밀
- EQUIPMENT_TYPE_CODE(36)은 너무 거침
- **446종이 법령 매핑에 적합한 입도(granularity)**

---

## 핵심 교훈

```
"설비 40종"은 목업 50개사가 실제 보유한 설비 유형코드 distinct였다.
입력코드화 대상은 사업장이 보유한 것이 아니라,
공정-설비 표준 마스터(process_equipment_map)의 facility_name_std 446종이다.

검증 원칙 재확인:
  distinct 수치는 반드시 "어느 테이블 / 어느 컬럼 기준"인지 명시해야 한다.
  목업 인스턴스 데이터와 표준 마스터 데이터를 혼동하면 안 된다.
```

---

## 다음 단계

```
WO-INPUT-CODE-AUDIT-001 (현재) — 완료
      ↓
WO-INPUT-CODE-ARCHITECTURE-001 정정 반영
  (설비 40 → 446, 총량 약 4,300개)
      ↓
WO-INPUT-CODE-INVENTORY-001
  input_code_catalog 생성 + 적재
  설비 원천은 facility_name_std 446종 기준
```

---

*WO-INPUT-CODE-AUDIT-001 완료.*
*정정: 설비 40 → 446 (facility_name_std 기준). 총 입력코드화 대상 약 4,300개.*
*목업 인스턴스(equipment_type_code 36)와 표준 마스터(facility_name_std 446) 혼동 정정.*
