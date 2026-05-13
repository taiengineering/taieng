# Cross-Graph Consistency Validation
## 2026-05-13

## 검증 대상
law → obligation → document → checklist → evidence

## 탐지 대상
- orphan obligation/checklist/evidence
- impossible completeness (mandatory 누락 + creatable=true)
- contradictory mapping
- missing source_trace

## Event Types
- GRAPH_INCONSISTENCY
- UNSUPPORTED_COVERAGE_DETECTED
- OPERATIONAL_TRUTH_MISMATCH
