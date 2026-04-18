# FN-FIX-8: 건축물대장 자동채움 필드 매핑 수정

**긴급도**: 🔴 즉시  
**대상**: `nexas/free-diagnosis.html` → `fetchBuildingRegister()` 함수

## 원인

BE `/building-register/search` 응답 키와 FE field_code가 불일치.  
`floor_count`만 일치하여 층수만 자동입력됨.

## 수정

`fetchBuildingRegister()` 함수 내 `fieldMap` 수정:

```javascript
// 현재 (매칭 안 됨):
const fieldMap = {
  total_floor_area: d.total_floor_area,
  floor_count: d.floor_count,
  basement_count: d.basement_count,
  building_use_type: d.building_use_type,
  built_year: d.built_year,
  main_structure: d.main_structure
};

// 수정 (BE 응답 키에 맞춤):
const fieldMap = {
  total_floor_area:  d.building_area,                               // BE: totArea
  floor_count:       d.floor_count,                                  // BE: grndFlrCnt ✅
  basement_count:    d.underground_floor_count,                      // BE: ugrndFlrCnt
  building_use_type: d.main_purpose_name || d.building_use_code,     // BE: mainPurpsCdNm
  built_year:        d.completion_year,                               // BE: useAprDay[:4]
  main_structure:    null                                             // BE에 해당 키 없음
};
```

또한 `fetchPriceTier()` 호출도 BE 키로 수정:
```javascript
// 현재:
if (d.total_floor_area) fetchPriceTier(d.total_floor_area, diagPrefix);

// 수정:
if (d.building_area) fetchPriceTier(d.building_area, diagPrefix);
```

## 기대 결과

주소 선택 후 자동채움:
- 연면적 (building_area → total_floor_area 폼)
- 지상 층수 (floor_count → floor_count 폼) ← 이미 작동
- 지하 층수 (underground_floor_count → basement_count 폼)
- 건물 용도 (main_purpose_name → building_use_type 폼)
- 건축연도 (completion_year → built_year 폼)
