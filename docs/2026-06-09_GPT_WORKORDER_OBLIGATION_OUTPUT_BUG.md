# [GPT 작업지시서] 법령엔진 의무 출력 오류 — obligation_summary 토큰화 + obligation_type 오분류

- 작성: 2026-06-09 (Claude 기획창)
- 대상: **GPT (법령엔진/Compiler/판정로직 전담)**
- 영역 구분: 본 문제는 **엔진 출력(obligation_summary/obligation_type 채움)** 으로 GPT 전담 영역. Claude는 진단·증거수집·표시(transform/HTML) 임시보정만 수행했고 엔진은 미수정.
- 우선순위: **높음** — 무료진단·유료진단·검증하니스 **모든 결과 출력에 공통 영향**. 사람이 의무 내용을 읽을 수 없음.

---

## 1. 증상 (사용자 확인)

검증하니스(제조업 목업, public_token `fd3592dc-378b-4a4e-8ef7-25a98f4a887d`, 총 177건)에서 결과페이지의 모든 의무가:

- 의무 제목에 사람이 읽는 문장이 아니라 **원천 토큰**이 그대로 출력됨
  - 예: `"APPOINTMENT_TASK_CANDIDATE: APPOINT_FAMILY"`, `"INSPECTION_TASK_CANDIDATE: INSPECT_FAMILY"`
- "조치 의무(ACTION)" 블록 아래에 **선임·점검 의무가 잘못 묶임**
- 법령명·조문(law_name/law_article)은 정상 출력됨

---

## 2. 근본 원인 (DB 실측 증거)

`anonymous_diagnosis_results.full_result.rules_table` 실측 (동일 토큰 진단):

| law_name | law_article | obligation_type | rule_type | category | obligation_summary | description |
|---|---|---|---|---|---|---|
| 소방시설공사업법 시행규칙 | 16 | **ACTION** | APPOINTMENT_TASK_CANDIDATE | 선임 | `APPOINTMENT_TASK_CANDIDATE: APPOINT_FAMILY` | 배치할 수 있다 |
| 화재의 예방 및 안전관리에 관한 법률 | 24 | **ACTION** | APPOINTMENT_TASK_CANDIDATE | 선임 | `APPOINTMENT_TASK_CANDIDATE: APPOINT_FAMILY` | 선임하여야 한다 |
| 화재의 예방 및 안전관리에 관한 법률 | 35 | **ACTION** | APPOINTMENT_TASK_CANDIDATE | 선임 | `APPOINTMENT_TASK_CANDIDATE: APPOINT_FAMILY` | 선임하여야 한다 |
| 소방시설 설치 및 관리에 관한 법률 | 6 | **ACTION** | INSPECTION_TASK_CANDIDATE | 점검 | `INSPECTION_TASK_CANDIDATE: INSPECT_FAMILY` | 확인하여야 한다 |

두 가지 오류가 동시에 존재:

### (A) obligation_summary에 코드 토큰이 들어감
- `obligation_summary` = `"APPOINTMENT_TASK_CANDIDATE: APPOINT_FAMILY"` (= runtime_name 원본 토큰)
- 사람이 읽는 텍스트는 `description`("선임하여야 한다" 등)에만 존재
- 즉 **요약 필드에 기술 토큰이 그대로 새어나옴**

### (B) obligation_type이 전부 ACTION으로 오분류
- `rule_type` = `APPOINTMENT_TASK_CANDIDATE` / `INSPECTION_TASK_CANDIDATE` (올바름)
- `category` = `선임` / `점검` (올바름)
- 그런데 `obligation_type` = **`ACTION`** (틀림) → 선임/점검 의무가 "조치"로 분류됨
- 결과페이지는 `obligation_type`으로 의무 블록(선임/점검/조치/보고/신고)을 나누므로, 선임·점검이 전부 조치 블록에 묶임

---

## 3. 발생 경로 (Claude 추적, GPT 확인 필요)

- 검증하니스 및 무료진단은 `run_step1_via_compiler` → `run_anonymous_diagnosis` (**compiler_core 경로**)를 탐
- 이 경로에서 rule_row를 만드는 자리(`services/anonymous_factory_service.py`의 `_applicability_to_rule_row` / `_task_to_rule_row` 계열)가:
  1. `obligation_summary`에 runtime_name 토큰을 그대로 넣음 (사람 텍스트로 치환 안 함)
  2. `obligation_type`을 `APPOINTMENT_TASK_CANDIDATE` → `APPOINT` 매핑하지 않고 ACTION으로 떨어뜨림

### 참고: 이미 존재하는 올바른 매핑 (재사용 가능)
`services/rule_candidate_projection.py`에 정확한 매핑 테이블이 이미 있음 (단 이 파일은 `[ISOLATED]` legacy 경로 = diagnosis_runtime_step1용이라 compiler_core는 안 씀):

```python
_TASK_TYPE_TO_OBLIGATION = {
    "APPOINTMENT_TASK_CANDIDATE": "APPOINT",
    "DESIGNATE_TASK_CANDIDATE": "APPOINT",
    "REPORT_TASK_CANDIDATE": "REPORT",
    "NOTIFY_TASK_CANDIDATE": "NOTIFY",
    "INSTALL_TASK_CANDIDATE": "ACTION",
    "MEASURE_TASK_CANDIDATE": "INSPECT",
    "INSPECT_TASK_CANDIDATE": "INSPECT",
}
_FAMILY_TO_OBLIGATION = {
    "APPOINT_FAMILY": "APPOINT", "REPORT_FAMILY": "REPORT",
    "NOTIFY_FAMILY": "NOTIFY", "INSTALL_FAMILY": "ACTION",
    "MEASURE_FAMILY": "INSPECT", "INSPECT_FAMILY": "INSPECT",
    "MANDATORY_FAMILY": "ACTION", "PERMISSIVE_FAMILY": "ACTION",
}
```

compiler_core 경로의 rule_row 생성부에서도 `rule_type`(`*_TASK_CANDIDATE`) 또는 `source_action_family`(`*_FAMILY`)를 이 매핑으로 obligation_type에 반영하면 (B) 해결.

---

## 4. 요청 사항 (GPT 판단·실행)

> 아래는 Claude가 파악한 방향일 뿐, **수정 범위·방식은 엔진 전담인 GPT가 결정**. source_trace/결정론 원칙(LLM 추론 금지, 추측 채움 금지)을 GPT 기준으로 유지할 것.

1. **(B) obligation_type 오분류 수정**: compiler_core 경로에서 `APPOINTMENT_TASK_CANDIDATE`/`INSPECTION_TASK_CANDIDATE` 등이 ACTION으로 떨어지지 않고 올바른 의무유형(APPOINT/INSPECT/REPORT/NOTIFY)으로 분류되도록.
2. **(A) obligation_summary 토큰화 수정**: 요약 필드에 `*_TASK_CANDIDATE: *_FAMILY` 토큰이 아니라 사람이 읽는 의무 텍스트가 들어가도록. (단, description의 "선임하여야 한다"는 서술어만 있고 주어·목적어가 빠져 거칢 → 6하원칙 WHO/WHAT을 어떻게 채울지는 역회전 엔진 설계상 GPT 판단.)
3. 수정 후 동일 입력(제조업 80명/위험물·화학물질·고압가스·보일러, factory_id `7e8764c5-be59-4dab-9027-fb19bfb5c86c`)으로 재진단하여 obligation_type 분포(선임/점검/조치/보고/신고)와 의무 텍스트가 정상인지 검증.

---

## 5. Claude가 이미 적용한 임시 표시보정 (참고 — 엔진 수정 후 무해)

엔진 출력이 토큰이어도 화면에서만 description을 우선 표시하도록 보정함. 엔진이 (A)(B)를 고치면 이 보정은 자동으로 정상값을 그대로 통과시킴 (충돌 없음):

- `routers/diagnosis_result_web.py` (transform): `_human_text`/`_is_token` 추가, `_rule_row_to_obligation_src`·`_merge_obligation_into_rule_row`에서 토큰이면 description 우선. commit `da27d7d`.
- `nexas/paid-diagnosis-result.html` (표시): `obTitle()` 헬퍼로 토큰이면 description 표시. commit `742888c`.

단, **obligation_type 분류(B)는 표시보정으로 해결 불가** — 엔진이 ACTION으로 내보내면 화면은 조치 블록에 묶음. 반드시 엔진에서 고쳐야 함.

또한 **PDF 경로(`/diagnosis/report-pdf/`)는 서버 생성이라 표시보정 미적용** → 엔진 수정 전까지 PDF엔 토큰이 보일 수 있음.

---

## 6. 영향 범위

- 무료진단 결과페이지 (`free-diagnosis-result.html` / `GET /diagnosis/result/{token}`)
- 유료진단 결과페이지 (`paid-diagnosis-result.html` / `GET /diagnosis/paid-result/{token}`)
- 검증 하니스 (`engine-test.html` / `POST /diagnosis/factory-test-run`)
- SaaS 작업할당(의무→작업 생성): obligation_type 오분류 시 작업 분류도 틀어질 수 있음 → **출시 전 필수 수정**

---

## 7. 증거 재현 쿼리

```sql
SELECT rule->>'law_name' AS law_name, rule->>'law_article' AS law_article,
       rule->>'obligation_type' AS obligation_type, rule->>'rule_type' AS rule_type,
       rule->>'category' AS category, rule->>'obligation_summary' AS obligation_summary,
       rule->>'description' AS description
FROM anonymous_diagnosis_results,
     jsonb_array_elements(full_result->'rules_table') AS rule
WHERE public_token = 'fd3592dc-378b-4a4e-8ef7-25a98f4a887d'
LIMIT 12;
```
