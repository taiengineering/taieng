# TAI 프론트엔드 창 — 2026-03-31 세션 메모리

## 환경
- 레포: `taiengineering/tai-admin` (main)
- 배포: Cloudflare Pages → `tadmin/full-version/`

---

## 완료된 작업 (커밋 순서)

### 1. KCSC 검색 대분류 fallback (`e8d452c`)
- `level1_name` null 시 `CT_LABEL[construction_type]` → 건축/토목/공통 표시
- `process-select.html` 테이블 헤더 "대분류" → "구분"

### 2. 공정 수동등록 메뉴 제거 + process-manage deprecated (`ab08f88`)
- `menu-tadmin.js v2.2.0`: `공정 수동등록` 항목 제거
- `process-manage.html`: DEPRECATED 주석 + `process-select.html` 리다이렉트

### 3. 내 회사 정보(tadmin) + 회사관리(admin) 전면 수정 (`a872c50`)

#### DB 마이그레이션
- `companies.business_sector TEXT` 추가 (업태)
- `companies.biz_license_url TEXT` 추가 (사업자등록증 사본 URL)

#### tadmin/my-company.html 변경
| 항목 | 처리 |
|------|------|
| 국세청 검증 버튼 | ✅ 삭제 (어드민에서만 검증) |
| 설립일 | ✅ 삭제 |
| KSIC | ✅ 직접입력 → 검색 모달 (코드+이름 표시) |
| 업태 (`business_sector`) | ✅ 신규 추가 |
| 업종명 (`business_category`) | ✅ 유지 |
| 사업자 유형 (`business_type`) | ✅ 법인/개인 select |
| 팩스 (`fax`) | ✅ 추가 |
| 사업자등록증 사본 | ✅ 드래그앤드롭 업로드 + 보기 버튼 |

#### admin/company-list.html 변경
- 사이드패널 `tab1Fields`에 사업자유형(법인/개인), 업태, 업종명, KSIC(수동), 팩스 추가
- 설립일 제거
- `tab4DocsHtml`에 `biz_license_url` 있으면 보기 버튼 표시
- `collectFormBody()` 함수로 save/update 바디 통합

### 4. 법령진단 프론트 전면 재작성 (`418c025`~`6c5d496`)

#### 파일 목록
| 파일 | 커밋 | 내용 |
|------|------|------|
| `diagnosis-step1.html` | `418c025` | 전면 재작성 |
| `diagnosis-result.html` | `94da9fa` | 신규 |
| `diagnosis-step2.html` | `a0c322b` | 신규 |
| `diagnosis-step3.html` | `65a8527` | 신규 |
| `construction-step1.html` | `6c5d496` | 신규 |

#### diagnosis-step1.html (전면 재작성)
- 반응형 그라디언트 히어로 (max-width:900px)
- 단계 스테퍼 (1.기초진단무료 / 2.공정진단🔒 / 3.설비진단🔒)
- 시설 상단 바 (선택된 시설명+KSIC 표시, 변경 버튼)
- 섹터 카드 4개 (2열 반응형, 모바일 min-height:110px)
  - 건설 클릭 → `construction-step1.html` 이동
- 섹터별 폼: BUILDING / MANUFACTURING / SPECIAL_FACILITY
  - 특수시설: 병원 선택 시 병상수, 학교 선택 시 학생수 표시
- POST `/legal-engine/diagnose/step1` → `diagnosis-result.html?id={id}&stage=1`
- `SECTOR_PRICES` 상수 정의

#### diagnosis-result.html (신규)
- GET `/legal-engine/diagnose/{id}/latest` 연동
- GET `/diagnosis/access-check?factory_id=&step=2` 연동
- 리스크 카드 (HIGH/MEDIUM/LOW 색상 분기)
- 무료 공개 영역: 선임의무 3종 체크, 주요의무 5개, 법령카테고리 (3개까지만 공개)
- 블러 잠금 영역: 가짜 테이블 3행 blur + 잠금배너 (섹터별 가격)
  - "결과를 이메일로 받기" 버튼
  - SaaS 구독 해제 불가 명시
- 전체 공개 섹션 (결제 후): 법령+조문+구분+의무+과태료 테이블, 2단계 CTA

#### diagnosis-step2.html (신규)
- init() → access-check → 잠금배너 or 공정선택폼
- 잠금배너: SaaS 구독 해제 불가 명시, 단건 결제 가격
- 공정선택: `/factory-process/search` 또는 `/factory-process/{id}/processes` fallback
- 공정 검색 필터, 체크박스 다중선택, 선택 배지 표시
- POST `/legal-engine/diagnose/step2`

#### diagnosis-step3.html (신규)
- init() → access-check → 잠금배너 or 설비등록폼
- 설비 추가 모달 (13종 설비, 용량/설치일/검사일/비고)
- 설비 카드 목록, 삭제 버튼
- POST `/legal-engine/diagnose/step3`

#### construction-step1.html (신규)
- 녹색 계열 히어로 (건설 전용)
- 공사금액 + 단위 select (원/만원/억원)
- 실시간 선임 기준 안내 (건축 150억, 토목 120억)
- 하도급 근로자 포함 안내 (산안법 시행령 제16조③)
- 발파·굴착 포함 여부 toggle
- 근로자수 기준 선임 안내 (20인/50인/100인)
- POST `/legal-engine/diagnose/step1` with `sector:'CONSTRUCTION'`

---

## DB 컬럼 현황 (companies 테이블 추가분)
| 컬럼 | 용도 |
|------|------|
| `business_type` | 사업자 유형 (법인/개인) — 기존 |
| `business_sector` | 업태 (제조업, 서비스업 등) — **신규** |
| `business_category` | 업종명 — 기존 |
| `fax` | 팩스 — 기존 |
| `biz_license_url` | 사업자등록증 사본 URL — **신규** |

---

## 핵심 파일 경로

```
tadmin/full-version/html/horizontal-menu-template/
  diagnosis-step1.html        ← 전면 재작성
  diagnosis-result.html       ← 신규
  diagnosis-step2.html        ← 신규
  diagnosis-step3.html        ← 신규
  construction-step1.html     ← 신규
  my-company.html             ← 수정 완료
  process-select.html         ← KCSC fallback 수정
  process-manage.html         ← deprecated (리다이렉트)

tadmin/full-version/assets/js/tai/
  menu-tadmin.js              ← v2.2.0 (공정 수동등록 제거)

admin/full-version/html/horizontal-menu-template/
  company-list.html           ← 수정 완료
```

---

## PENDING 작업
| 항목 | 비고 |
|------|------|
| 백엔드 worker-registry API | POST/GET/PATCH/DELETE/invite/bulk-import/template |
| Cloudflare Pages root directory | `tadmin/full-version` 변경 후 재배포 |
| Cloudflare Zero Trust Access | taieng.co.kr hetto@kakao.com only |
| diagnosis-purchase.html | 단건 결제 페이지 (미구현) |
| `/diagnosis/access-check` API | 백엔드 구현 필요 |
| my-diagnosis.html | 진단 이력 페이지 확인 필요 |

---

## 주요 버그 패턴 (재발 방지)
1. **전각괄호** `（）` → JS 파싱 에러 → 스크립트 전체 중단
2. **`loadGlobals` 예외 전파** → init() 중단 → loadList() 미호출
3. **`status_code=ACTIVE`** → 백엔드 미지원 시 빈 목록 반환
4. **`level1_name` null** → KCSC 검색 결과 대분류 빈칸 → `construction_type` fallback 처리
