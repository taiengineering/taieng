# CONSTRUCTION BINDING — GPT 인계 자료 (작업 1 완료, 작업 2~4 인계)
# WO-CONSTRUCTION-BINDING-ACTIVATION-001

**작성일**: 2026-06-20
**수행**: 작업 1(건설 조문 추출 + 본문 Reading) = Claude 완료.
**인계**: 작업 2~4(입력조건 정의 / draft_slot·binding_field 생성 / FIELD_MAP 확장) = GPT.
**역할 근거**: draft_slot·binding_field·FIELD_MAP 생성, 법령 의무 해석 = GPT 전담(절대 규칙).
**금지 준수**: 신규 법령 0 / 의무 문장 작성 0 / binding 생성 0 (Claude는 조회·읽기만).

---

## ★ 작업 1 핵심 발견: 건설 조문 대부분이 "장비 기술기준"이지 "사업장 의무"가 아니다

```
CONSTRUCTION sector 조문 = 4,079건.
위험별 조문을 본문 Reading + 의무성 단서로 분류:

  hazard      DUTY_LIKELY(사업장 의무)   SPEC_LIKELY(장비 기술기준)
  타워크레인        2                       97
  굴착             0                       35
  밀폐공간          0                        5
  해체             4                       27
  비계             1                        1
  잠수             0                        0 (CONSTRUCTION sector 내 거의 없음)

= 건설 위험 조문의 대다수가 "장비 제조·구조 기술기준"이다.
```

### 본문 실제 예시 (Reading)

```
[타워크레인 — SPEC]
  "타워크레인은 연속적인 정격하중상태에서 변형이 있어서는 아니 된다"
  "주행식 타워크레인은 제동장치를 설치하여야 한다 ... 제동토크값은 ..."
  "기복장치를 갖는 타워크레인은 경사각 지시장치를 설치하여야 한다"
  "자립고란 ... 높이를 말한다" (용어 정의)

[굴착 — SPEC]
  "굴착기의 디퍼 및 크람셀 버킷은 균열이나 손상된 곳이 없어야 하고..."
  "굴착기는 최대작업반경 상태에서 버킷 끝단 기울기 변화량이 10분당 5도 이내..."
  "평적선이란 ... 직선을 말한다" (용어 정의)
```

→ 이 조문들은 "굴착기/타워크레인 제조사가 지켜야 할 기계 안전인증 기준"이지,
  "굴착 작업을 하는 건설 사업장이 이행할 의무"가 아니다.
```

---

## ★★ 이것이 binding을 Claude가 만들면 안 되는 이유

```
WO 작업 2의 예: "타워크레인 조문 → has_tower_crane".
이를 기계적으로 binding하면:
  has_tower_crane=True인 5,000개 현장에
  "정격하중 변형 금지", "제동토크값 50% 이상" 같은
  장비 제조기준 97건이 사업장 의무로 쏟아짐.
= sector filter로 막은 것과 같은 종류의 새 오매핑.

검증 원칙(절대): 카운트가 아닌 "글 읽기"로 의무 여부 판단.
  타워크레인 조문 99건 중 사업장 의무는 2건뿐.
  어느 2건인지, 어떤 입력조건이 맞는지 가리는 것 = 법령 해석 = GPT.
```

---

## 작업 1 산출: GPT가 받을 건설 위험 조문 목록 (의무성 후보)

```
GPT 작업 2~4를 위한 입력:

[DUTY_LIKELY 우선 검토 대상 — 사업장 의무 가능성]
  타워크레인 DUTY 2건 / 해체 DUTY 4건 / 비계 DUTY 1건
  → 이들 본문을 GPT가 읽어 "진짜 사업장 의무"인지 확정,
    맞으면 입력조건(has_tower_crane 등) 정의.

[SPEC_LIKELY — 사업장 의무 아님, binding 제외 권고]
  타워크레인 97 / 굴착 35 / 해체 27 / 밀폐 5 / 비계 1
  → 장비 기술기준. 사업장 task로 만들면 오매핑.
    binding 대상에서 제외하는 것이 검증 원칙에 맞음.

[부재 — CONSTRUCTION sector에 거의 없음]
  잠수: CONSTRUCTION 0건 (앞 WO: 전체에서도 극소)
  발파/석면: CONSTRUCTION 0건, COMMON·INDUSTRIAL에 분산
  → has_blasting/has_asbestos/has_diving 입력에 대응할
    CONSTRUCTION 의무 조문 자체가 거의 없음.
    COMMON분 활용 여부 = GPT 판단.
```

---

## GPT 인계 작업 (작업 2~4)

```
[GPT-작업2] 건설 위험별 DUTY 조문 확정
  - DUTY_LIKELY 후보(타워2/해체4/비계1) 본문 정독
  - "사업장이 이행하는 의무"만 선별 (장비기준·정의 제외)
  - 각 의무 조문 ↔ 입력(has_tower_crane 등) 대응 정의

[GPT-작업3] draft_slot / binding_field 생성
  - 선별된 의무 조문에 IF_SCOPE 슬롯 부여
  - binding_field: construction_hazard / construction_equipment 등
    (WO-CONSTRUCTION-FILTER-CONNECTION-001 매핑표 참조)

[GPT-작업4] FIELD_MAP 확장
  - binding_field → factories 컬럼 매핑 정의
    has_tower_crane / has_confined_space / has_asbestos_demo /
    has_blasting / has_diving (factories에 실재 컬럼)
```

---

## Claude 후속 (GPT 작업2~4 확정 후, 작업 5~7)

```
[작업5] run_facility_applicability 재실행 (railway run)
[작업6] run_task_candidate 재실행 (railway run)
[작업7] 건설 VR 결과 문서 재읽기:
  - 타워크레인 입력 현장에 타워크레인 의무 문장 등장 여부
  - 입력 없는 현장에 미등장 여부
  - 본문 읽기로 확인 (카운트 아님)
```

---

## 정직한 결론

```
작업 1을 수행하니, WO의 전제("건설 법령에 binding만 걸면 의무가 나온다")가
실제 데이터와 다르다:
  CONSTRUCTION 조문 대부분이 장비 기술기준이라,
  기계적 binding은 새 오매핑을 만든다.

따라서 작업 2(어느 조문이 진짜 사업장 의무인가)는 법령 해석이고,
작업 3·4(draft_slot/binding_field/FIELD_MAP 생성)는 엔진 입력계약 변경이다.
둘 다 GPT 전담 영역이므로, Claude는 작업 1(조문 추출+Reading)까지 수행하고
GPT에 인계한다.

"안 나온다"는 증명했고(앞 WO), "나오게 만들기"의 전제 검증도 끝냈다.
다음은 GPT의 법령 해석이 선행되어야 한다.
```

---

## 완료 문장 (이 WO에서 Claude가 도달한 지점)

```
건설 고유 입력에 대응하는 기존 건설 법령을 추출해 본문을 읽은 결과,
CONSTRUCTION 조문 대부분이 사업장 의무가 아닌 장비 기술기준임을 확인하였다.
기계적 binding은 새 오매핑을 만들므로, 어느 조문이 진짜 사업장 의무인지
가리는 법령 해석을 GPT에 인계한다. binding 생성은 수행하지 않았다.
```
