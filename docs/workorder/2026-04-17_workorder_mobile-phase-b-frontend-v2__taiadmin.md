# 워크오더 — 모바일 Phase B (프론트엔드) v2

**작성일**: 2026-04-16 (v2: GPS + WebAuthn 추가)
**착수일**: 2026-04-17
**대상 창**: 프론트엔드 세션 (tai-admin)
**백엔드 연계**: `tai-api/docs/workorder-2026-04-17-mobile-phase-b-backend-v2.md`
**예상 소요**: 7일 (v1 4일 → v2 7일)

> 전체 내용은 이전 기획세션에서 작성됨. 핵심 항목만 요약.

## 핵심 변경 (v1→v2)
- GPS 수집 공통 함수 (`location.js`) 신규
- WebAuthn 공통 함수 (`webauthn.js`) 신규
- 생체인증 로그인 UI + 등록 모달
- `biometric-settings.html` 신규
- 기존 6개 페이지에 GPS 통합

## 역할 체계
| role | 한글 | 모바일 UI |
|---|---|---|
| WORKER | 작업자 | 현행 + GPS + 생체인증 |
| FOREMAN | 작업반장 | 확장 + GPS + 생체인증 |
| SAFETY_MANAGER | 안전관리자 | 신규 + GPS + 생체인증 |

## 신규 페이지
- `admin-dashboard.html` (안전관리자)
- `admin-ptw-approval.html` (안전관리자)
- `admin-alerts.html` (안전관리자)
- `foreman-tbm-mode.html` (작업반장)
- `foreman-ptw-create.html` (작업반장)
- `biometric-settings.html` (공통)

## 7일 일정
- Day 1: location.js + webauthn.js + role 분기
- Day 2: 생체인증 로그인 UI
- Day 3: GPS 통합 6개 페이지
- Day 4: 안전관리자 UI 3개
- Day 5: 작업반장 UI 2개
- Day 6: 통합 테스트
- Day 7: DAL + i18n + 에러 시나리오

## 주의사항
- WORKER UI 절대 손상 금지
- GPS 권한 거부해도 점검 진행 가능 (차단 금지)
- 생체인증 실패 시 OTP fallback 필수
- WebAuthn rpId = safe.taieng.co.kr 고정
