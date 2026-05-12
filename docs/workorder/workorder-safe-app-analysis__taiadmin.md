# safe.taieng.co.kr 현장 앱 분석 및 작업 지시서
> 2026-04-13 기획창 분석 결과. 프론트엔드/백엔드 창에서 이 문서 기반으로 작업 진행.

---

## 핵심 설계 원칙 (대표 확인)

### 1. 세 가지 유형은 페이지가 달라야 한다
- **건물** (building) — 오피스, 상가, 주거 시설
- **산업** (manufacturing) — 제조공장, 산업시설
- **건설** (construction) — 건설현장, 공사장

각 유형별로 보이는 메뉴, 점검항목, TBM 템플릿, 대시보드가 달라야 함.
현재 다른 유형의 페이지/데이터가 보이는 것은 **오류**.

### 2. 작업배정 흐름
- 설비 등록 → 안전관리자가 **최초 1회 작업배정** → 할당 완료
- 자동 배정이 아니라 안전관리자가 직접 1회 할당하는 구조
- 미배정 69%는 아직 안전관리자가 배정을 안 한 상태 (UX 개선으로 해결)

### 3. TAI 핵심 신념
> "작업자가 대충 체크해도 안 하는 것보다 낫다"
→ 5초 안에 체크 시작할 수 있어야 함

---

## 현재 DB 상태

| 테이블 | 건수 | 상태 |
|--------|------|------|
| companies | 11 | 정상 |
| factories | 12 | 정상 |
| users | 9 | 정상 |
| work_schedules | 268 | 전부 MANUAL (ENGINE=0) |
| work_assignments | 2,881 | 배정 892 / 미배정 1,989 |
| notifications | 112 | 발송 0건 (send_status=SUCCESS이나 실제 발송 안 됨) |
| inspection_sets | 304 | 정상 |
| inspection_set_items | 67 | 부족 (세트당 0.22개) |
| construction_sites | 0 | 미구축 |
| construction_workers | 0 | 미구축 |
| tbm_meetings | 0 | 미구축 |
| risk_assessments | 0 | 미구축 |
| worker_registry | 0 | 미구축 |

---

## PART 1: 버그/오류 수정 (프론트엔드 + 백엔드)

### BUG-01: 유형별 페이지 분리 오류 ██ CRITICAL
**현상:** 건물/산업/건설 유형과 무관하게 모든 페이지가 노출됨
**원인:** 로그인 사용자의 회사/공장 유형(sector) 기반으로 메뉴를 필터링하지 않음
**해결:**
1. 로그인 시 `factory.sector` 값을 localStorage에 저장
2. menu-tadmin.js에서 sector 값에 따라 메뉴 항목 show/hide
3. 각 페이지 JS에서 해당 sector 데이터만 호출

**메뉴 매핑:**
| 메뉴 | 건물 | 산업 | 건설 |
|------|------|------|------|
| 시설관리 | O | O | X (현장관리로 대체) |
| 공정관리 | O | O | O (건설공정) |
| 설비관리 | O | O | X |
| 점검관리 | O | O | O (건설점검) |
| TBM | O | O | O |
| 현장관리 | X | X | O |
| 작업자관리 | X | X | O |
| 작업관리 | X | X | O |
| 교육관리 | O | O | O |

### BUG-02: TBM 하드코딩 ██ HIGH
**현상:** TBM이 건설현장 ID에 하드코딩되어 있어 제조/건물 공장에서 접근 불가
**해결:** TBM 생성/조회 시 factory_id 기반으로 동작하도록 변경. construction_site_id는 건설 유형일 때만 사용.

**대상 파일:**
- 프론트: `tbm-list.html`, `tbm-setting.html`
- 백엔드: TBM 관련 라우터 (관련 API 엔드포인트 확인 필요)

### BUG-03: 알림 발송 실패 ██ HIGH
**현상:** notifications 112건 존재, send_status=SUCCESS이지만 실제 발송(SMS/카카오) 0건
**확인할 것:**
1. Railway cron이 HTTP 405 오류 중이었음 — 알림 발송 cron도 영향받았는지
2. send_status=SUCCESS인데 sent_at이 NULL이면 로직 오류
3. SMS/카카오톡 API 키 설정 확인

### BUG-04: 점검 항목 부족 ██ HIGH
**현상:** inspection_sets 304개에 inspection_set_items 67개 (세트당 평균 0.22개)
**해결:** 점검항목 일괄생성 엔드포인트 실행 (기존 `/inspection-sets/generate-all-items` 확인)

### BUG-05: engine-qa.html 빈 페이지 █ LOW
**현상:** 190 bytes. 사실상 빈 파일
**해결:** 삭제 또는 제대로 구현

---

## PART 2: 제거/숨김 (프론트엔드)

### 현장 작업자 메뉴에서 숨길 페이지

| 페이지 | 사유 | 처리 |
|--------|------|------|
| engine-document.html | 관리자 전용 | 안전관리자 권한일 때만 메뉴 표시 |
| engine-schedule.html | 관리자 전용 | 안전관리자 권한일 때만 메뉴 표시 |
| engine-qa.html | 빈 페이지 | 삭제 |
| kmong-list.html | 내부 운영용 | 메뉴에서 제거 (페이지는 유지) |
| manager-permission.html | 관리자 전용 | 안전관리자 권한일 때만 표시 |
| diagnosis-step1/2/3 | 1회성 온보딩 | "내 진단" 내부에서만 접근 |
| diagnosis-purchase.html | 1회성 구매 | "내 진단" 내부에서만 접근 |
| tai_survey_v5.html | 92KB 초대형 설문 | 온보딩 전용으로 분리 |

### 권한 기반 메뉴 노출 규칙
```
role_code = localStorage.getItem('role_code')

// 작업자 (WORKER): 홈 / 점검 / TBM / 알림 — 4개만
// 안전관리자 (MANAGER): 전체 메뉴 (유형별 필터링 적용)
// 슬퍼어드민 (001): 전체 (이건 admin.taieng.co.kr)
```

---

## PART 3: 추가 기능 (우선순위 순)

### ADD-01: 작업자 전용 간소화 뷰 ██ CRITICAL
**내용:** 작업자 로그인 시 보이는 화면을 3가지로 제한
1. **오늘의 할일** — 배정된 점검/TBM/교육 카드
2. **점검 수행** — 정상/이상/보류 버튼
3. **이상 신고** — 사진 첨부 + 간단 메모

**UI 요구사항:**
- 하단 탭바: 홈 | 점검 | TBM | 알림 (4개)
- 버튼 최소 48px 높이 (장갑 터치)
- 점검 항목 폰트 16px+

**참고 UI:** 프로젝트 파일 `tai_forklift_check_ui_html.html` (지게차 점검 UI 시안)

### ADD-02: 유형별 대시보드 분리 ██ HIGH
**내용:** 로그인 사용자의 공장 sector에 따라 다른 대시보드 표시
- **건물**: 점검일정, 설비상태, 법령의무 현황
- **산업**: 공정별 점검현황, 설비 상태, 위험도
- **건설**: 작업별 TBM완료율, 위험성평가, 작업자 출근

**현재 파일:** safety-dashboard.html (15KB — 기능 부족)

### ADD-03: QR 스쳪 → 즉시 점검 시작 ██ HIGH
**내용:** 작업자가 설비에 붙은 QR을 스쳪하면 해당 설비 점검 화면이 바로 열림
**현재:** equipment-qr-manager.html은 QR 생성 전용. 작업자용 QR 스쳪 → 점검 흐름 없음
**구현:**
- 하단탭 중앙에 QR 스쳪 버튼 (FAB 스타일)
- 스쳪 → equipment_id 추출 → 해당 설비 점검세트 로드 → 점검 시작

### ADD-04: 점검 시 사진 첨부 ██ HIGH
**내용:** 이상 선택 시 카메라 자동 실행, 사진 첨부
**구현:** `<input type="file" accept="image/*" capture="environment">` + Supabase Storage 업로드

### ADD-05: 안전관리자용 작업배정 UX 개선 █ MEDIUM
**내용:** 최초 1회 작업배정이 핸심이므로, 배정 안 된 설비/일정을 눈에 띄게 표시
- 대시보드에 "미배정 업무 N건" 경고 카드
- 작업일정 목록에서 미배정 항목 하이라이트
- 한 번에 복수 배정 가능한 UI

### ADD-06: 오프라인 모드 (PWA) █ MEDIUM
**내용:** 점검 체크 후 네트워크 복구 시 자동 동기화
**구현:** Service Worker + IndexedDB 캐싱

### ADD-07: GPS 기반 현장 자동 인식 █ LOW
### ADD-08: 음성 메모 █ LOW

---

## PART 4: UX 개선 (건설 현장 인력 관점)

### UX-01: 터치 영역 확대 ██ CRITICAL
- Vuexy 기본 버튼 32~36px → **최소 48px**
- 정상/이상/보류 버튼은 **60px+ 권장**
- 터치 타겟 간 간격 최소 12px
- `custom.css`에 추가:
```css
.worker-view .btn { min-height: 48px; font-size: 16px; }
.worker-view .check-btn { min-height: 60px; font-size: 18px; font-weight: 700; }
```

### UX-02: 메뉴 대폭 축소 (작업자 모드) ██ CRITICAL
- 현재 메뉴 10개+ 카테고리
- 작업자에게는: **홈 / 점검 / TBM / 알림** — 4개
- 상단 가로 메뉴 → 하단 탭바로 변경
- `position: fixed; bottom: 0` 탭바

### UX-03: 폰트 크기 확대 ██ HIGH
- Vuexy 기본 13~14px → 점검항목 **최소 16px**, 제목 **20px+**
- 야외 직사광선에서 가독성 확보

### UX-04: 고대비 모드 █ HIGH
- 직사광선에서 읽을 수 있도록 고대비 색상
- 정상 = 진한 초록(#16a34a), 이상 = 진한 빨강(#dc2626)
- 회색 계열 최소화

### UX-05: 불필요 JS/CSS 로딩 제거 █ MEDIUM
- apex-charts, datatables, swiper 등 작업자 점검에 불필요
- 작업자 페이지는 최소 번들만 로드
- LTE 환경에서 로딩 3초 → 1.5초 목표

### UX-06: 진동 피드백 █ LOW
- 점검 완료, 이상 선택 시 햄틱 피드백
- `navigator.vibrate([50])` (Vibration API)

---

## 작업 우선순위

### Phase 1: 파이프라인 수정 (가장 시급)
1. **BUG-01** 유형별 페이지 분리 — sector 기반 메뉴 필터링
2. **BUG-02** TBM 하드코딩 제거
3. **BUG-04** 점검항목 일괄생성 실행
4. **BUG-03** 알림 발송 확인 및 수정

### Phase 2: 작업자 화면 (핵심 가치)
5. **ADD-01** 작업자 전용 간소화 뷰
6. **UX-01** 터치 영역 확대
7. **UX-02** 메뉴 축소 + 하단 탭바
8. **UX-03** 폰트 크기 확대

### Phase 3: 기능 확장
9. **ADD-02** 유형별 대시보드
10. **ADD-03** QR 스쳪 → 점검
11. **ADD-04** 사진 첨부
12. **ADD-05** 작업배정 UX 개선

### Phase 4: 고도화 (후순위)
13. **ADD-06** 오프라인 모드
14. **UX-04** 고대비 모드
15. **UX-05** JS/CSS 최적화
16. **ADD-07/08** GPS, 음성

---

## 참고 파일

- 프로젝트 UI 시안: `tai_forklift_check_ui_html.html`
- 사이트맵: `docs/sitemap-taieng-co-kr.md`
- 기획 세션: `docs/session-2026-04-12-planning.md`
