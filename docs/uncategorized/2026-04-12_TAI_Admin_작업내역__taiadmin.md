# TAI Admin 프론트엔드 작업 내역
**작업일**: 2026-04-12  
**레포**: `taiengineering/tai-admin`  
**경로**: `admin/full-version/html/horizontal-menu-template/`  
**배포**: Cloudflare Pages (git push → 자동)

---

## ✅ 완료된 작업

### STEP 1 — `expert-list.html` 신규 생성
**커밋**: `ba0feccf` → 재작성 `b5ea466`

#### 구현 내용
- **페이지 제목**: 전문가회원 통합 관리
- **탭**: 전체 / 선임 / 컨설팅 / 수선 (`expert_type` 파라미터 전환)
- **필터**: 사업자구분 / 승인상태 / 활성여부 / 키워드 검색
- **테이블 헤더**: No. | 전문가명(회사명) | 유형 | 사업자구분 | 전문분야 | 활동지역 | 승인상태 | 활성여부
- **슬라이드 패널**: 행 클릭 → 상세 정보 3섹션(기본/전문/관리) + 활성/비활성 토글 버튼
- **API**: `GET /experts/admin/expert-list`
- **토글 API**: `PATCH /experts/admin/expert/{source_table}/{id}/toggle?is_active={bool}`
- **메뉴 active**: 매칭관리 > 전문가회원

#### 스펙 준수 항목
| 항목 | 내용 |
|------|------|
| alert() | 전면 금지 → `showToast()` 사용 |
| 코드값 | 하드코딩 금지 → `loadGlobals()` + `codeLabel()` |
| loadGlobals | `entity_type`, `expert_type`, `expert_work_type`, `expert_status` |
| closePanel() | DOMContentLoaded 최상단 호출 |
| CSS `.detail-row` | `justify-content:space-between`, `font-size:.875rem` |
| CSS `.detail-label` | `flex-shrink:0`, 좌측 고정 |
| CSS `.detail-value` | `text-align:right`, `word-break:break-all` |
| CSS `.sec-title` | `margin:18px 0 6px; padding:0 16px` |
| salary 필드 | `salary_min ~ salary_max` 표시 |
| scripts 하단 | `notification.js`, `mail-check.js` 순서 준수 |

---

### STEP 2 — `consulting-list.html` 신규 생성
**커밋**: `3454153`

#### 구현 내용
- **기반**: `personnel-list.html` 구조 적용
- **페이지 제목**: 컨설팅연결
- **탭1**: 컨설팅 연결 현황 (`GET /consulting/requests`)
- **탭2**: 컨설팅 전문가 목록 (`GET /experts/admin/expert-list?expert_type=CONSULTING`)
- **통계 카드 4개**: 전체 요청 / 매칭완료 / 계약성사 / 수수료 수입
- **필터**: 사업자구분 / 승인상태 / 활성상태 / 키워드
- **슬라이드 패널**: 전문가 상세 + 활성/비활성 토글
- **메뉴 active**: 매칭관리 > 컨설팅연결
- **`expert_type=CONSULTING` 고정**: `getQueryT2()` 내부에서 항상 세팅

---

### STEP 3 — `personnel-list.html` 메뉴 업데이트
**커밋**: `a90731f`

- 기존 `업체연결 > 선임연결 active` 구조 → `매칭관리 > 선임연결관리 active` 로 교체
- 기존 `utils.js` 스크립트 누락 → 추가

---

### STEP 4 — 메뉴 전체 교체 (Cursor 작업 지시 전달)
**상태**: Claude에서 Cursor로 작업 프롬프트 전달 완료

#### Cursor 찾아바꾸기 대상 (약 28개 파일)
| 구분 | 내용 |
|------|------|
| 대상 경로 | `admin/full-version/html/horizontal-menu-template/*.html` |
| 방법 | `Ctrl+Shift+H` 폴더 전체 찾아바꾸기 |
| 찾기 | `<li class="menu-item"><a ... tabler-users-group ... 업체연결 ... 선임연결 ... 진단연결 ... 수선연결 ...` |
| 바꾸기 | `매칭관리` 블록(전문가회원/선임연결관리/컨설팅연결/수선연결) + `업체연결` 블록(진단연결) 분리 |

#### Active 파일 개별 수정 필요
| 파일 | Active 항목 | 처리 방법 |
|------|-------------|-----------|
| `expert-list.html` | 매칭관리 > 전문가회원 | ✅ Claude 처리 완료 |
| `personnel-list.html` | 매칭관리 > 선임연결관리 | ✅ Claude 처리 완료 |
| `consulting-list.html` | 매칭관리 > 컨설팅연결 | ✅ Claude 처리 완료 |
| `repair-list.html` | 매칭관리 > 수선연결 | ⚠️ Cursor 수동 확인 필요 |
| `diagnosis-step1.html` | 업체연결 > 진단연결 | ⚠️ Cursor 수동 확인 필요 |

---

## 📋 커밋 이력

| 커밋 SHA | 내용 |
|----------|------|
| `ba0feccf` | feat: 전문가회원 통합 관리 페이지 생성 (expert-list.html) |
| `3454153` | feat: 컨설팅연결 관리 페이지 생성 (consulting-list.html) |
| `a90731f` | feat: personnel-list 메뉴 → 매칭관리 > 선임연결관리 active |
| `b5ea466` | feat: expert-list.html 스펙 기반 재작성 (패널 상세/토글/CSS 완성) |

---

## 🔧 신규 파일 API 연동 현황

### `expert-list.html`
```
GET  /experts/admin/expert-list
     ?expert_type=EXPERT|CONSULTING|REPAIR
     &entity_type=...
     &verified_status=...
     &is_active=true|false
     &keyword=...
     &page=1&size=20

PATCH /experts/admin/expert/{source_table}/{id}/toggle?is_active={bool}
```

### `consulting-list.html`
```
GET  /consulting/stats
GET  /consulting/requests?page=1&size=20&expert_type=CONSULTING
PATCH /consulting/requests/{id}  body: { status: 'MATCHED' }

GET  /experts/admin/expert-list?expert_type=CONSULTING&...  (탭2 전문가 목록)
PATCH /experts/admin/expert/{source_table}/{id}/toggle?is_active={bool}
```

---

## ⚠️ 이슈 및 주의사항

### 1. `expert-list.html` SHA 불일치 오류 (해결됨)
- **원인**: 이전 세션 컨텍스트의 SHA가 만료되어 push 실패
- **해결**: `get_file_contents`로 현재 SHA 재조회 후 업데이트 성공

### 2. `expert-list.html` 메뉴에 불필요 항목 발견
- **발견**: Cursor가 `matching-list.html`, `settlement-list.html` 항목을 임의로 추가한 것으로 추정
- **해결**: Claude가 표준 4개 항목(전문가회원/선임연결관리/컨설팅연결/수선연결)으로 재정비

### 3. `consulting/stats` 엔드포인트 미확인
- **이슈**: `/consulting/stats` API가 백엔드에 구현되어 있는지 미확인
- **권고**: 엔드포인트가 없을 경우 404 에러 시 통계 카드 `-` 처리로 graceful fallback 구현되어 있음
- **확인 필요**: 백엔드 담당자와 엔드포인트 존재 여부 확인

### 4. STEP 4 대량 파일 메뉴 교체 미완료
- **이슈**: 총 28개 파일을 Claude API로 일괄 처리하기에는 컨텍스트 한계 도달
- **권고**: Cursor `Ctrl+Shift+H` 전체 찾아바꾸기로 처리 후 `git push`
- **이후 확인**: `repair-list.html`, `diagnosis-step1.html` active 클래스 수동 검토

### 5. `consulting-list.html` 탭2 행 클릭 함수 참조 이슈
- **이슈**: `openDetail(idx, rows+idx)` 형태의 잘못된 인수 참조가 일부 포함될 수 있음
- **해결**: `openExpertDetail(rows[Number(tr.dataset.idx)])` 방식으로 이벤트 리스너에서 처리

---

## 📂 파일 현황 요약

| 파일 | 상태 | 비고 |
|------|------|------|
| `expert-list.html` | ✅ 완료 | 신규 생성 + 스펙 재작성 |
| `consulting-list.html` | ✅ 완료 | 신규 생성 |
| `personnel-list.html` | ✅ 완료 | 메뉴 업데이트 |
| `repair-list.html` | ⚠️ 미완료 | Cursor 메뉴 교체 + active 수동 확인 필요 |
| `diagnosis-step1.html` | ⚠️ 미완료 | Cursor 메뉴 교체 + active 수동 확인 필요 |
| 나머지 ~26개 파일 | ⚠️ 미완료 | Cursor 전체 찾아바꾸기 필요 |

---

## 🚀 남은 작업 (Cursor)

```
1. Ctrl+Shift+H → 폴더 전체 찾아바꾸기
   경로: admin/full-version/html/horizontal-menu-template/

2. repair-list.html active 확인:
   매칭관리 active + 수선연결 active

3. diagnosis-step1.html active 수정:
   매칭관리는 non-active, 업체연결 active + 진단연결 active

4. git push origin main
```
