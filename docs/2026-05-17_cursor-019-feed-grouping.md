# Cursor 작업지시서 019: Feed Grouping + Readability 고도화

작성일: 2026-05-17
대상: tai-admin 레포 (tadmin + site)
우선순위: P2

---

## 배경

Notification Center Feed의 가독성 향상. Frontend grouping only — Backend 변경 금지.

---

## TASK 1 — Feed Date Grouping (날짜 그룹핑)

### 대상 파일
```
tadmin/full-version/html/horizontal-menu-template/notification-center.html
site/full-version/html/vertical-menu-template-no-customizer/notification-center.html
admin/full-version/html/horizontal-menu-template/notification-center.html
```

### 작업

`renderFeed()` 함수에 `groupBy === 'date'` 옵션 추가:

```javascript
// groupBy select에 추가
<option value="date">날짜별</option>
```

그룹핑 로직:
```javascript
function dateGroup(isoStr) {
  var d = new Date(isoStr);
  var now = new Date();
  var today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  var yesterday = new Date(today - 86400000);
  var weekAgo = new Date(today - 7 * 86400000);
  if (d >= today) return '오늘';
  if (d >= yesterday) return '어제';
  if (d >= weekAgo) return '이번 주';
  return '이전';
}
```

---

## TASK 2 — Feed Readability 개선

### 대상

전체 notification-center.html (3개 파일)

### 수정

1. **본문 2줄 제한** (ellipsis)
```css
.nc-feed-item .body {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
```

2. **QUIET_HOUR_DELAYED badge** — Feed 카드에 `지연` badge 표시
```javascript
// feedCard 함수 내부
var delayBadge = (i.queue_status === 'QUIET_HOUR_DELAYED')
  ? '<span class="nc-ch" style="background:#fef3c7;color:#d97706;">🌙 지연</span>'
  : '';
```

3. **RESUMED badge** — 지연 후 전달된 알림
```javascript
var resumedBadge = (i.queue_status === 'QUIET_HOUR_RESUMED')
  ? '<span class="nc-ch" style="background:#d1fae5;color:#065f46;">✅ 재개</span>'
  : '';
```

---

## TASK 3 — 모바일 Feed Readability 동기화

### 대상
```
site/full-version/html/vertical-menu-template-no-customizer/notification-center.html
```

### 확인

018에서 적용된 compact health + 2줄 말줄임 + fullscreen timeline이 정상 동작하는지 확인.
TASK 1, 2의 date grouping + delayed/resumed badge도 동일 적용.

---

## 절대 규칙

1. **tai-api 레포 수정 금지**
2. **Backend aggregation 금지** — Frontend grouping only
3. **Queue Admin / Retry / DLQ UI 금지**

---

## 성공 기준

| # | 기준 |
|---|---|
| 1 | groupBy 셀렉트에 '날짜별' 옵션 존재 |
| 2 | 오늘/어제/이번주/이전 그룹 헤더 표시 |
| 3 | 본문 2줄 ellipsis |
| 4 | QUIET_HOUR_DELAYED 피드에 지연 badge |
| 5 | 모바일 동일 적용 |
