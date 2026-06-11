# 법령엔진 v4 레이어 재설계 기획서 (객체화·표준화)

작성일: 2026-06-11
작성: Claude (기획설계 담당 — 사장님 승인으로 GPT 영역 포함 진행)
상태: 설계 확정 대기 → 승인 시 단계별 이행
근거 분석: `2026-06-11_PIPELINE_TRACE_FWD_REV.md` (정추적·역추적 정밀분석)

---

# 0. 한 문장 요약

> 법령엔진이 계속 실패한 원인은 레이어 내부가 아니라 **이음새**다 —
> 법 쪽과 사업장 쪽이 **같은 언어(표준 객체·공통 사전)로 말하지 않아서**,
> 35,412개 조문의 분해 결과가 "컬럼 11개 매핑 + site_type 글자 존재 확인"으로
> 퇴화했다. 해법은 재작성이 아니라 **표준 객체 2개를 정의하고 기존 레이어를
> 그 객체 중심으로 재배열**하는 것이다.

---

# 1. 배경 — 왜 재설계인가 (분석 근거)

## 1.1 정추적이 보여준 것 (깔때기 손실)

```
법령 768 / 조문 35,412
  ↓ Parser                rule_candidate 34,456
  ↓ compatibility PASS    10,725 (31%)  ← 69% 영구 소멸. 산안법 제15~19조
                                          (안전관리자·관리감독자 선임)가 여기서
                                          죽어 모든 진단에서 누락
  ↓ binding 있는 IF슬롯      748 (7%)    ← 93%는 런타임이 평가조차 못 함.
                                          유해위험방지계획서가 draft 있는데도 비가시
  ↓ 사업장 입력과 실제 맞물리는 binding = 45개 수준
```

## 1.2 역추적이 보여준 것 (건설현장 결과 111개의 통과 사유)

- **84%(93건)**: "site_type 컬럼에 글자가 있다"는 사실 하나로 통과 (scope 무력)
- **수 건**: 미입력→0 저장→"N 이하" 조건에 0이 자동 참 (0값 매치;
  의료장소 접지·친환경주택이 건설현장에 들어온 메커니즘)
- **수 건**: 검증 안 된 AMBIGUOUS 조건이 위 MATCH에 편승
- **단 1건**: 사업장의 실제 입력값으로 정당하게 판정 (시료채취 근로자수 50≥2)

## 1.3 실패의 공통 뿌리 = 객체화·표준화 부재

1. 법 쪽: "간이스프링클러설비를 설치한 경우"가 `설비코드+보유관계`라는 객체가
   아니라 FACILITY_SCOPE라는 막연한 family + facility_type이라는 막연한
   binding으로 남음 → 대조 불가능 → 존재 확인으로 퇴화
2. 사업장 쪽: 사업장이 가진 것이 객체 목록이 아니라 factories 테이블 컬럼
   11개로 평탄화. 결측이 0으로 둔갑(3치 부재)
3. 주체(누구의 의무인가)가 1급 객체가 아님 → 측정기관·관리업자·행정청 의무가
   사업주 의무로 혼입
4. 앞 레이어가 만든 정보(subject, IF_ACTOR)가 뒤 레이어에서 버려짐 —
   A 게이트(WO-LEG-Compiler-002)가 고친 것이 정확히 이 패턴 한 곳이었음
5. 탈락 = 소멸 (보류·재심사 트랙 없음) → 핵심 의무 영구 누락
6. 이미 보유한 사전 자산(industry_master 501 / ksic_process_map 6,957 /
   process_equipment_map 187,319)이 파이프라인에 연결돼 있지 않음

---

# 2. 설계 원칙 (불변)

1. **양쪽이 같은 사전으로 말한다** — 법 측 대상과 사업장 측 보유물은 동일한
   공통 사전 코드로 표현. 대조 = "코드 ∈ 목록".
2. **이음새 = 계약(Contract)** — 레이어 간 입출력 스키마를 고정. 레이어 구현은
   교체 가능, 계약은 불변. (체크엔진 5원칙의 확장)
3. **결측 ≠ 0** — 모든 사업장 값은 3치(있음/없음/모름). 모름은 모름으로 흐른다.
4. **탈락 = 보류, 소멸 금지** — 어떤 레이어도 데이터를 버리지 않는다. 탈락분은
   사유와 함께 보류 풀에 보존되어 재처리 가능하다.
5. **판단은 한 곳에만** — "모름을 포함시킬 것인가" 같은 정책 판단은 판정정책
   레이어(C2) 단 한 곳. 나머지 레이어는 전부 무판단 변환·대조.
6. **모든 산출물은 역링크** — 의무 → 조건 객체 → 조문 원문, 판정 → 통과 사유.
   글읽기 검증이 결과 화면에서 바로 가능해야 한다.
7. **Candidate 철학 유지** — 어떤 레이어도 법적 Truth를 확정하지 않는다.
   (기존 엔진의 강점 계승)
8. **표준은 한 번 정하면 바꾸지 않는다** — 객체 스키마·사전 코드 체계는
   버전으로만 진화하고, 문제 발생 시 표준이 아니라 구현을 고친다.

---

# 3. 표준 객체 (이 설계의 본체)

## 3.1 FacilityProfile — 사업장 프로필 객체

사업장이 "무엇을 가졌고 무엇을 하는가"의 표준 표현. 모든 진단의 입력.

```
FacilityProfile {
  profile_id, sector,                    # BUILDING/INDUSTRIAL/CONSTRUCTION(/휴면 SPECIAL_FACILITY)

  building:  { use_code: TriValue<코드>,  # 건물용도 (공통사전 BLDG:*)
               floor_area: TriValue<수>,  # 연면적 ㎡
               floor_count: TriValue<수> }

  workforce: { regular_workers: TriValue<수>,     # 상시근로자
               subcontract_workers: TriValue<수> } # 협력업체

  processes: TriList<공정코드>            # 공통사전 PROC:* (KSIC에서 확장 가능)
  equipment: TriList<설비코드>            # 공통사전 EQUIP:* (보일러·압력용기·크레인·스프링클러…)
  materials: TriList<물질코드>            # 공통사전 MAT:* (위험물·화학물질·고압가스…)
  activities: TriList<활동코드>           # 공통사전 ACT:* (공사종류·발파·굴착·밀폐공간작업…)
  metrics:   { construction_amount: TriValue<수>, electrical_kw: TriValue<수>,
               gas_capacity: TriValue<수>, boiler_capacity: TriValue<수>, … }

  provenance: { 입력값/확장값/기본값 구분 — A3 확장으로 추가된 항목은 표시 }
}

TriValue<T> = { state: PRESENT|ABSENT|UNKNOWN, value: T|null }
TriList<T>  = { confirmed: [T], denied: [T], unknown_rest: true|false }
```

핵심: **UNKNOWN이 1급 상태.** 결측을 0으로 채우는 일이 타입 수준에서 불가능.

## 3.2 ApplicabilityCondition — 적용조건 객체

조문 하나(또는 항·호 하나)가 요구하는 것의 표준 표현. 법 번역기의 산출물.

```
ApplicabilityCondition {
  condition_id,
  source: { law_id, article_id, part_ref, raw_text_span },   # 원문 역링크 (필수)

  actor:   { code: 주체코드, raw: 원문주어 }   # ACTOR:OWNER(사업주)/AGENCY(기관)/
                                              # CONTRACTOR(관리업자)/GOV(행정청)…
                                              # ★ 1급 필드. 코드화 실패 시 UNKNOWN

  targets: [ { kind: EQUIP|PROC|MAT|ACT|BLDG, # 무엇을 가진/하는 경우인가
               code: 공통사전코드,
               relation: HAS|OPERATES|HANDLES|PERFORMS,
               raw: 원문구절 } ]

  quantifiers: [ { metric: 지표코드(WORKERS|AREA|AMOUNT|CAPACITY…),
                   subject_raw: 원문주어,     # ★ A 게이트 교훈: 수량의 주어 보존
                   operator, value, unit } ]

  obligation: { action_type: APPOINT|INSPECT|ACTION|REPORT|NOTIFY,
                action_text, deadline, frequency,
                evidence_form_ref, penalty_ref }

  completeness: { actor_coded, targets_coded, quantifiers_subject_ok }  # B6 게이트 입력
  status: ACTIVE | QUARANTINED(사유)                                     # 소멸 없음
}
```

## 3.3 공통 사전 Registry (단일 표준)

- 체계: `EQUIP:*`(설비) / `PROC:*`(공정) / `MAT:*`(물질) / `ACT:*`(활동) /
  `BLDG:*`(건물용도) / `ACTOR:*`(주체) / `METRIC:*`(수량지표)
- 각 코드: 정식명 + 동의어/표기변형 목록(법령 표현 ↔ 소비자 표현 양방향)
- 기존 자산 흡수: industry_master → PROC 시드, process_equipment_map →
  PROC↔EQUIP 추론 간선, 별표·서식 데이터 → evidence_form_ref
- 단일 소스 원칙: 사전은 한 테이블 군. 법 번역기도 사업장 번역기도 같은 것을 참조

---

# 4. 레이어 구성

```
[B축 법 번역기 — 배치]              [A축 사업장 번역기 — 런타임]
B1 수집/버전                        A1 입력수집 (sector별 폼)
B2 구조파싱 (조/항/호)               A2 프로필표준화 (입력→FacilityProfile, 결측=UNKNOWN)
B3 의미추출 (주체·대상·관계·수량·행위)  A3 프로필확장 (사전 추론: KSIC→공정→추정설비,
B4 조건조립 (→ApplicabilityCondition)      "가지고 감" 원칙, provenance 표시)
B5 사전정규화 (대상→공통사전 코드) ★신설
B6 품질게이트 (완전성 검사→ACTIVE/보류) ★PASS깔때기 대체
        ↘                          ↙
          [공통 사전 Registry]
        ↙                          ↘
              [C축 대조기 — 런타임]
C1 매칭   : Condition × Profile, 코드 대 코드 3치 대조 (무판단, 체크엔진 계약)
C2 판정정책: UNKNOWN 처리 정책 (보수모드=잠정포함+확인질문 생성) ← 판단 유일 지점
C3 의무생성: 통과 조건 → 의무 인스턴스 (행위/기한/주기/서식/벌칙 + trace)

[횡단]
사전 Registry / 레이어 계약(스키마) / 추적성(역링크·통과사유) / 보류 풀(Quarantine)
```

## 4.1 레이어별 역할·계약 정의

| 레이어 | 입력 → 출력 (계약) | 핵심 규칙 |
|---|---|---|
| B1 | 법령 원문 → law_master/law_article + 버전 | 현행 유지 |
| B2 | 조문 → 구조화 part | 현행 유지 |
| B3 | part 텍스트 → 의미토큰 {주체,대상,관계,수량(주어포함),행위} | 추출물은 버려지지 않고 전부 B4로 |
| B4 | 의미토큰 → ApplicabilityCondition(미정규화) | IF/THEN 슬롯·binding 개념 폐지, 객체 필드로 직행 |
| B5 | Condition 대상 raw → 공통사전 코드 | 매핑 실패는 코드=UNKNOWN으로 보존 (버리지 않음) |
| B6 | Condition → ACTIVE / QUARANTINED(사유) | 완전성 기준: actor 코드화 + targets 또는 quantifiers 1개 이상 유효. 보류는 재심사 큐로 |
| A2 | 소비자입력 → FacilityProfile | 결측은 UNKNOWN. 0 기입 금지 |
| A3 | Profile → 확장 Profile | 사전 간선으로 후보 확장. 확장분은 provenance=INFERRED |
| C1 | Condition×Profile → MatchResult{MATCH/NOT/UNKNOWN, 사유} | actor≠OWNER면 즉시 NOT(혼입 차단). 수량은 주어 검증된 것만. 무판단 |
| C2 | MatchResult → 포함/제외/잠정포함+질문 | 정책 한 곳. sector·플랜별 모드 가능 |
| C3 | 포함 조건 → 의무 인스턴스 | trace(조문 역링크+통과사유) 필수 포함 |

---

# 5. 기존 자산 재배치 (재작성 아닌 재배열)

| 현행 | 신설계 위치 | 처리 |
|---|---|---|
| L0 수집 (law_collector 등) | B1 | 유지 |
| L1 파싱 (auto_parse 등) | B2 | 유지 |
| L2 constraint_node 284,579 / numeric_constraint 10,329 | B3 | 유지하되 산출물이 객체 필드로 직행 (subject 보존) |
| L3 rule_candidate / L6 executable_draft+draft_slot | B4 | 통합·치환 — 슬롯/binding 개념 폐지 |
| L4 compatibility_validation (PASS 깔때기) | B6 | 치환 — 탈락=소멸을 탈락=보류로 |
| L5 numeric_family (A 게이트 포함) | B3/B4의 수량 처리에 흡수 (주어 게이트 계승) |
| L7 facility_applicability_eval | C1 | 치환 — FIELD_MAP/존재확인/0비교 폐지, 코드 대조로 |
| 입구 sector 필터 (law_sector_mapping) | C1 사전 필터 | 유지 (미매핑 통과 원칙 유지) |
| L8 task/schedule/penalty | C3 | 유지·연결 |
| 사전 자산 (ksic_process_map 등) | Registry + A3 | **신규 연결** (현재 미사용 → 핵심 활용) |
| check_engine.py | C1의 대조 계약 + 검증 어댑터 | 유지·확장 |
| master_rule_v2 (현재 0건) | — | 휴면 확인됨. 본 설계 범위 외 |
| SPECIAL_FACILITY | — | 의도적 휴면 유지. 건드리지 않음 |

---

# 6. 현재 실패 → 설계 해결 매핑

| 확정된 실패 (분석 근거) | 해결 장치 |
|---|---|
| 산안법 제15~19조 영구 누락 (PASS 0건) | B6: 탈락=보류+사유, 재심사 큐 |
| binding 커버리지 7% (계획서·위원회 비가시) | binding 개념 폐지 — 조건은 객체 필드, 전 조건이 대조 대상 |
| scope 무력 통과 (결과의 84%) | B5 코드화 + C1 "코드 ∈ 보유목록" 대조 |
| 0값 매치 (의료장소·친환경주택 혼입) | TriValue — 결측=UNKNOWN, 0 둔갑 타입상 불가 |
| AMBIGUOUS 편승 | C1은 조건별 3치 결과를 보존, C2가 조건 단위로 정책 적용 (집계 편승 구조 폐지) |
| 기관·업자 의무 혼입 | actor 1급 객체 + C1 즉시 차단 |
| "N명" 주어 오인 (A 게이트로 1곳 수정) | quantifier.subject 보존 + 검증을 계약에 내장 (패턴이 아니라 구조로) |
| 검증이 매번 글읽기 노동 | trace 필수 — 통과사유가 결과에 붙어 나옴. 정답지(골든 케이스) 대조는 check_engine 어댑터로 |

---

# 7. 이행 전략 (단계별, 각 단계 독립 검증)

**Phase 0 — 표준 확정 (코드 0줄)**
객체 스키마 2종 + Registry 코드 체계 + 레이어 계약을 본 문서 기준으로 확정.
GPT와 합의 지점: B3~B6 변환 규칙의 세부 (법 해석 로직 소유권은 GPT 유지,
계약·스키마는 본 설계를 따름).

**Phase 1 — Registry 구축 + A축**
공통 사전 테이블 군 생성, 기존 사전 자산 흡수. A2/A3 구현
(FacilityProfile 생성·확장). 검증: 8케이스 매트릭스의 프로필이 의도대로
생성되는지 (특히 빈 입력 → 전부 UNKNOWN).

**Phase 2 — 파일럿 법령군으로 B4~B6**
산업안전보건법(법·령·규칙) + 화재예방법 + NFPC 일부 = 파일럿 범위.
기존 B3 산출물(constraint_node/numeric_constraint)을 입력으로
ApplicabilityCondition 생성 → B5 코드화 → B6 게이트.
검증: 산안법 제15~19조 선임 의무가 ACTIVE Condition으로 살아나는지 글로 확인.

**Phase 3 — C축 + 병행 가동**
C1~C3 구현. 하니스에 신엔진 경로 추가, **기존 엔진과 병행 출력**(같은 케이스
양쪽 결과 diff). 검증: 8케이스 × 정답지(MUST/MUST_NOT 센티넬) 기계 대조
+ diff 신규 항목만 글읽기.

**Phase 4 — 전 법령 확대 → 전환**
파일럿 기준 충족 시 768개 법령 확대. 기존 경로는 보존(롤백 가능) 후 전환.

각 Phase 공통 규칙: 기존 데이터·경로 삭제 금지(병행·보존), 단계별 결과는
글읽기로 최종 확인, 보고 형식 = 1.산출물 2.검증결과 3.남은문제.

**우선 착수 제안: Phase 0의 객체 스키마 + Phase 1의 Registry.**
모든 것의 토대이며, 기존 엔진을 건드리지 않아 위험이 0이다.

---

# 8. 검증 체계 (설계에 내장)

1. **케이스 매트릭스**: TEST_HARNESS 사업장 8종 — 제조 49/50명(선임 경계),
   건설 49/50억, **전부 빈 입력**(UNKNOWN 처리·0값 결함 검출 전용),
   전부 채운 입력, 건물, (휴면 제외).
2. **정답지(골든 케이스)**: 케이스별 MUST/MUST_NOT 센티넬 10~20개.
   글읽기는 정답지 구축 시 1회 (Claude 초안 → 사장님 글 확인 확정).
   이후 재진단마다 check_engine 어댑터가 기계 대조.
3. **trace 표준**: 모든 결과 항목에 통과사유(어느 조건이 어느 프로필 값과
   어떻게 매치) 부착 — 역추적이 결과 화면에서 공짜.
4. **diff**: 수정 전후 토큰 비교 — 추가/소멸 항목만 글읽기.
5. 글읽기의 최종 지위: 기준을 세우는 곳(정답지·diff 신규분·분기별 표본)에만.
   반복 대조는 기계. (글읽기 원칙은 유지하되 1회 투자로 전환)

---

# 9. 역할 분담

- **Claude**: 본 설계 전체의 기획·설계·진행 주관 (사장님 승인 기준).
  객체 스키마/계약/Registry/A축/C축/검증 체계 구현 및 B축 이행 조율.
- **GPT**: B3~B6의 법 해석 변환 규칙 세부(주체 추출 정밀화, 대상 표현 → 사전
  코드 매핑 규칙, 보류 사유 분류)에 대한 협의·검수 파트너. 계약과 스키마는
  본 설계를 따른다.
- **사장님**: 표준 확정 승인(Phase 0), 정답지 글읽기 확정, 단계 전환 승인.

---

# 부록 A. 본 설계가 폐지하는 것 / 유지하는 것

폐지: IF/THEN draft_slot·binding_field 체계, compatibility PASS 소멸 깔때기,
FIELD_MAP 11개 매핑, scope 존재확인 통과, 결측→0 기입, 집계 편승.
유지: Candidate 철학, 수집·파싱 레이어, sector 필터(미매핑 통과), 사전 자산,
check_engine, A 게이트의 교훈(주어 검증 — 구조로 승격), SPECIAL_FACILITY 휴면,
글읽기 검증 원칙(위치만 이동).

# 부록 B. 근거 문서

- `2026-06-11_PIPELINE_TRACE_FWD_REV.md` — 정추적·역추적 정밀분석 (깔때기
  정량, 통과경로 전수 분류, 병목 우선순위)
- `2026-06-10_CHECK_ENGINE_GUIDE.md` — 체크엔진 5원칙 (계약 사상의 원형)
- WO-LEG-Compiler-001/002 — 주어 게이트 수정·검증 기록 (subject 보존의 근거)
