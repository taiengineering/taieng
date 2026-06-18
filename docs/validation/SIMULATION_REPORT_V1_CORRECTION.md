# SIMULATION_REPORT_V1 계산식 정정
# (Impact Ranking 자체 검증 결과)

**작성일**: 2026-06-18  
**성격**: 자체 정정. SIMULATION_REPORT_V1의 Impact Ranking 해석 오류 수정.

---

## 결론 먼저

```
SIMULATION_REPORT_V1의 "Equipment 42.4% → Priority HIGH" 판정은 철회한다.
42.4%는 규칙 개수 분포(rule distribution)이지
판정 영향도(verdict impact)가 아니다.
```

---

## GPT 5개 질문에 대한 답

### 질문 1. 42.4%는 정확히 무엇의 42.4%인가

**답: 후보 A (규칙 개수 비율)**

실행한 쿼리:
```sql
SELECT scope_class, COUNT(DISTINCT draft_id)
FROM draft_slot WHERE section='IF_SCOPE'
GROUP BY scope_class
```

정확한 수치:
```
equipment_type 규칙:  209건
facility_type 규칙:   133건
process_type 규칙:    16건
UNRESOLVED 규칙:      135건
전체 IF_SCOPE draft:  481건

209 / 481 = 43.5% (UNRESOLVED 포함 분모 계산시 42.4%)
```

→ 이것은 "법령이 equipment_type을 조건으로 가진 빈도"일 뿐,  
→ "equipment 입력이 사업장 verdict를 바꾸는 비율"이 아니다.

---

### 질문 2. UNRESOLVED 27.4%는 무엇인가

**답: binding_field=null 규칙 건수 비율**

135 / 481 = 27.4%.  
판정 영향도가 아니다. 단순히 "연결점 생성에 실패한 규칙이 전체 IF_SCOPE의 27.4%"라는 뜻.

---

### 질문 3. 분포인가 영향도인가

**답: 규칙 분포(rule distribution)을 측정한 것이다.**

```
현재 측정됨:  규칙 분포
  = draft_slot에 어떤 binding_field가 몇 건인가

측정 안 됨:  판정 영향도
  = 이 규칙들이 실제 사업장 verdict를 몇 % 바꾸는가
```

두 지표는 완전히 다르다. SIMULATION_REPORT_V1은 이 둘을 혼용했다.

---

### 질문 4. 현재 결과로 Priority HIGH 판정 가능한가

**답: 아니다. 증명되지 않았다.**

```
규칙 수가 많다 ≠ 판정 영향도가 크다

예시 반례:
  equipment_type 규칙이 209건이어도
  그 209건이 상시근로자 50인 조건과 중복되면
  equipment 입력이 없어도 이미 인원 조건으로 MATCH될 수 있음
  → equipment 제거 시 verdict 변화 0%일 수도 있음
```

따라서 "Equipment가 Process보다 13배 중요"는 현재 증명되지 않은 주장이다.  
SIMULATION_REPORT_V1의 해당 문장을 철회한다.

---

### 질문 5. 실제 영향도 측정에 필요한 실험

**답: ON/OFF 차등 실험(ablation)이 필요하다.**

```
실제 영향도 측정 설계:

1. 가상 사업장 N개 생성 (equipment 속성 포함)

2. 두 번 평가:
   (a) equipment 입력 OFF → verdict 집합 V0
   (b) equipment 입력 ON  → verdict 집합 V1

3. verdict 변화율 = (V1 ≠ V0인 사업장 수) / 전체

이것이 진짜 Impact.
현재는 (2) 단계가 불가능:
  equipment_type IF_SCOPE 조건이 factories 컬럼과 연결 안 됨
  → ON/OFF 자체가 아직 불가
  → 그래서 현재는 "규칙 분포"만 측정 가능했던 것
```

---

## 정정된 결론

```
SIMULATION_REPORT_V1이 실제로 증명한 것:
  ✅ 가상 사업장 1000개 자동 평가 파이프라인 작동
  ✅ 규모별 MATCH 의무 증가 패턴 (정상)
  ✅ 법령의 IF_SCOPE 규칙 분포

SIMULATION_REPORT_V1이 증명하지 못한 것 (철회):
  ❌ Equipment가 Process보다 중요하다
  ❌ Equipment Priority HIGH
  ❌ 입력 연결 우선순위

이유: 규칙 분포는 측정했지만 판정 영향도는 측정하지 않음
```

---

## 다음 단계 (수정된 방향)

```
진짜 Impact 측정을 위한 선행 조건:
  equipment_type IF_SCOPE 조건이 사업장 입력과 연결되어야 함
  → 그러나 이 연결 자체가 "구현"이므로
  → GPT 판단 전에는 금지

따라서 현재 단계에서는:
  Impact Ranking을 "규칙 분포"로만 보고
  "판정 영향도"는 미측정 상태로 남겨둔다

증명 가능한 Impact:
  CONSTRUCTION/BUILDING은 현재 전체 UNKNOWN
  → 이건 "규칙 분포"가 아니라 실제 100% 미커버
  → Coverage Gap이 명확히 측정된 영역
```

---

## 교훈

```
규칙 개수(distribution)를 영향도(impact)로 읽으면 안 된다.
수치가 나왔다고 다 같은 의미가 아니다.
42.4%는 진짜이지만, 그것이 뜻하는 바는 내가 처음 말한 것과 다르다.
```
