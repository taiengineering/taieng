# tadmin 계약 기반 메뉴 분기 작업지시서
## 담당: 프론트엔드 창

---

## 계약 구조 (확정)

### contracts 테이블 핵심 필드
```
contracts.service_type  = 'SAAS' | 'SAFETY' | 'CONSULTING' | 'REPAIR'
contracts.plan_code     = 'INDUSTRY_L1' ~ 'INDUSTRY_L4'
                        | 'FACILITY_L1' ~ 'FACILITY_L4'
contracts.addon_codes   = ['ADDON_EDU', 'ADDON_REPORT']  (배열)
contracts.status_code   = 'ACTIVE' | 'SUSPENDED' | 'EXPIRED'
```

### plan_code 파싱 규칙
```javascript
const planCode = 'INDUSTRY_L2';
const sector   = planCode.split('_')[0];          // 'INDUSTRY' | 'FACILITY'
const levelStr = planCode.split('_')[1];          // 'L1' ~ 'L4'
const level    = parseInt(levelStr.replace('L',''), 10);  // 1 ~ 4
```

### 기능 포함 범위
| 단계 | INDUSTRY | FACILITY |
|------|----------|----------|
| L1 | 시설+공정+설비+법정점검 | 시설+설비+법정점검+입주사관리 |
| L2 | L1+모델연결+자산관리 | L1+모델연결+에너지관리 |
| L3 | L2+AI위험예측 | L2+AI위험예측 |
| L4 | L3+커스터마이징 | L3+커스터마이징 |

### 애드온
- ADDON_EDU → 교육관리 메뉴 표시
- ADDON_REPORT → 신고관리 메뉴 표시 (없으면 무료 기본 제공 여부는 별도 결정)

---

## STEP 1. API — GET /contracts/my 응답 확인 (Code 창)

백엔드에서 로그인 사용자의 활성 계약 조회 시 아래 필드 포함 여부 확인:
```json
{
  "service_type": "SAAS",
  "plan_code": "INDUSTRY_L2",
  "addon_codes": ["ADDON_EDU"],
  "status_code": "ACTIVE"
}
```
없으면 Code 창에 추가 요청.

---

## STEP 2. 로그인 처리 — localStorage 저장

### 파일: auth-login-cover.html (tadmin)

로그인 성공 시 `/contracts/my` 호출 → localStorage 저장:

```javascript
async function afterLogin(token) {
  localStorage.setItem('access_token', token);

  // 계약 정보 조회
  try {
    const res = await apiCall('GET', '/contracts/my');
    const contract = (res.data && res.data.items && res.data.items[0]) || null;

    if (contract && contract.status_code === 'ACTIVE') {
      const planCode   = contract.plan_code || '';       // 'INDUSTRY_L2'
      const sector     = planCode.split('_')[0] || '';   // 'INDUSTRY'
      const levelStr   = planCode.split('_')[1] || 'L0'; // 'L2'
      const level      = parseInt(levelStr.replace('L',''), 10) || 0; // 2
      const addons     = contract.addon_codes || [];     // ['ADDON_EDU']
      const svcType    = contract.service_type || '';    // 'SAAS'

      localStorage.setItem('contract_plan_code',  planCode);
      localStorage.setItem('contract_sector',     sector);   // INDUSTRY | FACILITY
      localStorage.setItem('contract_level',      String(level)); // 1~4
      localStorage.setItem('contract_addons',     JSON.stringify(addons));
      localStorage.setItem('contract_service_type', svcType);
    } else {
      // 계약 없음 → FREE 상태
      localStorage.setItem('contract_plan_code',  '');
      localStorage.setItem('contract_sector',     'FREE');
      localStorage.setItem('contract_level',      '0');
      localStorage.setItem('contract_addons',     '[]');
      localStorage.setItem('contract_service_type', '');
    }
  } catch(e) {
    // 계약 조회 실패해도 로그인 진행 (FREE로 처리)
    localStorage.setItem('contract_sector', 'FREE');
    localStorage.setItem('contract_level', '0');
    localStorage.setItem('contract_addons', '[]');
  }

  location.replace('index.html');
}
```

---

## STEP 3. 공통 메뉴 파일 생성

### 파일: tadmin/full-version/assets/js/tai/menu-tadmin.js (신규)

```javascript
/**
 * menu-tadmin.js
 * 계약 기반 tadmin 메뉴 동적 렌더링
 * buildMenu(containerId) 호출 시 localStorage contract_* 값 기반으로 메뉴 생성
 */

(function() {

  // ── 헬퍼 ──────────────────────────────────────────
  function getContractInfo() {
    return {
      sector:      localStorage.getItem('contract_sector') || 'FREE',     // INDUSTRY | FACILITY | FREE
      level:       parseInt(localStorage.getItem('contract_level') || '0', 10), // 0~4
      addons:      JSON.parse(localStorage.getItem('contract_addons') || '[]'), // ['ADDON_EDU']
      serviceType: localStorage.getItem('contract_service_type') || '',   // SAAS | SAFETY | CONSULTING
    };
  }

  function hasAddon(addons, code) {
    return Array.isArray(addons) && addons.includes(code);
  }

  function currentPage() {
    return window.location.pathname.split('/').pop() || 'index.html';
  }

  function isActive(pages) {
    const cur = currentPage();
    return pages.some(p => cur.startsWith(p)) ? 'active' : '';
  }

  // ── 메뉴 정의 ───────────────────────────────────────
  //   visible: function(sector, level, addons, svcType) → bool
  //   sub: 서브메뉴 배열

  const MENU_DEFS = [
    {
      id: 'dashboard',
      label: '대시보드', icon: 'tabler-smart-home',
      href: 'index.html',
      pages: ['index.html'],
      visible: () => true,
    },
    {
      id: 'facility',
      label: '시설관리', icon: 'tabler-building',
      visible: (s, lv) => lv >= 1,
      sub: [
        { label: '시설관리',   href: 'factory-list.html',    visible: (s, lv) => lv >= 1 },
        { label: '공정관리',   href: 'process-select.html',  visible: (s, lv) => lv >= 1 && s === 'INDUSTRY' },
        { label: '설비관리',   href: 'my-equipment.html',    visible: (s, lv) => lv >= 1 },
        { label: '점검관리',   href: 'my-inspection.html',   visible: (s, lv) => lv >= 1 },
        { label: '모델관리',   href: 'facility-model.html',  visible: (s, lv) => lv >= 2 },
        { label: '입주사관리', href: 'tenant-list.html',     visible: (s, lv) => lv >= 1 && s === 'FACILITY' },
        { label: '에너지관리', href: 'energy-list.html',     visible: (s, lv) => lv >= 2 && s === 'FACILITY' },
      ]
    },
    {
      id: 'worker',
      label: '작업자관리', icon: 'tabler-users',
      visible: (s, lv) => lv >= 1 && s === 'INDUSTRY',
      sub: [
        { label: '작업자관리', href: 'worker-list.html',       visible: () => true },
        { label: '권한설정',   href: 'manager-permission.html',visible: () => true },
        { label: '하도급관리', href: 'worker-subcontract.html',visible: () => true },
      ]
    },
    {
      id: 'work',
      label: '작업관리', icon: 'tabler-clipboard-list',
      visible: (s, lv) => lv >= 1 && s === 'INDUSTRY',
      sub: [
        { label: '작업관리', href: 'work-list.html',    visible: () => true },
        { label: '작업요청', href: 'work-request.html', visible: () => true },
        { label: '일지관리', href: 'work-diary.html',   visible: () => true },
        { label: '작업설정', href: 'work-setting.html', visible: () => true },
      ]
    },
    {
      id: 'tbm',
      label: 'TBM관리', icon: 'tabler-clipboard-check',
      visible: (s, lv) => lv >= 1 && s === 'INDUSTRY',
      sub: [
        { label: 'TBM관리', href: 'tbm-list.html',    visible: () => true },
        { label: 'TBM설정', href: 'tbm-setting.html', visible: () => true },
      ]
    },
    {
      id: 'education',
      label: '교육관리', icon: 'tabler-school',
      visible: (s, lv, addons) => lv >= 1 && hasAddon(addons, 'ADDON_EDU'),
      badge: '애드온',
      sub: [
        { label: '교육관리', href: 'education-list.html',    visible: () => true },
        { label: '교육설정', href: 'education-setting.html', visible: () => true },
        { label: '설문조사', href: 'tai_survey_v5.html',     visible: () => true },
      ]
    },
    {
      id: 'risk',
      label: '위험관리', icon: 'tabler-alert-triangle',
      visible: (s, lv) => lv >= 1,
      sub: [
        { label: '위험성평가', href: 'risk-assessment.html', visible: () => true },
        { label: '사고관리',   href: 'risk-accident.html',   visible: () => true },
        { label: 'AI위험예측', href: 'risk-predict.html',    visible: (s, lv) => lv >= 3,
          badge: 'L3+' },
      ]
    },
    {
      id: 'doc',
      label: '문서관리', icon: 'tabler-files',
      visible: (s, lv) => lv >= 1,
      sub: [
        { label: '문서함',      href: 'doc-box.html',    visible: () => true },
        { label: '신고관리',    href: 'doc-report.html', visible: (s, lv, addons) => hasAddon(addons, 'ADDON_REPORT'),
          badge: '애드온' },
        { label: '문서신청',    href: 'doc-request.html',visible: () => true },
      ]
    },
    {
      id: 'mypage',
      label: '마이페이지', icon: 'tabler-user-circle',
      visible: () => true,
      sub: [
        { label: '공지사항',  href: 'index.html',              visible: () => true },
        { label: '알림센터',  href: 'notification-list.html',  visible: () => true },
        { label: '이용안내',  href: 'index.html',              visible: () => true },
        { label: '계약내역',  href: 'my-contract.html',        visible: () => true },
        { label: '법령진단',  href: 'my-diagnosis.html',       visible: () => true },
        { label: '문의하기',  href: 'contact.html',            visible: () => true },
      ]
    },
  ];

  // ── FREE(계약없음) 전용 메뉴 ─────────────────────────
  const FREE_MENU_DEFS = [
    {
      id: 'dashboard', label: '대시보드', icon: 'tabler-smart-home',
      href: 'index.html', pages: ['index.html'], visible: () => true,
    },
    {
      id: 'diagnosis', label: '법령진단', icon: 'tabler-scale',
      href: 'my-diagnosis.html', pages: ['my-diagnosis.html'], visible: () => true,
    },
    {
      id: 'mypage', label: '마이페이지', icon: 'tabler-user-circle',
      visible: () => true,
      sub: [
        { label: '계약내역', href: 'my-contract.html',       visible: () => true },
        { label: '법령진단', href: 'my-diagnosis.html',      visible: () => true },
        { label: '문의하기', href: 'contact.html',           visible: () => true },
      ]
    },
  ];

  // ── 렌더링 ──────────────────────────────────────────
  function renderMenuItem(def, sector, level, addons, svcType) {
    if (!def.visible(sector, level, addons, svcType)) return '';

    const cur = currentPage();

    if (def.href && !def.sub) {
      // 단일 링크
      const active = cur === def.href || (def.pages && def.pages.some(p => cur.startsWith(p))) ? 'active' : '';
      return `<li class="menu-item ${active}">
        <a href="${def.href}" class="menu-link">
          <i class="menu-icon icon-base ti ${def.icon}"></i>
          <div>${def.label}</div>
        </a>
      </li>`;
    }

    // 드롭다운
    const visibleSubs = (def.sub || []).filter(s => s.visible(sector, level, addons, svcType));
    if (!visibleSubs.length) return '';

    const subPages = visibleSubs.map(s => s.href);
    const isParentActive = subPages.some(p => cur.startsWith(p)) ? 'active' : '';

    const subItems = visibleSubs.map(s => {
      const sBadge = s.badge ? ` <span class="badge bg-label-primary ms-1" style="font-size:0.6rem;">${s.badge}</span>` : '';
      const sActive = cur.startsWith(s.href) ? 'active' : '';
      return `<li class="menu-item ${sActive}">
        <a href="${s.href}" class="menu-link">
          <div>${s.label}${sBadge}</div>
        </a>
      </li>`;
    }).join('');

    const pBadge = def.badge ? ` <span class="badge bg-label-warning ms-1" style="font-size:0.6rem;">${def.badge}</span>` : '';

    return `<li class="menu-item ${isParentActive}">
      <a href="javascript:void(0)" class="menu-link menu-toggle">
        <i class="menu-icon icon-base ti ${def.icon}"></i>
        <div>${def.label}${pBadge}</div>
      </a>
      <ul class="menu-sub">${subItems}</ul>
    </li>`;
  }

  // ── 업그레이드 유도 배너 ─────────────────────────────
  function renderUpgradeBanner(sector, level) {
    if (level >= 4) return ''; // L4는 최고 단계
    const next = level + 1;
    const features = {
      INDUSTRY: { 1: '모델·자산관리', 2: 'AI위험예측', 3: '커스터마이징' },
      FACILITY: { 1: '모델·에너지관리', 2: 'AI위험예측', 3: '커스터마이징' },
    };
    const feat = (features[sector] || {})[level] || 'Premium 기능';
    return `<!-- 업그레이드 배너: L${next}로 업그레이드 시 "${feat}" 사용 가능 -->`;
  }

  // ── 공개 API ────────────────────────────────────────
  window.buildMenu = function(containerId) {
    const container = document.getElementById(containerId || 'layout-menu');
    if (!container) return;

    const { sector, level, addons, serviceType } = getContractInfo();
    const defs = (sector === 'FREE' || level === 0) ? FREE_MENU_DEFS : MENU_DEFS;

    const html = defs
      .map(def => renderMenuItem(def, sector, level, addons, serviceType))
      .join('');

    const inner = container.querySelector('.menu-inner');
    if (inner) inner.innerHTML = html;

    // 업그레이드 배너 삽입 (body 최하단)
    const bannerHtml = renderUpgradeBanner(sector, level);
    if (bannerHtml) {
      const bannerEl = document.createElement('div');
      bannerEl.innerHTML = bannerHtml;
      // 필요시 실제 UI 배너로 교체
    }

    // sector를 body에 data 속성으로 노출 (CSS 테마 분기용)
    document.body.setAttribute('data-sector', sector.toLowerCase());
    document.body.setAttribute('data-level', String(level));
  };

  // ── 계약 정보 노출 헬퍼 ──────────────────────────────
  window.getContractInfo = getContractInfo;

  // ── 접근 제어 ────────────────────────────────────────
  // 특정 기능 페이지 진입 시 레벨 체크
  window.requireLevel = function(minLevel) {
    const { level } = getContractInfo();
    if (level < minLevel) {
      alert(`이 기능은 L${minLevel} 이상 계약이 필요합니다.`);
      history.back();
      return false;
    }
    return true;
  };

  window.requireAddon = function(addonCode) {
    const { addons } = getContractInfo();
    if (!hasAddon(addons, addonCode)) {
      alert('이 기능은 별도 애드온 구독이 필요합니다.');
      history.back();
      return false;
    }
    return true;
  };

})();
```

---

## STEP 4. 각 HTML 페이지 적용

### 기존 하드코딩 메뉴 → buildMenu() 교체

현재 모든 tadmin HTML에서:
```html
<!-- 기존 -->
<ul class="menu-inner">
  <li class="menu-item active">...</li>
  ...
</ul>
```

변경:
```html
<!-- 변경 후: menu-inner는 비워두고 JS로 채움 -->
<ul class="menu-inner"></ul>
```

스크립트 로드 순서 (body 하단):
```html
<!-- 기존 스크립트 다음에 추가 -->
<script src="../../assets/js/tai/menu-tadmin.js"></script>
<script>
  buildMenu('layout-menu');
</script>
```

### 적용 대상 파일 (tadmin 전체)
- index.html
- factory-list.html
- my-equipment.html
- my-inspection.html
- facility-model.html (기존 있음)
- worker-list.html
- manager-permission.html
- worker-subcontract.html
- work-list.html / work-request.html / work-diary.html / work-setting.html
- tbm-list.html / tbm-setting.html
- education-list.html / education-setting.html
- risk-assessment.html / risk-accident.html
- doc-box.html / doc-report.html / doc-request.html
- notification-list.html
- my-contract.html / my-diagnosis.html / contact.html
- process-select.html / tai_survey_v5.html

---

## STEP 5. 레벨 제한 페이지 적용

```javascript
// facility-model.html 상단 인증 블록에 추가
// 모델관리는 L2 이상
requireLevel(2);  // L2 미만이면 이전 페이지로 이동

// risk-predict.html (위험예측) — L3 이상
requireLevel(3);

// education-list.html — ADDON_EDU 필요
requireAddon('ADDON_EDU');

// doc-report.html — ADDON_REPORT 필요 (또는 무료 기본 제공 결정 후 적용)
requireAddon('ADDON_REPORT');
```

---

## STEP 6. 대시보드 계약 정보 표시

```javascript
// index.html 대시보드에서 현재 플랜 표시
const { sector, level, addons } = getContractInfo();
const sectorLabel = sector === 'INDUSTRY' ? '산업' : sector === 'FACILITY' ? '시설' : '무료';
const planLabel = level > 0 ? `${sectorLabel} L${level}` : '계약 없음';
// → 대시보드 헤더 배너에 표시
```

---

## 완료 기준
- [ ] menu-tadmin.js 파일 생성
- [ ] auth-login-cover.html 로그인 후 contract 정보 localStorage 저장
- [ ] index.html buildMenu() 적용 및 동작 확인
- [ ] INDUSTRY_L1: 시설/설비/점검만 표시, 모델 메뉴 없음 확인
- [ ] INDUSTRY_L2: 모델관리 메뉴 추가 표시 확인
- [ ] INDUSTRY_L3: AI위험예측 메뉴 추가 확인
- [ ] ADDON_EDU 없으면 교육관리 메뉴 미표시 확인
- [ ] FACILITY_L1: 입주사관리 표시, 공정/작업/TBM 미표시 확인
- [ ] FREE: 법령진단+계약내역+문의만 표시 확인
- [ ] tadmin 전체 HTML buildMenu() 교체 완료

## git commit
```
feat: tadmin 계약 기반 동적 메뉴 분기 (menu-tadmin.js)
```
