# INPUT SECTOR LAW REFERENCE TRACE V1
# (확인 전용 — 입력부의 섹터별 법령 참조 구조)

**작성일**: 2026-06-20
**목적**: 입력부가 섹터별 법령 데이터를 어디서·어떻게 참조하는지 확인만.
**금지 준수**: 수정/판정/원인분석 없음. 참조 지점·작동 방식 확인만.

---

## 발견한 섹터별 법령 참조 지점 (sector 컬럼 보유 테이블 중 입력 관련)

```
입력부와 섹터·법령을 잇는 핵심 테이블 3종 확인:

1. diagnosis_input_fields   — 섹터별 "무엇을 입력받는가" 정의
2. runtime_metadata_resolution — 법령을 5W1H로 해석한 결과(섹터 보유)
3. (factory_features)       — 섹터별 메뉴/기능 노출 정의 (입력 UI 측)
```

---

## 1. diagnosis_input_fields (섹터별 입력 필드 정의)

```
섹터별 필드 수:
  BUILDING     51
  INDUSTRIAL   46
  CONSTRUCTION 31

건설(CONSTRUCTION) 입력 필드 실제 내용:
  [기본정보] project_address, project_amount, worker_count,
            construction_type, subcontractor_count
  [공정]    process_list (table)
  [위험시설] has_tower_crane, has_confined_space, has_asbestos_demo,
            has_blasting, has_diving
  [협력업체] subcontractor (table)

구조 컬럼: field_code / field_group / field_type / auto_source /
          input_options / unknown_handler

★ auto_source = 전부 null.
  → 이 테이블은 "섹터별로 무엇을 입력받을지(UI 필드)"를 정의한다.
    그러나 그 입력이 어느 법령조건(binding_field/draft_slot)으로
    연결되는지는 이 테이블에 정의돼 있지 않다 (auto_source null).
```

---

## 2. runtime_metadata_resolution (법령 5W1H 해석, 섹터 보유)

```
구조: runtime_name, source_law_name, source_article_no, sector,
      who/when/how/evidence/condition/schedule (각 _value/_source/_status),
      overall_completeness

섹터별 분포:
  sector='ALL'   3388건 / 법령 68종 / condition_value 0건
  sector='공통'    4건 / 법령 2종 / condition 4건
  sector='제조'    2건 / 법령 2종 / condition 2건
  sector='건설'    1건 / 법령 1종 / condition 1건

★ 관찰:
  - ALL 3388건은 task_candidate(3388건)와 같은 규모.
    = 런타임 의무별 5W1H 메타데이터. 단 condition_value는 0건.
  - 섹터 라벨이 명시된 행(공통/제조/건설)은 극소수(4/2/1건)뿐.
  - 건설 섹터 명시 행 = 1건.
```

---

## 3. 입력 → 법령 연결의 작동 방식 (확인된 사실)

```
[입력 UI 층]
  diagnosis_input_fields:
    섹터별 입력 필드 정의 (건설 31개 등).
    field_code로 입력 항목 식별. auto_source=null.
    → "무엇을 입력받는가"만 정의. 법령 연결 없음.

[법령 해석 층]
  runtime_metadata_resolution:
    법령을 5W1H로 해석. sector 라벨 보유.
    그러나 섹터 명시 행은 극소수, condition 대부분 비어 있음.

[엔진 평가 층] (직전 WO 확인)
  draft_slot.binding_field (11종) ← FIELD_MAP(11종) 매칭
    → facility_applicability → task_candidate
    건설 전용 binding_field = 0건.

★ 연결 상태:
  diagnosis_input_fields(입력 필드 field_code: has_tower_crane,
    has_blasting, process_list 등)와
  draft_slot.binding_field(평가 키: equipment_type, area_size 등)는
  서로 다른 네임스페이스다.

  - 입력 필드는 field_code로 식별 (has_tower_crane, has_blasting…)
  - 평가는 binding_field로 매칭 (equipment_type, power_capacity…)
  - 둘을 잇는 매핑(auto_source 또는 별도 매핑 테이블)이
    diagnosis_input_fields에 채워져 있지 않다 (auto_source null).
```

---

## 작동 방식 요약 (확인된 것만, 판정 아님)

```
1. 입력부는 섹터별 법령 데이터를 "참조"한다:
   - diagnosis_input_fields가 섹터별로 입력 필드를 정의 (건설 31개).
   - 이 필드 정의 자체가 "섹터별 법령이 요구하는 입력"을 반영한 것으로 보임
     (위험시설: 타워크레인/석면/발파/잠수 = 건설 법령 관심사).

2. 그러나 입력값 → 엔진 평가의 자동 연결은 비어 있다:
   - diagnosis_input_fields.auto_source = null (입력→소스 매핑 없음).
   - 입력 field_code(has_tower_crane)와 평가 binding_field(equipment_type)가
     다른 네임스페이스이고, 잇는 매핑이 채워져 있지 않음.
   - draft_slot에 건설 binding_field 0건 (직전 WO 확인).

= 입력부는 "섹터별로 무엇을 받을지"는 법령 기반으로 정의돼 있으나,
  그 입력이 실제 평가 엔진(Compiler Core)으로 자동 전달되는
  매핑 경로는 현재 연결돼 있지 않다.
```

---

## 참조 지점 한눈에

| 층 | 테이블 | 섹터 인식 | 법령 참조 | 입력→평가 연결 |
|---|---|---|---|---|
| 입력 필드 정의 | diagnosis_input_fields | O (B51/I46/C31) | 필드가 법령 관심사 반영 | auto_source=null |
| 법령 5W1H 해석 | runtime_metadata_resolution | O (ALL/공통/제조/건설) | source_law_name 68종 | condition 대부분 빔 |
| 엔진 평가 | draft_slot + FIELD_MAP | binding_field로 | part/article 연결 | 건설 binding_field 0 |

---

## 완료 (확인 전용)

```
입력부가 섹터별 법령을 참조하는 지점을 확인하였다:
  diagnosis_input_fields (섹터별 입력 필드, 건설 31개)가
  섹터별 법령 관심사를 반영해 입력 항목을 정의한다.

작동 방식:
  입력 필드 정의(diagnosis_input_fields)와
  엔진 평가(draft_slot/FIELD_MAP)는 서로 다른 네임스페이스이며,
  둘을 잇는 매핑(auto_source)이 비어 있어
  입력값이 평가로 자동 전달되는 경로는 현재 연결돼 있지 않다.

수정/판정/원인분석은 수행하지 않았다. 확인만.
```
