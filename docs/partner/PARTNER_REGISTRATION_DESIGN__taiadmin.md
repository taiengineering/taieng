# TAI 파트너 모집·등록 — UX·데이터·API 설계서

버전: 1.0 · 대상: 웹 프론트 / 백엔드 / 관리자 · 전제: 최소 기능 → SaaS·커머스 확장 가능

---

## 1. 정보구조(IA)와 UX 흐름

### 1.1 진입 구조

```
/partners                          → 파트너 랜딩 (3 카드 선택만)
/partners/repair/register          → 수선업체 전용 등록 (독립 IA)
/partners/inspector/register       → 선임기술자·선임대행 전용 등록
/partners/safety-agency/register   → 안전관리대행업체 전용 등록
/partners/status/:submissionId     → (선택) 제출 상세·보완 요청 대응
```

- **랜딩**에서는 카드로 유형만 고르고, **선택 즉시 전용 URL로 이동**한다.  
- 각 등록 URL은 **브레드크럼·히어로 카피·폼 제목이 유형 전용**이어야 한다.  
- 내부적으로는 `partner_type` 하나로 분기하지만, **사용자에게는 “같은 시스템의 다른 제품”**처럼 보이게 한다.

### 1.2 단계형 UX (공통 골격, 카피·필드만 유형별)

| 단계 | 목적 | 공통 처리 |
|------|------|-----------|
| 1. 자격·신원 | 신뢰·심사 가능한 최소 정보 | 사업자/담당/연락/약관 |
| 2. 전문성 | 유형별 핵심 차별화 | 유형별 상세 JSON |
| 3. 운영·상업 | 매칭·과금·운영 (선택 다수) | 일부는 “검토 후 입력” 허용 |
| 4. 검토 제출 | 접수 완료 + 상태 안내 | `SUBMITTED` |

- **1차 필수**만 막고, 나머지는 `optional` 또는 `review_requested` 시 보완.  
- **보완요청** 시 관리자 코멘트 + 필드 단위 플래그로 재제출 유도.

### 1.3 사용자 상태 머신 (제출 단위)

```
DRAFT → SUBMITTED → UNDER_REVIEW → NEEDS_SUPPLEMENT → UNDER_REVIEW → APPROVED
                              ↘ REJECTED (종료)
```

- `NEEDS_SUPPLEMENT`: 사용자에게만 **요청 필드 + 코멘트** 노출.  
- `APPROVED` 이후 **공개 프로필**과 **관리자 전용 필드** 분리 저장.

---

## 2. 통합 폼 vs 분리 UI + 통합 데이터 (비교)

| 구분 | 단일 통합 폼 | 외부 UI 분리 + 내부 통합 모델 |
|------|----------------|-------------------------------|
| 인지 부담 | 유형 선택 드롭다운으로 “분류” 느낌 | 유형별 전용 페이지로 **정체성·프라이드** 유지 |
| 마케팅/카피 | 한 화면에 억지로 공존 | 유형별 히어로·순서·톤 최적화 |
| 개발 | 폼 1개 | 라우트 3개 + 공통 컴포넌트 + `partner_type` |
| 데이터 | 동일하게 통합 가능 | **동일** — `common` + `detail` JSON 권장 |
| 유지보수 | 필드 폭증 시 스파게티 위험 | 유형별 파일/모듈 분리로 확장 용이 |

**결론:** 내부는 **하나의 `partner_submissions` (또는 유사) 테이블 + `detail` JSON**으로 통합하고, 외부만 3개로 나누는 것이 요구사항(프라이드·전문성·B2B 톤)과 확장성에 맞다.

---

## 3. 유형별 페이지 설계 (표)

### 3.1 수선업체 (`REPAIR_CONTRACTOR`)

| 섹션 | 제목 예시 | 주요 입력 | 필수(1차) |
|------|-----------|-----------|-----------|
| A. 현장 대응 소개 | 현장·시공 역량을 알려주세요 | 소개 문구, 로고 | 소개 문구 |
| B. 사업자 정보 | 사업자 및 연락 | 업체명, 대표, 담당, 연락, 이메일, 사업자번호, 주소 | 업체명, 담당, 연락, 이메일, 사업자번호 |
| C. 전문 분야 | 어떤 작업을 수행하시나요? | 전문 분야 멀티, 공사 범위 | 전문 분야 1개 이상 |
| D. 운영 조건 | 출동·견적·A/S | 긴급 출동, 견적 방식, A/S, 시간대 | 긴급 여부, 견적 방식 |
| E. 자격·안전 | 면허·보험·인력 | 면허/등록증 파일, 보험, 기술인력 수 | 보험 여부(선택) |
| F. 상업 정보 | 단가·최소비용 | 평균 단가 범위, 최소 출동비 | 선택 |
| G. 실적·미디어 | 대표 사례 | 실적 텍스트, 작업 사진 | 선택 |
| H. 약관 | 제출 동의 | 약관·개인정보 | 필수 |

**톤:** 현장·시공·신속 대응. 색·아이콘: 공구·헬멧 계열(과한 쇼핑몰 배너 지양).

---

### 3.2 선임기술자 / 선임대행 (`APPOINTED_EXPERT`)

| 섹션 | 제목 예시 | 주요 입력 | 필수(1차) |
|------|-----------|-----------|-----------|
| A. 전문가 소개 | 선임·자문 역량 | 소개, 등록 유형(개인/대행업체) | 등록 유형, 소개 |
| B. 신원·연락 | 연락 및 사업자 | 업체명 또는 활동명, 대표/담당, 연락, 이메일, 사업자번호(업체 시) | 담당, 연락, 이메일 |
| C. 선임 가능 범위 | 분야·업종 | 선임 분야, 업종, 활동 지역 | 분야·지역 |
| D. 자격·경력 | 자격 증빙 | 자격 종류, 번호, 취득일, 경력 연수 | 자격 종류, 경력 |
| E. 계약·활동 형태 | 월계약·자문·방문 | 월 계약 가능, 단기 자문, 현장 방문 | 최소 1개 선택 |
| F. 운영 지표 | 사업장 수·단가 | 월 관리 가능 사업장 수, 평균 단가 범위 | 선택 |
| G. 이력 | 주요 수행 이력 | 텍스트 | 선택 |
| H. 약관 | 동의 | 약관 | 필수 |

**톤:** 전문직·등록·자격. 카드는 얇은 보더, 과한 일러스트 금지.

---

### 3.3 안전관리대행업체 (`SAFETY_AGENCY`)

| 섹션 | 제목 예시 | 주요 입력 | 필수(1차) |
|------|-----------|-----------|-----------|
| A. 기관 소개 | 안전관리 대행 역량 | 소개, 업체 유형(기관/컨설팅/위평/교육 등) | 업체 유형, 소개 |
| B. 사업자 정보 | 법인·연락 | 업체명, 대표, 담당, 사업자번호, 주소 | 업체명, 사업자번호, 담당, 연락 |
| C. 서비스·대상 | 제공 서비스·업종 | 제공 서비스, 대상 업종, 지역 | 서비스 1개 이상, 지역 |
| D. 계약·운영 | 구독·방문·리포트 | 계약 형태, 정기 방문 횟수, 온라인 관리, 보고서 | 계약 형태 |
| E. 인력·자격 | 인증·인력 | 등록/지정 증빙 파일, 인력 수, 전담 기술자, 자격 현황 | 증빙 1건 이상 권장(선택 가능) |
| F. 부가 | 교육·보험·SaaS | 교육, 보험, SaaS 연동 | 선택 |
| G. 상업·레퍼런스 | 단가·고객·사례 | 평균 단가, 주요 고객 업종, 사례, 소개서 PDF | 선택 |
| H. 약관 | 동의 | 약관 | 필수 |

**톤:** 기관·컨설팅·감사 대응. 단계 헤더에 “심사·등록” 뉘앙스 문구.

---

## 4. 공통 필드 vs 유형별 필드

### 4.1 공통 (`PartnerCommon`)

- 업체명 또는 활동명 `legal_name`  
- 대표자명 `ceo_name`  
- 담당자명 `manager_name`  
- 연락처 `phone`  
- 이메일 `email`  
- 사업자등록번호 `business_number` (개인은 nullable)  
- 사업장 주소 `address`, `address_detail`  
- 서비스 가능 지역 `service_regions: string[]`  
- 홈페이지 `website_url`  
- 소개 문구 `introduction`  
- 로고 URL `logo_url` (업로드 후)  
- 세금계산서 발행 가능 `tax_invoice_available: boolean`  
- 상태 `status` (제출 단위)  
- 약관 동의 `terms_agreed_at`, `privacy_agreed_at`  

### 4.2 유형별 (`detail`)

- `repair`: 수선업체 후보 필드 전부 → JSON  
- `inspector`: 선임기술자/대행 후보 필드 → JSON  
- `safety_agency`: 안전관리대행 후보 필드 → JSON  

### 4.3 관리자 전용 (비공개)

- 내부 메모 `admin_note`  
- 심사자 ID `reviewer_id`  
- 보완 요청 사유 `supplement_note`  
- 반려 사유 `reject_reason`  
- 신뢰도 점수(향후) `trust_score`  

공개 프로필(`partner_profiles`)은 승인 후 스냅샷 또는 뷰로 노출 필드만 복제.

---

## 5. 저장용 데이터 모델 (요약)

상세 TypeScript 정의는 `partner-registration.types.ts` 참고.

**핵심 엔티티 (논리)**

1. `partner_submissions`  
   - `id`, `partner_type`, `common` (JSON 또는 컬럼 정규화), `detail` (JSON), `status`, `version`, `created_at`, `updated_at`, `user_id` (nullable)

2. `partner_submission_events` (감사·상태 이력)  
   - `submission_id`, `from_status`, `to_status`, `actor`, `note`, `created_at`

3. `partner_profiles` (승인 후 공개용, 선택)  
   - `submission_id` FK, 공개 허용 필드만

---

## 6. API 엔드포인트 제안

| Method | Path | 설명 |
|--------|------|------|
| POST | `/api/v1/partner-submissions` | 신규 제출 (draft 또는 submit) |
| PATCH | `/api/v1/partner-submissions/:id` | 수정 (DRAFT / NEEDS_SUPPLEMENT만) |
| GET | `/api/v1/partner-submissions/:id` | 본인 제출 조회 |
| POST | `/api/v1/partner-submissions/:id/submit` | 최종 제출 → SUBMITTED |
| POST | `/api/v1/uploads/presign` | S3 등 프리사인 (로고·PDF) |

**관리자**

| Method | Path | 설명 |
|--------|------|------|
| GET | `/api/v1/admin/partner-submissions` | 목록 필터 `status`, `partner_type` |
| POST | `/api/v1/admin/partner-submissions/:id/transition` | 상태 전이 + 메모 |
| GET | `/api/v1/admin/partner-submissions/:id` | 상세 + 이력 |

`transition` body 예: `{ "to": "NEEDS_SUPPLEMENT", "fields": ["detail.repair.insurance_proof_url"], "note": "..." }`

---

## 7. 관리자 승인 흐름

1. 사용자 제출 → `SUBMITTED`  
2. 담당자 배정 → `UNDER_REVIEW`  
3. 부족 시 → `NEEDS_SUPPLEMENT` + 필드 목록 + 코멘트 (이메일/알림 선택)  
4. 재제출 → 다시 `UNDER_REVIEW`  
5. 승인 → `APPROVED` + `partner_profiles` 생성/갱신  
6. 반려 → `REJECTED` + 사유 (재신청 정책은 별도)

**공개/비공개:** API 응답에서 `role === admin` 일 때만 `admin_note` 등 포함.

---

## 8. 폴더 구조 제안 (React 기준)

```
apps/partner-web/                    # 또는 src/features/partners/
├── src/
│   ├── app/
│   │   ├── routes.tsx
│   │   └── layout/
│   ├── pages/
│   │   ├── PartnerLandingPage.tsx
│   │   ├── repair/
│   │   │   └── RepairPartnerRegisterPage.tsx
│   │   ├── inspector/
│   │   │   └── InspectorPartnerRegisterPage.tsx
│   │   └── safety-agency/
│   │       └── SafetyAgencyRegisterPage.tsx
│   ├── features/
│   │   └── partner-registration/
│   │       ├── components/
│   │       │   ├── StepperLayout.tsx
│   │       │   ├── common/
│   │       │   │   ├── BusinessIdentitySection.tsx
│   │       │   │   ├── ContactSection.tsx
│   │       │   │   └── TermsSection.tsx
│   │       │   ├── repair/
│   │       │   ├── inspector/
│   │       │   └── safety-agency/
│   │       ├── hooks/
│   │       │   └── usePartnerSubmission.ts
│   │       └── api.ts
│   ├── types/
│   │   └── partner-registration.types.ts
│   └── styles/
│       └── partner-b2b.css
```

---

## 9. 디자인 방향 (요약)

- **레이아웃:** 좌측 고정 스텝퍼(데스크톱) / 상단 스텝(모바일).  
- **컬러:** 단일 프라이머리(예: TAI 블루) + 중립 그레이. 카드는 그림자 최소.  
- **카피:** “등록”, “심사”, “제출 완료” 등 공공·B2B 톤.  
- **컴포넌트:** `Card` + `SectionTitle` + `Description` + 폼 그리드.

---

## 10. 다음 작업

- 본 저장소의 `partner-registration.types.ts`, `api-payload-examples.md`, `react-example/*` 참고.  
- 백엔드는 `partner_submissions` 단일 테이블 + `detail` JSON으로 MVP 권장.
