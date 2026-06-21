# EXPERIMENT QUEUE — 실험 준비 상태 (READY)
# WO-EXPERIMENT-QUEUE-MODE-001

**작성일**: 2026-06-21
**목적**: 조사 종료. GPT binding 입력 시 즉시 실행 가능한 READY 상태 구축.
**역할**: GPT=binding 값/operator/임계값/slot 선정(법령해석). Claude=적용·실행·측정·롤백.
**상태**: ★ READY — GPT 입력 1줄이면 즉시 실험 시작.

---

## 실험 대상 좌표 (확정, 재조사 금지)

```
의무: 안전관리계획의 수립
법령: 건설기술 진흥법 시행령
sector 매핑: {CONSTRUCTION} (정상)
draft 수: 5개 / slot 수: 28개 (전부 binding_field = null)

draft_id 목록:
  0ecad91b-68d3-45c7-adc6-eac9a315903e  (THEN: "작성할 수 있다" PERMISSIVE)
  1562c91e-9e5a-4c15-a353-70a6a00e8fd7  (ACTOR: 국토교통부장관, "제출해야 한다")
  70af45c7-dc73-4eea-a0cd-4b2adc8b7c42  (ACTOR: 국토교통부장관, "제출해야 한다")
  8b23dac4-a60b-44b8-b8bd-020724c73a53  ("통보해야 한다", 20일)
  be179aed-1fc5-479e-bb73-2f0bbc8cf153  (IF_ON_CHANGE "변경하는 경우", "제출해야 한다")
```

---

## binding 부여 가능 slot (IF_NUMERIC / IF_CONDITION) — GPT 선정 대기

```
slot_id                               draft_id   section       현재 raw_token       현재 operator/value
2170dd43-81c7-4442-bac9-485e45282697  1562c91e   IF_NUMERIC    "7일 이내"          <= 7 일
d1de2057-369e-4fa9-8b6d-5c29a8c7b871  70af45c7   IF_NUMERIC    "7일 이내"          <= 7 일
58deee47-495a-4abd-a11b-97e8d68ba731  8b23dac4   IF_NUMERIC    "20일 이내"         <= 20 일
67c35621-7942-4058-aba2-a91f8cddebea  0ecad91b   IF_CONDITION  "해당하는 경우에는"  (none)
bfb1ca19-a345-4136-8f68-4ec1ef6d61ac  be179aed   IF_CONDITION  "변경하는 경우에"    (none)
16048931-0641-4f6a-9aa2-6e9a84a167f0  be179aed   IF_CONDITION  "제출하는 경우에는"  (none)

★ 주의(GPT 판단 필요): 현재 IF_NUMERIC들은 "7일/20일 이내"=제출기한(DEADLINE)이지
  사업장 적용 조건(공사금액/규모)이 아님. = 이 slot에 binding을 걸어도
  "기한"이라 facility 매칭이 안 될 수 있음.
  안전관리계획의 "적용 대상" 조건(예: 공사금액 ≥ N억, 1종/2종 시설)이
  이 draft에 slot으로 없을 수 있음 → GPT가 (a) 기존 slot에 binding 부여할지
  (b) 적용조건 slot 신설이 필요한지 판단.
```

---

## 실험 절차 (READY)

```
STEP-1 백업      : 아래 롤백 SQL의 현재값 = 전부 binding_field NULL (기록 완료)
STEP-2 변경      : GPT가 지정한 slot_id에 binding_field/operator/value UPDATE
                   (GPT 입력 형식 예: "slot 2170dd43에 binding_field=contract_amount,
                    operator=>=, value=5000000000")
STEP-3 실행      : POST /diagnosis/factory-test-run {factory_id: 7b9bf18d-...}
STEP-4 결과 Reading: GET /diagnosis/paid-result/{새토큰} → rules_table
STEP-5 측정      : "안전관리계획" 등장 여부 → PRESENT 0→1?
```

---

## 롤백 SQL (READY)

```sql
-- 실험 후 즉시 롤백 가능 (현재 전 slot binding_field=NULL이 기준선)
UPDATE draft_slot
SET binding_field = NULL, operator = <백업값>, value = <백업값>
WHERE id = '<실험한 slot_id>';
-- IF_NUMERIC slot 백업값:
--   2170dd43: operator='<=', value='7'
--   d1de2057: operator='<=', value='7'
--   58deee47: operator='<=', value='20'
-- IF_CONDITION slot 백업값: operator=NULL, value=NULL
```

---

## 검증 factory_id (READY)

```
건설 프로브: 7b9bf18d-ea18-47aa-8d43-8996ce1151eb  (테스트 건설현장)
산업 프로브: 7e8764c5-be59-4dab-9027-fb19bfb5c86c  (대한정밀화학)
실행: engine-test runOne() = POST /diagnosis/factory-test-run {factory_id}
결과: GET /diagnosis/paid-result/{반환 public_token}
```

---

## 측정 기준 (READY)

```
기준선 (건설):
  PRESENT = 0
  MISSING = 11 (안전관리계획 포함)
  WRONG ≈ 98% (소방+전기)

측정 항목:
  PRESENT: rules_table에 "안전관리계획" 등장 수 (0→1 목표)
  MISSING: 11 → 10? (안전관리계획 빠지는지)
  WRONG: 소방+전기 비율 변화 (증가 없어야)

판정:
  A PRESENT +1, WRONG 증가 없음 → 유지
  B PRESENT +1, 경미 부작용     → 유지
  C PRESENT 변화 없음           → 롤백
  D WRONG/오염 증가             → 롤백
```

---

## 상태 선언

```
READY
  대상: 안전관리계획 draft (5 draft / 28 slot, binding_field 전부 NULL)
  변경 대기: GPT binding 입력 (slot_id + binding_field + operator + value)
  실행: READY (factory-test-run 7b9bf18d)
  롤백: READY (binding_field=NULL 원복)
  검증: READY (paid-result 측정)
  측정: READY (PRESENT/MISSING/WRONG)

→ GPT가 binding 정의 1줄 던지면 즉시 STEP-2~5 실행 + EXPERIMENT_LOG 기록.
  Claude는 "무슨 binding?" 질문하지 않음. 입력 오면 실행만.
```

---

## 완료 문장

```
조사 루프를 종료하고 변경 루프의 READY 상태를 구축하였다.
안전관리계획 draft 5건/slot 28건의 좌표, 백업(전 slot binding_field NULL),
롤백 SQL, 검증 factory_id(7b9bf18d), 측정 기준(PRESENT/MISSING/WRONG)을
모두 실값으로 확보하였다. GPT가 binding 정의를 입력하는 즉시
적용→실행→측정→유지/롤백을 수행하고 EXPERIMENT_LOG에 기록한다.
binding 값·operator·임계값·slot 선정은 GPT 영역으로 남긴다.
```
