# TAI Frontend MEMORY — 2026-04-06 세션 인계

## 오늘 완료된 작업 전체

### 1. engine-legal.html — 판정룰 탭 개선 ✅
- 필터: `filter-source` 셀렉트 추가 (전체 / AI생성 / 수동)
- 테이블 헤더: `출처 | 조건코드 | 상태` 3컨럼 추가
- `loadRules()`에 `source_api` 파라미터 전달
- `resetRulesFilter()`에 filter-source 초기화
- GitHub 에디터로 커밋 (56,671자)

### 2. engine-legal-ai.html — 조문 미리보기 ✅
- `renderDraftCards()` 함수에 `article_text` 첫 80자 미리보기 div 추가
- `-webkit-line-clamp:2` 스타일로 2줄 클램핑
- GitHub 엔에디터로 커밋 (59,505자)

### 3. contract-kmong.html / page.js / edit.html — 완료 ✅
- 경로: `admin/full-version/html/horizontal-menu-template/contract-kmong.html`
- 경로: `admin/full-version/assets/js/tai/contract-kmong.page.js`
- 경로: `admin/full-version/html/horizontal-menu-template/contract-kmong-edit.html`
- 실제 admin 레이아웃(수직사이드바 + 수평메뉴) 구조 적용
- menu-nav.js 계약관리 그룹에 `크몽` 항목 추가
- API 연동 확인: `GET /contract/kmong` → 200 OK
- escapeHtml 미정의 오류 수정 커밋 (d226ae7)
- contract-kmong.html 레이아웃 파일 전체 수정 커밋 (30c8f42)

### 4. engine-document.html — admin 완료 ✅
- 위치: `admin/full-version/html/horizontal-menu-template/engine-document.html`
- 탭 3개: 법정서식 / TAI표준서식 / 자유서식가이드
- API: `GET /engine/forms?form_type=LEGAL|STANDARD|FREE`
- menu-nav.js `엔진설정 > 문서관리` 항목 포함됨
- GitHub 엔디터로 커밋 (18983c7)

### 5. tai-safe.html 마케팅 사이트 리듀지인 ✅
- 경로: `site/full-version/html/tai-safe.html`
- 가격 템플릿 삽입 (쫐이 공개 → 실제 가격 3단조)
- 베이직 구독료: 79,000원/월
- 프리미엄 구독료: 149,000원/월
- 기업/공공기관: 별독 협의
- 법령진단 1회 서비스 (3개 카테고리) 추가
- 실제 코드: 15,983자

### 6. site/full-version/html/ 14개 파일 — footer 사업자정보 추가 ✅
파일 목록: about, apply-business, apply-manager, apply-repair,
contact-site-legacy, faq, for-repair, safety-news-detail, safety-news,
tai-care, tai-fix, tai-manager, tai-safe, terms

추가된 footer 정보:
- 사업자등록번호: 723-39-01422
- 주소: 서울특별시 강남구 테헤란로79길 6 JS타워 3층 브이 1314
- 전화번호: 010-4775-8888

---

## admin 페이지 작성 규칙 (확정)

| 항목 | 값 |
|------|----|
| 레이아웃 | 수직 사이드바 (layout-compact layout-menu-fixed) |
| assets 경로 | `../../assets/` |
| data-skin | `data-skin="default"` 필수 |
| dir | `dir="ltr"` 필수 |
| 아이콘 CSS | `iconify-icons.css` (remixicon 아님) |
| 메뉴 | menu-nav.js 공통 (`.menu-inner` 동적 렌더링) |
| 인증 | `localStorage.getItem('access_token')` |
| 로그아웃 | `doLogout()` (page.js에 정의) |
| API | `apiCall('GET', '/path')` (api.js 공통 함수) |
| 스크립트 필수 | globals.js, utils.js, notification.js, autocomplete-js.js |
| 파일구조 | `*.html` (shell) + `assets/js/tai/*.page.js` (로직) |
| 리스트규칙 | 1열=체크박스(toggleAll), 2열=No. |

---

## 다음 우선순위

1. 백엔드: `/engine/forms` API 구현 (form_type 파라미터)
2. 백엔드: `/engine-legal/rules` 응답에 `source_api`, `condition_code` 필드 추가
3. engine-legal-ai.html `draft=1` 모드 토글 정상화
4. 공지예외주장 제출 마감 **2026-04-28** (patent.go.kr)
5. Cloudflare Zero Trust Access 설정 (taieng.co.kr 잠금)
6. 혁신장터 등록 (business registration 이후)

---

## 주의 사항

- GitHub 엔디터 커밋시 **CM6 에디터 주입 성공 패턴**:
  ```js
  ce.focus();
  const range=document.createRange();range.setStart(ce,0);range.setEnd(ce,ce.childNodes.length);
  window.getSelection().removeAllRanges();window.getSelection().addRange(range);
  document.execCommand('insertText',false,content);
  ```
- github-tai MCP `push_files`에 content 직접 문자열 전달 불가 → 반드시 GitHub 엔디터 방식 사용
- window.name으로 쫐대량 파일 데이터 유지 (페이지 이동 후에도 유지됨)
- 엔디터 로드 대기: `for(let i=0;i<25;i++){...await 200ms}` 패턴
