# Notification Engine Frontend Integration — 세션 로그

작성일: 2026-05-17
범위: tai-admin 레포 (admin + tadmin + site)

---

## 작업 요약

Notification Engine Phase 1 Frontend 통합 — Cursor TASK 1~4 실행 + admin 알림센터 메뉴/페이지 추가 + 버그 수정

---

## tai-admin 커밋 체인 (이번 세션, 최신순)

| SHA | 작성자 | 내용 |
|---|---|---|
| `e576444b` | Claude | notification-center.html → Vuexy admin 레이아웃 (탑바+메뉴+푸터) |
| `66011c87` | Claude | [object Object] 버그 — extractCount() 헬퍼로 unread-count 응답 파싱 |
| `93f7c36c` | Claude | admin notification-center.html 생성 (시스템 > 알림센터) |
| `9cc2fc7a` | Claude | admin menu-nav.js 시스템 children에 알림센터 추가 |
| `17b4bda9` | Cursor | tadmin+site 알림센터 네비 통합 + notification.js v2 API 연동 (TASK 1~4) |
| `b247d1de` | Claude | notification.js v2.0 — API 연동 + 60s badge refresh (TASK 017) |
| `efa5e44e` | Claude | notification-list.html → notification-center.html redirect (TASK 017) |
| `16e955c3` | Claude | Notification Center page — Feed/Timeline/Settings/Health (TASK 016) |

---

## Cursor TASK 1~4 (작업지시서: `taieng/docs/2026-05-17_cursor-notification-nav-integration.md`)

| TASK | 내용 | 상태 |
|---|---|---|
| 1 | `tadmin/menu-tadmin.js` 사이드바 알림센터 (tabler-bell, Lv≥1) | ✅ `17b4bda9` |
| 2 | `tadmin/nav-tadmin.js` 드롭다운 「전체 알림 보기」 → center 링크 | ✅ `17b4bda9` |
| 3 | site vertical/horizontal center·list·menu 복제 | ✅ `17b4bda9` |
| 4 | site notification.js v2.0 API 동기화 | ✅ `17b4bda9` |

---

## admin.taieng.co.kr 추가 작업 (Cursor 범위 밖)

### 발견: admin ≠ tadmin

admin.taieng.co.kr은 `admin/` 디렉토리 사용 (menu-nav.js), tadmin은 `tadmin/` 디렉토리 사용 (menu-tadmin.js + nav-tadmin.js). Cursor 작업지시서는 tadmin/site만 대상이었고, admin은 별도 처리 필요.

### 작업 내역

1. **`admin/full-version/assets/js/tai/menu-nav.js`** — 시스템 children에 `{ label: '알림센터', href: 'notification-center.html', status: 'done' }` 추가
2. **`admin/full-version/html/horizontal-menu-template/notification-center.html`** — Vuexy admin 레이아웃으로 생성
   - Vuexy core.css + demo.css
   - menu-nav.js 탑바 + 수평 메뉴
   - footer-nav.js 푸터
   - Bootstrap Modal (타임라인)
   - Vuexy form-switch (설정 토글)

---

## 이슈 및 버그 수정

### ISSUE-1: `[object Object]` 표시 버그

**증상**: 알림센터 Health 위젯 「읽지 않음」 카드에 `[object Object]` 표시

**원인**: `/notification-inbox/unread-count` API가 `{status: "success", data: {count: N}}` 객체를 반환하는데, `loadUnread()` 함수가 `d.data`를 숫자로 가정하고 직접 표시

```javascript
// 버그 코드
const c = d.data != null ? d.data : (d.count || 0);
// d.data = {count: 0} → [object Object]
```

**수정**: `extractCount()` 헬퍼 추가

```javascript
function extractCount(raw) {
  if (raw == null) return 0;
  if (typeof raw === 'number') return raw;
  if (typeof raw === 'object') return raw.count ?? raw.unread_count ?? 0;
  return 0;
}
const c = extractCount(d.data);  // → 0
```

**영향 범위**: admin notification-center.html 수정 완료. tadmin notification-center.html도 동일 버그 있음 (PENDING).

---

### ISSUE-2: admin 탑바 메뉴 스크롤 한계

**증상**: admin.taieng.co.kr 탑바 `>` 스크롤 화살표 클릭 시 한 글자씩만 이동하여 끝쪽 메뉴(엔진설정, 알림센터 등)에 접근 불가

**원인**: Vuexy horizontal-menu-template의 메뉴 스크롤 step이 작음 + 메뉴 항목 11개로 화면 초과

**해결**: 알림센터를 독립 탑레벨이 아닌 **시스템 하위 메뉴**로 배치하여 접근성 확보

---

### ISSUE-3: standalone 페이지 UI 불일치

**증상**: 최초 생성된 notification-center.html이 standalone (자체 파란색 top-bar + Bootstrap CDN)이어서 admin 페이지와 UI 불일치

**해결**: Vuexy admin 레이아웃으로 전면 재작성 — menu-nav.js 탑바 + 수평 메뉴 + footer-nav.js 푸터 + Vuexy card/tab/modal 컴포넌트

---

## 디렉토리 구조 확인 (학습)

| 도메인 | 디렉토리 | 메뉴 JS | 용도 |
|---|---|---|---|
| admin.taieng.co.kr | `admin/` | menu-nav.js | 슈퍼어드민 |
| safe.taieng.co.kr (데스크톱) | `tadmin/` | menu-tadmin.js + nav-tadmin.js | SaaS 사용자 |
| safe.taieng.co.kr (모바일) | `site/` | menu-tadmin.js | 작업자 PWA |

---

## PENDING

1. **tadmin notification-center.html** — `[object Object]` 버그 동일 존재 (extractCount 미적용)
2. **tadmin notification-center.html** — Vuexy SaaS 레이아웃으로 재작성 필요 (현재 standalone)
3. **admin 벨 아이콘** — admin/ 경로에 notification.js 미연동 (탑바 벨 아이콘 팝업 없음)
4. **site notification-center.html** — standalone 상태, 모바일 최적화 필요

---

## 관련 문서

- `taieng/docs/2026-05-17_cursor-notification-nav-integration.md` — Cursor 작업지시서 v3
- Notification Engine Phase 1 전체 세션 로그: 이전 세션 참조
