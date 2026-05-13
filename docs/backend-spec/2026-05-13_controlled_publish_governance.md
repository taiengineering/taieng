# Controlled Publish Governance
## 2026-05-13

## 필수 흐름
```
detect → collect → diff → simulate → regression QA
→ graph validation → review → controlled publish → runtime activation
```

## Publish Gate (6개)
1. regression_qa: PASSED 필수
2. graph_validation: PASSED 필수
3. ai_contamination: 0 unresolved 필수
4. mandatory_drift: 0 unresolved 필수
5. unsupported_coverage: info only
6. explainability: 0 unresolved 필수

## CHECK 제약
- `chk_err_no_auto_publish`: regression PASSED 없이 publish 불가
- `chk_err_no_graph_fail_publish`: graph PASSED 없이 publish 불가
