# REAL INPUT PATH TRACE V1
# WO-INPUT-PATH-TRACE-001 (확장: 실제 유료진단/SaaS 입력부 추적)

**작성일**: 2026-06-20
**목적**: 유료진단·SaaS 입력 데이터의 실제 흐름을 추적해 "진짜 입력부"를 확인.
**금지 준수**: 판정/원인분석/수정 없음. 흐름 추적·사실 기록만.
**배경**: 직전 검증(PHASE 4~6)이 "엔진에 연결된 입력부"를 본 게 맞는지 의문 제기됨.

---

## ★ 핵심 발견: 내가 검증한 경로 ≠ 실제 유료진단 경로

```
내가 PHASE 4~6에서 쓴 경로:
  VR → build_facility_profile → applicability_conditions(ACTIVE 14건)
  → Python 재현 → Fingerprint

실제 유료진단 경로 (코드 추적으로 확인):
  POST /api/v1/diagnosis-engine/evaluate (factory_id + input_data)
  → DiagnosisService.evaluate()
  → fetch_compiler_candidates(sb, factory_id)   ← Compiler Core
  → 사전 materialized 런타임 테이블을 읽음:
       facility_applicability  (적용 법령)
       task_candidate          (의무)
       schedule_candidate      (일정)
       penalty_obligation_relation (벌칙)
       compliance_review_queue / compliance_package

→ 두 경로는 완전히 다른 엔진이다.
  내가 본 applicability_conditions(14건)는 실제 진단이 읽는 테이블이 아니다.
```

---

## 코드 추적 (실측)

```
[1] routers/diagnosis_engine.py
    POST /api/v1/diagnosis-engine/evaluate
      body = {factory_id, input_data}
      → DiagnosisService.evaluate(sb, factory_id, input_data)

[2] services/diagnosis_service.py
    DiagnosisService.evaluate():
      core = fetch_compiler_candidates(sb, factory_id)
      applicability = core["applicability_candidates"]
      tasks = core["task_candidates"]
      ...
      → 결과 = diagnosis_candidate / diagnosis_session에 저장

[3] services/compiler_core_svc.py
    fetch_compiler_candidates(sb, factory_id):
      명시 주석: "Reads pre-materialized runtime tables
                 (facility_applicability, task_candidate, …).
                 Does not run batch evaluation;
                 see scripts/run_facility_applicability.py for that."
      읽는 테이블:
        facility_applicability  (factory_id 기준)
        task_candidate          (factory_id 기준)
        schedule_candidate
        penalty_obligation_relation
        compliance_review_queue
        compliance_package
```

---

## 실제 진단 입력부 데이터 규모 (DB 실측)

```
facility_applicability  29,096건
task_candidate           3,388건
schedule_candidate       1,159건
compliance_package          30건

= 실제 진단은 이 테이블들을 읽는다.
  내가 PHASE 4에서 쓴 applicability_conditions(ACTIVE 14건)와
  규모·구조가 완전히 다르다.
```

---

## 실제 task_candidate 구조 (건설 sector, 실측)

```
건설 사업장의 task_candidate는 "family 코드"로 추상화돼 있음:
  REPORT_TASK_CANDIDATE / REPORT_FAMILY / MANDATORY_FAMILY   260건
  INSTALL_TASK_CANDIDATE / INSTALL_FAMILY                    165+90건
  APPOINTMENT_TASK_CANDIDATE / APPOINT_FAMILY                100+60건
  MANAGE / NOTIFY / INSPECTION / VERIFY / DESIGNATE / MEASURE / EXECUTE / RECORD ...

→ 내가 PHASE 5에서 읽은 "경보설비/안전관리자 선임/교육" 같은
  구체 텍스트와 다른 구조(family 코드 추상화).
  = 또 다른 별개 엔진(Compiler Core)의 사전 materialized 결과.
```

---

## 경로 비교 (내 검증 경로 vs 실제 진단 경로)

| 항목 | 내가 검증한 경로 | 실제 유료진단 경로 |
|---|---|---|
| 진입점 | (없음 — VR 직접) | POST /diagnosis-engine/evaluate |
| 엔진 | applicability_conditions 적용 | Compiler Core (fetch_compiler_candidates) |
| 입력 | build_facility_profile(factories) | facility_applicability / task_candidate (사전 materialized) |
| 조건 수 | 14건 (ACTIVE) | 29,096 / 3,388건 |
| 의무 표현 | 구체 텍스트("경보설비") | family 코드("INSTALL_FAMILY") |
| 채우는 주체 | (런타임 평가) | 배치 스크립트 run_facility_applicability.py |

---

## 성공 기준 점검

```
실제 사용자 입력(유료진단/SaaS) 흐름 추적 → ✅
진짜 입력부 확인 → ✅ (Compiler Core / facility_applicability·task_candidate)
판정/원인분석/수정 안 함 → ✅
```

---

## 완료 문장

```
유료진단·SaaS 데이터의 실제 흐름을 추적하여 진짜 입력부를 확인하였다.
실제 유료진단은 Compiler Core(facility_applicability / task_candidate 사전
materialized 테이블)를 읽으며, 내가 PHASE 4~6에서 검증한
applicability_conditions(14건) 경로와는 다른 엔진이다.
```

---

## 이 발견이 뒤집는 것 (사실 기록, 판정 아님)

```
PHASE 4 결과공간(7종), PHASE 5 이상패턴(A~F), PHASE 6 PATTERN-C 대응표는
모두 내가 재현한 applicability_conditions(14건) 기준이었다.

실제 유료진단은 그 경로가 아니라 Compiler Core를 탄다.
→ 따라서 PHASE 4~6 결과는 "실제 진단 엔진의 결과"가 아니라
  "내가 재현한 14건 조건의 결과"였다.

  PATTERN-C("건설 의무 미출력")도 실제 진단이 아니라
  내 재현 경로에서 나온 것이다.
  실제 task_candidate(건설)에는 INSTALL/REPORT/APPOINT 등
  family 의무가 존재한다(건설 sector 1000+건).

= "건설 의무가 실제로 미출력인가"는 다시 실제 경로 기준으로
  측정해야 한다. (이 WO는 경로 확인까지. 재측정은 다음 WO.)
```

---

## 다음 단계 메모 (방향, 판정 아님)

```
지금까지의 검증(PHASE 4~6)은 실제 진단 엔진이 아닌 경로 기준이었음이 확인됨.
→ 마스터플랜의 "엔진"을 실제 경로(Compiler Core)로 재정의하고,
  PHASE 4(결과공간)부터 실제 경로 기준으로 다시 측정하는 것이
  방향으로 보임.
  단 이 WO는 입력부 확인까지. 재측정 여부·범위는 별도 지시.
```
