# ENGINE BOOLEAN TRIGGER HANDOFF — Claude 성과 고정 + GPT 인계
# WO-ENGINE-HANDOFF-BOOLEAN-TRIGGER-001

**성격**: 수정 WO 아님. 현재 GOOD 상태 고정 + GPT/엔진 인계 문서.
**작성일**: 2026-06-21

---

## 1. 현재 GOOD 상태 (고정, 문장 기준)

```
건설 프로브(7b9bf18d) 결과 7건, WRONG 0:

A. 사업장 안전의무 (3)
   - 안전관리계획의 수립               (건설기술 진흥법 시행령)
   - 소규모 건설공사 안전관리계획의 수립 등 (동)
   - 안전점검의 시기ㆍ방법 등           (동)
B. 위험요소 안전의무 (1)
   - 표면공급식 잠수작업 시 조치        (산업안전보건기준에 관한 규칙)
C. 기술기준/주변 (2~3)
   - 방사선 화재방호시설 / 친환경주택 설계조건 / 작업환경측정 시료채취
D. 행정절차 (0)
E. 기관업무 (0)
WRONG(소방·전기 오염): 0
```

---

## 2. 유지된 변경 목록 (DB 실재 확인됨)

```
[1] 소방 법령 sector UPDATE (CONSTRUCTION 제거) — 10건
    law_sector_mapping: 소방기본법/소방시설법4종/소방시설공사업법3종/화재예방법3종
    sectors에서 CONSTRUCTION 제거 → BUILDING/INDUSTRIAL 유지.
    롤백: array_append(sectors,'CONSTRUCTION').

[2] NFPC 화재안전기준 sector INSERT (BUILDING) — 27건
    law_sector_mapping에 NFPC 26개 + 한국전기설비규정 → sectors={BUILDING}.
    식별: notes LIKE 'MPF002%'. 롤백: 해당 행 DELETE.

[3] PRESENT/B축 binding (employee_count >= 0) — 8개 slot
    건설기술진흥법 시행령 IF_NUMERIC 7개(A축) + 잠수 IF_NUMERIC 1개(B축).
    slot: 0001cf36/58deee47/d1de2057/2170dd43/10e0b328/b61024a4/52071a14
          + 97c5960a(잠수).
    롤백: binding_field=NULL.
```

---

## 3. Claude가 달성한 것 (수치 아닌 문장 결과)

```
WRONG 정화:  소방·전기 기술기준 오염 → 0
  결과에서 옥내소화전/포소화설비/할론/감지기/도로터널 화재안전기준 등 전부 제거.
A축 생성:    "안전관리계획의 수립" / "안전점검의 시기·방법" 등 건설 사업장 의무 출현.
B축 생성:    "표면공급식 잠수작업 시 조치" 위험요소 의무 출현.
검증 방식:   "몇 건"이 아니라 "무슨 의무가 나왔는가"를 읽어 GOOD 판정.

방법론 전환 실증:
  단건 수정 = 무효(소방 1건 / monetary_value 1건 → 변화 없음).
  대량 패턴 수정 = 유효(소방 일괄 → WRONG 0, 건설기술진흥법 7개 → A축 3).
```

---

## 4. Claude 방식의 한계 (결과로 확정)

```
4종(타워크레인/석면/발파/밀폐공간) = Claude binding 방식으로 확장 불가.

  타워크레인 "지지"      → IF_CONDITION → employee_count binding 걸어도 미출현
  석면 "해체 작업 조치"   → IF_CONDITION → 동일 미출현
    (실측: IF_CONDITION은 평가 루프 _load_draft_slot_groups에 미적재.
     잠수 IF_NUMERIC만 출현한 것이 그 증거.)
  발파 / 밀폐공간        → 조건 slot(IF_*) 자체가 0 → binding 걸 자리도 없음.

= 잠수는 IF_NUMERIC을 우연히 보유해 Claude 방식으로 가능했으나,
  4종은 IF_CONDITION(Boolean) 또는 조건 slot 부재 → 구조적 막힘.
```

---

## 5. GPT/엔진 인계 작업 (Boolean Trigger)

```
목표: has_tower_crane/has_asbestos_demo/has_blasting/has_confined_space 입력이
      결과 문장으로 나오게 한다.

필요 작업 (전부 GPT/엔진 영역):
  (1) compiler_core 평가 루프 확장:
      _load_draft_slot_groups가 IF_CONDITION도 적재하도록.
      (현재 IF_NUMERIC/IF_SCOPE만 적재 → IF_CONDITION 2525건이 죽은 조건)
  (2) Boolean trigger binding 설계:
      "~하는 경우/보유" Boolean을 입력값과 잇는 binding_field 신유형.
      (기존 binding_field는 전부 numeric/scope = distance/equipment/voltage 등)
  (3) 입력 필드 ↔ condition 연결 (FIELD_MAP):
      has_tower_crane → 타워크레인 의무 draft
      has_asbestos_demo → 석면 의무 draft
      has_blasting → 발파 의무 draft  (※ 조건 slot 부재 → draft_slot 보강 필요)
      has_confined_space → 밀폐공간 의무 draft (※ 동일 보강 필요)
  (4) 발파/밀폐: 조건 slot 신설 또는 condition slot 보강
      (현재 IF_* slot 0 → 추출 단계부터 보강 필요).
  (5) 정제 주의(앞 WO 확인): IF_CONDITION 2525건 중 ACTIVE ~1%.
      UNRESOLVED 1808건(행정·법인·타부처)은 binding 금지.
      위험요소 보유 trigger만 선별 binding(오염 폭증 방지).

참고 자료(기존 docs/validation):
  GPT_BINDING_HANDOFF_P1_RISK_INPUTS.md (위험요소별 A의무 후보)
  INPUT_TYPE_COVERAGE_MAP_V1.md (TYPE-C/D/F FAIL 구조)
  CONDITION_QUALITY_REGISTER.md (IF_CONDITION ACTIVE 24건/DISCARD 1808)
```

---

## 6. GPT 작업 후 Claude 검증 기준

```
GPT가 Boolean trigger 작업 완료 후, Claude 역할:
  1. factory-test-run(7b9bf18d) 재실행
  2. 결과 문장 Reading (숫자 금지)
  3. A/B/C/D/E 분류
  4. GOOD/BAD/ROLLBACK 판정

B축 등장 검증 문장(GPT 작업 성공 시 나와야 함):
  타워크레인: 신호수 배치 / 작업중지(풍속) / 벽체지지
  석면:      작업계획 수립 / 조사결과 게시 / 출입통제
  발파:      피난장소 / 장전중지·대피 / 경계구역
  밀폐공간:   감시인 배치 / 비상연락체계 / 구조장비

판정:
  GOOD   = 4종 중 1+ 실제 문장 등장
  BETTER = 2+
  BEST   = 3+
  ROLLBACK = C/D/E(기술기준·행정·기관) 증가 시
```

---

## 7. Claude가 임의 수행하지 않는 것 (경계 재확인)

```
- IF_CONDITION 평가 로직 수정 (compiler_core)
- Boolean binding 설계
- draft_slot 생성
- binding_field 신설
- 법령 조건 해석
= 전부 GPT/엔진 영역. Claude는 변경 적용·재실행·읽기·판정만.
```

---

## 완료 문장

```
Claude 변경-검증 루프로 WRONG 0, A축 3건, B축 1건(잠수) 상태를 만들고
GOOD으로 고정하였다. 유지된 변경 3종(소방 UPDATE 10 / NFPC INSERT 27 /
binding 8 slot)은 DB에 실재한다.
타워크레인/석면/발파/밀폐공간 4종은 IF_CONDITION/조건 slot 부재 구조로
Claude 방식 확장 불가함을 결과 읽기로 확인하고, compiler_core 평가루프 확장 +
Boolean trigger binding 설계를 GPT/엔진으로 인계한다.
이 상태는 실패가 아니라 Claude 루프의 최대치다.
```
