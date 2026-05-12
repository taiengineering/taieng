# 가격체계 프론트엔드 작업지시서

> 2026-04-14 기획창 작성
> 대상: taieng (new.taieng.co.kr) + tai-admin (admin.taieng.co.kr)
> 브랜치: dev → PR → main

---

## 개요

1. pricing.html (new.taieng.co.kr) — 고객용 가격 + KG이니시스 결제
2. price-setting.html (admin.taieng.co.kr) — 관리자 가격 설정
3. connect.html (new.taieng.co.kr) — 연결 서비스 사전등록

핵심: 어드민 가격 수정 → API → pricing.html 자동 반영 (하드코딩 아님)

---

## 1. pricing.html 고도화 (taieng 레포)

### 파일: nexas/pricing.html

### 구조
```
[페이지 로드 시]
  fetch('https://api.taieng.co.kr/public/pricing/saas-plans')
  fetch('https://api.taieng.co.kr/public/pricing/diagnosis-reports')
  → JS로 렌더링
  → API 실패 시 하드코딩 fallback 표시

[탭]
  탭 1: 법령진단 (1회성)
    서브탭: 건물 | 산업 | 건설
  탭 2: SaaS 구독 (월정액)
    서브탭: 건물 | 산업 | 건설
    토글: 월간 / 연간 (연간 = 2개월 무료)
```

### 법령진단 탭

법령진단 = 리포트만 제공. 일정생성·TBM·신고서식은 SaaS 기능.

**건물 (2단계):**
| 무료 | 종합 299,000원 |
|------|---------------|
| 적용법령 수 + 선임의무 | 법령·조문·과태료 + 설비별 점검주기 리포트 |
| [무료 진단] | [바로 결제] |

**산업 (4단계):**
| 무료 | 표준 99K | 설비 199K | 종합 249K |
|------|---------|---------|----------|
| 적용법령 수 | 법령·과태료 | +설비 점검 | +전체 통합 |
| [무료 진단] | [결제] | [결제] | [결제] |

**건설 (2단계):**
| 무료 | 종합 299,000원 |
|------|---------------|
| 선임의무 + 안전관리비 | 전체 의무 + 공정별 리포트 |
| [무료 진단] | [바로 결제] |

### SaaS 탭

과금 기준: 시설당(건물·산업) / 현장당(건설)
포함 건수 표시. 크레딧 미사용.

각 플랜 카드에 [바로 결제] → KG이니시스 PG 연동
CUSTOM은 [문의하기]

### 연간/월간 토글
```
Nexas 원본 pricing 템플릿의 Monthly/Annually 토글 활용
연간: 월가격 × 10 (2개월 무료)
  예: STARTER 79K/월 → 연간 790,000원 (158,000원 절약)
```

### 결제 버튼
```
[바로 결제] 클릭:
  1. 로그인 체크 (미로그인 → 로그인 페이지)
  2. KG이니시스 결제창 호출
  3. 결제 완료 → 서비스 활성화
  4. safe.taieng.co.kr로 리다이렉트

[문의하기] → 문의 폼 or 전화번호
```

### API 연동 코드
```javascript
async function loadPricing() {
  try {
    const [saas, diag] = await Promise.all([
      fetch('https://api.taieng.co.kr/public/pricing/saas-plans').then(r=>r.json()),
      fetch('https://api.taieng.co.kr/public/pricing/diagnosis-reports').then(r=>r.json())
    ]);
    renderSaas(saas);
    renderDiagnosis(diag);
  } catch(e) {
    renderFallback(); // 하드코딩 가격 표시
  }
}
```

### 디자인
- Nexas 원본 pricing 레이아웃 기반 (nexas_sample/ 참고)
- 보라색 그라디언트, Lato 폰트, sc5 클래스
- header.js / footer.js 공통 적용

---

## 2. price-setting.html 수정 (tai-admin 레포)

### 파일
```
tadmin/full-version/html/horizontal-menu-template/price-setting.html
tadmin/full-version/assets/js/tai/pages/price-setting.page.js
```

### 수정 내용

**탭 1: SaaS 플랜**
- 기존 3개 카드 → 서브탭(건물|산업|건설)으로 변경
- 각 서브탭에 해당 섹터 플랜 카드 표시
- 수정 가능 필드: monthly_base_fee, sms_included, kakao_included, doc_included, storage_history_month, include_tbm, is_active
- included_users, extra_user_fee_v2 필드 숨김

**탭 2: 법령진단 단건**
- 기존 6행 → 3행 (건물/산업/건설)
- 건물: 무료 + 종합 299K (중간 없음)
- 산업: 4단계 유지
- 건설: 무료 + 종합 299K (중간 없음)
- facility_type_code 필터: _V2 접미사

**탭 3: 변경 이력** — 기존 유지

**탭 4 (신규): 연결 사전등록 관리**
- GET /connect/pre-registrations 호출
- 테이블: 체크박스 | No. | 등록일 | 유형 | 서비스 | 업체명 | 연락처 | 상태
- 상태 변경: PENDING → CONTACTED → REGISTERED
- UI 표준 준수 (첫번째 체크박스, 두번째 No.)

---

## 3. 연결 서비스 사전등록 페이지 (taieng 레포)

### 파일: nexas/service/connect.html (신규)

### 구조
```
[상단] 안내
  "안전관리 전문가·설비수선 업체를 연결합니다"
  사전등록 혜택: 정식 오픈 시 우선 매칭, 수수료 할인 등

[2분할]
  [왼쪽: 기업 (수요)]
    "안전관리자 선임이 필요합니다"
    "설비수선이 필요합니다"
    → 사전등록 폼

  [오른쪽: 전문가/업체 (공급)]
    "안전관리 전문가입니다"
    "설비수선 전문업체입니다"
    → 사전등록 폼

[폼 필드]
  유형: 수요/공급 (라디오)
  서비스: 선임/수선/진단 (체크박스, 복수)
  업체명/성함, 연락처(필수), 이메일, 활동 지역, 간단 설명
  [사전등록 신청]

[제출 시]
  POST /public/connect/pre-register
  성공: "등록 완료. 정식 오픈 시 우선 안내드리겠습니다."
```

### 네비게이션
- header.js에 "연결 서비스" 메뉴 추가 (서비스 하위)
- service/appointment.html, service/repair.html에서 사전등록 링크

---

## 4. 금지 용어

절대 금지: 소개비, 소개수수료, 인력소개, 소개료
사용: 플랫폼 이용료, 연결 서비스료, 매칭 서비스료, 성과 정산금, 플랫폼 수수료

---

## 5. 작업 순서

```
[Phase 1] 백엔드 먼저 (별도 지시서)
  → DB + 공개 API + 배포

[Phase 2] 프론트 — admin
  → price-setting.html 수정
  → 연결 사전등록 관리 탭

[Phase 3] 프론트 — new.taieng.co.kr
  → pricing.html 고도화 (API 연동 + KG이니시스)
  → connect.html 사전등록 페이지
  → header.js 메뉴 업데이트
```

---

## 6. 체크리스트

```
DB (백엔드 지시서 참고)
  [ ] price_saas_plan 섹터별 데이터
  [ ] price_diagnosis_report V2 데이터
  [ ] connect_pre_registration 테이블

백엔드
  [ ] public_pricing.py + 배포
  [ ] connect_registration.py + 배포
  [ ] price_setting.py sector 필터

프론트 (admin)
  [ ] price-setting.html 섹터별 서브탭
  [ ] 연결 사전등록 관리 탭

프론트 (new.taieng.co.kr)
  [ ] pricing.html API 연동 + KG이니시스 결제
  [ ] connect.html 사전등록 페이지
  [ ] header.js 메뉴 업데이트
```
