# Cursor 작업지시서 — 모든 목록 페이지 전체선택 체크박스 + 순번(No.) 추가

## 참조
- MASTER_CONTEXT: https://github.com/taiengineering/tai-admin/blob/main/docs/TAI_MASTER_CONTEXT.md
- 작업일: 2026-03-28
- 커밋: `refactor(table): 모든 목록 페이지 전체선택 체크박스 + 순번 컬럼 추가`

---

## 작업 목적
모든 리스트 페이지의 테이블에 두 가지를 통일 적용한다.
1. **첫 번째 컬럼**: 전체선택 체크박스 (`<th>` 에 체크박스, `<td>` 에 개별 체크박스)
2. **두 번째 컬럼**: 순번 No. (현재 페이지 기준 `(page-1)*pageSize + index + 1`)

이 두 가지는 **앞으로 만들어질 신규 페이지 포함 TAI 전체 리스트 페이지 필수 요소**다.

---

## 대상 파일 목록

### admin (22개)
```
admin/full-version/html/horizontal-menu-template/member-list.html
admin/full-version/html/horizontal-menu-template/company-list.html
admin/full-version/html/horizontal-menu-template/factory-list.html
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
admin/full-version/html/horizontal-menu-template/permission.html
admin/full-version/html/horizontal-menu-template/system-codes.html
admin/full-version/html/horizontal-menu-template/engine-equipment.html
admin/full-version/html/horizontal-menu-template/engine-model.html
admin/full-version/html/horizontal-menu-template/report-v1.html
admin/full-version/html/horizontal-menu-template/report_v1.html
admin/full-version/html/horizontal-menu-template/report-v1-viewer.html
```

### tadmin (12개)
```
tadmin/full-version/html/horizontal-menu-template/factory-list.html
tadmin/full-version/html/horizontal-menu-template/education-list.html
tadmin/full-version/html/horizontal-menu-template/education-setting.html
tadmin/full-version/html/horizontal-menu-template/notification-list.html
tadmin/full-version/html/horizontal-menu-template/my-contract.html
tadmin/full-version/html/horizontal-menu-template/my-diagnosis.html
tadmin/full-version/html/horizontal-menu-template/my-equipment.html
tadmin/full-version/html/horizontal-menu-template/my-inspection.html
tadmin/full-version/html/horizontal-menu-template/manager-permission.html
tadmin/full-version/html/horizontal-menu-template/contact.html
tadmin/full-version/html/horizontal-menu-template/process-select.html
```

> 제외: auth-*.html, index.html, maps-leaflet.html, tai_survey_v5.html (목록 테이블 없는 페이지)

---

## 적용 규칙

### 1. thead 수정

**기존 첫 번째 `<th>` 앞에 2개 컬럼 추가:**
```html
<!-- 전체선택 체크박스 -->
<th style="width:36px;" class="ps-3">
  <input type="checkbox" class="form-check-input" id="chkAll" onchange="toggleAll(this)">
</th>
<!-- 순번 -->
<th style="width:48px;">No.</th>
<!-- 기존 컬럼들 유지 -->
```

### 2. tbody 렌더링 수정

**각 `<tr>` 렌더링 JS에서 앞에 2개 td 추가:**
```javascript
// 순번 계산 (변수명은 페이지마다 다를 수 있음 — currentPage, page 등 확인 후 적용)
var rowNo = (currentPage - 1) * pageSize + index + 1;

'<tr>' +
'<td class="ps-3"><input type="checkbox" class="form-check-input row-chk" value="' + escapeHtml(item.id || '') + '"></td>' +
'<td class="text-body-secondary">' + rowNo + '</td>' +
// 기존 td들 유지...
'</tr>'
```

### 3. toggleAll 함수 추가 (없는 경우에만)

```javascript
function toggleAll(chk) {
  document.querySelectorAll('.row-chk').forEach(function(c) { c.checked = chk.checked; });
}
```

> 이미 toggleAll이 있는 파일은 기존 함수 유지, 클래스명만 `.row-chk`로 통일

### 4. engine-equipment.html 주의사항
- 탭1 설비 마스터: 이미 전체선택 존재 (`.eq-chk`) → 순번만 추가
- 탭2 모델 마스터: 전체선택 + 순번 모두 추가

### 5. 탭 구조 페이지 주의사항 (education-list, notification-setting 등)
- 탭 내부 테이블 각각에 동일 규칙 적용
- 탭마다 chkAll id 충돌 방지: `id="chkAll-tab1"`, `id="chkAll-tab2"` 형태로 탭별 구분
- toggleAll도 탭별로 구분: `toggleAll(chk, '.row-chk-tab1')`

### 6. colspan 수정
- 데이터 없음 메시지 `<td colspan="N">` → N에 +2 적용
- 로딩 스피너 `<td colspan="N">` → N에 +2 적용

---

## 스타일 (추가 CSS 불필요)
- 체크박스: Bootstrap `form-check-input` 클래스 그대로
- 순번: `text-body-secondary` 클래스 (회색 작은 느낌)
- 체크박스 컬럼 너비: `style="width:36px;"`
- 순번 컬럼 너비: `style="width:48px;"`

---

## 완료 조건
1. 모든 대상 파일의 테이블에 전체선택 체크박스(1번째 컬럼) + 순번(2번째 컬럼) 적용
2. 순번은 페이지네이션 연동 — 2페이지 1번째 행이 `pageSize+1`번으로 표시
3. 전체선택 체크박스 클릭 시 해당 테이블 모든 행 체크/해제
4. 기존 기능(정렬, 슬라이드 패널, 필터, 페이지네이션) 정상 동작 유지
5. GitHub push: `taiengineering/tai-admin` main
6. 커밋 메시지: `refactor(table): 모든 목록 페이지 전체선택 체크박스 + 순번 컬럼 추가`

---

## 신규 페이지 제작 시 필수 적용 규칙 (영구 규정)

> TAI 모든 리스트 페이지는 아래 두 가지를 반드시 포함해야 한다.

| 순서 | 컬럼 | 내용 |
|------|------|------|
| 1번째 | 전체선택 | `<th>` 체크박스 (toggleAll) + `<td>` 개별 체크박스 (.row-chk) |
| 2번째 | No. | `(currentPage-1)*pageSize + index + 1` 계산 순번 |
