# TAI 작업지시서 — 회사 등록 온보딩 플로우 (KSIC 검색 포함)

> 우선순위: 🔴 긴급  
> 작성일: 2026-03-31  
> 관련 레포: tai-admin (프론트) + tai-api (백엔드)

---

## 설계 원칙

**사업자번호 = 유니크 키**

```
홈페이지 회원가입  ──┐
tadmin 첫 진입     ──┼──→  사업자번호 입력  →  companies 테이블 upsert
법령진단 의뢰       ──┘         (unique)           ↓
                                            견적 / 계약 / SaaS 모두 연결
```

---

## DB 현황 (확인 완료)

`industry_master` 테이블에 KSIC 데이터 **501건** 존재.
한글명 + 코드 양방향 검색 가능.

```sql
-- 검색 쿼리 예시
SELECT lv4_code, lv4_name, lv1_name, industry_path_ko
FROM industry_master
WHERE is_active = true
  AND (lv4_name ILIKE '%{keyword}%'
    OR lv3_name ILIKE '%{keyword}%'
    OR lv4_code ILIKE '%{keyword}%')
ORDER BY lv4_code
LIMIT 20;
```

컬럼 구조:
- `lv4_code` — 4자리 KSIC 코드 (예: 2512)
- `lv4_name` — 세세분류명 (예: 금속 구조재 제조업)
- `lv3_name` — 세분류명
- `lv1_name` — 대분류명 (예: 제조업(10~34))
- `industry_path_ko` — 전체 경로 (예: 제조업 > 금속가공 > ...)

---

## 전체 플로우

```
[홈페이지 회원가입 or tadmin 첫 진입]
        │
        ▼
  이메일 + 비밀번호 가입
        │
        ▼
  ┌─────────────────────────────────┐
  │  내 회사 정보 입력 (필수)        │
  │  - 회사명          (필수)        │
  │  - 사업자번호      (필수, unique) │
  │  - 대표자명        (필수)        │
  │  - 업종 검색       (선택)   ←NEW │
  │  - 연락처          (선택)        │
  └─────────────────────────────────┘
        │
        ▼
  companies 테이블 upsert
        │
        ▼
  tadmin 대시보드 진입
```

---

## 작업 1 (백엔드): `/auth/register` API 수정

```python
# POST /auth/register
{
  "email": "manager@company.co.kr",
  "password": "...",
  "name": "홍길동",
  "phone": "010-1234-5678",
  "company_name": "(주)한국산업",     # 필수
  "business_number": "123-45-67890", # 필수, unique
  "representative_name": "김대표",   # 필수
  "ksic_code": "2512",               # 선택 (검색으로 선택한 값)
  "ksic_name": "금속 구조재 제조업",   # 선택 (함께 저장)
  "contact_phone": "02-1234-5678"    # 선택
}
```

처리 로직:
```python
# 사업자번호로 기존 company 조회
existing = companies.select().eq("business_number", business_number).first()

if existing:
    company_id = existing.id  # 기존 회사에 연결
else:
    company = companies.insert({
        "name": company_name,
        "business_number": business_number,
        "representative_name": representative_name,
        "ksic_code": ksic_code,       # 검색으로 선택한 코드
        "ksic_name": ksic_name,       # 검색으로 선택한 이름
        "status_code": "TRIAL",
        "company_type_code": "002",
        "is_active": True
    })
    company_id = company.id

user = users.insert({
    "email": email,
    "password_hash": bcrypt.hash(password),
    "name": name, "phone": phone,
    "company_id": company_id,
    "role_code": "002",
    "status_code": "ACTIVE", "is_active": True
})
```

---

## 작업 2 (백엔드): KSIC 검색 API 신규

```python
# GET /industry/search?q=금속&limit=10
# GET /industry/search?q=2512&limit=10  ← 코드 직접 검색도 지원

# Response
{
  "status": "success",
  "data": [
    {
      "code": "2512",
      "name": "금속 구조재 제조업",
      "path": "제조업 > 금속가공제품 제조업 > 구조용 금속제품 > 금속 구조재 제조업",
      "lv1_name": "제조업(10~34)"
    },
    ...
  ]
}
```

DB 쿼리:
```sql
SELECT lv4_code as code, lv4_name as name, 
       industry_path_ko as path, lv1_name
FROM industry_master
WHERE is_active = true
  AND (
    lv4_name ILIKE '%' || :q || '%'
    OR lv3_name ILIKE '%' || :q || '%'
    OR lv2_name ILIKE '%' || :q || '%'
    OR lv4_code ILIKE :q || '%'
  )
ORDER BY 
  CASE WHEN lv4_code = :q THEN 0
       WHEN lv4_code ILIKE :q || '%' THEN 1
       ELSE 2 END,
  lv4_code
LIMIT :limit
```

---

## 작업 3 (백엔드): `/companies/check-biz` API 신규

```python
# GET /companies/check-biz?business_number=123-45-67890
{
  "status": "success",
  "data": {
    "exists": true,
    "company_name": "(주)한국산업",
    "representative_name": "김대표"
  }
}
```

---

## 작업 4 (프론트): `auth-register.html` — 2단계 회원가입

### Step 1: 계정 정보
이름 / 이메일 / 비밀번호 / 연락처

### Step 2: 회사 정보 (KSIC 검색 포함)

```html
<!-- 회사명 -->
<div class="mb-3">
  <label class="form-label">회사명 <span class="text-danger">*</span></label>
  <input type="text" class="form-control" id="reg-company-name" placeholder="(주)한국산업">
</div>

<!-- 사업자번호 -->
<div class="mb-3">
  <label class="form-label">사업자번호 <span class="text-danger">*</span></label>
  <div class="input-group">
    <input type="text" class="form-control" id="reg-biz" placeholder="000-00-00000" maxlength="12">
    <button class="btn btn-outline-secondary" type="button" onclick="checkBizNumber()">확인</button>
  </div>
  <div id="biz-result" class="mt-1"></div>
</div>

<!-- 대표자명 -->
<div class="mb-3">
  <label class="form-label">대표자명 <span class="text-danger">*</span></label>
  <input type="text" class="form-control" id="reg-rep" placeholder="홍길동">
</div>

<!-- 업종 검색 (핵심) -->
<div class="mb-3">
  <label class="form-label">업종</label>
  <div class="position-relative">
    <input type="text" class="form-control" id="reg-ksic-search"
           placeholder="업종명 또는 코드 검색 (예: 금속, 식품, 건설)"
           oninput="searchKsic(this.value)" autocomplete="off">
    <!-- 검색 결과 드롭다운 -->
    <div id="ksic-dropdown"
         class="position-absolute w-100 bg-body border rounded shadow-sm"
         style="top:100%;left:0;z-index:1050;max-height:240px;overflow-y:auto;display:none">
    </div>
  </div>
  <!-- 선택된 값 표시 -->
  <div id="ksic-selected" class="mt-1" style="display:none">
    <span class="badge bg-label-primary fs-6 py-2 px-3">
      <span id="ksic-selected-text"></span>
      <button type="button" class="btn-close btn-close-sm ms-2 align-middle"
              onclick="clearKsic()" style="font-size:0.6rem"></button>
    </span>
  </div>
  <!-- hidden fields -->
  <input type="hidden" id="reg-ksic-code">
  <input type="hidden" id="reg-ksic-name">
</div>

<!-- 회사 연락처 -->
<div class="mb-3">
  <label class="form-label">회사 연락처</label>
  <input type="tel" class="form-control" id="reg-company-phone" placeholder="02-0000-0000">
</div>
```

### KSIC 검색 JS

```javascript
let ksicTimer = null;

async function searchKsic(q) {
  clearTimeout(ksicTimer);
  const dropdown = document.getElementById('ksic-dropdown');

  if (!q || q.trim().length < 1) {
    dropdown.style.display = 'none';
    return;
  }

  ksicTimer = setTimeout(async () => {
    try {
      const res = await fetch(
        `https://api.taieng.co.kr/industry/search?q=${encodeURIComponent(q.trim())}&limit=10`
      );
      const data = await res.json();
      const items = data.data || [];

      if (!items.length) {
        dropdown.innerHTML = '<div class="px-3 py-2 text-muted small">검색 결과가 없습니다.</div>';
        dropdown.style.display = 'block';
        return;
      }

      dropdown.innerHTML = items.map(item => `
        <div class="ksic-item px-3 py-2 border-bottom"
             style="cursor:pointer"
             onmousedown="selectKsic('${item.code}','${item.name.replace(/'/g,"\\'")}','${item.path.replace(/'/g,"\\'")}')">
          <div class="fw-semibold small">${item.code} &nbsp;${item.name}</div>
          <div class="text-muted" style="font-size:0.75rem">${item.path}</div>
        </div>
      `).join('');

      dropdown.style.display = 'block';
    } catch(e) {
      dropdown.style.display = 'none';
    }
  }, 250); // 250ms 디바운스
}

function selectKsic(code, name, path) {
  document.getElementById('reg-ksic-code').value = code;
  document.getElementById('reg-ksic-name').value = name;
  document.getElementById('reg-ksic-search').value = '';
  document.getElementById('ksic-selected-text').textContent = `${code} ${name}`;
  document.getElementById('ksic-selected').style.display = 'block';
  document.getElementById('ksic-dropdown').style.display = 'none';
}

function clearKsic() {
  document.getElementById('reg-ksic-code').value = '';
  document.getElementById('reg-ksic-name').value = '';
  document.getElementById('reg-ksic-search').value = '';
  document.getElementById('ksic-selected').style.display = 'none';
}

// 외부 클릭 시 드롭다운 닫기
document.addEventListener('click', function(e) {
  if (!e.target.closest('#reg-ksic-search') && !e.target.closest('#ksic-dropdown')) {
    document.getElementById('ksic-dropdown').style.display = 'none';
  }
});
```

---

## 작업 5 (프론트): `my-company.html` — tadmin 회사관리 페이지

KSIC 필드를 검색 방식으로 구현 (auth-register.html과 동일한 컴포넌트 사용).

```html
<!-- 업종 검색 (my-company.html) -->
<div class="col-12">
  <label class="form-label">업종</label>
  <div class="position-relative">
    <input type="text" class="form-control" id="mc-ksic-search"
           placeholder="업종명 또는 코드 검색 (예: 금속, 식품, 건설)"
           oninput="searchKsicMc(this.value)" autocomplete="off">
    <div id="mc-ksic-dropdown" class="position-absolute w-100 bg-body border rounded shadow-sm"
         style="top:100%;left:0;z-index:1050;max-height:240px;overflow-y:auto;display:none"></div>
  </div>
  <div id="mc-ksic-selected" class="mt-1" style="display:none">
    <span class="badge bg-label-primary fs-6 py-2 px-3">
      <span id="mc-ksic-selected-text"></span>
      <button type="button" class="btn-close btn-close-sm ms-2 align-middle"
              onclick="clearKsicMc()" style="font-size:0.6rem"></button>
    </span>
  </div>
  <input type="hidden" id="mc-ksic-code">
  <input type="hidden" id="mc-ksic-name">
</div>
```

기존 회사 정보 로드 시 KSIC 선택 상태 복원:
```javascript
// 기존 데이터 바인딩 시
if (company.ksic_code && company.ksic_name) {
  document.getElementById('mc-ksic-code').value = company.ksic_code;
  document.getElementById('mc-ksic-name').value = company.ksic_name;
  document.getElementById('mc-ksic-selected-text').textContent =
    `${company.ksic_code} ${company.ksic_name}`;
  document.getElementById('mc-ksic-selected').style.display = 'block';
}
```

---

## 작업 6 (프론트): nav-tadmin.js — onboarding 체크 추가

```javascript
// checkCompanyOnboarding() — nav-tadmin.js init()에 추가
async function checkCompanyOnboarding() {
  const companyId = localStorage.getItem('company_id');
  if (!companyId || companyId === 'null') {
    const current = window.location.pathname.split('/').pop();
    const excluded = ['my-company.html', 'auth-login-cover.html', 'auth-register.html'];
    if (!excluded.includes(current)) {
      location.replace('my-company.html?onboarding=1');
    }
  }
}
```

---

## 작업 7 (프론트): menu-tadmin.js — 마이페이지에 내 회사 정보 추가

```javascript
{ label: '내 회사 정보', href: 'my-company.html', visible: function() { return true; } },
```

---

## UX 흐름 (KSIC 검색)

```
사용자 입력: "금속"
        ↓ (250ms 디바운스)
API 호출: GET /industry/search?q=금속
        ↓
드롭다운 표시:
  2512  금속 구조재 제조업
        제조업 > 금속가공제품 > 구조용 금속제품 > ...
  2591  금속 단조제품 제조업
        제조업 > 금속가공제품 > 기타 금속가공 > ...
  ...
        ↓ 클릭
선택 배지 표시: [2512 금속 구조재 제조업  ×]
hidden input에 code, name 저장
```

---

## 완료 체크리스트

```
백엔드
□ GET  /industry/search?q=&limit= — KSIC 검색 API (industry_master 테이블)
□ GET  /companies/check-biz?business_number= — 사업자번호 중복 확인 API
□ POST /auth/register — company 필드 추가 (ksic_code, ksic_name 포함)

프론트
□ auth-register.html — 2단계 폼 (Step1: 계정, Step2: 회사+KSIC검색)
□ my-company.html — 신규 (KSIC 검색 포함)
□ nav-tadmin.js — checkCompanyOnboarding() 추가
□ menu-tadmin.js — 마이페이지 > 내 회사 정보 추가
□ GitHub push
```

---

## 효과

| 상황 | 처리 |
|------|------|
| KSIC 모르는 사람 | 한글 업종명 검색으로 쉽게 선택 |
| KSIC 아는 사람 | 코드 직접 입력으로 즉시 선택 |
| 선택 안 해도 됨 | 선택 필드이므로 건너뛰기 가능 |
| 나중에 수정 | my-company.html에서 언제든 변경 |
