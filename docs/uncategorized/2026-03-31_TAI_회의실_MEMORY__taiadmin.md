# TAI 회의실 Memory — 2026-03-31

## 오늘 완료된 주요 결정 및 작업

### 1. 교육 모듈 설계 확정
- KOSHA 인터넷교육은 유료 (24,000원~) → TAI Safe는 이수 관리 플랫폼으로 포지셔닝
- 교육 링크 우선순위: company_education_setting.custom_url > education_master.source_url
- company_education_setting 테이블 생성 (회사별 교육 링크 재정의)
- education_assignment 테이블 생성
- 작업지시서: docs/TAI_Cursor_작업지시서_교육발령_이수관리_20260331.md

### 2. 작업자 등록 체계 확정
- Track A (users): 안전관리자, 관리감독자 → 이메일+비밀번호 로그인
- Track B (worker_registry): 작업자, 일용직 → 안전관리자 일괄 등록, 로그인 없음
- 포지션(직종) 필수 입력 → 법령 기반 필수 교육 자동 도출
- 등록 방식: 수동 등록 + 엑셀 파일 업로드
- worker_job_type 코드 20건 추가 (WJT001~WJT020)
- 작업지시서: docs/TAI_Cursor_작업지시서_작업자등록_20260331.md

### 3. 앱 방향 확정
- 작업자 앱: PWA → 네이티브 앱으로 진행 결정
- 앱 푸시 알림 비용: 0원 (FCM/APNs 무료)
- 작업자 앱 설치율 = TAI 핵심 운영 KPI
- 최초 초대: SMS 1회 → 이후 앱 푸시 무제한

### 4. 회사 등록 설계 확정
- 회원가입: 이메일+비밀번호+이름만 (회사정보 없음)
- my-company.html: 회사 정보 전체 관리 (모든 필드 유지)
- 법령진단 등 다른 곳에서는 별도 폼으로 필요한 정보만 수집
- company_name → name 컬럼 매핑 백엔드 처리 완료

### 5. 공지예외주장 불필요 확정
- Google/Wayback Machine 미색인 확인
- 출원 전 공개 사실 없음 → 신규성 상실 사유 없음
- 심사청구 기한 2029-03-29만 남음

### 6. 법령진단 단계별 설계 확정
- 1단계: 무료 (회원가입 필수)
- 2단계: 단건 결제 (SaaS 구독으로 해제 불가)
- 3단계: 단건 결제 (SaaS 구독으로 해제 불가)
- 섹터별 분리: BUILDING/MANUFACTURING/SPECIAL_FACILITY + CONSTRUCTION 별도
- 잠금 로직: diagnosis_purchases 테이블 기반
- 단건 가격: 일반건물 29k/59k/99k, 제조공장 49k/99k/249k, 건설 79k/149k/399k
- 작업지시서: docs/TAI_Cursor_작업지시서_법령진단_프론트_반응형_20260331.md

### 7. TAI CARE 서비스 방향 확정
- 위험성평가 작성 = 산업안전기사 자격자만 가능
- 대표님 시험 합격 후 TAI CARE 전문서비스 런칭 예정
- AI 엔진으로 초안 생성 → 자격자 검토·서명 → 납품
- SaaS와 완전 분리된 별도 유료 서비스

### 8. 법령 의무 미구현 모듈 발굴
- TBM (작업 전 안전점검회의): tbm_meetings 테이블 확장
- 안전보건위원회/협의체: safety_committee_meetings 테이블 신규
- 위험성평가: risk_assessments 테이블 신규
- DB migration 완료
- 작업지시서: docs/TAI_Cursor_작업지시서_TBM_안전회의_위험성평가_20260331.md

## API 검증 현황 (v4.8.0)
| API | 상태 |
|-----|------|
| GET / | ✅ |
| GET /education/master | ✅ |
| GET /education/assignments/summary | ✅ (UUID 필요) |
| GET /event-schedules/factory/{uuid} | ✅ (UUID 필요) |
| GET /worker-registry | ✅ |

## PENDING 항목 (내일 계속)

### 🔴 프론트 미완료 (Cursor 재전달 필요)
| 파일 | 상태 |
|------|------|
| diagnosis-step1.html | ⚠️ CSS만 수정, 전면 재설계 미완료 |
| diagnosis-result.html | ❌ 미생성 |
| diagnosis-step2.html | ❌ 미생성 |
| diagnosis-step3.html | ❌ 미생성 |
| construction-step1.html | ❌ 미생성 |
| tbm-list.html | ❌ 미생성 |
| safety-meeting-list.html | ❌ 미생성 |
| risk-assessment-list.html | ❌ 미생성 |

### 🟡 백엔드 미완료
| 항목 | 상태 |
|------|------|
| TBM API (STT 포함) | ❌ 미구현 |
| 안전보건회의 API | ❌ 미구현 |
| 위험성평가 API | ❌ 미구현 |
| 법령진단 백엔드 (diagnosis_purchases) | ❌ 미구현 |

### 🟢 기타
- w.taieng.co.kr 작업자 앱 PWA 설계
- Cloudflare Zero Trust Access 설정
