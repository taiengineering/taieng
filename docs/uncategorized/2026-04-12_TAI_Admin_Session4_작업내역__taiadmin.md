# TAI Admin 개발 세션 4 — 작업내역 및 이슈
> 날짜: 2026-04-12  
> 레포: taiengineering/tai-admin · taiengineering/tai-api  
> 진행: Claude (직접 GitHub 커밋) + Cursor + 백엔드

---

## 1. 전체 점검 (세션 시작)

### 직전 세션 누락 확인 결과

| 항목 | 상태 |
|---|---|
| matching-list.html | ✅ 존재 확인 (38.4KB) |
| settlement-list.html | ✅ 존재 확인 (48.4KB) |
| 백엔드 라우터 6개 (matching/settlements/contracts_engine 등) | ✅ |
| DB 테이블 7개 + 뷰 2개 + Storage 버킷 6개 | ✅ |

---

## 2. 이번 세션 작업 목록

### 작업 1 — index.html 대시보드 매칭 파이프라인 현황 섹션 추가

**담당:** Claude 직접 커밋  
**커밋:** `feat: 대시보드 매칭 파이프라인 현황 섹션 추가`  
**SHA:** d66d1950f579e96e09f698c9526c605b9a722651

**변경 내용:**
- 기존 4개 핵심 통계 카드 아래 `매칭 파이프라인 현황` 섹션 추가
- 통계 카드 4개: 신규 신청 / 계약 진행 중 / 이번달 신규 / 정산 대기
- `⚡ 처리 필요` 액션 뱃지 바 (매칭 필요 / 제안 대기 / 계약서 생성 / 정산 처리)
- `loadMatchingStats()` JS 함수 — `GET /matching/admin/dashboard` 연동
- 빠른 바로가기 8개 → 12개 확장 (매칭신청, 전문가신청검토, 정산관리, 결제내역, 가격설정 추가)
- 메뉴에 `전문가신청검토` 항목 추가

---

### 작업 2 — expert-applications.html 신규 생성

**담당:** Claude 직접 커밋  
**커밋:** `feat: 전문가 신청 검토 페이지 추가`  
**SHA:** b0c27409ad3bcdd1f7d18f0fc848d2bfb16af26d  
**크기:** 40.7KB

**기능:**
- 전문가 신청 목록 (필터: 신청상태 / 전문가유형 / 사업자구분 / 키워드)
- 테이블 컬럼: 신청자 / 유형 / 사업자구분 / 사업자명·번호 / 연락처 / 본인인증 / 상태 / 신청일
- 슬라이드 패널 상세 (기본정보 / 자격·인허가 / 활동정보 / 검토현황)
- 첨부 서류 확인 버튼 (`GET /experts/admin/{id}/documents`)
- 승인 버튼: 수수료율(%) 입력 → `PATCH /experts/admin/{id}/approve`
- 반려 버튼: 사유 입력 모달 → `PATCH /experts/admin/{id}/reject`
- 메뉴 active: 매칭관리 > 전문가신청검토

**연동 API:**
```
GET  /experts/admin/list?status=&expert_type=&entity_type=&keyword=&page=&size=
GET  /experts/admin/{id}/documents
PATCH /experts/admin/{id}/approve  { platform_fee_rate, review_note }
PATCH /experts/admin/{id}/reject   { reason }
```

---

### 작업 3A — 전체 HTML 메뉴 전문가신청검토 항목 추가 (Cursor)

**담당:** Cursor (찾아바꾸기)  
**적용 파일:** 전체 HTML 파일 (매칭관리 드롭다운 포함)  

**찾아바꾸기 패턴:**
```
[전] 전문가회원 → 매칭신청
[후] 전문가회원 → 전문가신청검토 → 매칭신청
```

**확인:** matching-list.html SHA 83539ff — 메뉴에 `expert-applications.html` 포함 ✅

---

### 작업 3B — price-setting.html 매칭 수수료 탭 추가 (Cursor)

**담당:** Cursor  
**SHA:** bad7143eab6fb4dce7bf70420012737157a42d71 (이전: 176452cde)  
**크기:** 24.4KB → 32.4KB (+8KB)

**추가 내용:**
- 탭 버튼: `🔗 매칭 수수료` (`#tab-commission`)
- 탭 패널: 서비스유형 / 기간범위 / 금액범위 / 수수료율 / 설명 / 활성 / 수정 / 삭제
- JS 함수: `loadCommissions()` / `saveCommission()` / `toggleCommission()` / `deleteCommission()`
- `shown.bs.tab` 이벤트로 탭 클릭 시 자동 로드
- 수수료 추가 버튼 (POST API 연동 후 활성화 예정)

**연동 API:**
```
GET    /price-commission
PATCH  /price-commission/{id}  { service_type, fee_rate, period_min/max, amount_min/max, description, is_active }
DELETE /price-commission/{id}
```

---

### 작업 4 — 백엔드 보완 (tai-api)

**담당:** 백엔드

| 작업 | 상태 |
|---|---|
| `matching.py` — `GET /matching/admin/dashboard` 필드 보완 | ✅ 확인 |
| `matching.py` — `/price-commission` CRUD 5개 엔드포인트 | ✅ main.py 등록 확인 |

**price_commission 엔드포인트:**
```
GET    /price-commission              목록
POST   /price-commission              신규 등록
PATCH  /price-commission/{id}         수정
DELETE /price-commission/{id}         비활성화
POST   /price-commission/calculate    미리보기
```

**dashboard 응답 구조 (확정):**
```json
{
  "data": {
    "total_requests": 0,
    "by_status": { "RECEIVED": 0, "MATCHING": 0, ... },
    "action_needed": {
      "matching": 0, "proposing": 0, "contracting": 0, "paying": 0, "settling": 0
    },
    "this_month": { "new_requests": 0 },
    "settlement": { "pending_count": 0 }
  }
}
```

---

## 3. 최종 파일 현황

### 프론트엔드 (tai-admin) — 매칭 파이프라인 전체

| 파일 | 크기 | 상태 |
|---|---|---|
| index.html | 33KB | ✅ 매칭 현황 섹션 추가 |
| expert-applications.html | 41KB | ✅ 신규 생성 |
| expert-list.html | 33KB | ✅ |
| consulting-list.html | 42KB | ✅ |
| matching-list.html | 38KB | ✅ |
| personnel-list.html | 52KB | ✅ |
| repair-list.html | 61KB | ✅ |
| settlement-list.html | 48KB | ✅ |
| payment-list.html | 39KB | ✅ |
| price-setting.html | 32KB | ✅ 매칭수수료 탭 추가 |
| identity-verify.html | 25KB | ✅ |

### 백엔드 (tai-api) — 매칭 파이프라인

| 파일 | 크기 | 상태 |
|---|---|---|
| matching.py | 42KB | ✅ dashboard + price_commission CRUD |
| settlements.py | 28KB | ✅ |
| contracts_engine.py | 34KB | ✅ |
| experts.py | 34KB | ✅ |
| payment.py | 52KB | ✅ |
| identity.py | 11KB | ✅ |

---

## 4. 알려진 이슈 및 대기 항목

### 🔴 외부 대기 (블로킹)

| 항목 | 내용 | 영향 |
|---|---|---|
| 이니시스 카드심사 | 심사 완료 대기 중 | VBANK·카드 실거래 불가 |
| 이니시스 간편인증 API 키 | 계약 미체결 | 계약서 전자서명 불가 |
| 국세청 NTS_API_KEY | 미수령 | 사업자번호 검증 불가 |

### 🟡 개발 필요 (다음 작업 후보)

| 순위 | 항목 | 내용 |
|---|---|---|
| 1 | price_commission POST 신규 등록 UI | 현재 버튼은 토스트 안내만 표시 |
| 2 | expert-applications.html AI 리뷰 표시 | `ai_review_*` 필드 패널 내 표시 |
| 3 | 계약서 웹뷰 페이지 | `GET /contracts/{id}/view` 연동 |
| 4 | 메뉴 전체 결제내역 항목 추가 | 계약관리 > 결제내역 링크 통일 |

### 🟢 조건부 대기

| 항목 | 조건 | 내용 |
|---|---|---|
| VBANK 가상계좌 흐름 테스트 | 이니시스 심사 완료 후 | 입금 확인 → 서비스 활성화 |
| 계약서 서명 실서비스 | 이니시스 간편인증 키 수령 후 | CI 기반 전자서명 |

---

## 5. 개발 규칙 (확정)

```
- BASE_URL: https://api.taieng.co.kr
- 신규 페이지 기준: maps-leaflet.html 복사 후 콘텐츠 교체
- alert() 사용 금지 → showToast('success'|'error'|'warning'|'info', '메시지')
- Supabase 직접 연결 금지 → FastAPI 경유
- 코드값 하드코딩 금지 → loadGlobals() + G[category]
- renderPagination: globals.js 사용
- closePanel() → DOMContentLoaded 최상단 호출
- 대량 변경 → Cursor 분할 전달
```

---

## 6. 전체 메뉴 구조 (현재 확정)

```
회원관리      회원관리 / 권한관리 / 알림설정 / 회사관리
계약관리      결제내역 / 구독·계약 / 견적관리 / 문의관리 / 발행문서 / 요청문서
산업안전      시설관리 / 공정관리 / 설비관리 / 모델관리 / 점검관리 / TBM관리
건설안전      현장관리 / 공정관리 / 작업관리 / 작업자관리 / 점검관리 / TBM관리
교육관리      교육관리 / 교육설정
위험관리      현황리포트 / 사고관리 / 법위반관리 / 위험관리 / 미교육관리 / 위험성평가
매칭관리 ★   전문가회원 / 전문가신청검토 / 매칭신청 / 선임연결관리 /
             컨설팅연결 / 수선연결 / 정산관리
업체연결      진단연결
설정          권한설정 / 견적설정 / 수선설정 / 문서설정 / 가격설정
엔진설정      전역변수 / 설비 / 모델 / 법규 / 공정(산업) / 공정(건설) /
             사고 / 엔진 / TBM / 교육 / 크론관리
```

---

## 7. 상태 전이 규칙 (matching_requests.status)

```
RECEIVED    → MATCHING, CANCELLED
MATCHING    → PROPOSED, FAILED, CANCELLED
PROPOSED    → SELECTED, CANCELLED
SELECTED    → CONTRACTING, DROPPED
CONTRACTING → CONTRACTED, DROPPED
CONTRACTED  → IN_PROGRESS
IN_PROGRESS → CONFIRMING
CONFIRMING  → SETTLED
SETTLED     → CLOSED
※ 위반 시 400 Bad Request
```

---

*생성일: 2026-04-12 | TAI Admin 개발 세션 4*
