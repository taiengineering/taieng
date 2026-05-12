# TAI 프론트엔드 세션 메모리 — 2026-03-29

## 작업 대상 레포
- **repo**: taiengineering/tai-admin (main 브랜치)
- **배포**: Cloudflare Pages → admin.taieng.co.kr / taieng.co.kr
- **API**: https://api.taieng.co.kr

---

## 완료된 작업 목록

### 1. 탑메뉴 협력사관리 이동 — Cursor 프롬프트 작성
**대상**: 23개 HTML 파일 (auth-*.html, report-v1-viewer.html 제외)

**변경 내용**:
- 회원관리 서브메뉴에서 `협력사관리` 항목 제거
- 수선관리 서브메뉴 제일 위에 `협력사관리` 추가
- active 클래스 수정 금지
- 커밋 메시지: `refactor(menu): 협력사관리 회원관리→수선관리 상단 이동`

**현재 수선관리 서브메뉴 (변경 후 형태)**:
```html
<ul class="menu-sub">
  <li class="menu-item"><a href="member-list.html" class="menu-link"><div>협력사관리</div></a></li>
  <li class="menu-item"><a href="repair-list.html" class="menu-link"><div>수선관리</div></a></li>
  <li class="menu-item"><a href="repair-settle.html" class="menu-link"><div>정산관리</div></a></li>
</ul>
```

---

### 2. company-list.html 회사코드 컬럼 미노출
**커밋**: `450b770`
- 테이블 헤더: `회사코드` th 제거, `회사유형`에 ps-4 이동
- tbody: `company_code` 배지 td 제거
- colspan 11 → 10

---

### 3. company-list.html 등록/수정 폼 전면 개편
**커밋**: `e9bd16b`

**필드 변경 요약**:
| 항목 | 변경 |
|---|---|
| 회사유형 | 맨 위로 이동, 필수 |
| 회사명 | 필수 |
| 사업자번호 | 필수 |
| 법인번호 | **삭제** |
| 대표자 | 필수 |
| 연락처 | 필수 |
| 이메일 | 필수 |
| 설립일 | **삭제** |
| 주소 | 필수 |
| 상태 | DB 순서대로 출력 (견적요청중→견적확정→계약중→일시정지) |

**담당자 탭**: 이름/연락처/이메일 필수 `*` 표시 + 저장 전 검증
**서류 탭**: 사업자등록증 필수 `*` 표시 + 파일 미업로드 시 저장 차단

**validateCompanyForm() 검증 순서**:
1. 회사유형 선택 여부
2. 회사명 입력 여부
3. 사업자번호 입력 여부
4. 대표자명 입력 여부
5. 연락처 입력 여부
6. 이메일 입력 여부
7. 도로명주소 입력 여부 (cp-road 존재 시)
8. 사업자등록증 업로드 여부 (cp-biz-file-list 내 .tai-file-row 존재 시)

---

### 4. contract_status DB 재정렬
**DB**: system_codes 테이블

| code | code_name | sort_order | is_active |
|---|---|---|---|
| REQUESTED | 견적요청중 | 1 | true |
| CONFIRMED | 견적확정 | 2 | true |
| ACTIVE | 계약중 | 3 | true |
| SUSPENDED | 일시정지 | 4 | true |
| PENDING_PAYMENT | 입금대기 | - | false |
| EXPIRED | 만료 | - | false |
| CANCELLED | 해지 | - | false |
| TRIAL | 체험 | - | false |

---

### 5. factory-list.html 회사 셀렉트 전체 목록 로드 수정
**커밋**: `276ba42`

**원인**: `/companies?size=500` → API `size ≤ 100` 제한 → 422 오류 → `companiesList = []`

**수정**: `loadAllCompanies()` 함수 신규 추가
```js
async function loadAllCompanies() {
  let all = [], page = 1;
  while (true) {
    const data = await apiCall('GET', '/companies?size=100&page=' + page + '&sort=company_name&order=asc');
    const items = (data && data.data && data.data.items) || [];
    const total = (data && data.data && data.data.total) || 0;
    all = all.concat(items);
    if (all.length >= total || items.length === 0) break;
    page++;
  }
  return all;
}
```
- size=100 페이지네이션 루프로 전체 회사 로드
- 회사명 오름차순 정렬
- 시설 등록/수정 폼의 회사 선택에 전체 회사 표시

---

### 6. taieng.co.kr 로그인 게이트 구현

#### 6-1. login.html 신규 생성
**파일**: `site/full-version/html/front-pages/login.html`
**커밋**: `3a53f78`

**구조**:
- 좌측: TAI 브랜딩 (로고, 서비스 배지 4개)
- 우측: 로그인 폼 (이메일/휴대폰, 비밀번호, Google/카카오 소셜)
- API: `POST https://api.taieng.co.kr/auth/login`
- 성공 시: `access_token`, `user_name`, `user_email`, `role_code` 등 localStorage 저장 → `index.html` redirect
- 이미 로그인 상태이면: 페이지 로드 즉시 `index.html` redirect
- 토스트: 자체 구현 (Vuexy 의존성 없음)

**localStorage 저장 키**:
```
access_token, user_name, user_email, role_code, user_id,
company_id, factory_id, refresh_token, user(JSON)
```

#### 6-2. index.html 로그인 게이트 추가
**파일**: `site/full-version/html/front-pages/index.html`
**커밋**: `014719438`

**추가 내용**:
```html
<!-- <head> 최상단 (CSS 로드 전) -->
<script>
(function(){
  var token = localStorage.getItem('access_token');
  if(!token) location.replace('login.html');
})();
</script>
```

**Navbar 버튼 변경**:
- 미로그인: 로그인 버튼 + 회원가입 버튼 표시
- 로그인 상태: 사용자명 버튼 + 로그아웃 버튼 표시
- `doLogout()`: localStorage 전체 클리어 → `login.html` redirect

**히어로 CTA 버튼 변경**:
- `지금 시작하기 →` → `대시보드로 이동 →` (tadmin.taieng.co.kr/...index.html)

---

## 전체 플로우
```
taieng.co.kr 접속
    ↓
index.html 로드 (head 최상단 스크립트 실행)
    ↓ 토큰 없음
login.html
    ↓ 로그인 성공
index.html (홈페이지)
    ↓ 로그아웃 클릭
login.html
```

---

## API 제한사항 (누적)
- `/companies?size=` 최대 100 (500 → 422 오류)
- `/factories?size=` 최대 100
- apiCall 응답 구조: `{ status, data: { items, total } }`

## 파일별 현재 SHA
| 파일 | SHA |
|---|---|
| company-list.html | 9a5b112 |
| factory-list.html | 4b12a0b |
| site/index.html | 85aa01e |
| site/login.html | 신규 생성 |

## 미완료 / 다음 작업
- 로그아웃 무한루프 이슈 (admin 측) — 미해결
- Cursor 탑메뉴 협력사관리 이동 실행 — 대기 중
