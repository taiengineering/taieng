# 법령엔진 v4 레이어 재설계 기획서 (객체화·표준화)

작성일: 2026-06-11  
**버전: v2.1 (2026-06-16 — GPT 정밀검토 반영)**  
작성: Claude (기획설계 담당 — 사장님 승인으로 GPT 영역 포함 진행)  
상태: **설계 확정. WO-D-001~007 + WO-APPENDIX-COLLECT-001 이행 중**  
GPT 최종 판정: **승인 가능 — "v4 완성 구현"이 아니라 "관찰 파이프라인 구축 문서"로 승인**

---

## ⚠️ 이 문서가 유일한 기준이다

```
법령엔진 설계에 관한 다른 문서는 읽지 않아도 된다.

폐기 또는 초과된 문서들:
  - docs/law-engine/Cursor_Phase_2_1_Rule_Redesign_Spec__taiadmin.md
  - docs/law-engine/Cursor_Phase_2_2_*.md (v3, v3.1, v4 포함 전부)
  - docs/law-engine/LEGAL_RULE_PIPELINE__taiadmin.md
  - docs/law-engine/2026-05-07_DESIGN_master_rule_v2__taiadmin.md

위 문서들은 2026-05 기준 설계로, 본 문서(v2.1)가 전면 대체한다.
"설계가 뭔지 모르겠다"면 이 문서 하나만 읽으면 된다.

구현 WO 전문은: docs/2026-06-16_WO_D_PIPELINE_IMPL.md
```

---

## ★ 한 장 총정리 (읽는 데 3분)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[문제] 왜 엔진이 틀린 결과를 내는가?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

건설현장 진단 결과 111개 중 실제로 맞는 것: 1개 (0.9%)
나머지 110개가 통과한 이유:
  - 84%: site_type 컬럼에 글자가 있다는 사실 하나로 통과
  - 나머지: 입력 안 한 값이 0으로 저장되어 "0 이하" 조건에 자동 매칭
            의료장소 접지 의무, 친환경주택 의무가 건설현장에 들어온 이유

산안법 안전관리자 선임 의무: 진단에서 아예 안 나옴
이유: "별표 3과 같다"고 조문에 써있는데 별표 3 데이터가 DB에 없음

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[원인] 왜 이렇게 됐는가?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

법 쪽이 말하는 것:
  "간이스프링클러설비를 설치한 경우"
  → DB에는 FACILITY_SCOPE family + facility_type binding으로 저장
  → 사업장 입력과 비교할 수 없음 → "글자 있으면 통과"로 퇴화

사업장 쪽이 말하는 것:
  "연면적 800㎡, 근로자 45명"
  → DB에는 factories 테이블 컬럼 11개로 평탄화
  → 입력 안 한 항목은 0으로 저장됨

→ 두 쪽이 다른 언어를 써서 비교가 안 됨
→ "글자 있음 = 통과", "0 ≤ N = 통과"로 퇴화

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[해법] 무엇을 바꾸는가?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

핵심: 법 쪽 표현과 사업장 쪽 표현을 같은 코드 체계로 변환한 뒤 비교

법 쪽:
  "간이스프링클러설비를 설치한 경우"
  → targets: [{ kind: EQUIP, code: "EQUIP:스프링클러간이", relation: HAS }]

사업장 쪽:
  "스프링클러 있음"
  → equipment: TriList { confirmed: ["EQUIP:스프링클러간이"] }

비교:
  "EQUIP:스프링클러간이" ∈ confirmed? → YES/NO/UNKNOWN
  → 결측은 반드시 UNKNOWN (0으로 채우지 않음)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[지금 하는 일] 현재 단계
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

해법(v4 완성)을 바로 구현하기 전에, 먼저 현재 엔진을 관찰 가능하게 만든다.
이유: 관찰 없이 고치면 또 "폭주"가 된다.

1단계 (지금): WO-D-001~007
  소비자 입력 → 의무 결과까지 전 구간을 추적할 수 있는 파이프라인 구축
  기존 엔진 교체 아님 — 병행 실행

  D-001: SemanticClause   (법령 의미절 객체화)
  D-002: Common Sieve     (기관·업자 의무 거름 — 2,219개 룰)
  D-003: Section Sieve    (산업/건설/건물 분리)
  D-004A: Track A Adapter (기존 facility_applicability 결과 관찰)
  D-005: KSIC Signal      (업종별 의무 신호)
  D-006: Reverse Check    (왜 포함됐는가 역추적)
  D-007: Refinery         (중복 제거 + 결과 생성)

2단계 (1단계 완료 후): WO-APPENDIX-COLLECT-001 + WO-D-004B
  별표 본체 수집 (지금 없음)
  SemanticClause를 직접 사업장과 비교하는 방법 설계

3단계 (2단계 완료 후): v4 원설계 이행
  표준 객체 확정 → Registry 구축 → ApplicabilityCondition 생성
  → C축 대조기 → 전 법령 적용

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[D단계 비목표 — 이것을 만드는 게 아니다]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

D-001~007은 정확도 개선 작업이 아니다.
D-001~007은 관찰 가능성 확보 작업이다.
정확도 개선은 관찰 결과를 바탕으로 별도 WO로만 수행한다.

D단계 완료 기준은 "정확한 결과"가 아니라:
  - 입력부터 결과까지 trace가 생겼는가?
  - 기존 Track A와 병행 비교 가능한가?
  - 어디서 빠졌는지 볼 수 있는가?

이 기준을 벗어나면 16번째 엔진 제작이 된다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[절대 금지] 건드리면 안 되는 것
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

함수:
  facility_applicability_eval    삭제 금지 (D-004A가 래핑)
  fetch_compiler_candidates      삭제 금지
  assemble_refinery_result       삭제 금지
  emit_stored_diagnosis_result   삭제 금지

테이블 (GPT 관리 — Claude 수정·삭제 금지):
  constraint_node / numeric_constraint / rule_candidate
  executable_draft / draft_slot / compatibility_validation

D-002 거름 금지 사항:
  법 해석 기반 DROP 금지 (산안법이면 DROP 같은 규칙 — GPT 영역)
  AUTHORITY/BUSINESS/FRAGMENT 수준만 허용
  애매하면 DROP이 아니라 반드시 PENDING (잘못 빼는 것이 가장 위험)

D-004A: SemanticClause를 facility_applicability_eval에 직접 연결 금지
  (binding_field 없어서 평가 대상 0건이 됨 — 가짜 연결)
  D-004A의 입력 = facility_applicability rows (읽기만)
  D-004A의 출력 = CheckResult view
  D-004A의 금지 = evaluate_single_factory / evaluate_draft_for_facility 수정

D-004B: D-001~007 범위에 포함하지 않는다.
  D-004B는 별도 설계 승인 전 구현 금지.
  선행 조건: D-001~007 완료 + 별표 수집 + actor 개선 + Registry 구축
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## v2.1 변경 내역 (GPT 정밀검토 반영)

```
v2 → v2.1 변경사항:

1. D단계 비목표 명시 (GPT 위험1 대응)
   "정확도 개선이 아니라 관찰 가능성 확보"
   완료 기준 = trace 생성 + 병행 비교 가능 + 누락 지점 가시화

2. D-004A 입출력 명확화 (GPT 개선점2 대응)
   입력: facility_applicability rows
   출력: CheckResult view
   금지: evaluate_single_factory / evaluate_draft_for_facility 수정

3. D-004B 강화 (GPT 개선점3 대응)
   D-001~007 범위 외 명시
   별도 설계 승인 전 구현 금지

4. D-002 거름 원칙 보강 (GPT 위험3 대응)
   "애매하면 PENDING" 명시 (DROP은 확실한 경우만)
```

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

# 1. 배경 — 왜 재설계인가

## 1.1 정추적 (깔때기 손실)

```
법령 768 / 조문 35,412
  ↓ compatibility PASS    10,725 (31%)  ← 69% 영구 소멸. 산안법 제15~19조 누락
  ↓ binding 있는 IF슬롯      748 (7%)    ← 93%는 평가 불가
  ↓ 실제 맞물리는 binding = 45개
```

## 1.2 역추적 (건설현장 111개 통과 사유)

- **84%**: site_type에 글자 있으면 통과
- **수 건**: 미입력→0 저장→"N 이하" 자동 참
- **1건**: 실제 입력값으로 정당하게 판정

## 1.3 실패의 공통 뿌리

법·사업장이 다른 언어 / 결측→0 둔갑 / 주체 미분류 → 혼입 /
앞 레이어 정보 버려짐 / 탈락=소멸 / 사전 자산 미연결

## 1.4 v2 추가 — 15차 실측 단절

```
[단절 1] Track A(draft_slot 기반) ↔ Track B(semantic_clause 기반) 미연결
[단절 2] 조문 본문("별표 3과 같다") ↔ 별표 3 본체 미수집
```

---

# 2. 설계 원칙 (불변)

1. 양쪽이 같은 사전으로 말한다
2. 이음새 = 계약(Contract) — 레이어 간 입출력 스키마 고정
3. 결측 ≠ 0 — 3치(있음/없음/모름)
4. 탈락 = 보류, 소멸 금지
5. 판단은 C2 한 곳에만
6. 모든 산출물은 역링크
7. Candidate 철학 유지 — 법적 Truth 확정 금지
8. 표준은 한 번 정하면 바꾸지 않는다

---

# 3. 표준 객체

## 3.1 FacilityProfile

```
FacilityProfile {
  profile_id, sector,
  building:   { use_code: TriValue<코드>, floor_area: TriValue<수>, floor_count: TriValue<수> }
  workforce:  { regular_workers: TriValue<수>, subcontract_workers: TriValue<수> }
  processes:  TriList<PROC:*>
  equipment:  TriList<EQUIP:*>
  materials:  TriList<MAT:*>
  activities: TriList<ACT:*>
  metrics:    { construction_amount, electrical_kw, gas_capacity, … }
  provenance: { 입력값/확장값/기본값 구분 }
}
TriValue<T> = { state: PRESENT|ABSENT|UNKNOWN, value: T|null }
TriList<T>  = { confirmed: [T], denied: [T], unknown_rest: bool }
```

## 3.2 ApplicabilityCondition

```
ApplicabilityCondition {
  condition_id,
  source: { law_id, article_id, part_ref, raw_text_span },
  actor:       { code: ACTOR:OWNER|AGENCY|CONTRACTOR|GOV, raw }   # UNKNOWN 허용
  targets:     [ { kind: EQUIP|PROC|MAT|ACT|BLDG, code, relation, raw } ]
  quantifiers: [ { metric, subject_raw, operator, value, unit } ]  # subject_raw 필수
  obligation:  { action_type, action_text, deadline, frequency, evidence_form_ref, penalty_ref }
  completeness: { actor_coded, targets_coded, quantifiers_subject_ok }
  status: ACTIVE | QUARANTINED(사유)
}
```

## 3.3 공통 사전 Registry

`EQUIP:*` / `PROC:*` / `MAT:*` / `ACT:*` / `BLDG:*` / `ACTOR:*` / `METRIC:*`  
기존: industry_master → PROC, process_equipment_map → PROC↔EQUIP  
v2 추가: 별표 → AppendixCondition (WO-APPENDIX-COLLECT-001 완료 후)

---

# 4. 레이어 구성

```
[B축 법 번역기]              [A축 사업장 번역기]
B1 수집/버전                 A1 입력수집
B2 구조파싱                  A2 프로필표준화 (결측=UNKNOWN)
B3 의미추출                  A3 프로필확장 (KSIC→설비 추론)
B4 조건조립 → ApplicabilityCondition
B5 사전정규화 (대상→코드)
B6 품질게이트 (ACTIVE/QUARANTINED)
         ↘                  ↙
           [Registry]
         ↙                  ↘
              [C축 대조기]
  C1: Condition×Profile, 코드 대조. actor≠OWNER → 즉시 NOT
  C2: UNKNOWN 처리 정책 (판단 유일 지점)
  C3: 의무 인스턴스 생성. trace 필수
```

| 레이어 | 입력 → 출력 | 핵심 규칙 |
|---|---|---|
| B1~B2 | 법령 수집·파싱 | 현행 유지 |
| B3 | part → 의미토큰 | subject 보존 필수 |
| B4 | 의미토큰 → ApplicabilityCondition | IF/THEN·binding 폐지 |
| B5 | Condition 대상 → 코드 | 실패 시 UNKNOWN 보존 |
| B6 | Condition → ACTIVE/QUARANTINED | 탈락=보류 |
| A2 | 소비자입력 → FacilityProfile | 결측=UNKNOWN, 0 기입 금지 |
| C1 | Condition×Profile → MatchResult | actor≠OWNER 즉시 NOT |
| C2 | MatchResult → 포함/제외/잠정 | 정책 한 곳 |
| C3 | 포함 조건 → 의무 인스턴스 | trace 필수 |

---

# 5. 기존 자산 재배치

| 현행 | v4 위치 | 처리 |
|---|---|---|
| law_collector 등 | B1 | 유지 |
| constraint_node 284,579 | B3 | 유지, subject 보존 |
| executable_draft / draft_slot | B4 | v2: 즉시 폐지 아님 — Track A 병행 |
| compatibility_validation | B6 | 치환 (탈락=보류) |
| facility_applicability_eval | C1 | v2: D-004A로 래핑. 수정 금지. |
| ksic_process_map 등 | Registry + A3 | 신규 연결 |
| **법령 별표 본체** | **AppendixCondition** | **WO-APPENDIX-COLLECT-001 선행** |
| SPECIAL_FACILITY | — | 의도적 휴면 |

---

# 6. 실패 → 해결 매핑

| 확정된 실패 | 해결 장치 | 현재 상태 |
|---|---|---|
| 산안법 선임 의무 누락 | B6 탈락=보류 | 미착수 (Phase 2) |
| scope 무력 통과 84% | B5 코드화 + C1 코드 대조 | 미착수 |
| 0값 매치 | TriValue UNKNOWN | D-004A 부분 적용 |
| 기관·업자 혼입 | actor 1급 + C1 차단 | 거름망 2,219개 선행 |
| 별표 조건 미진입 | AppendixCondition | WO-APPENDIX-COLLECT-001 대기 |
| Track B 평가 미정 | D-004B 설계 | D-001~007 + 별도 승인 후 |

---

# 7. 이행 로드맵

## 1단계 — 현재 진행 (GPT 권고 순서)

```
D-001  SemanticClause Pipeline    semantic_clause_fix → 객체화
D-002  Common Sieve Engine        legal_sieve_rule (2,219개)
D-003  Section Sieve              산업/건설/건물 분리
D-004A Track A Check Adapter     facility_applicability rows → CheckResult view
D-005  KSIC Signal Engine         업종 신호
D-006  Reverse Check Engine       역추적
D-007  Refinery                   중복 제거·결과 생성
       ↓
       Track A 결과 ↔ 관찰 파이프라인 diff
```

목표: 소비자 입력 → 결과까지 전 구간 관찰 가능. 기존 엔진 교체 아님.

## 2단계 — 1단계 완료 후

```
WO-APPENDIX-COLLECT-001    별표 수집 (law_appendix + appendix_condition)
WO-LEG-Compiler-003        Actor Resolution (UNKNOWN 43,432건 개선)
WO-D-004B                  Semantic Evaluator — 별도 설계 승인 후 착수
```

## 3단계 — 2단계 완료 후

```
Phase 0  스키마 + Registry 코드 체계 확정 (코드 0줄)
Phase 1  Registry + A축
Phase 2  파일럿 법령군 B4~B6
Phase 3  C축 + Track A diff
Phase 4  전 법령 확대 → 전환
```

---

# 8. 검증 체계

1. 케이스 매트릭스: 8종 (제조 49/50명, 건설 49/50억, 빈 입력, 건물)
2. 정답지: MUST/MUST_NOT 케이스당 10~20개. 글읽기 1회 → 이후 기계 대조
3. trace: 모든 결과에 통과사유 부착
4. diff: Track A ↔ 관찰 파이프라인 비교 → 누락 항목만 글읽기
5. 글읽기 위치: 정답지 구축 / diff 신규분 / 분기별 표본 한정

---

# 9. 역할 분담

| 담당 | 영역 |
|---|---|
| Claude | 기획·WO 진행, A축·C축·검증, D-001~007 구현 조율 |
| GPT | B3~B6 법 해석 변환 규칙, Compiler, 별표 수집기, Actor Resolution |
| 사장님 | 표준 확정 승인, 정답지 글읽기 확정, 단계 전환 승인, D-004B 설계 승인 |

**GPT 관리 테이블 — Claude 수정·삭제 절대 금지:**  
`constraint_node` / `numeric_constraint` / `rule_candidate` /  
`executable_draft` / `draft_slot` / `compatibility_validation`

---

# 부록. 근거 문서

- **구현 WO 전문**: `docs/2026-06-16_WO_D_PIPELINE_IMPL.md`
- 정추적·역추적 분석: `docs/2026-06-11_PIPELINE_TRACE_FWD_REV.md`
- 체크엔진 5원칙: `docs/2026-06-10_CHECK_ENGINE_GUIDE.md`
- 15차 세션 핸드오프: `docs/2026-06-15_SESSION_HANDOFF.md`
- WO-LEG-Compiler-001/002: 주어 게이트 수정·검증 기록
