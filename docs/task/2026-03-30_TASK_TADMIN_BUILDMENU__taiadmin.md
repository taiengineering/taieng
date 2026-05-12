# tadmin 전체 HTML buildMenu() 적용 작업지시서
## 담당: Cursor
## 기준 커밋: 167a2ae

---

## 배경

다음 3개 파일은 이미 완료됨 — **건드리지 말 것**:
- `tadmin/full-version/html/horizontal-menu-template/auth-login-cover.html`
- `tadmin/full-version/html/horizontal-menu-template/index.html`
- `tadmin/full-version/assets/js/tai/menu-tadmin.js`

---

## 작업 목표

아래 **13개 HTML 파일** 각각에 대해 두 가지 변경을 적용한다.

### 변경 1: menu-inner 비우기

각 파일의 `<ul class="menu-inner">` 안의 모든 `<li>` 항목을 제거하고 빈 ul만 남긴다.

```html
<!-- 변경 전 -->
<ul class="menu-inner">
  <li class="menu-item active">...</li>
  <li class="menu-item">...</li>
  ...
</ul>

<!-- 변경 후 -->
<ul class="menu-inner"></ul>
```

### 변경 2: 스크립트 추가

각 파일의 `</body>` 바로 위, 기존 `<script src="...">` 블록 **다음**에 아래 두 줄을 추가한다.

```html
<script src="../../assets/js/tai/menu-tadmin.js"></script>
<script>buildMenu('layout-menu');</script>
```

**이미 있으면 중복 추가 금지.**

---

## 적용 대상 13개 파일

모두 `tadmin/full-version/html/horizontal-menu-template/` 경로.

| 파일명 | STEP 5 레벨 제한 추가 여부 |
|--------|----------------------------|
| `contact.html` | 없음 |
| `diagnosis-step1.html` | 없음 |
| `education-list.html` | `requireAddon('ADDON_EDU');` 추가 |
| `education-setting.html` | `requireAddon('ADDON_EDU');` 추가 |
| `factory-list.html` | 없음 |
| `manager-permission.html` | 없음 |
| `my-contract.html` | 없음 |
| `my-diagnosis.html` | 없음 |
| `my-equipment.html` | 없음 |
| `my-inspection.html` | 없음 |
| `notification-list.html` | 없음 |
| `process-select.html` | 없음 |
| `tai_survey_v5.html` | 없음 |

---

## STEP 5: 레벨 제한 적용 방법

`education-list.html` 과 `education-setting.html` 에만 적용.

기존 인증 체크 스크립트 블록(access_token 검사)에 한 줄 추가:

```javascript
// 기존
if (!localStorage.getItem('access_token'))
  location.replace('...');

// 변경 후 (requireAddon 한 줄 추가)
if (!localStorage.getItem('access_token'))
  location.replace('...');
// menu-tadmin.js 로드 후 실행되므로 DOMContentLoaded 이후 호출
document.addEventListener('DOMContentLoaded', function() {
  if (typeof requireAddon === 'function') requireAddon('ADDON_EDU');
});
```

---

## doLogout 함수 통일 (모든 대상 파일)

각 파일의 `doLogout()` 함수를 아래로 교체한다.
계약 관련 키도 함께 제거해야 함:

```javascript
function doLogout() {
  ['access_token','refresh_token','role_code','user_name','user_id',
   'company_id','company_name','factory_id',
   'contract_plan_code','contract_sector','contract_level',
   'contract_addons','contract_service_type'
  ].forEach(function(k){ localStorage.removeItem(k); });
  location.replace('https://tadmin.taieng.co.kr/html/horizontal-menu-template/auth-login-cover.html');
}
```

---

## 작업 순서

1. `git pull origin main` (167a2ae 기준)
2. 13개 파일 순서대로 수정
3. 단일 커밋:

```
git commit -m "feat: tadmin 전체 HTML buildMenu() 적용 (menu-tadmin.js STEP 4~5)"
```

4. `git push origin main`

---

## 검증 기준

- `<ul class="menu-inner">` 안에 `<li>` 태그 없음
- `menu-tadmin.js` 스크립트 태그 존재
- `buildMenu('layout-menu')` 호출 존재
- `doLogout` 에 contract_* 키 포함
- education-list / education-setting 에 `requireAddon('ADDON_EDU')` 존재
