# 법령엔진 v4 레이어 재설계 기획서 (객체화·표준화)

작성일: 2026-06-11  
**버전: v2 (2026-06-16 — 15차 실측 검증 반영)**  
작성: Claude (기획설계 담당 — 사장님 승인으로 GPT 영역 포함 진행)  
상태: **설계 확정. WO-D-001~007 + WO-APPENDIX-COLLECT-001 이행 중**  
근거 분석: `2026-06-11_PIPELINE_TRACE_FWD_REV.md` (정추적·역추적 정밀분석)

---

## v2 변경 내역 (2026-06-16 실측 기반)

```
[확정된 사실 — DB·코드 직접 확인]

1. Track A ≠ Track B. 현재 두 경로는 별개 엔진이다.
   Track A: factories + draft_slot(binding_field) → evaluate_draft_for_facility
             → facility_applicability
   Track B: semantic_clause_fix → CandidateClause → SectionCandidateClause
             → ??? (평가 방법 미설계)

2. SemanticClause를 facility_applicability_eval에 직접 연결하면
   평가 대상이 0건이 된다 (binding_field 없음).
   → D-004를 A/B로 분리. D-004A = Track A 래핑, D-004B = NOT IMPLEMENTED.

3. 시행령 별표 본체 미수집.
   산안법 시행령 제16조: "별표 3과 같다" 언급만 있고
   별표 3 데이터는 law_article에 없음 (article_type에 '별표' 없음).
   → WO-APPENDIX-COLLECT-001 선행 필요.

4. B3 품질 한계 확인.
   ACTOR UNKNOWN 43,432건 = 원래 한계 + 일부 개선 가능.
   EQUIPMENT_SCOPE distinct 토큰 8종 = B5 코드화 재료 빈약.
   → WO-LEG-Compiler-003 (Actor Resolution) D-001~007 완료 후 발행 예정.

5. v4 설계 논리는 유효. 방향 오류 없음.
   단 Phase 0(표준 확정) 전에 WO-D-001~007로
   관찰 가능한 파이프라인 먼저 구축 (GPT 권고, 채택).
```

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

## 1.4 v2 추가 — 15차 실측으로 확인된 구조적 단절

```
[단절 1] SemanticClause 경로 ↔ Track A 경로

Track A (현재 운영 중):
  factories(사업장) + draft_slot(binding_field 있는 것만)
  → evaluate_draft_for_facility
  → facility_applicability (MATCH_CANDIDATE / POSSIBLE_CANDIDATE)

Track B (semantic_clause_fix 기반, 관찰 불가 상태):
  semantic_clause_fix → legal_sieve_rule 거름
  → 이후 사업장과 비교하는 방법이 정의되지 않음

두 경로는 현재 연결되지 않는다.
SemanticClause를 facility_applicability_eval에 넣으면 평가 대상 0건.

[단절 2] 조문 본문 ↔ 시행령 별표

산안법 제16조: "별표 3과 같다" (언급만)
별표 3 본체: DB 미수집
→ 선임 기준(제조업 50인 이상 등)이 파이프라인에 진입 불가
```

---

# 2. 설계 원칙 (불변)

1. **양쪽이 같은 사전으로 말한다** — 법 측 대상과 사업장 측 보유물은 동일한
   공통 사전 코드로 표현. 대조 = "코드 ∈ 목록".
2. **이음새 = 계약(Contract)** — 레이어 간 입출력 스키마를 고정. 레이어 구현은
   교체 가능, 계약은 불변.
3. **결측 ≠ 0** — 모든 사업장 값은 3치(있음/없음/모름). 모름은 모름으로 흐른다.
4. **탈락 = 보류, 소멸 금지** — 어떤 레이어도 데이터를 버리지 않는다.
5. **판단은 한 곳에만** — 정책 판단은 판정정책 레이어(C2) 단 한 곳.
6. **모든 산출물은 역링크** — 의무 → 조건 객체 → 조문 원문. 글읽기 검증이 결과 화면에서 바로 가능.
7. **Candidate 철학 유지** — 어떤 레이어도 법적 Truth를 확정하지 않는다.
8. **표준은 한 번 정하면 바꾸지 않는다** — 문제 발생 시 표준이 아니라 구현을 고친다.

---

# 3. 표준 객체 (이 설계의 본체)

## 3.1 FacilityProfile — 사업장 프로필 객체

```
FacilityProfile {
  profile_id, sector,
  building:  { use_code: TriValue<코드>, floor_area: TriValue<수>, floor_count: TriValue<수> }
  workforce: { regular_workers: TriValue<수>, subcontract_workers: TriValue<수> }
  processes: TriList<공정코드>    # PROC:*
  equipment: TriList<설비코드>    # EQUIP:*
  materials: TriList<물질코드>    # MAT:*
  activities: TriList<활동코드>   # ACT:*
  metrics:   { construction_amount, electrical_kw, gas_capacity, boiler_capacity, … }
  provenance: { 입력값/확장값/기본값 구분 }
}

TriValue<T> = { state: PRESENT|ABSENT|UNKNOWN, value: T|null }
TriList<T>  = { confirmed: [T], denied: [T], unknown_rest: bool }
```

## 3.2 ApplicabilityCondition — 적용조건 객체

```
ApplicabilityCondition {
  condition_id,
  source: { law_id, article_id, part_ref, raw_text_span },
  actor:   { code: ACTOR:OWNER|AGENCY|CONTRACTOR|GOV, raw: 원문주어 }  # UNKNOWN 허용
  targets: [ { kind: EQUIP|PROC|MAT|ACT|BLDG, code, relation, raw } ]
  quantifiers: [ { metric, subject_raw, operator, value, unit } ]  # subject_raw 필수
  obligation: { action_type, action_text, deadline, frequency, evidence_form_ref, penalty_ref }
  completeness: { actor_coded, targets_coded, quantifiers_subject_ok }
  status: ACTIVE | QUARANTINED(사유)
}
```

## 3.3 공통 사전 Registry

- `EQUIP:*` / `PROC:*` / `MAT:*` / `ACT:*` / `BLDG:*` / `ACTOR:*` / `METRIC:*`
- 기존 자산 흡수: industry_master → PROC, process_equipment_map → PROC↔EQUIP 간선
- **v2 추가**: 별표 데이터 → AppendixCondition (WO-APPENDIX-COLLECT-001 완료 후 연결)

---

# 4. 레이어 구성

```
[B축 법 번역기 — 배치]              [A축 사업장 번역기 — 런타임]
B1 수집/버전                        A1 입력수집
B2 구조파싱                         A2 프로필표준화 (결측=UNKNOWN)
B3 의미추출                         A3 프로필확장 (KSIC→공정→설비 추론)
B4 조건조립 → ApplicabilityCondition
B5 사전정규화 (대상→공통사전 코드)
B6 품질게이트 (ACTIVE / QUARANTINED)
          ↘                       ↙
            [공통 사전 Registry]
          ↙                       ↘
                [C축 대조기 — 런타임]
  C1 매칭    : Condition × Profile, 코드 대 코드 3치 대조
               actor≠OWNER → 즉시 NOT (혼입 차단)
  C2 판정정책: UNKNOWN 처리 정책 (판단 유일 지점)
  C3 의무생성: trace 필수 포함
```

## 4.1 레이어별 계약

| 레이어 | 입력 → 출력 | 핵심 규칙 |
|---|---|---|
| B1~B2 | 법령 수집·파싱 | 현행 유지 |
| B3 | part 텍스트 → 의미토큰 | subject 보존 필수 |
| B4 | 의미토큰 → ApplicabilityCondition | IF/THEN·binding 폐지 |
| B5 | Condition 대상 → 공통사전 코드 | 실패 시 UNKNOWN 보존 |
| B6 | Condition → ACTIVE/QUARANTINED | 탈락=보류, 소멸 금지 |
| A2 | 소비자입력 → FacilityProfile | 결측=UNKNOWN, 0 기입 금지 |
| A3 | Profile → 확장 Profile | provenance=INFERRED 표시 |
| C1 | Condition×Profile → MatchResult | actor≠OWNER 즉시 NOT |
| C2 | MatchResult → 포함/제외/잠정 | 정책 한 곳 |
| C3 | 포함 조건 → 의무 인스턴스 | trace 필수 |

---

# 5. 기존 자산 재배치

| 현행 | v4 위치 | 처리 |
|---|---|---|
| law_collector 등 | B1 | 유지 |
| auto_parse 등 | B2 | 유지 |
| constraint_node 284,579 | B3 | 유지, subject 보존 |
| rule_candidate / executable_draft / draft_slot | B4 | **v2: 즉시 폐지 아님 — Track A로 병행 유지** |
| compatibility_validation | B6 | 치환 (탈락=보류) |
| facility_applicability_eval | C1 | **v2: Track A 어댑터(D-004A)로 래핑. 수정 금지.** |
| law_sector_mapping | C1 사전 필터 | 유지 (미매핑 통과) |
| task/schedule/penalty | C3 | 유지 |
| ksic_process_map 등 사전 자산 | Registry + A3 | 신규 연결 |
| check_engine.py | C1 계약 + 검증 어댑터 | 유지·확장 |
| master_rule_v2 (0건) | — | 휴면 |
| SPECIAL_FACILITY | — | 의도적 휴면 |
| **법령 별표 본체 (v2 추가)** | **AppendixCondition** | **WO-APPENDIX-COLLECT-001 선행** |

---

# 6. 실패 → 설계 해결 매핑

| 확정된 실패 | 해결 장치 | v2 상태 |
|---|---|---|
| 산안법 제15~19조 영구 누락 | B6 탈락=보류 | 미착수 (Phase 2) |
| binding 커버리지 7% | binding 폐지, 조건 객체화 | 미착수 |
| scope 무력 통과 84% | B5 코드화 + C1 코드 대조 | 미착수 |
| 0값 매치 | TriValue (UNKNOWN 1급) | D-004A에서 부분 적용 |
| 기관·업자 의무 혼입 | actor 1급 + C1 즉시 차단 | 거름망 2,219개로 부분 선행 |
| 시행령 별표 조건 미진입 | AppendixCondition + 별표 수집 | **WO-APPENDIX-COLLECT-001 대기** |
| Track B 평가 방법 미정 | D-004B 설계 | **D-001~007 + APPENDIX 완료 후** |

---

# 7. 이행 전략 — v2 확정 로드맵

## 1단계 — 관찰 가능한 파이프라인 구축 (현재 진행)

```
WO-D-001  SemanticClause Pipeline        semantic_clause_fix → 객체화
WO-D-002  Common Sieve Engine            legal_sieve_rule 적용
WO-D-003  Section Sieve                  섹터별 분리
WO-D-004A Track A Check Adapter         facility_applicability 결과 래핑
WO-D-005  KSIC Signal Engine             process_noun_match_stats 활용
WO-D-006  Reverse Check Engine           역추적
WO-D-007  Refinery                       중복 제거·문장 생성
```

목표: 소비자 입력 → 결과까지 전 구간 관찰 가능한 상태.
기존 엔진 교체 아님. 병행 실행.

## 2단계 — 별표 수집 + Track B 평가 설계

```
WO-APPENDIX-COLLECT-001  별표 본체 수집 (law_appendix + appendix_condition)
WO-D-004B                Semantic Candidate Evaluator 설계·구현
```

1단계 완료 후 착수. Track A / Track B diff 분석 후 누락 의무 확인 → 평가 방법 확정.

## 3단계 — v4 원설계 이행 (Phase 0~4)

```
Phase 0  객체 스키마 + Registry 코드 체계 확정 (코드 0줄)
Phase 1  Registry 구축 + A축 (FacilityProfile 생성·확장)
Phase 2  파일럿 법령군 B4~B6 (ApplicabilityCondition 생성)
Phase 3  C축 + 병행 가동 (Track A diff)
Phase 4  전 법령 확대 → 전환
```

2단계 완료 후 착수. WO-LEG-Compiler-003 (Actor Resolution) 병행.

---

# 8. 검증 체계

1. **케이스 매트릭스**: TEST_HARNESS 사업장 8종 (제조 49/50명, 건설 49/50억,
   전부 빈 입력, 전부 채운 입력, 건물)
2. **정답지(골든 케이스)**: MUST/MUST_NOT 센티넬 케이스당 10~20개.
   글읽기는 정답지 구축 시 1회 → 이후 기계 대조.
3. **trace 표준**: 모든 결과에 통과사유 부착.
4. **diff**: Track A ↔ Track B 결과 비교 → 누락 항목만 글읽기.
5. **글읽기 위치**: 정답지 구축 / diff 신규분 / 분기별 표본 한정.

---

# 9. 역할 분담

| 담당 | 영역 |
|---|---|
| Claude | 기획·설계·WO 진행, A축·C축·검증 체계, D-001~007 구현 조율 |
| GPT | B3~B6 법 해석 변환 규칙, Compiler 구조, 별표 수집기, Actor Resolution |
| 사장님 | 표준 확정 승인, 정답지 글읽기 확정, 단계 전환 승인 |

**GPT 관리 테이블 — Claude 수정·삭제 금지:**
`constraint_node` / `numeric_constraint` / `rule_candidate` /
`executable_draft` / `draft_slot` / `compatibility_validation`

---

# 부록 A. 폐지 / 유지 목록 (v2 업데이트)

**폐지 (장기)**: IF/THEN draft_slot·binding_field 체계, compatibility PASS 소멸 깔때기,
FIELD_MAP 11개 매핑, scope 존재확인 통과, 결측→0 기입, 집계 편승.

**v2 수정**: `facility_applicability_eval` — 즉시 교체 아님. Track A 어댑터(D-004A)로
래핑 후 병행. D-004B 완성 후 단계적 전환.

**유지**: Candidate 철학, 수집·파싱 레이어, sector 필터(미매핑 통과), 사전 자산,
check_engine, A 게이트 교훈(subject 보존), SPECIAL_FACILITY 휴면, 글읽기 검증 원칙.

# 부록 B. 근거 문서

- `2026-06-11_PIPELINE_TRACE_FWD_REV.md` — 정추적·역추적 정밀분석
- `2026-06-10_CHECK_ENGINE_GUIDE.md` — 체크엔진 5원칙
- `2026-06-16_WO_D_PIPELINE_IMPL.md` — **구현 WO 전문 (v2 기준)**
- `2026-06-15_SESSION_HANDOFF.md` — 15차 세션 핸드오프
- WO-LEG-Compiler-001/002 — 주어 게이트 수정·검증 기록
