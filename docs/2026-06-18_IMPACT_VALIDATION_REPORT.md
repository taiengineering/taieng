# IMPACT VALIDATION REPORT
# WO-IMPACT-VALIDATION-001

**작성일**: 2026-06-18  
**성격**: 검증 WO. 구현 없음.  
**목적**: 현재까지 나온 모든 측정값을 Distribution / Coverage / Impact로 분리

---

## 세 지표의 정의

| 지표 | 정의 | 계산식 |
|---|---|---|
| **Distribution** | 규칙 개수 분포 | 특정 유형 규칙 수 / 전체 규칙 수 |
| **Coverage** | 엔진이 커버하는 영역 | 조건 존재하는 sector / 전체 sector |
| **Impact** | 입력 ON/OFF 시 verdict 변화율 | (V1≠V0 사업장) / 전체 사업장 |

---

## Step 1~2. 모든 측정값 수집 및 분류

| 출처 | Metric | Value | **Type** | 계산식 |
|---|---|---|---|---|
| SIMULATION_V1 | EQUIPMENT | 42.4% | **Distribution** | equipment_type 규칙 209 / IF_SCOPE 481 |
| SIMULATION_V1 | UNRESOLVED | 27.4% | **Distribution** | binding=null 규칙 135 / 481 |
| SIMULATION_V1 | FACILITY | 27.0% | **Distribution** | facility_type 규칙 133 / 481 |
| SIMULATION_V1 | PROCESS | 3.2% | **Distribution** | process_type 규칙 16 / 481 |
| SIMULATION_V1 | MATCH 비율 | 23.0% | **Distribution** | 가상평가 14000건 중 MATCH 3213 |
| SIMULATION_V1 | 규모별 평균 MATCH | 1.89~3.68 | **Distribution** | 사업장당 MATCH 의무 수 평균 |
| §8 | Track A False Positive | 93% | **Impact** | 화성 114건 중 MUST_NOT 106건 (실측) |
| §8 | V4 MUST 커버율 | 100% | **Coverage** | MUST 8건 중 8건 MATCH |
| §8 | INDUSTRIAL 조건 수 | 14건 | **Coverage** | applicability_conditions sector=INDUSTRIAL |
| §8 | CONSTRUCTION 조건 수 | 0건 | **Coverage** | 조건 없음 → 전체 UNKNOWN |
| §8 | BUILDING 조건 수 | 0건 | **Coverage** | 조건 없음 → 전체 UNKNOWN |

---

## Step 3. "Impact"라고 불렸던 수치 재검증

### SIMULATION_V1의 42.4% 등 — Impact 아님

```
계산식: COUNT(DISTINCT draft_id) GROUP BY binding_field
출처: draft_slot 테이블 (IF_SCOPE 섹션)
진실: 규칙이 그 필드를 조건으로 가진 빈도
→ Type = Distribution
→ verdict와 무관
```

### Track A 93% — 이것은 진짜 Impact

```
계산식: 화성 제2공장 MATCH_CANDIDATE 114건 중
        GOLDEN_CASE MUST_NOT 해당 106건
출처: facility_applicability (실제 평가 결과) × GOLDEN_CASE_HS2 v1.0
진실: Track A가 실제로 틀린 판정을 낸 비율
→ Type = Impact (verdict 수준 측정)
→ 단, 케이스 1개(화성) 기준이므로 표본 1
```

---

## Step 4. 현재 실제로 측정된 Impact / Coverage 목록

| 항목 | 값 | Type | 증명 상태 |
|---|---|---|---|
| CONSTRUCTION 미커버 | 100% | Coverage | ✅ 증명됨 (조건 0건, 전체 UNKNOWN 관찰) |
| BUILDING 미커버 | 100% | Coverage | ✅ 증명됨 (조건 0건, 전체 UNKNOWN 관찰) |
| INDUSTRIAL MUST 커버 | 100% | Coverage | ✅ 증명됨 (MUST 8/8) |
| Track A False Positive | 93% | Impact | ⚠️ 표본 1개 (화성 제2공장만) |

---

## Step 5. 현재 측정 불가능한 Impact 목록

| 항목 | 측정 가능 여부 | 이유 |
|---|---|---|
| Equipment Impact | ❌ 측정 불가 | equipment_type IF_SCOPE가 factories와 연결 안 됨 → ON/OFF 불가 |
| Process Impact | ❌ 측정 불가 | process_type 동일 |
| Boolean Impact | ❌ 측정 불가 | has_* 필드가 create_temp_factory에 저장 안 됨 |
| Facility Impact | ❌ 측정 불가 | facility_type IF_SCOPE 연결 안 됨 |

**핵심**: 이 네 가지는 "연결"이 선행되어야 Impact 측정 가능.  
그러나 연결 자체가 구현이므로 GPT 판단 전 금지.  
→ 따라서 현재는 Impact 측정 불가, Distribution만 알 수 있음.

---

## 결론

```
진짜로 측정된 것 (증명 가능):
  Coverage:
    INDUSTRIAL 100% 커버
    CONSTRUCTION 0% 커버
    BUILDING 0% 커버
  Impact (표본 1):
    Track A False Positive 93% (화성 제2공장)

분포일 뿐인 것 (Impact 아님):
  Equipment 42.4%, Facility 27.0%, Process 3.2%, UNRESOLVED 27.4%
  → 전부 Distribution

측정 불가한 것:
  Equipment/Process/Boolean/Facility의 실제 verdict Impact
  → 연결(구현)이 선행되어야 측정 가능
```

---

## 다음 단계에서 말할 수 있는 것 / 없는 것

```
말할 수 있다:
  "CONSTRUCTION은 100% 미커버다" (Coverage, 증명됨)
  "BUILDING은 100% 미커버다" (Coverage, 증명됨)

아직 말할 수 없다:
  "Equipment가 Process보다 중요하다" (Impact 미측정)
  "Boolean 연결이 급하다" (Impact 미측정)
```

---

## 교훈

```
수치 세 종류는 섞이면 안 된다:
  Distribution = 규칙이 몇 개인가
  Coverage     = 엔진이 어디까지 다루는가
  Impact       = 입력이 결과를 얼마나 바꾸는가

SIMULATION_REPORT_V1은 첫 번째를 세 번째로 읽었다.
```
