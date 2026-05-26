# 안전대시보드 법령진단현황 삭제 + 진단이력 사업장 필터 수정

> 작성일: 2026-05-26
> 대상 파일:
>   - `tadmin/full-version/html/horizontal-menu-template/safety-dashboard.html`
>   - `tadmin/full-version/assets/js/tai/safety-dashboard.page.js`
> 레포: `taiengineering/tai-admin` (main 직접 커밋)

---

## 작업 1: 법령진단현황 카드 HTML 삭제

### 파일: `safety-dashboard.html`

아래 블록 전체를 삭제한다:

```html
              <!-- 법령 진단 현황 -->
              <div class="card mb-3">
                <div class="card-header pb-2">
                  <h6 class="mb-0"><i class="ti tabler-scale me-1 text-primary"></i>법령 진단 현황</h6>
                  <small class="text-body-secondary" id="legalFactoryName">사업장 미선택</small>
                </div>
                <div class="card-body py-2">
                  <div class="row g-2">
                    <div class="col-6">
                      <div class="card border-0 bg-light h-100 text-center py-3 legal-card" onclick="location.href='my-diagnosis.html'">
                        <div class="legal-num text-primary" id="legalTotal">-</div>
                        <small class="text-body-secondary">적용법령</small>
                      </div>
                    </div>
                    <div class="col-6">
                      <div class="card border-0 bg-light h-100 text-center py-3 legal-card" onclick="location.href='my-diagnosis.html'">
                        <div class="legal-num text-danger" id="legalAppoint">-</div>
                        <small class="text-body-secondary">선임의무</small>
                      </div>
                    </div>
                    <div class="col-6">
                      <div class="card border-0 bg-light h-100 text-center py-3 legal-card" onclick="location.href='my-inspection.html'">
                        <div class="legal-num text-warning" id="legalInspect">-</div>
                        <small class="text-body-secondary">점검의무</small>
                      </div>
                    </div>
                    <div class="col-6">
                      <div class="card border-0 bg-light h-100 text-center py-3 legal-card" onclick="location.href='my-diagnosis.html'">
                        <div class="legal-num text-info" id="legalReport">-</div>
                        <small class="text-body-secondary">신고의무</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
```

### `<style>` 블록에서 삭제할 CSS:

```css
    .legal-num { font-size:2rem; font-weight:800; line-height:1; }
    .legal-card { cursor:pointer; transition:box-shadow .15s; }
    .legal-card:hover { box-shadow:0 2px 12px rgba(0,0,0,.1)!important; }
```

---

## 작업 2: loadLegalSummary 함수 삭제 + loadDiagHistory 분리

### 파일: `safety-dashboard.page.js`

#### 2-1. loadDashboard() 수정

변경 전:
```js
function loadDashboard() {
  if (!_currentFactoryId) {
    renderInspectionDailyChart();
    return;
  }
  loadSchedules();
  loadUsers();
  loadLegalSummary();   // ← 삭제
}
```

변경 후:
```js
function loadDashboard() {
  if (!_currentFactoryId) {
    renderInspectionDailyChart();
    return;
  }
  loadSchedules();
  loadUsers();
  loadDiagHistory();    // 진단이력만 직접 호출
}
```

#### 2-2. loadLegalSummary 함수 전체 삭제

아래 함수 전체를 삭제한다:

```js
function loadLegalSummary() {
  var f = _factories.find(function(x){ return x.id === _currentFactoryId; });
  var nameEl = document.getElementById('legalFactoryName');
  if (nameEl) nameEl.textContent = f ? f.name : '';
  ... (전체 함수)
}
```

#### 2-3. loadDiagHistory 수정 — 사업장(factory_id) 필터 적용

**현재 문제:** `company_id`로만 필터링하여 회사 전체 진단이력이 표시됨.
**수정:** 현재 선택된 `_currentFactoryId`로 필터링.

변경 전:
```js
function loadDiagHistory() {
  var el = document.getElementById('diagHistoryList');
  var companyId = localStorage.getItem('company_id') || '';
  var url = '/quotes/survey/list?page=1&page_size=5' + (companyId ? '&company_id='+companyId : '');
  apiFetch(url)
    .then(function(r){ return r.ok ? r.json() : Promise.reject(r.status); })
    .then(function(d){
      var items = (d.data && d.data.items) || d.items || [];
      if (!items.length) { el.innerHTML='<div class="text-center text-body-secondary small py-2">진단 이력 없음</div>'; return; }
      el.innerHTML = items.map(function(i){
        return '<div class="border-bottom py-2 small"><div class="fw-semibold">'+esc(i.factory_name||i.company_name||'미상')+
          '</div><div class="text-body-secondary">'+esc((i.created_at||'').slice(0,10))+'</div></div>';
      }).join('');
    }).catch(function(){ el.innerHTML='<div class="text-center text-body-secondary small py-2">진단 이력 없음</div>'; });
}
```

변경 후:
```js
function loadDiagHistory() {
  var el = document.getElementById('diagHistoryList');
  if (!el) return;
  if (!_currentFactoryId) {
    el.innerHTML = '<div class="text-center text-body-secondary small py-3">사업장을 선택해주세요.</div>';
    return;
  }
  var url = '/quotes/survey/list?page=1&page_size=5&factory_id=' + encodeURIComponent(_currentFactoryId);
  apiFetch(url)
    .then(function(r){ return r.ok ? r.json() : Promise.reject(r.status); })
    .then(function(d){
      var items = (d.data && d.data.items) || d.items || [];
      if (!items.length) {
        el.innerHTML = '<div class="text-center text-body-secondary small py-2">이 사업장의 진단 이력이 없습니다.</div>';
        return;
      }
      el.innerHTML = items.map(function(i){
        return '<div class="border-bottom py-2 small">'
          + '<div class="fw-semibold">' + esc(i.factory_name || i.company_name || '미상') + '</div>'
          + '<div class="text-body-secondary">' + esc((i.created_at||'').slice(0,10))
          + (i.engine_version ? ' · ' + esc(i.engine_version) : '') + '</div>'
          + '</div>';
      }).join('');
    })
    .catch(function(){
      el.innerHTML = '<div class="text-center text-body-secondary small py-2">진단 이력 없음</div>';
    });
}
```

핵심 변경:
- `company_id` → `factory_id` 파라미터로 변경
- `_currentFactoryId` 사용 (현재 드롭다운에서 선택한 사업장)
- factory_id 미선택 시 안내 메시지
- engine_version 표시 추가 (runtime 엔진 구분용)

---

## 작업 3: 진단이력 API factory_id 지원 확인

### 확인 대상: `tai-api/routers/` 에서 `/quotes/survey/list` 엔드포인트

해당 API가 `factory_id` 쿼리파라미터를 지원하는지 확인 필요.
만약 미지원이면 → Supabase에서 `factory_id` 필터를 추가하거나,
프론트에서 받은 전체 목록을 클라이언트 필터링으로 대체:

```js
// factory_id 미지원 시 대안
var url = '/quotes/survey/list?page=1&page_size=50&company_id=' + encodeURIComponent(companyId);
// ... 응답 후 클라이언트 필터:
var items = (d.data && d.data.items) || d.items || [];
items = items.filter(function(i) {
  return i.factory_id === _currentFactoryId;
}).slice(0, 5);
```

---

## 배포

tai-admin은 Cloudflare Pages 자동배포 (main push 시 즉시).

## 검증

- [ ] safe.taieng.co.kr 접속 → safety-dashboard.html로 자동 리다이렉트
- [ ] 법령진단현황 카드가 사라졌는지 확인
- [ ] 진단이력이 선택한 사업장의 것만 표시되는지 확인
- [ ] 사업장 드롭다운 변경 시 진단이력 갱신 확인
- [ ] 콘솔에 JS 에러 없는지 확인
