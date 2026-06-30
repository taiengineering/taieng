# WO-PIPELINE-CONNECTION-001 — 최종 출력까지 다음 연결점 1개

**작성일:** 2026-06-29 | **성격:** 읽기 전용 규명(연결점 식별까지). 새 설계·복원 논의 0. 실데이터 기준.
**목표:** Consumer Input → Engine → Output → SaaS → 진단서 까지 연결. 이번 WO는 **가장 앞 BROKEN 1개 식별**까지.

---

## TASK-001 — 현재 파이프라인 한 줄 (실데이터 동반)
```
소비자입력(diagnosis_input_fields 100)
  → normalize_consumer_inp → create_temp_factory(임시 factories)
  → 엔진 평가(facility_applicability_eval)
  → 진단결과 저장 (anonymous_diagnosis_results 172 / factory_diagnosis_results 7)
  → [SaaS 운영] saas_setup_candidate 50 → runtime_obligation_assignment 0 → runtime_task 339 → runtime_task_activation 0
  → 구독/결제 (subscriptions 32 / diagnosis_purchases 16)
  → 진단서(safety_reports 0 / 안전관리설계서 테이블 없음)
```

## TASK-002 — 단계별 상태 (CONNECTED / BROKEN / BYPASS)
```
① 소비자입력 → 정규화           CONNECTED  (normalize_consumer_inp 라이브)
② 정규화 → 엔진 평가            CONNECTED  (create_temp_factory → eval)
③ 엔진 → 진단결과 저장          CONNECTED  (anon 172 / fdr 7 적재됨)
④ 진단결과 → SaaS 셋업후보       CONNECTED  (saas_setup_candidate 50 존재)
⑤ SaaS 셋업 → 의무 배정          BROKEN     (runtime_obligation_assignment 0)   ★가장 앞 BROKEN
⑥ 의무배정 → 작업 활성화         BROKEN     (runtime_task_activation 0; runtime_task 339는 마스터/후보)
⑦ 작업 → 진단서/안전관리설계서    BROKEN     (safety_reports 0, 설계서 테이블 없음)
보조: 결제(subscriptions 32 / purchases 16)  CONNECTED
보조: obligation_instance(171)→진단서 경로     BYPASS    (테스트 1시설만, 운영 미연결)
```

## TASK-003 — BROKEN만 추림
```
⑤ SaaS 셋업후보 → runtime_obligation_assignment   (0건)
⑥ 의무배정 → runtime_task_activation              (0건)
⑦ 작업/의무 → 진단서(safety_reports / 안전관리설계서)  (0건/테이블 없음)
```

## TASK-004 — 가장 앞 BROKEN 1개 선택
```
★ ⑤ saas_setup_candidate(50) → runtime_obligation_assignment(0)
   = SaaS 셋업 후보는 50건 생겼는데, 시설별 "의무 배정"으로 한 단계도 넘어가지 못함.
   이 한 칸이 막혀 ⑥ 작업활성화·⑦ 진단서가 전부 0.
   → 진단결과(④)까지는 흐르나, SaaS 운영(의무→작업→진단서)으로 들어가는 첫 관문이 ⑤.
```

## TASK-005 — 연결 실행 (이번 WO 범위 = 위치 확정 + 실행 핸드오프)
```
연결 대상: saas_setup_candidate → runtime_obligation_assignment 적재 1개.
확인 필요(다음 단계, 읽기):
  - saas_setup_candidate 스키마/상태값 (어떤 후보가 배정 대기인지)
  - runtime_obligation_assignment 적재 계약 (factory_id, obligation, status 컬럼)
  - 이 적재를 수행하는 기존 서비스/엔드포인트가 있는지(있으면 실행, 없으면 그 지점이 진짜 BROKEN)
실행 주체: 적재 로직이 대형 서비스 파일/엔진 영역이면 Cursor 핸드오프, 단순 상태전이면 위치 확정 후 보고.
※ 이번 WO에서 ⑥⑦은 건드리지 않음(가장 앞 1개만).
```

## TASK-006 — 성공 기준
```
복원 완료가 아님. "⑤ saas_setup_candidate → runtime_obligation_assignment 한 칸이 연결되어
데이터 1건이라도 흐르는가"가 성공 기준. 그 다음에 ⑥으로 이동.
```

## 다음 액션 (단일)
```
saas_setup_candidate / runtime_obligation_assignment 두 테이블의 스키마·상태값·기존 적재 서비스 유무를
읽기로 확인 → ⑤ 연결점의 정확한 코드 위치(또는 부재) 확정 → 실행 or Cursor 핸드오프.
```

## Boundary 준수
```
읽기 전용(식별). 새 설계/복원 논의/과거 분석 반복 0. 가장 앞 BROKEN 1개(⑤)만 선택. ⑥⑦ 미접촉.
```

*WO-PIPELINE-CONNECTION-001 — 현재 ①~④ CONNECTED(진단결과까지 흐름), ⑤ saas_setup_candidate(50)→runtime_obligation_assignment(0) = 가장 앞 BROKEN. 다음: ⑤ 두 테이블 스키마·기존 적재 서비스 확인 → 연결점 코드 위치 확정.*
