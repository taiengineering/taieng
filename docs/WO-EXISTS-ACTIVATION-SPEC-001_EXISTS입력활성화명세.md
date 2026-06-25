# WO-EXISTS-ACTIVATION-SPEC-001
# EXISTS 입력 활성화 명세 (무엇을 물으면 Coverage가 얼마나 오르나)

**작성일:** 2026-06-25 | **상태:** 완료 (명세 — ① Applicability 내부, 읽기 전용)
**선행:** WO-COVERAGE-GAP-001 (ROI 1순위 = EXISTS)
**헌법:** WO-ARCHITECTURE-FREEZE-001 준수

## Boundary Check (헌법 TASK-007)

```
Applicability 내부 작업인가?    YES  (EXISTS 입력 역산)
Boundary 변경 필요한가?         NO
Data Contract 변경 필요한가?    NO
Breaking Change인가?            NO
→ 전부 통과.
```

---

## 결론 먼저 (파레토)

```
CONFIRMED EXISTS = 28개 has_* 입력, 누적 507 의무.

상위 10개 has_* 수집 → 355 의무 (70%)
상위 12개 has_* 수집 → 392 의무 (77%)

→ 28개 중 10개만 물어도 EXISTS 의무의 70%가 살아난다.
→ Coverage 영향: 산안법 4법 20.4% → 추정 ~31% (기준규칙 EXISTS 활성).
```

---

## TASK-001/002: input_field별 ROI (전체 28개)

| 순위 | has_* | 의무수 | 누적 | sector |
|---|---|---|---|---|
| 1 | has_confined_space | 68 | 68 | I,C,B |
| 2 | has_hazardous_material | 68 | 136 | I |
| 3 | has_dust_work | 37 | 173 | I |
| 4 | has_chemical_substance | 32 | 205 | I |
| 5 | has_asbestos_demo | 30 | 235 | B,C |
| 6 | has_diving | 27 | 262 | C |
| 7 | has_crane | 25 | 287 | I |
| 8 | has_excavation | 23 | 310 | C |
| 9 | has_asbestos | 23 | 333 | B |
| 10 | has_scaffold | 22 | **355** | C |
| 11 | has_high_place_work | 19 | 374 | I |
| 12 | has_welding | 18 | **392** | I |
| 13 | has_pile_work | 17 | 409 | C |
| 14 | has_elevator | 14 | 423 | I |
| 15 | has_radiation | 12 | 435 | I |
| 16 | has_boiler | 8 | 443 | B,I |
| 17 | has_tower_crane | 7 | 450 | C |
| 18 | has_high_pressure_gas | 7 | 457 | C,I |
| 19 | has_forklift | 7 | 464 | I |
| 20 | has_conveyor | 7 | 471 | I |
| 21~28 | (pressure_vessel/grinding/demolition/blasting/press/rolling/gondola/injection) | 36 | 507 | - |

---

## TASK-003: 입력 질문 문구 (입력표준 field_name 그대로)

```
★ 질문 문구는 diagnosis_input_fields에 이미 정의됨.
  Cursor는 새로 만들지 말고 field_name을 그대로 노출.

has_confined_space     → "밀폐공간 유무"
has_hazardous_material → "유해물질 취급"
has_dust_work          → "분진작업 유무"
has_chemical_substance → "화학물질 취급"
has_asbestos_demo      → "석면해체 유무"
has_diving             → "잠수작업 유무"
has_crane              → "크레인/호이스트 유무"
has_excavation         → "굴착작업 유무"
has_asbestos           → "석면 사용 여부" (help: 건축연도 2009년 이전 자동경고)
has_scaffold           → "비계 사용 유무"
has_high_place_work    → "고소작업 유무" (help: 2m 이상)
has_welding            → "용접 공정 유무"
has_pile_work          → "항타/항발작업 유무"
has_elevator           → "승강기(화물) 유무"
```

---

## TASK-004: 입력 그룹화 (field_group 기준)

```
위험물:   has_hazardous_material, has_chemical_substance,
          has_dust_work, has_confined_space(I)
공정:     has_welding, has_excavation, has_high_place_work, has_pile_work
설비:     has_crane, has_elevator, has_forklift, has_conveyor
위험시설: has_confined_space(C), has_diving, has_scaffold, has_asbestos_demo
석면:     has_asbestos
```

---

## TASK-005: MVP 입력세트 (sector별 — 핵심)

```
★ sector마다 ROI 상위가 다르다. sector 선택 후 해당 세트만 노출.

[INDUSTRIAL] 7개 질문 → 약 230 의무
  1. 유해물질 취급          (has_hazardous_material)  68
  2. 분진작업 유무          (has_dust_work)           37
  3. 화학물질 취급          (has_chemical_substance)  32
  4. 밀폐공간 유무          (has_confined_space)      26
  5. 크레인/호이스트 유무   (has_crane)               25
  6. 고소작업 유무          (has_high_place_work)     19
  7. 용접 공정 유무         (has_welding)             18

[CONSTRUCTION] 7개 질문 → 약 145 의무
  1. 잠수작업 유무          (has_diving)              27
  2. 밀폐공간 유무          (has_confined_space)      26
  3. 석면해체 유무          (has_asbestos_demo)       23
  4. 굴착작업 유무          (has_excavation)          23
  5. 비계 사용 유무         (has_scaffold)            22
  6. 항타/항발작업 유무     (has_pile_work)           17
  7. 타워크레인 유무        (has_tower_crane)          7

[BUILDING] 3개 질문 → 약 46 의무
  1. 석면 사용 여부         (has_asbestos)            23
  2. 밀폐공간 유무          (has_confined_space)      16
  3. 석면해체 유무          (has_asbestos_demo)        7

→ INDUSTRIAL 7문항이 단일 sector 최대 ROI (230 의무).
→ 전 sector 공통 10문항 묶으면 355 의무 (70%).
```

---

## TASK-006: Cursor 인계 명세

```
Cursor가 할 일 (입력단 — Cursor 영역):

1. UI 노출
   - diagnosis_input_fields WHERE field_type='boolean'
     AND field_code IN (위 sector별 MVP 세트)
   - sector 선택 후 해당 세트만 노출 (토스 원칙: 필요한 것만)
   - field_name을 질문 문구로, help_text를 보조설명으로

2. 응답 저장 (Data Contract 무변경 — 기존 경로)
   - has_* 응답을 facility_profiles에 저장
     OR Input Contract Builder가 읽는 위치에
   - field_code 그대로 사용 (has_welding 등, 변환 없음)
   - 주의: 현재 facility_profiles.profile_snapshot엔 has_* 없음
     → 이 저장 경로를 새로 연결하는 게 핵심 작업

3. 필드명 변환 주의 (CASE-B, WO-EXISTS-INPUT-TRACE-001)
   - public_diagnosis_requests는 has_gas/has_hazardous 약식명 사용
   - generator는 has_high_pressure_gas/has_hazardous_material
   - 저장 시 정식 field_code로 통일

금지 (헌법):
  - 새 Trigger/Mapping/Harvest 생성 금지
  - Check Engine 수정 금지
  - Data Contract 변경 금지 (has_*는 기존 입력표준)
```

---

## 핵심 발견

### 발견 1: 파레토 — 10개로 70%

```
28개 has_* 중 상위 10개가 355/507 의무(70%).
→ 입력 28개 다 안 물어도 됨.
→ MVP 10문항으로 EXISTS 대부분 활성.
```

### 발견 2: sector별 입력세트가 다르다

```
INDUSTRIAL: 유해물질/분진/화학 (물질 중심)
CONSTRUCTION: 잠수/굴착/비계/항타 (작업 중심)
BUILDING: 석면/밀폐공간 (소수)
→ sector 선택 후 해당 세트만 노출 = UX 최적 + ROI 최대.
→ INDUSTRIAL 7문항이 단일 최대(230 의무).
```

### 발견 3: 질문 문구는 이미 존재

```
diagnosis_input_fields.field_name이 질문 문구.
"밀폐공간 유무", "유해물질 취급" 등 14개 확인.
→ Cursor는 새로 작성 불필요. 그대로 노출.
→ help_text도 있음(석면 2009년, 고소 2m).
```

### 발견 4: 저장 경로가 유일한 관문

```
입력표준/질문문구/매핑 전부 준비됨.
유일한 미연결 = has_* 응답 저장 위치.
  facility_profiles.profile_snapshot엔 has_* 없음.
→ Cursor 핵심 작업 = 이 저장 경로 1개 연결.
→ 연결되면 즉시 Coverage 20%→31% 점프.
```

---

## 성공 기준 답변

```
상위 10개 has_* 입력만 수집해도 몇 개 obligation이
추가로 살아나는가?

✅ 355개 (전체 EXISTS 507의 70%).
  상위 12개면 392개(77%).
  INDUSTRIAL 단독 7문항 → 230개.

Coverage 영향:
  산안법 4법 20.4% → 추정 ~31%
  (기준규칙 EXISTS 의무 대거 활성).
```

---

## Coverage 추적 갱신

```
현재: 20.4% (444/2,174)
EXISTS 상위10 활성 시: ~31% (+~240 distinct clause)
  → 다음 WO에서 실측 갱신.
```

---

## 다음 단계

```
이 명세 → Cursor 인계 (입력단 구현):
  CURSOR-TASK-002 (예정)
    1. sector별 MVP 입력세트 UI 노출
    2. has_* 저장 경로 연결 (facility_profiles)
    3. 실제 factory 진단 → obligation_instance 증가 실측

Claude(기획창) 후속:
  - 저장 연결 후 Coverage 재측정 (WO-COVERAGE-GAP-002)
  - EXISTS 활성 실측치로 baseline 갱신
```

---

*WO-EXISTS-ACTIVATION-SPEC-001 완료. 입력 활성화 명세 — ① 내부.*
*핵심: 상위10 has_* = 355 의무(70%). sector별 세트 분리. 질문문구 기존재.*
*유일 관문 = has_* 저장경로 연결(Cursor). Boundary/Contract 무변경.*
