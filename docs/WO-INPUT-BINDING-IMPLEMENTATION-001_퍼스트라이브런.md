# WO-INPUT-BINDING-IMPLEMENTATION-001
# First Live Run — 실제 Factory 데이터로 의무 생성

**작성일:** 2026-06-24 | **상태:** 완료 (실제 데이터 실행)
**선행:** WO-INPUT-BINDING-ARCHITECTURE-001
**주의:** 새 매핑/Trigger/Harvest/Review 없음. 실제 연결 구현·실행만.
**목적:** 실제 facility_profiles → Contract → generator → obligation_instance 실행.

> 가정 입력이 아니라 실제 Factory 데이터로 첫 실행. 결과를 있는 그대로 기록.

---

## 결론 먼저 (정직한 실측)

```
실제 factory 데이터로 generator 실행 결과: obligation_instance 0건.

이유 (가정 없이 실측):
  실제 facility_profiles에 has_* 입력이 없음.
  → EXISTS 293 규칙이 대기 중이나 발동 0.
  → UNIVERSAL CONFIRMED 0 (전부 HARVESTED) → baseline 0.

→ 규칙(generator)은 살아있다. 입력(has_*)이 비어있다.
→ 이전 75건은 "가정 입력" 결과였고, 실제 입력은 0.
→ 진짜 갭은 "엔진 연결"이 아니라 "EXISTS 입력 미수집"이었다.
```

---

## TASK-001: 실제 facility_profiles 선택

```
선택: factory_id = e9c56af6-5de7-487d-bd2e-0d452291a562
  sector: INDUSTRIAL ✅
  ksic_code: C28 ✅
  입력값 존재: ✅ (workforce/building/metrics)
```

---

## TASK-003: has_* 저장 방식 검증 (구현 직전 핵심)

```
질문이었던 것: has_*가 어떻게 저장되는가?
  A: {"has_welding": true}      (값)
  B: ["has_welding"]            (필드 목록)
  C: 다른 구조

답: C — has_*는 아예 저장되지 않는다.

실측 구조 (profile_snapshot, jsonb):
{
  "sector": "INDUSTRIAL",
  "ksic_code": "C28",
  "workforce": {
    "total_workers":   {"state":"PRESENT","value":280,"provenance":"INPUT"},
    "regular_workers": {"state":"PRESENT","value":280,...},
    "subcontract_workers": {"state":"PRESENT","value":0,...}
  },
  "building": {
    "floor_area":  {"state":"PRESENT","value":12500,...},
    "floor_count": {"state":"PRESENT","value":3,...},
    "use_code":    {"state":"UNKNOWN","value":null,...}
  },
  "metrics": {
    "electrical_kw": {"state":"PRESENT","value":1400,...},
    "gas_capacity":  {"state":"PRESENT","value":500,...},
    "construction_amount": {"state":"UNKNOWN",...}
  },
  "provenance": {"input_fields":[...9개...]}
}

input_fields (text[] ARRAY) = 입력된 "필드 목록":
  ["sector","ksic_code","workforce.regular_workers",
   "workforce.subcontract_workers","workforce.total_workers",
   "building.floor_area","building.floor_count",
   "metrics.electrical_kw","metrics.gas_capacity"]

→ SCOPE(sector/ksic) + THRESHOLD(숫자) 만 수집됨.
→ EXISTS(has_welding 등) 작업·설비 입력은 구조 자체에 없음.
```

---

## TASK-002: Generator Input Contract (실제 데이터)

```json
{
  "factory_id": "e9c56af6-5de7-487d-bd2e-0d452291a562",
  "sector": "INDUSTRIAL",
  "ksic_code": "C28",

  "worker_count": 280,        // total_workers.value
  "regular_workers": 280,
  "building_area": 12500,     // floor_area.value
  "floor_count": 3,
  "electrical_kw": 1400,
  "gas_capacity": 500

  // has_* : 없음 (profile_snapshot에 미존재)
}
```

```
가정 금지 준수: has_*를 임의로 true 넣지 않음.
실제 DB에 없으므로 Contract에도 없음.
```

---

## TASK-004~005: generator 실행 + 결과 검증

```
실행: factory e9c56af6, 실제 has_* = 빈 배열

| 항목 | 값 |
|---|---|
| factory_id | e9c56af6... |
| 입력필드 수 (실제) | 9 (sector/ksic/숫자 7) |
| 활성 has_* Trigger 수 | 0 |
| EXISTS 대기 규칙 (미발동) | 293 |
| UNIVERSAL CONFIRMED | 0 |
| 생성 obligation 수 | 0 |

→ 실제 데이터로 0건. 가정(75건)과 정반대.
```

---

## TASK-006: 첫 운영 시나리오 (실제 흐름 + 갭)

```
설계상 흐름:
  사용자 입력 → diagnosis_session → facility_profiles
  → Input Contract → generator → obligation_instance → Check Engine

실제 흐름 (현재):
  사용자 입력 → facility_profiles
    [수집됨]   sector, ksic, workforce, building, metrics
    [미수집]   has_welding/has_crane 등 작업·설비 EXISTS
  → Input Contract (SCOPE+THRESHOLD만)
  → generator
    EXISTS: has_* 0개 → 발동 0
    UNIVERSAL: CONFIRMED 0 → 0
    THRESHOLD: cmc 거의 없음 → ~0
  → obligation_instance 0건
  → Check Engine (입력 없음)

→ 라인은 연결됐으나, 입력 부족으로 출력 0.
```

---

## 핵심 발견

### 발견 1: 진짜 갭은 "EXISTS 입력 미수집"이었다

```
이전 가정: 엔진 연결만 하면 됨.
실측: 연결돼도 has_* 입력이 없어 0건.

→ facility_profiles는 SCOPE+THRESHOLD만 수집.
→ 작업/설비 존재(has_welding 등)는 입력 단계에 없음.
→ 입력표준(diagnosis_input_fields)엔 has_* 정의됨(스키마).
→ 그러나 실제 수집 플로우가 has_*를 안 채움.
```

### 발견 2: 입력표준 ≠ 실제 수집

```
ARCHITECTURE-001: "has_* 28개 입력표준에 100% 존재".
IMPLEMENTATION-001: "실제 facility_profiles엔 has_* 0개".

→ 입력표준(필드 정의)은 있다.
→ 실제 수집된 값(profile_snapshot)엔 없다.
→ 정의와 수집의 분리. 둘 다 사실.
```

### 발견 3: generator는 정상, 입력 파이프가 미완

```
generator 로직 정상 (가정 입력 75건 생성 확인됨).
입력 파이프(UI→facility_profiles)가 has_* 미수집.

→ 고칠 곳은 generator가 아니라 입력 수집.
→ 진단 UI/플로우가 작업·설비 질문을 해야 함.
→ 또는 다른 소스(공정/설비 등록)에서 has_* 유도.
```

### 발견 4: profile_snapshot이 풍부한 THRESHOLD 소스

```
실제 데이터: worker 280, floor_area 12500, electrical_kw 1400, gas_capacity 500.
→ THRESHOLD 판정 재료는 충분.
→ 단 cmc에 THRESHOLD 규칙이 거의 없음(수확 2건).
→ THRESHOLD 매핑 보강 시 이 숫자들로 즉시 의무 생성 가능.
  (예: worker 280 ≥ 50 → 안전관리자 선임)
```

---

## 성공 기준 답변

```
가정 입력이 아니라 실제 Factory 데이터로
첫 obligation_instance가 생성됐는가?

결과: 0건 생성.

이것은 실패가 아니라 정확한 진단:
  - generator 라인은 실제로 연결됨 (실행됨, 에러 없음)
  - 실제 입력에 has_*가 없어 발동 0
  - 진짜 갭 = EXISTS 입력 수집 (엔진 아님)

→ First Live Run의 가치: 가정(75) vs 실제(0)의 간극 확인.
→ 다음 작업 방향이 명확해짐.
```

---

## 다음 단계 (실측 기반 우선순위)

```
실제 갭이 드러났으므로 우선순위 재정렬:

1순위: EXISTS 입력 수집 경로 확인 (읽기 전용)
  - 진단 UI가 has_welding 등을 묻는가?
  - 묻는다면 어디 저장되는가? (profile_snapshot 아닌 다른 곳?)
  - diagnosis_session.input_snapshot에 들어오는가?
  → 입력이 어디로 가는지 추적

2순위: THRESHOLD 매핑 보강
  - profile_snapshot 숫자는 이미 풍부 (280/12500/1400/500)
  - cmc에 THRESHOLD 규칙 추가하면 즉시 의무 생성
  - worker_count ≥ 50 → 안전관리자 등

3순위: UNIVERSAL 310 CONFIRMED 승격
  - sector만으로 baseline 생성 (has_* 불필요)
  - 현재 INDUSTRIAL이면 즉시 226 baseline 가능

→ has_* 없이도 2(THRESHOLD)+3(UNIVERSAL)으로
  의미있는 진단 가능. EXISTS는 입력수집 후.
```

---

## 현재 위치 (수정)

```
매핑 완료 / 생성기 완료 / 바인딩 규격 완료
  ↓
First Live Run 완료 ← 지금 (결과: 입력 갭 발견)
  ↓
입력 갭 해소 (EXISTS 수집 OR UNIVERSAL/THRESHOLD 우회)
  ↓
실제 의무 생성 (>0건)
  ↓
Check Engine
```

---

*WO-INPUT-BINDING-IMPLEMENTATION-001 완료. 실제 데이터 실행.*
*결과: obligation_instance 0건 — has_* 미수집이 진짜 갭.*
*핵심: generator 정상, 입력 파이프 미완. profile_snapshot은 SCOPE+THRESHOLD만.*
*가정(75) vs 실제(0) 간극 확인. 다음은 입력수집 OR UNIVERSAL/THRESHOLD 우회.*
