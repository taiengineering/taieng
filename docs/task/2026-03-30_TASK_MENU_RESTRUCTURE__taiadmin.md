# 전역 메뉴 재구성 작업 지시서
## 날짜: 2026-03-30
## 대상: `admin/full-version/html/horizontal-menu-template/*.html`

원격에 병합 초안 문서가 있었으나, **실제 반영본은 `scripts/apply_menu_restructure.py`와 동일**하다.

---

## 목표

기존 **회원관리 / 계약관리 / 시설관리 / 위험관리 / …** 평면 구조를  
**산업안전 / 건설안전 / 업체연결** 중심으로 재편한다.

- **산업안전**: 공정·시설·지도·설비·선임·점검·모델 (기존 시설관리 블록)
- **건설안전**: 현황·위험·TBM·교육·법령진단 (기존 위험관리 + TBM + 교육 + diagnosis)
- **업체연결**: 회원·계약·견적·문의·수선·정산·세부설정 (기존 회원/계약/수선/설정 일부)

**문서관리**, **엔진설정**은 상위 메뉴로 유지.

---

## 표준 `<ul class="menu-inner">`

구현은 **`scripts/apply_menu_restructure.py`** 의 `MENU_SPEC` / `render_menu_inner()` 를 기준으로 한다.

---

## 파일별 active 매핑

| 파일명 | active 처리 |
|--------|-------------|
| index.html | 대시보드 `li.menu-item` |
| facility-process.html | 산업안전 상위 + 공정관리 |
| factory-list.html | 산업안전 + 시설관리(서브) |
| maps-leaflet.html | 산업안전 + 시설지도 |
| equipment-list.html | 산업안전 + 설비관리 |
| facility-equipment.html | 산업안전 + 설비관리 |
| personnel-list.html | 산업안전 + 선임연결 |
| inspection-list.html | 산업안전 + 점검관리 |
| report_v1.html, report-v1.html | 건설안전 + 현황리포트 |
| diagnosis-step1.html | 건설안전 + 법령진단 |
| education-list.html | 건설안전 + 교육관리 |
| education-setting.html | 건설안전 + 교육설정 |
| member-list.html | 업체연결 + 회원관리 (협력사와 동일 href 시 회원관리 우선) |
| permission.html | 업체연결 + 권한관리 |
| notification-setting.html | 업체연결 + 알림설정 |
| company-list.html | 업체연결 + 회사관리 |
| contract-list.html | 업체연결 + 계약관리 |
| quote-list.html | 업체연결 + 견적관리 |
| inquiry-list.html | 업체연결 + 문의관리 |
| repair-list.html | 업체연결 + 수선관리 |
| quote-setting.html | 업체연결 + 견적설정 |
| repair-setting.html | 업체연결 + 수선설정 |
| doc-setting.html | 업체연결 + 문서설정 |
| repair-settle.html | 업체연결 + 정산관리 |
| system-codes.html | 엔진설정 + 전역변수 |
| engine-equipment.html | 엔진설정 + 설비 |
| engine-model.html | 엔진설정 + 모델 |
| engine-legal.html | 엔진설정 + 법규 |
| cron-list.html | 엔진설정 + 크론관리 |

**스킵:** `auth-*.html`, `report-v1-viewer.html`  
**참고:** `report_v1.html`, `report-v1.html`은 본 템플릿에 `menu-inner`가 없어 메뉴 교체 대상에서 제외(리포트 전용 화면).

**자동 적용 스크립트:** `scripts/apply_menu_restructure.py`

---

## 완료 기준

- [x] 모든 대상 HTML의 `menu-inner`가 표준 HTML과 동일 구조
- [x] 파일별 `active` 적용
- [x] 커밋 메시지: `feat: 전체 메뉴 재구성 — 산업안전/건설안전/업체연결 구조 변경`
