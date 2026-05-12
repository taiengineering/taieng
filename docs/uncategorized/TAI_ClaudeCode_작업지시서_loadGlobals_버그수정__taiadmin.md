# Claude Code 작업지시서 — loadGlobals 버그 전체 수정

## 참조
- MASTER_CONTEXT: https://github.com/taiengineering/tai-admin/blob/main/docs/TAI_MASTER_CONTEXT.md
- 작업 레포: `taiengineering/tai-admin` (main 브랜치)
- 배포: Cloudflare Pages 자동배포

---

## 버그 설명

### 증상
페이지 진입 시 테이블이 "로딩 중..." 상태에서 영구 고착. 데이터가 절대 로드되지 않음.

### 근본 원인

```javascript
// ❌ 기존 패턴 (버그)
(async function init(){
  await loadGlobals(['category1', 'category2']); // API 실패 시 예외 발생
  loadList(); // ← 위에서 예외나면 이 줄 실행 안 됨 → 화면 고착
})();
```

`loadGlobals()` 내부에서 `/system-codes/multi` API 호출 실패 시
예외가 전파되어 `loadList()`가 실행되지 않는다.
결과적으로 화면이 스피너 상태로 영구 고착된다.

### globals.js 응답 구조 (중요)
```javascript
// apiCall 응답 구조
{ status: 'success', data: { company_type: [...], contract_status: [...] } }
// 따라서 data.data.category 로 접근해야 함
```

---

## 수정 방법

### 패턴 A — loadGlobals 사용 페이지 (표준 수정)

```javascript
// ✅ 수정 패턴
(async function init(){
  closePanel(); // 있는 경우
  try {
    await loadGlobals(['category1', 'category2']);
  } catch(e) {
    console.warn('[페이지명] globals load failed:', e.message);
  }
  // globals 성공/실패 무관하게 항상 실행
  fillSelect(document.getElementById('filter-xxx'), 'category1');
  fillSelect(document.getElementById('filter-yyy'), 'category2');
  loadList();
})();
```

### 패턴 B — loadGlobals 없이 직접 apiCall 사용 페이지

```javascript
// ✅ 직접 호출 패턴
(async function init(){
  closePanel();
  try {
    const res = await apiCall('GET',
      '/system-codes/multi?categories=' + encodeURIComponent('cat1,cat2'));
    if (res && res.data) {
      G['cat1'] = res.data['cat1'] || [];
      G['cat2'] = res.data['cat2'] || [];
    }
  } catch(e) {
    console.warn('[페이지명] globals load failed:', e.message);
  }
  fillSelect(document.getElementById('filter-cat1'), 'cat1');
  loadList();
})();
```

---

## 수정 대상 파일 목록

아래 파일들에서 `loadGlobals` + `loadList()` 패턴을 찾아 모두 수정하라.

### admin (우선순위 높음)
```
admin/full-version/html/horizontal-menu-template/factory-list.html
admin/full-version/html/horizontal-menu-template/member-list.html
admin/full-version/html/horizontal-menu-template/contract-list.html
admin/full-version/html/horizontal-menu-template/quote-list.html
admin/full-version/html/horizontal-menu-template/inquiry-list.html
admin/full-version/html/horizontal-menu-template/inspection-list.html
admin/full-version/html/horizontal-menu-template/equipment-list.html
admin/full-version/html/horizontal-menu-template/facility-equipment.html
admin/full-version/html/horizontal-menu-template/facility-process.html
admin/full-version/html/horizontal-menu-template/education-list.html
admin/full-version/html/horizontal-menu-template/education-setting.html
admin/full-version/html/horizontal-menu-template/notification-setting.html
admin/full-version/html/horizontal-menu-template/personnel-list.html
admin/full-version/html/horizontal-menu-template/repair-list.html
admin/full-version/html/horizontal-menu-template/system-codes.html
admin/full-version/html/horizontal-menu-template/engine-equipment.html
admin/full-version/html/horizontal-menu-template/engine-model.html
```

### tadmin
```
tadmin/full-version/html/horizontal-menu-template/factory-list.html
tadmin/full-version/html/horizontal-menu-template/education-list.html
tadmin/full-version/html/horizontal-menu-template/education-setting.html
tadmin/full-version/html/horizontal-menu-template/notification-list.html
tadmin/full-version/html/horizontal-menu-template/my-contract.html
tadmin/full-version/html/horizontal-menu-template/my-diagnosis.html
tadmin/full-version/html/horizontal-menu-template/my-equipment.html
tadmin/full-version/html/horizontal-menu-template/my-inspection.html
tadmin/full-version/html/horizontal-menu-template/process-select.html
```

---

## 작업 절차

1. 각 파일을 열어 `init()` 함수 또는 즉시실행함수 패턴을 찾는다
2. `loadGlobals` 또는 `apiCall('/system-codes')` 호출이 있으면 try-catch로 감싼다
3. `loadList()` (또는 유사 초기 로드 함수)가 try 바깥에서 반드시 실행되도록 수정
4. `loadList()` 내부에서도 `data.data` null 체크 후 그냥 `return` 하는 패턴을
   → 빈 배열로 처리하도록 수정:

```javascript
// ❌ 기존
if (!data || !data.data) return;
const items = data.data.items || [];

// ✅ 수정
const items = (data && data.data && data.data.items) || [];
const total = (data && data.data && data.data.total) || 0;
// return 제거 → 빈 목록 처리 계속 진행
```

---

## 추가 수정 — loadList 내 에러 표시 개선

빈 tbody에 에러 메시지가 보이지 않는 경우:
```javascript
// tbody에 colspan이 맞는지 확인 후 수정
tbody.innerHTML = '<tr><td colspan="N" class="text-center py-4 text-danger">' +
  esc(err.message || '데이터 로드에 실패했습니다.') + '</td></tr>';
```

---

## 수정하지 말 것

- 탑메뉴 구조 (절대 변경 금지)
- active 클래스
- 인증 로직 (access_token 체크)
- API 엔드포인트 URL
- 기존 기능 (정렬, 필터, 슬라이드 패널, 페이지네이션)

---

## 커밋 및 배포

```
레포: taiengineering/tai-admin
브랜치: main
커밋 메시지: fix(globals): loadGlobals 에러 시 loadList 미호출 버그 전체 수정
```

GitHub push 후 Cloudflare Pages 자동배포 확인.

---

## 검증 방법

각 수정 파일에서:
1. 브라우저 개발자도구 네트워크 탭에서 `/system-codes/multi` 실패 시뮬레이션
2. 테이블이 "데이터가 없습니다" 또는 에러 메시지로 전환되는지 확인
3. `/system-codes/multi` 정상 응답 시 기존과 동일하게 동작하는지 확인
