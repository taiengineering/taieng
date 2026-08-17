# DECISION — safety_inspections.assignment_id 명명/FK 정합

> 2026-08-17 · Goal G-mswtdmi1-420f8c 별건 4
> 근거: 운영 DB(vwlahtguyggrhvslabax) 실측

## 사실

- `safety_inspections.assignment_id` 의 FK 는 **`work_schedules(id)`** 를 참조한다(컬럼명은 "assignment"이나 대상은 "schedule").
- 실측: 총 2행 중 assignment_id 채워진 건 **1행**, 그 값은 work_schedules 에 존재(work_assignments 에는 없음) → 컬럼은 **일정(schedule) 공간**.
- 이 불일치가 2026-08-17 제출 500(work_assignments.id 를 넣어 FK 위반)의 근본 원인이었고, **worker_check v1.4.1(#144)** 에서 `body.assignment_id` → `work_assignments.schedule_id` 변환 저장으로 근본 수정됨.

## 결정: **A (현 구조 유지) + 문서화**. B/C 는 유예.

이유:
1. 데이터가 사소(1행)하고 현재 코드가 정상 동작한다 — 즉시 스키마 변경의 실익이 작다.
2. "무엇을 링크해야 하는가(일정 vs 배정)"의 의미 결정은 **작업 전 점검/점검항목 마스터 기능이 엔진 대기로 파킹된 지금**이 아니라, **기능 재개 시점에 GPT·기획과 함께** 정하는 것이 옳다.
3. 스키마 변경(B/C)은 엔진/아키텍처 영역이며 임의로 하지 않는다.

## 대안 (재검토 시 참고)

- **B. FK → work_assignments(id) 로 이전** — 의미상 "배정을 링크". 단 기존 schedule_id 를 assignment_id 로 되돌리는 변환이 **1:다(한 일정에 배정 여럿)로 모호**. 코드도 body.assignment_id 직접 저장으로 변경.
- **C. 컬럼명 → schedule_id 로 rename** — 값이 이미 schedule 공간이라 데이터 변환 불필요. ALTER RENAME + 코드 참조(worker_check 저장부·판독부) 갱신 필요. 이름=내용=FK 일치.

## 재발 방지 (풋건 경고)

**`safety_inspections.assignment_id` 에는 `work_schedules.id`(=schedule_id)만 넣을 것.**
`work_assignments.id` 를 넣으면 FK 위반으로 500 이 난다. worker_check 는 이미 변환 저장(#144)하나, 다른 경로에서 이 컬럼에 값을 넣을 때 주의.

## 재검토 트리거

작업 전 점검 / 점검항목 마스터 기능의 **엔진 재작업이 끝나 기능이 언파킹될 때** — 그때 링크 대상(일정/배정)을 확정하고 필요하면 B 또는 C 를 GPT·기획과 함께 진행.
