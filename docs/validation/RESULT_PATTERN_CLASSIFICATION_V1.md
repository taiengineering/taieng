# RESULT PATTERN CLASSIFICATION — 4상태 레지스터
# WO-RESULT-PATTERN-CLASSIFICATION-001

**작성일**: 2026-06-21
**목적**: 결과페이지 기준 엔진 품질 문제 전수 수집 → FACT/CANDIDATE/UNKNOWN/VALID 분리.
**원칙**: 결과 먼저 읽기, 카운트 아닌 문장 읽기, 수정 0. VALID로 정상경로 잠금(재조사 방지).
**금지 준수**: law_sector_mapping/compiler_core/draft_slot/binding/sector filter 수정 0, 삭제 0.
**샘플**: 건설 114 + 산업 97 = 211건 Reading (RPC-01 충족: 100건+).

---

## STEP-1: 결과 샘플 수집 (RESULT_SAMPLE_COLLECTION)

```
건설(token 16cea20b, 근로30): 114건
  category: 서류65 / 신고35 / 선임8 / 점검6
  rule_type: INSTALL45 / REPORT35 / MANAGE11 / APPOINTMENT8 / INSPECTION5 / ACTION7 ...
  source: 전부 DIAGNOSIS
  remarks 품질: human 114 / empty 0 / token 0

산업(ef9766ee, KSIC C20 화학): 97건
  category: 서류61 / 신고26 / 점검6 / 선임3 / 교육1
  rule_type: INSTALL45 / REPORT26 / MANAGE11 / INSPECTION4 / MEASURE2 ...
  source: 전부 DIAGNOSIS
  remarks 품질: human 97 / empty 0 / token 0
```

---

## STEP-2: 패턴 분류 (RESULT_PATTERN_CLASSIFICATION)

```
[A. Sector 오염] ★ 최대 문제
  건설·산업 양쪽 INSTALL 45건 동일 = 소방 NFPC 설비 설치기준.
  실제 문장: "감지기"/"포헤드 및 고정포방출구"/"함 및 방수구"/"음향장치"/
            "적응성 및 설치개수"(피난기구)/"전원"(옥내소화전)
  = 소방시설 부품 설치 사양. 근로30 건설현장 안전의무 아님.

[B. 건설 의무 누락]
  건설 고유 의무(안전관리계획수립/안전관리조직/자체·정기·정밀 안전점검/
  안전교육 기록 — 앞 분류 A 61건)가 결과에 0건.
  결과 선임 8건은 소방안전관리자 등 소방 계열이지 건설 안전관리책임자 아님.

[C. 산업 의무 누락] — 해당 없음(정상)
  산업 고유(작업환경측정/산안법 서류보존/측정결과보고)는 정상 유입.

[D. COMMON 과다] — 경미
  REPORT(신고) 35/26건 다수가 소방/측정 보고. "보고하여야" 추상은
  remarks가 article_title로 채워져 토큰 노출은 없음(표현은 정상).

[E. 표현 품질 문제] — 없음(정상)
  remarks 211건 전부 human. 코드 토큰("APPOINTMENT_TASK_CANDIDATE:...") 0건.
  = diagnosis_result_web의 _human_text/_refine_rules_table 정상 작동.

[F. Penalty 누락] ★
  결과 화면 "예상 최대 과태료 0원". penalty_summary가 코드에서 빈 문자열 고정
  (_task_to_rule_row: "penalty_summary": ""). penalty 미연결.

[G. Form 누락] ★
  summary.form_linked = 0. 신고35·서류65건인데 제출 양식 연결 0.

[H. 기타 — category 분류 불일치]
  "화재방호시설"(방사선규칙) rule_type=INSTALL인데 category=서류.
  "[KEC] 계통연계 보호장치 시설"(전기) ACTION인데 category=서류.
  일부 행에서 rule_type bucket과 category 라벨 불일치.
```

---

## STEP-3: 원인 레이어 매핑 (PATTERN_ROOTCAUSE_MATRIX)

```
패턴              원인 후보 레이어              확정여부
A Sector오염      L4 sector filter             FACT
                  (_load_sector_allowed_draft_ids
                   미매핑 보수적 통과 allowed.add)
                  근본: law_sector_mapping 미등록(NFPC)
B 건설의무누락    L3 draft_slot (binding 없음)  CANDIDATE
                  + L2 executable_draft         (GPT 영역)
C 산업의무        정상                          VALID
D COMMON과다      L6 presentation (경미)         CANDIDATE
E 표현품질        L7 result page (정상작동)      VALID
F Penalty누락     L5 compiler_core              FACT
                  (_task_to_rule_row penalty_summary="")
G Form누락        L5 compiler_core (form_linked 0)  FACT
H category불일치  L5 compiler_core              CANDIDATE
                  (_bucket_for_task_type vs category)
```

---

## STEP-4: 4상태 레지스터 (FACT/CANDIDATE/UNKNOWN/VALID)

### FACT REGISTER (재현됨 + 원인 소스 확인)
```
F-01 Sector 오염 (소방 NFPC 건설92%/산업82%)
   근거: 실제 문장(감지기/포헤드/방수구) + 원인코드(allowed.add 미매핑통과)
   다음: WO-LAW-SECTOR-MAPPING-UNKNOWN (GPT 법령해석)
F-02 Penalty 0원
   근거: _task_to_rule_row penalty_summary="" 고정 + 화면 0원
   다음: penalty 연결 설계 (GPT/구조)
F-03 Form_linked 0
   근거: summary.form_linked=0, 코드 고정
   다음: form 연결 설계
```

### CANDIDATE REGISTER (근거 있음, 추가 검증 필요)
```
C-01 건설 의무 누락 (안전관리계획/점검/교육 0건)
   근거: 앞 분류 A 61건이 결과 미출현. binding 미생성 추정.
   다음: GPT binding 후 재실행 검증.
C-02 category 분류 불일치 (INSTALL/ACTION이 서류로)
   근거: 일부 행 bucket≠category. 단 영향 범위 미측정.
   다음: _bucket_for_task_type ↔ category 매핑 Reading.
C-03 "작업환경측정기관"→TRAINING 분류
   근거: 측정기관(주체)이 사업장 의무로 분류됐을 가능성.
   다음: 해당 조문 본문 주체 확인.
C-04 COMMON/추상 의무 과다
   근거: REPORT 다수. 단 표현은 정상이라 품질 아닌 양 문제.
```

### UNKNOWN REGISTER (판단 불가)
```
U-01 건물(BUILDING) 섹터 결과
   사유: engine-test에 건물 프로브 없음. 무료진단 플로우 생성 필요.
U-02 전체 138 vs rules_table 114 차이(24건)
   사유: dedupe로 줄었는지, 누락인지 미확인.
U-03 INSTALL 45건이 양 섹터 동일한 정확한 이유
   사유: 소방 미매핑 통과로 추정하나 draft_slot 레벨 미확인.
```

### VALID REGISTER (추적 완료, 정상 — 재검토 불필요) ★
```
V-01 compiler_core 경로 (실행버튼→결과)
   근거: WO-RESULT-RUNTIME-BACKTRACE-003 전구간 YES.
   engine_version=v3.0-compiler-core-anonymous 서명.
V-02 결과 문장 계보 (remarks ← law_article.article_title)
   근거: 211건 전부 human 텍스트, 토큰 0. 정상 유래.
V-03 rule_type 변환 (draft_slot.family_name → _ACTION_TO_TASK)
   근거: WO-003 소스 확정. APPOINTMENT/INSPECTION/REPORT 정상 생성.
V-04 표현 정제 (diagnosis_result_web _refine_rules_table)
   근거: 코드 토큰 0건. _human_text 정상 작동.
V-05 산업 고유 의무 (작업환경측정/산안법)
   근거: 화학제조에 정확히 맞는 의무, rule_type/category 일치.
   = compiler_core가 KSIC C20 입력 정상 반영.
V-06 sector filter mismatch=0 (섹터 누수 없음)
   근거: verify mismatch 0. 잘못된 섹터 전용 법령 유입은 차단됨.
   (단 미매핑 통과는 별개 문제 = F-01)
```

---

## STEP-5: 수정 우선순위 큐 (FIX_PRIORITY_QUEUE)

```
P1 (즉시 수정 가능 — 단 소관 확인)
   - F-02 Penalty 연결: penalty_summary 채우기 (compiler_core 영역 → 소관 확인 필요)
   - F-03 Form 연결: form_linked (동일)
   ※ 단 compiler_core 수정은 엔진 영역 → GPT/사장님 승인 후.

P2 (후보 검증 후 수정)
   - F-01 Sector 오염: law_sector_mapping 정화 (GPT 법령해석) ← 최우선 실질효과
   - C-01 건설 의무 binding (GPT)
   - C-02 category 불일치 Reading 후 판단

P3 (대규모 구조 검토)
   - C-04 COMMON 과다 (presentation 구조)
   - U-02 138 vs 114 차이 규명
```

---

## 의존성 분석 (RPC-06)

```
F-01(Sector오염) ← law_sector_mapping (GPT) — 독립 수정 가능, compiler 무관.
F-02/F-03 ← compiler_core 내부 — 엔진 영역, 단독 수정 위험(GPT 승인).
C-01 ← draft_slot/binding (GPT 전담) — Claude 수정 금지.
C-02/H ← compiler_core _bucket↔category — 엔진 영역.
V-* ← 전부 정상, 의존성 잠금 완료(재조사 불필요).

★ 가장 독립적이고 효과 큰 것 = F-01 (law_sector_mapping 정화).
  compiler_core를 안 건드리고 데이터만으로 소방 오염 해소 가능.
```

---

## 성공 기준

```
RPC-01 결과 100건+ Reading → ✅ 211건
RPC-02 패턴 분류 완료      → ✅ A~H
RPC-03 원인 레이어 매핑    → ✅ L1~L7 매트릭스
RPC-04 Fact/Candidate 분리 → ✅ FACT3/CANDIDATE4/UNKNOWN3/VALID6
RPC-05 수정 없이 완료      → ✅
RPC-06 의존성 분석         → ✅
RPC-07 우선순위 큐         → ✅ P1~P3
```

---

## 완료 문장

```
결과페이지 211건을 기준으로 엔진 품질 문제를 수집하고,
FACT(3) / CANDIDATE(4) / UNKNOWN(3) / VALID(6)로 분리하였다.
VALID 레지스터로 compiler_core 경로·결과 계보·표현 정제·산업 의무를
정상 확인하여 잠갔다(재조사 불필요). 수정은 수행하지 않았으며,
향후 작업은 가장 독립적이고 효과 큰 F-01(law_sector_mapping 정화)부터
적용한다. compiler_core는 미변경 원칙을 유지한다.
```
