# TAI Safe SaaS 오픈 검증 체크리스트 v1.0

> 작성일: 2026-05-25
> 목표: "실제 고객이 가입하고 돈 내고 사용할 수 있는가" 검증
> 검증 기준: 실제 브라우저 + 모바일 + 실제 계정 + 실제 결제 흐름

---

## 시나리오 A — 신규 고객 전체 흐름

| # | 단계 | URL (safe.taieng.co.kr) | API 엔드포인트 | DB 테이블 | 상태 |
|---|------|------------------------|---------------|-----------|------|
| A1 | 회원가입 | `/auth-register.html` | `POST /auth/register` | `profiles`, `companies` | ⬜ |
| A2 | 로그인 | `/auth-login-cover.html` | `POST /auth/login` | `profiles` | ⬜ |
| A3 | 회사 정보 확인 | `/my-company.html` | `GET /companies/{id}` | `companies` | ⬜ |
| A4 | 현장(사업장) 생성 | `/factory-list.html` | `POST /factories` | `factories` | ⬜ |
| A5 | 작업자 등록 | `/worker-list.html` | `POST /workers` | `workers` | ⬜ |
| A6 | 점검 실행 | `/inspection-anchor.html` | `POST /inspections` | `inspection_results` | ⬜ |
| A7 | 점검 PDF 다운로드 | 점검 결과 내 | `GET /document-forms/{code}/preview` | `documents` | ⬜ |
| A8 | 로그아웃 | 상단 메뉴 | `POST /auth/logout` | - | ⬜ |
| A9 | 재로그인 | `/auth-login-cover.html` | `POST /auth/login` | - | ⬜ |
| A10 | 데이터 유지 확인 | 대시보드 | `GET /factories`, `GET /workers` | - | ⬜ |

### A 시나리오 검증 포인트
- [ ] 회원가입 후 자동 로그인 되는가?
- [ ] 회사 생성이 가입과 동시에 되는가, 별도인가?
- [ ] 현장 생성 시 주소 검색(행정안전부 API) 작동하는가?
- [ ] 작업자 등록 시 필수 필드만으로 완료 가능한가?
- [ ] 점검 항목이 현장 특성에 맞게 자동 생성되는가?
- [ ] PDF 다운로드 시 Gotenberg 정상 응답하는가?
- [ ] 재로그인 후 모든 데이터 유지되는가?

---

## 시나리오 B — TBM (Tool Box Meeting)

| # | 단계 | URL | API 엔드포인트 | DB 테이블 | 상태 |
|---|------|-----|---------------|-----------|------|
| B1 | TBM 설정 | `/tbm-setting.html` | `POST /tbm/sessions` | `tbm_sessions` | ⬜ |
| B2 | TBM 생성 | `/tbm-create.html` | `POST /tbm/records` | `tbm_records` | ⬜ |
| B3 | 작업자 선택 | TBM 생성 내 | 위 API 내 workers 파라미터 | `tbm_participants` | ⬜ |
| B4 | 서명 | `/tbm-sign.html` | `POST /tbm/{id}/sign` | `tbm_signatures` | ⬜ |
| B5 | TBM PDF 생성 | TBM 목록 내 | `GET /document-forms/DOC-OSH-056/preview` | `documents` | ⬜ |
| B6 | documents 기록 확인 | - | `GET /documents?category=tbm` | `documents` | ⬜ |

### B 시나리오 검증 포인트
- [ ] tbm-create.html이 정상 렌더링되는가? (현재 433bytes — stub 가능성)
- [ ] tbm-sign.html이 정상 렌더링되는가? (현재 431bytes — stub 가능성)
- [ ] 서명 캔버스가 모바일에서 작동하는가?
- [ ] TBM PDF에 서명 이미지가 포함되는가?
- [ ] documents 테이블에 자동 기록되는가?

---

## 시나리오 C — 결제 + 구독

| # | 단계 | URL | API 엔드포인트 | DB 테이블 | 상태 |
|---|------|-----|---------------|-----------|------|
| C1 | 무료체험 시작 | 가입 시 자동 | `POST /subscriptions/trial` | `subscriptions` | ⬜ |
| C2 | 플랜 선택 | `/my-contract.html` (?) | `GET /plans` | `plans` | ⬜ |
| C3 | KG이니시스 결제 | 결제 팝업 | `POST /payment/inicis/request` | `payments` | ⬜ |
| C4 | 결제 콜백 처리 | - | `POST /payment/inicis/callback` | `payments` | ⬜ |
| C5 | subscription 생성 | 자동 | 결제 성공 후 내부 | `subscriptions` | ⬜ |
| C6 | 플랜 적용 확인 | 대시보드 | `GET /subscriptions/me` | `subscriptions` | ⬜ |
| C7 | 기능 제한 반영 | 전체 UI | 각 API의 플랜 체크 | - | ⬜ |
| C8 | 관리자 화면 반영 | admin.taieng.co.kr | `GET /admin/subscriptions` | - | ⬜ |

### C 시나리오 검증 포인트
- [ ] 가입 시 무료체험 자동 시작되는가?
- [ ] 플랜 선택 → 결제 화면 전환이 매끄러운가?
- [ ] KG이니시스 테스트 결제가 정상 처리되는가?
- [ ] 결제 완료 후 subscription 즉시 반영되는가?
- [ ] 무료 → 유료 전환 시 기능 잠금 해제되는가?
- [ ] 관리자 대시보드에서 결제/구독 상태 확인 가능한가?

---

## 프론트엔드 페이지 존재 여부 (tadmin/)

### ✅ 존재 확인 (50+ 페이지)
- 인증: auth-login-cover, auth-register
- 대시보드: index, safety-dashboard, situation-dashboard
- 현장: factory-list, my-company
- 작업자: worker-list, worker-check, worker-home
- 점검: inspection-anchor, inspection-calendar, inspection-custom, my-inspection
- TBM: tbm-list, tbm-setting, tbm-create*, tbm-sign*
- 문서: document-forms, engine-document
- 교육: education-list, education-setting
- 진단: diagnosis-step1~3, diagnosis-result, diagnosis-result-v2, diagnosis-purchase, my-diagnosis
- 공정: process-manage, process-select
- 일정: engine-schedule, schedule-review, work-schedule-list
- 설비: my-equipment, equipment-qr-manager
- 위험성평가: risk-assessment-list
- 알림: notification-center, alert-list, overdue-list
- 계약: my-contract
- 건설: construction-site-list, construction-worker-list, construction-inspection-list 등
- 기타: safety-info, fix-chat, contact, site-map

### ⚠️ 주의 필요
- `tbm-create.html`: 433 bytes — redirect/stub 가능성 높음
- `tbm-sign.html`: 431 bytes — redirect/stub 가능성 높음
- 결제/플랜 선택 전용 페이지 부재 — my-contract.html이 담당?

### ❌ 누락 가능성
- 결제 전용 페이지 (pricing/checkout)
- 구독 관리 페이지 (plan upgrade/downgrade)
- 비밀번호 재설정 페이지
- 온보딩/가이드 페이지

---

## 모바일 UX 검증 (현장 관점)

| 항목 | 검증 기준 | 상태 |
|------|----------|------|
| 버튼 크기 | 최소 44x44px 터치 타겟 | ⬜ |
| 입력 단계 수 | 핵심 작업 3단계 이내 | ⬜ |
| 스크롤 길이 | 점검 실행 시 과도한 스크롤 없음 | ⬜ |
| PDF 다운로드 | 모바일 브라우저에서 즉시 열림 | ⬜ |
| 한손 사용성 | 주요 버튼 하단 배치 | ⬜ |
| 응답 속도 | 페이지 로드 3초 이내 | ⬜ |
| 오프라인 | PWA 기본 동작 확인 | ⬜ |

---

## 관리자 운영 검증 (admin.taieng.co.kr)

| 항목 | 검증 기준 | 상태 |
|------|----------|------|
| 사용자 조회 | 가입된 사용자 목록 + 검색 | ⬜ |
| 구독 상태 | 회사별 플랜/결제 상태 확인 | ⬜ |
| 결제 내역 | 결제 이력 + 환불 처리 | ⬜ |
| 문의 대응 | 고객 문의 접수/응답 | ⬜ |
| 장애 확인 | API health + 모듈 상태 | ⬜ |
| 사업장 현황 | 전체 사업장 + 진단 현황 | ⬜ |

---

## 우선순위

1. **P0 — 가입~점검~PDF** (시나리오 A1→A7): 이것이 안 되면 오픈 불가
2. **P0 — 결제 흐름** (시나리오 C1→C5): 매출이 안 되면 오픈 의미 없음
3. **P1 — TBM 전체** (시나리오 B): 현장 실사용의 핵심
4. **P1 — 모바일 UX**: 현장 작업자 사용 환경
5. **P2 — 관리자 운영**: 오픈 후 운영 필수
