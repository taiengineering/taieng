# 프론트엔드 작업지시서 — F-FEAT-001
# 섹터 × 플랜 Feature Flag 기반 블록 제어

> 작성일: 2026-04-01  
> 우선순위: 🟡 중요  
> 작업 대상: tadmin 공통 JS 맨 신규 생성 + 메뉴 적용

---

## 배경

**핵심 개념:** 틀(화면)은 하나, 블록을 섹터+플랜 조합으로 열거나 잠근다.

| 상태 | 의미 | 표시 |
|------|------|------|
| open | 셀터 일치 + 플랜 충족 | 정상 렌더링 |
| locked | 셀터 일치이지만 플랜 부족 | 잠금 UI + 업그레이드 안내 |
| hidden | 셀터 불일치 | `d-none` 완전 숨김 |

---

## 작업 1 — feature-flags.js 신규 생성

**파일:** `assets/js/feature-flags.js`

```javascript
/**
 * TAI Safe Feature Flag 시스템
 * 셀터 + 플랜 조합 기반으로 tadmin 블록 제어
 */

const TAIFeatureFlags = {
  flags: { open: [], locked: [], hidden: [] },
  loaded: false,

  /**
   * API에서 feature flags 로드
   * @param {string} sector - INDUSTRY / BUILDING / CONSTRUCTION / SPECIAL
   * @param {string} plan   - STARTER / BUSINESS / ENTERPRISE / CUSTOM
   */
  async load(sector, plan) {
    try {
      const res = await fetch(
        `${API_BASE_URL}/feature-flags/?sector=${sector}&plan=${plan}`,
        { headers: { 'Authorization': `Bearer ${getToken()}` } }
      );
      const json = await res.json();
      if (json.status === 'success') {
        this.flags = json.data;
        this.loaded = true;
        this.apply();
      }
    } catch (e) {
      console.error('[FeatureFlag] 로드 실패:', e);
    }
  },

  /**
   * DOM에 블록 제어 적용
   * data-feature="FEATURE_CODE" 속성을 가진 요소를 대상으로 제어
   */
  apply() {
    const openCodes   = this.flags.open?.map(f => f.feature_code) || [];
    const lockedFlags = this.flags.locked || [];
    const hiddenCodes = this.flags.hidden || [];

    document.querySelectorAll('[data-feature]').forEach(el => {
      const code = el.dataset.feature;

      if (hiddenCodes.includes(code)) {
        // 셍터 불일치 → 완전 숨김
        el.classList.add('d-none');

      } else if (openCodes.includes(code)) {
        // 정상 오픈
        el.classList.remove('d-none');
        el.querySelector('.feature-lock-overlay')?.remove();

      } else {
        // 잠김 (locked)
        const lockInfo = lockedFlags.find(f => f.feature_code === code);
        const required = lockInfo?.required_plan || 'BUSINESS';
        el.classList.remove('d-none');
        this._applyLockOverlay(el, required);
      }
    });
  },

  /**
   * 잠김 오버레이 UI 삽입
   */
  _applyLockOverlay(el, requiredPlan) {
    if (el.querySelector('.feature-lock-overlay')) return;
    const overlay = document.createElement('div');
    overlay.className = 'feature-lock-overlay';
    overlay.innerHTML = `
      <div class="feature-lock-content">
        <i class="ti ti-lock text-muted fs-4"></i>
        <p class="mb-1 text-muted small"><strong>${requiredPlan}</strong> 이상에서 사용 가능</p>
        <a href="/pricing.html" class="btn btn-sm btn-outline-primary">업그레이드</a>
      </div>
    `;
    el.style.position = 'relative';
    el.appendChild(overlay);
  },

  /**
   * 특정 feature_code가 열린 상태인지 확인
   */
  isOpen(code) {
    return this.flags.open?.some(f => f.feature_code === code) || false;
  }
};

// CSS 주입
(function injectLockStyle() {
  const style = document.createElement('style');
  style.textContent = `
    .feature-lock-overlay {
      position: absolute; inset: 0;
      background: rgba(255,255,255,0.85);
      backdrop-filter: blur(2px);
      display: flex; align-items: center; justify-content: center;
      border-radius: 8px; z-index: 10;
    }
    .feature-lock-content { text-align: center; padding: 16px; }
  `;
  document.head.appendChild(style);
})();
```

---

## 작업 2 — 메뉴 data-feature 속성 적용

**파일:** `assets/js/menu-tadmin.js`

각 메뉴 아이템에 `data-feature` 속성 추가.

```javascript
// menu-tadmin.js의 메뉴 아이템 구조 예시
const MENU_ITEMS = [
  // 공통
  { code: 'DASHBOARD',               label: '대시보드',           icon: 'ti-home',          href: 'dashboard.html' },
  { code: 'LEGAL_DIAGNOSIS_BASIC',   label: '법령진단',           icon: 'ti-scale',         href: 'diagnosis/diagnosis-step1.html' },
  { code: 'WORK_ASSIGN',             label: '업무할당',            icon: 'ti-clipboard-list',href: 'work/work-assign.html' },
  { code: 'EDUCATION_BASIC',         label: '교육관리',            icon: 'ti-school',        href: 'education/education-list.html' },
  // INDUSTRY
  { code: 'FACILITY_BASIC',          label: '시설관리',            icon: 'ti-building',      href: 'facility/factory-list.html' },
  { code: 'FACILITY_PROCESS',        label: '공정관리',            icon: 'ti-git-branch',    href: 'facility/process-list.html' },
  { code: 'FACILITY_EQUIPMENT',      label: '설비관리',            icon: 'ti-tool',          href: 'facility/equipment-list.html' },
  { code: 'WORK_TBM',                label: 'TBM',                icon: 'ti-checklist',     href: 'work/tbm-list.html' },
  { code: 'WORK_RISK',               label: '위험성평가',          icon: 'ti-alert-triangle', href: 'work/risk-assessment.html' },
  // CONSTRUCTION
  { code: 'CONSTRUCTION_SITE',       label: '건설현장',            icon: 'ti-building-arch', href: 'construction/site-list.html' },
  { code: 'CONSTRUCTION_PROCESS',    label: '공정관리',            icon: 'ti-timeline',      href: 'construction/process-list.html' },
  { code: 'CONSTRUCTION_PTW',        label: '위험작업허가',        icon: 'ti-shield-check',  href: 'construction/ptw-list.html' },
  { code: 'CONSTRUCTION_ENTRY',      label: '작업자입입',           icon: 'ti-door-enter',    href: 'construction/entry-list.html' },
  { code: 'CONSTRUCTION_SAFETY',     label: '안전점검',            icon: 'ti-eye',           href: 'construction/safety-check.html' },
  // 공통 고급
  { code: 'REPORT_FORM',             label: '신고서식',            icon: 'ti-file-text',     href: 'report/report-form.html' },
  { code: 'REPORT_AUTO',             label: '전자제출',            icon: 'ti-send',          href: 'report/report-auto.html' },
];

// 메뉴 렌더링
function buildTadminMenu(sector, plan) {
  TAIFeatureFlags.load(sector, plan).then(() => {
    const nav = document.getElementById('side-nav');
    MENU_ITEMS.forEach(item => {
      const li = document.createElement('li');
      li.className = 'menu-item';
      li.setAttribute('data-feature', item.code);
      li.innerHTML = `
        <a href="${item.href}" class="menu-link">
          <span class="menu-icon"><i class="ti ${item.icon}"></i></span>
          <span class="menu-text">${item.label}</span>
        </a>
      `;
      nav.appendChild(li);
    });
    TAIFeatureFlags.apply();
  });
}
```

---

## 작업 3 — 시설 선택 시 sector 세션 저장

**파일:** 시설 선택 화면 (factory-list.html 또는 로그인 직후)

```javascript
// 시설 선택 시 sector + plan 세션 저장
async function onSelectFactory(factoryId) {
  const res = await apiCall('GET', `/factories/${factoryId}`);
  const factory = res.data;

  // 세션에 현재 시설 정보 저장
  sessionStorage.setItem('active_factory_id', factoryId);
  sessionStorage.setItem('active_sector',     factory.sector     || 'INDUSTRY');
  sessionStorage.setItem('active_plan',       factory.plan_code  || 'STARTER');

  // 메뉴 재렌더링
  buildTadminMenu(factory.sector, factory.plan_code);
}

// 페이지 로드 시 세션에서 읽어 적용
(function initFeatureFlags() {
  const sector = sessionStorage.getItem('active_sector') || 'INDUSTRY';
  const plan   = sessionStorage.getItem('active_plan')   || 'STARTER';
  buildTadminMenu(sector, plan);
})();
```

---

## HTML 적용 예시

메뉴 레이아웃에 `data-feature` 속성만 추가하면 자동 제어:

```html
<!-- 섹터 일치 + 플랜 충족 → 정상 표시 -->
<li class="menu-item" data-feature="CONSTRUCTION_PTW">
  <a href="ptw-list.html" class="menu-link">
    <span class="menu-icon"><i class="ti ti-shield-check"></i></span>
    <span class="menu-text">위험작업허가(PTW)</span>
  </a>
</li>

<!-- CONSTRUCTION 시설인데 INDUSTRY 셀터 마크 요소 → d-none 자동 적용 -->
<div class="dashboard-card" data-feature="WORK_RISK">
  ...
</div>
```

---

## 완료 기준

- [ ] `assets/js/feature-flags.js` 파일 생성 및 모든 tadmin HTML head에 스크립트 포함
- [ ] 메뉴 아이템에 `data-feature` 속성 적용 완료
- [ ] 시설 선택 시 sector/plan 세션 저장 로직 적용
- [ ] CONSTRUCTION 시설 + STARTER 플랜 선택 시:
  - PTW 메뉴 → 잠김 표시 (BUSINESS 이상)
  - TBM 메뉴 → 완전 숨김 (INDUSTRY 섹터 전용)
  - 공정관리 → 정상 표시
