# END-TO-END GAP MAP — 입력→결과 전 구간 격차
# WO-END-TO-END-GAP-MAP-001

**작성일**: 2026-06-21
**목적**: 최종 성공조건("입력한 특징이 결과 의무로 나오는가") 기준 전 구간 GAP.
**제한**: 소방/sector mapping 몰입 금지. 그것은 GAP 하나(F-01)로만 기록.
**방법**: 소스+읽기 검증. 수정 0.

---

## STEP-1: 최종 성공조건 정의

```
성공 = 사용자가 입력한 특징이 결과 의무에 반영된다.

기대(건설 예):
  입력: 건설 / 타워크레인 있음 / 석면 있음 / 발파 있음 / 근로자 50
   ↓
  결과: 건설 특화 의무 + 타워크레인 의무 + 석면 의무 + 발파 의무

전 구간:
  INPUT → APPLICABILITY → OBLIGATION → CHECK → EVIDENCE → 판단 → RESULT
```

---

## STEP-2~3: 발견사항 수집 + GAP 위치 분류

### ★ 최상위 GAP — OBLIGATION GAP (입력↔의무 연결 없음)

```
[G-01] 위험요소 입력 ↔ 의무 연결 0건  ← 최상위 위험
  증거(소스+읽기):
    입력단 _merge_body_input에 has_crane/has_blasting/has_tunnel_bridge/
      has_high_work 등 위험요소 필드 존재(입력은 받음).
    그러나 draft_slot.binding_field 전체 목록:
      distance_value415 / equipment_type260 / facility_type220 /
      voltage_level142 / concentration_level110 / process_type33 /
      storage_capacity23 / power_capacity15 / area_size12 /
      monetary_value6 / employee_count3
    = has_crane/has_blasting/has_asbestos를 받는 binding_field = 0.
  결론: 타워크레인 입력해도 타워크레인 의무가 안 나옴.
        위험요소 입력이 의무로 연결되는 경로 자체가 없음.
  위치: OBLIGATION GAP (draft_slot binding 미생성)

[G-02] binding이 "장비 기술기준" 파라미터에 편중
  증거: binding_field 상위가 distance_value/equipment_type/voltage_level
    = "장비가 ~m 이내" "전압 ~V" 같은 기술 사양.
    "사업장이 무엇을 보유했나(위험요소)"가 아님.
  앞 건설분류 WO와 일치: 건설 법령 대부분 장비 기술기준, 사업장 의무 binding 0.
  위치: OBLIGATION GAP

[G-03] 건설 고유 의무 0건 (결과)
  증거: 결과 114건에 안전관리계획/안전관리조직/자체·정기·정밀안전점검/
    안전교육 = 0건. (앞 분류 A 61건이 결과 미출현)
  위치: OBLIGATION GAP
```

### APPLICABILITY GAP

```
[G-04] 입력 다양성 ↔ 결과 다양성 없음
  증거(앞 VR WO): 건설 5000현장 입력 다양해도 결과 동일 6문장 반복.
    facility_applicability가 numeric/scope binding만 평가 →
    위험요소 boolean 입력은 평가 대상에 없음.
  위치: APPLICABILITY GAP (G-01의 결과적 증상)
```

### INPUT GAP

```
[G-05] 건물(BUILDING) 입력 경로 미검증
  증거: engine-test에 건물 프로브 없음. 입력→결과 검증 불가.
  위치: INPUT GAP (환경 부족 = UNKNOWN)
```

### CHECK / EVIDENCE GAP

```
[G-06] Check Layer 실체 — 진단엔 의무목록만, 체크변환 없음
  증거(앞 WO): result_data는 "의무 목록"이지 "체크 질문/증빙/판단" 아님.
    runtime_checklist_execution 비어있음.
  단 NOT_ERROR 가능성: 무료/유료 진단(Step1)은 "의무 제시"가 목적,
    체크 실행은 SaaS 운영(별 단계)일 수 있음 → 설계 의도 확인 필요.
  위치: CHECK GAP + EVIDENCE GAP (단 진단 범위 밖일 수 있음 = UNKNOWN)
```

### RESULT GAP

```
[G-07] Sector 오염 (소방 NFPC) ← F-01, GAP 하나로만 기록
  증거: 소방 법령 108개 중 미매핑 100개(93%) → 보수적 통과.
  위치: RESULT GAP (law_sector_mapping 데이터)
  ※ 이 WO에서 더 파지 않음. 독립 수정 가능 항목으로만 기록.

[G-08] Penalty/Form 결과 비어있음
  증거: penalty_summary="" / form_linked=0 (스키마는 존재).
  위치: RESULT GAP (단 Step1 설계상 제외인지 미확정 = UNKNOWN)

[G-09] 138 vs rules_table 114 차이(24건)
  증거: applicable_count 138 vs dedupe 후 114.
  위치: RESULT GAP (정보 부족 = UNKNOWN)
```

---

## STEP-4: 영향도 평가

```
GAP    결과정확도영향  사용자체감영향  수정범위
G-01   ★최대          ★최대(입력 무의미)  draft_slot binding 생성(GPT)
G-02   ★최대          높음            binding 철학 재설계(GPT)
G-03   높음           높음(건설 핵심의무 없음)  binding(GPT)
G-04   높음           ★최대(결과 천편일률)  G-01 해소시 동반 해결
G-05   중간           중간            건물 프로브 추가
G-06   중간           중간            진단 범위 확정 필요
G-07   높음           높음(부적합 법령 노출)  law_sector_mapping(데이터, 독립)
G-08   중간           중간            설계의도 확인 후
G-09   낮음           낮음            규명
```

---

## STEP-5: 우선순위

```
P1 (입력이 결과로 안 감 — 제품 핵심 실패)
  G-01 위험요소 입력 ↔ 의무 연결 0건
  G-02 binding이 장비기준 편중 (사업장 의무 아님)
  G-03 건설 고유 의무 0건
  G-04 입력 다양성 ↔ 결과 다양성 없음 (G-01의 증상)
  → 전부 draft_slot/binding = GPT 전담. Claude는 조문 분류 인계까지.

P2 (결과 품질 — 부적합/누락)
  G-07 소방 오염 (law_sector_mapping, 데이터, 독립 수정 가능)
  G-08 Penalty/Form 미연결 (설계의도 확인 후)

P3 (검증 환경/규명)
  G-05 건물 프로브
  G-06 Check Layer 진단범위 확정
  G-09 138 vs 114 규명
```

---

## STEP-6: 최종 산출 (E2E GAP MAP)

```
현재 성공한 것 (VALID_LOCK):
  - compiler_core 경로 살아있음, 결과 화면까지 관통
  - 결과 문장 계보 정상(law_article.article_title)
  - 산업 고유 의무(작업환경측정/산안법)는 입력 반영됨
  - sector filter mismatch=0 (잘못된 섹터 차단)

현재 실패한 것 (성공조건 기준):
  ★ 위험요소 입력(타워크레인/석면/발파)이 결과 의무로 연결 안 됨 (G-01)
  ★ 건설 고유 의무가 결과에 없음 (G-03)
  ★ 입력이 달라도 결과가 같음 (G-04)
  - 소방 부적합 법령 다량 노출 (G-07)
  - Penalty/Form 비어있음 (G-08)

원인 위치:
  최상위 = OBLIGATION GAP (draft_slot binding이 위험요소 입력을 안 받음)
  차상위 = RESULT GAP (소방 오염 / penalty·form)

영향도 1위:
  G-01 (위험요소 입력↔의무 연결 0) = 제품 핵심 가치("입력한 게 결과로")의 실패.

우선순위:
  P1 = 입력↔의무 연결 (G-01~04, GPT binding)
  P2 = 결과 품질 (G-07 소방, G-08 penalty/form)
  P3 = 검증환경 (G-05 건물, G-06 check, G-09 차이)
```

---

## ★ 이 WO가 바꾼 우선순위 (사장님 지적의 핵심)

```
이전 흐름: 소방/sector mapping(G-07)에 몰입.
교정: G-07은 P2. 진짜 P1은 G-01(위험요소 입력↔의무 연결 없음).

이유:
  - 소방 오염은 "틀린 게 나옴"(품질 문제).
  - 입력↔의무 미연결은 "맞는 게 안 나옴 + 입력이 무의미"(핵심 가치 실패).
  - TAI의 정체성("입력한 사업장 특징대로 의무를 준다")이
    G-01에서 작동하지 않음.
  → 소방 정화보다 binding(입력↔의무 연결)이 상위 위험.

단 P1(G-01~04)은 전부 draft_slot/binding = GPT 전담.
  Claude 역할 = 위험요소별 의무 조문 분류해 GPT 인계(앞 건설분류 WO 연장).
```

---

## 성공 기준

```
- 최종 성공조건 정의       → ✅
- 발견사항 전부 수집       → ✅ (FACT/VALID/CANDIDATE/UNKNOWN 투입)
- GAP 위치 분류            → ✅ (INPUT/APPLICABILITY/OBLIGATION/CHECK/EVIDENCE/RESULT)
- 영향도 평가              → ✅
- 우선순위 산정            → ✅ (P1 입력↔의무, P2 품질, P3 환경)
- 수정 0건                 → ✅
```

---

## 완료 문장

```
최종 성공조건("입력한 특징이 결과 의무로 나오는가") 기준으로 전 구간 GAP을
작성하였다. 최상위 GAP은 OBLIGATION GAP — 위험요소 입력(타워크레인/석면/발파)을
받는 draft_slot binding_field가 0건이어서, 입력이 결과 의무로 연결되지 않는다.
이는 소방 오염(F-01)보다 상위 위험이며, TAI 핵심 가치의 실패다.
P1은 입력↔의무 연결(GPT binding), 소방은 P2로 재배치하였다. 수정 0.
```
