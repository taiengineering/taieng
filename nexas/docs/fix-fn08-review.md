# FN-08 점검 결과 — 즉시 수정 7건

**점검일**: 2026-04-18  
**점검자**: 기획창  
**대상 파일**: `nexas/free-diagnosis.html`  
**긴급도**: 플로우 차단 버그 3건 + 기획 위반 4건

---

## 플로우 차단 버그 (즉시 수정)

### FN-FIX-1: 주소 검색 배열 처리 (크리티컬)

`searchAddr()` 함수 내:

```javascript
// 현재 (버그 — json.data가 배열인데 단일 객체로 처리):
const json = await r.json();
const item = json.data;
if (!item?.road_address) {
  dd.innerHTML = '...검색 결과가 없습니다...';
}

// 수정 (BE가 배열 반환):
const json = await r.json();
const items = json.data || [];
if (!items.length) {
  dd.innerHTML = '<div class="addr-item" style="color:#9a8f80;">검색 결과가 없습니다</div>';
  dd.classList.add('show');
  return;
}
// 복수 결과 드롭다운 표시
let listHtml = '';
items.forEach((item, idx) => {
  const bNm = item.building_name ? ` (${item.building_name})` : '';
  listHtml += `<div class="addr-item" onclick="selectAddr('${prefix}', ${idx})">
    <div class="road">${item.road_address}${bNm}</div>
    <div class="jibun">우편번호 ${item.zip_code || ''}</div>
  </div>`;
});
window['_addrList_'+prefix] = items;
dd.innerHTML = listHtml;
dd.classList.add('show');
```

`selectAddr()` 함수도 수정:
```javascript
// 현재:
async function selectAddr(prefix) {
  const item = window['_addrData_'+prefix];

// 수정 (배열 인덱스 받기):
async function selectAddr(prefix, idx) {
  const items = window['_addrList_'+prefix] || [];
  const item = items[idx || 0];
  if (!item) return;
  const roadAddr = item.road_address;
  ...
```

---

### FN-FIX-2: auth/check 호출 방식 불일치

```javascript
// 현재 (FE — 헤더 사용):
const checkR = await fetch(`${API}/diagnosis/auth/check`, {
  headers: { 'X-Auth-Token': authToken }
});

// 수정 (BE가 query param 기대):
const checkR = await fetch(
  `${API}/diagnosis/auth/check?auth_token=${encodeURIComponent(authToken)}`
);
```

---

### FN-FIX-3: disclaimer API 필드 불일치

```javascript
// 현재 (FE — BE 스키마와 다름):
body: JSON.stringify({
  auth_token: authToken,
  sector,                 // ← BE에 없는 필드
  disclaimer_text: '...', // ← BE는 서버측 사용
  ip: ''                  // ← BE는 ip_address
})

// 수정 (BE DisclaimerBody 스키마 맞춤):
body: JSON.stringify({
  auth_token: authToken,
  agreed: true
})
```

또한 `disclaimerLogId` 응답 파싱도 수정:
```javascript
// 현재:
disclaimerLogId = disclJson.data?.disclaimer_log_id || '';

// BE 응답 구조에 맞춤 (data 래핑 없음):
disclaimerLogId = disclJson.disclaimer_log_id || '';
```

---

## 기획 위반 수정

### FN-FIX-4: "건축물대장" 언급 제거

`fetchBuildingRegister()` 내 메시지 수정:

```javascript
// 수정 전:
'🔍 건축물대장 조회 중...'
'⚠️ 건축물대장을 찾지 못했습니다. 아래 항목을 직접 입력해주세요.'
'✅ 건축물대장에서 5개 항목을 자동으로 채웠습니다.'

// 수정 후:
'🔍 사업장 정보 조회 중...'
'⚠️ 자동 조회가 되지 않았습니다. 아래 항목을 직접 입력해주세요.'
'✅ 5개 항목이 자동으로 입력되었습니다.'
```

좌측 패널 텍스트 수정:
```html
<!-- 수정 전: -->
<li>건축물대장 자동 연동 (건물 섹터)</li>
<!-- 수정 후: -->
<li>주소 입력 시 사업장 정보 자동 확인</li>
```

---

### FN-FIX-5: 면책 문구 확정 문구로 교체

```html
<!-- 현재: -->
<div class="disclaimer-text">
  본 진단 결과는 입력 정보를 기반으로 정밀 분석하여 도출된 참고 자료입니다.<br>
  법령 해석의 최종 책임은 사업주에게 있으며...
</div>

<!-- 확정 문구로 교체: -->
<div class="disclaimer-text">
  본 진단 결과는 현행 법령과 사업장 정보를 정밀 분석하여
  적용 가능한 법적 의무를 도출한 것입니다.<br>
  본 서비스는 법률 상담·자문·의견 제공이 아니며,
  개별 사안에 대한 법적 판단이나 해석을 포함하지 않습니다.<br>
  실제 행정 처분·감독 기준은 관할 기관의 판단에 따라
  달라질 수 있으므로, 구체적 법률 적용이 필요한 경우
  관할 행정기관 또는 법률 전문가에게 확인하시기 바랍니다.
</div>
```

`submitFree()` 내 하드코딩된 문구도 삭제:
```javascript
// 삭제 (불필요 — BE가 서버측 DISCLAIMER_TEXT 사용):
disclaimer_text: '본 진단 결과는 ...',
```

---

### FN-FIX-6: 헤더 제거

```html
<!-- 삭제: -->
<div id="tai-header"></div>
...
<script src="assets/js/header.js"></script>
<script src="assets/js/nav-auth.js"></script>
```

---

### FN-FIX-7: price-tier 파라미터명 불일치

```javascript
// 현재 (FE):
fetch(`${API}/diagnosis/price-tier?sector=BUILDING&total_floor_area=${area}`)

// BE가 기대하는 파라미터:
fetch(`${API}/diagnosis/price-tier?sector=BUILDING&floor_area=${area}`)
```

---

## 수정 우선순위

| 순서 | 건 | 심각도 | 설명 |
|---|---|---|---|
| 1 | FN-FIX-1 | 🔴 치명적 | 주소 검색 불가 → 전체 플로우 차단 |
| 2 | FN-FIX-2 | 🔴 치명적 | 본인인증 후 횟수확인 실패 |
| 3 | FN-FIX-3 | 🔴 치명적 | 면책동의 API 에러 |
| 4 | FN-FIX-7 | 🟡 기능 오류 | 가격 판정 실패 |
| 5 | FN-FIX-4 | 🟡 기획 위반 | 건축물대장 언급 |
| 6 | FN-FIX-5 | 🟡 기획 위반 | 면책 문구 불일치 |
| 7 | FN-FIX-6 | 🟡 기획 위반 | 헤더 제거 |
