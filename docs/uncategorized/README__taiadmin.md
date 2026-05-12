# 파트너 등록 설계 패키지

| 파일 | 설명 |
|------|------|
| [PARTNER_REGISTRATION_DESIGN.md](./PARTNER_REGISTRATION_DESIGN.md) | IA, UX, 유형별 섹션, 승인 흐름, 폴더 구조, 통합폼 비교 |
| [partner-registration.types.ts](./partner-registration.types.ts) | TypeScript 공통·유형별 상세 모델 |
| [api-payload-examples.md](./api-payload-examples.md) | REST payload 예시 |
| [react-example/](./react-example/) | React 라우트·랜딩·수선업체 폼 예시·훅 |

백엔드 구현 시 `partner_submissions` 단일 테이블 + `detail` JSON + `partner_type` 조합을 권장합니다.
