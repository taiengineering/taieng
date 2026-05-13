# Cross-Graph Correctness Audit
## 2026-05-13

## 검증 대상
law → obligation → document → checklist → evidence

## 확인 항목
- obligation 있는데 document 없는가: 검증 대상
- mandatory document 있는데 checklist 후보 없는가: 검증 대상
- mandatory requirement 있는데 evidence 없는가: 검증 대상
- completeness가 mandatory 누락을 잡는가: 검증 대상
- source_trace 누락된 edge: 검증 대상

## 결과
Golden Scenario 50건 기반 graph 검증 구조 확보.
