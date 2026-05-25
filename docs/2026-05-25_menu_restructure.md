# SaaS 메뉴 구조 개편 작업지시

> 작성일: 2026-05-25
> 대상: menu-tadmin.js v6.0.0
> 원칙: 서비스하지 않는 건 숨김, 같은 건 통합

## 신규 메뉴 구조

### 공통 (모든 섹터)
```
대시보드 (index.html) ← 전용대시보드 통합
TBM관리
  - TBM관리 (tbm-list.html)
  - 안전회의 (safety-meeting-list.html)
  - TBM설정 (tbm-setting.html)
교육관리
  - 교육목록 (education-list.html)
  - 교육설정 (education-setting.html)
문서관리 ← 문서관리+문서 병합
  - 일정관리 (engine-schedule.html)
  - 문서 (engine-document.html)
  - 서식작성 (document-forms.html)
알림센터 (notification-center.html)
마이페이지
  - 내 회사 정보 (my-company.html)
  - 알림목록 (notification-list.html)
  - 계약내역 (my-contract.html)
  - 법령진단 (my-diagnosis.html)
  - 문의하기 (contact.html)
```

### 산업(INDUSTRIAL) 전용
```
시설관리
  - 시설목록 (factory-list.html)
  - 공정관리 (process-manage.html)
  - 설비관리 (my-equipment.html)
점검관리
  - 점검항목관리 (inspection-anchor.html)
  - 점검목록 (my-inspection.html)
  - 작업관리 (construction-work-list.html) ← 산업+건설 공통
  - 점검 캘린더 (inspection-calendar.html)
  - 업무일정 (work-schedule-list.html)
작업근로자
  - 작업근로자 (worker-list.html)
  - 권한설정 (manager-permission.html)
```

### 건물(FACILITY) 전용
```
시설관리
  - 시설목록 (factory-list.html)
  - 설비관리 (my-equipment.html)
점검관리
  - 점검항목관리 (inspection-anchor.html)
  - 점검목록 (my-inspection.html)
  - 작업관리 (construction-work-list.html) ← 산업+건설 공통
  - 점검 캘린더 (inspection-calendar.html)
  - 업무일정 (work-schedule-list.html)
```

### 건설(CONSTRUCTION) 전용
```
건설관리
  - 현장관리 (construction-site-list.html)
  - 공정관리 (construction-process-list.html)
  - 작업관리 (construction-work-list.html)
점검관리
  - 점검항목관리 (construction-inspection-anchor.html)
  - 점검목록 (construction-inspection-list.html)
  - 업무일정 (work-schedule-list.html)
작업근로자
  - 작업근로자 (construction-worker-list.html)
  - 하도급관리 (subcontract-management.html) ← 신규 페이지 필요
  - 권한설정 (manager-permission.html)
```

## 삭제 (메뉴에서 제거)
- 안전정보 (safety-info.html) — 홈페이지에서 서비스 중
- 전용대시보드 (safety-dashboard.html) — 대시보드에 통합

## 추후 오픈 (숨김)
- 위험성평가 (risk-assessment-list.html) — 전문성 필요
- 미이행관리 (overdue-list.html)
- QR관리 (equipment-qr-manager.html) — 전문성 필요
- 전문가 매칭 (fix-chat.html) — 모수 부족
- 운영 상황 센터/대시보드 — 내부용

## 신규 페이지 생성 필요
- subcontract-management.html (하도급관리) — 건설 전용, 필수

## 핵심 변경점
1. construction-work-list.html → 산업+건설 모두 점검관리 하위에 노출 (작업관리)
2. 문서관리 + 문서 → 하나로 병합
3. 전용대시보드 → 대시보드로 통합
4. 건설: 하도급관리 메뉴 추가 (페이지 신규 생성)

## 구현
- menu-tadmin.js v6.0.0으로 업데이트
- plan-gate.js는 v2.0.0 유지 (기능 잠금 없음)
- Cursor에서 작업 (18KB 파일)
