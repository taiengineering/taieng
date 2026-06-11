# 진단 파이프라인 정추적·역추적 정밀분석

작성일: 2026-06-11
작성: Claude (기획창) — 읽기 전용 분석, 코드·데이터 수정 없음
목적: **해당 사업장에 맞는 법령과 의무 목록을 도출**한다는 관점에서, 파이프라인이
어디서 의무를 잃고(누락) 어디서 엉뚱한 의무를 넣는지(오염)를 양방향으로 확정

기준 데이터:
- 정추적: 전체 분해 데이터 + 건설현장 진단 토큰 `bce78ced-0b2c-402c-8e9e-c28ee9de92f4`
  (테스트 건설현장: CONSTRUCTION, 건축, 50억, 직영 30·협력 20 → 결과 138건)
- 역추적: 위 건설 결과 138건(고유 항목 111개)을 출력→판정→binding→draft→조문으로 역으로 추적
- 비교 참조: 화학공장 토큰 `b90d40f2`(제조업 80명, 118건, A 게이트 적용 후)

---

# 1부. 정추적 (소비자입력 → 출력)

## 1.1 파이프라인 지도 (코드 실체)

```
① 소비자입력    UI/하니스 → DiagnoseStep1Body (sector별 필드 상이)
② 표준화입력    normalize_consumer_inp → _input_to_facility_context
                → create_temp_factory → 임시 factories 행
③ 법령엔진      law_article → Parser → rule_candidate → compatibility_validation
                → executable_draft → draft_slot(binding)        [사전 생성·정적]
④ 체크엔진      _load_sector_allowed_draft_ids (sector 필터)
                → _load_draft_slot_groups (binding 있는 IF슬롯만 적재)
                → facility_applicability_eval (factory 값과 대조) [런타임]
⑤ 정제레이어    fetch_compiler_candidates → _compiler_result_to_step1_format
                (조문제목 주입·bucket 분류·요약 생성)
⑥ 출력          anonymous_diagnosis_results → paid-diagnosis-result
```

## 1.2 깔때기 정량 (2026-06-11 DB 확정치)

```
법령 768개 / 조문 35,412개
  ↓ Parser                         rule_candidate 34,456개
  ↓ compatibility_validation PASS  10,725개 (31%)   ← 69% 소멸  ★병목1
  ↓ executable_draft               10,725개
  ↓ binding 있는 IF슬롯 보유          748개 (7%)     ← 93% 런타임 비가시 ★병목2
  ↓ sector 필터 + factory 대조       결과 118~138건
```

조문 35,412개 중 런타임이 평가할 수 있는 것은 748개(2%). 결과의 모든 항목은
이 748개에서 나온다.

## 1.3 단계별 손실·오염

**① 소비자입력 — sector별 입력 비대칭.** 건설: construction_type / contract_amount_eok /
direct_workers / subcon_workers. 제조: worker_count / floor_area / ksic / 위험물 플래그.
건설 입력에는 면적·전기용량이 없다(→ ②에서 0으로 저장됨, 역추적 경로2의 씨앗).

**② 표준화입력 — 결측이 0으로 둔갑.** `create_temp_factory`는 미입력 수치를
0으로 채워 저장한다(building_area=0, electrical_capacity_kw=0). 평가기는
`fac_val is None`만 결측으로 보므로, **0은 실값으로 비교**된다.
(주: 건설 근로자수는 `_input_to_facility_context`가 direct+subcon을 합산해
worker_count/employee_count=50으로 정상 전달함 — 1차 분석에서 "소실" 보고했으나
역추적으로 오류임을 확인, 정정.)

**③ 법령엔진 — 최대 병목 2개.**
- 병목1: compatibility_validation에서 RC의 69%가 PASS 못 받고 소멸.
  실증: **산업안전보건법 제15~19조(안전보건관리책임자·관리감독자·안전관리자·
  보건관리자·안전보건관리담당자)는 rule_candidate까지 생성됐으나 PASS 0건
  (AMBIGUOUS 3 / UNRESOLVED 11) → executable_draft 0건** → 어떤 사업장
  진단에서도 영구 누락. 건설현장 산안법 0건의 근본 원인.
- 병목2: draft 10,725개 중 binding 있는 IF슬롯 보유는 748개(7%)뿐.
  나머지 9,977개는 ④에서 적재조차 안 되어 결과에 못 들어간다.
  실증: 산안법 제42조 유해위험방지계획서는 draft가 **있는데도** binding이
  없어 결과에 못 들어옴. 위험성평가·산업안전보건위원회·중대재해 조치 등 동일.
- 748개의 binding 구성도 어긋남: distance 219 / voltage 110 / concentration 82는
  조문 내부 기술치수(사업장 입력값 아님), equipment_type 209는 평가기 매핑
  미구현. **사업장 입력과 실제 맞물리는 binding은 employee 3 / storage 19 /
  power 10 / area 7 / monetary 6 = 45개 수준.**

**④ 체크엔진 — 통과 판정이 무름.**
- sector 필터는 정상(law_sector_mapping 그대로 읽음, 미매핑 통과=의도).
- `evaluate_scope_check`: facility_type scope를 **site_type 컬럼에 값이 있다는
  사실만으로 POSSIBLE_CANDIDATE**(SCOPE_FIELD_EXISTS). scope의 내용(어떤
  시설/설비인가)은 대조하지 않음.
- 주체(actor) 검증 없음: IF_ACTOR 슬롯은 적재 대상이 아님 → 측정기관·관리업체·
  소방공사업자 의무가 사업장 의무로 통과.

**⑤ 정제레이어 — 변환만 하고 거르지 않음.** 조문제목 주입·bucket 분류는 정상
(Bug A/B/C 수정 완료). ④가 통과시킨 오염이 그대로 출력으로 감. task_count=0이라
항상 applicability fallback 경로로 동작.

**⑥ 출력 — 입력의 거울.** 카운트(118/138건)는 그럴듯하나 내용은 ③④의 산물.

---

# 2부. 역추적 (출력 → 통과 사유)

건설 결과 고유 항목 111개를 전수 역추적해 "왜 들어왔는가"를 분류.

## 2.1 통과 경로별 전수 분류

**경로 1 — facility_type 무력 scope: 93건 (84%)**
결과 ← POSSIBLE ← evaluate_scope_check ← "site_type에 값 있음" ←
건설 입력 construction_type='건축'이 site_type으로 저장.
간이스프링클러(주택전용)·공동주택·고층건축물·도로터널 설치기준 전부가
**"site_type이 '건축'이라고 적혀 있다"는 사실 하나**로 통과.

**경로 2 — "0값 매치": area_size·power_capacity의 `≤` 조건 (역추적 신규 발견 ★)**
결과 ← MATCH ← compare_numeric(0 ≤ N)=참 ← create_temp_factory가 미입력을
0으로 저장 ← 건설 입력에 면적·전기용량 없음.
실례(글로 확인): KEC 「의료장소 내의 접지 설비」(면적 50㎡ 이하 → 0≤50 참),
「에너지절약형 친환경주택 설계조건」(0.7 이하 → 0≤0.7 참), KEC 531(200 이하 → 참).
**미입력→0→모든 "N 이하" 조건 자동 참.** 결측이 실값으로 둔갑하는 ②+④ 합작.

**경로 3 — AMBIGUOUS 편승: voltage·storage·monetary**
FIELD_MAP quality가 AMBIGUOUS인 필드는 비교 없이 AMBIGUOUS 반환. 단독이면
저장 안 되지만, 같은 draft에 경로 2의 MATCH가 하나라도 있으면
aggregate("MATCH 있음 + NOT_MATCHED 없음 → MATCH")로 전체 통과. 미검증
조건이 0값 매치에 편승.

**경로 4 — 정당한 통과: 1건**
「시료채취 근로자수」(employee_count ≥ 2): 임시 factory employee_count=50
(direct+subcon 정상 합산) → 50≥2 MATCH.
**111개 중 사업장의 실제 입력값으로 정당하게 판정된 항목은 사실상 이 1건.**

## 2.2 누락 측 역추적

- 산안법 제15~19조 선임: 결과에 없음 ← draft 없음 ← PASS 0건. (병목1 실증)
- 산안법 제42조 유해위험방지계획서: draft 존재 ← binding 없는 IF슬롯 ←
  ④ 적재 불가 ← 결과 진입 불가. (병목2 실증)

## 2.3 역추적이 잡은 정추적 오류 (정정)

1차 정추적에서 "건설 direct_workers가 employee_count로 합산되지 않아 0"이라
보고했으나 **오류**. `_input_to_facility_context` CONSTRUCTION 분기가
direct+subcon을 합산해 50으로 정상 전달함을 코드로 확인. 근로자수는 살아
있고, 죽는 것은 **면적·전기용량**(건설 입력에 없어 0 저장 → 경로 2 유발).

## 2.4 역추적 한 줄 요약

> 결과 111개의 통과 사유 = "site_type에 글자가 있다"(93) + "미입력 0이
> '이하' 조건에 참"(수 건) + "그 MATCH에 편승한 미검증 조건" + 정당한 판정 1건.

현재 결과물은 사업장 대조의 산물이 아니라 **평가기의 두 가지 관대함
(존재=통과, 0=실값)이 만든 산물**이다. 반대편에서 진짜 의무(산안법 체제·
계획서·위원회)는 draft 부재(PASS 0) 또는 binding 부재로 평가장에 입장조차
못 한다.

---

# 3부. 병목 우선순위 (목적 관점)

"사업장에 맞는 법령·의무 도출"을 막는 순서:

1. **③ compatibility_validation PASS율 31%** — 핵심 의무가 draft가 못 되어
   영구 누락. 가장 치명적. **GPT 영역(Compiler 판정).**
2. **③ binding 커버리지 7%** — draft가 있어도 평가 조건이 안 만들어짐.
   사업장 입력과 맞물리는 binding 45개 수준. **GPT 영역(분해기).**
3. **④ scope 무력 통과** — facility_type 93건/111의 오염 주범.
   `evaluate_scope_check` 한 함수.
4. **④ 0값 매치 + AMBIGUOUS 편승** — 결측을 0으로 저장(②)하고 0을 실값으로
   비교(④), 미검증 AMBIGUOUS가 MATCH에 편승(aggregate). 같은 파일 내 보완.
5. **④ 주체 미검증** — IF_ACTOR 미적재로 기관·업자 의무 혼입.

평가기 측 결함(3·4·5)은 모두 `facility_applicability_eval.py` 한 파일의
판정 계층에 있음. 이 계층은 GPT 영역 경계 — 수정 주체(Claude 직접 vs GPT
작업지시)는 별도 결정 사항.

---

# 부록. 세션 중 확정된 관련 사실

- A 게이트(WO-LEG-Compiler-002, 주어 게이트)는 정상 작동: employee_count
  binding 172→3건, 유족·위원회·잠수작업 오매핑 소멸, 실의무 잔존 (글로 검증).
- B(scope) 1차 시도(executable_draft 보류)는 진단 경로가 status를 읽지 않아
  무효 → 전량 롤백 완료. 이번 역추적으로 진짜 차단 지점이
  `evaluate_scope_check`임을 확정.
- 기관/업자 주체 혼입(측정기관 지정신청, 소방시설관리업 등)은 숫자 주어
  문제(A)와 별개의 비숫자 주체 미검증 문제.
- SPECIAL_FACILITY는 의도적 휴면 — 수정 금지 (기존 표준 유지).
