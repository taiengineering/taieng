# Runtime Snapshot Sync Validation
## 2026-05-13

## 탐지 대상
- stale snapshot
- snapshot mismatch
- delayed propagation
- inconsistent completeness state

## CRITICAL 예시
동일 snapshot hash인데 completeness 결과 다름 → CRITICAL
