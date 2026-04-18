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

**원인**: API 실패 시 fallback이 "처리 중" 메시지.

**수정**: `renderFreeResult()` 함수 내:
```javascript
// 현재:
if (!data) {
  area.innerHTML = `... 진단 데이터 처리 중 ...`;

// 수정:
if (!data) {
  area.innerHTML = `<div class="result-item">
    <div class="ri-title">진단을 실행할 수 없습니다</div>
    <div class="ri-law">입력 정보를 확인하고 다시 시도해주세요.</div>
  </div>`;
  document.getElementById('paidCta').style.display = 'none';
  return;
}
```

---

### BUG-4: "PAID 진단에서 추가로 확인되는 항목들:" 문구 노출 🔴

**수정**: HTML + JS 둘 다:
```html
<!-- 현재: -->
<h5>더 정밀한 진단이 필요하신가요?</h5>
<p>PAID 진단에서 추가로 확인되는 항목들:</p>

<!-- 수정: -->
<h5>현재 진단에서 확인할 수 없는 영역이 있습니다</h5>
<!-- <p> 태그 제거 -->
```

---

## 대표님 추가 보고 — 3건 (신규)

### BUG-10: 유료 진단 전 최종 점검 안내 없음 🔴

**기획**: 유료 진단은 결제 후 재입력 불가.
→ 결제 직전에 "입력 내용을 확인하세요" 확인 단계 필요.

**수정**: Step 4 결제 버튼 `startPayment()` 내:
```javascript
function startPayment() {
  // 입력 내용 요약 표시
  const paidData = formValues['paid'] || {};
  const filledCount = Object.values(paidData).filter(v => v !== '' && v !== null).length;
  const totalFields = document.querySelectorAll('#paidFormArea .form-row').length;
  
  const confirmed = confirm(
    `입력 내용을 확인해 주세요.\n\n` +
    `• 입력 완료: ${filledCount}건 / 전체: ${totalFields}건\n` +
    `• 결제 금액: ${paidFee.toLocaleString()}원 (VAT 별도)\n\n` +
    `⚠️ 진단 실행 후에는 재입력할 수 없습니다.\n` +
    `정보를 모두 입력하셨습니까?`
  );
  if (!confirmed) return;
  
  // 기존 결제 로직
  const modal = new bootstrap.Modal(document.getElementById('payPrepModal'));
  modal.show();
}
```

---

### BUG-11: 여부 필드가 텍스트 input으로 렌더링 🔴

**DB 현황**: `field_type = 'tri_state'` 필드 **58건**
- BUILDING PAID: 18건 (비상발전기 유무, 스프링클러 유무 등)
- CONSTRUCTION PAID: 14건 (굴착작업 유무, 타워크레인 유무 등)
- INDUSTRY PAID1~3: 26건 (보일러 유무, 크레인 유무 등)

**원인**: `renderField()`에 `tri_state` 핸들러가 없어서 `else` 블록(텍스트 input)으로 빠짐.

**수정**: `renderField()` 함수에 `tri_state` 분기 추가:
```javascript
} else if (f.field_type === 'tri_state') {
  // 예 / 아니오 / 모름 3버튼
  ctrl = `<div class="yn-grid" style="grid-template-columns:1fr 1fr 1fr;">
    <div class="yn-btn" onclick="setTriState('${f.field_code}','yes',this,'${prefix}')">예</div>
    <div class="yn-btn" onclick="setTriState('${f.field_code}','no',this,'${prefix}')">아니오</div>
    <div class="yn-btn" onclick="setTriState('${f.field_code}','unknown',this,'${prefix}')"
      style="color:#9a8f80;font-size:.82rem;">모름</div>
  </div>`;
```

`setTriState()` 함수 추가:
```javascript
function setTriState(code, val, el, prefix) {
  el.parentNode.querySelectorAll('.yn-btn').forEach(b => b.className = 'yn-btn');
  if (val === 'yes') el.className = 'yn-btn sel-yes';
  else if (val === 'no') el.className = 'yn-btn sel-no';
  else el.className = 'yn-btn sel-no'; // 모름도 선택 스타일
  setVal(code, val, prefix);
}
```

---

### BUG-12: 숫자 필드에 한글/특수문자 입력 가능 🔴

**DB 현황**: `field_type = 'number'` 필드 **36건**
- 예: 지하주차장 면적(㎡), 연면적(㎡), 총 공사금액(만원), 근로자 수(명) 등

**원인**: `<input type="number">`이지만 추가 입력 제어 없음.
모바일 키보드가 한글 모드일 때 한글 입력 가능.

**수정**: `renderField()` 내 number 분기:
```javascript
} else if (f.field_type === 'number') {
  ctrl = `<div class="num-wrap">
    <input type="number" class="form-input-tai" id="${id}"
      placeholder="${f.placeholder || '0'}" min="0"
      inputmode="numeric"
      pattern="[0-9]*"
      oninput="this.value=this.value.replace(/[^0-9.]/g,''); setVal('${f.field_code}',this.value,'${prefix}')"
      ${f.auto_source === 'building_register' ? 'data-auto-source="building_register"' : ''}>
    ${f.unit ? `<span class="num-unit">${f.unit}</span>` : ''}
  </div>`;
```

핵심 변경:
- `inputmode="numeric"` — 모바일 숫자 키보드 강제
- `pattern="[0-9]*"` — iOS 숫자 키보드
- `oninput` — 한글/특수문자 즉시 제거 (소수점은 허용)

---

## 최종 수정 우선순위 (12건)

| 순서 | 버그 | 심각도 | 예상 시간 |
|---|---|---|---|
| 1 | BUG-1: 건설 주소 검색버튼 | 🔴 | 1분 |
| 2 | BUG-11: tri_state 렌더러 (58건) | 🔴 | 10분 |
| 3 | BUG-12: number 입력 제어 (36건) | 🔴 | 5분 |
| 4 | BUG-2: 필수 필드 validation | 🔴 | 10분 |
| 5 | BUG-10: 유료 결제 전 최종 확인 | 🔴 | 5분 |
| 6 | BUG-3: 결과 없음 메시지 | 🔴 | 2분 |
| 7 | BUG-4: PAID 문구 노출 | 🔴 | 3분 |
| 8 | BUG-6: 면책동의 초기화 | 🟡 | 1분 |
| 9 | BUG-9: CTA 문구 변경 | 🟢 | 2분 |
| 10 | BUG-5: 주소검색 재확인 | 🟡 | 재테스트 |
| 11 | BUG-7: 좌측 패널 동적 | 🟡 | 확인 |
| 12 | BUG-8: 주소 우선 표시 | 🟢 | 대표님 판단 |
