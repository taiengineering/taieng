# 기상 작업중지 위젯 — 대시보드 작업지시서

> 작성일: 2026-04-11  
> 담당: 프론트엔드창 (tai-admin repo)  
> 대상 파일: `site/full-version/html/horizontal-menu-template/index.html`

---

## 배경 및 원칙

| 항목 | 내용 |
|---|---|
| 위치 기준 | **factories 테이블의 latitude/longitude** (등록된 시설 주소 기반) |
| 결과 표시 | 대시보드 위젯 (안전관리자 이상만 보임) |
| SMS 발송 | 크론이 담당, 위젯에서는 **발송 여부 상태만 표시** |
| SMS 중복 방지 | 동일 이벤트 1회만 발송 (크론에서 처리) |
| 작업자 미표시 | role_code 014(작업자)에게는 위젯 미노출 |

---

## 위젯 UI 설계

```
┌────────────────────────────────────────────────────┐
│ 🌤 기상 작업중지 모니터링          [조회] 버튼      │
│ 시설: 대성정밀 1공장 ▼ (드롭다운)                   │
├────────────────────────────────────────────────────┤
│ [조회 전 상태]                                      │
│ "등록된 시설 주소 기반으로 현재 기상을 확인합니다." │
│ [조회하기] 버튼                                     │
├────────────────────────────────────────────────────┤
│ [조회 후 — 정상]                                    │
│ ✅ 작업 진행 가능                                   │
│ 기온 15.6°C  풍속 3.6m/s  강수 없음                │
│ 📍 인천광역시 미추홀구  ·  16:00 기준               │
│ 💬 크론 자동 감시 중 (30분 주기)                    │
├────────────────────────────────────────────────────┤
│ [조회 후 — 작업중지 필요]                            │
│ ⚠️ 작업중지 필요                                   │
│ 강풍 12.3m/s — 고소작업·타워크레인 중단 (산안법 §37)│
│ 📨 안전관리자 이상 SMS 발송됨 (2026.04.11 16:00)    │
│ 💬 크론 자동 감시 중 (30분 주기) · 중복 발송 없음   │
└────────────────────────────────────────────────────┘
```

---

## 삽입 위치

`index.html`의 **빠른 바로가기** 카드와 **다가오는 점검 일정** 카드 사이에 삽입.

```html
<!-- 기존 빠른 바로가기 row 끝 -->
</div></div>  ← 이 태그 바로 다음

<!-- 기상 작업중지 위젯 row 추가 -->
<div class="row g-4 mb-5" id="wx-widget-wrap">
  ...
</div>

<!-- 다가오는 점검 일정 row -->
<div class="row g-4">
```

---

## 위젯 HTML 코드

```html
<!-- ── 기상 작업중지 모니터링 위젯 (안전관리자 이상만 표시) ── -->
<div class="row g-4 mb-5" id="wx-widget-wrap" style="display:none;">
  <div class="col-12">
    <div class="card border-0" id="wx-widget-card" style="
      background: linear-gradient(135deg,#1a4fa0,#0d2e6e);
      border-radius:14px; color:#fff;">
      <div class="card-body p-4">

        <!-- 헤더 -->
        <div class="d-flex align-items-center justify-content-between mb-3 flex-wrap gap-2">
          <div class="d-flex align-items-center gap-2">
            <span style="font-size:1.4rem;">🌤</span>
            <div>
              <div class="fw-bold" style="font-size:.95rem;">기상 작업중지 모니터링</div>
              <div style="font-size:.78rem;opacity:.7;">
                등록된 시설 주소 기반 · 30분 자동 감시 중
              </div>
            </div>
          </div>
          <!-- 시설 선택 드롭다운 -->
          <div class="d-flex align-items-center gap-2 flex-wrap">
            <select id="wx-factory-select"
              class="form-select form-select-sm"
              style="width:auto;min-width:140px;background:rgba(255,255,255,.15);
                     color:#fff;border-color:rgba(255,255,255,.3);">
              <option value="">시설 선택...</option>
            </select>
            <button class="btn btn-sm btn-light fw-bold px-3" onclick="wxCheck()">
              조회
            </button>
          </div>
        </div>

        <!-- 결과 영역 -->
        <div id="wx-result" style="
          background:rgba(255,255,255,.12);
          border-radius:10px;
          padding:14px 16px;
          font-size:.85rem;
          line-height:1.6;">
          <span style="opacity:.7;">
            시설을 선택하고 [조회]를 누르면 현재 기상과 작업중지 여부를 확인합니다.
          </span>
        </div>

      </div>
    </div>
  </div>
</div>
```

---

## 위젯 JavaScript 코드

`(function init(){...})();` 호출 **이전**에 추가:

```javascript
/* ── 기상 작업중지 위젯 ── */
const WX_ALLOWED_ROLES = ['001','002','003','010','011','012','013','016','025'];

async function wxInit() {
  const roleCode = localStorage.getItem('role_code') || '';
  // 작업자 등 제외
  if (!WX_ALLOWED_ROLES.includes(roleCode)) return;
  document.getElementById('wx-widget-wrap').style.display = '';

  // 시설 목록 로드
  try {
    const companyId = localStorage.getItem('company_id');
    const r = await apiCall('GET',
      '/factories?size=20' + (companyId ? '&company_id=' + companyId : ''));
    const factories = (r && r.data && r.data.items) || [];
    const sel = document.getElementById('wx-factory-select');
    factories.forEach(f => {
      if (!f.latitude || !f.longitude) return; // 좌표 없으면 제외
      const opt = document.createElement('option');
      opt.value = JSON.stringify({lat: f.latitude, lon: f.longitude, name: f.name});
      opt.textContent = f.name;
      sel.appendChild(opt);
    });
    // 시설 1개면 자동 선택 후 조회
    if (factories.filter(f => f.latitude && f.longitude).length === 1) {
      sel.selectedIndex = 1;
      wxCheck();
    }
  } catch(e) {}
}

async function wxCheck() {
  const sel = document.getElementById('wx-factory-select');
  const result = document.getElementById('wx-result');
  const card = document.getElementById('wx-widget-card');

  if (!sel.value) {
    result.innerHTML = '<span style="opacity:.7;">시설을 선택해 주세요.</span>';
    return;
  }

  result.innerHTML = '<div class="spinner-border spinner-border-sm me-2"></div>조회 중...';

  const { lat, lon, name } = JSON.parse(sel.value);

  try {
    const r = await fetch(
      `https://api.taieng.co.kr/weather/now?lat=${lat}&lon=${lon}`);
    const d = await r.json();
    if (d.status !== 'success') throw new Error('api error');

    const wx = d.weather;
    const ws = d.work_stop;
    const obs = d.observed;
    const baseTime = String(obs.base_time || '').padStart(4,'0');
    const obsLabel = `${obs.base_date||''} ${baseTime.slice(0,2)}:${baseTime.slice(2,4)} 기준`;

    if (ws.required) {
      // 작업중지 필요 — 빨간 카드
      card.style.background = 'linear-gradient(135deg,#991b1b,#7f1d1d)';
      const reasons = (ws.triggered || []).map(t =>
        `<li>⚠️ ${esc(t.msg || t.message || t.name)}</li>`
      ).join('');
      result.innerHTML = `
        <div class="fw-bold mb-2" style="font-size:1rem;">⛔ 작업중지 필요</div>
        <ul class="mb-2 ps-3" style="font-size:.83rem;">${reasons || '<li>' + esc(ws.message) + '</li>'}</ul>
        <div style="font-size:.78rem;opacity:.75;">
          📍 ${esc(name)} · ${obsLabel}<br>
          📨 안전관리자 이상 경고 문자 발송됨 (크론 자동 · 중복 발송 없음)
        </div>`;
    } else {
      // 정상 — 파란 카드
      card.style.background = 'linear-gradient(135deg,#1a4fa0,#0d2e6e)';
      result.innerHTML = `
        <div class="fw-bold mb-2" style="font-size:1rem;">✅ 작업 진행 가능</div>
        <div style="font-size:.83rem;opacity:.9;" class="mb-2">
          기온 ${wx.temperature ?? '--'}°C &nbsp;
          풍속 ${wx.wind_speed ?? '--'} m/s &nbsp;
          강수 ${wx.rain_1h > 0 ? wx.rain_1h + 'mm' : '없음'}
        </div>
        <div style="font-size:.78rem;opacity:.7;">
          📍 ${esc(name)} · ${obsLabel}<br>
          🔄 크론 자동 감시 중 (30분 주기) · 기준 초과 시 자동 문자 발송
        </div>`;
    }
  } catch(e) {
    result.innerHTML = '<span style="opacity:.7;">날씨 정보를 불러올 수 없습니다.</span>';
  }
}
```

`(function init(){...})();` 블록 안에 추가:
```javascript
wxInit();
```

---

## 백엔드 크론 연계 (별도 백엔드 작업)

```
크론: WEATHER_WORK_STOP_CHECK (30분마다)
  └ 활성 factories 전체 순회
  └ factories.latitude / longitude로 /weather/now 호출
  └ work_stop.required = true 이면:
      └ 해당 시설 안전관리자 이상 조회
        (role_code IN ['001','002','003','010','011','012','013','016','025'])
      └ notifications 테이블에 해당 시설+당일 레코드 있는지 확인
        → 없으면 SMS/이메일 발송 + 레코드 삽입 (1회만)
        → 있으면 발송 SKIP
      └ work_stop.required = false 로 복구 시 레코드 삭제 (다음 이벤트 대비)
```

**SMS 1회 보장 쿼리:**
```sql
-- 발송 전 체크
SELECT id FROM notifications
WHERE factory_id = $1
  AND notification_type = 'WEATHER_WORK_STOP'
  AND created_at::date = CURRENT_DATE
LIMIT 1;

-- 없으면 INSERT 후 SMS 발송
INSERT INTO notifications (...) VALUES (...);
```

---

## 완료 기준

- [ ] 대시보드 위젯 노출 (안전관리자 이상만)
- [ ] 시설 드롭다운 — 좌표 있는 시설만 표시
- [ ] 시설 1개면 자동 조회
- [ ] 정상 → 파란 카드, 작업중지 → 빨간 카드
- [ ] 작업중지 시 "경고 문자 발송됨" 표시
- [ ] 정상 시 "크론 자동 감시 중" 표시
- [ ] role_code 014(작업자) 미노출 확인
