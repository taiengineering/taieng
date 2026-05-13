# Engine Release Pipeline
## 2026-05-13

## Release Status Lifecycle
```
DRAFT → QA_PENDING → QA_FAILED / READY_TO_PUBLISH
READY_TO_PUBLISH → PUBLISHED
PUBLISHED → ROLLED_BACK
```

## Release Types
LAW_UPDATE, REQUIREMENT_UPDATE, MAPPING_UPDATE,
DOCUMENT_RULE_UPDATE, ENGINE_PATCH, HOTFIX

## Rollback 조건
- obligation drift 폭증
- regression failure 증가
- completeness corruption
- mass obligation contamination

## 절대 금지: mass instant activation
