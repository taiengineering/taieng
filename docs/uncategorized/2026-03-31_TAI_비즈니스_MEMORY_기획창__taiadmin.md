# TAI 비즈니스 메모리 — 2026-03-31 (기획 창)

---

## 오늘 완료한 것

| 항목 | 내용 | 상태 |
|------|------|------|
| 서비스 본질 재정의 | 법령진단=온보딩 / SaaS=엔진 자동작동 | ✅ |
| 기안자 관점 분석 | 안전관리자·경영지원·대표·건설소장 등 | ✅ |
| 패러다임 전환 냉정 분석 | 비전은 맞으나 판매 메시지는 달라야 함 | ✅ |
| 조달청 등록 현실 전략 | 혁신장터→GS인증→CSAP 단계 정리 | ✅ |
| 요금체계 v2.0 docx | 시설기본료+사용자수 혼합 과금 | ✅ |
| 가격설정 DB 마이그레이션 | price_saas_plan v2 / price_diagnosis_report / price_change_log | ✅ |
| 가격설정 백엔드 API | 6개 엔드포인트 Railway 배포 완료 (012cd3d) | ✅ |
| 가격설정 프론트 작업지시서 | HTML+JS 코드 포함 GitHub 저장 | ✅ |
| admin/tadmin 보안 | _headers, _redirects, robots.txt 적용 | ✅ |
| 법령진단 기획 v3.0 | 산업·건설·건물 3분류 + 건설 가격 상향 | ✅ |
| 법령진단 회원가입 전환전략 | 별도 기획서 GitHub 저장 | ✅ |

---

## 핵심 결정사항

```
서비스 본질:
  법령진단 = 1회성 유료 (온보딩 도구)
  SaaS = 법령엔진 백그라운드 자동 작동 (사용자 버튼 없음)
  주 타깃 = 겸직 안전관리자

요금체계 v2.0:
  STARTER 79,000원 (10명) / BUSINESS 149,000원 (30명)
  법령진단: 산업 99~249K / 건설 99~299K / 건물 79~179K
  회원가입 필수 → 무료 체험 → 과태료 블러 → 결제 유도

브랜딩:
  홍보: TAI Safe / 상표권: TAI / 미래 확장: TAI Care

조달청 전략:
  혁신장터(ppi.go.kr) → GS인증 → CSAP 순서

특허: 110-2026-0056330 / 공지예외주장 기한: 2026-04-28
```

---

## 가격설정 개발 현황

### DB (완료)
```
price_saas_plan     — v2 컬럼 추가 완료
price_diagnosis_report — 시설유형별 6건 초기 데이터
price_change_log    — 가격 변경 이력 자동 기록
```

### 백엔드 (완료 — 커밋 012cd3d, Railway 배포)

| Method | URL | 상태 |
|--------|-----|------|
| GET | /price-setting/saas-plans | ✅ 정상 (3건) |
| GET | /price-setting/saas-plans/{id} | ✅ 정상 |
| PATCH | /price-setting/saas-plans/{id} | ✅ 변경이력 자동기록 |
| GET | /price-setting/diagnosis-reports | ✅ 정상 (6건) |
| PATCH | /price-setting/diagnosis-reports/{id} | ✅ 정상 |
| GET | /price-setting/change-logs | ✅ 정상 |

### 프론트엔드 (작업지시서 완료, Cursor 작업 대기)
```
신규 파일:
  price-setting.html (탭 3개)
  price-setting.page.js (함수 7개)

기존 수정:
  모든 admin 페이지 aside 메뉴에 '가격설정' 추가

참고:
  docs/TAI_가격설정_프론트_작업지시서.md (코드 포함)
```

---

## 보안 설정

```
완료:
  _headers    — 보안 헤더 (noindex, X-Frame-Options)
  _redirects  — 루트 → 로그인 강제이동
  robots.txt  — 검색엔진 크롤링 차단

내일 예정:
  Cloudflare Access 설정
  taieng.co.kr 전체 OTP 인증
  허용 이메일: hetto@kakao.com
  인증: One-time PIN (무료)
```

---

## 법령진단 요금 최종

| 구분 | 무료 | 표준 | 설비/공정 | 종합 |
|------|------|------|-----------|------|
| 산업 | 무료 | 99,000 | 199,000 | 249,000 |
| 건설 | 무료 | 99,000 | 199,000 | **299,000** |
| 건물 | 무료 | 79,000 | 129,000 | 179,000 |

---

## 사무실·통신 인프라

```
비상주오피스: 스테이지나인 강남 월 4만원대
02 인터넷전화: 월 10,000원
인터넷팩스:   월 3,000원
총:           월 약 53,000원
```

---

## 내일 우선순위

| 순위 | 작업 | 비고 |
|------|------|------|
| 🔴 1 | **공지예외주장 제출** | patent.go.kr / 기한 2026-04-28 |
| 🔴 2 | Cloudflare Access 설정 | taieng.co.kr OTP 인증 |
| 🔴 3 | 스테이지나인 비상주 계약 | |
| 🔴 4 | 사업자 등록 (startbiz.go.kr) | |
| 🟡 5 | 가격설정 프론트 Cursor 작업 | 작업지시서 전달 |
| 🟡 6 | 홈페이지 특허출원번호 표기 | |
| 🟡 7 | 결제 연동 (토스페이먼츠) | 사업자등록 후 |
