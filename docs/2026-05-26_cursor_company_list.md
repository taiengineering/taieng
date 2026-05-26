# Cursor 작업지시: my-company.html 전면 재구성

> 대상: tai-admin `tadmin/.../my-company.html` + `site/...` 동기화
> 참조 레이아웃: `factory-list.html` (목록 + 사이드패널 패턴)

---

## 핵심 요구사항

1. **여러 회사를 등록하여 관리** — 단일 회사 수정 페이지가 아님
2. **등록**: 새 회사 추가 가능
3. **리스트**: 등록된 회사 목록 표시
4. **수정**: 행 클릭 → 수정 폼
5. **필수 필드**: 회사 전화번호, 팩스번호, 주소, 이메일

---

## 페이지 구조 (factory-list.html 패턴 따라가기)

### 헤더
```html
<div class="d-flex align-items-center justify-content-between mb-4">
  <div>
    <h4 class="mb-0"><i class="ti tabler-building me-2 text-primary"></i>회사정보</h4>
    <small class="text-body-secondary">등록된 회사 목록 조회·추가·수정</small>
  </div>
  <button class="btn btn-primary" onclick="openAddPanel()">
    <i class="ti tabler-plus me-1"></i>회사 등록
  </button>
</div>
```

### 목록 테이블 (card)
| No. | 회사명 | 사업자번호 | 대표자 | 연락처 | 등록일 | 상태 |

API: `GET /companies?page=1&size=20`

### 사이드패널 (factory-list.html의 tai-side-panel 그대로)
- 등록 모드: 빈 폼
- 상세 모드: 읽기 전용
- 수정 모드: 수정 가능

---

## 폼 필드

| 필드 | ID | 필수 | 비고 |
|--------|------|------|------|
| 회사명 | mc-name | ✅ | |
| 사업자번호 | mc-biz | ✅ | 000-00-00000 포맷 |
| 대표자명 | mc-rep | ✅ | |
| 사업자 유형 | mc-biz-type | | 법인/개인 |
| 업태 | mc-sector | | 사업자등록증 상 |
| 업종명 | mc-category | | 사업자등록증 상 |
| 회사 전화번호 | mc-phone | ✅ | **필수** |
| 팩스 | mc-fax | ✅ | **필수** |
| 회사 이메일 | mc-email | ✅ | **필수** |
| 주소 | mc-road + mc-detail | ✅ | **필수** — 주소검색 버튼 |

### KSIC 없음 — 회사정보에서는 삭제

---

## API

| 메서드 | 엔드포인트 | 용도 |
|--------|------------|------|
| GET | /companies?page=1&size=20 | 목록 조회 |
| GET | /companies/{id} | 상세 조회 |
| POST | /companies | 신규 등록 |
| PATCH | /companies/{id} | 수정 |
| DELETE | /companies/{id} | 삭제 |

---

## 테마

`factory-list.html`과 동일한 CSS + 레이아웃:
- `.tai-factory-banner` 배너 (회사정보 요약)
- `.stat-pill` 통계 (등록 회사 수, 사업장 수 등)
- 테이블 + 페이지네이션
- 사이드패널 (tai-side-panel)

---

## 주의사항

1. 기존 단일 회사 로직 제거 — 목록 기반으로 전면 재구성
2. 사업자등록증 사본 업로드 기능 유지 (회사별)
3. 주소검색 모달 유지
4. 온보딩 배너 유지 (?onboarding=true)
5. 필수 필드 미입력 시 저장 차단 + 경고 표시
6. tadmin/ 수정 후 site/ 동기화
