# WORK ORDER 2026-04-24 · PWA 프론트 보강 (P0 + P1)

- **대상**: Cursor (프론트창)
- **레포/브랜치**: `tai-admin` / `main` (직접 커밋)
- **배포**: main push → Cloudflare Pages 자동 반영 (`safe.taieng.co.kr`)
- **관련 리뷰 문서**: `tai-admin/docs/PWA_APP_REVIEW_20260424.md`
- **백엔드 지시서**: `tai-api/docs/WORK_ORDER_20260424_pwa_backend.md`
- **의존 관계**: **P0-1~P0-3은 백엔드 엔드포인트 배포 후 착수 가능**. P0-4~P0-7, P1 전체는 즉시 착수 가능

---

## 필수 준수 규칙

1. 200+ 라인 파일 수정은 반드시 Cursor (MCP push_files 금지)
2. 모든 페이지 수정 시 **기존 레이아웃/탭/JS 구조 보존** — 최소 침습 원칙
3. 로컬 미리보기로 375px 모바일 뷰 깨짐 여부 확인
4. 커밋은 기능 단위(파일 묶음)로 분할해서 커밋 메시지에 이슈 번호 명시 (`fix(P0-1): ...`)
5. **금지**: 카카오 API, localStorage에 base64 사진, 설명 없는 주석 삭제, 데모 데이터 재삽입
6. **허용**: 기존 MessageMi SMS, Vworld API, Supabase Storage 사용

---

## 배경

점검 리뷰(`PWA_APP_REVIEW_20260424.md`)에서 총 37건 이슈 발견. 본 작업 오더는 **P0 6건 + P1 11건** 처리. P2/P3는 별도 오더.

---

## PART A · 즉시 착수 가능 (백엔드 의존 없음)

### P0-4. FCM SW URL 수정 — **5분 작업**

**파일**: `tadmin/full-version/firebase-messaging-sw.js`

```js
// Before
let url = 'https://safe.taieng.co.kr/html/horizontal-menu-template/worker-check.html';

// After
let url = 'https://safe.taieng.co.kr/app/index.html';

// + data.type 분기 추가
const URL_MAP = {
  emergency: '/app/emergency.html',
  check: '/app/inspect.html',
  corrective: '/app/corrective.html',
  approve: '/app/work_request.html',
  notice: '/app/notifications.html',
};
let url = 'https://safe.taieng.co.kr' + (URL_MAP[data.type] || '/app/index.html');
if (data.url) url = data.url;
```

---

### P0-5. 데모 데이터 제거

**파일**: `tadmin/full-version/app/notifications.html`

```js
// Before (L 165+)
if(!_notifs){
  _notifs=[
    {id:'n1',type:'check',...},  // 5건 데모
    ...
  ];
  localStorage.setItem('tai_notifs',JSON.stringify(_notifs));
}

// After
if(!_notifs) _notifs = [];

// 서버 응답 병합 로직에서 데모 잔존 제거
// Before: ..._notifs.filter(n=>n.id.startsWith('n'))
// After:  ..._notifs.filter(n=>!String(n.id).startsWith('n'))  // 데모 제외
```

**파일**: `tadmin/full-version/app/history.html`

```js
// Before (L 100+): 서버 빈 응답 시 8건 데모 생성
if(!_records.length){
  _records=Array.from({length:8},...);
}

// After
if(!_records.length){
  _records = [];
}
```

렌더 함수에서 `_records.length === 0`이면 기존 `empty-view` 표시 (이미 구현돼 있음).

---

### P0-6. camera.html 처리

**결정**: 삭제. 현재 dead code이며 `inspect.html`은 `<input type="file" capture>`로 충분.

**파일**: `tadmin/full-version/app/camera.html` — **파일 삭제**  
**파일**: `tadmin/full-version/app/test.txt` — **파일 삭제**

(Git에서 delete 후 커밋)

---

### P1-5. SW Precache 강화

**파일**: `tadmin/full-version/app/sw.js`

```js
const CACHE_NAME = 'tai-safe-v1.4';  // 버전 bump
const RUNTIME_CACHE = 'tai-safe-runtime-v1.4';

const PRECACHE_URLS = [
  '/app/index.html',
  '/app/inspect.html',
  '/app/construction_inspect.html',
  '/app/report.html',
  '/app/emergency.html',
  '/app/tbm.html',
  '/app/corrective.html',
  '/app/education.html',
  '/app/risk.html',
  '/app/work_request.html',
  '/app/attendance.html',
  '/app/qr_scan.html',
  '/app/notifications.html',
  '/app/history.html',
  '/app/profile.html',
  '/app/install.html',
  '/app/i18n.js',
  '/app/_utils.js',       // P1-1에서 신설
  '/app/manifest.json',
  '/assets/img/tai-icon-192.png',
  '/assets/img/tai-icon-512.png',
];
```

`install` 이벤트에서 `cache.addAll(PRECACHE_URLS)` 유지.

---

### P1-1. 공통 유틸 신설 — **핵심 작업**

**신규 파일**: `tadmin/full-version/app/_utils.js`

```js
// TAI Safe 공통 유틸 v1.0
(function(global){
  const API = 'https://api.taieng.co.kr';

  // ── 인증 ─────────────────────────
  function getUser(){
    try { return JSON.parse(localStorage.getItem('tai_user')||'null'); } catch { return null; }
  }
  function getToken(){
    return localStorage.getItem('access_token') || '';
  }
  function requireAuth(redirect='index.html'){
    const u = getUser();
    if (!u || !u.worker_id) {
      location.href = redirect;
      return null;
    }
    return u;
  }

  // ── API 호출 (Authorization 자동, 오프라인 큐) ─────
  async function apiFetch(path, options={}){
    const url = path.startsWith('http') ? path : API + path;
    const token = getToken();
    const headers = {
      ...(options.headers || {}),
      ...(token ? {'Authorization': 'Bearer ' + token} : {}),
    };
    if (options.body && !(options.body instanceof FormData) && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }
    try {
      const res = await fetch(url, { ...options, headers });
      if (res.status === 401) {
        // 토큰 만료 — 로그인 페이지로
        localStorage.removeItem('tai_user');
        localStorage.removeItem('access_token');
        location.href = '/app/index.html';
        throw new Error('AUTH_EXPIRED');
      }
      return res;
    } catch (e) {
      throw e;
    }
  }

  // ── 사진 업로드 (백엔드 TASK 1 연동) ──────
  async function uploadPhoto(file, context, ids={}){
    const fd = new FormData();
    fd.append('file', file);
    fd.append('context', context);  // inspection | report | emergency | tbm
    if (ids.inspection_id) fd.append('inspection_id', ids.inspection_id);
    if (ids.factory_id)   fd.append('factory_id', ids.factory_id);
    if (ids.site_id)      fd.append('site_id', ids.site_id);
    const res = await apiFetch('/uploads/inspection-photo', { method:'POST', body: fd });
    if (!res.ok) throw new Error('UPLOAD_FAILED_' + res.status);
    return res.json();  // {url, path, size, mime}
  }

  // Base64 DataURL → File 변환 (기존 Base64 저장된 사진 재전송용)
  function dataUrlToFile(dataUrl, filename='photo.jpg'){
    const [meta, b64] = dataUrl.split(',');
    const mime = meta.match(/:(.*?);/)[1];
    const bin = atob(b64);
    const arr = new Uint8Array(bin.length);
    for (let i=0; i<bin.length; i++) arr[i] = bin.charCodeAt(i);
    return new File([arr], filename, { type: mime });
  }

  // ── 오프라인 큐 ─────────────────────────
  function queuePush(kind, body){
    const key = `tai_queue_${kind}_${Date.now()}`;
    try {
      localStorage.setItem(key, JSON.stringify(body));
    } catch (e) {
      // quota 초과 — 가장 오래된 큐부터 삭제
      queueCleanup();
      try { localStorage.setItem(key, JSON.stringify(body)); } catch {}
    }
    return key;
  }
  function queueCleanup(maxPerKind=20){
    const kinds = {};
    Object.keys(localStorage).filter(k=>k.startsWith('tai_queue_')).forEach(k=>{
      const parts = k.split('_');
      const kind = parts[2];
      (kinds[kind] = kinds[kind] || []).push(k);
    });
    Object.values(kinds).forEach(arr=>{
      arr.sort(); // timestamp 오름차순
      while (arr.length > maxPerKind) {
        localStorage.removeItem(arr.shift());
      }
    });
  }
  async function queueFlush(kind, endpoint){
    const keys = Object.keys(localStorage).filter(k=>k.startsWith(`tai_queue_${kind}_`));
    for (const key of keys) {
      try {
        const body = JSON.parse(localStorage.getItem(key)||'null');
        if (!body) { localStorage.removeItem(key); continue; }
        const res = await apiFetch(endpoint, { method:'POST', body: JSON.stringify(body) });
        if (res.ok) localStorage.removeItem(key);
      } catch (e) { /* 네트워크 에러 — 다음 기회 */ }
    }
  }

  // ── 로그아웃 (모든 tai_* 키 + access_token) ─────
  function logoutClean(){
    const prefixes = ['tai_', 'access_token'];
    Object.keys(localStorage).forEach(k => {
      if (prefixes.some(p => k === p || k.startsWith(p))) {
        localStorage.removeItem(k);
      }
    });
  }

  // ── Expose ──────────────────────
  global.TAI = {
    API, getUser, getToken, requireAuth,
    apiFetch, uploadPhoto, dataUrlToFile,
    queuePush, queueCleanup, queueFlush,
    logoutClean,
  };
})(window);
```

**모든 페이지에서 import**: `<script src="_utils.js"></script>`를 `<script src="i18n.js"></script>` 아래 삽입.

---

### P1-6. i18n 언어 자동 감지

**파일**: `tadmin/full-version/app/i18n.js`

```js
// 기존 getLang()
function getLang() {
  const stored = localStorage.getItem('tai_lang_code');
  if (stored && TAI_I18N[stored]) return stored;
  // 브라우저 locale 감지 (최초 1회)
  const nav = (navigator.language || 'ko').slice(0,2).toLowerCase();
  const map = { zh:'zh', vi:'vi', ne:'ne', km:'km', fil:'tl', tl:'tl', en:'en', ko:'ko' };
  const detected = map[nav] || 'ko';
  localStorage.setItem('tai_lang_code', detected);
  return detected;
}
```

---

### P1-7. 로그아웃 정리

**파일**: `tadmin/full-version/app/index.html`, `profile.html`

```js
// Before
function doLogout(){
  if(!confirm(t('logout_confirm')))return;
  localStorage.removeItem('tai_user');
  _user=null;
  showPage('pg-auth'); // or location.href='index.html'
}

// After
function doLogout(){
  if(!confirm(t('logout_confirm')))return;
  TAI.logoutClean();
  _user=null;
  location.href='index.html';
}
```

---

## PART B · 백엔드 배포 후 착수 (P0-1 ~ P0-3)

> **선결 조건**: 백엔드 `tai-api/docs/WORK_ORDER_20260424_pwa_backend.md` TASK 1~4 배포 완료 확인 후 진행.

### P0-1. emergency.html 실패 처리 통합

**파일**: `tadmin/full-version/app/emergency.html`

```js
// Before
async function sendEmergency(){
  ...
  try{
    await fetch(API+'/emergency/report',{...});  // 실패 은폐
  }catch(e){}
  // 무조건 done 화면
  document.getElementById('reportNum').textContent = 'EMG-'+Date.now()...;
  // ...
}

// After
async function sendEmergency(){
  const user = TAI.getUser();
  if (!user) { alert('로그인이 필요합니다'); location.href='index.html'; return; }

  const typeLabel = _typeKey ? t('em_type_'+_typeKey) : t('em_unclassified');
  const body = {
    phone: user.phone || '',
    worker_name: user.name || t('em_worker_default'),
    accident_type: typeLabel,
    accident_type_key: _typeKey || 'other',
    location: '',
    photo_urls: [],  // 긴급신고는 사진 옵션 (현재 없음)
  };

  if (navigator.geolocation) {
    try {
      const pos = await new Promise((res,rej) =>
        navigator.geolocation.getCurrentPosition(res,rej,{timeout:3000}));
      body.location = `${pos.coords.latitude},${pos.coords.longitude}`;
      body.location_lat = pos.coords.latitude;
      body.location_lng = pos.coords.longitude;
    } catch(e) {}
  }

  let reportNumber = null;
  let saved = false;
  try {
    const res = await TAI.apiFetch('/emergency/report', {
      method: 'POST',
      body: JSON.stringify(body),
    });
    if (res.ok) {
      const j = await res.json();
      reportNumber = j.report_number;
      saved = true;
    } else {
      throw new Error('server ' + res.status);
    }
  } catch(e) {
    // 오프라인 큐 적재
    TAI.queuePush('emergency', body);
    reportNumber = 'OFFLINE-' + Date.now().toString().slice(-6);
  }

  // 활동 로그
  const acts = JSON.parse(localStorage.getItem('tai_activities')||'[]');
  acts.unshift({
    type:'bad', icon:'🚨',
    title: t('em_activity_title'),
    sub: typeLabel + (saved?'':' (오프라인 저장)'),
    time: new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'}),
  });
  localStorage.setItem('tai_activities', JSON.stringify(acts.slice(0,10)));

  // done 화면
  document.getElementById('emBody').style.display='none';
  document.getElementById('doneScreen').style.display='flex';
  document.getElementById('reportNum').textContent = t('em_report_num_prefix') + reportNumber;

  // 오프라인 저장인 경우 done 메시지 변경
  if (!saved) {
    document.getElementById('doneMsgEl').innerHTML =
      '⚠ 네트워크 오류로 기기에 임시 저장됐습니다.<br>즉시 119·112에 직접 전화하세요.<br>네트워크 복구 시 자동 재전송됩니다.';
    document.getElementById('doneMsgEl').style.color = '#ffab00';
  }

  localStorage.setItem('tai_last_emergency', JSON.stringify({...body, reportNum: reportNumber, saved}));
}

// 페이지 로드 시 오프라인 큐 플러시 시도
window.addEventListener('DOMContentLoaded', () => {
  TAI.queueFlush('emergency', '/emergency/report');
});
```

**핵심 변경**:
- Authorization 헤더 자동 부착 (apiFetch 사용)
- 서버 실패 시 사용자에게 명시적 경고 + 오프라인 저장
- 오프라인인 경우 119 직접 전화 유도 문구
- 서버 발급 `report_number` 사용

---

### P0-2. report.html 사진 업로드 분리

**파일**: `tadmin/full-version/app/report.html`

```js
// Before
async function submitReport(){
  const body = {
    ...
    photos: _photos,  // Base64 배열 — 413 위험
  };
  await fetch(API+'/safety-reports', {method:'POST', ...});
  // 실패 은폐
}

// After
async function submitReport(){
  const user = TAI.getUser();
  if (!user) { alert('로그인 필요'); return; }

  const btn = document.getElementById('submitBtn');
  btn.disabled = true;
  btn.textContent = t('report_sending');

  // 1단계: 사진 먼저 업로드 → URL 배열 확보
  const photo_urls = [];
  for (let i = 0; i < _photos.length; i++) {
    try {
      const file = TAI.dataUrlToFile(_photos[i], `report_${i+1}.jpg`);
      const up = await TAI.uploadPhoto(file, 'report', {
        factory_id: user.factory_id,
        site_id: user.site_id,
      });
      photo_urls.push(up.url);
    } catch (e) {
      console.warn('photo upload failed', i, e);
      // 사진 일부 실패해도 신고는 계속
    }
  }

  // 2단계: 신고 body (photo_urls로 전송)
  const body = {
    phone: user.phone || '',
    worker_id: user.worker_id || null,
    factory_id: user.factory_id || null,
    site_id: user.site_id || null,
    report_type: _type,
    description: document.getElementById('descInput').value.trim(),
    urgency: _urgency,
    location_lat: _location.lat,
    location_lng: _location.lng,
    location_text: _location.text,
    photo_urls: photo_urls,
    submitted_at: new Date().toISOString(),
  };

  let saved = false;
  let reportNumber = null;
  try {
    const res = await TAI.apiFetch('/safety-reports', {
      method: 'POST',
      body: JSON.stringify(body),
    });
    if (res.ok) {
      const j = await res.json();
      reportNumber = j.report_number;
      saved = true;
    } else {
      throw new Error('server ' + res.status);
    }
  } catch (e) {
    TAI.queuePush('report', body);
    reportNumber = 'OFFLINE-' + Date.now().toString().slice(-6);
  }

  // 활동 로그 + done 화면 (기존 로직 유지)
  ...
  document.getElementById('reportNum').textContent = t('report_number_prefix') + reportNumber;
  if (!saved) {
    document.getElementById('doneMsgEl').innerHTML =
      '⚠ 네트워크 오류로 기기에 저장됐습니다.<br>네트워크 복구 시 자동 재전송됩니다.';
  }
}

window.addEventListener('DOMContentLoaded', () => {
  TAI.queueFlush('report', '/safety-reports');
});
```

---

### P0-3. inspect.html 사진 업로드 분리

**파일**: `tadmin/full-version/app/inspect.html`

```js
// Before: items에 photo_count만 전송
// After: 사진 업로드 → items[].photo_urls 포함

async function submitCheck(){
  const user = TAI.getUser();
  if (!user) { alert('로그인 필요'); return; }

  const btn = document.getElementById('submitBtn');
  btn.disabled = true; btn.textContent = t('saving');

  // 각 item의 Base64 사진을 업로드 → URL로 변환
  const items = [];
  for (const it of _items) {
    const r = _results[it.id] || {};
    const photo_urls = [];
    for (let i = 0; i < (r.photos||[]).length; i++) {
      try {
        const file = TAI.dataUrlToFile(r.photos[i], `${it.id}_${i+1}.jpg`);
        const up = await TAI.uploadPhoto(file, 'inspection', {
          factory_id: user.factory_id,
        });
        photo_urls.push(up.url);
      } catch (e) { /* 사진 실패해도 계속 */ }
    }
    items.push({
      name: it.name,
      result: r.val || 'ok',
      memo: r.memo || '',
      photo_urls,
    });
  }

  const body = {
    phone: user.phone || '',
    worker_id: user.worker_id || null,
    factory_id: user.factory_id || null,
    schedule_id: _scheduleId || null,
    inspection_type: isCon ? 'BEFORE_WORK_CON' : 'BEFORE_WORK',
    items,
    submitted_at: new Date().toISOString(),
  };
  _lastBody = body;

  let saved = false;
  try {
    const res = await TAI.apiFetch('/worker-check/submit', {
      method:'POST', body: JSON.stringify(body),
    });
    if (res.ok) saved = true;
  } catch (e) {}

  if (!saved) {
    TAI.queuePush('check', body);
    document.getElementById('retryBar').style.display = '';
  }

  // 활동 로그, done 화면 (기존 유지)
  ...
}

// 페이지 로드 시 pending 큐 플러시
async function init(){
  ...
  await TAI.queueFlush('check', '/worker-check/submit');
  // 기존 tai_check_pending_* 키도 함께 플러시 (호환)
  Object.keys(localStorage).filter(k=>k.startsWith('tai_check_pending_')).forEach(async key=>{
    try {
      const body = JSON.parse(localStorage.getItem(key)||'null');
      if (!body) return;
      const res = await TAI.apiFetch('/worker-check/submit', {
        method:'POST', body: JSON.stringify(body),
      });
      if (res.ok) localStorage.removeItem(key);
    } catch(e){}
  });
}
```

---

### 적용: tbm.html, corrective.html, work_request.html 등

동일 패턴으로 `TAI.apiFetch`로 교체. 핵심은:
- `fetch(API+path, ...)` → `TAI.apiFetch(path, ...)` 일괄 치환
- 실패 시 `queuePush` + 사용자 알림

---

## PART C · i18n 통합 (P1-4)

**작업**: 7개 페이지의 `*_EXT` 객체를 `i18n.js` 본체로 이관.

**대상 파일**:
- `emergency.html` → `EM_EXT` 제거, i18n.js에 통합
- `report.html` → `REPORT_EXT` 제거
- `qr_scan.html` → `QR_EXT` 제거
- `history.html` → `HIST_EXT` 제거
- `profile.html` → `PROFILE_EXT` 제거
- `notifications.html` → `NOTIF_EXT` 제거
- `install.html` → `INST_EXT` 제거

**방법**: 각 페이지에서 EXT 객체 전부 copy → `i18n.js`의 각 언어 블록에 병합. EXT 선언 코드 + `Object.keys(...).forEach(...)` 병합 코드 제거.

**주의**: i18n.js가 86KB → ~100KB로 증가 예상. Service Layer 규칙은 백엔드 전용이므로 프론트 JS는 적용 대상 아님. 단, 100KB 넘으면 언어별 파일 분할 권장 (본 작업에선 통합까지만).

---

## 체크리스트

### PART A (즉시)
- [ ] `_utils.js` 신설 + 모든 HTML에서 import
- [ ] `firebase-messaging-sw.js` URL 수정
- [ ] `notifications.html` 데모 제거
- [ ] `history.html` 데모 제거
- [ ] `camera.html` 삭제
- [ ] `test.txt` 삭제
- [ ] `sw.js` precache 확대 + 버전 bump
- [ ] `i18n.js` navigator.language 감지
- [ ] `index.html`, `profile.html` 로그아웃 정리

### PART B (백엔드 배포 후)
- [ ] `emergency.html` 실패 처리 통합 + 서버 report_number
- [ ] `report.html` 사진 분리 업로드
- [ ] `inspect.html` 사진 분리 업로드 + photo_urls
- [ ] `construction_inspect.html` 동일 패턴
- [ ] `tbm.html` Authorization 적용
- [ ] `corrective.html` Authorization
- [ ] `work_request.html` Authorization

### PART C (P1)
- [ ] 7개 페이지의 *_EXT → i18n.js 통합
- [ ] 통합 후 각 페이지 동작 확인 (언어 전환 정상)

### 최종 QA
- [ ] 375px 모바일 뷰 레이아웃 정상
- [ ] 오프라인 모드 → 재연결 시 자동 재전송 확인
- [ ] 5개 언어(ko/en/zh/vi/ne) 화면 전환 확인
- [ ] PWA 홈 추가 → 재시작 시 정상 로드
- [ ] 콘솔 에러 0건

---

## 배포 순서

1. PART A 먼저 커밋 (백엔드 독립)
2. 백엔드 배포 완료 통보 받기
3. PART B 커밋
4. PART C 커밋 (별도 PR 또는 분리 커밋)
5. 프로덕션 `safe.taieng.co.kr/app/` 실 기기 테스트
6. 심태왕에게 최종 확인 요청

---

**작성**: Claude (기획창)  
**실행**: Cursor (프론트창)  
**검증**: 심태왕
