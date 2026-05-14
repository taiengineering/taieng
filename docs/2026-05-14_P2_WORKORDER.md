# P2 작업지시서 — 오픈 후 개선 4건 (2026-05-14)

> 실행 도구: Cursor (모든 파일 200+ lines)
> 역할: Product/SaaS/Runtime Ops Architect
> 엔진 아키텍처 변경 금지

---

## 1. WORKER-03: 작업자 홈 대시보드 UI 개선

### 대상 파일
- `site/full-version/html/vertical-menu-template-no-customizer/worker-home.html` (21KB)
- `tadmin/full-version/html/horizontal-menu-template/worker-home.html` (22KB)

### 현재 상태
기본 구조 완성: 헤더(인사/사업장) → 날씨위젯 → 요약카드(3칸: 오늘할일/긴급/완료) → 할일목록 → 탭바(홈/점검/TBM/알림) → 이상신고 바텀시트

### API (이미 배포됨)
- `GET /workers/home/{worker_id}` → `{ worker, today_tasks[], today_count, overdue_count }`
- `GET /work-assignments?assigned_user_id=&factory_id=&due_date=` → 할일 목록
- `GET /weather/now?lat=&lon=` → 날씨 + 작업중지
- `GET /notifications?user_id=&is_read=false` → 미읽음 알림

### 개선 사항

#### A. 요약카드 → 진행률 추가
현재 3칸 (오늘할일 / 긴급 / 완료) → 4칸으로 변경:
```
[ 오늘 할일: N건 ] [ 미완료: N건 (빨강) ] [ 완료: N건 ] [ 진행률: N% (원형) ]
```
- 진행률 = `(done / total) * 100`, CSS-only 원형 프로그레스 (conic-gradient)
- 모바일 2x2 그리드, 데스크탑 4x1

#### B. 빠른 액션 섹션 (요약카드 아래)
```html
<div class="quick-actions">
  <a href="worker-check.html">📋 점검 시작</a>
  <a href="tbm-list.html">👥 TBM 참여</a>
</div>
```
- 2컬럼, min-height 56px, 터치 최적화

#### C. 미완료(Overdue) 경고 배너
`overdue_count > 0`일 때 할일목록 위에 표시:
```
⚠️ 미완료 N건 — 기한이 지난 점검이 있습니다 [바로가기→]
```
- 배경 `#fef2f2`, 텍스트 `#dc2626`
- 클릭 시 overdue 필터 적용

#### D. 작업자 식별 개선
현재: `localStorage`의 `user_id`로 work-assignments 호출
개선: 작업자가 `worker_registry`에 등록된 경우 `worker_id`도 localStorage에 저장하고, `/workers/home/{worker_id}` API도 병렬 호출하여 정확한 factory 매핑

### 금지사항
- 기존 CSS 변수/색상 체계 유지 (slate 계열)
- 하단 탭바 구조 변경 금지
- API 신규 생성 금지 (기존 API만 사용)

---

## 2. ADM-03: 리스트 페이지 컨벤션 (전체선택 + 순번)

### 규칙
모든 리스트 페이지의 `<thead>` + `<tbody>`:
1. **1열**: 전체선택 체크박스 `<input type="checkbox" id="checkAll">`
2. **2열**: 순번 (No.) — `(page - 1) * pageSize + rowIndex + 1`
3. 나머지 열: 기존 유지

### 대상 파일 (tadmin/full-version/html/horizontal-menu-template/)

| 파일 | 크기 | 비고 |
|------|------|------|
| alert-list.html | 27KB | |
| construction-inspection-list.html | 43KB | |
| construction-process-list.html | 27KB | |
| construction-site-list.html | 37KB | |
| construction-work-list.html | 33KB | |
| construction-worker-list.html | 32KB | |
| education-list.html | 27KB | |
| factory-list.html | 56KB | |
| kmong-list.html | 28KB | |
| my-diagnosis.html | 25KB | |
| my-equipment.html | 38KB | |
| my-inspection.html | 29KB | |
| overdue-list.html | 24KB | |
| risk-assessment-list.html | 11KB | |
| safety-meeting-list.html | 11KB | |
| tbm-list.html | 13KB | |
| work-schedule-list.html | 28KB | |
| worker-list.html | 35KB | |

**총 18개 파일**

### 구현 패턴

#### thead 변경
```html
<!-- Before -->
<thead><tr><th>이름</th><th>상태</th>...</tr></thead>

<!-- After -->
<thead><tr>
  <th style="width:40px;"><input type="checkbox" id="checkAll" onclick="toggleAll(this)"></th>
  <th style="width:50px;">No.</th>
  <th>이름</th><th>상태</th>...
</tr></thead>
```

#### tbody 행 렌더링
```javascript
// 각 행 앞에 추가
'<td><input type="checkbox" class="row-check" value="' + id + '"></td>' +
'<td>' + ((page - 1) * pageSize + idx + 1) + '</td>' +
```

#### 공통 JS (이미 있으면 확인 후 통합)
```javascript
function toggleAll(master) {
  document.querySelectorAll('.row-check').forEach(function(cb) {
    cb.checked = master.checked;
  });
}
function getCheckedIds() {
  return Array.from(document.querySelectorAll('.row-check:checked')).map(function(cb) {
    return cb.value;
  });
}
```

### 주의사항
- `notification-list.html` (923B, 거의 빈 파일) — 스킵
- 각 파일의 기존 renderTable/renderRow 함수 찾아서 해당 패턴 삽입
- `colspan` 사용하는 empty state 행은 colspan +2

---

## 3. DOC-03: 서식 작성/미리보기/다운로드 프론트 UI

### 개요
안전관리자가 문서 서식을 선택 → 사업장 정보 자동 채움 → 미리보기 → PDF 다운로드하는 UI.

### 신규 파일
`tadmin/full-version/html/horizontal-menu-template/document-forms.html`

### API (이미 배포됨)
- `GET /documents/templates` → 서식 목록 (현재 10종 MVP)
- `GET /documents/templates/{template_id}` → 서식 상세 + 필드 정의
- `POST /documents/generate` → `{ template_id, factory_id, field_values }` → PDF URL 반환
- `GET /factories/{factory_id}` → 사업장 정보 (자동 채움용)

### 페이지 구조

```
┌─────────────────────────────────────────┐
│ 서식 선택 (카드 그리드 또는 리스트)          │
│ [안전관리계획서] [점검표] [교육일지] ...     │
├─────────────────────────────────────────┤
│ 서식 작성 폼 (동적 필드)                   │
│ - 사업장 정보: 자동 채움 (readonly)         │
│ - 추가 입력 필드: template 정의에 따라      │
│ [미리보기]  [PDF 다운로드]                  │
├─────────────────────────────────────────┤
│ 미리보기 영역 (iframe 또는 모달)            │
└─────────────────────────────────────────┘
```

### UI 플로우
1. 페이지 진입 → `GET /documents/templates` → 카드 그리드 렌더
2. 카드 클릭 → `GET /documents/templates/{id}` → 폼 필드 동적 생성
3. 사업장 정보 자동 채움: `GET /factories/{selectedFactoryId}`
4. 미리보기 클릭 → `POST /documents/generate` (preview: true) → iframe에 PDF 표시
5. 다운로드 클릭 → `POST /documents/generate` (preview: false) → `window.open(pdf_url)`

### 디자인 가이드
- 기존 tadmin 레이아웃 (수평 메뉴 + content-wrapper) 사용
- 카드: 아이콘 + 서식명 + 설명 + "작성" 버튼
- 폼: Bootstrap form-control, form-label 통일
- 미리보기: 모달 (`#previewModal`) + `<iframe>` PDF 표시
- 사이드 메뉴에 "문서 > 서식 작성" 항목 추가 필요

### 금지사항
- xhtml2pdf 직접 호출 금지 (백엔드 API만 사용)
- 서식 필드 하드코딩 금지 (API 응답 기반 동적 렌더)

---

## 4. SAAS-04: TBM 플로우 검증

### 대상 파일
- `tadmin/.../tbm-setting.html` (47KB) — 안전관리자: TBM 세팅
- `tadmin/.../tbm-list.html` (13KB) — TBM 목록
- `site/.../worker-home.html` → 탭바 "TBM" 링크

### 검증 항목 체크리스트

Cursor에서 각 파일을 열고 아래 항목을 확인 후, 문제 있으면 수정:

#### A. tbm-setting.html
- [ ] API 엔드포인트 URL 확인: `POST /tbm/create`, `GET /tbm/list`
- [ ] factory_id 기반 TBM 생성 (localStorage에서 selectedFactoryId 사용)
- [ ] 참석자 선택: worker_registry 기반 체크박스
- [ ] 날짜/시간 입력 → `scheduled_at` 필드
- [ ] 위험요인 입력 → `risk_factors` 배열
- [ ] 안전대책 입력 → `safety_measures` 배열
- [ ] 저장 후 tbm-list.html로 이동

#### B. tbm-list.html
- [ ] `GET /tbm/list?factory_id=` 호출 확인
- [ ] 상태 표시: PLANNED / IN_PROGRESS / COMPLETED
- [ ] 클릭 → 상세 패널 또는 모달
- [ ] ADM-03 컨벤션 적용 (전체선택 + 순번)

#### C. 작업자 TBM 참여 플로우
- [ ] worker-home.html 탭바 "TBM" → tbm-list.html 링크 정상
- [ ] 작업자가 TBM에 참석 확인 (서명/체크) 할 수 있는 UI 존재 여부
- [ ] 없으면: `tbm-attend.html` 신규 생성 필요 (바텀시트 확인 → PATCH /tbm/{id}/attend)

#### D. API 존재 확인
```
GET  /tbm/list?factory_id=
GET  /tbm/{id}
POST /tbm/create
PATCH /tbm/{id}
PATCH /tbm/{id}/attend  (작업자 참석)
```
→ 없는 API가 있으면 이 문서에 기록하고 Claude 기획창에 보고

### 수정 원칙
- 기존 코드 구조 유지하며 버그/누락만 수정
- API가 없으면 코드 수정하지 말고 보고만
- TBM 세팅 로직 변경 금지 (기존 플로우 검증만)

---

## Cursor 실행 순서

1. **WORKER-03** → site + tadmin worker-home.html 개선
2. **ADM-03** → 18개 리스트 페이지 일괄 적용
3. **DOC-03** → document-forms.html 신규 생성
4. **SAAS-04** → TBM 3개 파일 검증 + 수정

각 작업 완료 후 커밋 메시지:
```
feat(WORKER-03): worker home dashboard UI improvement
feat(ADM-03): add select-all checkbox + sequential No. to all list pages
feat(DOC-03): document forms create/preview/download UI
fix(SAAS-04): TBM flow verification and fixes
```

---

## CF DNS 전환 가이드 (대표님 수동)

Cloudflare Dashboard → taieng.co.kr → DNS:

1. 기존 `taieng.co.kr` CNAME/A 레코드 삭제 또는 수정
2. `taieng.co.kr` → `new.taieng.co.kr` 와 동일한 Cloudflare Pages 프로젝트로 지정
3. Pages > Custom domains에서 `taieng.co.kr` 추가
4. SSL/TLS → Full (strict) 확인
5. `new.taieng.co.kr` → `taieng.co.kr` 301 리다이렉트 추가 (Page Rules 또는 _redirects)

**주의:** KG이니시스 도메인 승인이 `new.taieng.co.kr`로 되어 있으면, 이니시스 관리자에서 `taieng.co.kr`로 변경 필요.
