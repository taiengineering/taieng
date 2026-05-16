# Cursor 작업지시서 018: Notification Center Navigation Promotion

작성일: 2026-05-17
대상: tai-admin 레포
우선순위: P1

---

## 배경

Notification Center가 보조 Surface(헤더 벨 전용)에서 Primary Navigation Surface로 승격.
menu-tadmin.js 사이드바 연결은 완료. 남은 작업: Badge Slot + Popup Read + 모바일 최적화.

---

## 절대 규칙

1. **tai-api 레포 수정 금지** — Runtime 코드 변경 없음
2. **Queue Admin / Retry / DLQ / Incident UI 금지**
3. **Bootstrap body 테마 클래스** — `home-2`~`home-6` 적용 금지
4. **`tai-brand.css` 명시적 링크 확인**

---

## TASK 1 — Sidebar Badge Slot (menu-tadmin.js)

### 대상 파일
```
tadmin/full-version/assets/js/tai/menu-tadmin.js
```

### 작업

`renderMenuItem()` 함수에서 `id === 'notification-center'` 항목에 badge slot 추가.

### 수정 위치

`renderMenuItem` 함수 내부, `def.href && !def.sub` 분기에서:

```javascript
// 기존
var badge = def.badge ? '...' : '';

// 변경
var badge = def.badge ? '...' : '';
var sidebarBadge = def.id === 'notification-center'
  ? ' <span class="notif-sidebar-badge badge bg-danger rounded-pill ms-auto" style="display:none;font-size:0.6rem;"></span>'
  : '';
```

그리고 반환하는 HTML에 `sidebarBadge` 추가:
```javascript
return '<li ...><a ...>' +
  '<i class="menu-icon ..."></i>' +
  '<div>' + def.label + badge + sidebarBadge + '</div></a></li>';
```

### 주의
- slot만 준비. 실시간 연동은 optional.
- `display:none` 기본. JS에서 count > 0일 때만 표시.

---

## TASK 2 — Popup Read 처리 (notification.js)

### 대상 파일
```
tadmin/full-version/assets/js/tai/notification.js
site/full-version/assets/js/tai/notification.js
```

### 현재 상태

Popup item이 `<a href="notification-center.html">` 직접 이동. read API 호출 없음.

### 수정 내용

`renderList()` 함수에서 각 알림 item에 `data-id` 속성 추가:

```javascript
'<a href="#" data-notif-id="' + (it.notification_id || it.id || '') + '" style="...">'
```

Popup 내부에 이벤트 리스너 추가 (쯔 `createPopup()` 하단 또는 `renderList` 후):

```javascript
popup.addEventListener('click', async function(e) {
  var link = e.target.closest('[data-notif-id]');
  if (!link) return;
  e.preventDefault();
  var nid = link.getAttribute('data-notif-id');
  if (nid) {
    // best-effort read
    try {
      await apiFetch('/notification-inbox/' + nid + '/read', { method: 'POST' });
    } catch(err) { /* ignore */ }
    updateBadge();
  }
  window.location.href = 'notification-center.html';
});
```

### 주의
- read 실패 시도 이동은 계속 진행 (best-effort)
- tadmin과 site 두 파일 동일 수정

---

## TASK 3 — 모바일 Notification Center 최적화

### 대상 파일
```
site/full-version/html/vertical-menu-template-no-customizer/notification-center.html
```

### 현재 상태

Cursor가 생성한 7KB standalone 페이지. 기본 기능은 있으나 모바일 최적화 부족.

### 수정 사항

1. **Health Widget Compact Mode**
   - 5개 카드 → 1행 수평 스크롤 또는 2x3 그리드
   - 카드 높이 축소 (padding 8px)

2. **Feed Card 모바일 레이아웃**
   - 본문 2줄 말줄임: `-webkit-line-clamp: 2`
   - trace_id 숨김 (터치 시 타임라인 진입)
   - 최소 터치 타겟: `min-height: 48px`

3. **Timeline Modal 모바일**
   - `modal-dialog-scrollable` + `modal-fullscreen-sm-down`
   - 소형 화면에서 전체 높이

4. **extractCount() 버그 수정**
   - `loadUnread()`에서 `d.data`를 직접 표시하는 코드가 있으면:
   ```javascript
   function extractCount(raw) {
     if (raw == null) return 0;
     if (typeof raw === 'number') return raw;
     if (typeof raw === 'object') return raw.count ?? raw.unread_count ?? 0;
     return 0;
   }
   ```
   으로 교체

5. **REFRESH_MS 변경**
   - 60000 → 30000 (30초)

---

## TASK 4 — tadmin notification-center.html extractCount 버그 수정

### 대상 파일
```
tadmin/full-version/html/horizontal-menu-template/notification-center.html
```

### 수정

`loadUnread()` 함수에서 `d.data`를 직접 표시하는 코드 찾기:
```javascript
// 이런 패턴이 있으면:
var cnt = d.data != null ? d.data : (d.count || 0);
// 또는
var c = d.data;
```

`extractCount()` 헬퍼로 교체:
```javascript
function extractCount(raw) {
  if (raw == null) return 0;
  if (typeof raw === 'number') return raw;
  if (typeof raw === 'object') return raw.count ?? raw.unread_count ?? 0;
  return 0;
}
// 사용:
var c = extractCount(d.data);
```

---

## TASK 5 — notification.js Badge extractCount 버그 수정

### 대상 파일
```
tadmin/full-version/assets/js/tai/notification.js
site/full-version/assets/js/tai/notification.js
```

### 수정

`updateBadge()` 함수 내부:
```javascript
// 기존
cnt = d.data != null ? d.data : (d.count || 0);

// 변경
function extractCount(raw) {
  if (raw == null) return 0;
  if (typeof raw === 'number') return raw;
  if (typeof raw === 'object') return raw.count ?? raw.unread_count ?? 0;
  return 0;
}
cnt = extractCount(d.data);
```

---

## 확인 방법

1. **Sidebar** → 알림센터 클릭 → 페이지 이동 + `.notif-sidebar-badge` span 존재
2. **헤더 벨** → 팝업 → 알림 클릭 → **read API 호출 후** 알림센터 이동 (브라우저 Network 탭에서 POST confirm)
3. **모바일** → notification-center.html → Health compact + Feed 2줄 말줄임 + Timeline 전체화면
4. **[object Object]** 버그 없음 (tadmin + site 모두)
5. **Badge** → 30초 갱신 + 숫자 표시 (객체 아님)

---

## 성공 기준

| # | 기준 | 대상 |
|---|---|---|
| 1 | Sidebar `.notif-sidebar-badge` slot 존재 | menu-tadmin.js |
| 2 | Popup click → POST read → 이동 | notification.js (tadmin+site) |
| 3 | 모바일 Health compact mode | site center |
| 4 | 모바일 Feed 2줄 말줄임 | site center |
| 5 | Timeline 모바일 fullscreen | site center |
| 6 | extractCount 버그 수정 | 전체 4파일 |
| 7 | 30초 badge refresh | notification.js |
| 8 | 기존 페이지 영향 없음 | 전체 |
