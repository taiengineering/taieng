# 파트너 회원 전환 · 일반회원 설계 (TAI)

Next.js/API/DB 도입 시 기준 문서. 프론트 네비·CTA는 **`GET /me` 응답의 `flags.canAccessPartnerDashboard`** 로 통일한다.

---

## 1. 프론트 단일 플래그: `canAccessPartnerDashboard`

- **역할**: 로그인 후 네비게이션(파트너 메뉴 노출), 마이페이지 CTA(「파트너 대시보드로 이동」 등)를 **한 필드**로 맞춘다.
- **의미**: `true`일 때만 파트너 전용 라우트(`/partner/*`) 접근·표시. `false`면 일반 마이페이지·전환 신청 흐름만 노출.
- **서버 계산**: `users.partner_role` 이 승인된 `SAFETY` / `REPAIR` 로 설정된 경우 등, 비즈니스 규칙에 따라 `true`로 계산해 내려준다. 신청 중(`UNDER_REVIEW` 등)만 있는 경우는 `false`.

### 응답 예시 (`GET /me`)

```json
{
  "user": { "id": "…", "email": "…", "accountRole": "USER" },
  "partner": {
    "role": "SAFETY",
    "isActive": true,
    "approvedAt": "2026-04-01T12:00:00.000Z"
  },
  "partnerApplication": {
    "id": "…",
    "type": "SAFETY",
    "status": "UNDER_REVIEW",
    "submittedAt": "…"
  },
  "flags": {
    "canAccessPartnerDashboard": false,
    "hasPendingPartnerApplication": true
  }
}
```

### 프론트 사용 규칙

| UI | 조건 |
|----|------|
| 파트너 대시보드 링크·탭 | `flags.canAccessPartnerDashboard === true` |
| 파트너 전환 신청 CTA | 승인 전: `!canAccessPartnerDashboard` + 신청 상태에 따라 문구 분기 |
| 라우트 가드 (`/partner/*`) | 동일 플래그 또는 403 응답 코드로 이중 방어 |

---

## 2. 비즈니스 요약

- 가입 직후 **모두 일반회원** (`account_role`: USER).
- 파트너 자격은 **전환 신청(`partner_applications`) → 검토 → 승인** 후에만 활성.
- 대외 UI: 「안전관리 파트너 등록」「시공/수선 업체 등록」 등 **진입은 분리**, 내부는 **동일 신청 파이프라인**.
- 홈 유입: 회원가입 직후 신청 폼으로 이어지게 하되, 내부적으로는 `user` 생성 + `partner_application` 생성.

---

## 3. 상태 (요약)

**계정**: 기본 USER. 승인 후 `users.partner_role` 등에 반영.

**신청(`partner_applications.status`)**:  
`NONE` → `DRAFT` → `SUBMITTED` → `UNDER_REVIEW` → `APPROVED` | `REVISION_REQUESTED` | `REJECTED`

**파트너 유형**: `SAFETY`, `REPAIR`

---

## 4. DB / API (요약)

- 테이블: `users`, `partner_applications`, `safety_partner_profiles`, `repair_partner_profiles`, `application_documents`, `application_status_logs` (상세는 구현 시 스키마 확정).
- API: `GET /me`, `GET /mypage/summary`, 파트너 신청 CRUD·제출, `GET /partner/me/dashboard` (승인자만), 관리자 승인·보완·반려 엔드포인트.

---

## 5. 정적 사이트 `nexas`와의 관계

- 현재 `taieng/nexas`는 **HTML/CSS 정적 페이지**. 위 플래그는 **백엔드 `GET /me` 연동 후** React/Next 또는 스크립트에서 소비한다.
- 비밀번호 찾기 등은 기존 `api.taieng.co.kr` 연동 패턴을 따른다.

---

## 6. Nexas 정적 사이트 작업 이력 (세션 기준)

다음은 본 저장소 `nexas` 쪽에서 진행·반영된 작업 요약이다.

| 구분 | 내용 |
|------|------|
| 다국어/카피 | 주요 페이지 한국어 정리, `lang="ko"`, 풋터·타이틀 패턴 통일 |
| 풋터 | 회사 정보 블록에서 **TEL / FAX 한 줄** 표기 (`TEL : … · FAX : …`) 로 통일 |
| 로그인 | **비밀번호 찾기**: 모달, 휴대폰 입력, `POST /auth/reset-password`, 토스트, `tai-auth.css` 모달 버튼 스타일 |
| 로그인 | 모달 닫기: `data-bs-dismiss` 클릭 방식 등 |
| 메인 `index.html` | 상단 히어로 **물류센터 느낌 Unsplash 제거**, 테마 기본 배너(`assets/img/banner/1.png`, `01.png`)로 복원 |
| 브랜딩 | `tai-brand.css`, `tai-auth.css` 등 공통 스타일 |

*(추가 작업은 본 문서 또는 커밋 메시지에 누적한다.)*

---

## 7. 참고

- 파트너 설계 상세(상태 전이, 라우팅, 관리자 흐름)는 팀 위키/이슈와 동기화할 것.
- `nexas` 내 문서: `nexas/docs/SITE-STRUCTURE.md`
