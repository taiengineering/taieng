# Requirement Graph Correctness
## 2026-05-13

## 검증 graph
law → obligation → document → checklist → evidence

## 탐지 대상
- orphan obligation
- orphan checklist
- impossible completeness (mandatory + no document)
- missing document linkage
- broken evidence chain
- unsupported graph edge

## CRITICAL 예시
mandatory obligation 존재 + document 없음 → FAIL

## Event Types
- LEGAL_CORRECTNESS_FAIL
- REQUIREMENT_GRAPH_FAIL
- GOLDEN_SCENARIO_MISMATCH
- COMPLETENESS_MISMATCH
