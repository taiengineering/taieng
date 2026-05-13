# Publish Gate Validation
## 2026-05-13

## 구현
- GET /engine-publish/publish-readiness/{id}: 6개 gate 검증
- POST /engine-publish/run-validation/{id}: regression + graph 실행
- POST /engine-publish/publish/{id}: READY_TO_PUBLISH에서만 가능
- POST /engine-publish/rollback/{id}: PUBLISHED에서만 가능

## 차단 규칙
- regression 실패 → publish 불가
- graph 실패 → publish 불가
- AI contamination → publish 불가
- mandatory drift → publish 불가
- explainability loss → publish 불가
