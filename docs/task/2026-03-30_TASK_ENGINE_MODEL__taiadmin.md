# 엔진설정 > 모델 관리 작업 지시서
## 담당: 백엔드 창 (Cursor) + 프론트 창

---

## 현황
- engine-model.html UI 완성됨
- 백엔드 API 4개 미구현 → 현재 페이지 전부 빈 화면
- equipment_assets.equipment_model_id 64/71개 연결 완료 (이 창에서 작업)
- 자산연결 현황 탭 미구현

---

# PART 1. 백엔드 API 구현 (Cursor)

## 파일: routers/engine_model.py (신규 생성)

```python
from fastapi import APIRouter, Query
from db.supabase_client import get_supabase

router = APIRouter(prefix="/engine-model", tags=["엔진-모델"])


# ── GET /engine-model/stats ──
@router.get("/stats")
def get_model_stats():
    sb = get_supabase()
    total = sb.table("equipment_model_master").select("id", count="exact").execute().count or 0

    # 설비종류, 제조사 distinct
    rows = sb.table("equipment_model_master").select(
        "equipment_std, manufacturer, cert_match_status"
    ).execute().data or []

    unique_std = len(set(r["equipment_std"] for r in rows if r.get("equipment_std")))
    unique_mfr = len(set(r["manufacturer"] for r in rows if r.get("manufacturer")))
    cert_matched = sum(1 for r in rows if r.get("cert_match_status") == "MATCHED")
    cert_no_match = total - cert_matched

    # 자산연결 현황
    asset_total = sb.table("equipment_assets").select("id", count="exact").execute().count or 0
    asset_linked = sb.table("equipment_assets").select(
        "id", count="exact"
    ).not_.is_("equipment_model_id", "null").execute().count or 0

    return {"status": "success", "data": {
        "total_models": total,
        "unique_std": unique_std,
        "unique_manufacturer": unique_mfr,
        "cert_matched": cert_matched,
        "cert_no_match": cert_no_match,
        "asset_total": asset_total,
        "asset_linked": asset_linked,
        "asset_unlinked": asset_total - asset_linked,
        "link_rate": round(asset_linked / asset_total * 100, 1) if asset_total else 0,
    }}


# ── GET /engine-model/filters ──
@router.get("/filters")
def get_model_filters():
    sb = get_supabase()
    rows = sb.table("equipment_model_master").select(
        "equipment_std, manufacturer, equipment_lv2"
    ).execute().data or []

    std_list = sorted(set(r["equipment_std"] for r in rows if r.get("equipment_std")))
    mfr_list = sorted(set(r["manufacturer"] for r in rows if r.get("manufacturer")))
    lv2_list = sorted(set(r["equipment_lv2"] for r in rows if r.get("equipment_lv2")))

    return {"status": "success", "data": {
        "equipment_std_list": std_list,
        "manufacturer_list": mfr_list,
        "equipment_lv2_list": lv2_list,
    }}


# ── GET /engine-model/list ──
@router.get("/list")
def list_models(
    page: int = 1,
    page_size: int = 30,
    search: str = None,
    equipment_std: str = None,
    equipment_lv2: str = None,
    manufacturer: str = None,
    source_type: str = None,
    cert_match_status: str = None,
    risk_min: int = None,
    risk_max: int = None,
):
    sb = get_supabase()
    q = sb.table("equipment_model_master").select(
        "id, equipment_std, equipment_lv2, manufacturer, model_name, "
        "model_year, expected_life_years, maintenance_cycle_months, "
        "risk_score, criticality_score, replacement_cost_index, "
        "certification_class, cert_match_status, source_type, country_of_origin"
    )

    if search:
        # 클라이언트 사이드 필터 (supabase python은 or_ 미지원시)
        q = q.or_(
            f"model_name.ilike.%{search}%,"
            f"manufacturer.ilike.%{search}%,"
            f"equipment_std.ilike.%{search}%"
        )
    if equipment_std:
        q = q.eq("equipment_std", equipment_std)
    if equipment_lv2:
        q = q.eq("equipment_lv2", equipment_lv2)
    if manufacturer:
        q = q.eq("manufacturer", manufacturer)
    if source_type:
        q = q.eq("source_type", source_type)
    if cert_match_status:
        q = q.eq("cert_match_status", cert_match_status)
    if risk_min is not None:
        q = q.gte("risk_score", risk_min)
    if risk_max is not None:
        q = q.lte("risk_score", risk_max)

    # 전체 수 조회
    count_res = q.execute()
    all_items = count_res.data or []
    total = len(all_items)

    # 페이지네이션
    offset = (page - 1) * page_size
    items = all_items[offset:offset + page_size]

    return {"status": "success", "data": {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }}


# ── GET /engine-model/{model_id} ──
@router.get("/{model_id}")
def get_model(model_id: str):
    sb = get_supabase()
    res = sb.table("equipment_model_master").select("*").eq("id", model_id).single().execute()
    if not res.data:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="모델을 찾을 수 없습니다.")

    # 연결된 자산 목록 조회
    assets = sb.table("equipment_assets").select(
        "id, asset_name, factory_id, manufacturer, install_year"
    ).eq("equipment_model_id", model_id).execute().data or []

    data = dict(res.data)
    data["linked_assets"] = assets
    data["linked_asset_count"] = len(assets)
    return {"status": "success", "data": data}


# ── PATCH /engine-model/{model_id} ──
@router.patch("/{model_id}")
def update_model(model_id: str, body: dict):
    sb = get_supabase()
    # 허용 필드만 필터링
    allowed = [
        "equipment_std", "equipment_lv2", "manufacturer", "model_name",
        "model_year", "expected_life_years", "maintenance_cycle_months",
        "risk_score", "criticality_score", "replacement_cost_index",
        "certification_class", "cert_match_status", "country_of_origin",
    ]
    update_data = {k: v for k, v in body.items() if k in allowed}
    if not update_data:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="수정할 데이터가 없습니다.")

    res = sb.table("equipment_model_master").update(update_data).eq("id", model_id).execute()
    return {"status": "success", "data": res.data[0] if res.data else {}}


# ── GET /engine-model/assets/linked ── (자산연결 현황)
@router.get("/assets/linked")
def get_linked_assets(
    page: int = 1,
    page_size: int = 30,
    linked: str = None,  # "Y" | "N" | None
    equipment_std: str = None,
):
    sb = get_supabase()
    q = sb.table("equipment_assets").select(
        "id, asset_name, manufacturer, equipment_type_code, "
        "install_year, factory_id, equipment_model_id"
    )
    if linked == "Y":
        q = q.not_.is_("equipment_model_id", "null")
    elif linked == "N":
        q = q.is_("equipment_model_id", "null")

    all_items = q.execute().data or []

    # equipment_model_id → 모델 정보 join (Python 레벨)
    model_ids = list(set(
        item["equipment_model_id"] for item in all_items
        if item.get("equipment_model_id")
    ))
    model_map = {}
    if model_ids:
        mres = sb.table("equipment_model_master").select(
            "id, equipment_std, model_name, manufacturer, "
            "expected_life_years, maintenance_cycle_months, risk_score"
        ).in_("id", model_ids).execute().data or []
        model_map = {m["id"]: m for m in mres}

    enriched = []
    for item in all_items:
        mid = item.get("equipment_model_id")
        item["model"] = model_map.get(mid) if mid else None
        if equipment_std and item.get("model"):
            if item["model"].get("equipment_std") != equipment_std:
                continue
        enriched.append(item)

    total = len(enriched)
    offset = (page - 1) * page_size
    items = enriched[offset:offset + page_size]

    return {"status": "success", "data": {
        "items": items, "total": total, "page": page, "page_size": page_size,
    }}
```

## main.py에 라우터 등록

```python
from routers import engine_model
app.include_router(engine_model.router)
```

## 검증
```bash
curl -s https://api.taieng.co.kr/engine-model/stats | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['data'])"
# 기대: total_models=2874, asset_linked=64, link_rate=90.1

curl -s https://api.taieng.co.kr/engine-model/list?page=1&page_size=3 | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['data']['total'], d['data']['items'][0]['equipment_std'])"
# 기대: 2874 [설비명]
```

## git commit
```
feat: engine-model API 구현 (stats/filters/list/detail/patch/assets)
```

완료 후 회의실 창에 결과 보고.

---

# PART 2. 프론트 수정 (프론트 창)

## 파일: admin/full-version/html/horizontal-menu-template/engine-model.html

### 수정1. 통계 카드에 자산연결 카드 추가 (6번째 카드)

기존 5개 카드 → 6개로 확장. 마지막에 추가:
```html
<div class="col-6 col-lg">
  <div class="card h-100" id="card-link">
    <div class="card-body d-flex align-items-center gap-3">
      <div class="avatar avatar-lg bg-label-primary rounded">
        <i class="icon-base ti tabler-link icon-28px text-primary"></i>
      </div>
      <div>
        <div class="text-body-secondary small">자산 연결률</div>
        <h4 class="mb-0" id="stat-link-rate">...</h4>
        <small class="text-body-secondary" id="stat-link-detail">0 / 0개</small>
      </div>
    </div>
  </div>
</div>
```

### 수정2. 탭 구조 추가

테이블 카드를 탭 카드로 교체:

```html
<div class="card">
  <div class="card-header">
    <ul class="nav nav-tabs card-header-tabs" role="tablist">
      <li class="nav-item">
        <button class="nav-link active" data-bs-toggle="tab" data-bs-target="#tab-models" id="btn-tab-models">📦 모델 목록</button>
      </li>
      <li class="nav-item">
        <button class="nav-link" data-bs-toggle="tab" data-bs-target="#tab-assets" id="btn-tab-assets">🔗 자산 연결 현황</button>
      </li>
    </ul>
  </div>
  <div class="card-body p-0">
    <div class="tab-content">

      <!-- 탭1: 모델목록 (기존 테이블 그대로) -->
      <div class="tab-pane fade show active" id="tab-models">
        <!-- 기존 card-header (검색건수/페이지당) + table + card-footer -->
      </div>

      <!-- 탭2: 자산연결 현황 -->
      <div class="tab-pane fade" id="tab-assets">
        <div class="p-3 border-bottom">
          <div class="row g-2 align-items-end">
            <div class="col-md-3">
              <label class="form-label small mb-1">연결 여부</label>
              <select class="form-select form-select-sm" id="af-linked">
                <option value="">전체</option>
                <option value="Y">연결됨</option>
                <option value="N">미연결</option>
              </select>
            </div>
            <div class="col-md-3">
              <button class="btn btn-primary btn-sm w-100" onclick="assetPage=1;loadAssets()">
                <i class="ti ti-search me-1"></i>검색
              </button>
            </div>
          </div>
        </div>
        <div class="table-responsive">
          <table class="table table-hover mb-0">
            <thead>
              <tr>
                <th style="width:40px;"><input type="checkbox" class="form-check-input" onclick="toggleAll('asset-tbody',this)"></th>
                <th style="width:50px;">No.</th>
                <th>설비명</th>
                <th>설비유형코드</th>
                <th class="text-center">연결상태</th>
                <th>연결모델 표준명</th>
                <th>연결모델명</th>
                <th class="text-center">수명(년)</th>
                <th class="text-center">위험도</th>
              </tr>
            </thead>
            <tbody id="asset-tbody">
              <tr><td colspan="9" class="text-center py-4">탭 클릭 시 로드됩니다.</td></tr>
            </tbody>
          </table>
        </div>
        <div class="card-footer d-flex justify-content-between align-items-center">
          <small class="text-body-secondary" id="asset-page-info"></small>
          <nav><ul class="pagination pagination-sm mb-0" id="asset-pagination"></ul></nav>
        </div>
      </div>

    </div>
  </div>
</div>
```

### 수정3. 통계 카드 loadStats()에 자산연결 추가

```javascript
// loadStats() 내부에 추가
document.getElementById('stat-link-rate').textContent = (s.link_rate || 0) + '%';
document.getElementById('stat-link-detail').textContent =
  (s.asset_linked || 0) + ' / ' + (s.asset_total || 0) + '개';

// link_rate에 따라 카드 색상
var rate = s.link_rate || 0;
var cardEl = document.getElementById('card-link');
if (rate >= 80) {
  document.querySelector('#card-link .avatar').className = 'avatar avatar-lg bg-label-success rounded';
  document.querySelector('#card-link .avatar i').className = 'icon-base ti tabler-link icon-28px text-success';
  document.getElementById('stat-link-rate').className = 'mb-0 text-success fw-bold';
} else if (rate >= 50) {
  document.querySelector('#card-link .avatar').className = 'avatar avatar-lg bg-label-warning rounded';
} else {
  document.querySelector('#card-link .avatar').className = 'avatar avatar-lg bg-label-danger rounded';
  document.getElementById('stat-link-rate').className = 'mb-0 text-danger fw-bold';
}
```

### 수정4. 자산 탭 JavaScript 추가

```javascript
var assetPage = 1, assetPageSize = 30;

async function loadAssets() {
  var tbody = document.getElementById('asset-tbody');
  tbody.innerHTML = '<tr><td colspan="9" class="text-center py-4"><div class="spinner-border spinner-border-sm text-primary"></div></td></tr>';

  var linked = document.getElementById('af-linked').value;
  var url = '/engine-model/assets/linked?page=' + assetPage + '&page_size=' + assetPageSize;
  if (linked) url += '&linked=' + linked;

  try {
    var data = await apiCall('GET', url);
    var items = (data && data.data && data.data.items) || [];
    var total = (data && data.data && data.data.total) || 0;
    var start = (assetPage - 1) * assetPageSize;

    document.getElementById('asset-page-info').textContent =
      items.length ? (start+1) + ' - ' + (start+items.length) + ' / 총 ' + total + '건' : '0건';

    if (!items.length) {
      tbody.innerHTML = '<tr><td colspan="9" class="text-center py-4 text-body-secondary">데이터가 없습니다.</td></tr>';
      return;
    }

    tbody.innerHTML = items.map(function(a, i) {
      var m = a.model || {};
      var isLinked = !!a.equipment_model_id;
      var statusBadge = isLinked
        ? '<span class="badge bg-success">연결됨</span>'
        : '<span class="badge bg-danger">미연결</span>';
      return '<tr>' +
        '<td onclick="event.stopPropagation()"><input type="checkbox" class="form-check-input row-check"></td>' +
        '<td>' + (start + i + 1) + '</td>' +
        '<td><strong>' + esc(a.asset_name || '-') + '</strong></td>' +
        '<td><span class="badge bg-label-secondary">' + esc(a.equipment_type_code || '-') + '</span></td>' +
        '<td class="text-center">' + statusBadge + '</td>' +
        '<td>' + esc(m.equipment_std || '-') + '</td>' +
        '<td class="small text-body-secondary">' + esc(m.model_name || '-') + '</td>' +
        '<td class="text-center">' + (m.expected_life_years != null ? m.expected_life_years + '년' : '-') + '</td>' +
        '<td>' + scoreBar(m.risk_score) + '</td>' +
        '</tr>';
    }).join('');

    renderPagination(total, assetPage, assetPageSize,
      function(p){ assetPage = p; loadAssets(); }, 'asset-pagination');
  } catch(e) {
    tbody.innerHTML = '<tr><td colspan="9" class="text-center py-4 text-danger">' + esc(e.message) + '</td></tr>';
  }
}

// 탭 클릭 시 자동 로드
document.getElementById('btn-tab-assets').addEventListener('click', function() {
  if (!document.getElementById('asset-tbody').querySelector('tr[data-id], tr.loaded')) {
    loadAssets();
  }
});
```

### 수정5. 사이드패널 자산연결 목록 섹션 추가

`renderPanel(m)` 함수 내 마지막 섹션에 추가:

```javascript
// 연결된 자산 목록
var assets = m.linked_assets || [];
html += '<div class="card mb-3"><div class="card-header py-2 d-flex justify-content-between">';
html += '<span class="fw-semibold small">🔗 연결 설비자산</span>';
html += '<span class="badge bg-label-primary">' + assets.length + '개</span>';
html += '</div><div class="card-body py-2">';
if (assets.length === 0) {
  html += '<p class="text-body-secondary small mb-0">연결된 설비자산이 없습니다.</p>';
} else {
  html += '<ul class="list-unstyled mb-0">';
  assets.forEach(function(a) {
    html += '<li class="d-flex align-items-center gap-2 py-1 border-bottom">';
    html += '<i class="icon-base ti tabler-tool text-primary"></i>';
    html += '<span class="small">' + esc(a.asset_name) + '</span>';
    if (a.install_year) html += '<small class="text-body-secondary ms-auto">' + a.install_year + '년 설치</small>';
    html += '</li>';
  });
  html += '</ul>';
}
html += '</div></div>';
```

## git commit
```
feat: engine-model.html 자산연결 탭 + 연결률 카드 추가
```
