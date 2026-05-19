# Runtime Taxonomy v1.0

TAI Universal Runtime Candidate Taxonomy.
Engine-agnostic. Safe/Legal/Watch/Marketing 공통.

## Categories

| category | semantic | activation | schedule | escalation |
|----------|----------|------------|----------|------------|
| inspection | 점검/검사 수행 | ✅ required | ✅ periodic/one_time | ✅ |
| permit | 허가/승인 획득 | ✅ required | ✅ deadline | ✅ |
| report | 보고서 제출 | ✅ required | ✅ deadline | ✅ |
| training | 교육 수행 | ✅ required | ✅ periodic | ✅ |
| appointment | 선임/지정 | ✅ required | ❌ | ✅ |
| compliance_check | 준수 확인 | ✅ required | ✅ periodic | ✅ |
| notification_action | 알림 처리 | ❌ auto | ❌ | ❌ |
| marketing_action | 마케팅 후속조치 | ✅ optional | ✅ one_time | ❌ |
| governance_action | 거버넌스 조치 | ❌ auto | ❌ | ✅ |
| recovery_action | 복구 조치 | ❌ auto | ❌ | ✅ |
| approval_action | 승인 요청 | ✅ required | ✅ deadline | ✅ |
| review_action | 검토 요청 | ✅ required | ✅ deadline | ❌ |
| evidence_collection | 증빙 수집 | ✅ required | ✅ deadline | ✅ |
| document_submission | 문서 제출 | ✅ required | ✅ deadline | ✅ |
| workflow_action | 워크플로우 단계 | ✅ optional | ❌ | ❌ |

## Rules

1. candidate_type MUST be one of the above categories
2. New categories require RFC approval
3. category determines default runtime behaviors
4. Domain-specific data goes in payload.domain, never in candidate_type
