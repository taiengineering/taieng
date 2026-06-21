# GPT BINDING HANDOFF — P1 위험요소 입력↔의무 연결
# WO-INPUT-OBLIGATION-BINDING-HANDOFF-001

**작성일**: 2026-06-21
**목적**: 위험요소 입력이 결과 의무로 안 가는 P1 GAP 해결용 조문 후보를 Reading 선별해 GPT 인계.
**원칙**: 선별만. draft_slot/binding_field/FIELD_MAP 생성·수정 0. DB update 0.
**핵심**: "타워크레인 조문 많다→전부 binding" 아님. "사업주 주체 안전의무만 후보".

---

## STEP-1: 위험요소 입력 현재 연결 상태 (INPUT_OBLIGATION_CONNECTION_STATUS)

```
입력필드             factories컬럼  binding_field  결과반영
has_tower_crane      YES           NO             NO
has_blasting         YES           NO             NO
has_asbestos_demo    YES           NO             NO
has_confined_space   YES           NO             NO
has_diving           YES           NO             NO
construction_type    YES           facility_type? UNKNOWN
construction_amount  YES           monetary_value YES(금액만)
has_excavation       NO            NO             NO  (입력컬럼 없음)
has_scaffold         NO            NO             NO  (입력컬럼 없음)
has_formwork         NO            NO             NO  (입력컬럼 없음)

★ 5개 위험요소(타워크레인/발파/석면해체/밀폐공간/잠수)는 factories 컬럼까지
  도달하나, 이를 받는 draft_slot.binding_field가 0건 → 결과 미반영.
  굴착/비계/거푸집/고소작업은 입력 컬럼 자체가 없음(별도 과제).
```

---

## STEP-2: 위험요소별 관련 조문 후보 수 (semantic_clause)

```
석면 503 / 굴착 170 / 비계 139 / 타워크레인 118 / 해체 111 /
잠수 36 / 밀폐공간 28 / 크레인일반 27 / 거푸집 19 / 발파 12
(카운트는 추출범위 파악용. 판단은 STEP-3 Reading.)
```

---

## STEP-3: 본문 Reading 분류 (RISK_ARTICLE_CLASSIFICATION)

### ★ 핵심 발견: 위험요소마다 "사업주 주체 사업장 의무"가 실재

```
[타워크레인] A 사업장의무 존재 (장비기준과 혼재):
  A: "사업주는 순간풍속 10m/s 초과 시 설치·수리·점검·해체 작업 중지"
     "사업주는 자립고 이상 설치 시 건축물 벽체에 지지"
     "사업주는 신호업무 담당자를 각각 배치"
     "사업주는 와이어로프 지지 시 준수사항 이행"
  B(제외): "지브에 폭40cm 보도 설치" "제동토크 정격50% 이상" "완충장치"
  D(제외): "설치·해체하려는 자는 고용노동부장관에게 등록"

[석면] A 사업장의무 다수:
  "사업주는 석면해체·제거 작업계획 수립 + 근로자 통지"
  "사업주는 석면조사 결과 게시"
  "사업주는 보호구 미착용자 출입금지"
  "사업주는 출입구 표지 게시"

[발파] A 사업장의무:
  "사업주는 피난 불가 시 피난장소 설치"
  "사업주는 벼락 우려 시 장전중지·근로자 대피"
  "사업주는 발파 종사 근로자 준수사항 이행"

[밀폐공간] A 사업장의무 다수:
  "사업주는 밀폐공간 사전파악 + 출입금지 표지"
  "사업주는 비상연락·구조장비·공기호흡기·응급처치 훈련 6개월 1회"
  "사업주는 감시인 연락설비 설치"

[잠수] A 사업장의무:
  "사업주는 스쿠버 잠수 2명1조 + 감시인 배치"
  "사업주는 감압 조치"
  "사업주는 표면공급식 설비 점검"
```

---

## STEP-4: A 분류 binding 후보 (RISK_TO_OBLIGATION_BINDING_CANDIDATE)

```
위험요소        입력필드            후보 의무(A)              제안 binding_field*  신뢰도
타워크레인      has_tower_crane     작업중지(풍속)/신호수배치/  has_tower_crane      높음
                                    벽체지지                  (boolean trigger)
석면            has_asbestos_demo   작업계획수립/조사게시/      has_asbestos_demo    높음
                                    출입통제/표지              (boolean trigger)
발파            has_blasting        피난장소/장전중지/대피      has_blasting         높음
밀폐공간        has_confined_space  사전파악/훈련/감시인/표지    has_confined_space   높음
잠수            has_diving          2명1조/감시인/감압/점검     has_diving           높음

* 제안일 뿐. 실제 binding_field 설계·생성은 GPT.
  주의: 기존 binding_field는 전부 numeric/scope(distance/equipment/voltage).
        위험요소는 boolean(있음/없음) trigger → 새 binding 유형 설계 필요(GPT 판단).
```

---

## STEP-5: 제외 후보 (NON_BINDING_RISK_ARTICLE_REGISTER)

```
[B. 장비·제품 기술기준 — binding 금지]
  타워크레인: 보도폭40cm / 제동토크50% / 완충장치 / 정지기구 / 이름판
  = 장비 제조·설치 사양. 사업장이 이행할 의무 아님. 장비 제조사·검사 대상.

[C. 정의] "타워크레인이란 ~" 등 → 의무 아님.

[D. 행정·등록·면허] "설치·해체하려는 자는 등록" "정기검사 받으려는 자"
  "건축주는 하중지지 서류 구비"(건축주 주체) → 사업장(시공) 안전의무 아님.

★ 특히 B(장비 기술기준)를 binding하면 G-02(장비기준 편중) 재발.
  현재 결과 오염(소방 NFPC)도 같은 유형 — 기술기준을 사업장 의무로 오노출.
  → A(사업주 주체)만 binding, B/C/D 제외가 P1 해결의 핵심.
```

---

## STEP-6: GPT 인계 (GPT_BINDING_HANDOFF_P1_RISK_INPUTS)

```
[P1 GAP 요약]
  위험요소 입력 5종(타워크레인/발파/석면/밀폐공간/잠수)이 factories까지
  도달하나, 이를 받는 binding_field가 0 → 입력이 결과 의무로 안 감.
  = TAI 핵심가치("입력대로 의무 제시") 실패.

[위험요소 입력 목록 + 대응 A의무]
  has_tower_crane    → 작업중지(풍속)/신호수/벽체지지
  has_asbestos_demo  → 작업계획/조사게시/출입통제/표지
  has_blasting       → 피난장소/장전중지/대피
  has_confined_space → 사전파악/훈련/감시인/표지
  has_diving         → 2명1조/감시인/감압/점검

[제외할 기술기준 조문]
  타워크레인 보도폭·제동토크·완충장치 등 장비 사양(B).
  등록·검사·건축주 서류(D).

[필요한 GPT 작업]
  1. A 조문 본문 정독 → 최종 "사업장(시공) 안전의무" 여부 확정
     (사업주 주체 + 현장 이행 의무만. 건축주/장비제조사 주체 제거).
  2. boolean 위험요소 입력을 받는 draft_slot/binding_field 설계
     (기존은 numeric/scope만 → boolean trigger 유형 신설 판단).
  3. FIELD_MAP: has_tower_crane/has_blasting/... → binding_field 매핑 설계.
  4. 굴착/비계/거푸집/고소작업은 입력 컬럼부터 부재 → 입력 추가 여부 판단.

[Claude가 한 것 / 안 한 것]
  한 것: 조문 Reading + A/B/C/D 분류 + A 후보 선별 + 인계.
  안 한 것: binding 생성 0, draft_slot 0, FIELD_MAP 0, DB update 0.
```

---

## 성공 기준

```
IBH-01 연결 상태표        → ✅ (5종 factories YES / binding NO)
IBH-02 조문 후보 추출     → ✅ (위험요소 10종)
IBH-03 본문 Reading 분류  → ✅ (A/B/C/D, 사업주 주체 의무 확인)
IBH-04 A만 승격           → ✅ (위험요소별 A 후보표)
IBH-05 B/C/D 분리         → ✅ (제외 레지스터)
IBH-06 GPT 인계 문서      → ✅
IBH-07 수정 0건           → ✅
```

---

## 완료 문장

```
위험요소 입력이 결과 의무로 연결되지 않는 P1 GAP에 대해, 기존 법령 조문을
Reading하여 위험요소별(타워크레인/발파/석면/밀폐공간/잠수) 사업주 주체
안전의무 후보(A)와 제외 대상 기술기준·행정 조문(B/D)을 분리하고,
GPT binding 작업용 인계 자료를 작성하였다.
"조문이 많다→전부 binding"이 아니라 "사업주 주체 안전의무만 후보"로 선별했다.
binding 생성·draft_slot·FIELD_MAP 수정은 수행하지 않았다.
```
