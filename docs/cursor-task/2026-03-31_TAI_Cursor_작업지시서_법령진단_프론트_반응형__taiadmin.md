# TAI Cursor 작업지시서 — 법령진단 프론트 반응형

> 작성일: 2026-03-31  
> 레포: tai-admin (tadmin)  
> 대상: 법령진단 1단계 · 법령진단 내역 화면

---

## 목표

- 모바일·태블릿(768px 이하)에서 레이아웃이 깨지지 않고 조작 가능할 것  
- 터치 영역 확보, 가로 스크롤 테이블은 관성 스크롤(`-webkit-overflow-scrolling`) 지원  
- Vuexy/Bootstrap 5 유틸 위주로 보강 (기존 레이아웃 클래스 무분별 삭제 금지)

---

## 적용 파일

| 파일 | 내용 |
|------|------|
| `tadmin/full-version/html/horizontal-menu-template/diagnosis-step1.html` | 상단 액션 줄바꿈, 섹터 카드 패딩·타이틀, 진단 버튼 전폭(모바일), 룰 테이블 폰트 |
| `tadmin/full-version/html/horizontal-menu-template/my-diagnosis.html` | 헤더·필터·테이블·히어로 배너 반응형 |

---

## 브레이크포인트 기준

- **767.98px 이하**: 세로 스택, 히어로·테이블 패딩 축소, 테이블 글자 크기 소폭 축소  
- **575.98px 이하**: 섹터 카드 이모지·타이틀 크기 조정  

---

## 완료 체크리스트

- [x] `diagnosis-step1.html` — 헤더 `flex-column` / 시설 목록 `w-100 w-sm-auto`  
- [x] 섹터 카드 `min-height`, `p-3 p-md-4`, 영문 코드 라벨은 `sm` 이상만 표시  
- [x] `1단계 진단하기` — `w-100 w-md-auto`  
- [x] 룰 테이블 — `table-responsive` + `tai-diagnosis-rules-table`  
- [x] `my-diagnosis.html` — 새 진단 신청 버튼·필터 그리드·테이블 터치 스크롤  

---

## 참고

- 동일 페이지가 `admin/` / `site/`에 복사본이 있으면 배포 정책에 맞게 동기화 필요.  
