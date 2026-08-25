# WP-PERSISTENCE-02 — IMPLEMENTATION SCOPE

- 작성일: 2026-08-25
- 상태: **BLOCKED (B1)**. 구현 지시서(FIND/REPLACE) 를 만들지 않는다.
- 아래는 B1 해제 시 예상되는 surface 의 윤곽일 뿐, 실행 지시가 아니다.

---

## 1. 왜 구현 지시서를 만들지 않는가

지시서 §7·§20·§22: form_schema mapping = NOT FOUND 이면
- 임의 매핑 설계 금지
- 구현 지시서 생성 금지
- blocker decision 을 먼저 제출

form_schema_id 는 runtime_document_data INSERT 의 필수 입력이며(create_document
시그니처가 요구), 그 정본이 없다. writer 를 지금 만들면 반드시 form_schema_id 를
추론하게 되어 원칙 위반. → 코드 지시서 생성을 중단한다.

## 2. B1 해제 시 예상 surface (윤곽만, 확정 아님)

| 파일 | 예상 성격 | 비고 |
|---|---|---|
| services/document_engine_svc.py | MODIFY (예상) | create_document 에 source_inspection_id 파라미터 추가 후보 |
| routers/inspection_checklist.py | MODIFY (예상) | **result 완료 전이** 직후 anchor 호출 부착 후보 (manual complete 경로는 B3 로 제외) |
| routers/worker_check.py | MODIFY (예상) | submit 완료 직후 anchor 호출 부착 후보 |
| schemas/document_engine.py | MODIFY (예상) | DocumentCreateIn 에 source_inspection_id 추가 후보 |
| (신규 orchestration service) | **지양** | NEW ENGINE 금지. 가능하면 기존 svc 에 작은 explicit 함수 |

- 위는 전부 **예상(후보)**이며, 실제 MODIFY/NEW/NO-CHANGE 확정은 B1 해제 후
  해당 시점 HEAD 재직독으로만 내린다. 예상 경로를 실제 경로처럼 쓰지 않는다.
- 새 orchestration engine 은 만들지 않는다. document_engine_svc 에 explicit
  `attach_source_inspection(...)` 류의 작은 함수 추가가 최소변경 방향(잠정).

## 3. 지금 확정된 MODIFY/NEW/NO-CHANGE

```
MODIFY     = (확정 불가 — B1)
NEW FILE   = 없음 (NEW ENGINE 금지 원칙 유지)
NO CHANGE  = 스키마 (컬럼/FK/UNIQUE 이미 LIVE, 변경 0)
           = inspection_bridge.py (읽기 전용, 이번 WP 변경 대상 아님)
```

## 4. 스키마 변경

- SCHEMA CHANGE = 0. source_inspection_id 컬럼·FK·UNIQUE 모두 이미 존재.
- 이번 WP 는 스키마를 만들지도 바꾸지도 않는다.

## 5. Legacy (STEP 11)

- 현재: safety_inspections=2, runtime_document_data=1, source_inspection_id populated=0.
- legacy backfill = 이번 WP 범위 아님. 과거 row 를 시간/factory 로 추론 연결 금지.
- backfill 필요 여부는 별도 migration/data-repair WP 로 판단.
- NEW WRITES(향후 writer 적용분)와 EXISTING ROWS(그대로 유지) 를 분리한다.
