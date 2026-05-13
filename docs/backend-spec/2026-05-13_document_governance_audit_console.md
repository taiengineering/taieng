# Document Governance Audit Console
## 2026-05-13

## 8개 Tab
1. **요구사항 규칙** — Mandatory/Recommended 31건 표시
2. **Completeness Drift** — mandatory 누락 + creatable=true 탐지
3. **Rule Drift** — requirement level 변경
4. **Mandatory Drift** — recommended가 mandatory 동작
5. **Render Drift** — DB값 ≠ 렌더 결과
6. **PDF Artifact** — PDF ≠ snapshot
7. **Explainability** — source_trace 누락
8. **미지원 문서** — 추론 생성 시도

## 핵심: PDF는 artifact, Source of Truth = runtime structured data
