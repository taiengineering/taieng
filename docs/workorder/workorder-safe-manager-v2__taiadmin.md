# safe.taieng.co.kr 안전관리자 사이트 분석 및 작업 지시서 v2
> 2026-04-13 기획창 분석. v1(초기 분석) 대체.
> 대표님 확인사항 반영완료.

---

## 핵심 설계 원칙 (대표 확정)

### 1. 세 가지 유형의 상품 구조

| 유형 | 구조 | SaaS 상품 단위 |
|------|------|----------------|
| **산업** (INDUSTRY) | 시설 → 공정 → 설비 | 3단계 구조의 상품 |
| **건설** (CONSTRUCTION) | 공사장 → 공정 → 작업 | 하나의 상품 |
| **건물** (FACILITY) | 시설 | 시설 하나로 구성 |

### 2. 안전관리자가 메인 사용자
- safe.taieng.co.kr은 안전관리자가 주로 사용
- 안전관리자 시각으로 모든 화면 설계
- 각 회원의 유형(sector)에 맞춤 메뉴만 보여야 함

### 3. 작업배정 흐름
- 설비 등록 → 안전관리자가 **최초 1회 작업배정** → 할당 완료
- 자동이 아니라 안전관리자가 직접 1회 할당하는 구조

---

## 현재 메뉴 분석 (menu-tadmin.js v4.2.0)

### 현재 메뉴 14개 상위 항목
| # | 메뉴 | 하위 | 문제점 |
|---|------|------|--------|
| 1 | 전용대시보드 | - | ✓ 필요 |
| 2 | 대시보드 | - | ✓ 필요 (통합 가능) |
| 3 | 시설관리 | 10개 | ✘ sector 무관하게 모두 노출. 건물용인 임차인/에너지가 산업에도 보임 |
| 4 | 건설관리 | 7개 | ✘ sector 무관하게 노출 |
| 5 | 작업근로자 | 3개 | ✘ 하도급관리 페이지 미존재 |
| 6 | 업무관리 | 5개 | ✘ 대부분 페이지 미존재 (work-list/request/diary/setting) |
| 7 | TBM관리 | 3개 | ✘ TBM이 건설현장 ID 하드코딩 |
| 8 | 교육관리 | 3개 | ✘ 만족도조사(92KB)가 여기 있음 |
| 9 | 위험관리 | 3개 | ✘ 위험성평가가 업무관리에도 중복 |
| 10 | QR/RFID관리 | 1개 | △ 단독 메뉴 불필요 |
| 11 | 문서설정 | 5개 | ✘ 대부분 페이지 미존재 (doc-box/report/request) |
| 12 | 견적관리 | 2개 | ✘ 크몰관리가 안전관리자에게 보임 |
| 13 | 안전정보 | - | ✓ 필요 |
| 14 | 마이페이지 | 6개 | △ 정리 필요 |

### 존재하지 않는 페이지를 가리키는 메뉴 (즉시 제거 필요)
| 메뉴 항목 | href | 상태 |
|-----------|------|------|
| 하도급관리 | worker-subcontract.html | ❌ 미존재 |
| 업무관리 | work-list.html | ❌ 미존재 |
| 업무요청 | work-request.html | ❌ 미존재 |
| 업무일지 | work-diary.html | ❌ 미존재 |
| 업무설정 | work-setting.html | ❌ 미존재 |
| 시설모델 | facility-model.html | ❌ 미존재 |
| 임차인관리 | tenant-list.html | ❌ 미존재 |
| 에너지관리 | energy-list.html | ❌ 미존재 |
| 사고관리 | risk-accident.html | ❌ 미존재 |
| AI위험예측 | risk-predict.html | ❌ 미존재 |
| 문서함 | doc-box.html | ❌ 미존재 |
| 보고관리 | doc-report.html | ❌ 미존재 |
| 문서요청 | doc-request.html | ❌ 미존재 |

---

## 개선된 메뉴 구조 (sector별)

### 건물 (FACILITY) — 시설 하나
```
대시보드
시설관리           → factory-list.html
점검관리
  ├ 점검앉커관리   → inspection-anchor.html
  ├ 점검목록       → my-inspection.html
  ├ 점검캘린더    → inspection-calendar.html
  └ 업무일정       → work-schedule-list.html
TBM관리
  ├ TBM목록       → tbm-list.html
  └ TBM설정       → tbm-setting.html
교육관리
  ├ 교육목록       → education-list.html
  └ 교육설정       → education-setting.html
안전정보           → safety-info.html
문서관리
  ├ 일정관리       → engine-schedule.html
  └ 문서           → engine-document.html
마이페이지
  ├ 내 회사 정보   → my-company.html
  ├ 알림목록       → notification-list.html
  ├ 계약내역       → my-contract.html
  ├ 법령진단       → my-diagnosis.html
  └ 문의하기       → contact.html
```

### 산업 (INDUSTRY) — 시설/공정/설비
```
대시보드
시설관리
  ├ 시설목록       → factory-list.html
  ├ 공정관리       → process-manage.html
  └ 설비관리       → my-equipment.html
점검관리
  ├ 점검앉커관리   → inspection-anchor.html
  ├ 점검목록       → my-inspection.html
  ├ 점검캘린더    → inspection-calendar.html
  └ 업무일정       → work-schedule-list.html
작업근로자
  ├ 작업근로자   → worker-list.html
  └ 권한설정       → manager-permission.html
TBM관리
  ├ TBM목록       → tbm-list.html
  ├ 안전회의       → safety-meeting-list.html
  └ TBM설정       → tbm-setting.html
교육관리
  ├ 교육목록       → education-list.html
  └ 교육설정       → education-setting.html
위험관리
  └ 위험성평가     → risk-assessment-list.html
QR관리            → equipment-qr-manager.html
안전정보           → safety-info.html
문서관리
  ├ 일정관리       → engine-schedule.html
  └ 문서           → engine-document.html
마이페이지
  ├ 내 회사 정보   → my-company.html
  ├ 알림목록       → notification-list.html
  ├ 계약내역       → my-contract.html
  ├ 법령진단       → my-diagnosis.html
  └ 문의하기       → contact.html
```

### 건설 (CONSTRUCTION) — 공사장/공정/작업
```
대시보드
현장관리
  ├ 현장목록       → construction-site-list.html
  ├ 공정관리       → construction-process-list.html
  └ 작업관리       → construction-work-list.html
점검관리
  ├ 점검앉커관리   → construction-inspection-anchor.html
  ├ 점검목록       → construction-inspection-list.html
  └ 업무일정       → work-schedule-list.html
작업자관리
  ├ 작업자목록   → construction-worker-list.html
  └ 권한설정       → manager-permission.html
TBM관리
  ├ TBM목록       → tbm-list.html
  ├ 안전회의       → safety-meeting-list.html
  └ TBM설정       → tbm-setting.html
교육관리
  ├ 교육목록       → education-list.html
  └ 교육설정       → education-setting.html
위험관리
  └ 위험성평가     → risk-assessment-list.html
안전정보           → safety-info.html
문서관리
  ├ 일정관리       → engine-schedule.html
  └ 문서           → engine-document.html
마이페이지
  ├ 내 회사 정보   → my-company.html
  ├ 알림목록       → notification-list.html
  ├ 계약내역       → my-contract.html
  ├ 법령진단       → my-diagnosis.html
  └ 문의하기       → contact.html
```

---

## 제거할 것 (메뉴에서 즉시 제거)

### 1. 존재하지 않는 페이지 링크 13개 ██ CRITICAL
위 표 참고. 메뉴에서 즙거하고 해당 페이지를 만들기 전까지는 노출 금지.
work-list, work-request, work-diary, work-setting, worker-subcontract,
facility-model, tenant-list, energy-list, risk-accident, risk-predict,
doc-box, doc-report, doc-request

### 2. 안전관리자에게 불필요한 항목
| 항목 | 사유 |
|------|------|
| 크몰관리 (kmong-list.html) | 내부 운영용. 안전관리자에게 노출 불필요 |
| 만족도조사 (tai_survey_v5.html) | 교육관리 하위에서 제거. 별도 진입점 필요 |
| engine-qa.html (190 bytes) | 빈 페이지. 삭제 |
| 견적관리 메뉴 전체 | 진단구매는 마이페이지>법령진단 내에서 접근 |

### 3. 중복 제거
| 항목 | 위치 | 처리 |
|------|------|------|
| 위험성평가 | 업무관리 + 위험관리 양쪽 | 위험관리에만 남김 |
| 대시보드 | 전용대시보드 + 대시보드 2개 | 통합 1개로 |

---

## 추가할 것

### ADD-01: sector 기반 메뉴 필터링 ██ CRITICAL
**현상:** menu-tadmin.js의 visible 함수가 level만 검사하고 sector를 검사하지 않음
**해결:** visible 함수에 sector 조건 추가

```javascript
// 예시: 시설관리는 FACILITY, INDUSTRY에만
visible: function(s, lv) { 
  return (s === 'FACILITY' || s === 'INDUSTRY') && lv >= 1; 
}
// 건설관리는 CONSTRUCTION에만
visible: function(s, lv) { 
  return s === 'CONSTRUCTION' && lv >= 1; 
}
```

상세 매핑은 위의 "개선된 메뉴 구조" 섹션 참고.

### ADD-02: 대시보드 통합 및 sector별 분리 ██ HIGH
- 전용대시보드 + 대시보드 → 1개로 통합
- sector에 따라 다른 카드/통계 표시
- 건물: 시설 점검일정, 법령의무
- 산업: 공정별 점검, 설비 상태
- 건설: TBM 완료율, 작업자 출근

### ADD-03: 미배정 업무 경고 ██ HIGH
- 대시보드에 "미배정 업무 N건" 경고 카드
- 안전관리자가 최초 배정을 놓치지 않도록 안내
- 클릭 시 배정 페이지로 이동

### ADD-04: 건물 전용 기능 █ MEDIUM
- 건물은 시설 하나만 있으므로 메뉴가 가장 단순
- 공정/설비 메뉴 숨김
- 임차인관리, 에너지관리는 향후 건물 전용으로 추가

---

## 수정할 것

### FIX-01: TBM 하드코딩 ██ CRITICAL
- 현상: construction_site_id에 하드코딩되어 제조/건물에서 접근 불가
- 해결: factory_id 기반으로 동작. construction_site_id는 건설 유형일 때만

### FIX-02: 점검항목 부족 ██ HIGH
- inspection_sets 304개에 inspection_set_items 67개 (밖에 없음)
- 점검 시 체크할 항목이 없는 상태
- `/inspection-sets/generate-all-items` 실행 필요

### FIX-03: 알림 발송 ██ HIGH
- 112건 존재하나 실제 발송 0건
- SMS/카카오톡 API 연동 확인 필요

### FIX-04: 업무관리 메뉴 정리 █ MEDIUM
- 업무관리 5개 하위메뉴 중 4개가 미존재 페이지
- 페이지가 만들어지기 전까지 메뉴에서 숨김
- 건설의 "업무관리"와 혼동 방지 — 건설은 "작업관리"로 명칭

---

## 작업 우선순위

### Phase 1: 즉시 수정 (메뉴 오류)
1. **존재하지 않는 13개 페이지 링크 제거** — menu-tadmin.js에서 제거
2. **sector 기반 메뉴 필터링 구현** — visible 함수에 sector 조건 추가
3. **크몰관리/만족도조사/engine-qa 제거**
4. **중복 메뉴 정리** (위험성평가, 대시보드)

### Phase 2: 백엔드 버그
5. **TBM 하드코딩 제거**
6. **점검항목 일괄생성**
7. **알림 발송 확인**

### Phase 3: 대시보드 개선
8. **대시보드 통합 + sector별 내용 분리**
9. **미배정 업무 경고 카드**

### Phase 4: 향후
10. 건물 전용 기능 (임차인, 에너지)
11. 업무관리 페이지 생성 (work-list 등)
12. AI위험예측, 사고관리 페이지 생성

---

## 참고

### 메뉴 수정 대상 파일
- `tadmin/full-version/assets/js/tai/menu-tadmin.js` (v4.2.0, 18KB)
- SHA: `a8d88b6bfb6a97bcf5972f4433c439ebd31e6baa`

### 현재 로카스토리지 키
- `contract_sector`: FACILITY / INDUSTRY / CONSTRUCTION / FREE
- `contract_level`: 0~3
- `role_code`: 001(슴퍼어드민) / 기타

### 관련 문서
- `docs/workorder-safe-app-analysis.md` (v1 — 현장작업자 관점, 참고용)
- `docs/sitemap-taieng-co-kr.md`
- `docs/session-2026-04-12-planning.md`
