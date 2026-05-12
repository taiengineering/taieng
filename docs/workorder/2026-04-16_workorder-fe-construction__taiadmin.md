# 건설 모듈 프론트엔드 작업지시서

**작성일:** 2026-04-16  
**참조:** tai-api/docs/workorder-fe-construction-20260416.md (상세)  
**리포:** taiengineering/tai-admin (main 브랜치)  
**경로:** `tadmin/full-version/html/horizontal-menu-template/`

---

## 작업 목록 (우선순위순)

### FE-1: construction-inspection-anchor.html — 빈 화면 가이드
- inspection_sets 0건일 때 "법령진단 실행하기" 버튼 + 안내 메시지 표시
- runDiagnosis() 함수: POST /construction/sites/{siteId}/diagnose 호출
- BE-1 미배포 상태에서도 가이드 메시지는 정상 표시

### FE-3: construction-site-list.html — 등록 폼 신규 필드
- 업종 선택 (종합/전문 + system_codes 동적 로드)
- 공사종류, 발주처유형, 발주처명
- 지상/지하 층수, 연면적(㎡), 공사금액(억원)
- 저장 시 새 필드 데이터 API에 전달

### FE-2: construction-process-list.html — KCSC 마스터 검색
- 공정 추가 모달에 KCSC 검색 필드 추가
- GET /construction/kcsc/processes?search=검색어 호출
- 선택 시 공정명+kcsc_process_id 자동 입력

## 의존관계
```
FE-3, FE-2 → BE 의존 없음, 바로 작업 가능
FE-1 → UI는 바로, API 연결은 BE-1 배포 후
```

## UI 표준
- 모든 리스트 첫 번째 컬럼: 전체선택 체크박스
- 두 번째 컬럼: 행번호 (No.)
