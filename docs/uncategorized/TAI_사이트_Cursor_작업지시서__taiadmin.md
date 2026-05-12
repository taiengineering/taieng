# TAI Engineering 홈페이지 Cursor 작업지시서 v2.1

> 작성일: 2026-03-28 (v2.1 경로 수정)
> 기준 기획서: TAI_홈페이지_기획서_v2.0
> 작업 위치: `site/full-version/html/` (루트)

---

## ⚠️ 실제 배포 구조 (v2.1 수정사항)

| 항목 | 내용 |
|------|------|
| **HTML 파일 위치** | `site/full-version/html/` 루트 |
| **로고 경로** | `front-pages/assets/tai-logo.png` (상대경로 그대로 사용) |
| **_redirects** | `site/full-version/html/_redirects` → `/ /index.html 200` |
| **API** | `https://api.taieng.co.kr/...` (tai-api `site_public`·`auth` 라우터) |
| **Cloudflare Build output** | `site/full-version/html` |

> 📌 로고 img src: `front-pages/assets/tai-logo.png` (기획서의 `assets/tai-logo.png` 아님)

---

## ✅ 진행현황 (2026-03-28 기준)

| 파일 | 상태 | 수정 내용 |
|------|------|---------|
| `tai-safe.html` | ✅ 완료 | HERO/문제 3카드/ROI 섹션/요금(상담 후 안내)/하단 CTA v2 반영 |
| `coming-risk.html` | ✅ 완료 | Bootstrap·AOS 이후 알림 스크립트 실행, JS 중괄호 오류 수정 |
| `coming-inspection.html` | ✅ 완료 | 동일 수정 |
| `for-manager.html` | ✅ 완료 | Hero class 중복 제거, 고용 형태 섹션 추가 |
| `index.html` | 🔲 미완 | |
| `for-repair.html` | 🔲 미완 | |
| `tai-manager.html` | 🔲 미완 | |
| `tai-fix.html` | 🔲 미완 | |
| `tai-care.html` | 🔲 미완 | |
| `safety-news.html` | 🔲 미완 | |
| `safety-news-detail.html` | 🔲 미완 | |
| `faq.html` | 🔲 미완 | |
| `about.html` | 🔲 미완 | |
| `contact.html` | 🔲 미완 | DB 저장 방식 (POST /contacts) |
| `terms.html` | 🔲 미완 | |
| `apply-business.html` | 🔲 미완 | 2단계 폼 |
| `apply-manager.html` | 🔲 미완 | 2단계 폼 |
| `apply-repair.html` | 🔲 미완 | 2단계 폼 |

---

## ⚠️ JS 로드 순서 주의 (coming-risk/inspection 수정 교훈)

```html
<!-- 반드시 이 순서로 -->
<script src="bootstrap.bundle.min.js"></script>
<script src="aos.js"></script>
<script>
  AOS.init({ duration: 700, once: true });   <!-- AOS 먼저 -->
  // 이후 커스텀 스크립트 (알림 신청 등)
</script>
```

> ❌ 커스텀 JS를 Bootstrap/AOS보다 앞에 두면 동작 안 함
> ❌ JS 중괄호 누락 시 전체 스크립트 블록 실패 → 꼼꼼히 검증

---

## 📦 공통 CDN (모든 HTML `<head>`에 포함)

```html
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap" rel="stylesheet">
<link href="https://unpkg.com/aos@2.3.1/dist/aos.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css">

<!-- </body> 직전 — 반드시 이 순서 -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script src="https://unpkg.com/aos@2.3.1/dist/aos.js"></script>
<script>
  AOS.init({ duration: 700, once: true });
  window.addEventListener('scroll', () => {
    document.getElementById('mainNav').classList.toggle('shadow-sm', window.scrollY > 10);
  });
  // 페이지별 커스텀 JS는 여기 아래에
</script>
```

---

## 🎨 공통 CSS (모든 HTML `<style>`에 포함)

```css
body { font-family: 'Noto Sans KR', sans-serif; }
.fw-900 { font-weight: 900; }
.py-section { padding-top: 5rem; padding-bottom: 5rem; }
.hover-lift { transition: transform 0.2s, box-shadow 0.2s; }
.hover-lift:hover { transform: translateY(-4px); box-shadow: 0 1rem 2rem rgba(0,0,0,.08) !important; }
.btn-primary { background: #1A5FD4; border-color: #1A5FD4; }
.btn-primary:hover { background: #0F3F8F; border-color: #0F3F8F; }
.text-primary { color: #1A5FD4 !important; }
.bg-primary { background-color: #1A5FD4 !important; }
#mainNav { transition: box-shadow 0.2s; border-bottom: 1px solid #f1f1f1; }
```

---

## 🔗 공통 NAVBAR (전 페이지 동일)

```html
<nav id="mainNav" class="navbar navbar-expand-lg sticky-top bg-white">
  <div class="container">
    <a class="navbar-brand" href="index.html">
      <img src="front-pages/assets/tai-logo.png" alt="TAI Engineering" height="50">
    </a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navMenu">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navMenu">
      <ul class="navbar-nav mx-auto gap-1">
        <li class="nav-item dropdown">
          <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">서비스</a>
          <ul class="dropdown-menu">
            <li><a class="dropdown-item" href="tai-safe.html">TAI Safe</a></li>
            <li><a class="dropdown-item" href="tai-manager.html">TAI Manager</a></li>
            <li><a class="dropdown-item" href="tai-fix.html">TAI Fix</a></li>
            <li><a class="dropdown-item" href="tai-care.html">TAI Care</a></li>
            <li><hr class="dropdown-divider"></li>
            <li><a class="dropdown-item text-muted" href="coming-risk.html">위험성진단 <span class="badge bg-secondary ms-1">준비중</span></a></li>
            <li><a class="dropdown-item text-muted" href="coming-inspection.html">정밀안전점검 <span class="badge bg-secondary ms-1">준비중</span></a></li>
          </ul>
        </li>
        <li class="nav-item"><a class="nav-link" href="safety-news.html">안전정보</a></li>
        <li class="nav-item"><a class="nav-link" href="faq.html">FAQ</a></li>
        <li class="nav-item"><a class="nav-link" href="about.html">회사소개</a></li>
        <li class="nav-item"><a class="nav-link" href="contact.html">문의</a></li>
      </ul>
      <div class="d-flex gap-2">
        <a href="https://tadmin.taieng.co.kr/html/horizontal-menu-template/auth-login-cover.html"
           class="btn btn-outline-primary btn-sm px-3">로그인</a>
        <a href="https://tadmin.taieng.co.kr/html/horizontal-menu-template/auth-login-cover.html"
           class="btn btn-primary btn-sm px-3">서비스 신청 →</a>
      </div>
    </div>
  </div>
</nav>
```

---

## 🦶 공통 FOOTER

```html
<footer class="bg-dark text-white pt-5 pb-4">
  <div class="container">
    <div class="row g-4">
      <div class="col-lg-3">
        <img src="front-pages/assets/tai-logo.png" alt="TAI" height="40"
             style="filter: brightness(0) invert(1);" class="mb-3">
        <p class="text-white-50 small">Trusted AI for Industrial Safety<br>산업안전을 AI로 더 쉽고 정확하게</p>
      </div>
      <div class="col-lg-3">
        <h6 class="fw-bold mb-3">서비스</h6>
        <ul class="list-unstyled">
          <li class="mb-1"><a href="tai-safe.html" class="text-white-50 text-decoration-none small">TAI Safe</a></li>
          <li class="mb-1"><a href="tai-manager.html" class="text-white-50 text-decoration-none small">TAI Manager</a></li>
          <li class="mb-1"><a href="tai-fix.html" class="text-white-50 text-decoration-none small">TAI Fix</a></li>
          <li class="mb-1"><a href="tai-care.html" class="text-white-50 text-decoration-none small">TAI Care</a></li>
          <li class="mb-1"><a href="coming-risk.html" class="text-white-50 text-decoration-none small">위험성진단 <span class="badge bg-secondary">준비중</span></a></li>
          <li><a href="coming-inspection.html" class="text-white-50 text-decoration-none small">정밀안전점검 <span class="badge bg-secondary">준비중</span></a></li>
        </ul>
      </div>
      <div class="col-lg-3">
        <h6 class="fw-bold mb-3">이용안내</h6>
        <ul class="list-unstyled">
          <li class="mb-1"><a href="safety-news.html" class="text-white-50 text-decoration-none small">안전정보</a></li>
          <li class="mb-1"><a href="faq.html" class="text-white-50 text-decoration-none small">FAQ</a></li>
          <li class="mb-1"><a href="about.html" class="text-white-50 text-decoration-none small">회사소개</a></li>
          <li class="mb-1"><a href="contact.html" class="text-white-50 text-decoration-none small">이용문의</a></li>
          <li><a href="terms.html" class="text-white-50 text-decoration-none small">이용약관</a></li>
        </ul>
      </div>
      <div class="col-lg-3">
        <h6 class="fw-bold mb-3">회사 정보</h6>
        <p class="text-white-50 small mb-1">주식회사 TAI엔지니어링</p>
        <p class="text-white-50 small mb-1">대표: 심태왕</p>
        <p class="text-white-50 small mb-0">Email: tai@taieng.co.kr</p>
      </div>
    </div>
    <hr class="border-secondary mt-4">
    <p class="text-center text-white-50 small mb-0">© 2026 TAI Engineering. All rights reserved.</p>
  </div>
</footer>
```

---

## 📄 전체 페이지 목록 (18개)

| # | 파일명 | 상태 | 내용 |
|---|--------|------|------|
| 1 | index.html | 🔲 | 홈 (역할선택 모달 포함) |
| 2 | for-manager.html | ✅ | 선임기술자 전용 랜딩 |
| 3 | for-repair.html | 🔲 | 수선업체 전용 랜딩 |
| 4 | tai-safe.html | ✅ | TAI Safe 상세 |
| 5 | tai-manager.html | 🔲 | TAI Manager 상세 |
| 6 | tai-fix.html | 🔲 | TAI Fix 상세 |
| 7 | tai-care.html | 🔲 | TAI Care 상세 |
| 8 | coming-risk.html | ✅ | 위험성진단 준비중 |
| 9 | coming-inspection.html | ✅ | 정밀안전점검 준비중 |
| 10 | safety-news.html | 🔲 | 안전정보 게시판 목록 |
| 11 | safety-news-detail.html | 🔲 | 안전정보 게시판 상세 |
| 12 | faq.html | 🔲 | FAQ |
| 13 | about.html | 🔲 | 회사소개 |
| 14 | contact.html | 🔲 | 이용문의 (DB 저장) |
| 15 | terms.html | 🔲 | 이용약관 |
| 16 | apply-business.html | 🔲 | 기업 서비스 신청 (2단계) |
| 17 | apply-manager.html | 🔲 | 선임기술자 등록 (2단계) |
| 18 | apply-repair.html | 🔲 | 수선업체 등록 (2단계) |

---

## 🏠 [1] index.html — 홈

### 역할 선택 모달 (body 최상단)

```html
<div id="roleModal" class="position-fixed top-0 start-0 w-100 h-100 align-items-center justify-content-center"
     style="background:rgba(0,0,0,0.7); z-index:9999; backdrop-filter:blur(4px); display:none;">
  <div class="bg-white rounded-4 p-5 text-center" style="max-width:700px; width:90%;">
    <h3 class="fw-900 mb-2">어떤 서비스를 찾고 계신가요?</h3>
    <p class="text-muted mb-4">역할을 선택하면 맞춤 정보를 보여드립니다</p>
    <div class="row g-3 mb-4">
      <div class="col-md-4">
        <div class="card border-2 border-primary rounded-4 p-4 hover-lift h-100" style="cursor:pointer"
             onclick="selectRole('business')">
          <div class="fs-1 mb-2">🏢</div>
          <h5 class="fw-bold">기업 / 안전관리자</h5>
          <p class="text-muted small mb-0">법령진단·선임·수선·컨설팅</p>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card border-2 border-success rounded-4 p-4 hover-lift h-100" style="cursor:pointer"
             onclick="selectRole('manager')">
          <div class="fs-1 mb-2">👷</div>
          <h5 class="fw-bold">선임기술자</h5>
          <p class="text-muted small mb-0">안전관리자로 등록하기</p>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card border-2 border-warning rounded-4 p-4 hover-lift h-100" style="cursor:pointer"
             onclick="selectRole('repair')">
          <div class="fs-1 mb-2">🔧</div>
          <h5 class="fw-bold">수선업체</h5>
          <p class="text-muted small mb-0">시설 수선 의뢰 받기</p>
        </div>
      </div>
    </div>
    <div class="d-flex align-items-center justify-content-center gap-3">
      <div class="form-check mb-0">
        <input class="form-check-input" type="checkbox" id="noShow">
        <label class="form-check-label text-muted small" for="noShow">다시 보지 않기</label>
      </div>
      <button class="btn btn-link text-muted small p-0" onclick="closeModal()">닫기</button>
    </div>
  </div>
</div>
<!-- Bootstrap·AOS 로드 이후에 위치 -->
<script>
  if (!localStorage.getItem('tai_role_selected')) {
    document.getElementById('roleModal').style.display = 'flex';
  }
  function selectRole(role) {
    if (document.getElementById('noShow').checked)
      localStorage.setItem('tai_role_selected', 'true');
    if (role === 'manager') location.href = 'for-manager.html';
    else if (role === 'repair') location.href = 'for-repair.html';
    else closeModal();
  }
  function closeModal() {
    document.getElementById('roleModal').style.display = 'none';
  }
</script>
```

### 섹션 구성

1. **HERO** (min-height:85vh) — "이걸 혼자 다 하고 계신가요?" + 법령진단 모의 카드
2. **신뢰 지표 바** (#1A5FD4) — 396개 / 118만건 / 67개 / 24시간
3. **문제 제기** — 📋😓⚠️ 3카드
4. **서비스 카드** — 4종 + 준비중 2개
5. **이용 프로세스** — STEP 1→2→3
6. **고객 후기** — ⭐⭐⭐⭐⭐ 3카드
7. **CTA 클로징** (#1A5FD4→#0F3F8F)

---

## 👷 [2] for-manager.html ✅ 완료

- Hero: 초록 배경 / "수수료 걱정 없이, 일감 걱정 없이"
- 문제 3카드: 💸수수료 / 📞연락빈도 / 📋단가
- 검증: 자격증→Q-Net→TAI Verified→매칭
- 고용형태: 상주 / 비상주 / 겸직 (섹션 추가 완료)
- CTA: [기술자 등록하기] → apply-manager.html

---

## 🔧 [3] for-repair.html

- Hero: 주황 배경 / "검증된 의뢰만, 투명한 수수료로"
- 문제 3카드: 📦물량 / 🎯매칭 / 💰수수료
- 검증: 사업자→국세청→면허→인증배지→우선매칭
- CTA: [업체 등록하기] → apply-repair.html

---

## 🔵 [4] tai-safe.html ✅ 완료

- Hero: 파란 배경 / "아직도 엑셀로 선임 관리하고 계신가요?"
- 문제: 법적리스크 / 관리누락 / 업무과부하
- 해결 (좌우 2단): 기능 4개 + 대시보드 CSS 목업
- **ROI 섹션 (핵심)**: ⏰업무시간 절감 / ⚖️법적 리스크 최소화 / 📊보고 자동화
- 요금: "서비스 요금은 상담 후 안내드립니다" + [무료 상담 신청]

---

## 🟢 [5] tai-manager.html

- Hero: 초록 배경 / "안전관리자 선임 의무, 아직도 혼자 해결하고 계신가요?"
- 프로세스: ①요건진단→②매칭요청→③검증인력→④계약완료
- 고용형태 카드 3종
- 수수료: "상담 후 안내드립니다"

---

## 🟠 [6] tai-fix.html

- Hero: 주황 배경 / "수선업체 찾기, 아직도 지인에게 묻고 계신가요?"
- 수수료: "수수료는 상담 후 확정됩니다. 숨겨진 비용은 없습니다."
- 프로세스: ①의뢰등록→②업체매칭→③견적확인→④계약진행

---

## 🔴 [7] tai-care.html

- Hero: 다크블루 / "사고 한 번이면 끝입니다"
- 3등급 비교 (모두 "요금 상담 후 안내"):
  - Lite: 법령진단 리포트 + 개선 권고안
  - Plus (추천): Lite + 현장방문 + 컨설팅
  - Pro: Plus + 전담관리사 + 분기점검

---

## 🔒 [8][9] 준비중 페이지 ✅ 완료

**핵심 수정사항**: Bootstrap·AOS 로드 이후 알림 스크립트 실행 (JS 중괄호 오류 수정 완료)

```html
<!-- Bootstrap·AOS 스크립트 이후에 -->
<script>
  AOS.init({ duration: 700, once: true });
  // 알림 신청 폼
  document.getElementById('alertForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const email = document.getElementById('alertEmail').value;
    try {
      const res = await fetch('https://api.taieng.co.kr/notification-requests', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          service_type: 'RISK_DIAGNOSIS' // coming-inspection.html은 'INSPECTION'
        })
      });
      if (res.ok) alert('신청 완료! 오픈 시 이메일로 알려드리겠습니다.');
      else alert('오류가 발생했습니다. 잠시 후 다시 시도해 주세요.');
    } catch {
      alert('오류가 발생했습니다.');
    }
  });
</script>
```

---

## 📋 [10][11] 안전정보 게시판

```javascript
// 목록
const res = await fetch(`https://api.taieng.co.kr/posts?category=${cat}&page=${p}&size=9`);
// 상세
const id = new URLSearchParams(location.search).get('id');
const res = await fetch(`https://api.taieng.co.kr/posts/${id}`);
```
⚠️ API 없을 시: 더미 5개 카드 UI 구현 후 주석으로 API 연동 예정 표시

---

## ❓ [12] faq.html

탭 4개 (Bootstrap Tab + Accordion):
- 서비스 이용 / 회원·가입 / 결제·계약 / 기술자·업체
- **요금 관련**: 모두 "서비스별 요금은 상담 후 안내드립니다"
- **수수료 관련**: "수수료는 상담 후 확정됩니다"

---

## 📩 [14] contact.html — DB 저장 방식

```javascript
document.getElementById('contactForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const data = {
    name: document.getElementById('name').value,
    company_name: document.getElementById('company').value,
    email: document.getElementById('email').value,
    phone: document.getElementById('phone').value,
    inquiry_type: document.getElementById('inquiry_type').value,
    content: document.getElementById('content').value,
    source: 'taieng.co.kr'
  };
  try {
    const res = await fetch('https://api.taieng.co.kr/contacts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (res.ok) alert('문의가 접수됐습니다. 24시간 이내 연락드리겠습니다.');
    else alert('오류가 발생했습니다. 잠시 후 다시 시도해 주세요.');
  } catch {
    alert('오류가 발생했습니다. tai@taieng.co.kr 로 직접 연락해 주세요.');
  }
});
```

문의 유형: TAI Safe / TAI Manager / TAI Fix / TAI Care / 위험성진단 / 정밀안전점검 / 기타

---

## 🧩 [16][17][18] 2단계 신청 폼

### apply-business.html (기업)
```
STEP 1: 이름 / 이메일 / 비밀번호 / 비밀번호확인 / 휴대폰
STEP 2: 회사명 / 사업자등록번호+[국세청검증] / 대표자명 / 업태 / 종목 / 주소(JUSO) / 세금계산서이메일 / 신청서비스(복수)
```

### apply-manager.html (선임기술자)
```
STEP 1: 이름 / 이메일 / 비밀번호 / 비밀번호확인 / 휴대폰
STEP 2: 자격증종류 / 자격증번호+생년월일+[Q-Net검증] / 경력년수 / 활동지역(다중) / 고용형태희망
```

### apply-repair.html (수선업체)
```
STEP 1: 이름 / 이메일 / 비밀번호 / 비밀번호확인 / 휴대폰
STEP 2: 업체명 / 사업자번호+[국세청검증] / 대표자명 / 수선분야(다중) / 활동지역(다중) / 면허번호(선택)+[인허가검증] / 최대공사금액
```

### 검증 버튼 UI 패턴
```javascript
// 성공
btn.innerHTML = '<i class="bi bi-check-circle-fill text-success"></i> 검증 완료';
input.classList.add('is-valid');
// 실패
btn.innerHTML = '<i class="bi bi-x-circle-fill text-danger"></i> 검증 실패';
input.classList.add('is-invalid');
```

---

## 📌 CTA 연결

| 버튼 | URL |
|------|-----|
| 서비스 신청하기 | https://tadmin.taieng.co.kr/html/horizontal-menu-template/auth-login-cover.html |
| 소개서 받기 | mailto:tai@taieng.co.kr?subject=TAI 소개서 요청 |
| 문의 폼 제출 | POST https://api.taieng.co.kr/contacts |
| 오픈 알림 | POST https://api.taieng.co.kr/notification-requests |

---

## ✅ 완료 체크리스트 (15개)

```
□ 1. 역할 선택 모달 동작 (localStorage 저장)
□ 2. NAVBAR 전 페이지 동일 + 준비중 배지
□ 3. FOOTER 전 페이지 동일
□ 4. 로고: front-pages/assets/tai-logo.png (일반/다크 배경 처리)
□ 5. 모바일 반응형 전 페이지 (768px 이하)
□ 6. AOS 스크롤 애니메이션 동작
□ 7. 서비스 신청 버튼 → tadmin 로그인 링크
□ 8. 문의 폼 → POST /contacts (실패 시 이메일 안내)
□ 9. 준비중 페이지 알림 신청 폼 동작
□ 10. FAQ Accordion 탭 전환 동작
□ 11. 2단계 신청 폼 STEP 전환 정상
□ 12. 사업자번호 검증 버튼 UI (성공/실패)
□ 13. 자격증 검증 버튼 UI (성공/실패)
□ 14. 모든 요금 관련 → "상담 후 안내" 문구 통일
□ 15. JS 로드 순서 확인 (Bootstrap→AOS→커스텀 JS)
```
