# FN-08 전체 버그 통합 수정 지시서 v2

**점검일**: 2026-04-18  
**점검자**: 기획창 + 대표님 실측 테스트  
**대상 파일**: `nexas/free-diagnosis.html`  
**우선순위**: 플로우 차단 → 로직 오류 → UX 위반 순

---

## 플로우 차단 버그 (4건)

### BUG-1: 건설 주소 검색버튼 없음 🔴

**원인**: DB에서 CONSTRUCTION 주소 필드코드가 `project_address`인데,
FE `renderField()`에서 `field_code === 'address'`만 체크하여 검색 UI 렌더링 안 됨.

**수정**: `renderField()` 함수 내:
```javascript
// 현재:
if (f.field_code === 'address') {

// 수정:
if (f.field_code === 'address' || f.field_code === 'project_address') {
```

---

### BUG-2: 필수 필드 미입력 시 결과 페이지 이동 가능 🔴

**원인**: `submitFree()`에 필수 필드 validation이 없음.

**수정**: `submitFree()` 함수 상단에 validation 추가:
```javascript
async function submitFree() {
  // 필수 필드 검증
  const freeData = formValues['free'] || {};
  const requiredFields = document.querySelectorAll('#dynFormArea .req');
  let missing = [];
  requiredFields.forEach(reqEl => {
    const row = reqEl.closest('.form-row');
    if (!row) return;
    const input = row.querySelector('input, select');
    if (!input) return;
    // field_code 추출
    const id = input.id || '';
    const code = id.replace('free_', '');
    const val = freeData[code];
    if (!val && val !== 0 && val !== false) {
      const label = row.querySelector('.form-label-tai')?.textContent?.trim() || code;
      missing.push(label.replace(' *', ''));
    }
  });
  if (missing.length > 0) {
    alert(`필수 항목을 입력해주세요:\n- ${missing.join('\n- ')}`);
    return;
  }
  // ... 기존 코드 계속
}
```

---

### BUG-3: 결과 없이 "진단 데이터 처리 중" 표시 🔴

**원인**: API 실패 시 fallback이 "처리 중" 메시지. 에러인데 "처리 중"으로 보임.

**수정**: `renderFreeResult()` 함수 내:
```javascript
// 현재:
if (!data) {
  area.innerHTML = `<div class="result-item">
    <div class="ri-title">진단 데이터 처리 중</div>
    <div class="ri-law">잠시 후 다시 확인해주세요.</div>
  </div>`;

// 수정:
if (!data) {
  area.innerHTML = `<div class="result-item">
    <div class="ri-title">진단을 실행할 수 없습니다</div>
    <div class="ri-law">입력 정보를 확인하고 다시 시도해주세요.</div>
  </div>`;
  // 유료 CTA 숨김 — 결과가 없으면 추천도 없음
  document.getElementById('paidCta').style.display = 'none';
  return;
}
```

---

### BUG-4: "PAID 진단에서 추가로 확인되는 항목들:" 문구 노출 🔴

**원인**: HTML에 하드코딩된 텍스트가 무조건 노출.

**수정**: `paid-cta` 영역 HTML 수정:
```html
<!-- 현재: -->
<h5>더 정밀한 진단이 필요하신가요?</h5>
<p>PAID 진단에서 추가로 확인되는 항목들:</p>

<!-- 수정 (기획 원칙: 필요성 먼저, 가격 나중): -->
<h5>현재 진단에서 확인할 수 없는 영역이 있습니다</h5>
<!-- <p> 태그 제거 — 항목 리스트가 직접 나오도록 -->
```

그리고 `renderFreeResult()` 내 CTA 로직:
```javascript
// CTA 항목 없으면 숨김
const paidItems = data.paid_preview || unconfirmed || [];
if (!paidItems.length && !items.length) {
  document.getElementById('paidCta').style.display = 'none';
  return;
}
```

---

## 로직 오류 (3건)

### BUG-5: 건물 주소 입력 → 자동채움 순서 문제 🟡

**기획 의도**: 주소 입력 → 주소 선택 → 건축물대장 조회 → 면적·층수 자동 채움  
**현재**: 주소 검색 자체가 404 (Fly.io 서버 다운이었음 → 재시작으로 해결)

**확인 필요**: 서버 재시작 후 `/juso/search` 응답 정상 여부 재테스트.


### BUG-6: 면책동의 체크 없이 진단 버튼 활성화 가능 🟡

**확인**: `onDisclaimerChange()`가 버튼 disabled 제어하는데,
페이지 로드 시 초기 상태에서 `btnSubmit.disabled = true`가 정상 설정되는지 확인.

```javascript
// loadFreeForm() 내에 확실히 초기화:
document.getElementById('disclaimerCheck').checked = false;
document.getElementById('btnSubmit').disabled = true;
```


### BUG-7: 좌측 패널 섹터별 동적 변경 안 됨 🟡

**기획**: Step 2에서 섹터에 따라 좌측 패널 메시지가 변경되어야 함.
```
BUILDING: "주소만 입력하면 바로 확인됩니다"
INDUSTRY: "업종과 규모만으로 진단합니다"
CONSTRUCTION: "공사 기본 정보로 진단합니다"
```
**확인 필요**: 현재 좌측 패널이 모든 Step에서 동일한지, Step별로 변경되는지.

---

## UX 기획 위반 (2건)

### BUG-8: 주소 필드만 먼저 표시 후 나머지 필드 출력 🟢

**기획 의도**: 건물 섹터는 주소만 먼저 보이고,
주소 선택 후 자동채움된 필드들이 표시되는 방식.

TAI UI 원칙: "지금 보지 않아도 되는 것은 보여주지 않는다."

**구현 방안** (선택적 — 대표님 판단):
```
Option A: 전체 표시 (현재) — 간단하지만 필드가 많아 보임
Option B: 주소만 독립 카드 → 자동채움 후 나머지 표시
```

### BUG-9: CTA 문구 기획 불일치 🟢

**기획 원칙**: "더 정밀한" 아니라 "지금 안 보이는 법령이 있다"

```html
<!-- 현재: -->
<h5>더 정밀한 진단이 필요하신가요?</h5>

<!-- 수정: -->
<h5>현재 진단에서 확인할 수 없는 영역이 있습니다</h5>
```

---

## 수정 우선순위

| 순서 | 버그 | 심각도 | 예상 시간 |
|---|---|---|---|
| 1 | BUG-1: 건설 주소 검색버튼 | 🔴 | 1분 |
| 2 | BUG-2: 필수 필드 validation | 🔴 | 10분 |
| 3 | BUG-3: 결과 없음 메시지 | 🔴 | 2분 |
| 4 | BUG-4: PAID 문구 노출 | 🔴 | 3분 |
| 5 | BUG-6: 면책동의 초기화 | 🟡 | 1분 |
| 6 | BUG-9: CTA 문구 변경 | 🟢 | 2분 |
| 7 | BUG-5: 주소검색 재테스트 | 🟡 | 확인 |
| 8 | BUG-7: 좌측 패널 동적 | 🟡 | 확인 |
| 9 | BUG-8: 주소 우선 표시 | 🟢 | 대표님 판단 |
