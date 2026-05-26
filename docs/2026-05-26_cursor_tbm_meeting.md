# Cursor 작업지시: TBM 템플릿 수정 + 안전회의 CRUD

> 대상: `tai-admin` (main 직접 커밋)
> 3건 작업: TBM create 수정, TBM sign 수정, 안전회의 등록/수정

---

## 작업 1: tbm-create.html 어드민 템플릿 적용

> 파일: `tadmin/.../tbm-create.html` (29KB)
> 목표: vertical-menu → horizontal-menu 변환

변경:
1. vertical-menu aside 제거 → tadmin 표준 horizontal navbar+aside
2. 하단에 globals.js, menu-tadmin.js, nav-tadmin.js 추가 + buildMenu() 호출
3. 비즈니스 로직(JS) 변경 없음
4. favicon 경로 수정
5. data-template="horizontal-menu-template"

참고: worker-list.html 레이아웃 그대로 따라가면 됨

---

## 작업 2: tbm-sign.html 어드민 템플릿 적용

> 파일: `tadmin/.../tbm-sign.html` (11KB)
> 목표: 독립형 → horizontal-menu 래퍼 추가

변경:
1. tadmin horizontal-menu 레이아웃으로 감싸기
2. 서명 캔버스 + JS 기능 변경 없음
3. auth-guard.js 제외 (URL 파라미터로 공개 접근)

---

## 작업 3: safety-meeting-list.html 등록/수정 기능

> 파일: `tadmin/.../safety-meeting-list.html` (11KB)
> 목표: 목록만 있는 상태 → 등록+수정 모달 추가

### DB: safety_committee_meetings
- meeting_type: 회의유형 (산업안전보건위원회/안전보건협의체/정기안전회의/기타)
- meeting_title, meeting_date, meeting_place, duration_min
- chair_name, attendee_count, attendees_json [{name, role, department}]
- agenda_items [{title, description, decision}]
- discussion_text (웹에디터 HTML)
- resolution_text (웹에디터 HTML)
- files_json [{name, url, size}]
- status_code: DRAFT / COMPLETED

### 구현 요구
- 등록/수정 모달 (modal-lg)
- Quill.js 웹에디터 (CDN)
- 파일첨부 (POST /file-upload 또는 Supabase Storage)
- 참석자/안건 동적 추가/삭제
- SweetAlert 삭제 확인

### 법적 필수 항목
개최일시/장소, 출석위원, 심의·의결사항, 토의사항, 보존 3년
