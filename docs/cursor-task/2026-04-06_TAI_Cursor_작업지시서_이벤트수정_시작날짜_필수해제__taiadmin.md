# 커서 작업지시서 — 이벤트 수정 모달 시작날짜 필수 해제

**작성일:** 2026-04-06  
**대상 저장소:** tai-admin  
**배경:** 이벤트는 시작날짜 없이 진행될 수 있으나 (상시 이벤트 등), 수정 모달에 필수로 설정되어 있음

---

## 작업 내용

이벤트 관리 페이지의 **수정(Edit) 모달**에서 `start_date` 필드 필수 해제

---

## 수정 상세

### 1. HTML 수정

이벤트 관리 HTML 파일에서 수정 모달 안 시작날짜 input 검색:

```html
<!-- 찾을 코드 -->
<input type="date" id="editStartDate" ... required>

<!-- 바꾸었 코드 -->
<input type="date" id="editStartDate" ...>
```

**라벨 수정 (필수 표시 * 제거):**
```html
<!-- 전 -->
<label for="editStartDate">시작 날짜 <span class="text-danger">*</span></label>

<!-- 후 -->
<label for="editStartDate">시작 날짜</label>
```

### 2. JS 수정

저장/수정 버튼 클릭 시 start_date 유효성 검사 로직이 있다면 제거 또는 선택 처리로 변경:

```javascript
// 제거 대상 패턴:
if (!startDate || startDate === '') {
    alert('시작 날짜를 입력하세요');
    return;
}
// 또는:
if (!document.getElementById('editStartDate').value) { ... }
```

---

## 파일 검색 방법

이벤트 관리 페이지를 다음 키워드로 검색:
- `event` + `start_date` + `required`
- `이벤트` + `editStartDate`
- 파일명 패턴: `event-management`, `event-list`, `events` 등

---

## 커밋 메시지
```
fix: 이벤트 수정 모달 시작날짜 필수 → 선택으로 변경
```
