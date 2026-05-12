# FN-08 — 법령진단 통합 입력 페이지 (`free-diagnosis.html`)

> 작성일: 2026-04-18  
> 저장소: taiengineering/taieng (nexas/free-diagnosis.html)  
> 배포: Cloudflare Pages → new.taieng.co.kr/free-diagnosis  
> 브랜치 정책: **main 직접 커밋** (taieng 저장소 정책)

---

## 1. 페이지 개요

### 목적
법령진단 무료 체험 + 유료 전환을 단일 페이지에서 처리.  
회원가입·로그인 표현 없이 "사업장 정보 보호" 프레이밍으로 본인인증 처리.

### 진입 경로 2가지
| 경로 | 쿼리파라미터 | 동작 |
|------|------------|------|
| 무료 링크 직접 진입 | 없음 | Step 0(본인인증) → Step 1(섹터) → Step 2(FREE 입력) → Step 3(FREE 결과) → 유료전환유도 |
| 결제 완료 후 리다이렉트 | `?paid=CODE&order_id=XXX` | 본인인증 생략 → 섹터 자동선택 → Step 4(PAID 입력) 즉시 표시 → Step 5(결과 즉시) |

---

## 2. 테마 & 디자인 원칙

### 테마: 현장 클립보드
- **색조**: 크래프트지 톤 (`#f5f0e8`, `#e8dcc8`)
- **포인트**: 도장 느낌 — 붉은 스탬프 레드(`#c0392b`), 먹색 잉크(`#1a1a2e`)
- **폰트**: Noto Serif KR (제목), Noto Sans KR (본문)
- **배경**: 크래프트지 질감 느낌의 연한 베이지
- **버튼**: 잉크 도장 스타일 — 진한 테두리 + 채움

### TAI UI 원칙 적용
> "지금 보지 않아도 되는 것은 보여주지 않는다."
- 섹터 선택 전: 세부 필드 전체 숨김
- FREE 결과 확인 전: 유료 플랜 가격 비노출
- INDUSTRY만: 등급선택 필드 표시 (BUILDING·CONSTRUCTION은 자동판정)

### 레이아웃
- **헤더·푸터 없음** (독립 랜딩 페이지)
- **좌우 분리**: 좌측 고정 설명패널 + 우측 스텝 폼 (데스크탑)
- **모바일**: 단일 컬럼 스크롤

---

## 3. 스텝 구조

### Step 0 — 본인인증 (무료 진입 경로만)

**프레이밍**: "사업장 정보 보호" — 회원가입·로그인 표현 절대 금지

**DB 기록**: `diagnosis_auth_log` 테이블
- `ci` TEXT — KG이니시스 CI 값 (사용자 고유 식별)
- `auth_at` TIMESTAMPTZ
- `ip` TEXT

**리밋 로직**: CI 기준 총 3회 무료 진단 가능 (리셋 없음)
- 3회 초과 시 → "이미 무료 진단을 모두 사용하셨습니다. 유료 진단으로 진행해 주세요." 표시
- 유료 결제 완료 진입(`?paid=`)은 리밋 미적용

---

### Step 1 — 섹터 선택

3개 카드 선택 (소형/대형 분리 금지 — 자동판정):

| 카드 | 아이콘 | 설명 |
|------|--------|------|
| 건물 | 🏢 | 사무용·판매·숙박·의료 등 건축물 |
| 산업 | 🏭 | 제조·가공·물류 공장 및 작업장 |
| 건설 | 🏗️ | 공사 현장 (신축·증축·리모델링) |

선택 즉시 Step 2 필드 표시 (탭 전환 아님, 슬라이드 다운).

---

### Step 2 — FREE 입력 필드

#### 공통 (전 섹터)
| 필드 | 타입 | 비고 |
|------|------|------|
| 사업장명 | text | |
| 주소 | 주소검색 | juso.go.kr API (카카오 금지) |
| 대표자명 | text | |
| 업종 | select | 섹터별 분기 |

#### BUILDING 전용 추가
| 필드 | 타입 | 비고 |
|------|------|------|
| 연면적 | number (㎡) | 자동판정용 — 5,000㎡ 기준 소형/대형 판정 |
| 건물 용도 | select | 업무·판매·숙박·의료·복합 등 |
| 건축물대장 | **UI 비노출** | 주소로 자동 채움 (백엔드 처리) |

#### INDUSTRY 전용 추가
| 필드 | 타입 | 비고 |
|------|------|------|
| 상시근로자 수 | number | |
| 주요 공정 | text | |
| **등급선택** | radio | FREE: BASIC 고정 / PAID: 1·2·3 선택 |

#### CONSTRUCTION 전용 추가
| 필드 | 타입 | 비고 |
|------|------|------|
| 공사 종류 | select | 건축·토목·설비·전기·소방 등 |
| 총 공사금액 | number (억원) | 자동판정용 — 50억 기준 기본/종합 판정 |
| ~~공종~~ | ~~select~~ | **FREE에서 제거 확정** |

#### 면책동의 (진단 실행 직전)
- 체크 전 "진단 시작" 버튼 비활성화
- **"기계적 대조" 표현 금지** → "정밀 분석하여 도출" 사용
- **"더 많이 입력하면 더 정확" 금지** → "해당 법령이 추가 적용됩니다" 사용

---

### Step 3 — FREE 결과

**원칙**: 완결된 결과 표시 — 빈약하게 보이면 유도행위로 비춰짐

- 적용 법령 목록 전체 표시
- "확인하지 못한 영역" 별도 카드로 표시
- **유료 가격 초기 비노출** → "유료 진단 알아보기" 버튼 클릭 후 가격 표시

---

### Step 4 — PAID 입력 (유료 경로)

`?paid=CODE&order_id=XXX` 파라미터 감지 시:
1. 본인인증 스킵
2. `order_id`로 결제 검증 API 호출 → 섹터 자동 세팅
3. PAID 전용 추가 필드 표시

#### INDUSTRY PAID 등급선택
| 등급 | 가격 | 포함 내용 |
|------|------|-----------|
| PAID-1 | 79,000원 | 기본 법령 전체 |
| PAID-2 | 149,000원 | + 특수설비·위험물 |
| PAID-3 | 249,000원 | + 전문가 선임·안전관리비 |

#### BUILDING PAID
- 소형(5,000㎡ 미만): 99,000원 / 대형(이상): 249,000원 — 연면적 자동판정, 등급선택 UI 없음

#### CONSTRUCTION PAID
- 기본(공사금액 50억 미만): 145,000원 / 종합(이상): 299,000원 — 자동판정

---

### Step 5 — PAID 결과 즉시 표시

- **마이페이지 리다이렉트 금지** — 동일 페이지에서 즉시 렌더링
- 결과 PDF 다운로드 버튼 제공
- Supabase Storage `diagnosis-pdfs` 버킷 업로드 후 다운로드 링크

---

## 4. API 연동

| 기능 | 엔드포인트 | 비고 |
|------|-----------|------|
| FREE 진단 실행 | `POST /api/v1/diagnosis/free` | |
| PAID 진단 실행 | `POST /api/v1/diagnosis/paid` | order_id 검증 포함 |
| 결제 검증 | `GET /api/v1/payment/verify?order_id=` | KG이니시스 |
| 본인인증 | KG이니시스 통합인증 | CI 반환 |
| 주소검색 | juso.go.kr API | 카카오 금지 |
| 건축물대장 자동채움 | 행안부 건축물대장 API | UI 비노출, 백엔드 자동 |

---

## 5. DB 테이블

### `diagnosis_auth_log` (신규 생성 필요)
```sql
CREATE TABLE diagnosis_auth_log (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  ci          TEXT NOT NULL,
  auth_at     TIMESTAMPTZ DEFAULT now(),
  ip          TEXT,
  used_count  INT DEFAULT 1
);
CREATE INDEX ON diagnosis_auth_log(ci);
```

### 기존 테이블 활용
- `diagnosis_sessions` — 진단 세션 (기존)
- `diagnosis_results` — 결과 저장 (기존)

---

## 6. 금지 사항

- 카카오 API 일체 사용 금지 (주소검색 포함)
- "소개비/소개수수료/소개료" 용어 금지
- "회원가입", "로그인" 표현 금지 (Step 0에서)
- "기계적 대조" 표현 금지 → "정밀 분석하여 도출"
- "더 많이 입력하면 더 정확" 금지 → "해당 법령이 추가 적용됩니다"
- 건설 FREE에서 공종 필드 금지
- 건축물대장 UI 노출 금지
- PAID 결과를 마이페이지로 리다이렉트 금지
- 유료 가격 초기 노출 금지 (버튼 클릭 후 표시)

---

## 7. 작업 파일

| 파일 | 저장소 | 브랜치 |
|------|--------|--------|
| `nexas/free-diagnosis.html` | taiengineering/taieng | main |
| `nexas/assets/js/diagnosis.js` | taiengineering/taieng | main |
| `nexas/assets/css/diagnosis.css` | taiengineering/taieng | main |

---

## 8. 완료 기준 체크리스트

- [ ] Step 0 — 본인인증 프레이밍 ("사업장 정보 보호")
- [ ] Step 0 — CI 3회 리밋 로직
- [ ] Step 1 — 섹터 3개 카드 (소형/대형 분리 없음)
- [ ] Step 2 — 섹터 선택 전 필드 숨김
- [ ] Step 2 — 건설 FREE 공종 필드 없음
- [ ] Step 2 — 건축물대장 UI 비노출
- [ ] Step 2 — 면책동의 체크박스 (진단 직전)
- [ ] Step 3 — 완결된 결과 표시
- [ ] Step 3 — "확인하지 못한 영역" 별도 표시
- [ ] Step 3 — 유료 가격 초기 비노출
- [ ] Step 4 — `?paid=&order_id=` 파라미터 처리
- [ ] Step 4 — INDUSTRY 등급선택 UI
- [ ] Step 4 — BUILDING/CONSTRUCTION 자동판정
- [ ] Step 5 — 결과 즉시 표시 (리다이렉트 없음)
- [ ] Step 5 — PDF 다운로드
- [ ] 크래프트지 + 도장 테마 적용
- [ ] 헤더·푸터 없음
- [ ] 좌우 분리 레이아웃 (데스크탑)
- [ ] juso.go.kr 주소검색 연동
- [ ] `diagnosis_auth_log` 테이블 Supabase 생성
