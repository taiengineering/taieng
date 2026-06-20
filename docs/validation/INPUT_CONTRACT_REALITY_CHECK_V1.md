# INPUT CONTRACT REALITY CHECK V1
# WO-INPUT-CONTRACT-REALITY-CHECK-001

**작성일**: 2026-06-20
**목적**: "사용자가 실제 입력하는 데이터 전체가 무엇인가" 확인.
  (≠ "현재 ACTIVE 조건이 뭘 쓰는가")
**금지 준수**: 결론/개선안/원인분석 없음. 입력계약 목록 + 엔진사용 분리만.

---

## 직전 WO 정정 (중요)

```
직전 WO(VR_INPUT_SPACE_MAP)에서 나는
  "엔진 입력 = KSIC + 근로자수 2개뿐"이라 했다.

이번 실측으로 그것이 확대해석이었음이 드러남:
  그건 "현재 ACTIVE applicability_conditions가 쓰는 차원"일 뿐,
  "사용자가 입력하는 데이터 전체"가 아니었다.

실제 사용자 입력공간은 훨씬 넓다 (아래 실측).
```

---

## 실측: 사용자 입력 수집 테이블 + 데이터 보유량

```
입력 차원별 실제 데이터(행 수):
  process_equipment_map      187,319   ← 공정-설비 매핑
  kosha_safety_materials      30,547   ← 물질(화학/안전자재)
  task_candidate               3,388   ← 작업 후보
  equipment_assets             1,285   ← 설비 자산
  runtime_task                   339   ← 작업
  runtime_facility_equipment     150   ← 시설 설비
  runtime_facility_hazard        100   ← 위험원
  factory_features                28   ← 시설 특성
  factory_process                 10   ← 사업장 공정
  facility_profiles                2   ← 시설 프로파일
  buildings                        1   ← 건축물
  facility_condition               0   ← 시설 조건(빈 구조)

→ 시설/설비/공정/작업/물질/위험원/건축물 입력이
  전부 수집 구조로 존재하고 대부분 실제 데이터 보유.
```

---

## 수집하는 입력항목 (컬럼 실측)

```
equipment_assets (설비) — 풍부:
  equipment_type_code, equipment_category,
  capacity_value, capacity_unit,   ← 용량 (수치 metric 후보)
  install_year, manufacture_year, manufacturer,
  is_legal_target, legal_status,   ← 법적대상 여부
  last_inspection_date, next_inspection_date,
  ksic_code, factory_process_id, building_id, floor_no

runtime_facility_hazard (위험원):
  hazard_type, hazard_name, quantity, status   ← 위험원 종류+수량

factory_process (공정):
  process_lv1~lv4, process_path, is_primary, legal_status

factory_features (시설 특성):
  feature_code, feature_name, sector, menu_path
```

---

## 입력항목 매핑표 (ICC)

| 입력항목 | 수집됨 | 수집 위치 | 현재 ACTIVE 엔진 사용 |
|---|---|---|---|
| 근로자수 | YES | factories/worker | **YES** (EMPLOYEE_COUNT) |
| KSIC(업종) | YES | factories/process | **YES** (scope) |
| 시설 | YES | facility_profiles, factory_features | NO* |
| 설비 | YES | equipment_assets (1,285) | NO* |
| 공정 | YES | factory_process, process_equipment_map (187K) | NO* |
| 작업 | YES | runtime_task, task_candidate (3,388) | NO* |
| 물질 | YES | kosha_safety_materials (30,547) | NO* |
| 위험원 | YES | runtime_facility_hazard (100) | NO* |
| 건축물 | YES | buildings | NO* (별도 sector) |
| 설비용량 | YES | equipment_assets.capacity_value | NO* |
| 위험원수량 | YES | runtime_facility_hazard.quantity | NO* |

```
* NO = 현재 ACTIVE applicability_conditions(14건)가
  판정 metric으로 안 씀 (직전 WO 실측).
  단 "엔진이 영영 못 쓴다"가 아니라 "현재 ACTIVE 조건이 안 쓴다".
  (이 구분이 직전 WO에서 내가 놓친 것)
```

---

## 분리 결과 (ICC-03, ICC-04)

```
[수집됨 + 현재 엔진 사용] (COVERED):
  근로자수, KSIC — 2개

[수집됨 + 현재 엔진 미사용] (COLLECTED_NOT_USED):
  시설, 설비, 공정, 작업, 물질, 위험원, 건축물,
  설비용량, 위험원수량 — 9개+
  → 사용자는 입력하는데(또는 마스터로 보유) 현재 ACTIVE
    판정 조건이 이 차원을 안 씀.

[미수집]:
  현재까지 확인된 범위에선 주요 안전 입력항목 대부분 수집됨.
  (에너지/저장/운반은 별도 확인 필요하나 equipment_category로
   포섭됐을 가능성 — 이번 단정 안 함)
```

---

## 이것이 VR 재현율에 의미하는 것 (사실만)

```
직전 WO 결론("VR이 17% 흔든다")은 보류해야 한다.

이유:
  - VR이 현재 흔드는 것 = KSIC + 근로자수 2차원 (맞음)
  - 그러나 "현실 사업장 입력"은 위 표처럼 설비/공정/물질/
    위험원/용량까지 포함 = 훨씬 넓은 공간.
  - 그리고 그 넓은 공간을 "엔진이 영영 안 쓴다"가 아니라
    "현재 ACTIVE 조건이 안 쓴다"이다.

→ 따라서 진짜 질문은 두 개로 갈린다:
  Q-A. VR이 현실 입력공간(설비/물질/위험원...)을 재현하는가?
       → 현재 NO (VR은 2차원만 생성)
  Q-B. 엔진이 그 입력공간을 판정에 쓰는가?
       → 현재 ACTIVE 조건은 NO (근로자수만)

  두 질문은 다르다. 직전엔 이 둘을 섞어
  "VR이 17%"라고 단정했다 = 성급했다.

  ※ 어느 쪽도 이번에 결론 안 냄 (ICC-05 준수).
```

---

## 성공 기준 점검

```
ICC-01 사용자 입력 전체목록 확보   → ✅ (11+ 항목)
ICC-02 실제 수집 데이터 확인       → ✅ (행 수 실측)
ICC-03 엔진 사용 여부 분리         → ✅ (COVERED 2 / COLLECTED_NOT_USED 9+)
ICC-04 미사용 데이터 식별          → ✅ (설비/공정/물질/위험원...)
ICC-05 결론 금지                  → ✅ (재현율 단정 보류)
ICC-06 개선안 금지                → ✅
```

---

## 원칙 준수

```
"현재 읽은 테이블 = 엔진 전체" 확대해석 안 함 ✅ (직전 오류 정정)
결론/개선안/원인분석 안 함 ✅
입력계약 전체 목록 + 엔진사용 분리만 ✅
```

---

## 결론

```
"사용자는 무엇을 입력하고 있는가"에 대한 답:

  근로자수, KSIC 뿐만 아니라
  시설/설비/공정/작업/물질/위험원/건축물/설비용량/위험원수량까지
  광범위하게 입력·수집하고 있다.
  (process_equipment_map 187K, kosha_safety_materials 30K 등 대량)

직전 WO 정정:
  "엔진 입력 = KSIC + 근로자수 2개"는
  "현재 ACTIVE 조건이 쓰는 2개"였지, 입력계약 전체가 아니었다.

따라서:
  COVERED(엔진 사용) = 2개 (KSIC, 근로자수)
  COLLECTED_NOT_USED = 9개+ (설비/공정/물질/위험원...)

  "VR이 17% 흔든다"는 결론은 보류.
  현실 입력공간이 훨씬 넓고, VR 재현율과 엔진 사용률은
  별개 질문임이 드러났다. (둘 다 이번엔 결론 안 냄)
```
