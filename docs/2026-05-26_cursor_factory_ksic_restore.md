# Cursor 작업지시: factory-list.html KSIC 필드 복원

> 대상: `tadmin/full-version/html/horizontal-menu-template/factory-list.html`
> 현재 상태: 탭 2개(기본정보/담당자) + 섹터별 필드 + 상태 disabled 적용 완료
> 문제: KSIC 필드가 삭제되어 공정관리(process-select.html)가 동작 안 함

---

## 작업 내용: KSIC 업종코드 필드 복원

원본 코드 참조: `git show 42d4359e:tadmin/full-version/html/horizontal-menu-template/factory-list.html`

### 1. fpTab1() 함수 내 KSIC 필드 추가

시설유형 select (`fp-site-type`) 아래에 다음 필드 추가:

```js
'<div class="col-12"><label class="form-label">업종코드 KSIC</label>'+
(readOnly
  ? '<p class="form-control-plaintext mb-0">' + escapeHtml(ksicDisp || '-') + '</p>'
  : '<div class="input-group"><input type="text" class="form-control" id="fp-ksic-display" readonly placeholder="검색 버튼으로 선택" value="' + escapeHtml(ksicDisp) + '" style="background:#fff;cursor:pointer;" onclick="openFpKsicSearch()">' +
    '<input type="hidden" id="fp-ksic" value="' + escapeHtml(ksicCode) + '">' +
    '<button type="button" class="btn btn-outline-primary" onclick="openFpKsicSearch()"><i class="ti ti-search"></i></button>' +
    '<button type="button" class="btn btn-outline-secondary" id="fp-ksic-clear" onclick="clearFpKsic()"' + (ksicCode ? '' : ' style="display:none"') + '>초기화</button></div>') +
'</div>'+
```

fpTab1 상단에 ksicCode/ksicDisp 변수 추가:
```js
var ksicCode = fpPick(f, ['ksic_code', 'industry_code_full']);
var ksicDisp = ksicCode + (fpPick(f, ['ksic_name', 'industry_name_full']) ? ' ' + fpPick(f, ['ksic_name', 'industry_name_full']) : '');
```

### 2. KSIC 검색 모달 HTML 복원

주소검색 모달 (`jusoSearchModal`) 아래에 추가:

```html
<!-- KSIC 업종 검색 모달 -->
<div class="modal fade" id="fpKsicModal" tabindex="-1">
  <div class="modal-dialog modal-lg"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title">KSIC 업종 검색</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body">
      <div class="input-group mb-3">
        <input type="text" id="fp-ksic-keyword" class="form-control" placeholder="업종명 또는 코드 (4자리)" autocomplete="off" onkeydown="if(event.key==='Enter'){event.preventDefault();searchFpKsic();}">
        <button type="button" class="btn btn-primary" onclick="searchFpKsic()"><i class="ti ti-search"></i> 검색</button>
      </div>
      <div id="fp-ksic-results" class="list-group" style="max-height:350px;overflow-y:auto;"></div>
    </div>
  </div></div>
</div>
```

### 3. JS 변수 복원

상단 변수 선언부에 추가:
```js
var fpKsicModal = null, fpKsicName = '';
```

### 4. JS 함수 복원 (4개)

```js
function openFpKsicSearch() {
  var modalEl = document.getElementById('fpKsicModal');
  if (!modalEl) return;
  if (!fpKsicModal) fpKsicModal = bootstrap.Modal.getOrCreateInstance(modalEl);
  document.getElementById('fp-ksic-keyword').value = '';
  document.getElementById('fp-ksic-results').innerHTML = '<p class="text-muted text-center py-3 small">업종명 또는 코드를 입력하고 검색하세요.</p>';
  fpKsicModal.show();
  setTimeout(function() { document.getElementById('fp-ksic-keyword').focus(); }, 300);
}

async function searchFpKsic() {
  var q = (document.getElementById('fp-ksic-keyword') && document.getElementById('fp-ksic-keyword').value || '').trim();
  if (!q) { showToast('warning', '검색어를 입력하세요.'); return; }
  var el = document.getElementById('fp-ksic-results');
  el.innerHTML = '<div class="text-center p-4"><div class="spinner-border spinner-border-sm text-primary"></div></div>';
  try {
    var res = await apiCall('GET', '/ksic-engine/search?query=' + encodeURIComponent(q) + '&size=30');
    var items = (res && (res.data || res) && ((res.data && res.data.items) || res.items || [])) || [];
    if (!Array.isArray(items)) items = [];
    if (!items.length) { el.innerHTML = '<p class="text-muted text-center py-3 small">검색 결과가 없습니다.</p>'; return; }
    el.innerHTML = items.map(function(it, i) {
      var code = String(it.ksic_code || it.code || '');
      var name = String(it.industry_name || it.name || '');
      return '<div class="list-group-item list-group-item-action py-2 px-3" style="cursor:pointer" data-fp-ksic-idx="' + i + '">' +
        '<span class="badge bg-label-primary me-2">' + escapeHtml(code) + '</span>' + escapeHtml(name) + '</div>';
    }).join('');
    window._fpKsicItems = items;
    el.querySelectorAll('[data-fp-ksic-idx]').forEach(function(row) {
      row.addEventListener('click', function() { selectFpKsic(parseInt(row.getAttribute('data-fp-ksic-idx'), 10)); });
    });
  } catch(e) {
    el.innerHTML = '<p class="text-danger small mb-0 p-3">' + escapeHtml(e.message || '검색 실패') + '</p>';
  }
}

function selectFpKsic(idx) {
  var it = window._fpKsicItems && window._fpKsicItems[idx];
  if (!it) return;
  var code = String(it.ksic_code || it.code || '');
  var name = String(it.industry_name || it.name || '');
  fpKsicName = name;
  var hid = document.getElementById('fp-ksic'), disp = document.getElementById('fp-ksic-display'), clr = document.getElementById('fp-ksic-clear');
  if (hid) hid.value = code;
  if (disp) disp.value = code + (name ? ' ' + name : '');
  if (clr) clr.style.display = '';
  if (fpKsicModal) fpKsicModal.hide();
}

function clearFpKsic() {
  fpKsicName = '';
  var hid = document.getElementById('fp-ksic'), disp = document.getElementById('fp-ksic-display'), clr = document.getElementById('fp-ksic-clear');
  if (hid) hid.value = '';
  if (disp) disp.value = '';
  if (clr) clr.style.display = 'none';
}
```

### 5. collectFactoryBody()에 ksic 필드 복원

```js
ksic_code: ksicEl ? ksicEl.value.trim() : '',
ksic_name: fpKsicName || undefined,
```

### 6. renderFactoryPanel()에 fpKsicName 초기화 복원

```js
fpKsicName = fpPick(f, ['ksic_name', 'industry_name_full']);
```

### 7. 목록 테이블 업종 컨럼 유지

목록에 "업종" 컨럼을 유지하되 KSIC 코드 + 이름 표시:
```js
'<td>' + escapeHtml(f.ksic_name || f.industry_name || f.ksic_code || '-') + '</td>'
```

---

## 변경하지 않는 것

- 탭 구성 (2개: 기본정보/담당자) — 유지
- 섹터별 필드 표시 — 유지
- 상태 disabled — 유지
- 담당자 탭 개선 — 유지
- 설비 링크 제거 — 유지
- 건축물대장 autoFill — 유지

---

## 체크리스트

- [ ] fpTab1에 KSIC 필드 추가
- [ ] KSIC 모달 HTML 추가
- [ ] JS 변수 (fpKsicModal, fpKsicName) 추가
- [ ] JS 함수 4개 추가
- [ ] collectFactoryBody에 ksic_code/ksic_name 추가
- [ ] renderFactoryPanel에 fpKsicName 초기화
- [ ] 테스트: 시설 등록 → KSIC 검색 → 선택 → 저장
- [ ] 테스트: 공정관리(process-select) 진입 시 KSIC 인식 확인
