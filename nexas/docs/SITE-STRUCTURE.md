# new.taieng.co.kr — 사이트·파일 구조 (1차)

## A. 추천 사이트맵

| 경로 | 한글 역할 | 영문 slug (참고) |
|------|-----------|------------------|
| `/index.html` | 메인·전체 서비스 개요 | `/` |
| `/index-1.html` | TAI SAFE — 안전관리자 관점 랜딩 | `/tai-safe` |
| `/index-2.html` | TAI MANAGER — 통합 랜딩 + 관점 앵커 | `/tai-manager` |
| `/index-3.html` | TAI FIX — 통합 랜딩 + 관점 앵커 | `/tai-fix` |
| `/index-4.html` | TAI CARE — 통합 랜딩 + 관점 앵커 | `/tai-care` |
| `/index-5.html` | 안전정보(콘텐츠 허브) | `/safety-info` |
| `/index-6.html` | (예비) 별도 랜딩 또는 리다이렉트 | `/legacy-home-6` |
| `/log-in.html` | 로그인 | `/login` |
| `/mypage.html` | 마이페이지(플레이스홀더) | `/mypage` |
| `/contact.html` | 문의 | `/contact` |

**index-6**: 상단 메뉴는 `log-in.html` + `mypage.html`로 연결. `index-6.html`은 템플릿 변형 홈으로 남겨 두고, 추후 리다이렉트·삭제·통합 가능.

## B. 파일 배치안 (index-1 ~ 6 역할)

| 파일 | 1차 역할 |
|------|----------|
| `index-1.html` | TAI SAFE 소개 및 **안전관리자** 관점 랜딩 (앵커 `#manager`) |
| `index-2.html` | TAI MANAGER 소개 — **건물·공장 경영자** `#client` / **기술자·대행** `#partner` |
| `index-3.html` | TAI FIX — **경영자** `#client` / **수선업체** `#vendor` |
| `index-4.html` | TAI CARE — **안전관리자** `#manager` / **대행·진단업체** `#agency` |
| `index-5.html` | **안전정보** 리스트·요약형 |
| `index-6.html` | 미사용 우선순위 낮음 (기존 Home 06 템플릿) |

**추후 확장**: `tai-manager-owner.html` 등으로 분리 시 동일 앵커 URL 유지 권장(301).

## C. 헤더 1차 메뉴명 · 드롭다운

1. **TAI SAFE** — 링크만 (`index-1.html`)
2. **TAI MANAGER** — 하위: 건물·공장 경영자 / 기술자·대행업체
3. **TAI FIX** — 하위: 건물·공장 경영자 / 수선업체
4. **TAI CARE** — 하위: 안전관리자 / 안전대행·진단업체
5. **안전정보** — `index-5.html`
6. **계정** — 하위: 로그인, 마이페이지

## D. 메인(`index.html`) 서비스 유도

- 서비스 카드 5개: SAFE / MANAGER / FIX / CARE / 안전정보 → 각 `index-1`~`5`
- CTA 버튼: `문의하기` → `contact.html`

## E. 로그인·마이페이지

- **비회원**: 상단 `계정` → 로그인(`log-in.html`), 마이페이지는 로그인 유도 문구만(또는 동일 링크)
- **회원(추후)**: JS로 `계정` 표시를 `마이페이지` 단일 링크 + 로그아웃으로 전환

## F. 수정된·참고 파일

- `index.html`, `index-1.html` … `index-6.html`: 공통 한국어 네비
- `about.html`, `blog.html`, `blog-2.html`, `blog-3.html`, `blog-single.html`, `blog-single-2.html`, `blog-single-3.html`, `contact.html`, `faq.html`, `log-in.html`, `sign-up.html`, `service.html`, `service-details.html`, `team.html`, `team-details.html`: 동일 TAI 네비 + 우측 `문의하기`
- `index.html`: 서비스 카드 링크
- `index-1`~`index-4`: 섹션에 앵커 `id` 부여
- `mypage.html`: 마이페이지 플레이스홀더(로그인 유도 문구)
- `demo.html`: 테마 데모 전용 네비 유지(템플릿 쇼케이스)
