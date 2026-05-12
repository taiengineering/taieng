# FN-03: 법령진단 입력 폼 UX 전면 개편

**우선순위**: P1  | **의존**: BE-05 완료 후

## 배경
체크박스 35개 연속, 자유텍스트 남용, "모름" 선택 불가, 건축물대장 자동채움 부재.
기획창 확정 UX 5원칙 준수.

## UX 5원칙
1. boolean → 3지선다 (예/아니오/모름)
2. 자유텍스트 → 배열·테이블 UI
3. 체크박스 연속 15개↑ 금지 → 그룹 접기
4. 자동채움 우선 (주소→대장, 사업자번호→공공데이터)
5. UNKNOWN 값은 결제 후 보완 동선 제공

## 할 일
- [ ] 공통 컴포넌트 6종 (`assets/js/diagnosis-inputs/`)
  - TriStateToggle / ProcessTable / SubcontractorTable
  - MultiSelectGroup / AutofillAddress / AutofillBiz
- [ ] BUILDING 입력화면 개편 (소방·위험물·수질환경·다중이용·특수시설 그룹접힘)
- [ ] CONSTRUCTION 입력화면 개편 (ProcessTable + SubcontractorTable + operation_shift 라디오)
- [ ] INDUSTRY PAID1/2/3 개편 (operation_shift 필수, process_worker_data → table)
- [ ] "모름" 값 결제 후 보완 페이지 `/diagnosis/fill-gaps`

## 디자인 토큰
- Vuexy + Bootstrap 5
- TriStateToggle: btn-group (예=primary, 아니오=secondary, 모름=outline-warning)
- 자동채움: 녹색 뱃지

## 산출물
- `pages/diagnosis/input-building.html`
- `pages/diagnosis/input-construction.html`
- `pages/diagnosis/input-industry-paid{1,2,3}.html`
- `assets/js/diagnosis-inputs/*.js`
- `pages/diagnosis/fill-gaps.html`

## 완료 조건
- 체크박스 연속 15개↑ 화면 0개
- 자유텍스트 필드 0개 (주소·회사명 제외)
- 모바일 375px 입력 완주

## 금기
- 카카오 지도/로그인/알림 API 금지
- main 직접 커밋 금지

## 실행 프롬프트
```
FN-03 실행. docs/workorder-fn03-input-ux.md. BE-05 완료 확인 후.
공통 컴포넌트 6종을 먼저 만들고 sector별 화면 조립. 기존 Vuexy 템플릿 최대 활용.
```
