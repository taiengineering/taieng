# CURSOR-WO-DIAGNOSIS-SUBTYPE-CONTRACT-FIX-001 — sub_type 계약 복구

**작성일:** 2026-06-30 | **대상:** Cursor (로컬 편집 + git push) | **모드:** Execution. 계약 복구.
**목적:** DiagnosisService가 `diagnosis_candidate.sub_type`을 기존 계약 어휘로 저장하도록 복구. 새 설계/분류/매핑 아님. extract_setup_candidates 미수정.

---

## 확정 사실 (재분석 금지, 그대로 사용)
```
계약 위반 주체: DiagnosisService (확정 B).
원인: TYPE_MAP 키가 'REPORT'/'INSPECTION'/... 인데 실제 task_type 값은
      'REPORT_TASK_CANDIDATE'/'INSPECTION_TASK_CANDIDATE'/... (접미사 _TASK_CANDIDATE 포함)
      → TYPE_MAP.get(task_type) 전건 미스 → 기본값 'GENERAL'로 저장됨.
DB 직독 확인(session 5075acb6...): obligation candidate 전건 sub_type='GENERAL'.
  실제 task_type prefix: REPORT_TASK_CANDIDATE(58), INSTALL_TASK_CANDIDATE(54),
  MANAGE_TASK_CANDIDATE(13), INSPECTION_TASK_CANDIDATE(11), APPOINTMENT_TASK_CANDIDATE(10),
  VERIFY_TASK_CANDIDATE(10), NOTIFY_TASK_CANDIDATE(9), MEASURE_TASK_CANDIDATE(2),
  PRESERVE_TASK_CANDIDATE(1), TRAINING_TASK_CANDIDATE(1), RECORD_TASK_CANDIDATE(1).
extract_setup_candidates는 계약대로 sub_type을 읽고 있음 → 수정 대상 아님.
title_candidate는 표시용 → 분류에 사용하지 않음.
```

## 수정 대상 (단일)
```
파일: services/diagnosis_service.py   (DiagnosisService.evaluate 내부)
지점: TYPE_MAP 조회 한 곳.
  현재:
    TYPE_MAP = {'REPORT':'REPORT','INSTALL':'GENERAL','APPOINTMENT':'APPOINTMENT',
                'INSPECTION':'INSPECTION','EDUCATION':'EDUCATION','RECORD':'RECORD',
                'MEASUREMENT':'MEASUREMENT','PRESERVATION':'PRESERVATION',
                'SUBMIT':'REPORT','MAINTAIN':'GENERAL'}
    sub = TYPE_MAP.get(t.get('task_type'), 'GENERAL')
문제: t['task_type'] 값이 '<X>_TASK_CANDIDATE' 형식이라 키가 안 맞음.
```

## TASK-001 — task_type을 계약 키로 정규화 후 조회 (계약 복구)
```
원칙: 새 분류체계를 만들지 않는다. 기존 TYPE_MAP 어휘를 그대로 쓰되,
      실제 task_type 값('<X>_TASK_CANDIDATE')에서 계약 키(<X>)를 뽑아 매칭한다.
방법(둘 중 Cursor가 기존 코드 스타일에 맞는 것 택1, 새 헬퍼/매퍼 신설 금지):
  (a) 조회 직전 prefix 추출:
        tt = (t.get('task_type') or '')
        key = tt.split('_TASK_CANDIDATE')[0].split(':')[0].strip()   # 'REPORT_TASK_CANDIDATE' → 'REPORT'
        sub = TYPE_MAP.get(key, 'GENERAL')
  (b) TYPE_MAP 키를 실제 값 형식('<X>_TASK_CANDIDATE')으로 정렬.
권고: (a). TYPE_MAP(계약 어휘 값)은 그대로 두고 키 매칭만 복구 → 계약 불변.
```

## TASK-002 — 계약 어휘 매핑 표 (TYPE_MAP 기준, 신규 아님)
```
task_type prefix      → sub_type (기존 TYPE_MAP 값 그대로)
REPORT                → REPORT
SUBMIT                → REPORT
INSPECTION            → INSPECTION
EDUCATION             → EDUCATION
MEASUREMENT           → MEASUREMENT
PRESERVATION          → PRESERVATION
APPOINTMENT           → APPOINTMENT
RECORD                → RECORD
INSTALL               → GENERAL   (기존 계약: INSTALL=GENERAL)
MAINTAIN              → GENERAL
그 외(MANAGE/VERIFY/NOTIFY/TRAINING/MEASURE/PRESERVE 등 TYPE_MAP에 키 없음) → GENERAL (기존 기본값)
```
```
⚠ 주의(계약 범위 확인 필요 — Cursor가 임의 확장 금지):
  실제 데이터의 task_type prefix 중 MEASURE / PRESERVE / TRAINING 은
  TYPE_MAP의 키 MEASUREMENT / PRESERVATION / EDUCATION 과 철자가 다르다.
  (MEASURE_TASK_CANDIDATE vs 키 MEASUREMENT, PRESERVE vs PRESERVATION, TRAINING vs EDUCATION)
  → 이건 기존 TYPE_MAP 계약에 그 키가 그 철자로 정의돼 있지 않다는 뜻.
  이 철자 불일치를 Cursor가 임의로 새 키 추가(MEASURE→MEASUREMENT 등)하면 '새 매핑'이 되어 금지에 해당.
  따라서 TASK-001 (a) 방식으로 _TASK_CANDIDATE 접미사만 제거해 기존 키와 매칭하고,
  기존 키에 없는 prefix는 기존 기본값 GENERAL로 둔다(계약 그대로). 새 키 추가는 별도 대표 승인 사항.
```

## TASK-003 — extract_setup_candidates 미수정
```
services/saas_setup_service.py 변경 금지. 기존 그대로 사용.
```

## TASK-004 — 동일 E2E 재실행 (대표/Cursor — Claude 네트워크 OFF)
```
curl -X POST https://api.taieng.co.kr/api/v1/diagnosis-engine/evaluate \
  -H "Content-Type: application/json" \
  -d '{"factory_id":"e9c56af6-5de7-487d-bd2e-0d452291a562","input_data":{}}'
→ 응답 diagnosis_id 회신.
```

## TASK-005 — 확인 (PASS/FAIL만, 숫자분석 없음)
```
1. sub_type 저장값 정상   : diagnosis_candidate.sub_type 이 REPORT/INSPECTION/... 계약 어휘로 저장(전건 GENERAL 아님)
2. extract 호출 정상       : (non-blocking 훅 호출 — 로그 또는 적재로 확인)
3. saas_setup_candidate 생성: 새 session_id 기준 row 생성(approval_status='PENDING_USER_APPROVAL')
4. 기존 진단 결과 무변경    : 응답 구조/diagnosis_status 동일(COMPLETED_WITH_CANDIDATES), 기존 흐름 무파손
※ Claude가 새 diagnosis_id로 Supabase 직독해 1~3 판정. 4는 응답 구조 대조.
```

## Boundary
```
편집: services/diagnosis_service.py (DiagnosisService.evaluate의 TYPE_MAP 조회 1곳).
미수정: saas_setup_service.py / extract_setup_candidates / title_candidate 로직.
금지: 새 Mapper/Adapter/FieldMap/분류체계, 기존 키에 없는 새 sub_type 키 추가(대표 승인 시에만).
diagnosis_service.py는 GPT 영역(의무분류)이므로 Cursor는 TYPE_MAP 키 매칭 복구로 한정. 분류 의미 변경 금지.
단일 파일 PR. /health 503 금지.
```

*CURSOR-WO-DIAGNOSIS-SUBTYPE-CONTRACT-FIX-001 — 계약 위반 B 확정. DiagnosisService TYPE_MAP.get(task_type) 전건 미스(task_type='<X>_TASK_CANDIDATE' vs 키 '<X>')로 sub_type=GENERAL. 복구=task_type에서 _TASK_CANDIDATE 접미사 제거 후 기존 TYPE_MAP 키 매칭(새 매핑 아님). 기존 키 없는 prefix는 기존 기본값 GENERAL 유지. extract_setup_candidates 미수정. 동일 E2E 재실행→Claude DB 직독 PASS/FAIL.*
