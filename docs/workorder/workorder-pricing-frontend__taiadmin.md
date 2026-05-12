# 프론트엔드 작업지시서 — 가격·결제·연결서비스
> 작성: 2026-04-14 | 기획창(Opus)
> 이전 버전: `docs/TAI_가격설정_프론트_작업지시서.md` (Phase 1 완료 기준)

---

## 핵심 데이터 흐름

```
어드민(price-setting.html) → PATCH /api/v1/admin/pricing
  → FastAPI DB 저장 → GET /api/v1/public/pricing (5분 캐시)
    → pricing.html 자동 반영 (하드코딩 fallback 병행)
```

---

## Phase 2 — price-setting.html 수정
**레포:** `taiengineering/tai-admin`
**파일:** `admin/full-version/html/horizontal-menu-template/price-setting.html`
**JS:** `admin/full-version/assets/js/tai/pages/price-setting.page.js`

### 2-1. 섹터별 서브탭 추가

현재 price-setting.html은 단일 뷰입니다.
아래와 같이 **3개 섹터 서브탭**으로 분리:

```
[탭] SaaS 구독  |  법령진단  |  연결 서비스 사전등록
```

#### 탭 1: SaaS 구독

| 필드명 | key | 단위 | 기본값 |
|--------|-----|------|--------|
| STARTER 월정가 | `saas_starter_monthly` | 원 | 79,000 |
| BUSINESS 월정가 | `saas_business_monthly` | 원 | 149,000 |
| ENTERPRISE | — | — | "협의" (편집 불가 표시만) |
| STARTER 포함인원 | `saas_starter_users` | 명 | 10 |
| BUSINESS 포함인원 | `saas_business_users` | 명 | 30 |
| 초과인원 단가 | `saas_user_overage` | 원/명/월 | |
| SMS 포함건수 (STARTER) | `saas_starter_sms_included` | 건/월 | |
| SMS 포함건수 (BUSINESS) | `saas_business_sms_included` | 건/월 | |
| SMS 초과단가 | `saas_sms_overage` | 원/건 | |
| 카카오 포함건수 (STARTER) | `saas_starter_kakao_included` | 건/월 | |
| 카카오 포함건수 (BUSINESS) | `saas_business_kakao_included` | 건/월 | |
| 카카오 초과단가 | `saas_kakao_overage` | 원/건 | |
| 서류출력 포함건수 (STARTER) | `saas_starter_doc_included` | 건/월 | |
| 서류출력 포함건수 (BUSINESS) | `saas_business_doc_included` | 건/월 | |
| 서류출력 초과단가 | `saas_doc_overage` | 원/건 | |

> **크레딧 미노출** — UI에 "크레딧"이라는 단어 절대 표시 금지. 항상 "포함건수 / 초과건수"로만 표시.

#### 탭 2: 법령진단 (단건 리포트)

법령진단은 **1회성 리포트 제공** 서비스입니다. SaaS 구독과 혼동 금지.

시설유형 × 등급 행렬 (총 12개 필드):

| key 패턴 | 시설유형 | 소규모 | 중소 | 중대 | 대형 |
|----------|---------|--------|------|------|------|
| `diag_building_*` | 건물·시설 | 99,000 | 199,000 | 299,000 | 499,000 |
| `diag_industry_*` | 제조(산업) | 249,000 | 399,000 | 599,000 | 999,000 |
| `diag_construction_*` | 건설현장 | 399,000 | 599,000 | 899,000 | 1,499,000 |

key 패턴: `diag_{시설코드}_{등급코드}`
- 시설코드: `building` / `industry` / `construction`
- 등급코드: `small` / `medium` / `large` / `xlarge`

UI에 명시할 무료 vs 유료 차이:
- **무료**: 핵심 법령·선임 의무 확인 (리포트 없음)
- **유료**: PDF 리포트 + 점검항목 생성 + 감사 대응 서류

#### 탭 3: 연결 서비스 사전등록 관리

**목적:** 오픈 전 수요·공급 사전등록자 관리

테이블 컬럼:
```
체크박스 | No | 등록유형(수요/공급) | 서비스유형 | 이름 | 연락처 | 등록일 | 지역 | 메모 | 상태
```

기능:
- 목록 조회 (페이지네이션 size=20)
- 등록유형 필터 (전체 / 수요자 / 공급자)
- 서비스유형 필터 (선임연결 / 수선연결 / 컨설팅)
- 메모 인라인 수정 (더블클릭 → textarea)
- 상태 변경 (사전등록 / 연락완료 / 서비스전환)
- 엑셀 다운로드

API (신규 개발 필요 — tai-api 백엔드창에 전달):
```
GET  /api/v1/admin/connect-registrations?type=&service=&page=&size=
PATCH /api/v1/admin/connect-registrations/{id}
GET  /api/v1/admin/connect-registrations/export
```

---

## Phase 3-1 — pricing.html 고도화
**레포:** `taiengineering/taieng`
**파일:** `nexas/pricing.html`

### API 연동 (신규 파일: `nexas/assets/js/pricing.js`)

```javascript
const API_BASE = 'https://api.taieng.co.kr';
const CACHE_KEY = 'tai_pricing_v1';
const CACHE_TTL = 5 * 60 * 1000; // 5분

async function loadPricing() {
  const cached = sessionStorage.getItem(CACHE_KEY);
  if (cached) {
    const { data, ts } = JSON.parse(cached);
    if (Date.now() - ts < CACHE_TTL) { applyPricing(data); return; }
  }
  try {
    const res = await fetch(`${API_BASE}/api/v1/public/pricing`);
    const data = await res.json();
    sessionStorage.setItem(CACHE_KEY, JSON.stringify({ data, ts: Date.now() }));
    applyPricing(data);
  } catch (e) {
    console.warn('pricing API 실패, 하드코딩 fallback 유지');
  }
}

function applyPricing(data) {
  document.querySelectorAll('[data-pricing-key]').forEach(el => {
    const key = el.dataset.pricingKey;
    if (data[key] !== undefined) {
      el.textContent = Number(data[key]).toLocaleString();
    }
  });
}
```

HTML 마크업 (각 가격 요소에 `data-pricing-key` 추가):
```html
<span data-pricing-key="saas_starter_monthly">79,000</span>원
<span data-pricing-key="saas_starter_users">10</span>명
```

### KG이니시스 직접 결제 버튼

**"문의하기" 아닌 직접 결제 프로세스** (KG이니시스 승인 대기 중이나 버튼 먼저 구현)

결제 흐름:
```
1. "시작하기" 클릭
2. 사업장 정보 입력 모달 (시설유형·인원수)
3. 최종 금액 확인 → "결제하기"
4. POST /api/v1/payments/prepare → { order_id, amount }
5. KG이니시스 INIStdPay.pay() 호출
6. 결제 완료 → /api/v1/payments/confirm
7. 완료 리다이렉트
```

KG이니시스 미승인 기간 처리:
- 버튼은 표시, 클릭 시 모달:
  "현재 온라인 결제 시스템 준비 중입니다. 문의하기로 신청해 주세요."
  → [문의하기] 버튼 링크

### 법령진단 탭 구매 플로우

```
시설유형 선택 → 규모 선택 → 가격 표시 → [지금 구매하기]
```
규모 기준 툴팁: 종사자 수 기준 안내

---

## Phase 3-2 — connect.html 신규
**레포:** `taiengineering/taieng`
**파일:** `nexas/connect.html` (신규 생성)

### 페이지 구조

```
히어로: "연결 서비스 — 곧 오픈합니다"
서브: "사전 등록하시면 오픈 즉시 연락드립니다"

[탭] 수요자 (서비스 필요) | 공급자 (전문가·업체)
```

#### 수요자 탭 (registration_type: 'demand')
```
서비스 유형 (복수 선택):
  ☐ 선임 연결   ☐ 수선 연결   ☐ 컨설팅
이름 * | 연락처 * | 지역(시·도) | 이메일 | 문의사항
[사전등록 신청]
```

#### 공급자 탭 (registration_type: 'supply')
```
서비스 유형 (복수 선택):
  ☐ 선임 연결   ☐ 수선 연결   ☐ 컨설팅
이름/업체명 * | 연락처 * | 보유 자격·전문분야 | 지역 | 이메일
[전문가 등록 신청]
```

### API
```
POST /api/v1/connect/register
Body: { registration_type, service_types[], name, phone, email, region, memo }
→ 201: { message: "사전등록이 완료되었습니다." }
```

성공 시: 인라인 성공 메시지 (페이지 이동 없음)

### DB 마이그레이션 (tai-api 백엔드창에 전달)
```sql
CREATE TABLE connect_registrations (
  id                BIGSERIAL PRIMARY KEY,
  registration_type TEXT NOT NULL CHECK (registration_type IN ('demand','supply')),
  service_types     TEXT[] NOT NULL,
  name              TEXT NOT NULL,
  phone             TEXT NOT NULL,
  email             TEXT,
  region            TEXT,
  memo              TEXT,
  status            TEXT DEFAULT 'registered',
  created_at        TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_connect_reg_type ON connect_registrations(registration_type);
CREATE INDEX idx_connect_reg_created ON connect_registrations(created_at DESC);
```

---

## Phase 3-3 — header.js 메뉴 추가
**레포:** `taiengineering/taieng`
**파일:** `nexas/assets/js/header.js`

서비스 드롭다운 하단에 구분선 + "연결 서비스 사전등록" 추가:

```javascript
// 법령진단 항목 다음에 추가
'<li><a href="' + base + 'service/diagnosis.html">법령진단</a></li>',
'<li style="border-top:1px solid rgba(255,255,255,.15);margin:4px 0;"></li>',
'<li><a href="' + base + 'connect.html">🔗 연결 서비스 사전등록</a></li>',
```

---

## 작업 의존성

```
Phase 2-1 → 독립 시작 가능
Phase 2-2 → Phase 3-2 DB 설계와 병렬
Phase 3-1 → /api/v1/public/pricing 엔드포인트 필요 (백엔드 먼저)
Phase 3-2 → DB 마이그레이션 → API → connect.html 순서
Phase 3-3 → connect.html 완성 후 마지막
```

---

## 공통 규칙

| 규칙 | 내용 |
|------|------|
| 크레딧 금지 | UI에 "크레딧" 절대 미노출. "포함건수/초과건수"만 |
| 법령진단 정체성 | 1회성 리포트. SaaS 구독과 혼동 금지 |
| 결제 graceful | KG이니시스 미승인 시 버튼 유지 + 모달 안내 |
| 가격 fallback | API 실패 시 하드코딩 값 유지 |
| 연결서비스 용어 | 소개비/소개수수료/인력소개/소개료 금지 → 플랫폼 이용료/매칭 서비스료 |
| 브랜치 규칙 | 모든 커밋 dev → PR → main |

---

## API 엔드포인트 요약

| 메서드 | 경로 | 작업 레포 |
|--------|------|----------|
| GET | `/api/v1/public/pricing` | tai-api |
| PATCH | `/api/v1/admin/pricing` | tai-api |
| POST | `/api/v1/connect/register` | tai-api |
| GET | `/api/v1/admin/connect-registrations` | tai-api |
| PATCH | `/api/v1/admin/connect-registrations/{id}` | tai-api |
| GET | `/api/v1/admin/connect-registrations/export` | tai-api |
| POST | `/api/v1/payments/prepare` | tai-api |
| POST | `/api/v1/payments/confirm` | tai-api |
