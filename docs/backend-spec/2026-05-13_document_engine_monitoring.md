# Document Engine Monitoring
## 2026-05-13

## 목적
Document Governance Integrity 실시간 감시.

## API (9 endpoints)
| Endpoint | 탐지 대상 |
|----------|----------|
| /document-monitoring/summary | 전체 요약 |
| /document-monitoring/completeness-drift | 동일 snapshot → 다른 creatable |
| /document-monitoring/rule-drift | Mandatory/Recommended 변경 |
| /document-monitoring/mandatory-drift | Recommended가 mandatory 동작 |
| /document-monitoring/render-drift | DB값 ≠ 렌더 결과 |
| /document-monitoring/pdf-artifact | PDF ≠ snapshot |
| /document-monitoring/explainability-audit | source_trace 누락 |
| /document-monitoring/unsupported-document | 미지원 문서 추론 |
| /document-monitoring/requirement-rules | 요구사항 규칙 조회 |

## 권한
- ROLE_ENGINE_ADMIN / ROLE_DOCUMENT_AUDITOR / ROLE_SUPER_ADMIN
- Worker/App 노출 금지
